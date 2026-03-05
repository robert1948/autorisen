"""Automated billing scheduler.

Runs as a background thread inside the web process (no separate dyno needed).
Every ``BILLING_CHECK_INTERVAL_HOURS`` hours it:

1. Detects subscriptions whose period has ended without a completed payment.
2. Generates renewal invoices for active paid subscriptions.
3. Marks overdue subscriptions as ``past_due``.
4. Logs missed-payment events to the ``billing_events`` table.
5. Queues dunning / reminder emails via the email-job table.
"""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.payments.constants import (
    get_plan_by_id,
)

log = logging.getLogger("billing.scheduler")

# ---------------------------------------------------------------------------
# Configuration (env-driven, safe defaults)
# ---------------------------------------------------------------------------

CHECK_INTERVAL_HOURS = int(os.getenv("BILLING_CHECK_INTERVAL_HOURS", "6"))
GRACE_PERIOD_DAYS = int(os.getenv("BILLING_GRACE_PERIOD_DAYS", "7"))
MAX_REMINDERS = int(os.getenv("BILLING_MAX_REMINDERS", "3"))
REMINDER_INTERVAL_DAYS = int(os.getenv("BILLING_REMINDER_INTERVAL_DAYS", "3"))
ENABLED = os.getenv("BILLING_SCHEDULER_ENABLED", "1").lower() in {"1", "true", "yes"}

_scheduler_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


# ---------------------------------------------------------------------------
# Core billing cycle logic
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime | None) -> datetime | None:
    """Ensure a datetime is timezone-aware (SQLite returns naive datetimes)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _generate_invoice_number(db: Session) -> str:
    """Generate the next sequential invoice number ``INV-YYYY-NNNNN``."""
    year = _utcnow().year
    prefix = f"INV-{year}-"

    last = (
        db.query(models.Invoice)
        .filter(models.Invoice.invoice_number.like(f"{prefix}%"))
        .order_by(models.Invoice.invoice_number.desc())
        .first()
    )
    if last and last.invoice_number:
        seq = int(last.invoice_number.replace(prefix, "")) + 1
    else:
        seq = 1
    return f"{prefix}{seq:05d}"


def _create_renewal_invoice(
    db: Session,
    sub: models.Subscription,
    user: models.User,
) -> models.Invoice:
    """Create a pending renewal invoice for a subscription period."""
    plan = get_plan_by_id(sub.plan_id)
    if not plan:
        raise ValueError(f"No plan definition for {sub.plan_id}")

    amount = plan.price_monthly_zar
    item_name = f"CapeControl {plan.name} - Monthly Renewal"

    invoice_id = str(uuid.uuid4())
    invoice = models.Invoice(
        id=invoice_id,
        user_id=user.id,
        amount=amount,
        currency="ZAR",
        status="pending",
        item_name=item_name,
        item_description=f"Renewal for {plan.name} plan – period starting {_utcnow().strftime('%Y-%m-%d')}",
        customer_email=user.email,
        customer_first_name=user.first_name,
        customer_last_name=user.last_name,
        invoice_number=_generate_invoice_number(db),
        payment_provider="payfast",
        external_reference=invoice_id,
    )
    db.add(invoice)
    log.info(
        "Renewal invoice created: %s for user %s plan=%s amount=%s",
        invoice.invoice_number, user.id, sub.plan_id, amount,
    )
    return invoice


def _log_billing_event(
    db: Session,
    *,
    user_id: str,
    subscription_id: str,
    event_type: str,
    detail: str,
    invoice_id: str | None = None,
) -> None:
    """Insert a row into the billing_events audit table."""
    event = models.BillingEvent(
        id=str(uuid.uuid4()),
        user_id=user_id,
        subscription_id=subscription_id,
        event_type=event_type,
        detail=detail,
        invoice_id=invoice_id,
    )
    db.add(event)
    log.info("billing_event: %s user=%s sub=%s %s", event_type, user_id, subscription_id, detail)


def _queue_reminder_email(
    db: Session,
    *,
    user_email: str,
    user_first_name: str | None,
    event_type: str,
    invoice_id: str | None = None,
    plan_name: str = "Pro",
    amount: str = "529.00",
    due_date: str = "",
    reminder_count: int = 1,
) -> None:
    """Insert an email job into the queue for the email worker."""
    idempotency_key = f"{event_type}:{invoice_id or user_email}:{reminder_count}"

    existing = (
        db.query(models.EmailJob)
        .filter(models.EmailJob.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        log.debug("Duplicate email job skipped: %s", idempotency_key)
        return

    payload = {
        "to": user_email,
        "first_name": user_first_name or "there",
        "event_type": event_type,
        "plan_name": plan_name,
        "amount": amount,
        "currency": "ZAR",
        "due_date": due_date,
        "invoice_id": invoice_id,
        "reminder_count": reminder_count,
        "billing_url": "https://cape-control.com/app/billing",
        "pricing_url": "https://cape-control.com/app/pricing",
    }

    job = models.EmailJob(
        job_type=f"billing_{event_type}",
        payload=payload,
        status="queued",
        max_attempts=3,
        idempotency_key=idempotency_key,
    )
    db.add(job)
    log.info("Queued %s email for %s (reminder #%d)", event_type, user_email, reminder_count)


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def run_billing_cycle(db: Session | None = None) -> dict:
    """Execute one full billing cycle. Returns a summary dict."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    stats = {
        "checked_at": _utcnow().isoformat(),
        "renewals_created": 0,
        "subscriptions_past_due": 0,
        "subscriptions_cancelled": 0,
        "reminders_queued": 0,
        "errors": 0,
    }

    try:
        now = _utcnow()
        grace_cutoff = now - timedelta(days=GRACE_PERIOD_DAYS)

        # ---------------------------------------------------------------
        # 1. Find paid subscriptions whose period has ended
        # ---------------------------------------------------------------
        expired_subs = (
            db.query(models.Subscription)
            .filter(
                models.Subscription.plan_id.in_(["pro", "enterprise"]),
                models.Subscription.status.in_(["active", "past_due", "trialing"]),
                models.Subscription.current_period_end.isnot(None),
                models.Subscription.current_period_end <= now,
            )
            .all()
        )

        for sub in expired_subs:
            try:
                user = db.query(models.User).filter(models.User.id == sub.user_id).first()
                if not user:
                    log.warning("Orphan subscription %s – no user found", sub.id)
                    continue

                plan = get_plan_by_id(sub.plan_id)
                plan_name = plan.name if plan else sub.plan_id

                # Check if there's already a pending renewal invoice
                existing_pending = (
                    db.query(models.Invoice)
                    .filter(
                        models.Invoice.user_id == sub.user_id,
                        models.Invoice.status == "pending",
                        models.Invoice.item_name.like("%Renewal%"),
                    )
                    .first()
                )

                # -------------------------------------------------------
                # 2. Create renewal invoice if none exists
                # -------------------------------------------------------
                if not existing_pending:
                    invoice = _create_renewal_invoice(db, sub, user)
                    stats["renewals_created"] += 1

                    _log_billing_event(
                        db,
                        user_id=user.id,
                        subscription_id=sub.id,
                        event_type="renewal_invoice_created",
                        detail=f"Renewal invoice {invoice.invoice_number} for {plan_name} R{invoice.amount}",
                        invoice_id=invoice.id,
                    )
                else:
                    invoice = existing_pending

                # -------------------------------------------------------
                # 3. Transition to past_due after period end
                # -------------------------------------------------------
                if sub.status in ("active", "trialing"):
                    sub.status = "past_due"
                    stats["subscriptions_past_due"] += 1

                    _log_billing_event(
                        db,
                        user_id=user.id,
                        subscription_id=sub.id,
                        event_type="subscription_past_due",
                        detail=f"Subscription moved to past_due – period ended {sub.current_period_end}",
                        invoice_id=invoice.id if invoice else None,
                    )

                    # First reminder
                    _queue_reminder_email(
                        db,
                        user_email=user.email,
                        user_first_name=user.first_name,
                        event_type="payment_overdue",
                        invoice_id=invoice.id if invoice else None,
                        plan_name=plan_name,
                        amount=str(plan.price_monthly_zar) if plan else "529.00",
                        due_date=sub.current_period_end.strftime("%Y-%m-%d") if sub.current_period_end else "",
                        reminder_count=1,
                    )
                    stats["reminders_queued"] += 1

                # -------------------------------------------------------
                # 4. Send follow-up reminders for past_due
                # -------------------------------------------------------
                elif sub.status == "past_due":
                    # Count existing reminders
                    reminder_count = (
                        db.query(models.BillingEvent)
                        .filter(
                            models.BillingEvent.subscription_id == sub.id,
                            models.BillingEvent.event_type == "reminder_sent",
                        )
                        .count()
                    )

                    if reminder_count < MAX_REMINDERS:
                        # Check if enough time has passed since last reminder
                        last_reminder = (
                            db.query(models.BillingEvent)
                            .filter(
                                models.BillingEvent.subscription_id == sub.id,
                                models.BillingEvent.event_type.in_(["reminder_sent", "payment_overdue"]),
                            )
                            .order_by(models.BillingEvent.created_at.desc())
                            .first()
                        )

                        days_since = REMINDER_INTERVAL_DAYS + 1  # default: send
                        if last_reminder and last_reminder.created_at:
                            last_dt = _ensure_aware(last_reminder.created_at)
                            days_since = (now - last_dt).days if last_dt else days_since

                        if days_since >= REMINDER_INTERVAL_DAYS:
                            next_count = reminder_count + 1
                            _queue_reminder_email(
                                db,
                                user_email=user.email,
                                user_first_name=user.first_name,
                                event_type="payment_overdue",
                                invoice_id=invoice.id if invoice else None,
                                plan_name=plan_name,
                                amount=str(plan.price_monthly_zar) if plan else "529.00",
                                due_date=sub.current_period_end.strftime("%Y-%m-%d") if sub.current_period_end else "",
                                reminder_count=next_count,
                            )
                            _log_billing_event(
                                db,
                                user_id=user.id,
                                subscription_id=sub.id,
                                event_type="reminder_sent",
                                detail=f"Reminder #{next_count} sent to {user.email}",
                                invoice_id=invoice.id if invoice else None,
                            )
                            stats["reminders_queued"] += 1

                # -------------------------------------------------------
                # 5. Cancel after grace period expires
                # -------------------------------------------------------
                if sub.status == "past_due" and sub.current_period_end:
                    period_end_aware = _ensure_aware(sub.current_period_end)
                    if period_end_aware and period_end_aware <= grace_cutoff:
                        sub.status = "cancelled"
                        sub.cancelled_at = now
                        sub.plan_id = "free"
                        sub.current_period_end = None
                        sub.payment_provider = None
                        stats["subscriptions_cancelled"] += 1

                        _log_billing_event(
                            db,
                            user_id=user.id,
                            subscription_id=sub.id,
                            event_type="subscription_cancelled_nonpayment",
                            detail=f"Auto-cancelled after {GRACE_PERIOD_DAYS}-day grace period",
                            invoice_id=invoice.id if invoice else None,
                        )

                        # Cancel the pending invoice too
                        if invoice and invoice.status == "pending":
                            invoice.status = "cancelled"

                        # Final cancellation email
                        _queue_reminder_email(
                            db,
                            user_email=user.email,
                            user_first_name=user.first_name,
                            event_type="subscription_cancelled",
                            invoice_id=invoice.id if invoice else None,
                            plan_name=plan_name,
                            amount=str(plan.price_monthly_zar) if plan else "529.00",
                            reminder_count=MAX_REMINDERS + 1,
                        )
                        stats["reminders_queued"] += 1

                db.commit()

            except Exception:
                db.rollback()
                stats["errors"] += 1
                log.exception("Error processing subscription %s", sub.id)

        # ---------------------------------------------------------------
        # 6. Handle cancel_at_period_end
        # ---------------------------------------------------------------
        cancel_at_end = (
            db.query(models.Subscription)
            .filter(
                models.Subscription.cancel_at_period_end.is_(True),
                models.Subscription.status == "active",
                models.Subscription.current_period_end.isnot(None),
                models.Subscription.current_period_end <= now,
            )
            .all()
        )
        for sub in cancel_at_end:
            try:
                user = db.query(models.User).filter(models.User.id == sub.user_id).first()
                sub.status = "cancelled"
                sub.cancelled_at = now
                sub.plan_id = "free"
                sub.current_period_end = None
                sub.cancel_at_period_end = False
                sub.payment_provider = None

                _log_billing_event(
                    db,
                    user_id=sub.user_id,
                    subscription_id=sub.id,
                    event_type="subscription_cancelled_by_user",
                    detail="Cancelled at period end as requested",
                )

                if user:
                    _queue_reminder_email(
                        db,
                        user_email=user.email,
                        user_first_name=user.first_name,
                        event_type="subscription_ended",
                        plan_name="Free",
                        reminder_count=1,
                    )
                    stats["reminders_queued"] += 1

                db.commit()
            except Exception:
                db.rollback()
                stats["errors"] += 1
                log.exception("Error cancelling subscription %s at period end", sub.id)

    except Exception:
        log.exception("Billing cycle failed")
        stats["errors"] += 1
    finally:
        if own_session:
            db.close()

    log.info("Billing cycle complete: %s", stats)

    # Process queued billing emails immediately (no separate worker dyno)
    _process_queued_emails(db if not own_session else None)

    return stats


def _process_queued_emails(db: Session | None = None) -> int:
    """Process all queued billing emails. Returns count of emails sent."""
    from backend.src.modules.billing.emails import dispatch_billing_email

    own_session = db is None
    if own_session:
        db = SessionLocal()

    sent = 0
    try:
        now = _utcnow()
        jobs = (
            db.query(models.EmailJob)
            .filter(
                models.EmailJob.status == "queued",
                models.EmailJob.job_type.like("billing_%"),
                models.EmailJob.run_after <= now,
            )
            .order_by(models.EmailJob.run_after.asc())
            .limit(50)
            .all()
        )

        for job in jobs:
            job.status = "processing"
            job.attempts = (job.attempts or 0) + 1
            db.commit()

            try:
                ok = dispatch_billing_email(job.job_type, job.payload or {})
                if ok:
                    job.status = "sent"
                    sent += 1
                else:
                    raise RuntimeError("dispatch returned False")
            except Exception as exc:
                job.last_error = str(exc)[:2000]
                if job.attempts >= job.max_attempts:
                    job.status = "failed"
                    log.warning("Email job %d permanently failed: %s", job.id, exc)
                else:
                    job.status = "queued"
                    job.run_after = now + timedelta(minutes=5 * job.attempts)

            db.commit()

        if sent:
            log.info("Processed %d/%d queued billing emails", sent, len(jobs))

    except Exception:
        log.exception("Error processing queued billing emails")
    finally:
        if own_session:
            db.close()

    return sent


# ---------------------------------------------------------------------------
# Background thread runner
# ---------------------------------------------------------------------------

def _scheduler_loop() -> None:
    """Long-running loop that calls ``run_billing_cycle`` periodically."""
    log.info(
        "Billing scheduler started (interval=%dh, grace=%dd, max_reminders=%d)",
        CHECK_INTERVAL_HOURS, GRACE_PERIOD_DAYS, MAX_REMINDERS,
    )
    # Short initial delay to let the app finish starting
    _stop_event.wait(30)

    while not _stop_event.is_set():
        try:
            run_billing_cycle()
        except Exception:
            log.exception("Unhandled error in billing scheduler loop")
        # Sleep in small increments so we can stop quickly
        for _ in range(CHECK_INTERVAL_HOURS * 3600 // 10):
            if _stop_event.is_set():
                break
            time.sleep(10)

    log.info("Billing scheduler stopped")


def start_scheduler() -> None:
    """Launch the billing scheduler in a daemon thread."""
    global _scheduler_thread
    if not ENABLED:
        log.info("Billing scheduler disabled (BILLING_SCHEDULER_ENABLED != 1)")
        return
    if _scheduler_thread and _scheduler_thread.is_alive():
        log.warning("Billing scheduler already running")
        return

    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop, name="billing-scheduler", daemon=True
    )
    _scheduler_thread.start()
    log.info("Billing scheduler thread launched")


def stop_scheduler() -> None:
    """Signal the scheduler thread to stop."""
    _stop_event.set()
    if _scheduler_thread:
        _scheduler_thread.join(timeout=15)
        log.info("Billing scheduler thread joined")
