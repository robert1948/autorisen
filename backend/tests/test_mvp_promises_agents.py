from __future__ import annotations

import uuid

from sqlalchemy import select

from backend.src.db import models
from backend.src.db.session import SessionLocal


def _csrf_headers(client):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def _register_user(client):
    email = f"mvp_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!23$"
    payload = {
        "first_name": "MVP",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "terms_accepted": True,
        "role": "Customer",
    }
    resp = client.post(
        "/api/auth/register",
        json=payload,
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _seed_agents() -> None:
    seeds = [
        {
            "slug": "onboarding-guide",
            "name": "Onboarding Guide",
            "description": "Guided onboarding with next-step tracking.",
            "category": "workflow",
        },
        {
            "slug": "cape-support-bot",
            "name": "Cape Support Bot",
            "description": "Support bot for FAQs and tickets.",
            "category": "communication",
        },
        {
            "slug": "data-analyst",
            "name": "Data Analyst",
            "description": "Ops insights with summaries.",
            "category": "analytics",
        },
    ]
    with SessionLocal() as session:
        for seed in seeds:
            agent = session.scalar(
                select(models.Agent).where(models.Agent.slug == seed["slug"])
            )
            if agent is None:
                agent = models.Agent(
                    slug=seed["slug"],
                    name=seed["name"],
                    description=seed["description"],
                    visibility="public",
                )
                session.add(agent)
                session.flush()

            existing_version = session.scalar(
                select(models.AgentVersion).where(
                    models.AgentVersion.agent_id == agent.id,
                    models.AgentVersion.status == "published",
                )
            )
            if existing_version:
                continue

            manifest = {
                "name": seed["name"],
                "description": seed["description"],
                "placement": seed["category"],
                "tools": ["demo"],
                "category": seed["category"],
                "permissions": ["demo"],
                "capabilities": ["demo"],
                "tags": ["demo"],
                "readme": "demo",
                "changelog": "demo",
            }
            version = models.AgentVersion(
                agent_id=agent.id,
                version="1.0.0",
                manifest=manifest,
                status="published",
            )
            session.add(version)
        session.commit()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_marketplace_agents_and_actions(client):
    _seed_agents()
    token = _register_user(client)
    headers = _auth_headers(token)

    list_resp = client.get("/api/agents?published=true", headers=headers)
    assert list_resp.status_code == 200, list_resp.text
    agents = list_resp.json()
    slugs = {agent["slug"] for agent in agents}
    assert "onboarding-guide" in slugs
    assert "cape-support-bot" in slugs
    assert "data-analyst" in slugs

    detail_resp = client.get("/api/agents/onboarding-guide?published=true", headers=headers)
    assert detail_resp.status_code == 200, detail_resp.text
    detail = detail_resp.json()
    assert detail["slug"] == "onboarding-guide"
    assert detail["permissions"], "permissions missing"

    launch_resp = client.post(
        "/api/agents/onboarding-guide/launch",
        json={"input": {"source": "test"}},
        headers=headers,
    )
    assert launch_resp.status_code == 201, launch_resp.text
    run_id = launch_resp.json()["id"]

    action_resp = client.post(
        "/api/agents/onboarding-guide/action",
        json={"run_id": run_id, "action": "next_step", "payload": {}},
        headers=headers,
    )
    assert action_resp.status_code == 200, action_resp.text
    action_payload = action_resp.json()["result"]
    step = action_payload.get("step")
    assert step is not None

    blocked_resp = client.post(
        "/api/agents/onboarding-guide/action",
        json={
            "run_id": run_id,
            "action": "blocked",
            "payload": {"step_key": step["step_key"], "reason": "Waiting on data"},
        },
        headers=headers,
    )
    assert blocked_resp.status_code == 200, blocked_resp.text

    support_launch = client.post(
        "/api/agents/cape-support-bot/launch",
        json={"input": {}},
        headers=headers,
    )
    assert support_launch.status_code == 201, support_launch.text
    support_run_id = support_launch.json()["id"]

    ticket_resp = client.post(
        "/api/agents/cape-support-bot/action",
        json={
            "run_id": support_run_id,
            "action": "create_ticket",
            "payload": {"subject": "Need help", "body": "Test ticket"},
        },
        headers=headers,
    )
    assert ticket_resp.status_code == 200, ticket_resp.text
    assert ticket_resp.json()["result"]["ticket"]["id"]

    analyst_launch = client.post(
        "/api/agents/data-analyst/launch",
        json={"input": {}},
        headers=headers,
    )
    assert analyst_launch.status_code == 201, analyst_launch.text
    analyst_run_id = analyst_launch.json()["id"]

    insight_resp = client.post(
        "/api/agents/data-analyst/action",
        json={
            "run_id": analyst_run_id,
            "action": "insight",
            "payload": {"intent": "project_status"},
        },
        headers=headers,
    )
    assert insight_resp.status_code == 200, insight_resp.text
    insight = insight_resp.json()["result"]
    assert insight.get("title")
    assert insight.get("summary")
