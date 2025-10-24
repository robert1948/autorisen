"""Security helpers for password hashing and JWT handling."""

from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import bcrypt
from jose import ExpiredSignatureError, JWTError, jwt

from backend.src.core.config import settings

_JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the provided password."""

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Check whether the provided password matches the stored hash."""

    try:
        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            return True
    except (ValueError, TypeError):
        pass

    # Fallback for legacy PBKDF2 hashes (base64(salt + hash))
    try:
        raw = base64.b64decode(hashed_password.encode())
    except (ValueError, TypeError):
        return False
    if len(raw) < 32:
        return False
    salt, digest = raw[:16], raw[16:]
    test = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hmac.compare_digest(digest, test)


def _ensure_expires_delta(expires_in: timedelta | int) -> timedelta:
    if isinstance(expires_in, timedelta):
        return expires_in
    return timedelta(minutes=expires_in)


def create_jwt(
    payload: Dict[str, Any], expires_in: timedelta | int
) -> Tuple[str, datetime]:
    """Create a signed JWT containing the payload."""

    expires_delta = _ensure_expires_delta(expires_in)
    now = datetime.now(timezone.utc)
    expire_at = now + expires_delta
    with_claims = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int(expire_at.timestamp()),
    }
    token = jwt.encode(with_claims, settings.secret_key, algorithm=_JWT_ALGORITHM)
    return token, expire_at


def decode_jwt(token: str, *, verify_exp: bool = True) -> Dict[str, Any]:
    """Decode a JWT and return the payload."""

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[_JWT_ALGORITHM],
            options={"verify_exp": verify_exp},
        )
    except ExpiredSignatureError as exc:  # pragma: no cover
        raise ValueError("token expired") from exc
    except JWTError as exc:  # pragma: no cover - pass through for callers
        raise ValueError("invalid token") from exc
