"""Subscription business logic."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.src.db import models
from .plans import PLANS_BY_ID, get_plan

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _period_end(start: datetime, interval: str | None) -> datetime | None:
    if interval == "month":
        # Approximate 30-day month
        return start + timedelta(days=30)
    return None


def _sub_to_dict(sub: models.Subscription) -> dict:
    """Convert a Subscription ORM instance to a dict matching SubscriptionOut."""
    plan = get_plan(sub.plan_id)
    return {
        "id": sub.id,
        "plan_id": sub.plan_id,
        "plan_name": plan.name if plan else sub.plan_id,
        "status": sub.status,
        "current_period_start": sub.current_period_start,
        "current_period_end": sub.current_period_end,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "cancelled_at": sub.cancelled_at,
        "created_at": sub.created_at,
    }


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_subscription(db: Session, user_id: str) -> models.Subscription | None:
    """Return the user's subscription or None."""
    return (
        db.query(models.Subscription)
        .filter(models.Subscription.user_id == user_id)
        .first()
    )


# Trial duration in days
TRIAL_DURATION_DAYS = 14


def ensure_subscription(db: Session, user_id: str) -> models.Subscription:
    """Return existing subscription or auto-create a Free one."""
    sub = get_subscription(db, user_id)
    if sub:
        return sub
    now = _utcnow()
    sub = models.Subscription(
        id=str(uuid.uuid4()),
        user_id=user_id,
        plan_id="free",
        status="active",
        current_period_start=now,
        current_period_end=None,
        cancel_at_period_end=False,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


# ---------------------------------------------------------------------------
# Subscribe / change plan
# ---------------------------------------------------------------------------

def subscribe(
    db: Session,
    user: models.User,
    plan_id: str,
) -> tuple[models.Subscription, str, Optional[str]]:
    """
    Set or change the user's plan.

    Returns (subscription, message, checkout_url).
    - For starter: immediate activation, checkout_url=None
    - For growth: set to pending, return a placeholder checkout_url
    - For enterprise: reject (use inquiry endpoint instead)
    """
    plan = get_plan(plan_id)
    if plan is None:
        raise ValueError(f"Unknown plan: {plan_id}")

    sub = get_subscription(db, user.id)
    now = _utcnow()

    if sub and sub.plan_id == plan_id and sub.status == "active":
        return sub, f"Already on the {plan.name} plan.", None

    if sub is None:
        sub = models.Subscription(
            id=str(uuid.uuid4()),
            user_id=user.id,
        )
        db.add(sub)

    checkout_url: str | None = None

    if plan_id == "free":
        sub.plan_id = "free"
        sub.status = "active"
        sub.current_period_start = now
        sub.current_period_end = None
        sub.cancel_at_period_end = False
        sub.cancelled_at = None
        sub.payment_provider = None
        sub.provider_subscription_id = None
        msg = "Free plan activated. Welcome!"

    elif plan_id == "pro":
        sub.plan_id = "pro"
        # Start with a 14-day free trial, no credit card required
        sub.status = "trialing"
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=TRIAL_DURATION_DAYS)
        sub.cancel_at_period_end = False
        sub.cancelled_at = None
        sub.payment_provider = "payfast"
        # After trial ends, user will need to complete payment
        checkout_url = "/api/payments/payfast/checkout"
        msg = f"Pro plan trial activated! You have {TRIAL_DURATION_DAYS} days to explore all Pro features. No credit card required."

    elif plan_id == "enterprise":
        sub.plan_id = "enterprise"
        sub.status = "pending"
        sub.current_period_start = now
        sub.current_period_end = _period_end(now, "month")
        sub.cancel_at_period_end = False
        sub.cancelled_at = None
        sub.payment_provider = "payfast"
        checkout_url = "/api/payments/payfast/checkout"
        msg = "Enterprise plan selected. Our team will reach out to finalize setup."

    else:
        raise ValueError(f"Unsupported plan: {plan_id}")

    db.commit()
    db.refresh(sub)
    log.info("User %s subscribed to %s (status=%s)", user.id, plan_id, sub.status)
    return sub, msg, checkout_url


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------

def cancel_subscription(
    db: Session,
    user_id: str,
    *,
    immediate: bool = False,
    reason: str | None = None,
) -> tuple[models.Subscription, str]:
    """Cancel the user's subscription."""
    sub = get_subscription(db, user_id)
    if sub is None:
        raise ValueError("No active subscription found.")

    if sub.plan_id == "free":
        raise ValueError("Cannot cancel the free plan.")

    if sub.status == "cancelled":
        raise ValueError("Subscription is already cancelled.")

    now = _utcnow()

    if immediate:
        sub.status = "cancelled"
        sub.cancelled_at = now
        sub.cancel_at_period_end = False
        # Downgrade to Free
        sub.plan_id = "free"
        sub.current_period_end = None
        sub.payment_provider = None
        msg = "Subscription cancelled. You've been moved to the Free plan."
    else:
        sub.cancel_at_period_end = True
        sub.cancelled_at = now
        msg = (
            "Subscription will cancel at the end of the current billing period. "
            "You'll retain access until then."
        )

    if reason:
        sub.metadata_json = {**(sub.metadata_json or {}), "cancel_reason": reason}

    db.commit()
    db.refresh(sub)
    log.info("User %s cancelled subscription (immediate=%s)", user_id, immediate)
    return sub, msg


# ---------------------------------------------------------------------------
# Enterprise inquiry
# ---------------------------------------------------------------------------

def create_enterprise_inquiry(
    db: Session,
    *,
    user_id: str | None,
    company_name: str,
    contact_name: str,
    contact_email: str,
    message: str | None,
) -> models.EnterpriseInquiry:
    """Record an enterprise sales inquiry."""
    inquiry = models.EnterpriseInquiry(
        id=str(uuid.uuid4()),
        user_id=user_id,
        company_name=company_name,
        contact_name=contact_name,
        contact_email=contact_email,
        message=message,
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    log.info("Enterprise inquiry %s created by user %s", inquiry.id, user_id)
    return inquiry


# ---------------------------------------------------------------------------
# Billing history
# ---------------------------------------------------------------------------

def list_invoices(
    db: Session, user_id: str, *, limit: int = 50
) -> list[models.Invoice]:
    """Return the user's invoices ordered newest-first."""
    return (
        db.query(models.Invoice)
        .filter(models.Invoice.user_id == user_id)
        .order_by(models.Invoice.created_at.desc())
        .limit(limit)
        .all()
    )
