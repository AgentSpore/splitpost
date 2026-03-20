from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: str
    display_name: str = ""
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    default_tone: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
