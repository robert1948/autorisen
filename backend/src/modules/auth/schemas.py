"""Pydantic schemas for authentication flows."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Incoming payload to register a new user."""

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    """Incoming payload to authenticate an existing user."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response structure."""

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class UserProfile(BaseModel):
    """Public representation of an authenticated user."""

    email: EmailStr
    full_name: Optional[str] = None
    created_at: datetime
