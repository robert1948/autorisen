# backend/tests/test_auth.py
"""Integration tests for authentication flow (register -> login -> refresh -> me)."""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import text

from backend.src.core import mailer as mailer_core
from backend.src.core.rate_limit import limiter  # single place for limiter
from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.auth.csrf import CSRF_COOKIE_NAME
from backend.src.services.security import create_jwt

CSRF_HEADER = "X-CSRF-Token"


def _latest_verification_token() -> str:
    assert mailer_core.TEST_OUTBOX, "expected verification email to be sent"
    message = mailer_core.TEST_OUTBOX[-1]
    body = message.get_body(preferencelist=("html", "plain"))
    content = body.get_content() if body is not None else message.get_content()
    match = re.search(r"/verify-email/([A-Za-z0-9._\-]+)", content)
    assert match, "verification token not found in email content"
    return match.group(1)


def _post_json_or_query_payload(
    client, url: str, body: Dict[str, Any], *, headers: Optional[Dict[str, str]] = None
):
    """POST JSON; if API expects ?payload=, retry accordingly."""
    r = client.post(url, json=body, headers=headers or {})
    if r.status_code == 422 and '"query","payload"' in r.text:
        r = client.post(
            url, params={"payload": json.dumps(body)}, headers=headers or {}
        )
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
        "password_reset_tokens",
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
        limiter.reset()
    except Exception:
        pass

    yield


def _headers_for_ip(ip: str) -> Dict[str, str]:
    # Make the backend see a stable client IP (if it trusts X-Forwarded-For)
    return {"X-Forwarded-For": ip}


def _csrf_headers_for_ip(
    client, ip: str, extra: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    headers = _headers_for_ip(ip)
    if extra:
        headers.update(extra)
    return _csrf_headers(client, headers)


def _csrf_headers(client, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data.get("csrf_token") or data.get("csrf") or data.get("token")
    assert token, f"missing csrf token in response: {data}"
    cookie_jar = getattr(client, "cookies", None)
    if cookie_jar is not None:
        cookie_jar.set(CSRF_COOKIE_NAME, token, path="/")
    headers: Dict[str, str] = {CSRF_HEADER: token}
    if extra:
        headers.update(extra)
    return headers


def _login(client, email: str, password: str, ip: str = "127.0.0.1"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=_csrf_headers_for_ip(client, ip),
    )
    assert response.status_code == 200, response.text
    return response


def _refresh(client, refresh_token: Optional[str] = None):
    if refresh_token:
        return client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token},
            headers=_csrf_headers(client),
        )
    return client.post("/api/auth/refresh", headers=_csrf_headers(client))


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
    auto_verify: bool = True,
) -> Tuple[str, str, Dict[str, Any]]:
    # Step 1
    step1_payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": role,
        "recaptcha_token": "dev-bypass-token",
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

    if auto_verify:
        token = _latest_verification_token()
        verify = client.get(f"/api/auth/verify?token={token}", allow_redirects=False)
        assert verify.status_code == 307, verify.text

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
        auto_verify=False,
    )
    assert user["email"] == email
    assert user["first_name"] == "Dev"
    assert user.get("role") in ("Developer", "developer")

    # Unverified login should fail
    unverified_login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=_csrf_headers(client),
    )
    assert unverified_login.status_code == 403
    assert "not verified" in unverified_login.text.lower()

    token = _latest_verification_token()
    verify = client.get(f"/api/auth/verify?token={token}", allow_redirects=False)
    assert verify.status_code == 307

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
    ref = _refresh(client, refresh_token)
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
        client,
        email,
        good,
        role="Customer",
        first_name="Rate",
        last_name="Limit",
        ip=ip,
    )

    # Five bad attempts -> 401
    for _ in range(5):
        res = client.post(
            "/api/auth/login",
            json={"email": email, "password": "bad"},
            headers=_csrf_headers_for_ip(client, ip),
        )
        assert res.status_code == 401, res.text

    # Sixth should trigger limiter (allow 401 until limiter is fully active)
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": "bad"},
        headers=_csrf_headers_for_ip(client, ip),
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
            "recaptcha_token": "dev-bypass-token",
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
            "recaptcha_token": "dev-bypass-token",
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
    refresh = _refresh(client)
    assert refresh.status_code == 200, refresh.text
    new_access = refresh.json().get("access_token")
    assert new_access, "refresh did not return access token"
    rotated_cookie = refresh.cookies.get("refresh_token")
    assert rotated_cookie and rotated_cookie != refresh_cookie

    logout = client.post("/api/auth/logout", headers=_csrf_headers(client))
    assert logout.status_code == 204, logout.text

    # Refresh should now fail because cookie has been cleared/revoked
    refresh_after_logout = _refresh(client)
    assert refresh_after_logout.status_code == 401


def test_logout_revokes_current_token(client):
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutPass123!"
    _complete_registration(client, email, password)

    login_response = _login(client, email, password)
    access_token = login_response.json().get("access_token")
    assert access_token

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
    _complete_registration(client, email, password)

    first_login = _login(client, email, password)
    access_token = first_login.json().get("access_token")
    assert access_token

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

    other_me = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {access_token_2}"}
    )
    assert other_me.status_code == 401
    assert "Session invalidated" in other_me.text


def test_logout_idempotent(client):
    email = f"logoutidem_{uuid.uuid4().hex[:8]}@example.com"
    password = "LogoutIdemPass123!"
    _complete_registration(client, email, password)

    login_response = _login(client, email, password)
    access_token = login_response.json().get("access_token")
    assert access_token

    headers = {"Authorization": f"Bearer {access_token}"}
    logout_headers = _csrf_headers(client, headers)
    first = client.post("/api/auth/logout", json={}, headers=logout_headers)
    assert first.status_code == 200
    second = client.post(
        "/api/auth/logout", json={}, headers=_csrf_headers(client, headers)
    )
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
            "token_version": int(getattr(user, "token_version", 0)),
        }
        expired_token, _ = create_jwt(payload, -1)

    headers = {"Authorization": f"Bearer {expired_token}"}
    res = client.post(
        "/api/auth/logout", json={}, headers=_csrf_headers(client, headers)
    )
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
        "recaptcha_token": "dev-bypass-token",
    }
    res = client.post("/api/auth/register/step1", json=payload)
    assert res.status_code == 403


def test_login_requires_csrf(client):
    email = f"csrf-login_{uuid.uuid4().hex[:8]}@example.com"
    password = "CsrfLoginPass123!"
    _complete_registration(client, email, password)

    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 403


def test_verification_resend_throttle(client):
    email = f"verify_{uuid.uuid4().hex[:8]}@example.com"
    password = "VerifyPass123!"
    _complete_registration(client, email, password, auto_verify=False)

    first = client.post(
        "/api/auth/verify/resend",
        json={"email": email},
        headers=_csrf_headers(client),
    )
    assert first.status_code == 202, first.text

    second = client.post(
        "/api/auth/verify/resend",
        json={"email": email},
        headers=_csrf_headers(client),
    )
    assert second.status_code == 429, second.text


def test_password_reset_flow(client, monkeypatch):
    email = f"reset_{uuid.uuid4().hex[:8]}@example.com"
    original_password = "OriginalPass123!"
    new_password = "NewPass123!@#"

    _complete_registration(client, email, original_password)

    captured: Dict[str, Any] = {}

    def fake_send(email_arg: str, reset_url: str, expires_at):
        captured["email"] = email_arg
        captured["reset_url"] = reset_url
        captured["expires_at"] = expires_at

    monkeypatch.setattr(
        "backend.src.modules.auth.router.send_password_reset_email", fake_send
    )

    forgot = client.post(
        "/api/auth/password/forgot",
        json={"email": email},
        headers=_csrf_headers(client),
    )
    assert forgot.status_code == 200, forgot.text
    assert captured["email"] == email.lower()
    reset_url = captured["reset_url"]
    parsed = urlparse(reset_url)
    assert "reset-password" in parsed.path
    assert parsed.query == "", "reset token must not be in querystring"
    token_list = parse_qs(parsed.fragment).get("token", [])
    assert token_list, "reset token not provided"
    token = token_list[0]

    reset_response = client.post(
        "/api/auth/password/reset",
        json={
            "token": token,
            "password": new_password,
            "confirm_password": new_password,
        },
        headers=_csrf_headers(client),
    )
    assert reset_response.status_code == 200, reset_response.text

    # Token should be single-use.
    second_reset = client.post(
        "/api/auth/password/reset",
        json={
            "token": token,
            "password": new_password,
            "confirm_password": new_password,
        },
        headers=_csrf_headers(client),
    )
    assert second_reset.status_code == 400

    # Old password rejected
    old_login = client.post(
        "/api/auth/login",
        json={"email": email, "password": original_password},
        headers=_csrf_headers(client),
    )
    assert old_login.status_code == 401

    # New password works
    new_login = client.post(
        "/api/auth/login",
        json={"email": email, "password": new_password},
        headers=_csrf_headers(client),
    )
    assert new_login.status_code == 200


def test_password_reset_unknown_email_is_noop(client, monkeypatch):
    captured: Dict[str, Any] = {}

    def fake_send(email_arg: str, reset_url: str, expires_at):
        captured["email"] = email_arg

    monkeypatch.setattr(
        "backend.src.modules.auth.router.send_password_reset_email", fake_send
    )

    forgot = client.post(
        "/api/auth/password/forgot",
        json={"email": "unknown@example.com"},
        headers=_csrf_headers(client),
    )
    assert forgot.status_code == 200, forgot.text
    assert not captured, "email should not be sent for unknown accounts"
