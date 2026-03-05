"""SEC-001: Verify prod secret_key startup guard."""

import pytest
from pydantic import ValidationError

from backend.src.core.config import Settings


def test_prod_rejects_dev_secret_key():
    """ENV=prod with a dev- prefixed SECRET_KEY must raise."""
    with pytest.raises(ValidationError, match="SECRET_KEY must not start with 'dev-'"):
        Settings(
            ENV="prod",
            SECRET_KEY="dev-secret-change-me",
            DATABASE_URL="sqlite:///test.db",
        )


def test_prod_accepts_strong_secret_key():
    """ENV=prod with a proper SECRET_KEY must succeed."""
    s = Settings(
        ENV="prod",
        SECRET_KEY="a-very-strong-random-production-key-1234567890",
        DATABASE_URL="sqlite:///test.db",
    )
    assert s.env == "prod"
    assert s.secret_key == "a-very-strong-random-production-key-1234567890"


def test_dev_allows_dev_secret_key():
    """ENV=dev with dev- prefix is fine for local development."""
    s = Settings(
        ENV="dev",
        SECRET_KEY="dev-secret-change-me",
        DATABASE_URL="sqlite:///test.db",
    )
    assert s.env == "dev"
    assert s.secret_key == "dev-secret-change-me"
