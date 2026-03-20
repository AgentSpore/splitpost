from typing import Annotated
from fastapi import Depends, HTTPException, Header
import jwt
import aiosqlite

from .config import Settings, settings
from .database import get_db


async def get_settings() -> Settings:
    return settings


async def get_current_user(
    authorization: str = Header(None),
    db: aiosqlite.Connection = Depends(get_db),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload["sub"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(401, "User not found")
    return dict(user)


DbDep = Annotated[aiosqlite.Connection, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
UserDep = Annotated[dict, Depends(get_current_user)]
