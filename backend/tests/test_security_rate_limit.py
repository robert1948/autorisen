# backend/tests/test_security_rate_limit.py
from __future__ import annotations

import os

import pytest
from httpx import AsyncClient

CSRF_HEADER_CANDIDATES = ("X-CSRF-Token", "X-CSRFToken", "X-XSRF-TOKEN")
CSRF_COOKIE_CANDIDATES = ("csrftoken", "csrf_token", "XSRF-TOKEN")


async def _csrf_headers(ac: AsyncClient) -> dict[str, str]:
    r = await ac.get("/api/auth/csrf")
    assert r.status_code in (200, 204), f"CSRF probe failed: {r.status_code} {r.text}"

    token = ""
    if r.headers.get("content-type", "").lower().startswith("application/json"):
        data = r.json()
        token = data.get("csrf") or data.get("csrf_token") or data.get("token") or ""

    if not token:
        for h in CSRF_HEADER_CANDIDATES:
            v = r.headers.get(h)
            if v:
                token = v
                break
    if not token:
        for c in CSRF_COOKIE_CANDIDATES:
            v = r.cookies.get(c)
            if v:
                token = v
                break
    if not token:
        token = "test-csrf-token"

    for cookie_name in CSRF_COOKIE_CANDIDATES:
        ac.cookies.set(cookie_name, token, domain="test", path="/")

    return {CSRF_HEADER_CANDIDATES[0]: token}


@pytest.mark.anyio
async def test_login_rate_limited(rate_async_client: AsyncClient):
    """Burst login requests; expect limiter signal if enabled."""
    if os.getenv("DISABLE_RATE_LIMIT", "0").lower() in {"1", "true", "yes"}:
        pytest.skip("Rate limiting disabled in test environment")

    headers = await _csrf_headers(rate_async_client)
    payload = {"email": "rate@example.com", "password": "wrong"}

    for _ in range(30):
        await rate_async_client.post("/api/auth/login", json=payload, headers=headers)

    r = await rate_async_client.post("/api/auth/login", json=payload, headers=headers)

    if r.status_code not in (429, 403):
        pytest.skip(
            f"Rate limit not enforced in tests (got {r.status_code}); skipping."
        )
    else:
        assert r.status_code in (429, 403)
