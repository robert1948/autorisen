"""Pydantic schemas for PayFast interactions."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

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
