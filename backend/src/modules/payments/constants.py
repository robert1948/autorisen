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
PRO_MONTHLY = "PRO_MONTHLY"
ENTERPRISE_MONTHLY = "ENTERPRISE_MONTHLY"
PRO_YEARLY = "PRO_YEARLY"
ENTERPRISE_YEARLY = "ENTERPRISE_YEARLY"

LIVE_VERIFY_R5_PRODUCT = PayFastProduct(
    code=LIVE_VERIFY_R5,
    amount_zar=Decimal("5.00"),
    item_name="Live Verification (R5)",
    item_description="Live PayFast payment verification only (R5.00).",
)

PRO_MONTHLY_PRODUCT = PayFastProduct(
    code=PRO_MONTHLY,
    amount_zar=Decimal("529.00"),
    item_name="CapeControl Pro — Monthly",
    item_description="CapeControl Pro plan: 50 AI agents, 2500 monthly executions, all integrations, priority support.",
)

ENTERPRISE_MONTHLY_PRODUCT = PayFastProduct(
    code=ENTERPRISE_MONTHLY,
    amount_zar=Decimal("1799.00"),
    item_name="CapeControl Enterprise — Monthly",
    item_description="CapeControl Enterprise plan: unlimited agents, custom integrations, dedicated support, SLA guarantees.",
)

PRO_YEARLY_PRODUCT = PayFastProduct(
    code=PRO_YEARLY,
    amount_zar=Decimal("4990.00"),
    item_name="CapeControl Pro — Yearly",
    item_description="CapeControl Pro plan (annual): Save 20%. 50 AI agents, 2500 monthly executions, all integrations.",
)

ENTERPRISE_YEARLY_PRODUCT = PayFastProduct(
    code=ENTERPRISE_YEARLY,
    amount_zar=Decimal("17190.00"),
    item_name="CapeControl Enterprise — Yearly",
    item_description="CapeControl Enterprise plan (annual): Save 20%. Unlimited agents, custom integrations, dedicated support.",
)


_PAYFAST_PRODUCTS_BY_CODE: dict[str, PayFastProduct] = {
    LIVE_VERIFY_R5_PRODUCT.code: LIVE_VERIFY_R5_PRODUCT,
    PRO_MONTHLY_PRODUCT.code: PRO_MONTHLY_PRODUCT,
    ENTERPRISE_MONTHLY_PRODUCT.code: ENTERPRISE_MONTHLY_PRODUCT,
    PRO_YEARLY_PRODUCT.code: PRO_YEARLY_PRODUCT,
    ENTERPRISE_YEARLY_PRODUCT.code: ENTERPRISE_YEARLY_PRODUCT,
}


def get_payfast_product_by_code(code: str) -> PayFastProduct | None:
    return _PAYFAST_PRODUCTS_BY_CODE.get(code.strip())
