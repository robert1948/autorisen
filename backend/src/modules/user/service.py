"""User profile and onboarding business logic."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.src.db import models
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from . import schemas


def get_user_profile(db: Session, user_id: str) -> schemas.UserProfileResponse:
    """Get user profile with calculated fields."""
    user = db.scalar(select(models.User).where(models.User.id == user_id))
    if not user:
        msg = "User not found"
        raise ValueError(msg)

    # Get or create user profile
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == user_id),
    )

    # Default values if profile doesn't exist
    interests = []
    notifications = {"email": True, "push": True, "sms": False}

    if profile and profile.payload:
        interests = profile.payload.get("interests", [])
        notifications.update(profile.payload.get("notifications", {}))

    return schemas.UserProfileResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        company=user.company_name or "",
        role=user.role,
        experience_level=profile.experience_level if profile else None,
        is_email_verified=user.is_email_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        interests=interests,
        notifications_email=notifications.get("email", True),
        notifications_push=notifications.get("push", True),
        notifications_sms=notifications.get("sms", False),
    )


def update_user_profile(
    db: Session,
    user_id: str,
    payload: schemas.UserProfileUpdate,
) -> schemas.UserProfileResponse:
    """Update user profile information."""

    # Update base user fields
    db.execute(
        update(models.User)
        .where(models.User.id == user_id)
        .values(
            first_name=payload.first_name,
            last_name=payload.last_name,
            company_name=payload.company or "",
            role=payload.role,
            updated_at=func.now(),
        ),
    )

    # Get or create user profile
    profile = db.scalar(
        select(models.UserProfile).where(models.UserProfile.user_id == user_id),
    )

    profile_data = {
        "interests": payload.interests or [],
        "notifications": {
            "email": payload.notifications_email,
            "push": payload.notifications_push,
            "sms": payload.notifications_sms,
        },
    }

    if profile:
        # Update existing profile
        profile.experience_level = payload.experience_level
        profile.payload = {**(profile.payload or {}), **profile_data}
        profile.updated_at = func.now()
    else:
        # Create new profile
        profile = models.UserProfile(
            user_id=user_id,
            experience_level=payload.experience_level,
            payload=profile_data,
        )
        db.add(profile)

    db.commit()
    return get_user_profile(db, user_id)


def get_onboarding_checklist(
    db: Session,
    user_id: str,
) -> schemas.OnboardingChecklistResponse:
    """Get user's onboarding checklist state."""

    # Get user's checklist state
    checklist = db.scalar(
        select(models.OnboardingChecklist).where(
            models.OnboardingChecklist.user_id == user_id,
        ),
    )

    # Default checklist items
    default_items = [
        {
            "id": "complete_profile",
            "title": "Complete Profile",
            "description": "Fill out your basic information and preferences",
            "required": True,
            "order": 1,
        },
        {
            "id": "verify_email",
            "title": "Verify Email",
            "description": "Click the verification link sent to your email",
            "required": True,
            "order": 2,
        },
        {
            "id": "watch_guide",
            "title": "Watch Welcome Guide",
            "description": "Learn about the platform with our interactive guide",
            "required": False,
            "order": 3,
        },
        {
            "id": "try_agent",
            "title": "Try First Agent",
            "description": "Deploy and test your first automation agent",
            "required": False,
            "order": 4,
        },
        {
            "id": "explore_marketplace",
            "title": "Explore Marketplace",
            "description": "Browse available agents and tools",
            "required": False,
            "order": 5,
        },
        {
            "id": "setup_notifications",
            "title": "Set Up Notifications",
            "description": "Configure your notification preferences",
            "required": False,
            "order": 6,
        },
    ]

    # Get completed items from checklist state
    completed_items = []
    if checklist and checklist.state:
        completed_items = checklist.state.get("completed_items", [])

    # Build response items and calculate stats in single pass
    items = []
    required_completed = 0
    optional_completed = 0
    required_total = 0
    optional_total = 0

    for item_data in default_items:
        completed = item_data["id"] in completed_items
        item = schemas.OnboardingChecklistItem(
            **item_data,
            completed=completed,
        )
        items.append(item)

        # Update counters
        if item.required:
            required_total += 1
            if completed:
                required_completed += 1
        else:
            optional_total += 1
            if completed:
                optional_completed += 1

    total_completed = required_completed + optional_completed
    completion_percentage = int((total_completed / len(items)) * 100) if items else 0

    return schemas.OnboardingChecklistResponse(
        items=items,
        completion_percentage=completion_percentage,
        required_completed=required_completed,
        required_total=required_total,
        optional_completed=optional_completed,
        optional_total=optional_total,
    )


def complete_onboarding_item(db: Session, user_id: str, item_id: str) -> None:
    """Mark an onboarding checklist item as complete."""

    # Get or create checklist
    checklist = db.scalar(
        select(models.OnboardingChecklist).where(
            models.OnboardingChecklist.user_id == user_id,
        ),
    )

    if checklist:
        # Update existing checklist
        completed_items = set(checklist.state.get("completed_items", []))
        completed_items.add(item_id)
        checklist.state = {
            **checklist.state,
            "completed_items": list(completed_items),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
    else:
        # Create new checklist
        checklist = models.OnboardingChecklist(
            user_id=user_id,
            state={
                "completed_items": [item_id],
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
        )
        db.add(checklist)

    db.commit()


def get_dashboard_stats(db: Session, user_id: str) -> schemas.DashboardStatsResponse:
    """Get dashboard statistics for user."""

    # Count user's agents
    agent_count = (
        db.scalar(
            select(func.count(models.Agent.id)).where(models.Agent.owner_id == user_id),
        )
        or 0
    )

    # Count flow runs
    flow_run_count = (
        db.scalar(
            select(func.count(models.FlowRun.id)).where(
                models.FlowRun.user_id == user_id,
            ),
        )
        or 0
    )

    # Calculate success rate (simplified)
    success_rate = 85.0  # Placeholder - would calculate from actual run data

    # System status (simplified)
    system_status = "operational"

    return schemas.DashboardStatsResponse(
        active_agents=agent_count,
        tasks_complete=flow_run_count,
        system_status=system_status,
        agents_deployed=agent_count,
        total_runs=flow_run_count,
        success_rate=success_rate,
    )


def get_recent_activity(
    db: Session,
    user_id: str,
    limit: int = 10,
) -> list[schemas.ActivityItem]:
    """Get recent activity for user."""

    # Get recent flow runs and convert to activity items
    recent_runs = db.scalars(
        select(models.FlowRun)
        .where(models.FlowRun.user_id == user_id)
        .order_by(models.FlowRun.created_at.desc())
        .limit(limit),
    ).all()

    # Convert flow runs to activity items using list comprehension
    activity_items = [
        schemas.ActivityItem(
            id=run.id,
            type="flow_run",
            title="Agent Execution",
            description=f"Agent run on {run.placement}",
            timestamp=run.created_at,
            status="success",
            metadata={
                "placement": run.placement,
                "thread_id": run.thread_id,
            },
        )
        for run in recent_runs
    ]

    # Add user login activity (simplified)
    user = db.scalar(select(models.User).where(models.User.id == user_id))
    if user and user.last_login_at:
        activity_items.append(
            schemas.ActivityItem(
                id=f"login_{user.id}",
                type="login",
                title="User Login",
                description="Successfully logged in to CapeControl",
                timestamp=user.last_login_at,
                status="success",
                metadata={"ip_address": "masked"},
            ),
        )

    # Sort by timestamp descending
    activity_items.sort(key=lambda x: x.timestamp, reverse=True)

    return activity_items[:limit]
