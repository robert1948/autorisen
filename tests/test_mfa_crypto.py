"""SEC-002: Tests for MFA secret encryption at rest."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet

from backend.src.core import crypto
from backend.src.core.config import settings


@pytest.fixture(autouse=True)
def _reset_fernet():
    """Ensure each test starts with a clean Fernet cache."""
    crypto.reset_fernet()
    yield
    crypto.reset_fernet()


# ── encrypt / decrypt round-trip ──────────────────────────────────────────


def test_encrypt_decrypt_round_trip(monkeypatch):
    """Encrypting then decrypting must return the original secret."""
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "mfa_encryption_key", key)

    plaintext = "JBSWY3DPEHPK3PXP"  # typical TOTP base32 secret
    ciphertext = crypto.encrypt_secret(plaintext)

    assert ciphertext != plaintext, "ciphertext should differ from plaintext"
    assert crypto.decrypt_secret(ciphertext) == plaintext


def test_decrypt_handles_legacy_plaintext(monkeypatch):
    """Pre-encryption base32 secrets should be returned as-is."""
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "mfa_encryption_key", key)

    legacy_secret = "JBSWY3DPEHPK3PXP"
    # This is NOT encrypted — should be detected as legacy plaintext
    result = crypto.decrypt_secret(legacy_secret)
    assert result == legacy_secret


def test_no_key_passthrough(monkeypatch):
    """Without MFA_ENCRYPTION_KEY, encrypt/decrypt are no-ops."""
    monkeypatch.setattr(settings, "mfa_encryption_key", None)

    secret = "JBSWY3DPEHPK3PXP"
    assert crypto.encrypt_secret(secret) == secret
    assert crypto.decrypt_secret(secret) == secret


def test_corrupted_non_base32_raises(monkeypatch):
    """Corrupted data that isn't base32 must raise ValueError."""
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(settings, "mfa_encryption_key", key)

    with pytest.raises(ValueError, match="corrupted"):
        crypto.decrypt_secret("not-valid-$#@!")


def test_invalid_key_disables_encryption(monkeypatch):
    """A malformed key should log an error and fall through to no-op."""
    monkeypatch.setattr(settings, "mfa_encryption_key", "not-a-valid-fernet-key")

    secret = "JBSWY3DPEHPK3PXP"
    # Should act as no-op since key is invalid
    assert crypto.encrypt_secret(secret) == secret
