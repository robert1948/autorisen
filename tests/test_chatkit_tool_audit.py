from __future__ import annotations

import uuid

from sqlalchemy import func, select

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.agents.tool_use import ToolUseContext, execute_tool
from backend.src.modules.chatkit import service as chatkit_service


def _create_user(db) -> models.User:
    email = f"tester-{uuid.uuid4()}@example.com"
    user = models.User(email=email, hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_chatkit_invoke_tool_creates_audit_event():
    with SessionLocal() as db:
        user = _create_user(db)

        thread, result, event = chatkit_service.invoke_tool(
            db,
            user=user,
            placement="onboarding",
            tool_name="onboarding.plan",
            payload={"goals": ["setup"], "industries": ["energy"]},
        )

        assert thread.id
        assert result["summary"]["user"] == user.email
        assert event.role == "tool"
        assert event.tool_name == "onboarding.plan"
        assert (event.event_metadata or {}).get("audit_event_id")

        audit_id = (event.event_metadata or {}).get("audit_event_id")
        audit_event = db.get(models.AuditEvent, audit_id)
        assert audit_event is not None
        assert audit_event.event_type == "chatkit_tool_invocation"
        assert (audit_event.payload or {}).get("tool_name") == "onboarding.plan"
        assert (audit_event.payload or {}).get("thread_id") == thread.id


def test_execute_tool_enforces_allowlist_without_writing_audit():
    with SessionLocal() as db:
        user = _create_user(db)

        before = db.scalar(select(func.count()).select_from(models.AuditEvent))

        ctx = ToolUseContext(
            placement="onboarding",
            thread_id=None,
            allowed_tools=["onboarding.checklist"],
        )

        try:
            execute_tool(
                db,
                user=user,
                ctx=ctx,
                tool_name="onboarding.plan",
                tool_payload={"goals": ["setup"]},
            )
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass

        after = db.scalar(select(func.count()).select_from(models.AuditEvent))
        assert after == before
