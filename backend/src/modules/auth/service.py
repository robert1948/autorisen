"""Authentication service utilities backed by the database and custom JWT."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_EXP_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def _hash(password: str, salt: Optional[bytes] = None) -> str:
    salt = salt or os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + dk).decode()


def _verify(password: str, encoded: str) -> bool:
    raw = base64.b64decode(encoded.encode())
    salt, dk = raw[:16], raw[16:]
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(dk, test)


def register(db: Session, email: str, password: str, full_name: Optional[str]) -> None:
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing:
        raise ValueError("user exists")

    hashed = _hash(password)
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


def _b64url(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _jwt_sign(payload: dict, expires_seconds: int) -> Tuple[str, datetime]:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    exp = now + expires_seconds
    payload = {**payload, "iat": now, "exp": exp}
    enc_header = _b64url(json.dumps(header, separators=(",", ":")).encode())
    enc_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = b".".join([enc_header, enc_payload])
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    token = b".".join([signing_input, _b64url(signature)]).decode()
    return token, datetime.fromtimestamp(exp, tz=timezone.utc)


def _pad_b64(segment: str) -> str:
    return segment + "=" * (-len(segment) % 4)


def _jwt_decode(token: str) -> dict:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = base64.urlsafe_b64decode(_pad_b64(signature_b64))
    expected_sig = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("bad sig")

    payload = json.loads(base64.urlsafe_b64decode(_pad_b64(payload_b64)).decode())
    if payload.get("exp", 0) < int(time.time()):
        raise ValueError("expired")
    return payload


def login(db: Session, email: str, password: str) -> Tuple[str, datetime]:
    user = db.scalar(select(models.User).where(models.User.email == email))
    if not user or not _verify(password, user.hashed_password):
        raise ValueError("bad credentials")

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    return _jwt_sign({"sub": email}, JWT_EXP_MIN * 60)


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
