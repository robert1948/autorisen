from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.app import app

client = TestClient(app)


def test_health_endpoint_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") in ("ok", "healthy")
    assert isinstance(payload.get("version"), str)


def test_alive_endpoint_ok():
    response = client.get("/api/health/alive")
    assert response.status_code == 200
    assert response.json() == {"alive": True}


def test_ping_endpoint_ok():
    response = client.get("/api/health/ping")
    assert response.status_code == 200
    assert response.json().get("ping") == "pong"
