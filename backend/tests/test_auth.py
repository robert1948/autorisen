"""Integration tests for authentication flow."""

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.app import app
from backend.src.modules.auth import service

client = TestClient(app)


def test_register_login_me_flow() -> None:
    service.reset_store()
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
    token = login_response.json().get("access_token")
    assert token

    me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["email"] == email
    assert "full_name" in payload
