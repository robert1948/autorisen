from pydantic import BaseModel, EmailStr
from typing import Optional, Dict


class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    onboarding: Optional[Dict[str, bool]] = None  # ✅ Add this

    class Config:
        orm_mode = True


class SuccessMessage(BaseModel):
    success: bool = True
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str
