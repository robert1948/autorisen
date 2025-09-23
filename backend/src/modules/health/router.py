"""Health router for the modularized backend.

Provides lightweight endpoints used by docker-compose healthchecks and smoke tests:
- GET /alive  -> quick liveness check
- GET /ping   -> returns pong with ISO timestamp
"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/alive")
def alive():
    """Simple liveness endpoint used by compose healthchecks."""
    return {"status": "ok", "ts": datetime.now(timezone.utc).isoformat()}


@router.get("/ping")
def ping():
    """Ping endpoint that returns a pong and current timestamp."""
    return {"status": "pong", "ts": datetime.now(timezone.utc).isoformat()}
