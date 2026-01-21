from __future__ import annotations

import os

import pytest


def _enable_auth_rl(monkeypatch):
    # Auth RL is disabled by default in ENV=test to avoid breaking existing tests.
    monkeypatch.setenv("AUTH_RATE_LIMIT_TESTING", "1")


def _csrf_headers_for_ip(client, ip: str):
    resp = client.get("/api/auth/csrf", headers={"X-Forwarded-For": ip})
    assert resp.status_code == 200
    data = resp.json()
    token = data.get("csrf_token") or data.get("csrf") or data.get("token")
    assert token
    # Mirror cookie for CSRFMiddleware comparisons
    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set("csrftoken", token, path="/")
    return {"X-CSRF-Token": token, "X-Forwarded-For": ip}


def test_login_rate_limit_by_email(monkeypatch, client):
    _enable_auth_rl(monkeypatch)

    ip = "203.0.113.10"
    headers = _csrf_headers_for_ip(client, ip)
    payload = {"email": "ratelimit_test@example.com", "password": "badpass"}

    # Email policy is 5/min; expect 429 on attempt 6.
    statuses = []
    for _ in range(6):
        r = client.post("/api/auth/login", json=payload, headers=headers)
        statuses.append(r.status_code)

    assert statuses[:5] == [401, 401, 401, 401, 401]
    assert statuses[5] == 429


def test_login_rate_limit_by_ip_not_colliding(monkeypatch, client):
    _enable_auth_rl(monkeypatch)

    email_template = "ip_only_{n}@example.com"

    # Same IP: 10/min. Use distinct emails to avoid email limiter.
    ip1 = "203.0.113.20"
    headers1 = _csrf_headers_for_ip(client, ip1)
    for n in range(10):
        r = client.post(
            "/api/auth/login",
            json={"email": email_template.format(n=n), "password": "badpass"},
            headers=headers1,
        )
        assert r.status_code == 401

    r = client.post(
        "/api/auth/login",
        json={"email": email_template.format(n=999), "password": "badpass"},
        headers=headers1,
    )
    assert r.status_code == 429

    # Different IP should not collide with the first IP's counter.
    ip2 = "203.0.113.21"
    headers2 = _csrf_headers_for_ip(client, ip2)
    r2 = client.post(
        "/api/auth/login",
        json={"email": "fresh@example.com", "password": "badpass"},
        headers=headers2,
    )
    assert r2.status_code == 401


@pytest.mark.parametrize(
    "path,endpoint_email_limit,attempts",
    [
        ("/api/auth/password/forgot", 3, 4),
    ],
)
def test_forgot_password_rate_limited(
    monkeypatch, client, path, endpoint_email_limit, attempts
):
    _enable_auth_rl(monkeypatch)

    ip = "203.0.113.30"
    headers = _csrf_headers_for_ip(client, ip)

    payload = {"email": "forgot_limit@example.com"}

    # forgot_password email policy is 3/min; expect 429 on attempt 4.
    statuses = []
    for _ in range(attempts):
        r = client.post(path, json=payload, headers=headers)
        statuses.append(r.status_code)

    assert statuses[:endpoint_email_limit] == [200] * endpoint_email_limit
    assert statuses[endpoint_email_limit] == 429
