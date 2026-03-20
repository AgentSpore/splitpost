from pydantic import BaseModel


class SplitRequest(BaseModel):
    text: str
    tone: str = "professional"  # professional, casual, viral, witty, academic
    platforms: list[str] = ["twitter", "linkedin", "instagram", "telegram", "tiktok"]
    tags: str = ""


class AdaptationResponse(BaseModel):
    platform: str
    content: str
    char_count: int
    char_limit: int
    hashtags: list[str]
    warnings: list[str]


class PostResponse(BaseModel):
    id: int
    original_text: str
    tone: str
    tags: str
    created_at: str
    adaptations: list[AdaptationResponse]


class PostListItem(BaseModel):
    id: int
    original_text: str
    tone: str
    tags: str
    created_at: str
    platform_count: int
