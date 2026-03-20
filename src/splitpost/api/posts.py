import time
import httpx

from fastapi import APIRouter, HTTPException

from ..core.config import settings
from ..core.deps import DbDep, UserDep
from ..schemas.post import SplitRequest, PostResponse, AdaptationResponse, PostListItem
from ..services.adapt_service import adapt_content, AdaptError
from ..services.platform_rules import PLATFORMS
from ..repositories import post_repo

router = APIRouter(prefix="/posts", tags=["posts"])

_models_cache: list[dict] = []
_models_cache_ts: float = 0
CACHE_TTL = 3600  # 1 hour


async def _fetch_free_models() -> list[dict]:
    global _models_cache, _models_cache_ts
    if _models_cache and time.time() - _models_cache_ts < CACHE_TTL:
        return _models_cache

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://openrouter.ai/api/v1/models")
            data = resp.json()
            models = []
            for m in data.get("data", []):
                pricing = m.get("pricing", {})
                if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                    modalities = m.get("architecture", {}).get("output_modalities", [])
                    if "text" not in modalities:
                        continue
                    models.append({
                        "id": m["id"],
                        "name": m.get("name", m["id"]),
                        "context_length": m.get("context_length", 0),
                    })
            models.sort(key=lambda x: x["name"])
            _models_cache = models
            _models_cache_ts = time.time()
            return models
    except Exception:
        return _models_cache or []


@router.get("/config")
async def get_config():
    models = await _fetch_free_models()
    return {
        "default_model": settings.llm_model,
        "models": models,
        "has_api_key": bool(settings.openrouter_api_key),
    }


@router.post("/split", response_model=PostResponse)
async def split_post(req: SplitRequest, user: UserDep, db: DbDep):
    if not req.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    if len(req.text) > 10_000:
        raise HTTPException(400, "Text too long (max 10,000 chars)")

    valid_platforms = [p for p in req.platforms if p in PLATFORMS]
    if not valid_platforms:
        raise HTTPException(400, f"No valid platforms. Choose from: {list(PLATFORMS.keys())}")

    try:
        result = await adapt_content(req.text, req.tone, valid_platforms, req.tags, req.model)
    except AdaptError as e:
        raise HTTPException(502, str(e))

    post_id = await post_repo.create_post(db, user["id"], req.text, req.tone, req.tags)
    await post_repo.save_adaptations(db, post_id, result["adaptations"])

    post = await post_repo.get_post_with_adaptations(db, post_id, user["id"])
    resp = _format_post(post)
    resp.model = result["model"]
    return resp


@router.get("/", response_model=list[PostListItem])
async def list_posts(user: UserDep, db: DbDep, limit: int = 50, offset: int = 0):
    posts = await post_repo.list_posts(db, user["id"], limit, offset)
    return posts


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, user: UserDep, db: DbDep):
    post = await post_repo.get_post_with_adaptations(db, post_id, user["id"])
    if not post:
        raise HTTPException(404, "Post not found")
    return _format_post(post)


@router.delete("/{post_id}")
async def delete_post(post_id: int, user: UserDep, db: DbDep):
    deleted = await post_repo.delete_post(db, post_id, user["id"])
    if not deleted:
        raise HTTPException(404, "Post not found")
    return {"status": "deleted"}


@router.get("/platforms/list")
async def list_platforms():
    return {k: {"name": v["name"], "char_limit": v["char_limit"]} for k, v in PLATFORMS.items()}


def _format_post(post: dict) -> dict:
    adaptations = []
    for a in post.get("adaptations", []):
        hashtags_raw = a.get("hashtags", "")
        hashtags = [h.strip() for h in hashtags_raw.split(",") if h.strip()] if isinstance(hashtags_raw, str) else hashtags_raw
        spec = PLATFORMS.get(a["platform"], {})
        adaptations.append(AdaptationResponse(
            platform=a["platform"],
            content=a["content"],
            char_count=a["char_count"],
            char_limit=spec.get("char_limit", 0),
            hashtags=hashtags,
            warnings=[],
        ))
    return PostResponse(
        id=post["id"],
        original_text=post["original_text"],
        tone=post["tone"],
        tags=post["tags"],
        created_at=str(post["created_at"]),
        adaptations=adaptations,
    )
