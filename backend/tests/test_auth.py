from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from backend.src.modules.auth import service
from backend.src.app import app

client = TestClient(app)


def setup_function() -> None:  # type: ignore[no-redef]
    service.reset_store()


def test_register_login_me_happy_path() -> None:
    register_payload = {"email": "user@example.com", "password": "StrongPass!1", "full_name": "Test User"}
    register_resp = client.post("/api/auth/register", json=register_payload)
    assert register_resp.status_code == 201
    assert register_resp.json() == {"ok": True}

    login_payload = {"email": "user@example.com", "password": "StrongPass!1"}
    login_resp = client.post("/api/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_json = login_resp.json()
    token = login_json["access_token"]
    assert token
    assert login_json["token_type"] == "bearer"

    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_json = me_resp.json()
    assert me_json["email"] == "user@example.com"
    assert me_json["full_name"] == "Test User"
