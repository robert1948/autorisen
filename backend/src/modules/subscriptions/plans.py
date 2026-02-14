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
    id="starter",
    name="Starter",
    display_price="$0",
    amount=Decimal("0.00"),
    currency="USD",
    interval=None,
    features=[
        "One guided workflow-mapping session",
        "CapeAI assistant for a single process",
        "Basic reporting and history",
    ],
    cta_label="Get Started Free",
    sort_order=0,
)

GROWTH = Plan(
    id="growth",
    name="Growth",
    display_price="$249/mo",
    amount=Decimal("249.00"),
    currency="USD",
    interval="month",
    features=[
        "Multiple workflows across your business",
        "Team access with roles and permissions",
        "Ops insights and automation tuning",
    ],
    cta_label="Talk to Sales",
    sort_order=1,
)

ENTERPRISE = Plan(
    id="enterprise",
    name="Enterprise",
    display_price="Let's talk",
    amount=None,
    currency="USD",
    interval=None,
    features=[
        "Dedicated environment & governance",
        "Custom tool adapters and integrations",
        "24/7 support & SLAs",
    ],
    cta_label="Contact Us",
    sort_order=2,
)


ALL_PLANS: list[Plan] = sorted([STARTER, GROWTH, ENTERPRISE], key=lambda p: p.sort_order)

PLANS_BY_ID: dict[str, Plan] = {p.id: p for p in ALL_PLANS}


def get_plan(plan_id: str) -> Plan | None:
    return PLANS_BY_ID.get(plan_id)
