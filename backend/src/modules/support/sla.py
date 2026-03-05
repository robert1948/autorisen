"""SLA configuration — maps subscription plan tiers to response-time guarantees."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models

# Plan ID → guaranteed response time in hours
PLAN_RESPONSE_HOURS: dict[str, int] = {
    "free": 48,
    "pro": 24,
    "enterprise": 4,
}

# Human-readable labels returned to the frontend
PLAN_RESPONSE_LABELS: dict[str, str] = {
    "free": "48 hours (Community)",
    "pro": "24 hours (Priority)",
    "enterprise": "4 hours (Priority Account SLA)",
}

DEFAULT_PLAN = "free"


def get_user_plan_id(db: Session, user_id: str) -> str:
    """Return the active plan_id for *user_id*, defaulting to ``free``."""
    stmt = select(models.Subscription.plan_id).where(
        models.Subscription.user_id == user_id,
        models.Subscription.status == "active",
    )
    plan_id: Optional[str] = db.scalars(stmt).first()
    return plan_id or DEFAULT_PLAN


def estimated_response_time(db: Session, user_id: str) -> str:
    """Return a human-readable estimated response time for the user."""
    plan = get_user_plan_id(db, user_id)
    return PLAN_RESPONSE_LABELS.get(plan, PLAN_RESPONSE_LABELS[DEFAULT_PLAN])


def response_hours(db: Session, user_id: str) -> int:
    """Return the numeric response-time guarantee in hours."""
    plan = get_user_plan_id(db, user_id)
    return PLAN_RESPONSE_HOURS.get(plan, PLAN_RESPONSE_HOURS[DEFAULT_PLAN])
