"""
FastAPI router implementing the Auth V2 endpoints expected by the test suite.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserProfile

router = APIRouter(prefix="/auth/v2", tags=["auth-v2"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "local-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 30))
)

VALID_ROLES = {"client", "developer"}


class PasswordValidationRequest(BaseModel):
    password: str = Field(..., min_length=1)


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1)
    user_role: str = Field(..., description="Either client or developer")
    company_name: Optional[str] = None
    industry: Optional[str] = None
    project_budget: Optional[str] = None
    skills: Optional[str] = None
    tos_accepted: bool = Field(False, description="Must be true to register")

    @validator("user_role")
    def _validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_ROLES:
            raise ValueError("invalid user_role")
        return normalized

    @validator("password")
    def _validate_password(cls, value: str) -> str:
        result = evaluate_password_strength(value)
        if not result["valid"]:
            raise ValueError("password does not meet strength requirements")
        return value

    @validator("full_name")
    def _validate_full_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("full_name is required")
        return normalized


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


def evaluate_password_strength(password: str) -> Dict[str, Any]:
    requirements = {
        "min_length": len(password) >= 12,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"\d", password)),
        "special": bool(re.search(r"[^\w\s]", password)),
    }
    score = 20 * sum(requirements.values())
    valid = score >= 80
    message = (
        "Password meets strength requirements."
        if valid
        else "Password is too weak; please meet all strength requirements."
    )
    return {
        "valid": valid,
        "score": score,
        "message": message,
        "requirements": requirements,
    }


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(" ", 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""
    return first, last


def send_welcome_email_task(email: str) -> None:  # pragma: no cover - patched in tests
    """Placeholder background task. Tests patch this to observe behaviour."""
    return None


@router.get("/validate-email")
def validate_email(email: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    normalized = _normalize_email(email)
    try:
        EmailStr.validate(normalized)
    except ValueError:
        return {"available": False, "reason": "invalid_format"}

    exists = (
        db.query(User)
        .filter(func.lower(User.email) == normalized.lower())
        .first()
    )
    if exists:
        return {"available": False, "reason": "already_registered"}
    return {"available": True}


@router.post("/validate-password")
def validate_password(payload: PasswordValidationRequest):
    result = evaluate_password_strength(payload.password)
    return result


@router.post("/register")
def register_user(
    payload: RegistrationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not payload.tos_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms of service must be accepted.",
        )

    normalized_email = _normalize_email(payload.email)

    existing = (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    password_hash = pwd_context.hash(payload.password)
    first_name, last_name = _split_full_name(payload.full_name)

    user = User(
        email=normalized_email,
        hashed_password=password_hash,
        full_name=payload.full_name.strip(),
        first_name=first_name[:50],
        last_name=last_name[:50],
        role=payload.user_role,
        company_name=(payload.company_name or "").strip(),
        is_active=True,
        is_email_verified=False,
    )

    db.add(user)
    db.flush()

    profile_payload = {
        "industry": payload.industry,
        "project_budget": payload.project_budget,
        "skills": payload.skills,
        "user_role": payload.user_role,
    }
    profile_payload = {k: v for k, v in profile_payload.items() if v is not None}
    profile = UserProfile(user_id=user.id, profile=profile_payload or {})
    db.add(profile)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        ) from exc

    background_tasks.add_task(send_welcome_email_task, user.email)

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "user_role": user.role,
    }


@router.post("/login")
def login_user(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    normalized_email = _normalize_email(payload.email)
    user = (
        db.query(User)
        .filter(func.lower(User.email) == normalized_email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = _create_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        token_type="access",
    )
    refresh_token = _create_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES,
        token_type="refresh",
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "user_role": user.role,
        },
    }


def _create_token(
    *,
    user_id: str,
    email: str,
    role: str,
    minutes: int,
    token_type: str,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


__all__ = [
    "router",
    "evaluate_password_strength",
    "send_welcome_email_task",
]
