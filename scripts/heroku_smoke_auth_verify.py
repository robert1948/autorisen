"""Authenticated smoke verification without leaking secrets."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from backend.src.app import app


def _csrf_headers(client: TestClient) -> dict[str, str]:
    resp = client.get("/api/auth/csrf")
    resp.raise_for_status()
    token = resp.json().get("csrf_token")
    return {"X-CSRF-Token": token} if token else {}


def main() -> None:
    client = TestClient(app)
    email = f"smoke_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!23$"

    register_payload = {
        "first_name": "Smoke",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "terms_accepted": True,
        "role": "Customer",
    }

    register = client.post(
        "/api/auth/register", json=register_payload, headers=_csrf_headers(client)
    )
    print(f"register_status={register.status_code}")
    if register.status_code != 201:
        print("register_error=failed")
        return

    token = register.json().get("access_token")
    if not token:
        print("register_error=missing_access_token")
        return

    auth_headers = {"Authorization": f"Bearer {token}"}

    agents = client.get("/api/agents", headers=auth_headers)
    print(f"agents_status={agents.status_code}")
    if agents.status_code == 200:
        data = agents.json()
        print(f"agents_count={len(data) if isinstance(data, list) else 0}")

    insight = client.get(
        "/api/ops/insights?intent=project_status", headers=auth_headers
    )
    print(f"ops_status={insight.status_code}")
    if insight.status_code == 200:
        payload = insight.json()
        title = payload.get("title")
        summary = payload.get("summary")
        status_value = None
        for metric in payload.get("key_metrics", []) or []:
            if isinstance(metric, dict) and metric.get("label") == "status":
                status_value = metric.get("value")
                break
        print(f"ops_title={title}")
        print(f"ops_summary={summary}")
        print(f"ops_status_value={status_value}")


if __name__ == "__main__":
    main()
