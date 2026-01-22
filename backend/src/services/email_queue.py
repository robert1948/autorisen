"""Durable email outbox enqueue helpers.

This module writes jobs into the DB-backed `email_jobs` table.
A separate worker is responsible for sending and retrying.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.exc import IntegrityError

from backend.src.core.config import settings
from backend.src.db import models
from backend.src.db.session import SessionLocal

log = logging.getLogger(__name__)


def enqueue_email_job(
    job_type: str,
    payload: dict[str, Any],
    idempotency_key: str,
    run_after: Optional[datetime] = None,
) -> None:
    """Insert an email job into the outbox.

    - Idempotent by `idempotency_key`.
    - Never raises to the caller (soft-fail).
    """

    if not idempotency_key:
        log.warning("email_job_enqueue_skipped missing_idempotency_key")
        return

    run_after_value = run_after
    if run_after_value is None:
        run_after_value = datetime.now(timezone.utc)

    job = models.EmailJob(
        job_type=job_type,
        payload=payload,
        idempotency_key=idempotency_key,
        run_after=run_after_value,
    )

    db = SessionLocal()
    try:
        db.add(job)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Treat unique violation as success for idempotency.
        log.info(
            "email_job_enqueue_idempotent",
            extra={"job_type": job_type, "idempotency_key": idempotency_key},
        )
    except Exception:
        db.rollback()
        log.warning(
            "email_job_enqueue_failed",
            extra={"job_type": job_type, "idempotency_key": idempotency_key},
        )
    finally:
        db.close()


def enqueue_admin_registration_notify(*, user: models.User) -> None:
    """Queue an admin notification email on successful registration.

    Skips if ADMIN_REGISTRATION_NOTIFY_EMAIL is missing/blank.
    """

    admin_email = (settings.admin_registration_notify_email or "").strip()
    if not admin_email:
        log.warning("admin_registration_notify_skipped missing_admin_email")
        return

    env_name = (getattr(settings, "env_name", None) or "").strip() or str(settings.env)

    first_name = (getattr(user, "first_name", "") or "").strip()
    last_name = (getattr(user, "last_name", "") or "").strip()
    role = (getattr(user, "role", "") or "").strip()

    subject = (
        f"New Registration ({env_name}): {role} – {first_name} {last_name}".strip()
    )

    company_name = (getattr(user, "company_name", "") or "").strip() or None

    created_at = getattr(user, "created_at", None)
    created_at_iso = None
    try:
        if created_at is not None:
            created_at_iso = created_at.astimezone(timezone.utc).isoformat()
    except Exception:
        created_at_iso = str(created_at) if created_at is not None else None

    payload: dict[str, Any] = {
        "to_email": admin_email,
        "subject": subject,
        "env_name": env_name,
        "user_id": getattr(user, "id", None),
        "first_name": first_name,
        "last_name": last_name,
        "email": getattr(user, "email", None),
        "role": role,
        "company_name": company_name,
        "created_at": created_at_iso,
    }

    user_id = payload.get("user_id")
    if not user_id:
        log.warning("admin_registration_notify_skipped missing_user_id")
        return

    enqueue_email_job(
        job_type="admin_registration_notify",
        payload=payload,
        idempotency_key=f"admin_notify:registration:{user_id}",
    )
