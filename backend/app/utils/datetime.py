"""Datetime utilities.

Central place for timezone-aware UTC timestamps. Using this helper avoids the
deprecated ``datetime.utcnow()`` (Python 3.12+ deprecation warning) and ensures
all persisted timestamps are timezone-aware (UTC) matching SQLAlchemy
``DateTime(timezone=True)`` columns.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return a timezone-aware UTC ``datetime``.

    Equivalent to ``datetime.now(timezone.utc)``. Prefer this over
    ``datetime.utcnow()`` which returns a naive datetime and is deprecated.
    """
    return datetime.now(timezone.utc)


def iso_utc_now() -> str:
    """Return an ISO8601 string for the current UTC time (timezone-aware)."""
    return utc_now().isoformat()


__all__ = ["utc_now", "iso_utc_now"]
