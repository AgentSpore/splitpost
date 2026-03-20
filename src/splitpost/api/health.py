from fastapi import APIRouter

from ..core.deps import DbDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: DbDep):
    cursor = await db.execute("SELECT COUNT(*) as c FROM posts")
    row = await cursor.fetchone()
    return {"status": "healthy", "posts": row["c"]}
