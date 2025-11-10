"""Pydantic schemas for PayFast interactions."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field, validator


class PayFastCheckoutRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Payment amount in ZAR")
    item_name: str = Field(..., min_length=3, max_length=255)
    item_description: Optional[str] = Field(default=None, max_length=255)
    customer_email: str = Field(..., min_length=5, max_length=255)
    customer_first_name: Optional[str] = Field(default=None, max_length=64)
    customer_last_name: Optional[str] = Field(default=None, max_length=64)
    metadata: Dict[str, str | int | float] = Field(default_factory=dict)

    @validator("metadata")
    def limit_metadata(cls, value: Dict[str, str | int | float]) -> Dict[str, str | int | float]:
        if len(value) > 5:
            # PayFast allows up to custom_str5; enforce early.
            pruned = dict(list(value.items())[:5])
            return pruned
        return value

    @validator("customer_email")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("customer_email must contain '@'")
        return value


class PayFastCheckoutResponse(BaseModel):
    process_url: str
    fields: Dict[str, str]


class PayFastITNResponse(BaseModel):
    status: str
