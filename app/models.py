"""
Thin re-export layer so tests can import ORM models via `app.models`.
"""

from __future__ import annotations

from backend.src.db import models as _models  # type: ignore
from backend.src.db.base import Base  # type: ignore

# Re-export commonly used models
User = _models.User
UserProfile = _models.UserProfile
Session = _models.Session

# Provide aliases expected by tests (password_hash vs hashed_password)
if not hasattr(User, "password_hash"):
    setattr(User, "password_hash", getattr(User, "hashed_password"))

__all__ = [
    "Base",
    "User",
    "UserProfile",
    "Session",
]
