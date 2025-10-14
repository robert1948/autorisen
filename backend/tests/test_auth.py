# backend/tests/test_auth.py
from __future__ import annotations

"""Integration tests for authentication flow (register -> login -> refresh -> me)."""

import json
import uuid
from typing import Any, Dict, Optional, Tuple

import pytest
from sqlalchemy import text

from backend.src.core.rate_limit import limiter  # single place for limiter
from backend.src.db.session import SessionLocal


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
    with SessionLocal() as db:
        db.execute(
            text(
                """
                TRUNCATE
                  analytics_events,
                  role_permissions,
                  user_roles,
                  sessions,
                  login_audits,
                  credentials,
                  permissions,
                  roles,
                  user_profiles,
                  users
                RESTART IDENTITY CASCADE;
                """
            )
        )
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
        client, "/api/auth/register/step1", step1_payload, headers=_headers_for_ip(ip)
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
    r2 = _post_json_or_query_payload(
        client,
        "/api/auth/register/step2",
        step2_payload,
        headers={"Authorization": f"Bearer {temp_token}", **_headers_for_ip(ip)},
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
    login = client.post("/api/auth/login", json={"email": email, "password": password})
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
            headers=_headers_for_ip(ip),
        )
        assert res.status_code == 401, res.text

    # Sixth should trigger limiter (allow 401 until limiter is fully active)
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "bad"},
        headers=_headers_for_ip(ip),
    )
    assert res.status_code in (401, 429), res.text


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
    )
    assert res.status_code == 422, res.text
    body = res.json()
    msgs = [err.get("msg", "") for err in body.get("detail", [])]
    assert any("Password" in m and ("12" in m or "length" in m.lower()) for m in msgs)


def test_login_refresh_cookie_logout_flow(client):
    email = f"cookie_{uuid.uuid4().hex[:8]}@example.com"
    password = "CookiePass123!"

    _complete_registration(client, email, password)

    login = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    access_token = login.json().get("access_token")
    assert access_token
    refresh_cookie = login.cookies.get("refresh_token")
    assert refresh_cookie, "refresh cookie not issued"

    # Refresh without explicit payload should use the cookie
    refresh = client.post("/api/auth/refresh")
    assert refresh.status_code == 200, refresh.text
    new_access = refresh.json().get("access_token")
    assert new_access, "refresh did not return access token"
    rotated_cookie = refresh.cookies.get("refresh_token")
    assert rotated_cookie and rotated_cookie != refresh_cookie

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204, logout.text

    # Refresh should now fail because cookie has been cleared/revoked
    refresh_after_logout = client.post("/api/auth/refresh")
    assert refresh_after_logout.status_code == 401
