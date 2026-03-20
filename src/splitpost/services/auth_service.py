import jwt
import time

from ..core.config import settings
from ..repositories import user_repo


async def register(db, username: str, email: str, display_name: str, password: str) -> dict:
    user = await user_repo.create_user(db, username, email, display_name, password)
    token = _create_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": _user_response(user)}


async def login(db, email: str, password: str) -> dict:
    user = await user_repo.verify_password(db, email, password)
    if not user:
        raise ValueError("Invalid email or password")
    token = _create_token(user["id"])
    return {"access_token": token, "token_type": "bearer", "user": _user_response(user)}


def _create_token(user_id: int) -> str:
    return jwt.encode(
        {"sub": str(user_id), "exp": int(time.time()) + settings.jwt_expire_hours * 3600},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def _user_response(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "display_name": user["display_name"],
        "default_tone": user["default_tone"],
    }
