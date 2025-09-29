"""Authentication service utilities (in-memory for MVP)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from . import schemas

SECRET_KEY = os.getenv("AUTH_SECRET", "dev-secret-key")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_TOKEN_MINUTES = int(os.getenv("AUTH_ACCESS_TOKEN_MINUTES", "60"))

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_users: Dict[str, Dict[str, object]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def reset_store() -> None:
    """Testing helper to clear in-memory users."""

    _users.clear()


def _hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def _verify_password(password: str, hashed: str) -> bool:
    return _pwd_context.verify(password, hashed)


def create_user(payload: schemas.RegisterRequest) -> schemas.UserProfile:
    if payload.email in _users:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user already exists")

    created_at = _now()
    _users[payload.email] = {
        "email": payload.email,
        "full_name": payload.full_name,
        "hashed_password": _hash_password(payload.password),
        "created_at": created_at,
    }
    return schemas.UserProfile(email=payload.email, full_name=payload.full_name)


def authenticate(payload: schemas.LoginRequest) -> schemas.UserProfile:
    record = _users.get(payload.email)
    if not record or not _verify_password(payload.password, record["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    return schemas.UserProfile(email=record["email"], full_name=record.get("full_name"))


def create_access_token(user: schemas.UserProfile, expires_delta: Optional[timedelta] = None) -> schemas.TokenResponse:
    expire = _now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_MINUTES))
    payload = {"sub": user.email, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return schemas.TokenResponse(access_token=token, expires_at=expire)


def decode_token(token: str) -> schemas.UserProfile:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc

    email = decoded.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token payload")

    record = _users.get(email)
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    return schemas.UserProfile(email=record["email"], full_name=record.get("full_name"))


def bearer_token_from_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authorization header missing")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid authorization header")
    return token
