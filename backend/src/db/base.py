"""SQLAlchemy declarative base with backwards compatibility."""

from __future__ import annotations

try:  # SQLAlchemy 2.x
    from sqlalchemy.orm import DeclarativeBase as _DeclarativeBase

    class Base(_DeclarativeBase):
        """Project-wide declarative base class."""

        pass

except ImportError:  # pragma: no cover - fallback for SQLAlchemy < 2.0
    from sqlalchemy.orm import declarative_base as _declarative_base

    Base = _declarative_base()  # type: ignore[assignment]
