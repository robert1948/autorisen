"""Authentication service utilities (in-memory for MVP)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

import jwt
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
    """Testing helper: clear in-memory user store."""

    _users.clear()


def register(email: str, password: str, full_name: Optional[str] = None) -> schemas.UserProfile:
    """Register a new user; raise ValueError if the email already exists."""

    if email in _users:
        raise ValueError("user already exists")

    hashed = _pwd_context.hash(password)
    _users[email] = {
        "email": email,
        "full_name": full_name,
        "hashed_password": hashed,
    }
    return schemas.UserProfile(email=email, full_name=full_name)


def _verify_credentials(email: str, password: str) -> Dict[str, object]:
    record = _users.get(email)
    if not record:
        raise ValueError("user not found")
    if not _pwd_context.verify(password, record["hashed_password"]):
        raise ValueError("invalid credentials")
    return record


def _issue_token(email: str, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    expire = _now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_MINUTES))
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire


def login(email: str, password: str) -> Tuple[str, datetime]:
    """Authenticate credentials and return (token, expires_at)."""

    _verify_credentials(email, password)
    return _issue_token(email)


def current_user(token: str) -> str:
    """Validate token and return the associated email."""

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise ValueError("invalid token") from exc

    email = decoded.get("sub")
    if not email or email not in _users:
        raise ValueError("user not found")
    return email


def profile(email: str) -> Optional[schemas.UserProfile]:
    """Return profile for email if present."""

    record = _users.get(email)
    if not record:
        return None
    return schemas.UserProfile(email=email, full_name=record.get("full_name"))
