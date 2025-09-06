"""Minimal auth dependency layer for tests.
Provides get_current_user returning a dummy user dict when real auth system
is not required. This prevents import errors in routes depending on auth.
"""

from __future__ import annotations
from typing import Any


async def get_current_user() -> dict[str, Any]:  # noqa: D401
    return {"id": "test-user", "role": "user"}
