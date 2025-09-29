"""Health-related API endpoints."""

from __future__ import annotations

import os
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health status", response_model=dict)
def health_status() -> dict[str, str]:
    """Return service health information."""
    return {"status": "ok", "env": os.getenv("APP_ENV", "development")}


@router.get("/alive", summary="Liveness probe", response_model=dict)
def alive() -> dict[str, bool]:
    """Return a simple liveness payload."""
    return {"alive": True}


@router.get("/ping", summary="Ping endpoint", response_model=dict)
def ping() -> dict[str, str]:
    """Return a ping/pong payload for quick connectivity tests."""
    return {"ping": "pong"}
