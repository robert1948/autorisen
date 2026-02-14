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


def ensure_subscription(db: Session, user_id: str) -> models.Subscription:
    """Return existing subscription or auto-create a Starter one."""
    sub = get_subscription(db, user_id)
    if sub:
        return sub
    now = _utcnow()
    sub = models.Subscription(
        id=str(uuid.uuid4()),
        user_id=user_id,
        plan_id="starter",
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

    if plan_id == "enterprise":
        raise ValueError(
            "Enterprise plans are provisioned via the enterprise inquiry process."
        )

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

    if plan_id == "starter":
        sub.plan_id = "starter"
        sub.status = "active"
        sub.current_period_start = now
        sub.current_period_end = None
        sub.cancel_at_period_end = False
        sub.cancelled_at = None
        sub.payment_provider = None
        sub.provider_subscription_id = None
        msg = "Starter plan activated. Welcome!"

    elif plan_id == "growth":
        sub.plan_id = "growth"
        sub.status = "pending"
        sub.current_period_start = now
        sub.current_period_end = _period_end(now, "month")
        sub.cancel_at_period_end = False
        sub.cancelled_at = None
        sub.payment_provider = "payfast"
        # In production this would create a PayFast recurring checkout session.
        # For now return a placeholder; the ITN webhook will activate on payment.
        checkout_url = "/api/payments/payfast/checkout"
        msg = "Growth plan selected. Complete payment to activate."

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

    if sub.plan_id == "starter":
        raise ValueError("Cannot cancel the free Starter plan.")

    if sub.status == "cancelled":
        raise ValueError("Subscription is already cancelled.")

    now = _utcnow()

    if immediate:
        sub.status = "cancelled"
        sub.cancelled_at = now
        sub.cancel_at_period_end = False
        # Downgrade to Starter
        sub.plan_id = "starter"
        sub.current_period_end = None
        sub.payment_provider = None
        msg = "Subscription cancelled. You've been moved to the Starter plan."
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
