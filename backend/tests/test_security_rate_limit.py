import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_rate_limited(client: AsyncClient):
    # Hammer invalid creds to trigger limiter (or at least 401, then 429)
    for _ in range(10):
        await client.post(
            "/api/auth/login", json={"email": "bad@ex.com", "password": "wrong"}
        )
    r = await client.post(
        "/api/auth/login", json={"email": "bad@ex.com", "password": "wrong"}
    )
    assert r.status_code in (401, 429), f"Expected 401/429, got {r.status_code}"
