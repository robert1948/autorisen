"""Focused tests for OpenClaw service persistence and fallback paths."""

from __future__ import annotations

import sys
import uuid

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.openclaw.models import (
    OpenClawApprovalDecisionRequest,
    OpenClawInput,
    OpenClawTaskCreateRequest,
)
from backend.src.modules.openclaw.service import OpenClawService
from backend.src.services.security import hash_password


def _create_user(db, email: str) -> models.User:
    user = models.User(
        email=email,
        first_name="OpenClaw",
        last_name="Tester",
        hashed_password=hash_password("StrongPass123!"),
        role="Customer",
        company_name="Test Co",
        is_email_verified=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_task_persists_completed_task(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    service = OpenClawService()
    with SessionLocal() as db:
        user = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="support_triage",
            input=OpenClawInput(text="Summarize this support ticket"),
            context_refs=["doc:support-playbook-v1"],
            mode="assisted",
        )
        response = service.create_task(request, actor_id=str(user.id), db=db)

        assert response.task_id.startswith("tsk_")
        assert response.status == "completed"
        assert response.requires_approval is False

        task = service.get_task(response.task_id, db=db)
        assert task.status == "completed"
        assert task.output is not None
        assert "support_triage" in task.output.summary
        assert task.cost is not None
        assert task.cost.input_tokens > 0


def test_create_task_requires_approval_then_approve(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    service = OpenClawService()
    with SessionLocal() as db:
        user = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="status_brief",
            input=OpenClawInput(text="Draft a status brief"),
            mode="autonomous",
        )
        created = service.create_task(request, actor_id=str(user.id), db=db)
        assert created.status == "requires_approval"
        assert created.requires_approval is True

        pending_task = service.get_task(created.task_id, db=db)
        assert pending_task.approval_id is not None

        decision = service.decide_approval(
            approval_id=pending_task.approval_id,
            actor_id=str(user.id),
            request=OpenClawApprovalDecisionRequest(
                comment="Looks good", ttl_minutes=30
            ),
            approved=True,
            db=db,
        )
        assert decision.status == "approved"

        completed_task = service.get_task(created.task_id, db=db)
        assert completed_task.status == "completed"
        assert completed_task.output is not None
        assert completed_task.output.actions == ["approved_action"]


def test_create_task_requires_approval_then_reject(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    service = OpenClawService()
    with SessionLocal() as db:
        user = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="status_brief",
            input=OpenClawInput(text="Draft and send externally"),
            mode="assisted",
        )
        created = service.create_task(request, actor_id=str(user.id), db=db)
        assert created.status == "requires_approval"
        assert created.requires_approval is True

        pending_task = service.get_task(created.task_id, db=db)
        assert pending_task.approval_id is not None

        decision = service.decide_approval(
            approval_id=pending_task.approval_id,
            actor_id=str(user.id),
            request=OpenClawApprovalDecisionRequest(comment="Reject", ttl_minutes=15),
            approved=False,
            db=db,
        )
        assert decision.status == "rejected"

        rejected_task = service.get_task(created.task_id, db=db)
        assert rejected_task.status == "rejected"
        assert rejected_task.policy_reason == "approval_rejected"


class _FailingBoto3:
    @staticmethod
    def client(*_args, **_kwargs):
        raise RuntimeError("forced bedrock client failure")


def test_bedrock_enabled_falls_back_to_local_payload(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "1")
    monkeypatch.setitem(sys.modules, "boto3", _FailingBoto3)

    service = OpenClawService()
    with SessionLocal() as db:
        user = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="support_triage",
            input=OpenClawInput(text="Summarize this ticket"),
            mode="assisted",
        )
        created = service.create_task(request, actor_id=str(user.id), db=db)

        task = service.get_task(created.task_id, db=db)
        assert task.status == "completed"
        assert task.output is not None
        assert "assisted mode" in task.output.summary


def test_db_idempotency_reuses_task_for_same_user(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    service = OpenClawService()
    with SessionLocal() as db:
        user = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="support_triage",
            input=OpenClawInput(text="Summarize this support ticket"),
            mode="assisted",
            idempotency_key="idem_123",
        )

        first = service.create_task(request, actor_id=str(user.id), db=db)
        second = service.create_task(request, actor_id=str(user.id), db=db)

        assert first.task_id == second.task_id
        assert first.trace_id == second.trace_id

        openclaw_agent = (
            db.query(models.Agent).filter(
                models.Agent.slug == OpenClawService.AGENT_SLUG
            )
        ).one()
        task_count = (
            db.query(models.Task)
            .filter(
                models.Task.user_id == str(user.id),
                models.Task.agent_id == str(openclaw_agent.id),
            )
            .count()
        )
        assert task_count == 1


def test_db_idempotency_isolated_per_user(monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    service = OpenClawService()
    with SessionLocal() as db:
        user_one = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")
        user_two = _create_user(db, f"openclaw_user_{uuid.uuid4().hex[:8]}@example.com")

        request = OpenClawTaskCreateRequest(
            workflow="support_triage",
            input=OpenClawInput(text="Summarize this support ticket"),
            mode="assisted",
            idempotency_key="idem_shared",
        )

        first = service.create_task(request, actor_id=str(user_one.id), db=db)
        second = service.create_task(request, actor_id=str(user_two.id), db=db)

        assert first.task_id != second.task_id
