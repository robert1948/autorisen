"""User profile and onboarding API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user

from . import schemas, service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.UserProfileResponse:
    """Get current user's profile information."""
    return service.get_user_profile(db, current_user.id)


@router.put("/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    payload: schemas.UserProfileUpdate,
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.UserProfileResponse:
    """Update current user's profile information."""
    return service.update_user_profile(db, current_user.id, payload)


@router.get("/onboarding/checklist", response_model=schemas.OnboardingChecklistResponse)
def get_onboarding_checklist(
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.OnboardingChecklistResponse:
    """Get current user's onboarding checklist state."""
    return service.get_onboarding_checklist(db, current_user.id)


@router.post("/onboarding/checklist/item/{item_id}/complete")
def complete_onboarding_item(
    item_id: str,
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> dict[str, str]:
    """Mark an onboarding checklist item as complete."""
    service.complete_onboarding_item(db, current_user.id, item_id)
    return {"status": "completed", "item_id": item_id}


@router.get("/dashboard/stats", response_model=schemas.DashboardStatsResponse)
def get_dashboard_stats(
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.DashboardStatsResponse:
    """Get dashboard statistics for the current user."""
    return service.get_dashboard_stats(db, current_user.id)


@router.get("/dashboard/recent-activity", response_model=list[schemas.ActivityItem])
def get_recent_activity(
    limit: int = 10,
    current_user=Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> list[schemas.ActivityItem]:
    """Get recent activity for the current user."""
    return service.get_recent_activity(db, current_user.id, limit)
