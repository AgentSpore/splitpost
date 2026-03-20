import json
import httpx

from ..core.config import settings
from .platform_rules import PLATFORMS, TONES

SYSTEM_PROMPT = """You are SplitPost — an expert content adaptation AI.
Your job: take ONE piece of content and rewrite it for EACH requested social media platform.

Rules:
- LANGUAGE: Detect the language of the original content and write ALL adaptations in that SAME language. If input is in Russian, output in Russian. If English, output in English. Etc.
- Each adaptation MUST respect the platform's character limit
- Match the requested tone perfectly
- Include platform-appropriate hashtags (in the same language as content)
- Never copy-paste — each version must feel NATIVE to its platform
- Twitter: if content is too long, create a thread (split into numbered tweets)
- TikTok: write as a video SCRIPT with [HOOK], [MAIN], [CTA] sections
- Instagram: visual caption style with emoji section markers
- LinkedIn: storytelling format, hook first line
- Telegram: markdown-formatted channel post

Return ONLY valid JSON (no markdown fences):
{
  "adaptations": [
    {
      "platform": "twitter",
      "content": "...",
      "hashtags": ["tag1", "tag2"],
      "warnings": []
    }
  ]
}

If content exceeds a platform's limit, add a warning. Never truncate silently."""


class AdaptError(Exception):
    """Raised when LLM adaptation fails."""
    pass


async def adapt_content(text: str, tone: str, platforms: list[str], tags: str, model: str = "") -> dict:
    """Returns {"adaptations": [...], "model": str, "ai_used": True}
    Raises AdaptError on any failure."""
    used_model = model or settings.llm_model

    if not settings.openrouter_api_key:
        raise AdaptError("No API key configured. Set SP_OPENROUTER_API_KEY or OPENROUTER_API_KEY.")

    tone_desc = TONES.get(tone, TONES["professional"])
    platform_specs = []
    for p in platforms:
        if p in PLATFORMS:
            spec = PLATFORMS[p]
            platform_specs.append(f"- {spec['name']}: max {spec['char_limit']} chars, {spec['hashtag_count']} hashtags. Style: {spec['style']}")

    user_msg = f"""Adapt this content for: {', '.join(platforms)}

Tone: {tone} — {tone_desc}
Tags/context: {tags or 'none'}

Platform specs:
{chr(10).join(platform_specs)}

Original content:
---
{text}
---"""

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                json={
                    "model": used_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.7,
                },
            )
            data = resp.json()

            if "error" in data:
                err_msg = data["error"].get("message", str(data["error"])) if isinstance(data["error"], dict) else str(data["error"])
                raise AdaptError(f"LLM error: {err_msg}")

            content = data["choices"][0]["message"]["content"]
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(content)

            adaptations = []
            for a in result.get("adaptations", []):
                platform = a["platform"]
                text_content = a["content"]
                spec = PLATFORMS.get(platform, {})
                char_limit = spec.get("char_limit", 9999)
                warnings = a.get("warnings", [])
                if len(text_content) > char_limit and not spec.get("supports_threads"):
                    warnings.append(f"Content is {len(text_content)} chars, limit is {char_limit}")

                adaptations.append({
                    "platform": platform,
                    "content": text_content,
                    "char_count": len(text_content),
                    "char_limit": char_limit,
                    "hashtags": a.get("hashtags", []),
                    "warnings": warnings,
                })

            if not adaptations:
                raise AdaptError("LLM returned empty adaptations")

            return {"adaptations": adaptations, "model": used_model, "ai_used": True}

    except AdaptError:
        raise
    except Exception as e:
        raise AdaptError(f"Failed to connect to AI: {e}")
