"""API-level integration tests for OpenClaw authenticated task creation."""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.auth.csrf import CSRF_COOKIE_NAME
from backend.src.services.csrf import generate_csrf_token
from backend.src.services.security import create_jwt, hash_password


def _create_verified_user(email: str, *, role: str = "Customer") -> models.User:
    with SessionLocal() as db:
        user = models.User(
            email=email,
            first_name="OpenClaw",
            last_name="API Tester",
            hashed_password=hash_password("StrongPass123!"),
            role=role,
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
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "jti": f"jti_{uuid4().hex}",
            "token_version": int(getattr(user, "token_version", 0) or 0),
        },
        expires_in=timedelta(minutes=30),
    )
    return {"Authorization": f"Bearer {token}"}


def _csrf_headers(client) -> dict[str, str]:
    csrf_token = generate_csrf_token()
    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set(CSRF_COOKIE_NAME, csrf_token, path="/")

    return {"X-CSRF-Token": csrf_token}


def _new_auth_headers(*, role: str = "Customer") -> dict[str, str]:
    user = _create_verified_user(
        f"openclaw_api_{uuid4().hex[:10]}@example.com",
        role=role,
    )
    return _auth_headers(user)


def _post_with_auth_csrf(client, url: str, auth_headers: dict[str, str], *, json=None):
    return client.post(
        url,
        json=json,
        headers={**auth_headers, **_csrf_headers(client)},
    )


def _post_with_csrf(client, url: str, *, json=None):
    return client.post(
        url,
        json=json,
        headers=_csrf_headers(client),
    )


def _task_payload(
    *,
    workflow: str = "support_triage",
    text: str = "Summarize this support ticket",
    mode: str = "assisted",
    idempotency_key: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "workflow": workflow,
        "input": {"text": text},
        "mode": mode,
    }
    if idempotency_key is not None:
        payload["idempotency_key"] = idempotency_key
    return payload


def test_openclaw_tasks_api_reuses_idempotency_key_for_same_user(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()
    idem_key = f"idem_{uuid4().hex[:12]}"

    payload = _task_payload(idempotency_key=idem_key)

    first = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=payload,
    )
    second = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text

    first_body = first.json()
    second_body = second.json()
    assert first_body["task_id"] == second_body["task_id"]
    assert first_body["trace_id"] == second_body["trace_id"]


def test_openclaw_tasks_api_idempotency_is_scoped_per_user(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers_one = _new_auth_headers()
    auth_headers_two = _new_auth_headers()
    idem_key = f"idem_{uuid4().hex[:12]}"

    payload = _task_payload(idempotency_key=idem_key)

    first = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers_one,
        json=payload,
    )
    second = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers_two,
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text

    first_body = first.json()
    second_body = second.json()
    assert first_body["task_id"] != second_body["task_id"]


def test_openclaw_tasks_api_reuses_idempotency_for_requires_approval(
    client, monkeypatch
):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()
    idem_key = f"idem_{uuid4().hex[:12]}"

    payload = _task_payload(
        workflow="status_brief",
        text="Draft and send externally",
        idempotency_key=idem_key,
    )

    first = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=payload,
    )
    second = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=payload,
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text

    first_body = first.json()
    second_body = second.json()
    assert first_body["status"] == "requires_approval"
    assert second_body["status"] == "requires_approval"
    assert first_body["requires_approval"] is True
    assert second_body["requires_approval"] is True
    assert first_body["task_id"] == second_body["task_id"]
    assert first_body["trace_id"] == second_body["trace_id"]


def test_openclaw_tasks_api_rejects_unauthenticated_request(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    response = _post_with_csrf(
        client,
        "/api/openclaw/tasks",
        json=_task_payload(idempotency_key=f"idem_{uuid4().hex[:12]}"),
    )

    assert response.status_code == 401, response.text
    assert response.json().get("detail") == "Not authenticated"


def test_openclaw_approve_endpoint_completes_task(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    create_payload = _task_payload(
        workflow="status_brief",
        text="Draft and send externally",
        idempotency_key=f"idem_{uuid4().hex[:12]}",
    )
    created = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=create_payload,
    )
    assert created.status_code == 200, created.text
    create_body = created.json()
    assert create_body["status"] == "requires_approval"

    task_id = create_body["task_id"]
    pending = client.get(
        f"/api/openclaw/tasks/{task_id}",
        headers=auth_headers,
    )
    assert pending.status_code == 200, pending.text
    approval_id = pending.json().get("approval_id")
    assert approval_id

    approved = _post_with_auth_csrf(
        client,
        f"/api/openclaw/approvals/{approval_id}/approve",
        auth_headers,
        json={"comment": "Ship it", "ttl_minutes": 30},
    )
    assert approved.status_code == 200, approved.text
    approved_body = approved.json()
    assert approved_body["approval_id"] == approval_id
    assert approved_body["status"] == "approved"

    completed = client.get(
        f"/api/openclaw/tasks/{task_id}",
        headers=auth_headers,
    )
    assert completed.status_code == 200, completed.text
    completed_body = completed.json()
    assert completed_body["status"] == "completed"
    assert completed_body["output"] is not None


def test_openclaw_reject_endpoint_marks_task_rejected(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    create_payload = _task_payload(
        workflow="status_brief",
        text="Draft and send externally",
        idempotency_key=f"idem_{uuid4().hex[:12]}",
    )
    created = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=create_payload,
    )
    assert created.status_code == 200, created.text
    create_body = created.json()
    assert create_body["status"] == "requires_approval"

    task_id = create_body["task_id"]
    pending = client.get(
        f"/api/openclaw/tasks/{task_id}",
        headers=auth_headers,
    )
    assert pending.status_code == 200, pending.text
    approval_id = pending.json().get("approval_id")
    assert approval_id

    rejected = _post_with_auth_csrf(
        client,
        f"/api/openclaw/approvals/{approval_id}/reject",
        auth_headers,
        json={"comment": "Do not proceed", "ttl_minutes": 30},
    )
    assert rejected.status_code == 200, rejected.text
    rejected_body = rejected.json()
    assert rejected_body["approval_id"] == approval_id
    assert rejected_body["status"] == "rejected"

    rejected_task = client.get(
        f"/api/openclaw/tasks/{task_id}",
        headers=auth_headers,
    )
    assert rejected_task.status_code == 200, rejected_task.text
    rejected_task_body = rejected_task.json()
    assert rejected_task_body["status"] == "rejected"
    assert rejected_task_body["policy_reason"] == "approval_rejected"


def test_openclaw_approve_endpoint_returns_404_for_missing_approval(
    client, monkeypatch
):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    missing_approval_id = f"apr_missing_{uuid4().hex[:12]}"
    response = _post_with_auth_csrf(
        client,
        f"/api/openclaw/approvals/{missing_approval_id}/approve",
        auth_headers,
        json={"comment": "approve", "ttl_minutes": 30},
    )

    assert response.status_code == 404, response.text
    assert response.json().get("detail") == "openclaw approval not found"


def test_openclaw_reject_endpoint_returns_404_for_missing_approval(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    missing_approval_id = f"apr_missing_{uuid4().hex[:12]}"
    response = _post_with_auth_csrf(
        client,
        f"/api/openclaw/approvals/{missing_approval_id}/reject",
        auth_headers,
        json={"comment": "reject", "ttl_minutes": 30},
    )

    assert response.status_code == 404, response.text
    assert response.json().get("detail") == "openclaw approval not found"


def test_openclaw_stats_api_returns_expected_shape_for_non_admin(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    created = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        auth_headers,
        json=_task_payload(idempotency_key=f"idem_{uuid4().hex[:12]}"),
    )
    assert created.status_code == 200, created.text

    response = client.get("/api/openclaw/stats?days=7", headers=auth_headers)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["window_days"] == 7
    assert "since" in body
    assert isinstance(body.get("event_breakdown"), dict)
    assert isinstance(body.get("total_events"), int)
    assert isinstance(body.get("total_tokens_in"), int)
    assert isinstance(body.get("total_tokens_out"), int)
    assert isinstance(body.get("total_cost_usd"), float)


def test_openclaw_stats_api_admin_scope_is_broader_than_user_scope(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    headers_one = _new_auth_headers()
    headers_two = _new_auth_headers()
    admin_headers = _new_auth_headers(role="admin")

    created_one = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        headers_one,
        json=_task_payload(idempotency_key=f"idem_{uuid4().hex[:12]}"),
    )
    created_two = _post_with_auth_csrf(
        client,
        "/api/openclaw/tasks",
        headers_two,
        json=_task_payload(idempotency_key=f"idem_{uuid4().hex[:12]}"),
    )
    assert created_one.status_code == 200, created_one.text
    assert created_two.status_code == 200, created_two.text

    user_stats = client.get("/api/openclaw/stats?days=7", headers=headers_one)
    admin_stats = client.get("/api/openclaw/stats?days=7", headers=admin_headers)

    assert user_stats.status_code == 200, user_stats.text
    assert admin_stats.status_code == 200, admin_stats.text

    user_body = user_stats.json()
    admin_body = admin_stats.json()
    assert admin_body["total_events"] >= user_body["total_events"]


def test_openclaw_stats_api_rejects_days_below_minimum(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    response = client.get("/api/openclaw/stats?days=0", headers=auth_headers)
    assert response.status_code == 422, response.text


def test_openclaw_stats_api_rejects_days_above_maximum(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()

    response = client.get("/api/openclaw/stats?days=91", headers=auth_headers)
    assert response.status_code == 422, response.text


def test_openclaw_aggregation_run_requires_admin(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=3&dry_run=true",
        auth_headers,
    )

    assert response.status_code == 403, response.text
    assert response.json().get("detail") == "Not authorized"


def test_openclaw_retention_run_requires_admin(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    auth_headers = _new_auth_headers()
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=30&dry_run=true",
        auth_headers,
    )

    assert response.status_code == 403, response.text
    assert response.json().get("detail") == "Not authorized"


def test_openclaw_aggregation_run_allows_admin(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=3&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["days_back"] == 3
    assert body["dry_run"] is True
    assert "generated_at" in body
    assert isinstance(body.get("rollups"), list)


def test_openclaw_retention_run_allows_admin(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=30&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["retention_days"] == 30
    assert body["dry_run"] is True
    assert "cutoff" in body
    assert isinstance(body.get("audit_events_affected"), int)
    assert isinstance(body.get("usage_logs_affected"), int)


def test_openclaw_aggregation_run_rejects_days_back_below_minimum(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=0&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_aggregation_run_rejects_days_back_above_maximum(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=91&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_retention_run_rejects_retention_days_below_minimum(
    client, monkeypatch
):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=6&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_retention_run_rejects_retention_days_above_maximum(
    client, monkeypatch
):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=366&dry_run=true",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_aggregation_run_rejects_malformed_dry_run(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=3&dry_run=notabool",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_retention_run_rejects_malformed_dry_run(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=30&dry_run=notabool",
        admin_headers,
    )

    assert response.status_code == 422, response.text


def test_openclaw_aggregation_run_accepts_dry_run_false(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/aggregation/run?days_back=3&dry_run=false",
        admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["days_back"] == 3
    assert body["dry_run"] is False


def test_openclaw_retention_run_accepts_dry_run_false(client, monkeypatch):
    monkeypatch.setenv("OPENCLAW_BEDROCK_ENABLED", "0")

    admin_headers = _new_auth_headers(role="admin")
    response = _post_with_auth_csrf(
        client,
        "/api/openclaw/retention/run?retention_days=30&dry_run=false",
        admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["retention_days"] == 30
    assert body["dry_run"] is False
