import hashlib
import hmac
import os

import aiosqlite


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return dk.hex(), salt.hex()


def _verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    salt = bytes.fromhex(salt_hex)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk.hex(), stored_hash)


async def create_user(db: aiosqlite.Connection, username: str, email: str, display_name: str, password: str) -> dict:
    pw_hash, salt = _hash_password(password)
    cursor = await db.execute(
        "INSERT INTO users (username, email, display_name, password_hash, salt) VALUES (?, ?, ?, ?, ?)",
        (username, email, display_name or username, pw_hash, salt),
    )
    await db.commit()
    return await get_user_by_id(db, cursor.lastrowid)


async def get_user_by_id(db: aiosqlite.Connection, user_id: int) -> dict | None:
    cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def get_user_by_email(db: aiosqlite.Connection, email: str) -> dict | None:
    cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = await cursor.fetchone()
    return dict(row) if row else None


async def verify_password(db: aiosqlite.Connection, email: str, password: str) -> dict | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if _verify_password(password, user["password_hash"], user["salt"]):
        return user
    return None
