"""CSRF token helpers (generation + validation)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from typing import Final

from backend.src.core.config import settings

_SEP: Final[str] = "."
_DEFAULT_TTL: Final[int] = 60 * 60  # 1 hour


def _sign(data: str) -> str:
    secret = settings.secret_key.encode()
    return hmac.new(secret, data.encode(), hashlib.sha256).hexdigest()


def generate_csrf_token() -> str:
    """Return a signed CSRF token containing a nonce and timestamp."""

    nonce = secrets.token_urlsafe(16)
    ts = int(time.time())
    payload = f"{nonce}{_SEP}{ts}"
    sig = _sign(payload)
    return f"{payload}{_SEP}{sig}"


def validate_csrf_token(token: str, *, max_age: int = _DEFAULT_TTL) -> bool:
    """Validate the token signature and optional TTL."""

    try:
        nonce, ts_str, sig = token.split(_SEP)
    except ValueError:
        return False

    payload = f"{nonce}{_SEP}{ts_str}"
    expected_sig = _sign(payload)
    if not hmac.compare_digest(sig, expected_sig):
        return False

    if max_age:
        try:
            ts = int(ts_str)
        except ValueError:
            return False
        if time.time() - ts > max_age:
            return False

    return True
