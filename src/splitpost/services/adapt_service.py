import json
import httpx

from ..core.config import settings
from .platform_rules import PLATFORMS, TONES

SYSTEM_PROMPT = """You are SplitPost — an expert content adaptation AI.
Your job: take ONE piece of content and rewrite it for EACH requested social media platform.

Rules:
- Each adaptation MUST respect the platform's character limit
- Match the requested tone perfectly
- Include platform-appropriate hashtags
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


async def adapt_content(text: str, tone: str, platforms: list[str], tags: str) -> list[dict]:
    if not settings.openrouter_api_key:
        return _fallback_adapt(text, tone, platforms, tags)

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
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                    ],
                    "temperature": 0.7,
                },
            )
            data = resp.json()
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
            return adaptations

    except Exception as e:
        return _fallback_adapt(text, tone, platforms, tags)


def _fallback_adapt(text: str, tone: str, platforms: list[str], tags: str) -> list[dict]:
    """Simple fallback when no API key."""
    adaptations = []
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    hashtags = [f"#{t.replace(' ', '')}" for t in tag_list[:5]]

    for p in platforms:
        spec = PLATFORMS.get(p)
        if not spec:
            continue
        limit = spec["char_limit"]
        truncated = text[:limit] if len(text) > limit else text
        adaptations.append({
            "platform": p,
            "content": truncated,
            "char_count": len(truncated),
            "char_limit": limit,
            "hashtags": hashtags[:spec["hashtag_count"]],
            "warnings": ["AI unavailable — showing truncated original"] if len(text) > limit else [],
        })
    return adaptations
