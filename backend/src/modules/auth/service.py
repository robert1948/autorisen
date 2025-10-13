"""Authentication and registration service utilities."""

from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.db import models
from backend.src.modules.auth.schemas import UserRole
from backend.src.services.security import create_jwt, decode_jwt, hash_password, verify_password

REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
TEMP_TOKEN_PURPOSE = "register_step1"
ACCESS_TOKEN_PURPOSE = "access"


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _generate_refresh_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")


def _refresh_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_email_available(db: Session, email: str) -> None:
    """Raise ValueError if the email is already taken."""

    normalized = _normalize_email(email)
    existing = db.scalar(select(models.User).where(func.lower(models.User.email) == normalized))
    if existing:
        raise ValueError("Email already registered.")


def begin_registration(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role: UserRole,
) -> str:
    """Generate a temporary token carrying registration information."""

    ensure_email_available(db, email)
    password_hash = hash_password(password)
    normalized_email = _normalize_email(email)
    payload = {
        "sub": normalized_email,
        "email": normalized_email,
        "first_name": first_name,
        "last_name": last_name,
        "role": role.value,
        "password_hash": password_hash,
        "purpose": TEMP_TOKEN_PURPOSE,
    }
    token, _ = create_jwt(payload, settings.temp_token_ttl_minutes)
    return token


def complete_registration(
    db: Session,
    *,
    temp_token: str,
    company_name: str,
    profile: Dict[str, Any],
) -> Tuple[str, str, datetime, models.User]:
    """Persist the user and profile using the temporary token payload."""

    payload = decode_jwt(temp_token)
    if payload.get("purpose") != TEMP_TOKEN_PURPOSE:
        raise ValueError("Invalid registration token.")

    normalized_email = _normalize_email(payload["email"])
    ensure_email_available(db, normalized_email)

    now = datetime.now(timezone.utc)

    user = models.User(
        email=normalized_email,
        first_name=payload["first_name"],
        last_name=payload["last_name"],
        full_name=f"{payload['first_name']} {payload['last_name']}".strip(),
        role=payload["role"],
        hashed_password=payload["password_hash"],
        company_name=company_name,
        is_email_verified=False,
        password_changed_at=now,
    )

    credential = models.Credential(
        user=user,
        provider="password",
        provider_uid=normalized_email,
        secret_hash=payload["password_hash"],
    )

    user.profile = models.UserProfile(profile=profile)
    db.add(user)
    db.add(credential)

    refresh_token = _generate_refresh_token()
    session = _create_session(db, user, refresh_token)

    access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
    }
    access_token, expires_at = create_jwt(access_payload, settings.access_token_ttl_minutes)

    db.commit()

    return access_token, refresh_token, expires_at, user


def _create_session(
    db: Session,
    user: models.User,
    refresh_token: str,
    *,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> models.Session:
    session = models.Session(
        user=user,
        token_hash=_refresh_hash(refresh_token),
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS),
    )
    db.add(session)
    return session


def login(
    db: Session,
    email: str,
    password: str,
    *,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[str, datetime, str]:
    normalized_email = _normalize_email(email)
    user = db.scalar(select(models.User).where(func.lower(models.User.email) == normalized_email))
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("bad credentials")

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)

    refresh_token = _generate_refresh_token()
    session = _create_session(db, user, refresh_token, user_agent=user_agent, ip_address=ip_address)

    access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
    }
    access_token, expires_at = create_jwt(access_payload, settings.access_token_ttl_minutes)
    db.commit()
    return access_token, expires_at, refresh_token


def current_user(db: Session, token: str) -> models.User:
    payload = decode_jwt(token)
    email = payload.get("sub")
    if not email:
        raise ValueError("invalid token payload")

    user = db.scalar(select(models.User).where(func.lower(models.User.email) == _normalize_email(email)))
    if not user or not user.is_active:
        raise ValueError("user not found")
    return user


def refresh_access_token(db: Session, refresh_token: str) -> Tuple[str, datetime, str]:
    token_hash = _refresh_hash(refresh_token)
    session = db.scalar(
        select(models.Session).where(models.Session.token_hash == token_hash, models.Session.revoked_at.is_(None))
    )
    now = datetime.now(timezone.utc)
    if not session:
        raise ValueError("invalid refresh token")
    expires_at = _ensure_aware(session.expires_at)
    if expires_at <= now:
        raise ValueError("invalid refresh token")

    user = session.user
    if not user or not user.is_active:
        raise ValueError("user not found")

    new_access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
    }
    new_access, expires_at = create_jwt(new_access_payload, settings.access_token_ttl_minutes)
    new_refresh = _generate_refresh_token()

    session.token_hash = _refresh_hash(new_refresh)
    session.expires_at = now + timedelta(days=REFRESH_TOKEN_DAYS)
    db.add(session)
    db.commit()

    return new_access, expires_at, new_refresh


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = _refresh_hash(refresh_token)
    session = db.scalar(select(models.Session).where(models.Session.token_hash == token_hash))
    if session:
        session.revoked_at = datetime.now(timezone.utc)
        db.add(session)
        db.commit()


def record_analytics_event(
    db: Session,
    *,
    event_type: str,
    step: Optional[str],
    role: Optional[str],
    details: Optional[Dict[str, Any]],
) -> None:
    event = models.AnalyticsEvent(
        event_type=event_type,
        step=step,
        role=role,
        details=details or {},
    )
    db.add(event)
    db.commit()
