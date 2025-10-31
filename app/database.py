"""
Database convenience layer that mirrors the backend package exports.

Tests import `app.database` directly, so we expose the same objects FastAPI uses.
"""

from __future__ import annotations

try:
    from backend.src.db.base import Base  # type: ignore
    from backend.src.db.session import SessionLocal, engine, get_db  # type: ignore
except ImportError as exc:  # pragma: no cover - surface helpful error in tests
    raise RuntimeError("Unable to import backend database session") from exc

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
