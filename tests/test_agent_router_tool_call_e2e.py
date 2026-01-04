from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, cast

import pytest
from sqlalchemy import select, update
from sqlalchemy.sql.functions import count

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.auth.csrf import CSRF_COOKIE_NAME


CSRF_HEADER = "X-CSRF-Token"


def _post_json_or_query_payload(
    client, url: str, body: Dict[str, Any], *, headers=None
):
    r = client.post(url, json=body, headers=headers or {})
    if r.status_code == 422 and '"query","payload"' in r.text:
        r = client.post(
            url, params={"payload": json.dumps(body)}, headers=headers or {}
        )
    return r


def _csrf_headers(client, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data.get("csrf_token") or data.get("csrf") or data.get("token")
    assert token, f"missing csrf token in response: {data}"

    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set(CSRF_COOKIE_NAME, token, path="/")

    headers: Dict[str, str] = {CSRF_HEADER: token}
    if extra:
        headers.update(extra)
    return headers


def _register_verified_user_and_get_token(client) -> tuple[str, str]:
    email = f"dev_{uuid.uuid4().hex[:10]}@example.com"
    password = "StrongerPass123!"

    step1_payload = {
        "first_name": "Dev",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": "Developer",
        "recaptcha_token": "dev-bypass-token",
    }

    r1 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step1",
        step1_payload,
        headers=_csrf_headers(client),
    )
    assert r1.status_code == 201, r1.text
    temp_token = r1.json()["temp_token"]

    step2_payload = {
        "company_name": "Dev LLC",
        "profile": {
            "skills": ["Python", "FastAPI"],
            "experience_level": "Senior",
            "portfolio_link": "https://example.com",
            "availability": "Full-time",
        },
    }
    step2_headers = {"Authorization": f"Bearer {temp_token}"}
    r2 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step2",
        step2_payload,
        headers=_csrf_headers(client, step2_headers),
    )
    assert r2.status_code == 200, r2.text
    access_token = r2.json().get("access_token")
    assert access_token, f"missing access_token: {r2.json()}"

    # The agent endpoints require a verified user. In CI/dev, SMTP/email delivery
    # may be disabled or ENV may not be forced to "test", so mark verified in DB.
    with SessionLocal() as db:
        db.execute(
            update(models.User)
            .where(models.User.email == email)
            .values(is_email_verified=True)
        )
        db.commit()

    return access_token, email


# -----------------------
# Deterministic OpenAI stub
# -----------------------


@dataclass
class _Fn:
    name: str
    arguments: str


@dataclass
class _ToolCall:
    id: str
    function: _Fn


@dataclass
class _Message:
    content: Optional[str] = None
    tool_calls: Optional[List[_ToolCall]] = None


@dataclass
class _Choice:
    message: _Message


@dataclass
class _Completion:
    choices: List[_Choice]


class _FakeChatCompletions:
    def __init__(self, *, tool_name: str):
        self._tool_name = tool_name
        self._calls = 0

    async def create(self, *, model: str, messages: List[Dict[str, Any]], **_kwargs):
        self._calls += 1
        _ = model

        if self._calls == 1:
            tool_call = _ToolCall(
                id="call_1",
                function=_Fn(
                    name=self._tool_name,
                    arguments=json.dumps(
                        {"goals": ["setup"], "industries": ["energy"]}
                    ),
                ),
            )
            return _Completion(
                choices=[
                    _Choice(message=_Message(content=None, tool_calls=[tool_call]))
                ]
            )

        # second call: respond using the tool message content
        tool_messages = [m for m in messages if m.get("role") == "tool"]
        tool_content = tool_messages[-1].get("content") if tool_messages else ""
        return _Completion(
            choices=[
                _Choice(
                    message=_Message(
                        content=f"E2E_OK TOOL_CONTENT={tool_content}",
                        tool_calls=None,
                    )
                )
            ]
        )


class _FakeOpenAIClient:
    def __init__(self, *, tool_name: str):
        self.chat = type(
            "_Chat",
            (),
            {
                "completions": _FakeChatCompletions(tool_name=tool_name),
            },
        )()


@pytest.fixture
def _stubbed_guide_service():
    # Override the app dependency so requests always get our stub.
    from backend.src.app import app as fastapi_app
    import importlib

    guide_router = importlib.import_module(
        "backend.src.modules.agents.cape_ai_guide.router"
    )
    from backend.src.modules.agents.cape_ai_guide.service import CapeAIGuideService

    service = CapeAIGuideService(
        openai_api_key=None, anthropic_api_key=None, model="gpt-4o-mini"
    )
    cast(Any, service).openai_client = _FakeOpenAIClient(tool_name="onboarding.plan")

    fastapi_app.dependency_overrides[guide_router.get_cape_ai_service] = lambda: service
    yield service
    fastapi_app.dependency_overrides.pop(guide_router.get_cape_ai_service, None)


def _count_tool_chat_events(db, *, user_id: str, tool_name: str) -> int:
    return int(
        db.scalar(
            select(count())
            .select_from(models.ChatEvent)
            .join(models.ChatThread, models.ChatThread.id == models.ChatEvent.thread_id)
            .where(
                models.ChatThread.user_id == user_id,
                models.ChatEvent.tool_name == tool_name,
            )
        )
        or 0
    )


def _latest_tool_chat_event(
    db, *, user_id: str, tool_name: str
) -> models.ChatEvent | None:
    stmt = (
        select(models.ChatEvent)
        .join(models.ChatThread, models.ChatThread.id == models.ChatEvent.thread_id)
        .where(
            models.ChatThread.user_id == user_id,
            models.ChatEvent.tool_name == tool_name,
        )
        .order_by(models.ChatEvent.created_at.desc())
    )
    return db.scalar(stmt)


def _count_tool_audit_events(db, *, user_id: str) -> int:
    return int(
        db.scalar(
            select(count())
            .select_from(models.AuditEvent)
            .where(
                models.AuditEvent.user_id == user_id,
                models.AuditEvent.event_type == "chatkit_tool_invocation",
            )
        )
        or 0
    )


def test_agent_router_tool_call_e2e_allowlisted(client, _stubbed_guide_service):
    access_token, email = _register_verified_user_and_get_token(client)

    with SessionLocal() as db:
        user = db.scalar(select(models.User).where(models.User.email == email))
        assert user is not None
        before_chat = _count_tool_chat_events(
            db, user_id=str(user.id), tool_name="onboarding.plan"
        )
        before_audit = _count_tool_audit_events(db, user_id=str(user.id))

    payload = {
        "query": "Please run onboarding planning.",
        "context": {
            "placement": "onboarding",
            "allowed_tools": ["onboarding.plan"],
        },
        "user_level": "beginner",
        "preferred_format": "text",
    }

    resp = client.post(
        "/api/agents/cape-ai-guide/ask",
        json=payload,
        headers=_csrf_headers(client, {"Authorization": f"Bearer {access_token}"}),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # Tool output should be visible (our stub echoes tool message)
    assert "E2E_OK" in body.get("response", "")
    assert "next_steps" in body.get("response", "")

    with SessionLocal() as db:
        user = db.scalar(select(models.User).where(models.User.email == email))
        assert user is not None

        after_chat = _count_tool_chat_events(
            db, user_id=str(user.id), tool_name="onboarding.plan"
        )
        after_audit = _count_tool_audit_events(db, user_id=str(user.id))
        assert after_chat == before_chat + 1
        assert after_audit == before_audit + 1

        event = _latest_tool_chat_event(
            db, user_id=str(user.id), tool_name="onboarding.plan"
        )
        assert event is not None
        audit_id = (event.event_metadata or {}).get("audit_event_id")
        assert isinstance(audit_id, str) and audit_id

        audit_event = db.get(models.AuditEvent, audit_id)
        assert audit_event is not None
        assert str(audit_event.id) == audit_id
        assert str(audit_event.event_type) == "chatkit_tool_invocation"


def test_agent_router_tool_call_e2e_blocks_non_allowlisted(client):
    # Stub service to request a tool call that is NOT allowlisted by request context.
    from backend.src.app import app as fastapi_app
    import importlib

    guide_router = importlib.import_module(
        "backend.src.modules.agents.cape_ai_guide.router"
    )
    from backend.src.modules.agents.cape_ai_guide.service import CapeAIGuideService

    service = CapeAIGuideService(
        openai_api_key=None, anthropic_api_key=None, model="gpt-4o-mini"
    )
    cast(Any, service).openai_client = _FakeOpenAIClient(tool_name="onboarding.plan")
    fastapi_app.dependency_overrides[guide_router.get_cape_ai_service] = lambda: service

    access_token, email = _register_verified_user_and_get_token(client)

    with SessionLocal() as db:
        user = db.scalar(select(models.User).where(models.User.email == email))
        assert user is not None
        before_chat = _count_tool_chat_events(
            db, user_id=str(user.id), tool_name="onboarding.plan"
        )
        before_audit = _count_tool_audit_events(db, user_id=str(user.id))

    payload = {
        "query": "Please run onboarding planning.",
        "context": {
            "placement": "onboarding",
            # Explicitly do NOT allow onboarding.plan
            "allowed_tools": ["onboarding.checklist"],
        },
        "user_level": "beginner",
        "preferred_format": "text",
    }

    resp = client.post(
        "/api/agents/cape-ai-guide/ask",
        json=payload,
        headers=_csrf_headers(client, {"Authorization": f"Bearer {access_token}"}),
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    # Service should surface the tool execution block as an error in the tool message content.
    assert "tool not allowlisted" in body.get("response", "")

    with SessionLocal() as db:
        user = db.scalar(select(models.User).where(models.User.email == email))
        assert user is not None
        after_chat = _count_tool_chat_events(
            db, user_id=str(user.id), tool_name="onboarding.plan"
        )
        after_audit = _count_tool_audit_events(db, user_id=str(user.id))

        assert after_chat == before_chat
        assert after_audit == before_audit

    fastapi_app.dependency_overrides.pop(guide_router.get_cape_ai_service, None)
