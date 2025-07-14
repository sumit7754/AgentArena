from pydantic import BaseModel, EmailStr
from typing import Optional
from ..models.enums import UserRole

class UserRegisterRequest(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    role : str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: Optional[str]
    role: UserRole
    isActive: bool
    isEmailVerified: bool

    class Config:
        from_attributes = True