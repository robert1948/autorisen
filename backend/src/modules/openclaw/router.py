"""OpenClaw router exposing task and approval APIs."""

from __future__ import annotations

from typing import Any

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user, require_roles
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .models import (
    OpenClawAggregationResponse,
    OpenClawApprovalDecisionRequest,
    OpenClawApprovalDecisionResponse,
    OpenClawEvent,
    OpenClawRetentionResponse,
    OpenClawStatsResponse,
    OpenClawTaskCreateRequest,
    OpenClawTaskCreateResponse,
    OpenClawTaskResponse,
)
from .service import (
    OpenClawApprovalNotFoundError,
    OpenClawService,
    OpenClawTaskNotFoundError,
)

router = APIRouter(prefix="/openclaw", tags=["openclaw"])
_service = OpenClawService()


def _user_id(user: Any) -> str:
    raw_id = getattr(user, "id", None)
    if raw_id is None:
        return "unknown"
    return str(raw_id)


@router.get("/health")
def openclaw_health(current_user: Any = Depends(get_verified_user)):
    """Health endpoint for OpenClaw module reachability and auth wiring."""
    return {
        "status": "ok",
        "module": "openclaw",
        "user_id": _user_id(current_user),
    }


@router.post("/tasks", response_model=OpenClawTaskCreateResponse)
def create_task(
    payload: OpenClawTaskCreateRequest,
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    return _service.create_task(payload, actor_id=_user_id(current_user), db=db)


@router.get("/tasks/{task_id}", response_model=OpenClawTaskResponse)
def get_task(
    task_id: str,
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    _ = current_user
    try:
        return _service.get_task(task_id, db=db)
    except OpenClawTaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="openclaw task not found",
        ) from None


@router.get("/events", response_model=list[OpenClawEvent])
def list_events(
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    _ = current_user
    return _service.list_events(db=db)


@router.get("/stats", response_model=OpenClawStatsResponse)
def openclaw_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    actor_id = _user_id(current_user)
    role = str(getattr(current_user, "role", "")).lower()
    is_admin = role == "admin"
    return _service.get_stats(
        db,
        actor_id=actor_id,
        is_admin=is_admin,
        window_days=days,
    )


@router.post("/retention/run", response_model=OpenClawRetentionResponse)
def run_retention(
    retention_days: int = Query(30, ge=7, le=365),
    dry_run: bool = Query(True),
    _admin: Any = Depends(require_roles("admin")),
    db: Session = Depends(get_session),
):
    return _service.run_retention(
        db,
        retention_days=retention_days,
        dry_run=dry_run,
    )


@router.post("/aggregation/run", response_model=OpenClawAggregationResponse)
def run_aggregation(
    days_back: int = Query(7, ge=1, le=90),
    dry_run: bool = Query(True),
    current_user: Any = Depends(require_roles("admin")),
    db: Session = Depends(get_session),
):
    return _service.run_daily_aggregation(
        db,
        actor_id=_user_id(current_user),
        days_back=days_back,
        dry_run=dry_run,
    )


@router.get("/tasks/{task_id}/events", response_model=list[OpenClawEvent])
def list_task_events(
    task_id: str,
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    _ = current_user
    try:
        return _service.list_task_events(task_id, db=db)
    except OpenClawTaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="openclaw task not found",
        ) from None


@router.post(
    "/approvals/{approval_id}/approve",
    response_model=OpenClawApprovalDecisionResponse,
)
def approve_task(
    approval_id: str,
    payload: OpenClawApprovalDecisionRequest,
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    try:
        return _service.decide_approval(
            approval_id=approval_id,
            actor_id=_user_id(current_user),
            request=payload,
            approved=True,
            db=db,
        )
    except OpenClawApprovalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="openclaw approval not found",
        ) from None


@router.post(
    "/approvals/{approval_id}/reject",
    response_model=OpenClawApprovalDecisionResponse,
)
def reject_task(
    approval_id: str,
    payload: OpenClawApprovalDecisionRequest,
    current_user: Any = Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    try:
        return _service.decide_approval(
            approval_id=approval_id,
            actor_id=_user_id(current_user),
            request=payload,
            approved=False,
            db=db,
        )
    except OpenClawApprovalNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="openclaw approval not found",
        ) from None
