"""Utility script to generate a PayFast checkout payload for smoke tests."""

from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.src.modules.payments import service  # noqa: E402
from backend.src.modules.payments.config import get_payfast_settings  # noqa: E402


def main() -> None:
    settings = get_payfast_settings()
    fields = service.build_checkout_fields(
        settings=settings,
        amount=Decimal("123.45"),
        item_name="CapeControl Subscription",
        item_description="Demo checkout generated via make payments-checkout",
        customer_email="demo@example.com",
        customer_first_name="Demo",
        customer_last_name="User",
        metadata={"env": settings.mode},
    )

    payload = {
        "process_url": settings.process_url,
        "fields": fields,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
