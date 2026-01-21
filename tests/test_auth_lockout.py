from __future__ import annotations

import uuid

from backend.src.db import models
from backend.src.db.session import SessionLocal


def _enable_lockout(monkeypatch):
    monkeypatch.setenv("AUTH_LOCKOUT_TESTING", "1")


def _csrf_headers(client, *, ip: str, user_agent: str):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200
    data = resp.json()
    token = data.get("token") or data.get("csrf_token") or data.get("csrf")
    assert token

    # Mirror cookie for CSRFMiddleware comparisons
    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set("csrftoken", token, path="/")

    return {
        "X-CSRF-Token": token,
        "X-Forwarded-For": ip,
        "User-Agent": user_agent,
    }


def _fetch_audits(email: str):
    with SessionLocal() as db:
        return (
            db.query(models.LoginAudit)
            .filter(models.LoginAudit.email == email)
            .order_by(models.LoginAudit.created_at.asc())
            .all()
        )


def test_lockout_after_five_failures(monkeypatch, client):
    _enable_lockout(monkeypatch)

    email = f"lockout_{uuid.uuid4().hex[:8]}@example.com"
    headers = _csrf_headers(client, ip="203.0.113.55", user_agent="lockout-test")

    payload = {"email": email, "password": "badpass"}

    for _ in range(5):
        r = client.post("/api/auth/login", json=payload, headers=headers)
        assert r.status_code == 401

    r6 = client.post("/api/auth/login", json=payload, headers=headers)
    assert r6.status_code in (423, 429)

    audits = _fetch_audits(email)
    assert len(audits) >= 6

    for a in audits[:5]:
        assert a.success is False
        assert a.reason == "INVALID_CREDENTIALS"
        assert a.ip_address == "203.0.113.55"
        assert a.user_agent == "lockout-test"

    locked = audits[5]
    assert locked.success is False
    assert locked.reason == "LOCKED_OUT"
    assert locked.ip_address == "203.0.113.55"
    assert locked.user_agent == "lockout-test"


def test_success_clears_lockout_counter(monkeypatch, client):
    _enable_lockout(monkeypatch)

    email = f"lockout_ok_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123!@#"

    headers = _csrf_headers(client, ip="203.0.113.56", user_agent="lockout-test")

    register_payload = {
        "first_name": "Lockout",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": "Customer",
        "company_name": "Lockout Co",
        "recaptcha_token": "dummy",
    }

    reg = client.post("/api/auth/register", json=register_payload, headers=headers)
    assert reg.status_code == 201

    # Two failed attempts
    for _ in range(2):
        r = client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrong"},
            headers=headers,
        )
        assert r.status_code == 401

    # Success should clear lockout state
    ok = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=headers,
    )
    assert ok.status_code == 200

    # Now we should still get 5 more failures before locked
    for _ in range(5):
        r = client.post(
            "/api/auth/login",
            json={"email": email, "password": "wrong"},
            headers=headers,
        )
        assert r.status_code == 401

    r6 = client.post(
        "/api/auth/login",
        json={"email": email, "password": "wrong"},
        headers=headers,
    )
    assert r6.status_code in (423, 429)

    audits = _fetch_audits(email)
    assert any(a.reason == "SUCCESS" and a.success is True for a in audits)
    assert any(a.reason == "LOCKED_OUT" and a.success is False for a in audits)
