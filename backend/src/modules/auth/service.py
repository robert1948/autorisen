
"""Authentication service utilities backed by the database and custom JWT."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_EXP_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))




def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value

def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + dk).decode()


def _verify_password(password: str, stored: str) -> bool:
    raw = base64.b64decode(stored.encode())
    salt, dk = raw[:16], raw[16:]
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk, test)


def _generate_refresh_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(48)).decode().rstrip("=")


def _refresh_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _jwt_sign(payload: dict, ttl_seconds: int) -> Tuple[str, datetime]:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    exp = now + ttl_seconds
    payload = {**payload, "iat": now, "exp": exp}
    enc_header = base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":")).encode()).rstrip(b"=")
    enc_payload = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=")
    signing_input = b".".join((enc_header, enc_payload))
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    token = b".".join((signing_input, base64.urlsafe_b64encode(signature).rstrip(b"="))).decode()
    return token, datetime.fromtimestamp(exp, tz=timezone.utc)


def _pad(segment: str) -> str:
    return segment + "=" * (-len(segment) % 4)


def _jwt_decode(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = base64.urlsafe_b64decode(_pad(signature_b64))
    expected_signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("bad signature")

    payload = json.loads(base64.urlsafe_b64decode(_pad(payload_b64)).decode())
    if payload.get("exp", 0) < int(time.time()):
        raise ValueError("token expired")
    return payload


def register(db: Session, email: str, password: str, full_name: Optional[str]) -> None:
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing:
        raise ValueError("user exists")

    hashed = _hash_password(password)
    now = datetime.now(timezone.utc)

    user = models.User(
        email=email,
        full_name=full_name,
        hashed_password=hashed,
        password_changed_at=now,
    )
    credential = models.Credential(
        user=user,
        provider="password",
        provider_uid=email,
        secret_hash=hashed,
        last_used_at=None,
    )
    db.add(user)
    db.add(credential)
    db.commit()


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
    db.commit()
    return session


def login(
    db: Session,
    email: str,
    password: str,
    *,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Tuple[str, datetime, str]:
    user = db.scalar(select(models.User).where(models.User.email == email))
    if not user or not _verify_password(password, user.hashed_password):
        raise ValueError("bad credentials")

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)

    refresh_token = _generate_refresh_token()
    _create_session(db, user, refresh_token, user_agent=user_agent, ip_address=ip_address)

    access_token, expires_at = _jwt_sign({"sub": user.email}, JWT_EXP_MIN * 60)
    return access_token, expires_at, refresh_token


def current_user(db: Session, token: str) -> str:
    payload = _jwt_decode(token)
    email = payload.get("sub")
    if not email:
        raise ValueError("invalid token payload")

    user = db.scalar(select(models.User).where(models.User.email == email))
    if not user or not user.is_active:
        raise ValueError("user not found")
    return email


def profile(db: Session, email: str) -> Optional[models.User]:
    return db.scalar(select(models.User).where(models.User.email == email))


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

    new_access, expires_at = _jwt_sign({"sub": user.email}, JWT_EXP_MIN * 60)
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
