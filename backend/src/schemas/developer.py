from pydantic import BaseModel, EmailStr
from typing import Optional, Dict


class DeveloperLoginRequest(BaseModel):
    email: EmailStr
    password: str


class DeveloperRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    company: Optional[str] = None
    portfolio: Optional[str] = None


class OnboardingUpdateRequest(BaseModel):
    onboarding: Dict[str, bool]


class DeveloperProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    company: Optional[str] = None
    portfolio: Optional[str] = None
    onboarding: Optional[Dict[str, bool]] = None

    class Config:
        orm_mode = True
