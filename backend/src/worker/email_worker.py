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

        logger.info(
            "Email job queued but processing not implemented",
            extra={"job_id": job.id, "job_type": job.job_type},
        )
        return False


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
