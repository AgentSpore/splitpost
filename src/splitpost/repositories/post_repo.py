import aiosqlite


async def create_post(db: aiosqlite.Connection, user_id: int, original_text: str, tone: str, tags: str) -> int:
    cursor = await db.execute(
        "INSERT INTO posts (user_id, original_text, tone, tags) VALUES (?, ?, ?, ?)",
        (user_id, original_text, tone, tags),
    )
    await db.commit()
    return cursor.lastrowid


async def save_adaptations(db: aiosqlite.Connection, post_id: int, adaptations: list[dict]):
    for a in adaptations:
        await db.execute(
            "INSERT INTO adaptations (post_id, platform, content, char_count, hashtags) VALUES (?, ?, ?, ?, ?)",
            (post_id, a["platform"], a["content"], a["char_count"], ",".join(a.get("hashtags", []))),
        )
    await db.commit()


async def get_post_with_adaptations(db: aiosqlite.Connection, post_id: int, user_id: int) -> dict | None:
    cursor = await db.execute("SELECT * FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id))
    post = await cursor.fetchone()
    if not post:
        return None
    post = dict(post)

    cursor = await db.execute("SELECT * FROM adaptations WHERE post_id = ? ORDER BY platform", (post_id,))
    rows = await cursor.fetchall()
    post["adaptations"] = [dict(r) for r in rows]
    return post


async def list_posts(db: aiosqlite.Connection, user_id: int, limit: int = 50, offset: int = 0) -> list[dict]:
    cursor = await db.execute(
        """SELECT p.*, COUNT(a.id) as platform_count
           FROM posts p LEFT JOIN adaptations a ON a.post_id = p.id
           WHERE p.user_id = ?
           GROUP BY p.id ORDER BY p.created_at DESC LIMIT ? OFFSET ?""",
        (user_id, limit, offset),
    )
    return [dict(r) for r in await cursor.fetchall()]


async def delete_post(db: aiosqlite.Connection, post_id: int, user_id: int) -> bool:
    cursor = await db.execute("DELETE FROM posts WHERE id = ? AND user_id = ?", (post_id, user_id))
    await db.commit()
    return cursor.rowcount > 0
