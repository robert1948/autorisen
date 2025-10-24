# backend/tests/test_security_csrf.py
import pytest
from httpx import AsyncClient

# Common header/cookie names many CSRF middlewares use.
CSRF_HEADER_CANDIDATES = ("X-CSRF-Token", "X-CSRFToken", "X-XSRF-TOKEN")
CSRF_COOKIE_CANDIDATES = ("csrftoken", "csrf_token", "XSRF-TOKEN")


async def _prime_csrf(client: AsyncClient) -> tuple[str, str]:
    """
    Fetch CSRF token and ensure an acceptable cookie is present.
    Returns (header_name, token).
    """
    r = await client.get("/api/auth/csrf")
    assert r.status_code in (200, 204), f"CSRF probe failed: {r.status_code} {r.text}"

    data = {}
    if r.headers.get("content-type", "").startswith("application/json"):
        data = r.json()
    token = data.get("csrf_token") or data.get("token") or ""

    # If the endpoint set a cookie, keep it; also set one explicitly under common names.
    # Some middleware requires a cookie *and* a matching header.
    for cookie_name in CSRF_COOKIE_CANDIDATES:
        client.cookies.set(cookie_name, token, domain="test", path="/")

    # Pick the first common header the middleware should accept.
    header_name = CSRF_HEADER_CANDIDATES[0]
    return header_name, token


@pytest.mark.anyio
async def test_reject_without_csrf(client: AsyncClient):
    # Mutating route with **no** CSRF should be rejected
    r = await client.post("/api/orgs", json={"name": "x"})
    assert r.status_code in (
        400,
        401,
        403,
    ), f"expected CSRF rejection, got {r.status_code} {r.text}"


@pytest.mark.anyio
async def test_accept_with_csrf(client: AsyncClient):
    header_name, token = await _prime_csrf(client)
    r = await client.post(
        "/api/orgs",
        json={"name": "x"},
        headers={header_name: token},
    )
    assert r.status_code in (
        200,
        201,
    ), f"expected success with CSRF, got {r.status_code} {r.text}"
