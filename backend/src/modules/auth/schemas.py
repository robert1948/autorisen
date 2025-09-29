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


class RefreshRequest(BaseModel):
    """Payload for exchanging a refresh token for a new access token."""

    refresh_token: str


class TokenResponse(BaseModel):
    """JWT token response structure."""

    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None


class UserProfile(BaseModel):
    """Public representation of an authenticated user."""

    email: EmailStr
    full_name: Optional[str] = None
