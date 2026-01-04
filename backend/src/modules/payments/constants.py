"""PayFast product definitions.

This module defines non-UI, backend-only PayFast products that can be referenced
by stable product codes.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PayFastProduct:
    code: str
    amount_zar: Decimal
    item_name: str
    item_description: str | None = None


# Live verification (internal): low-value product for confirming production
# PayFast configuration. This should not be exposed as a normal selectable SKU.
LIVE_VERIFY_R5 = "LIVE_VERIFY_R5"

LIVE_VERIFY_R5_PRODUCT = PayFastProduct(
    code=LIVE_VERIFY_R5,
    amount_zar=Decimal("5.00"),
    item_name="Live Verification (R5)",
    item_description="Live PayFast payment verification only (R5.00).",
)


_PAYFAST_PRODUCTS_BY_CODE: dict[str, PayFastProduct] = {
    LIVE_VERIFY_R5_PRODUCT.code: LIVE_VERIFY_R5_PRODUCT,
}


def get_payfast_product_by_code(code: str) -> PayFastProduct | None:
    return _PAYFAST_PRODUCTS_BY_CODE.get(code.strip())
