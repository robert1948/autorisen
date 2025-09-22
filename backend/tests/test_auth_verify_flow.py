import pytest
import requests
import uuid

from app.crud import user as crud_user
from app.deps import get_db
from app.core.security import create_verification_token


BASE = "http://127.0.0.1:8000"


def create_test_user(db, email: str):
    # create a user using the CRUD helper
    return crud_user.create_user(db, email=email, name="Test Verify", password_plain="password123")


def test_request_and_confirm_verify():
    # Create user in DB with a unique email to avoid collisions
    email = f"test+{uuid.uuid4().hex}@example.com"
    with next(get_db()) as db:
        user = create_test_user(db, email=email)
        assert user is not None
        assert not user.is_verified

    # Hit request-verify endpoint to ensure it accepts the request (server prints link to logs in dev)
    resp = requests.post(f"{BASE}/api/auth/request-verify", json={"email": "test+verify@example.com"}, timeout=5)
    assert resp.status_code == 200
    assert 'Verification link generated' in resp.json().get('message', '')

    # Prefer token returned by the endpoint in dev; fallback to creating one directly
    token = resp.json().get('token') or create_verification_token(user.id)

    # Call confirm endpoint
    resp2 = requests.get(f"{BASE}/api/auth/confirm-verify?token={token}", timeout=5)
    assert resp2.status_code == 200
    assert resp2.json().get('ok') is True

    # Verify DB user flag
    with next(get_db()) as db:
        refreshed = crud_user.get_user_by_email(db, 'test+verify@example.com')
        assert refreshed is not None
        assert refreshed.is_verified is True
