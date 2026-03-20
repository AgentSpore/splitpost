import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SplitPost"
    debug: bool = False

    # Database
    db_path: str = "splitpost.db"

    # JWT
    jwt_secret: str = "splitpost-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 72

    # LLM
    openrouter_api_key: str = ""
    llm_model: str = "google/gemini-2.0-flash-001"

    model_config = {"env_prefix": "SP_"}


settings = Settings()

# Fallback: use OPENROUTER_API_KEY if SP_OPENROUTER_API_KEY not set
if not settings.openrouter_api_key:
    settings.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "")
