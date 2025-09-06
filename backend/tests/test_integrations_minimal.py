import os

# Default tests to local Postgres (docker-compose) unless overridden
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://%s:%s@127.0.0.1:5433/%s"
    % (
        os.getenv("POSTGRES_USER", "autorisen"),
        os.getenv("POSTGRES_PASSWORD", "postgres"),
        os.getenv("POSTGRES_DB", "autorisen"),
    ),
)

from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.init_db import *  # ensure tables exist


client = TestClient(fastapi_app)


def test_create_crm_lead_minimal():
    resp = client.post(
        "/api/v1/integrations/crm/leads",
        json={"name": "Alice", "email": "alice@example.com", "source": "web"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "stored"
    assert data["id"]
    assert isinstance(data["external"], dict)


def test_create_pos_order_minimal():
    resp = client.post(
        "/api/v1/integrations/pos/orders",
        json={"item": "Coffee", "quantity": 2, "total_cents": 700},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] in ("stored", "pending", "succeeded", "failed")
    assert data["id"]
    assert isinstance(data["external"], dict)
