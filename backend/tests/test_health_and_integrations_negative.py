import os
from fastapi.testclient import TestClient

# Point tests to local Postgres via docker-compose defaults
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://%s:%s@127.0.0.1:5433/%s"
    % (
        os.getenv("POSTGRES_USER", "autorisen"),
        os.getenv("POSTGRES_PASSWORD", "postgres"),
        os.getenv("POSTGRES_DB", "autorisen"),
    ),
)

from app.main import app as fastapi_app  # noqa: E402

client = TestClient(fastapi_app)


def test_health_status_ok():
    r = client.get("/api/health/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "healthy"


def test_crm_lead_invalid_email():
    r = client.post(
        "/api/v1/integrations/crm/leads",
        json={"name": "Bob", "email": "not-an-email", "source": "web"},
    )
    assert r.status_code == 422


def test_pos_order_negative_quantity():
    r = client.post(
        "/api/v1/integrations/pos/orders",
        json={"item": "Tea", "quantity": -1, "total_cents": 500},
    )
    assert r.status_code == 422
