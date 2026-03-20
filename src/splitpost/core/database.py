import aiosqlite
import os

DB_PATH = None
_db: aiosqlite.Connection | None = None


async def init_db(db_path: str | None = None):
    global _db, DB_PATH
    DB_PATH = db_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "splitpost.db")
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")

    await _db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL DEFAULT '',
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            default_tone TEXT NOT NULL DEFAULT 'professional',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            original_text TEXT NOT NULL,
            tone TEXT NOT NULL DEFAULT 'professional',
            tags TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS adaptations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            char_count INTEGER NOT NULL DEFAULT 0,
            hashtags TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    await _db.commit()


async def get_db() -> aiosqlite.Connection:
    assert _db is not None, "Database not initialized"
    return _db


async def close_db():
    global _db
    if _db:
        await _db.close()
        _db = None
