"""Application-level encryption helpers for sensitive fields (MFA secrets, etc.).

Uses Fernet symmetric encryption from the ``cryptography`` library.
The key is sourced from ``settings.mfa_encryption_key``.

If the key is not configured, encrypt is a no-op (returns plaintext) and
decrypt gracefully handles both encrypted and plaintext values.  This allows
rolling out encryption without a hard migration — new secrets are encrypted,
existing plaintext secrets continue to work until the user re-enrols or an
admin runs a backfill script.
"""

from __future__ import annotations

import logging

from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger(__name__)

# Lazy-loaded singleton — avoids import-time dependency on settings.
_fernet: Fernet | None = None
_fernet_loaded: bool = False


def _get_fernet() -> Fernet | None:
    """Return a Fernet instance if MFA_ENCRYPTION_KEY is configured."""
    global _fernet, _fernet_loaded
    if not _fernet_loaded:
        from backend.src.core.config import settings

        key = settings.mfa_encryption_key
        if key:
            try:
                _fernet = Fernet(key.encode() if isinstance(key, str) else key)
            except Exception:
                log.error("Invalid MFA_ENCRYPTION_KEY — encryption disabled")
                _fernet = None
        else:
            log.warning("MFA_ENCRYPTION_KEY not set — MFA secrets stored unencrypted")
            _fernet = None
        _fernet_loaded = True
    return _fernet


def reset_fernet() -> None:
    """Reset the cached Fernet instance (useful for testing)."""
    global _fernet, _fernet_loaded
    _fernet = None
    _fernet_loaded = False


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a plaintext secret.  Returns ciphertext or plaintext if no key."""
    f = _get_fernet()
    if f is None:
        return plaintext
    return f.encrypt(plaintext.encode()).decode()


def decrypt_secret(stored: str) -> str:
    """Decrypt a stored secret.

    Handles three cases:
    1. Encrypted value → decrypt
    2. Plaintext (pre-encryption) → return as-is
    3. Invalid/corrupted → raise
    """
    f = _get_fernet()
    if f is None:
        # No key configured — assume stored value is plaintext
        return stored
    try:
        return f.decrypt(stored.encode()).decode()
    except InvalidToken:
        # Likely a pre-encryption plaintext secret (base32 TOTP seed).
        # Validate it looks like a base32 string before accepting.
        if _looks_like_base32(stored):
            log.info("Decrypting MFA secret as legacy plaintext (pre-encryption)")
            return stored
        raise ValueError("MFA secret is corrupted — cannot decrypt")


def _looks_like_base32(value: str) -> bool:
    """Quick check whether a string looks like a base32-encoded TOTP secret."""
    import re

    return bool(re.fullmatch(r"[A-Z2-7=]+", value.upper())) and 16 <= len(value) <= 64
