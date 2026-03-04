"""Email job worker for queued outbound email tasks."""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone

from sqlalchemy.exc import ProgrammingError

from backend.src.db.models import EmailJob
from backend.src.db.session import SessionLocal

logger = logging.getLogger(__name__)

EMAIL_JOBS_ENABLED = os.getenv("EMAIL_JOBS_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
}
POLL_SECONDS = int(os.getenv("EMAIL_JOBS_POLL_SECONDS", "5"))
IDLE_SECONDS = int(os.getenv("EMAIL_JOBS_IDLE_SECONDS", "60"))

_missing_table_logged = False


def _dispatch_job(job: EmailJob) -> bool:
    """Route a job to the correct email sender. Returns True on success."""
    job_type = job.job_type or ""
    payload = job.payload or {}

    # Billing emails (payment_overdue, subscription_cancelled, etc.)
    if job_type.startswith("billing_"):
        from backend.src.modules.billing.emails import dispatch_billing_email
        return dispatch_billing_email(job_type, payload)

    # Generic email (fallback)
    if job_type == "send_email":
        from backend.src.core.mailer import send_email
        send_email(
            subject=payload.get("subject", ""),
            to=payload.get("to", []) if isinstance(payload.get("to"), list) else [payload.get("to", "")],
            text_body=payload.get("text_body", ""),
            html_body=payload.get("html_body"),
        )
        return True

    logger.warning("Unknown email job type: %s (job_id=%d)", job_type, job.id)
    return False

_missing_table_logged = False


def _claim_next_job(session) -> EmailJob | None:
    now = datetime.now(timezone.utc)
    return (
        session.query(EmailJob)
        .filter(EmailJob.status == "queued", EmailJob.run_after <= now)
        .order_by(EmailJob.run_after.asc(), EmailJob.created_at.asc())
        .first()
    )


def _process_once() -> bool:
    global _missing_table_logged

    with SessionLocal() as session:
        try:
            job = _claim_next_job(session)
        except ProgrammingError as exc:
            if "email_jobs" in str(exc).lower():
                if not _missing_table_logged:
                    logger.warning(
                        "email_jobs table missing; worker idle",
                        extra={"error": str(exc)},
                    )
                    _missing_table_logged = True
                return False
            raise

        if not job:
            return False

        # Mark as in-progress
        job.status = "processing"
        job.attempts = (job.attempts or 0) + 1
        session.commit()

        try:
            success = _dispatch_job(job)
        except Exception as exc:
            success = False
            job.last_error = str(exc)[:2000]
            logger.exception(
                "Email job %d (%s) raised an exception",
                job.id, job.job_type,
            )

        if success:
            job.status = "sent"
            logger.info(
                "Email job %d processed successfully",
                job.id,
                extra={"job_type": job.job_type},
            )
        else:
            if job.attempts >= job.max_attempts:
                job.status = "failed"
                logger.warning(
                    "Email job %d permanently failed after %d attempts",
                    job.id, job.attempts,
                )
            else:
                # Re-queue for retry with backoff
                from datetime import timedelta
                job.status = "queued"
                job.run_after = datetime.now(timezone.utc) + timedelta(
                    minutes=5 * job.attempts
                )
                logger.info(
                    "Email job %d will retry (attempt %d/%d)",
                    job.id, job.attempts, job.max_attempts,
                )

        session.commit()
        return success


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    if not EMAIL_JOBS_ENABLED:
        logger.warning(
            "EMAIL_JOBS_ENABLED is false; worker idle",
            extra={"env": os.getenv("ENV", "unknown")},
        )
        while True:
            time.sleep(IDLE_SECONDS)

    while True:
        processed = _process_once()
        if processed:
            continue
        time.sleep(max(POLL_SECONDS, IDLE_SECONDS))


if __name__ == "__main__":
    main()
