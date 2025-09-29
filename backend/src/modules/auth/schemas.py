"""Pydantic schemas for authentication flows."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    """Incoming payload to register a new user."""

    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Incoming payload to authenticate an existing user."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response structure."""

    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None


class UserProfile(BaseModel):
    """Public representation of an authenticated user."""

    email: EmailStr
    full_name: Optional[str] = None
