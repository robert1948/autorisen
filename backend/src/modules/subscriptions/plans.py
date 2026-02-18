"""Subscription plan catalog.

Defines the three pricing tiers available on the platform.
This is the single source of truth for plan metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    display_price: str
    amount: Optional[Decimal]  # None = custom pricing
    currency: str
    interval: Optional[str]  # "month", None for free / custom
    features: List[str] = field(default_factory=list)
    cta_label: str = "Get Started"
    is_public: bool = True
    sort_order: int = 0


STARTER = Plan(
    id="free",
    name="Free",
    display_price="$0",
    amount=Decimal("0.00"),
    currency="USD",
    interval=None,
    features=[
        "5 AI agents",
        "100 monthly executions",
        "Basic integrations",
        "Community support",
        "Standard templates",
    ],
    cta_label="Get Started Free",
    sort_order=0,
)

GROWTH = Plan(
    id="pro",
    name="Pro",
    display_price="$29/mo",
    amount=Decimal("29.00"),
    currency="USD",
    interval="month",
    features=[
        "50 AI agents",
        "2,500 monthly executions",
        "All integrations",
        "Priority support",
        "Advanced templates",
        "Custom workflows",
        "Analytics dashboard",
    ],
    cta_label="Start Pro Trial",
    sort_order=1,
)

ENTERPRISE = Plan(
    id="enterprise",
    name="Enterprise",
    display_price="$99/mo",
    amount=Decimal("99.00"),
    currency="USD",
    interval="month",
    features=[
        "Unlimited AI agents",
        "Unlimited executions",
        "Custom integrations",
        "Dedicated support",
        "White-label options",
        "Advanced security",
        "SLA guarantees",
        "On-premise deployment",
    ],
    cta_label="Contact Sales",
    sort_order=2,
)


ALL_PLANS: list[Plan] = sorted([STARTER, GROWTH, ENTERPRISE], key=lambda p: p.sort_order)

PLANS_BY_ID: dict[str, Plan] = {p.id: p for p in ALL_PLANS}


def get_plan(plan_id: str) -> Plan | None:
    return PLANS_BY_ID.get(plan_id)
