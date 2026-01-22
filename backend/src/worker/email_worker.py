"""DB-backed email outbox worker.

Run as:
  python -m backend.src.worker.email_worker

Polls for queued jobs and processes them with deterministic backoff.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import asc
from sqlalchemy.orm import Session

from backend.src.core.mailer import MailerError, send_email
from backend.src.db import models
from backend.src.db.session import SessionLocal

log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def backoff_delay(attempt: int) -> timedelta:
    """Deterministic backoff schedule as a pure function of attempt (1-based)."""

    # 1m, 5m, 15m, 1h, 3h, 12h, 24h, 24h...
    schedule_seconds = [
        60,
        5 * 60,
        15 * 60,
        60 * 60,
        3 * 60 * 60,
        12 * 60 * 60,
        24 * 60 * 60,
    ]
    if attempt <= 0:
        return timedelta(seconds=0)
    idx = min(attempt - 1, len(schedule_seconds) - 1)
    return timedelta(seconds=schedule_seconds[idx])


def claim_next_job(db: Session) -> Optional[models.EmailJob]:
    """Claim a single ready job by flipping it to processing.

    Uses an optimistic update to stay compatible with SQLite tests.
    """

    now = _utcnow()

    candidate = (
        db.query(models.EmailJob)
        .filter(models.EmailJob.status == "queued")
        .filter(models.EmailJob.run_after <= now)
        .order_by(asc(models.EmailJob.run_after), asc(models.EmailJob.created_at))
        .first()
    )
    if candidate is None:
        return None

    updated = (
        db.query(models.EmailJob)
        .filter(models.EmailJob.id == candidate.id)
        .filter(models.EmailJob.status == "queued")
        .update({"status": "processing", "updated_at": now})
    )
    if updated != 1:
        db.rollback()
        return None

    db.commit()
    db.refresh(candidate)
    return candidate


def _mark_succeeded(db: Session, job: models.EmailJob) -> None:
    db.query(models.EmailJob).filter(models.EmailJob.id == job.id).update(
        {
            "status": "succeeded",
            "updated_at": _utcnow(),
            "last_error": None,
        }
    )
    db.commit()


def _mark_failed_and_reschedule(
    db: Session, job: models.EmailJob, error: Exception
) -> None:
    now = _utcnow()
    next_attempts = int(getattr(job, "attempts", 0) or 0) + 1
    max_attempts = int(getattr(job, "max_attempts", 8) or 8)

    if next_attempts >= max_attempts:
        status = "dead"
        run_after = now
    else:
        status = "queued"
        run_after = now + backoff_delay(next_attempts)

    db.query(models.EmailJob).filter(models.EmailJob.id == job.id).update(
        {
            "status": status,
            "attempts": next_attempts,
            "run_after": run_after,
            "last_error": str(error)[:4000],
            "updated_at": now,
        }
    )
    db.commit()


def dispatch_job(job: models.EmailJob) -> None:
    """Dispatch job based on type."""

    payload: dict[str, Any] = dict(getattr(job, "payload", {}) or {})

    if job.job_type == "admin_registration_notify":
        to_email = (payload.get("to_email") or "").strip()
        subject = (payload.get("subject") or "").strip() or "New Registration"

        # Plain text content (no secrets)
        lines = [
            f"Name: {(payload.get('first_name') or '').strip()} {(payload.get('last_name') or '').strip()}".strip(),
            f"Email: {payload.get('email')}",
            f"Role: {payload.get('role')}",
            f"Company: {payload.get('company_name')}",
            f"Registered At (UTC): {payload.get('created_at')}",
            f"Environment: {payload.get('env_name')}",
            f"User ID: {payload.get('user_id')}",
        ]
        text_body = "\n".join(lines) + "\n"

        if not to_email:
            raise ValueError("Missing to_email")

        send_email(subject=subject, to=[to_email], text_body=text_body)
        return

    raise ValueError(f"Unknown job_type: {job.job_type}")


def process_once() -> bool:
    """Process at most one ready job. Returns True if a job was processed."""

    db = SessionLocal()
    try:
        job = claim_next_job(db)
        if job is None:
            return False

        try:
            dispatch_job(job)
        except Exception as exc:
            _mark_failed_and_reschedule(db, job, exc)
            log.warning(
                "email_job_failed",
                extra={
                    "job_id": job.id,
                    "job_type": job.job_type,
                    "attempts": job.attempts,
                },
            )
            return True

        _mark_succeeded(db, job)
        log.info(
            "email_job_succeeded",
            extra={"job_id": job.id, "job_type": job.job_type},
        )
        return True
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    poll_interval = float(os.getenv("EMAIL_WORKER_POLL_INTERVAL_SEC", "1.0"))

    log.info("email_worker_start", extra={"poll_interval_sec": poll_interval})

    while True:
        processed = process_once()
        if not processed:
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
