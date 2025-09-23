import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient


# Load the app module directly by path to avoid package import issues in CI/local
def _load_app():
    base = Path(__file__).parents[1] / "app"
    module_path = base / "main.py"
    spec = importlib.util.spec_from_file_location("health_app", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app


def test_alive():
    app = _load_app()
    client = TestClient(app)
    r = client.get("/alive")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_ping():
    app = _load_app()
    client = TestClient(app)
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json().get("status") == "pong"

