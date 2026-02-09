from __future__ import annotations

import uuid

from sqlalchemy import select

from backend.src.db import models
from backend.src.db.session import SessionLocal


def _csrf_headers(client):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def test_register_login_me_smoke(client):
    email = f"MVP_{uuid.uuid4().hex[:8]}@Example.com"
    normalized_email = email.lower()
    password = "Passw0rd!23$"

    register_payload = {
        "first_name": "MVP",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "terms_accepted": True,
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
        json={"email": normalized_email, "password": password},
        headers=_csrf_headers(client),
    )
    assert login.status_code == 200, login.text
    tokens = login.json()
    access_token = tokens.get("access_token")
    assert access_token, "access_token missing from login"

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200, me.text
    profile = me.json()
    assert profile["email"] == normalized_email
    assert profile["first_name"] == "MVP"

    with SessionLocal() as session:
        user = session.scalar(
            select(models.User).where(models.User.email == normalized_email)
        )
        assert user is not None
        assert user.terms_accepted_at is not None
        assert user.terms_version == "v1"


def test_register_duplicate_email_case_insensitive(client):
    email = f"DUP_{uuid.uuid4().hex[:8]}@Example.com"
    password = "Passw0rd!23$"

    register_payload = {
        "first_name": "Dup",
        "last_name": "Tester",
        "email": email,
        "password": password,
        "confirm_password": password,
        "terms_accepted": True,
        "role": "Customer",
    }

    register = client.post(
        "/api/auth/register",
        json=register_payload,
        headers=_csrf_headers(client),
    )
    assert register.status_code == 201, register.text

    register_payload["email"] = email.lower()
    duplicate = client.post(
        "/api/auth/register",
        json=register_payload,
        headers=_csrf_headers(client),
    )
    assert duplicate.status_code == 409, duplicate.text
