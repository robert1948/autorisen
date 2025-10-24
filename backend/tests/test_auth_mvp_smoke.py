from __future__ import annotations

import uuid


def _csrf_headers(client):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def test_register_login_me_smoke(client):
    email = f"mvp_{uuid.uuid4().hex[:8]}@example.com"
    password = "Passw0rd!23$"

    register_payload = {
        "first_name": "MVP",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "role": "Customer",
    }

    register = client.post(
        "/api/auth/register",
        json=register_payload,
        headers=_csrf_headers(client),
    )
    assert register.status_code == 201, register.text
    body = register.json()
    assert body.get("access_token"), "access_token missing"
    assert body.get("refresh_token"), "refresh_token missing"

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers=_csrf_headers(client),
    )
    assert login.status_code == 200, login.text
    tokens = login.json()
    access_token = tokens.get("access_token")
    assert access_token, "access_token missing from login"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200, me.text
    profile = me.json()
    assert profile["email"] == email
    assert profile["first_name"] == "MVP"
