# backend/tests/test_security_csrf.py
from __future__ import annotations

import pytest
from httpx import AsyncClient


# --- Fixture aliasing ---------------------------------------------------------
# Some of your runs expose `rate_async_client` (not `async_client`).
# This alias keeps the tests portable across both setups.
@pytest.fixture
async def async_client(rate_async_client: AsyncClient):  # provided by conftest.py
    yield rate_async_client


# -----------------------------------------------------------------------------

# Common CSRF names many middlewares accept
CSRF_HEADER_CANDIDATES = ("X-CSRF-Token", "X-CSRFToken", "X-XSRF-TOKEN")
CSRF_COOKIE_CANDIDATES = ("csrftoken", "csrf_token", "XSRF-TOKEN")


async def _prime_csrf(client: AsyncClient) -> dict[str, str]:
    """
    Fetch a CSRF token and ensure a matching cookie is present.
    Returns headers to include on subsequent mutating requests.
    """
    r = await client.get("/api/auth/csrf")
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

    # Ensure cookie exists for middlewares requiring cookie+header
    for cookie_name in CSRF_COOKIE_CANDIDATES:
        client.cookies.set(cookie_name, token, domain="test", path="/")

    return {CSRF_HEADER_CANDIDATES[0]: token}


@pytest.mark.anyio
async def test_reject_without_csrf(async_client: AsyncClient):
    """
    A mutating request without CSRF must be rejected (typically 403).
    """
    r = await async_client.post(
        "/api/auth/login", json={"email": "x@example.com", "password": "x"}
    )
    assert (
        r.status_code == 403
    ), f"expected CSRF rejection (403), got {r.status_code} {r.text}"


@pytest.mark.anyio
async def test_accept_with_csrf(async_client: AsyncClient):
    """
    With CSRF supplied, the request should not be blocked for CSRF.
    (Invalid credentials may still yield 400/401; that's fine.)
    """
    headers = await _prime_csrf(async_client)
    r = await async_client.post(
        "/api/auth/login",
        json={"email": "x@example.com", "password": "x"},
        headers=headers,
    )
    assert (
        r.status_code != 403
    ), f"unexpected CSRF rejection with token: {r.status_code} {r.text}"
