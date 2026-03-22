"""Resilience tests for API endpoints under DB query failures."""

from __future__ import annotations

import uuid

from sqlalchemy.exc import SQLAlchemyError

from backend.src.app import app
from backend.src.db import models
from backend.src.db.session import SessionLocal, get_session
from backend.src.modules.auth.csrf import CSRF_COOKIE_NAME
from backend.src.modules.usage import router as usage_router
from backend.src.services.csrf import generate_csrf_token
from backend.src.services.security import create_jwt, hash_password


class _BrokenSession:
    """Session stub that raises SQLAlchemy errors for read/query operations."""

    def scalar(self, *_args, **_kwargs):
        raise SQLAlchemyError("forced scalar failure")

    def scalars(self, *_args, **_kwargs):
        raise SQLAlchemyError("forced query failure")

    def execute(self, *_args, **_kwargs):
        raise SQLAlchemyError("forced execute failure")

    def query(self, *_args, **_kwargs):
        raise SQLAlchemyError("forced query failure")


def _create_user(db, email: str) -> models.User:
    user = models.User(
        email=email,
        first_name="Test",
        last_name="User",
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


def _auth_headers(user: models.User) -> dict[str, str]:
    token, _ = create_jwt(
        {
            "user_id": user.id,
            "email": user.email,
            "jti": str(uuid.uuid4()),
            "token_version": user.token_version,
        },
        expires_in=30,
    )
    return {"Authorization": f"Bearer {token}"}


def _override_broken_session():
    def _dep():
        yield _BrokenSession()

    app.dependency_overrides[get_session] = _dep


def _clear_session_override():
    app.dependency_overrides.pop(get_session, None)


def _csrf_headers(client) -> dict[str, str]:
    token = generate_csrf_token()
    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set(CSRF_COOKIE_NAME, token, path="/")
    return {"X-CSRF-Token": token}


def test_projects_mine_returns_empty_when_task_query_fails(client):
    with SessionLocal() as db:
        user = _create_user(db, f"res_user_{uuid.uuid4().hex[:8]}@example.com")

    _override_broken_session()
    try:
        response = client.get("/api/projects/mine", headers=_auth_headers(user))
    finally:
        _clear_session_override()

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_create_project_returns_503_when_storage_query_fails(client):
    with SessionLocal() as db:
        user = _create_user(db, f"res_user_{uuid.uuid4().hex[:8]}@example.com")

    _override_broken_session()
    try:
        response = client.post(
            "/api/projects",
            headers={**_auth_headers(user), **_csrf_headers(client)},
            json={"title": "Resilience Project", "description": "desc"},
        )
    finally:
        _clear_session_override()

    assert response.status_code == 503, response.text
    assert "temporarily unavailable" in response.text.lower()


def test_usage_summary_returns_zeroed_payload_on_usage_query_error(client, monkeypatch):
    with SessionLocal() as db:
        user = _create_user(db, f"usage_user_{uuid.uuid4().hex[:8]}@example.com")

    def _raise_usage_error(*_args, **_kwargs):
        raise SQLAlchemyError("forced usage summary failure")

    monkeypatch.setattr(usage_router.service, "get_usage_summary", _raise_usage_error)

    response = client.get("/api/usage/summary", headers=_auth_headers(user))
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["api_calls_used"] == 0
    assert payload["total_tokens_in"] == 0
    assert payload["total_tokens_out"] == 0
    assert payload["total_cost_usd"] == 0.0
    assert payload["plan_id"] == "free"
    assert payload["agent_count"] == 0
    assert payload["max_agents"] >= 1
