"""Pydantic schemas for PayFast interactions."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PayFastCheckoutRequest(BaseModel):
    product_code: Optional[str] = Field(
        default=None,
        max_length=64,
        description="Optional stable product code (e.g. LIVE_VERIFY_R5)",
    )
    amount: Optional[Decimal] = Field(
        default=None, gt=0, description="Payment amount in ZAR"
    )
    item_name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    item_description: Optional[str] = Field(default=None, max_length=255)
    customer_email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Ignored — backend uses the authenticated user's email",
    )
    customer_first_name: Optional[str] = Field(default=None, max_length=64)
    customer_last_name: Optional[str] = Field(default=None, max_length=64)
    metadata: Dict[str, str | int | float] = Field(default_factory=dict)

    @model_validator(mode="after")
    def require_product_or_amount_fields(self):
        if self.product_code:
            return self

        if self.amount is None or self.item_name is None:
            raise ValueError(
                "Either product_code must be provided, or amount and item_name must be set"
            )

        return self

    @field_validator("metadata")
    @classmethod
    def limit_metadata(
        cls, value: Dict[str, str | int | float]
    ) -> Dict[str, str | int | float]:
        if len(value) > 5:
            # PayFast allows up to custom_str5; enforce early.
            pruned = dict(list(value.items())[:5])
            return pruned
        return value


class PayFastCheckoutResponse(BaseModel):
    process_url: str
    fields: Dict[str, str]


class PayFastITNResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Plan catalog
# ---------------------------------------------------------------------------


class PlanFeature(BaseModel):
    text: str


class PlanOut(BaseModel):
    id: str
    name: str
    description: str
    price_monthly_zar: str
    price_yearly_zar: str
    product_code_monthly: Optional[str] = None
    product_code_yearly: Optional[str] = None
    features: List[str]
    is_default: bool = False
    is_enterprise: bool = False


class PlansResponse(BaseModel):
    plans: List[PlanOut]
    currency: str = "ZAR"


# ---------------------------------------------------------------------------
# Subscription
# ---------------------------------------------------------------------------


class SubscriptionOut(BaseModel):
    id: str
    plan_id: str
    plan_name: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    cancelled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubscriptionCreateRequest(BaseModel):
    plan_id: str = Field(..., description="Plan to subscribe to: free, pro, enterprise")
    billing_cycle: str = Field(
        default="monthly",
        description="monthly or yearly",
    )

    @field_validator("plan_id")
    @classmethod
    def validate_plan_id(cls, v: str) -> str:
        if v.lower() not in ("free", "pro", "enterprise"):
            raise ValueError("plan_id must be free, pro, or enterprise")
        return v.lower()

    @field_validator("billing_cycle")
    @classmethod
    def validate_billing_cycle(cls, v: str) -> str:
        if v.lower() not in ("monthly", "yearly"):
            raise ValueError("billing_cycle must be monthly or yearly")
        return v.lower()


class SubscriptionCancelResponse(BaseModel):
    message: str
    cancel_at_period_end: bool
    current_period_end: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


class InvoiceOut(BaseModel):
    id: str
    amount: str
    currency: str
    status: str
    item_name: str
    item_description: Optional[str] = None
    payment_provider: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    invoices: List[InvoiceOut]
    total: int
