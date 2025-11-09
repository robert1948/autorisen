"""
Integration tests for ChatKit backend routes (project task CHAT-001).

These tests verify that:
- `/api/chatkit/token` returns signed bundles tied to persisted threads.
- `/api/chatkit/tools/{tool_name}` invokes placement-scoped adapters,
  emits chat events, and enforces placement restrictions.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_chatkit_api.db")
os.environ.setdefault("CHATKIT_APP_ID", "chatkit-test-app")
os.environ.setdefault("CHATKIT_SIGNING_KEY", "chatkit-test-signing-key")

from backend.src.db import models  # noqa: E402
from backend.src.db.base import Base  # noqa: E402
from backend.src.db.session import SessionLocal, engine, get_session  # noqa: E402
from backend.src.modules.auth.deps import get_verified_user  # noqa: E402
from backend.src.modules.chatkit.router import router as chatkit_router  # noqa: E402

TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def _override_session() -> Generator[Session, None, None]:
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _build_app(user: models.User) -> FastAPI:
    """Create a minimal FastAPI app with dependency overrides."""

    test_app = FastAPI()
    test_app.include_router(chatkit_router, prefix="/api")
    test_app.dependency_overrides[get_session] = _override_session

    async def _get_user_override() -> models.User:
        return user

    test_app.dependency_overrides[get_verified_user] = _get_user_override
    return test_app


def _create_user() -> models.User:
    """Insert a verified user record for auth overrides."""

    session = SessionLocal()
    try:
        user = models.User(
            email="chatkit@test.example.com",
            first_name="Chat",
            last_name="Kit",
            hashed_password="test-hash",
            role="Customer",
            company_name="CapeControl",
            is_email_verified=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        session.expunge(user)
        return user
    finally:
        session.close()


def _query_all(model) -> list:
    session = SessionLocal()
    try:
        return session.query(model).all()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_schema() -> Generator[None, None, None]:
    """Ensure a clean schema for each test."""

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_issue_token_persists_thread_and_returns_allowed_tools():
    user = _create_user()
    app = _build_app(user)

    with TestClient(app) as client:
        resp = client.post(
            "/api/chatkit/token",
            json={"placement": "onboarding"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["placement"] == "onboarding"
    assert data["thread_id"]
    assert data["token"]
    assert "onboarding.plan" in data["allowed_tools"]
    assert "onboarding.checklist" in data["allowed_tools"]

    threads = _query_all(models.ChatThread)
    assert len(threads) == 1
    assert threads[0].id == data["thread_id"]


def test_invoke_tool_records_event_and_returns_payload():
    user = _create_user()
    app = _build_app(user)

    with TestClient(app) as client:
        token_data = client.post(
            "/api/chatkit/token",
            json={"placement": "onboarding"},
        ).json()
        resp = client.post(
            "/api/chatkit/tools/onboarding.checklist",
            json={
                "placement": "onboarding",
                "thread_id": token_data["thread_id"],
                "payload": {"task_id": "intro_call", "done": True},
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["thread_id"] == token_data["thread_id"]
    assert data["tool_name"] == "onboarding.checklist"
    assert data["event_id"]
    assert data["result"]["summary"]["total"] >= 1
    assert data["allowed_tools"].count("onboarding.checklist") == 1

    events = _query_all(models.ChatEvent)
    assert len(events) == 1
    assert events[0].tool_name == "onboarding.checklist"


def test_invoke_tool_rejects_invalid_tool_for_placement():
    user = _create_user()
    app = _build_app(user)

    with TestClient(app) as client:
        resp = client.post(
            "/api/chatkit/tools/support.ticket",
            json={"placement": "onboarding", "payload": {}},
        )

    assert resp.status_code == 400
    assert "tool not available" in resp.json()["detail"]
