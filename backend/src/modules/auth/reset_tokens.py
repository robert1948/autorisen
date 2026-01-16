from __future__ import annotations

import hashlib
import hmac
import os

from backend.src.core.config import settings


def hmac_sha256_hex(token: str) -> str:
    """Return an HMAC-SHA256 hex digest of the provided token.

    Uses RESET_TOKEN_SECRET when set, otherwise falls back to SECRET_KEY.
    """

    secret = (
        os.getenv("RESET_TOKEN_SECRET")
        or settings.reset_token_secret
        or settings.secret_key
        or ""
    ).encode()
    msg = (token or "").encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()
