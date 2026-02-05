from __future__ import annotations

import uuid


def _csrf_headers(client):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def _assert_error_envelope(payload: dict):
    assert "error" in payload, payload
    error = payload["error"]
    assert isinstance(error, dict), payload
    assert error.get("code"), payload
    assert error.get("message"), payload


def test_login_invalid_credentials_enveloped(client):
    email = f"missing_{uuid.uuid4().hex[:6]}@example.com"
    resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": "invalid"},
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 401, resp.text
    body = resp.json()
    _assert_error_envelope(body)
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_register_validation_error_enveloped(client):
    payload = {
        "first_name": "",
        "last_name": "",
        "email": "not-an-email",
        "password": "short",
        "confirm_password": "short",
    }
    resp = client.post(
        "/api/auth/register",
        json=payload,
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 422, resp.text
    body = resp.json()
    _assert_error_envelope(body)
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"].get("fields"), body


def test_refresh_requires_csrf(client):
    no_csrf = client.post("/api/auth/refresh")
    assert no_csrf.status_code == 403, no_csrf.text
    no_csrf_body = no_csrf.json()
    _assert_error_envelope(no_csrf_body)
    assert no_csrf_body["error"]["code"] == "CSRF_FAILED"

    with_csrf = client.post("/api/auth/refresh", headers=_csrf_headers(client))
    assert with_csrf.status_code == 401, with_csrf.text
    with_csrf_body = with_csrf.json()
    _assert_error_envelope(with_csrf_body)
    assert with_csrf_body["error"]["code"] == "INVALID_REFRESH_TOKEN"