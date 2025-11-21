from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.src.modules.payments import service  # noqa: E402
from backend.src.modules.payments.config import (  # noqa: E402
    PayFastSettings,
    reset_payfast_settings_cache,
)
from backend.src.modules.payments.router import router  # noqa: E402


@pytest.fixture(autouse=True)
def payfast_env(monkeypatch):
    monkeypatch.setenv("PAYFAST_MERCHANT_ID", "10000100")
    monkeypatch.setenv("PAYFAST_MERCHANT_KEY", "abc123")
    monkeypatch.setenv("PAYFAST_RETURN_URL", "https://example.com/return")
    monkeypatch.setenv("PAYFAST_CANCEL_URL", "https://example.com/cancel")
    monkeypatch.setenv("PAYFAST_NOTIFY_URL", "https://example.com/itn")
    monkeypatch.setenv("PAYFAST_MODE", "sandbox")
    monkeypatch.setenv("PAYFAST_PASSPHRASE", "secret")
    reset_payfast_settings_cache()
    yield
    reset_payfast_settings_cache()


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    return TestClient(app)


def test_checkout_endpoint_returns_signed_fields():
    client = _client()

    resp = client.post(
        "/api/payments/payfast/checkout",
        json={
            "amount": "120.50",
            "item_name": "CapeControl Plan",
            "item_description": "Pilot",
            "customer_email": "customer@example.com",
            "customer_first_name": "Cape",
            "customer_last_name": "Control",
            "metadata": {"order": "O-1"},
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["process_url"].startswith("https://sandbox.payfast")
    assert data["fields"]["item_name"] == "CapeControl Plan"
    assert "signature" in data["fields"]


def test_itn_endpoint_validates_signature(monkeypatch):
    client = _client()
    fields = service.build_checkout_fields(
        settings=PayFastSettings(
            merchant_id="10000100",
            merchant_key="abc123",
            return_url="https://example.com/return",
            cancel_url="https://example.com/cancel",
            notify_url="https://example.com/itn",
            mode="sandbox",
            passphrase="secret",
        ),
        amount="10.00",
        item_name="Test",
        customer_email="customer@example.com",
    )

    resp = client.post(
        "/api/payments/payfast/itn",
        data=fields,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    assert resp.text == "OK"

    fields["signature"] = "bad"
    resp = client.post(
        "/api/payments/payfast/itn",
        data=fields,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 400
