"""Capsule module — FastAPI router for workflow capsule operations."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.db import models

from .schemas import CapsuleListResponse, CapsuleRunRequest, CapsuleRunResponse
from .service import CapsuleService

log = logging.getLogger(__name__)

router = APIRouter(prefix="/capsules", tags=["capsules"])

# Module-level singleton (lazy init)
_service: Optional[CapsuleService] = None


def _get_service() -> CapsuleService:
    global _service
    if _service is None:
        _service = CapsuleService()
    return _service


# ------------------------------------------------------------------
# Capsule listing
# ------------------------------------------------------------------


@router.get("/", response_model=CapsuleListResponse)
def list_capsules():
    """List all available workflow capsules."""
    service = _get_service()
    return service.list_capsules()


@router.get("/{capsule_id}")
def get_capsule(capsule_id: str):
    """Get a single capsule definition by ID."""
    service = _get_service()
    capsule = service.get_capsule(capsule_id)
    if capsule is None:
        raise HTTPException(status_code=404, detail="Capsule not found")
    return capsule


# ------------------------------------------------------------------
# Capsule execution
# ------------------------------------------------------------------


@router.post("/run", response_model=CapsuleRunResponse)
async def run_capsule(
    request: CapsuleRunRequest,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    """Execute a workflow capsule.

    Runs the capsule's template-driven RAG pipeline and returns
    a structured result with citations.
    """
    service = _get_service()
    return await service.run(db, current_user, request)
