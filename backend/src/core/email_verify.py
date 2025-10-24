"""Helpers for issuing and validating email verification tokens."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from backend.src.core.config import settings

ALGORITHM = "HS256"
TOKEN_TYPE = "email_verify"
DEFAULT_TTL = timedelta(hours=24)


class EmailTokenError(Exception):
    """Raised when an email verification token cannot be parsed."""


def _require_secret() -> str:
    secret = settings.email_token_secret
    if not secret:
        raise EmailTokenError("Email token secret not configured")
    return secret


def issue_email_token(
    user_id: str, token_version: int, *, ttl: timedelta | None = None
) -> str:
    """Issue a signed email verification token for the given user."""
    expires_in = ttl or DEFAULT_TTL
    payload: Dict[str, Any] = {
        "sub": user_id,
        "typ": TOKEN_TYPE,
        "v": int(token_version),
        "exp": datetime.now(timezone.utc) + expires_in,
    }
    secret = _require_secret()
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def parse_email_token(token: str) -> Dict[str, Any]:
    """Decode and validate an email verification token."""
    secret = _require_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:  # pragma: no cover - expiration path
        raise EmailTokenError("Verification link has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise EmailTokenError("Invalid verification token") from exc

    if payload.get("typ") != TOKEN_TYPE:
        raise EmailTokenError("Invalid verification token")

    if "sub" not in payload or "v" not in payload:
        raise EmailTokenError("Invalid verification token")

    return payload
