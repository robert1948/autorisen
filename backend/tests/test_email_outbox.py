from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.services.email_queue import enqueue_email_job
from backend.src.worker import email_worker


def _clear_email_jobs() -> None:
    db = SessionLocal()
    try:
        db.query(models.EmailJob).delete()
        db.commit()
    finally:
        db.close()


def test_enqueue_email_job_idempotent() -> None:
    _clear_email_jobs()

    key = "admin_notify:registration:test-user-1"
    payload = {
        "to_email": "zeonita@example.com",
        "subject": "New Registration (autorisen): Customer – Test User",
    }

    enqueue_email_job("admin_registration_notify", payload, key)
    enqueue_email_job("admin_registration_notify", payload, key)

    db = SessionLocal()
    try:
        count = (
            db.query(models.EmailJob)
            .filter(models.EmailJob.idempotency_key == key)
            .count()
        )
        assert count == 1
    finally:
        db.close()


def test_worker_retries_then_succeeds(monkeypatch) -> None:
    _clear_email_jobs()

    # Create one ready job
    now = datetime.now(timezone.utc)
    job = models.EmailJob(
        job_type="admin_registration_notify",
        payload={
            "to_email": "zeonita@example.com",
            "subject": "New Registration (autorisen): Customer – Test User",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "role": "Customer",
            "company_name": "",
            "created_at": now.isoformat(),
            "env_name": "autorisen",
            "user_id": "user-1",
        },
        idempotency_key="admin_notify:registration:user-1",
        status="queued",
        attempts=0,
        max_attempts=3,
        run_after=now - timedelta(seconds=1),
    )

    db = SessionLocal()
    try:
        db.add(job)
        db.commit()
        job_id = job.id
    finally:
        db.close()

    calls = {"n": 0}

    def _flaky_send_email(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("smtp down")
        return None

    monkeypatch.setattr(email_worker, "send_email", _flaky_send_email, raising=True)

    # First attempt fails -> rescheduled
    assert email_worker.process_once() is True

    db = SessionLocal()
    try:
        refreshed = db.query(models.EmailJob).filter(models.EmailJob.id == job_id).one()
        assert refreshed.status == "queued"
        assert refreshed.attempts == 1
        assert refreshed.run_after > now
    finally:
        db.close()

    # Make it ready and succeed
    db = SessionLocal()
    try:
        db.query(models.EmailJob).filter(models.EmailJob.id == job_id).update(
            {"run_after": datetime.now(timezone.utc) - timedelta(seconds=1)}
        )
        db.commit()
    finally:
        db.close()

    assert email_worker.process_once() is True

    db = SessionLocal()
    try:
        refreshed = db.query(models.EmailJob).filter(models.EmailJob.id == job_id).one()
        assert refreshed.status == "succeeded"
    finally:
        db.close()
