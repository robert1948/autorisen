# backend/app/routes/auth_public.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ⚠️ DEV-ONLY in-memory store (replace with DB-backed logic later)
_users: Dict[str, str] = {}

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: str

class RegisterOut(BaseModel):
    id: int
    email: EmailStr
    name: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=RegisterOut, status_code=201)
def register(payload: RegisterIn):
    if payload.email in _users:
        raise HTTPException(status_code=400, detail="Email already registered")
    _users[payload.email] = payload.password
    return {"id": 1, "email": payload.email, "name": payload.name}

@router.post("/login")
def login(payload: LoginIn):
    if _users.get(payload.email) != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Return a fake token for now; replace with JWT later
    return {"access_token": "dev-token", "token_type": "bearer"}

@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    if authorization != "Bearer dev-token":
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"email": "local1@example.com", "name": "Local User"}
