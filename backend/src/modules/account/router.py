"""Account, profile, projects, and billing endpoints for dashboard modules."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user

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
        .values(is_active=False, token_version=new_token_version, updated_at=datetime.now(timezone.utc)),
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
            payload={"reason": "user_requested"},
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
    return schemas.PersonalInfo(
        phone=info.get("phone"),
        location=info.get("location"),
        timezone=info.get("timezone"),
        bio=info.get("bio"),
        avatar_url=info.get("avatar_url"),
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

    info = dict((profile.profile or {}).get("personal_info", {}))
    for key, value in payload.model_dump(exclude_none=True).items():
        info[key] = value

    updated_profile = dict(profile.profile or {})
    updated_profile["personal_info"] = info
    profile.profile = updated_profile
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return schemas.PersonalInfo(
        phone=info.get("phone"),
        location=info.get("location"),
        timezone=info.get("timezone"),
        bio=info.get("bio"),
        avatar_url=info.get("avatar_url"),
        updated_at=profile.updated_at,
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
            title=task.goal or "Task",
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
            title=task.goal or "Task",
            status=task.status,
            created_at=task.created_at,
        )
        for task in tasks
    ]
    # Provide a safe default when the user has no tasks.
    value = projects[0].status if projects else "Not set"
    return schemas.ProjectStatusSummary(value=value, total=len(projects), projects=projects)


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

    return schemas.AccountBalance(
        total_paid=float(total_paid),
        total_pending=float(total_pending),
        currency="ZAR",
    )
