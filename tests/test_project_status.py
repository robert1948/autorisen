"""Tests for project status summary endpoint."""

from __future__ import annotations

import uuid

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.services.security import create_jwt, hash_password


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


def _create_agent(db, owner_id: str) -> models.Agent:
    agent = models.Agent(
        owner_id=owner_id,
        slug=f"agent-{uuid.uuid4().hex[:8]}",
        name="Test Agent",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def _create_task(db, user_id: str, agent_id: str) -> models.Task:
    task = models.Task(
        user_id=user_id,
        agent_id=agent_id,
        goal="Demo task",
        status="running",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


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


def test_project_status_summary_with_task(client):
    with SessionLocal() as db:
        user = _create_user(db, f"user_{uuid.uuid4().hex[:8]}@example.com")
        agent = _create_agent(db, user.id)
        _create_task(db, user.id, agent.id)

    response = client.get("/api/projects/status", headers=_auth_headers(user))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["value"]
    assert payload["value"] == "running"
    assert payload["total"] == 1
    assert len(payload["projects"]) == 1


def test_project_status_summary_without_tasks(client):
    with SessionLocal() as db:
        user = _create_user(db, f"user_{uuid.uuid4().hex[:8]}@example.com")

    response = client.get("/api/projects/status", headers=_auth_headers(user))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["value"]
    assert payload["value"] == "Not set"
    assert payload["total"] == 0
    assert payload["projects"] == []
