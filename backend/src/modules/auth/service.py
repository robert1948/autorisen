"""Authentication and registration service utilities."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, cast
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.db import models
from backend.src.modules.auth.schemas import UserRole
from backend.src.services.security import (
    create_jwt,
    decode_jwt,
    hash_password,
    verify_password,
)

REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
TEMP_TOKEN_PURPOSE = "register_step1"
ACCESS_TOKEN_PURPOSE = "access"
PASSWORD_RESET_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_TTL_MINUTES", "30"))
TERMS_VERSION_DEFAULT = "v1"


class DuplicateEmailError(ValueError):
    """Raised when a registration hits a unique email constraint."""



def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _generate_refresh_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")


def _refresh_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _password_reset_hash(token: str) -> str:
    secret = settings.secret_key.encode()
    return hmac.new(secret, token.encode(), hashlib.sha256).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _is_unique_violation(exc: IntegrityError) -> bool:
    orig = getattr(exc, "orig", None)
    pgcode = getattr(orig, "pgcode", None)
    if pgcode == "23505":
        return True
    message = str(orig or exc).lower()
    return "unique constraint" in message or "unique violation" in message


def _token_version_for(user: Any, *, default: int = 0) -> int:
    raw_version = getattr(user, "token_version", default)
    try:
        version = int(raw_version)
    except (TypeError, ValueError):
        return default
    return version if version >= 0 else default


def _bool_attr(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return bool(value)


def ensure_email_available(db: Session, email: str) -> None:
    """Raise ValueError if the email is already taken."""
    normalized = _normalize_email(email)
    existing = db.scalar(
        select(models.User).where(func.lower(models.User.email) == normalized)
    )
    if existing:
        raise DuplicateEmailError("Email already registered.")


def begin_registration(
    db: Session,
    *,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role: UserRole,
    terms_accepted: Optional[bool] = None,
    terms_version: Optional[str] = None,
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
    if terms_accepted is True:
        payload["terms_accepted"] = True
        payload["terms_version"] = terms_version or TERMS_VERSION_DEFAULT
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
    terms_accepted = bool(payload.get("terms_accepted"))
    terms_version = payload.get("terms_version") or TERMS_VERSION_DEFAULT

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
    if terms_accepted:
        user.terms_accepted_at = now
        user.terms_version = terms_version

    credential = models.Credential(
        user=user,
        provider="password",
        provider_uid=normalized_email,
        secret_hash=payload["password_hash"],
    )

    setattr(user, "profile", models.UserProfile(profile=profile))
    try:
        db.add(user)
        db.add(credential)

        # Ensure PKs are available before generating tokens
        db.flush()

        refresh_token = _generate_refresh_token()
        _create_session(db, user, refresh_token)

        token_version = _token_version_for(user)
        access_payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "purpose": ACCESS_TOKEN_PURPOSE,
            "jti": str(uuid4()),
            "token_version": token_version,
        }
        access_token, expires_at = create_jwt(
            access_payload, settings.access_token_ttl_minutes
        )

        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _is_unique_violation(exc):
            raise DuplicateEmailError("Email already registered.") from exc
        raise

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
    user = db.scalar(
        select(models.User).where(func.lower(models.User.email) == normalized_email)
    )
    if user is None:
        raise ValueError("bad credentials")

    stored_hash = cast(Optional[str], getattr(user, "hashed_password", None))
    if not stored_hash or not verify_password(password, stored_hash):
        raise ValueError("bad credentials")

    now = datetime.now(timezone.utc)
    setattr(user, "last_login_at", now)
    db.add(user)

    refresh_token = _generate_refresh_token()
    _create_session(
        db, user, refresh_token, user_agent=user_agent, ip_address=ip_address
    )

    token_version = _token_version_for(user)
    access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
        "jti": str(uuid4()),
        "token_version": token_version,
    }
    access_token, expires_at = create_jwt(
        access_payload, settings.access_token_ttl_minutes
    )
    db.commit()
    return access_token, expires_at, refresh_token


def current_user(db: Session, token: str) -> models.User:
    payload = decode_jwt(token)
    if payload.get("purpose") != ACCESS_TOKEN_PURPOSE:
        raise ValueError("invalid token payload")
    email = payload.get("sub")
    if not email:
        raise ValueError("invalid token payload")

    user = db.scalar(
        select(models.User).where(
            func.lower(models.User.email) == _normalize_email(email)
        )
    )
    if user is None:
        raise ValueError("user not found")

    if not _bool_attr(getattr(user, "is_active", True), default=False):
        raise ValueError("user not found")

    expected_version = _token_version_for(user)
    raw_version = payload.get("token_version", 0)
    try:
        token_version = int(raw_version)
    except (TypeError, ValueError):
        token_version = 0
    if token_version != expected_version:
        raise ValueError("invalid token payload")

    payload_user_id = payload.get("user_id")
    if payload_user_id and str(payload_user_id) != str(user.id):
        raise ValueError("invalid token payload")

    return user


def refresh_access_token(db: Session, refresh_token: str) -> Tuple[str, datetime, str]:
    token_hash = _refresh_hash(refresh_token)
    session = db.scalar(
        select(models.Session).where(
            models.Session.token_hash == token_hash, models.Session.revoked_at.is_(None)
        )
    )
    now = datetime.now(timezone.utc)
    if session is None:
        raise ValueError("invalid refresh token")

    expires_at_raw = cast(Optional[datetime], getattr(session, "expires_at", None))
    if expires_at_raw is None:
        raise ValueError("invalid refresh token")

    expires_at = _ensure_aware(expires_at_raw)
    if expires_at <= now:
        raise ValueError("invalid refresh token")

    user = session.user
    if user is None:
        raise ValueError("user not found")

    if not _bool_attr(getattr(user, "is_active", True), default=False):
        raise ValueError("user not found")

    token_version = _token_version_for(user)
    new_access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
        "jti": str(uuid4()),
        "token_version": token_version,
    }
    new_access, expires_at = create_jwt(
        new_access_payload, settings.access_token_ttl_minutes
    )
    new_refresh = _generate_refresh_token()

    setattr(session, "token_hash", _refresh_hash(new_refresh))
    setattr(session, "expires_at", now + timedelta(days=REFRESH_TOKEN_DAYS))
    db.add(session)
    db.commit()

    return new_access, expires_at, new_refresh


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    token_hash = _refresh_hash(refresh_token)
    session = db.scalar(
        select(models.Session).where(models.Session.token_hash == token_hash)
    )
    if session:
        setattr(session, "revoked_at", datetime.now(timezone.utc))
        db.add(session)
        db.commit()


def initiate_password_reset(
    db: Session,
    email: str,
    *,
    ttl_minutes: int = PASSWORD_RESET_TTL_MINUTES,
) -> Optional[Tuple[models.User, str, datetime]]:
    """
    Create a one-time password reset token for the given email.

    Returns (user, raw_token, expires_at) when a user is found; otherwise None.
    """
    normalized_email = _normalize_email(email)
    user = db.scalar(
        select(models.User).where(func.lower(models.User.email) == normalized_email)
    )
    if user is None:
        return None
    if not _bool_attr(getattr(user, "is_active", True), default=False):
        return None

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=int(ttl_minutes))

    # Invalidate any previous unused tokens.
    existing_tokens = list(
        db.scalars(
            select(models.PasswordResetToken).where(
                models.PasswordResetToken.user_id == user.id,
                models.PasswordResetToken.used_at.is_(None),
            )
        )
    )
    for token in existing_tokens:
        setattr(token, "used_at", now)
        db.add(token)

    raw_token = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
    token_hash = _password_reset_hash(raw_token)

    record = models.PasswordResetToken(
        user=user,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()

    return user, raw_token, expires_at


def complete_password_reset(
    db: Session,
    token: str,
    new_password: str,
) -> models.User:
    """
    Reset the password for a user using the supplied raw token.

    Raises ValueError if the token is invalid or expired.
    """
    normalized_token = (token or "").strip()
    if not normalized_token:
        raise ValueError("Invalid reset token")

    token_hash = _password_reset_hash(normalized_token)
    record = db.scalar(
        select(models.PasswordResetToken).where(
            models.PasswordResetToken.token_hash == token_hash
        )
    )

    if not record:
        raise ValueError("Invalid reset token")

    now = datetime.now(timezone.utc)
    expires_at = cast(Optional[datetime], getattr(record, "expires_at", None))
    if expires_at is None:
        raise ValueError("Invalid reset token")
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    used_at = cast(Optional[datetime], getattr(record, "used_at", None))
    if used_at is not None and used_at.tzinfo is None:
        used_at = used_at.replace(tzinfo=timezone.utc)

    if used_at is not None or expires_at <= now:
        raise ValueError("Reset token expired")

    user = record.user
    if user is None:
        raise ValueError("Invalid reset token")
    if not _bool_attr(getattr(user, "is_active", True), default=False):
        raise ValueError("Invalid reset token")

    current_version = _token_version_for(user)
    password_hash = hash_password(new_password)
    setattr(user, "hashed_password", password_hash)
    setattr(user, "password_changed_at", now)
    setattr(user, "token_version", current_version + 1)

    # Keep Credential table in sync when present.
    credential = db.scalar(
        select(models.Credential).where(
            models.Credential.user_id == user.id,
            models.Credential.provider == "password",
        )
    )
    if credential:
        setattr(credential, "secret_hash", password_hash)
        setattr(credential, "last_used_at", now)
        db.add(credential)

    # Revoke outstanding sessions for safety.
    sessions = list(
        db.scalars(
            select(models.Session).where(
                models.Session.user_id == user.id, models.Session.revoked_at.is_(None)
            )
        )
    )
    for session in sessions:
        setattr(session, "revoked_at", now)
        db.add(session)

    setattr(record, "used_at", now)
    db.add(user)
    db.add(record)
    db.commit()
    return user


def social_login(
    db: Session,
    *,
    provider: str,
    provider_uid: str,
    email: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[str, datetime, str, models.User]:
    """
    Create or update a user via social login and return auth tokens.
    """
    normalized_email = _normalize_email(email)
    user: Optional[models.User] = db.scalar(
        select(models.User).where(func.lower(models.User.email) == normalized_email)
    )
    now = datetime.now(timezone.utc)

    first = (first_name or "").strip()
    last = (last_name or "").strip()
    full_name = f"{first} {last}".strip() or None

    if user is None:
        random_password = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("=")
        password_hash = hash_password(random_password)
        user = models.User(
            email=normalized_email,
            first_name=first or "",
            last_name=last or "",
            full_name=full_name,
            hashed_password=password_hash,
            role=UserRole.CUSTOMER.value,  # enum value for consistency
            is_active=True,
            is_email_verified=True,
            password_changed_at=now,
        )
        db.add(user)
        db.flush()  # ensure user.id for subsequent ops
    else:
        existing_user = cast(models.User, user)
        updated = False
        if first and not getattr(existing_user, "first_name", ""):
            setattr(existing_user, "first_name", first)
            updated = True
        if last and not getattr(existing_user, "last_name", ""):
            setattr(existing_user, "last_name", last)
            updated = True
        if full_name and not getattr(existing_user, "full_name", None):
            setattr(existing_user, "full_name", full_name)
            updated = True
        if getattr(existing_user, "is_email_verified", None) is False:
            setattr(existing_user, "is_email_verified", True)
            updated = True
        setattr(existing_user, "last_login_at", now)
        if updated:
            db.add(existing_user)
        user = existing_user

    # Credential
    credential: Optional[models.Credential] = db.scalar(
        select(models.Credential).where(
            models.Credential.user_id == user.id,
            models.Credential.provider == provider,
        )
    )
    if credential is None:
        credential = models.Credential(
            user=user,
            provider=provider,
            provider_uid=provider_uid,
            secret_hash=None,
            last_used_at=now,
        )
        db.add(credential)
    else:
        credential = cast(models.Credential, credential)
        setattr(credential, "provider_uid", provider_uid)
        setattr(credential, "last_used_at", now)
        db.add(credential)

    # Session
    refresh_token = _generate_refresh_token()
    _create_session(
        db,
        user,
        refresh_token,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    # Access token
    token_version = _token_version_for(user)
    access_payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": ACCESS_TOKEN_PURPOSE,
        "jti": str(uuid4()),
        "token_version": token_version,
    }
    access_token, expires_at = create_jwt(
        access_payload, settings.access_token_ttl_minutes
    )

    db.commit()
    return access_token, expires_at, refresh_token, user


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
