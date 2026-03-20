from fastapi import APIRouter, HTTPException

from ..core.deps import DbDep, UserDep
from ..schemas.user import RegisterRequest, LoginRequest, AuthResponse
from ..services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: DbDep):
    try:
        return await auth_service.register(db, req.username, req.email, req.display_name, req.password)
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(409, "User already exists")
        raise HTTPException(400, str(e))


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: DbDep):
    try:
        return await auth_service.login(db, req.email, req.password)
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.get("/me")
async def me(user: UserDep):
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "display_name": user["display_name"],
        "default_tone": user["default_tone"],
    }
