"""Account, profile, projects, and billing endpoints for dashboard modules."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user
from backend.src.modules.payments.enforcement import (
    enforce_paid_plan,
    enforce_project_limit,
)
from backend.src.modules.support.sla import estimated_response_time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from . import schemas

router = APIRouter(tags=["account"])


def _normalize_role(raw_role: str) -> str:
    role_normalized = (raw_role or "").lower()
    return "developer" if "dev" in role_normalized else "user"


def _display_name(user: models.User) -> str:
    full_name = getattr(user, "full_name", "")
    if full_name:
        return full_name
    first_name = getattr(user, "first_name", "")
    last_name = getattr(user, "last_name", "")
    combined = f"{first_name} {last_name}".strip()
    return combined or user.email


@router.get("/account/me", response_model=schemas.AccountDetails)
def get_account_me(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.AccountDetails:
    user = db.scalar(select(models.User).where(models.User.id == current_user.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.AccountDetails(
        id=str(user.id),
        email=user.email,
        display_name=_display_name(user),
        status="active" if user.is_active else "inactive",
        role=_normalize_role(getattr(user, "role", "")),
        created_at=user.created_at,
        last_login=getattr(user, "last_login_at", None),
        company_name=getattr(user, "company_name", None),
    )


@router.patch("/account/me", response_model=schemas.AccountDetails)
def update_account_me(
    payload: schemas.AccountUpdate,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.AccountDetails:
    user = db.scalar(select(models.User).where(models.User.id == current_user.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data: dict[str, Any] = {}
    if payload.first_name is not None:
        update_data["first_name"] = payload.first_name
    if payload.last_name is not None:
        update_data["last_name"] = payload.last_name
    if payload.company_name is not None:
        update_data["company_name"] = payload.company_name
    if payload.display_name is not None:
        update_data["full_name"] = payload.display_name

    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        db.execute(
            update(models.User)
            .where(models.User.id == current_user.id)
            .values(**update_data),
        )
        db.commit()
        db.refresh(user)

    return schemas.AccountDetails(
        id=str(user.id),
        email=user.email,
        display_name=_display_name(user),
        status="active" if user.is_active else "inactive",
        role=_normalize_role(getattr(user, "role", "")),
        created_at=user.created_at,
        last_login=getattr(user, "last_login_at", None),
        company_name=getattr(user, "company_name", None),
    )


@router.delete("/account/me", response_model=schemas.DeleteAccountResponse)
def delete_account_me(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.DeleteAccountResponse:
    user = db.scalar(select(models.User).where(models.User.id == current_user.id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_token_version = int(getattr(user, "token_version", 0)) + 1
    db.execute(
        update(models.User)
        .where(models.User.id == current_user.id)
        .values(
            is_active=False,
            token_version=new_token_version,
            updated_at=datetime.now(timezone.utc),
        ),
    )
    db.execute(
        update(models.Session)
        .where(models.Session.user_id == current_user.id)
        .values(revoked_at=datetime.now(timezone.utc)),
    )
    db.add(
        models.AuditEvent(
            user_id=current_user.id,
            event_type="account_deleted",
            event_data={"reason": "user_requested"},
        ),
    )
    db.commit()

    return schemas.DeleteAccountResponse(
        status="deleted",
        message="Account deactivated and sessions revoked.",
    )


@router.get("/profile/me", response_model=schemas.PersonalInfo)
def get_personal_info(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.PersonalInfo:
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == current_user.id),
    )
    if profile is None:
        profile = models.UserProfile(user_id=current_user.id, profile={})
        db.add(profile)
        db.commit()
        db.refresh(profile)

    info = (profile.profile or {}).get("personal_info", {})
    prefs = (profile.profile or {}).get("preferences", {})
    return schemas.PersonalInfo(
        phone=info.get("phone"),
        location=info.get("location"),
        timezone=info.get("timezone"),
        bio=info.get("bio"),
        avatar_url=info.get("avatar_url"),
        currency=prefs.get("currency", "ZAR"),
        updated_at=profile.updated_at,
    )


@router.patch("/profile/me", response_model=schemas.PersonalInfo)
def update_personal_info(
    payload: schemas.PersonalInfoUpdate,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.PersonalInfo:
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == current_user.id),
    )
    if profile is None:
        profile = models.UserProfile(user_id=current_user.id, profile={})
        db.add(profile)
        db.commit()
        db.refresh(profile)

    update_data = payload.model_dump(exclude_none=True)
    currency_val = update_data.pop("currency", None)

    info = dict((profile.profile or {}).get("personal_info", {}))
    for key, value in update_data.items():
        info[key] = value

    updated_profile = dict(profile.profile or {})
    updated_profile["personal_info"] = info

    if currency_val is not None:
        prefs = dict(updated_profile.get("preferences", {}))
        prefs["currency"] = currency_val
        updated_profile["preferences"] = prefs

    profile.profile = updated_profile
    db.add(profile)
    db.commit()
    db.refresh(profile)

    prefs = (profile.profile or {}).get("preferences", {})
    return schemas.PersonalInfo(
        phone=info.get("phone"),
        location=info.get("location"),
        timezone=info.get("timezone"),
        bio=info.get("bio"),
        avatar_url=info.get("avatar_url"),
        currency=prefs.get("currency", "ZAR"),
        updated_at=profile.updated_at,
    )


@router.post(
    "/projects",
    response_model=schemas.ProjectStatusItem,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: schemas.ProjectCreate,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
    _quota=Depends(enforce_project_limit),
) -> schemas.ProjectStatusItem:
    """Create a new project (stored as a task)."""
    # Pick a default agent — use the first available or the Onboarding Guide
    agent = db.scalars(select(models.Agent).limit(1)).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No agents available",
        )

    task = models.Task(
        title=payload.title,
        description=payload.description,
        user_id=current_user.id,
        agent_id=agent.id,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Auto-complete onboarding step
    try:
        from backend.src.modules.onboarding import service as onboarding_svc

        onboarding_svc.set_step_status(
            db, current_user, "checklist_create_first_project", "completed"
        )
    except Exception:
        pass  # Non-critical

    return schemas.ProjectStatusItem(
        id=str(task.id),
        title=task.title,
        status=task.status,
        created_at=task.created_at,
    )


@router.get("/projects/mine", response_model=list[schemas.ProjectStatusItem])
def get_projects_mine(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> list[schemas.ProjectStatusItem]:
    tasks = db.scalars(
        select(models.Task)
        .where(models.Task.user_id == current_user.id)
        .order_by(models.Task.created_at.desc())
        .limit(25),
    ).all()
    return [
        schemas.ProjectStatusItem(
            id=str(task.id),
            title=task.title or "Task",
            status=task.status,
            created_at=task.created_at,
        )
        for task in tasks
    ]


@router.get("/projects/status", response_model=schemas.ProjectStatusSummary)
def get_project_status_summary(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.ProjectStatusSummary:
    tasks = db.scalars(
        select(models.Task)
        .where(models.Task.user_id == current_user.id)
        .order_by(models.Task.created_at.desc())
        .limit(25),
    ).all()
    projects = [
        schemas.ProjectStatusItem(
            id=str(task.id),
            title=task.title or "Task",
            status=task.status,
            created_at=task.created_at,
        )
        for task in tasks
    ]
    value = projects[0].status if projects else "Not set"
    return schemas.ProjectStatusSummary(
        value=value, total=len(projects), projects=projects
    )


@router.get("/projects/{project_id}", response_model=schemas.ProjectDetail)
def get_project_detail(
    project_id: int,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.ProjectDetail:
    """Get full project details."""
    task = db.scalars(
        select(models.Task).where(
            models.Task.id == project_id,
            models.Task.user_id == current_user.id,
        )
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return schemas.ProjectDetail(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status,
        estimated_response_time=estimated_response_time(db, current_user.id),
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
    )


@router.patch("/projects/{project_id}", response_model=schemas.ProjectDetail)
def update_project(
    project_id: int,
    payload: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.ProjectDetail:
    """Update a project's title, description, or status."""
    task = db.scalars(
        select(models.Task).where(
            models.Task.id == project_id,
            models.Task.user_id == current_user.id,
        )
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    updates = payload.model_dump(exclude_unset=True)
    if "status" in updates:
        new_status = updates["status"]
        if new_status == "in-progress" and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        elif new_status in ("completed", "cancelled") and not task.completed_at:
            task.completed_at = datetime.now(timezone.utc)

    for key, value in updates.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return schemas.ProjectDetail(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=task.status,
        estimated_response_time=estimated_response_time(db, current_user.id),
        created_at=task.created_at,
        updated_at=task.updated_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> None:
    """Delete a project."""
    task = db.scalars(
        select(models.Task).where(
            models.Task.id == project_id,
            models.Task.user_id == current_user.id,
        )
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    db.delete(task)
    db.commit()


log = logging.getLogger(__name__)

_INSTRUCTIONS_SYSTEM_PROMPT = (
    "You are CapeAI, a business automation assistant. "
    "The user has created a project on the CapeControl platform. "
    "Based on the project title and description below, generate a clear, "
    "actionable instruction sheet with numbered next steps the user should "
    "follow to complete this project successfully. "
    "Be specific, practical, and concise. Use plain language. "
    "Return ONLY the numbered steps (no preamble, no summary). "
    "Aim for 5–8 steps."
)


@router.post(
    "/projects/{project_id}/instructions",
    response_model=schemas.ProjectInstructions,
)
def generate_project_instructions(
    project_id: int,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
    _plan=Depends(enforce_paid_plan),
) -> schemas.ProjectInstructions:
    """Generate (or return cached) AI instruction sheet for a project."""
    task = db.scalars(
        select(models.Task).where(
            models.Task.id == project_id,
            models.Task.user_id == current_user.id,
        )
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # Return cached instructions if they match the current brief
    cache_key = f"{task.title}|{task.description or ''}"
    cached = task.output_data or {}
    if cached.get("instructions") and cached.get("_cache_key") == cache_key:
        return schemas.ProjectInstructions(instructions=cached["instructions"])

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI backend is not configured.",
        )

    user_prompt = f"Project: {task.title}"
    if task.description:
        user_prompt += f"\nDescription: {task.description}"

    try:
        import anthropic
        from backend.src.modules.usage.model_router import select_model

        model = select_model(user_prompt, force_model=os.getenv("ANTHROPIC_MODEL"))
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=_INSTRUCTIONS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        content = "".join(b.text for b in response.content if hasattr(b, "text"))
        if not content:
            raise HTTPException(status_code=500, detail="Empty AI response")

        # Cache in output_data so we don't regenerate on every visit
        task.output_data = {
            "instructions": content,
            "_cache_key": cache_key,
            "model": response.model,
        }
        db.commit()

        # Record usage
        try:
            from backend.src.modules.usage import service as usage_svc

            usage_svc.record_usage(
                db,
                user_id=current_user.id,
                event_type="project_instructions",
                model=response.model,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
            )
            db.commit()
        except Exception:  # noqa: BLE001
            log.warning(
                "Failed to record usage for project instructions", exc_info=True
            )

        return schemas.ProjectInstructions(instructions=content)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        log.exception("Failed to generate project instructions: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate instructions. Please try again.",
        ) from exc


@router.get("/billing/balance", response_model=schemas.AccountBalance)
def get_billing_balance(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.AccountBalance:
    total_paid = (
        db.scalar(
            select(func.coalesce(func.sum(models.Invoice.amount), 0)).where(
                models.Invoice.user_id == current_user.id,
                models.Invoice.status == "paid",
            ),
        )
        or 0
    )
    total_pending = (
        db.scalar(
            select(func.coalesce(func.sum(models.Invoice.amount), 0)).where(
                models.Invoice.user_id == current_user.id,
                models.Invoice.status == "pending",
            ),
        )
        or 0
    )

    # Determine currency from user profile preferences, default ZAR
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == current_user.id),
    )
    currency = "ZAR"
    if profile and profile.profile:
        currency = profile.profile.get("preferences", {}).get("currency", "ZAR")

    return schemas.AccountBalance(
        total_paid=float(total_paid),
        total_pending=float(total_pending),
        currency=currency,
    )
