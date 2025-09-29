
"""Integration tests for authentication flow."""

from pathlib import Path
import sys

from fastapi.testclient import TestClient
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.app import app
from backend.src.db.session import SessionLocal

client = TestClient(app)


def _reset_auth_tables() -> None:
    with SessionLocal() as db:
        for table in (
            "role_permissions",
            "user_roles",
            "sessions",
            "credentials",
            "permissions",
            "roles",
            "users",
        ):
            db.execute(text(f"DELETE FROM {table}"))
        db.commit()


def test_register_login_refresh_me_flow() -> None:
    _reset_auth_tables()

    email = "dev@example.com"
    password = "secret123"

    register_response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Dev"},
    )
    assert register_response.status_code in (200, 201)

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    login_json = login_response.json()
    access_token = login_json.get("access_token")
    refresh_token = login_json.get("refresh_token")
    assert access_token
    assert refresh_token

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["email"] == email
    assert payload["full_name"] == "Dev"

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    refresh_json = refresh_response.json()
    new_access = refresh_json.get("access_token")
    new_refresh = refresh_json.get("refresh_token")
    assert new_access and new_refresh and new_refresh != refresh_token

    # ensure refreshed access works
    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["email"] == email
    assert payload["full_name"] == "Dev"
