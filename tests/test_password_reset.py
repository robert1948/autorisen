from __future__ import annotations

import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.auth.csrf import CSRF_COOKIE_NAME
from backend.src.modules.auth.reset_tokens import hmac_sha256_hex
from backend.src.modules.auth.service import hash_password

CSRF_HEADER = "X-CSRF-Token"


def _csrf_headers(client):
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json().get("csrf_token")
    assert token
    # Ensure cookie-based CSRF double-submit passes.
    client.cookies.set(CSRF_COOKIE_NAME, token, path="/")
    return {CSRF_HEADER: token}


def test_hmac_sha256_hex_stable(monkeypatch):
    monkeypatch.setenv("RESET_TOKEN_SECRET", "test-reset-secret")

    value = "token-value"
    assert hmac_sha256_hex(value) == hmac_sha256_hex(value)
    assert hmac_sha256_hex(value) != hmac_sha256_hex(value + "x")


def test_forgot_password_non_leaky(client):
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongerPass123!"

    with SessionLocal() as db:
        user = models.User(
            email=email,
            hashed_password=hash_password(password),
            role="Customer",
            is_active=True,
            is_email_verified=True,
            token_version=0,
            password_changed_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()

    headers = _csrf_headers(client)

    r_known = client.post(
        "/api/auth/password/forgot",
        json={"email": email},
        headers=headers,
    )
    r_unknown = client.post(
        "/api/auth/password/forgot",
        json={"email": f"missing_{uuid.uuid4().hex[:8]}@example.com"},
        headers=headers,
    )

    assert r_known.status_code == 200
    assert r_unknown.status_code == 200
    assert r_known.json() == r_unknown.json()


def test_password_reset_consumes_token_once(client, monkeypatch):
    monkeypatch.setenv("RESET_TOKEN_SECRET", "test-reset-secret")

    email = f"reset_{uuid.uuid4().hex[:8]}@example.com"

    with SessionLocal() as db:
        user = models.User(
            email=email,
            hashed_password=hash_password("OldPassword123!"),
            role="Customer",
            is_active=True,
            is_email_verified=True,
            token_version=0,
            password_changed_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.flush()

        raw_token = secrets.token_urlsafe(32)
        token_hash = hmac_sha256_hex(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

        db.add(
            models.PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )
        db.commit()

    headers = _csrf_headers(client)

    payload = {
        "token": raw_token,
        "password": "NewPassword123!",
        "confirm_password": "NewPassword123!",
    }

    r1 = client.post("/api/auth/password/reset", json=payload, headers=headers)
    assert r1.status_code == 200, r1.text

    r2 = client.post("/api/auth/password/reset", json=payload, headers=headers)
    assert r2.status_code == 400, r2.text
