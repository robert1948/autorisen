import uuid
import requests
from time import sleep

BASE = "http://127.0.0.1:8000"


def make_user(email=None, password="old-pass"):
    if email is None:
        email = f"ti+{uuid.uuid4().hex}@example.com"
    name = "Test User"
    resp = requests.post(f"{BASE}/api/auth/register", json={"email": email, "password": password, "name": name}, timeout=5)
    # allow existing users (idempotent in some test runs)
    assert resp.status_code in (200, 201)
    return email, password


def login(email, password):
    resp = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password}, timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    return data["access_token"]


def get_me(token):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE}/api/auth/me", headers=headers, timeout=5)


def test_token_invalidated_after_password_change():
    # create user and login
    email, old_password = make_user()
    access = login(email, old_password)

    # ensure token works
    r = get_me(access)
    assert r.status_code == 200

    # request reset (dev returns token)
    rr = requests.post(f"{BASE}/api/auth/request-reset", json={"email": email}, timeout=5)
    assert rr.status_code == 200
    token = rr.json().get("token")
    assert token

    # confirm reset with new password -> this sets password_changed_at
    new_password = "new-pass-123"
    cr = requests.post(f"{BASE}/api/auth/confirm-reset", json={"token": token, "new_password": new_password}, timeout=5)
    assert cr.status_code == 200

    # Old token should now be rejected
    r2 = get_me(access)
    assert r2.status_code == 401

    # Logging in with new password should succeed
    access2 = login(email, new_password)
    r3 = get_me(access2)
    assert r3.status_code == 200
