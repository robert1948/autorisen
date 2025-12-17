from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.src.modules.payments import service  # noqa: E402
from backend.src.modules.payments.config import PayFastSettings  # noqa: E402


def _settings() -> PayFastSettings:
    return PayFastSettings(
        merchant_id="10000100",
        merchant_key="abc123",
        return_url="https://example.com/return",
        cancel_url="https://example.com/cancel",
        notify_url="https://example.com/itn",
        mode="sandbox",
        passphrase="secret",
    )


def test_build_checkout_fields_generates_signature():
    settings = _settings()
    fields = service.build_checkout_fields(
        settings=settings,
        amount=Decimal("99.99"),
        item_name="CapeControl Plan",
        item_description="Enterprise tier",
        customer_email="customer@example.com",
        customer_first_name="Cape",
        customer_last_name="Control",
        metadata={"order_id": "ord_123"},
    )

    assert fields["merchant_id"] == settings.merchant_id
    assert fields["amount"] == "99.99"
    assert fields["custom_str1"] == "ord_123"
    assert "signature" in fields

    signature = fields["signature"]
    recomputed = service.generate_signature(
        {k: v for k, v in fields.items() if k != "signature"}, settings.passphrase
    )
    assert signature == recomputed


def test_verify_itn_signature_roundtrip():
    settings = _settings()
    payload = service.build_checkout_fields(
        settings=settings,
        amount=50,
        item_name="Test",
        customer_email="customer@example.com",
    )

    assert service.verify_itn_signature(payload, settings=settings)
    payload["signature"] = "invalid"
    assert not service.verify_itn_signature(payload, settings=settings)
