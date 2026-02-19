"""PayFast product definitions and plan catalog.

This module defines non-UI, backend-only PayFast products that can be referenced
by stable product codes, plus the subscription plan catalog.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List


@dataclass(frozen=True)
class PayFastProduct:
    code: str
    amount_zar: Decimal
    item_name: str
    item_description: str | None = None


@dataclass(frozen=True)
class PlanDefinition:
    """Public plan definition exposed via /api/payments/plans."""

    id: str
    name: str
    description: str
    price_monthly_zar: Decimal
    price_yearly_zar: Decimal
    product_code_monthly: str | None
    product_code_yearly: str | None
    features: list[str] = field(default_factory=list)
    is_default: bool = False
    is_enterprise: bool = False


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


# ---------------------------------------------------------------------------
# Plan catalog (exposed via /api/payments/plans)
# ---------------------------------------------------------------------------

FREE_PLAN = PlanDefinition(
    id="free",
    name="Free",
    description="Get started with CapeControl basics",
    price_monthly_zar=Decimal("0.00"),
    price_yearly_zar=Decimal("0.00"),
    product_code_monthly=None,
    product_code_yearly=None,
    features=[
        "3 AI agents",
        "100 monthly executions",
        "Community support",
        "Basic integrations",
    ],
    is_default=True,
)

PRO_PLAN = PlanDefinition(
    id="pro",
    name="Pro",
    description="Scale your automation with more power",
    price_monthly_zar=Decimal("529.00"),
    price_yearly_zar=Decimal("4990.00"),
    product_code_monthly=PRO_MONTHLY,
    product_code_yearly=PRO_YEARLY,
    features=[
        "50 AI agents",
        "2,500 monthly executions",
        "All integrations",
        "Priority email support",
        "Advanced analytics",
    ],
)

ENTERPRISE_PLAN = PlanDefinition(
    id="enterprise",
    name="Enterprise",
    description="Unlimited power for large teams",
    price_monthly_zar=Decimal("1799.00"),
    price_yearly_zar=Decimal("17190.00"),
    product_code_monthly=ENTERPRISE_MONTHLY,
    product_code_yearly=ENTERPRISE_YEARLY,
    features=[
        "Unlimited AI agents",
        "Unlimited executions",
        "Custom integrations",
        "Dedicated account manager",
        "SLA guarantees",
        "SSO & advanced security",
    ],
    is_enterprise=True,
)

PLANS: List[PlanDefinition] = [FREE_PLAN, PRO_PLAN, ENTERPRISE_PLAN]
PLANS_BY_ID: Dict[str, PlanDefinition] = {p.id: p for p in PLANS}


def get_plan_by_id(plan_id: str) -> PlanDefinition | None:
    return PLANS_BY_ID.get(plan_id.strip().lower())
