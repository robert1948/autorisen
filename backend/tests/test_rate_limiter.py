import time
import requests
import uuid

BASE = "http://127.0.0.1:8000"


def test_login_rate_limit():
    # Use a unique email to avoid DB collisions; login route is a dev stub that accepts any credentials
    email = f"rate+{uuid.uuid4().hex}@example.com"
    password = "irrelevant"
    # limit set in code: 10 per 60s
    allowed = 10
    # First allowed requests should succeed (200)
    for i in range(allowed):
        resp = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password}, timeout=5)
        assert resp.status_code == 200

    # Next request should be rate-limited (429)
    resp2 = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password}, timeout=5)
    assert resp2.status_code == 429


def test_request_reset_rate_limit():
    # request-reset limit set to 5 per 300s
    email = f"rr+{uuid.uuid4().hex}@example.com"
    allowed = 5
    for i in range(allowed):
        resp = requests.post(f"{BASE}/api/auth/request-reset", json={"email": email}, timeout=5)
        assert resp.status_code == 200

    resp2 = requests.post(f"{BASE}/api/auth/request-reset", json={"email": email}, timeout=5)
    assert resp2.status_code == 429
