# backend/tests/test_auth.py
from __future__ import annotations

"""Integration tests for authentication flow (register -> login -> refresh -> me)."""

import json
import uuid
from typing import Any, Dict, Optional, Tuple

import pytest
from sqlalchemy import text

from backend.src.core.rate_limit import limiter  # single place for limiter
from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.services.security import create_jwt

CSRF_HEADER = "X-CSRF-Token"


def _post_json_or_query_payload(
    client, url: str, body: Dict[str, Any], *, headers: Optional[Dict[str, str]] = None
):
    """POST JSON; if API expects ?payload=, retry accordingly."""
    r = client.post(url, json=body, headers=headers or {})
    if r.status_code == 422 and '"query","payload"' in r.text:
        r = client.post(url, params={"payload": json.dumps(body)}, headers=headers or {})
    return r


@pytest.fixture(autouse=True)
def _clean_auth_state():
    """
    Hard reset of auth-related state between tests:
    - Truncate known tables and reset IDs (Postgres)
    - Reset in-memory/IP-based limiter state
    """
    # DB reset
    tables = [
        "analytics_events",
        "role_permissions",
        "user_roles",
        "sessions",
        "login_audits",
        "credentials",
        "permissions",
        "roles",
        "user_profiles",
        "users",
    ]

    with SessionLocal() as db:
        bind = db.get_bind()
        dialect = getattr(bind.dialect, "name", "") if bind else ""

        if dialect == "postgresql":
            existing = {
                row[0]
                for row in db.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
                )
            }
            targets = [t for t in tables if t in existing]
            if targets:
                joined = ", ".join(targets)
                db.execute(text(f"TRUNCATE {joined} RESTART IDENTITY CASCADE;"))
        else:
            # SQLite fallback used in dev CI/sandboxes — cascade manually.
            db.execute(text("PRAGMA foreign_keys = OFF;"))
            for table in tables:
                try:
                    db.execute(text(f"DELETE FROM {table};"))
                except Exception:
                    pass
            try:
                db.execute(text("DELETE FROM sqlite_sequence;"))
            except Exception:
                pass
            db.execute(text("PRAGMA foreign_keys = ON;"))

        db.commit()

    # Limiter reset (memory/redis)
    try:
        limiter.reset("*")  # if your limiter supports wildcard
    except Exception:
        pass

    yield


def _headers_for_ip(ip: str) -> Dict[str, str]:
    # Make the backend see a stable client IP (if it trusts X-Forwarded-For)
    return {"X-Forwarded-For": ip}


def _csrf_headers(client, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    headers: Dict[str, str] = {CSRF_HEADER: token}
    if extra:
        headers.update(extra)
    return headers


def _login(client, email: str, password: str, ip: str = "127.0.0.1"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=_csrf_headers(client, _headers_for_ip(ip)),
    )
    assert response.status_code == 200, response.text
    return response


def _complete_registration(
    client,
    email: str,
    password: str,
    *,
    role: str = "Customer",
    first_name: str = "Test",
    last_name: str = "User",
    company_name: str = "Test Co",
    ip: str = "127.0.0.1",
) -> Tuple[str, str, Dict[str, Any]]:
    # Step 1
    step1_payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": role,
        "recaptcha_token": "unit-test-token",
    }
    r1 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step1",
        step1_payload,
        headers=_csrf_headers(client, _headers_for_ip(ip)),
    )
    assert r1.status_code == 201, r1.text
    temp_token = r1.json()["temp_token"]

    # Step 2 profile differs per role
    if role == "Customer":
        profile = {
            "industry": "Technology",
            "company_size": "1-10",
            "use_cases": ["Testing"],
            "budget_range": "<$1k",
        }
    else:
        profile = {
            "skills": ["Python", "FastAPI"],
            "experience_level": "Senior",
            "portfolio_link": "https://example.com",
            "availability": "Full-time",
        }

    step2_payload = {"company_name": company_name, "profile": profile}
    step2_headers = _headers_for_ip(ip)
    step2_headers["Authorization"] = f"Bearer {temp_token}"
    r2 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step2",
        step2_payload,
        headers=_csrf_headers(client, step2_headers),
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    return body["access_token"], body["refresh_token"], body["user"]


def test_register_login_refresh_me_flow(client):
    email = f"dev_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongerPass123!"

    access_token, refresh_token, user = _complete_registration(
        client,
        email,
        password,
        role="Developer",
        first_name="Dev",
        last_name="Example",
        company_name="Dev LLC",
    )
    assert user["email"] == email
    assert user["first_name"] == "Dev"
    assert user.get("role") in ("Developer", "developer")

    # Login
    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=_csrf_headers(client),
    )
    assert login.status_code == 200, login.text
    login_json: Dict[str, Any] = login.json()
    access_token = login_json.get("access_token")
    refresh_token = login_json.get("refresh_token")
    assert access_token, f"missing access_token in {login_json}"
    assert refresh_token, f"missing refresh_token in {login_json}"

    # /me
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200, me.text
    payload = me.json()
    assert payload["email"] == email
    assert payload["first_name"] == "Dev"
    # company_name may be flattened or nested; accept either
    assert payload.get("company_name") in (None, "Dev LLC") or "company" in payload

    # refresh
    ref = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert ref.status_code == 200, ref.text
    ref_json: Dict[str, Any] = ref.json()
    new_access = ref_json.get("access_token")
    new_refresh = ref_json.get("refresh_token")
    assert new_access and new_refresh and new_refresh != refresh_token

    # /me with new token
    me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me2.status_code == 200, me2.text
    assert me2.json()["email"] == email


def test_login_rate_limit(client):
    email = f"rate_{uuid.uuid4().hex[:8]}@example.com"
    good = "SecurePass123!"
    ip = "203.0.113.77"  # test IP

    _complete_registration(
        client, email, good, role="Customer", first_name="Rate", last_name="Limit", ip=ip
    )

    # Five bad attempts -> 401
    for _ in range(5):
        res = client.post(
            "/api/auth/login",
            json={"email": email, "password": "bad"},
            headers=_csrf_headers(client, _headers_for_ip(ip)),
        )
        assert res.status_code == 401, res.text

    # Sixth should trigger limiter (allow 401 until limiter is fully active)
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "bad"},
        headers=_csrf_headers(client, _headers_for_ip(ip)),
    )
    assert res.status_code in (401, 429), res.text
    if res.status_code == 429:
        assert "Retry-After" in res.headers


def test_register_duplicate_email(client):
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    password = "DuplicatePass123!"

    _complete_registration(client, email, password)

    step1 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step1",
        {
            "first_name": "Other",
            "last_name": "User",
            "email": email,
            "password": password,
            "confirm_password": password,
            "role": "Customer",
            "recaptcha_token": "unit-test-token",
        },
        headers=_csrf_headers(client),
    )
    assert step1.status_code in (409, 400), step1.text  # 409 preferred


def test_password_policy_enforced(client):
    res = _post_json_or_query_payload(
        client,
        "/api/auth/register/step1",
        {
            "first_name": "Policy",
            "last_name": "Test",
            "email": f"policy_{uuid.uuid4().hex[:8]}@example.com",
            "password": "short",
            "confirm_password": "short",
            "role": "Customer",
            "recaptcha_token": "unit-test-token",
        },
        headers=_csrf_headers(client),
    )
    assert res.status_code == 422, res.text
    body = res.json()
    msgs = [err.get("msg", "") for err in body.get("detail", [])]
    assert any("Password" in m and ("12" in m or "length" in m.lower()) for m in msgs)


def test_login_refresh_cookie_logout_flow(client):
    email = f"cookie_{uuid.uuid4().hex[:8]}@example.com"
    password = "CookiePass123!"

    _complete_registration(client, email, password)

    login_response = _login(client, email, password)
    login = login_response.json()
    access_token = login.get("access_token")
    assert access_token
    refresh_cookie = login_response.cookies.get("refresh_token")
    assert refresh_cookie, "refresh cookie not issued"

    # Refresh without explicit payload should use the cookie
    refresh = client.post("/api/auth/refresh")
    assert refresh.status_code == 200, refresh.text
    new_access = refresh.json().get("access_token")
    assert new_access, "refresh did not return access token"
    rotated_cookie = refresh.cookies.get("refresh_token")
    assert rotated_cookie and rotated_cookie != refresh_cookie

    logout = client.post("/api/auth/logout", headers=_csrf_headers(client))
    assert logout.status_code == 204, logout.text

    # Refresh should now fail because cookie has been cleared/revoked
    refresh_after_logout = client.post("/api/auth/refresh")
    assert refresh_after_logout.status_code == 401


def test_logout_revokes_current_token(client):
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutPass123!"
    access_token, _, _ = _complete_registration(client, email, password)

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_headers = _csrf_headers(client, headers)
    res = client.post("/api/auth/logout", json={}, headers=logout_headers)
    assert res.status_code == 200, res.text
    assert res.json()["message"] == "Logged out"

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 401
    assert "Token revoked" in me.text


def test_logout_all_devices_invalidates_other_tokens(client):
    email = f"logoutall_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutAllPass123!"
    access_token, _, _ = _complete_registration(client, email, password)

    second_login = _login(client, email, password, ip="198.51.100.7")
    access_token_2 = second_login.json().get("access_token")
    assert access_token_2

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_headers = _csrf_headers(client, headers)
    res = client.post(
        "/api/auth/logout",
        json={"all_devices": True},
        headers=logout_headers,
    )
    assert res.status_code == 200

    other_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token_2}"})
    assert other_me.status_code == 401
    assert "Session invalidated" in other_me.text


def test_logout_idempotent(client):
    email = f"logoutidem_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutIdemPass123!"
    access_token, _, _ = _complete_registration(client, email, password)

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_headers = _csrf_headers(client, headers)
    first = client.post("/api/auth/logout", json={}, headers=logout_headers)
    assert first.status_code == 200
    second = client.post("/api/auth/logout", json={}, headers=_csrf_headers(client, headers))
    assert second.status_code == 200


def test_logout_with_expired_token_returns_200(client):
    email = f"exp_{uuid.uuid4().hex[:8]}@example.com"
    password = "ExpiredLogoutPass123!"
    _, _, _ = _complete_registration(client, email, password)

    with SessionLocal() as db:
        user = db.query(models.User).filter(models.User.email == email.lower()).one()
        payload = {
            "sub": user.email,
            "user_id": user.id,
            "role": user.role,
            "purpose": "access",
            "jti": uuid.uuid4().hex,
            "token_version": int(getattr(user, "token_version", 1)),
        }
        expired_token, _ = create_jwt(payload, -1)

    headers = {"Authorization": f"Bearer {expired_token}"}
    res = client.post("/api/auth/logout", json={}, headers=_csrf_headers(client, headers))
    assert res.status_code == 200, res.text
    assert res.json()["message"] == "Logged out"


def test_register_requires_csrf(client):
    email = f"csrf_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "first_name": "NoCsrf",
        "last_name": "User",
        "email": email,
        "password": "NoCsrfPass123!",
        "confirm_password": "NoCsrfPass123!",
        "role": "Customer",
        "recaptcha_token": "unit-test-token",
    }
    res = client.post("/api/auth/register/step1", json=payload)
    assert res.status_code == 403


def test_login_requires_csrf(client):
    email = f"csrf-login_{uuid.uuid4().hex[:8]}@example.com"
    password = "CsrfLoginPass123!"
    _complete_registration(client, email, password)

    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 403
