"""Flow orchestration API leveraging the ChatKit tool adapters."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user
from backend.src.orchestrator import run_engine

from . import schemas
from .onboarding import ensure_checklist, serialize_checklist, update_task

router = APIRouter(prefix="/flows", tags=["flows"])


@router.post("/run", response_model=schemas.FlowRunResponse)
def run_flow(
    payload: schemas.FlowRunRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.FlowRunResponse:
    if not payload.tool_calls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tool_calls must contain at least one entry",
        )

    agent_ctx = None
    try:
        if payload.agent_slug:
            agent_ctx = run_engine.resolve_agent_context(
                db,
                user=user,
                agent_slug=payload.agent_slug,
                version=payload.agent_version,
            )
            effective_placement = agent_ctx.placement
        else:
            effective_placement = payload.placement
        if not effective_placement:
            raise ValueError("placement required when agent_slug is not provided")

        tool_calls = [
            run_engine.ToolCall(name=call.name, payload=call.payload) for call in payload.tool_calls
        ]
        result = run_engine.execute(
            db,
            user=user,
            placement=effective_placement,
            tool_calls=tool_calls,
            thread_id=payload.thread_id,
            agent=agent_ctx,
            idempotency_key=payload.idempotency_key,
            max_attempts=payload.max_attempts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except run_engine.RunExecutionError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": str(exc),
                "run_id": exc.run_id,
                "retryable": exc.retryable,
            },
        ) from exc

    return schemas.FlowRunResponse(
        run_id=result.run_id,
        thread_id=result.thread_id,
        placement=result.placement,
        steps=[
            schemas.RunStep(
                tool=step.tool,
                payload=step.payload,
                result=step.result,
                event_id=step.event_id,
            )
            for step in result.steps
        ],
        agent_id=result.agent_id,
        agent_version_id=result.agent_version_id,
        status=result.status,
        attempt=result.attempt,
        max_attempts=result.max_attempts,
        error_message=result.error_message,
        started_at=result.started_at,
        completed_at=result.completed_at,
    )


@router.get("/runs", response_model=list[schemas.FlowRunRecord])
def list_runs(
    placement: Optional[str] = Query(default=None, max_length=64),
    limit: int = Query(default=10, ge=1, le=100),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.FlowRunRecord]:
    stmt = (
        select(models.FlowRun)
        .where(models.FlowRun.user_id == user.id)
        .order_by(models.FlowRun.created_at.desc())
        .limit(limit)
    )
    if placement:
        stmt = stmt.where(models.FlowRun.placement == placement)

    runs = db.scalars(stmt).all()
    return [
        schemas.FlowRunRecord(
            id=run.id,
            placement=run.placement,
            thread_id=run.thread_id,
            agent_id=run.agent_id,
            agent_version_id=run.agent_version_id,
            steps=run.steps or [],
            created_at=run.created_at,
            status=run.status,
            attempt=run.attempt,
            max_attempts=run.max_attempts,
            error_message=run.error_message,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )
        for run in runs
    ]


@router.get("/onboarding/checklist", response_model=dict)
def get_onboarding_checklist(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict:
    thread_stmt = (
        select(models.ChatThread)
        .where(models.ChatThread.user_id == user.id, models.ChatThread.placement == "onboarding")
        .order_by(models.ChatThread.updated_at.desc())
    )
    thread = db.scalar(thread_stmt)
    checklist = ensure_checklist(db, user_id=user.id)
    return serialize_checklist(checklist)


@router.post("/onboarding/checklist", response_model=dict)
def update_onboarding_checklist(
    payload: schemas.ChecklistUpdateRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> dict:
    checklist = update_task(
        db,
        user_id=user.id,
        thread_id=payload.thread_id,
        task_id=payload.task_id,
        done=payload.done,
        label=payload.label,
    )
    return serialize_checklist(checklist)
