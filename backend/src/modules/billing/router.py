"""Billing management API – admin/internal endpoints.

Provides:
- POST /billing/cycle/run   — trigger a billing cycle manually
- GET  /billing/events       — list billing events (audit trail)
- GET  /billing/events/stats — aggregate missed-payment stats
- POST /billing/process-emails — process queued billing emails now
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.dependencies import get_verified_user

log = logging.getLogger("billing.router")

router = APIRouter(prefix="/billing", tags=["billing"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class BillingCycleResult(BaseModel):
    checked_at: str
    renewals_created: int
    subscriptions_past_due: int
    subscriptions_cancelled: int
    reminders_queued: int
    errors: int


class BillingEventOut(BaseModel):
    id: str
    user_id: str
    subscription_id: str
    event_type: str
    detail: Optional[str] = None
    invoice_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BillingEventsResponse(BaseModel):
    events: List[BillingEventOut]
    total: int


class BillingStatsOut(BaseModel):
    total_events: int
    renewals_created: int
    subscriptions_past_due: int
    reminders_sent: int
    cancelled_nonpayment: int
    cancelled_by_user: int


class EmailProcessResult(BaseModel):
    processed: int
    succeeded: int
    failed: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/cycle/run", response_model=BillingCycleResult)
def trigger_billing_cycle(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> BillingCycleResult:
    """Manually trigger a billing cycle (admin only)."""
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    from backend.src.modules.billing.scheduler import run_billing_cycle
    result = run_billing_cycle(db)
    return BillingCycleResult(**result)


@router.get("/events", response_model=BillingEventsResponse)
def list_billing_events(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID (admin only)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> BillingEventsResponse:
    """List billing events. Regular users see only their own events."""
    query = db.query(models.BillingEvent)

    # Non-admins can only see their own events
    if current_user.role not in ("admin", "superadmin"):
        query = query.filter(models.BillingEvent.user_id == current_user.id)
    elif user_id:
        query = query.filter(models.BillingEvent.user_id == user_id)

    if event_type:
        query = query.filter(models.BillingEvent.event_type == event_type)

    total = query.count()
    events = (
        query.order_by(models.BillingEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return BillingEventsResponse(
        events=[
            BillingEventOut(
                id=e.id,
                user_id=e.user_id,
                subscription_id=e.subscription_id,
                event_type=e.event_type,
                detail=e.detail,
                invoice_id=e.invoice_id,
                created_at=e.created_at,
            )
            for e in events
        ],
        total=total,
    )


@router.get("/events/stats", response_model=BillingStatsOut)
def billing_event_stats(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> BillingStatsOut:
    """Get aggregate billing event stats (admin only)."""
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    def _count(event_type: str) -> int:
        return (
            db.query(func.count(models.BillingEvent.id))
            .filter(models.BillingEvent.event_type == event_type)
            .scalar() or 0
        )

    total = db.query(func.count(models.BillingEvent.id)).scalar() or 0

    return BillingStatsOut(
        total_events=total,
        renewals_created=_count("renewal_invoice_created"),
        subscriptions_past_due=_count("subscription_past_due"),
        reminders_sent=_count("reminder_sent"),
        cancelled_nonpayment=_count("subscription_cancelled_nonpayment"),
        cancelled_by_user=_count("subscription_cancelled_by_user"),
    )


@router.post("/process-emails", response_model=EmailProcessResult)
def process_billing_emails(
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
    batch_size: int = Query(20, ge=1, le=100),
) -> EmailProcessResult:
    """Process queued billing emails immediately (admin only)."""
    if current_user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    from backend.src.modules.billing.emails import dispatch_billing_email

    now = datetime.now(timezone.utc)
    jobs = (
        db.query(models.EmailJob)
        .filter(
            models.EmailJob.status == "queued",
            models.EmailJob.job_type.like("billing_%"),
            models.EmailJob.run_after <= now,
        )
        .order_by(models.EmailJob.run_after.asc())
        .limit(batch_size)
        .all()
    )

    processed = 0
    succeeded = 0
    failed = 0

    for job in jobs:
        processed += 1
        job.status = "processing"
        job.attempts = (job.attempts or 0) + 1
        db.commit()

        try:
            ok = dispatch_billing_email(job.job_type, job.payload or {})
            if ok:
                job.status = "sent"
                succeeded += 1
            else:
                raise RuntimeError("dispatch returned False")
        except Exception as exc:
            job.last_error = str(exc)[:2000]
            if job.attempts >= job.max_attempts:
                job.status = "failed"
            else:
                job.status = "queued"
            failed += 1
            log.warning("Email job %d failed: %s", job.id, exc)

        db.commit()

    return EmailProcessResult(processed=processed, succeeded=succeeded, failed=failed)
