"""Pydantic schemas for subscription endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# --- Plan listing (public) ---

class PlanFeatureOut(BaseModel):
    text: str


class PlanOut(BaseModel):
    id: str
    name: str
    display_price: str
    amount: Optional[Decimal] = None
    currency: str
    interval: Optional[str] = None
    features: List[str]
    cta_label: str
    is_public: bool


# --- Current subscription ---

class SubscriptionOut(BaseModel):
    id: str
    plan_id: str
    plan_name: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    cancelled_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Subscribe / change plan ---

class SubscribeRequest(BaseModel):
    plan_id: str = Field(..., pattern=r"^(starter|growth|enterprise)$")


class SubscribeResponse(BaseModel):
    subscription: SubscriptionOut
    message: str
    checkout_url: Optional[str] = None  # set for paid plans needing checkout


# --- Cancel ---

class CancelRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=500)
    immediate: bool = False  # True = cancel now; False = at period end


class CancelResponse(BaseModel):
    subscription: SubscriptionOut
    message: str


# --- Enterprise inquiry ---

class EnterpriseInquiryRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    contact_name: str = Field(..., min_length=1, max_length=100)
    contact_email: EmailStr
    message: Optional[str] = Field(None, max_length=2000)


class EnterpriseInquiryResponse(BaseModel):
    id: str
    status: str
    message: str


# --- Billing / invoice history ---

class InvoiceOut(BaseModel):
    id: str
    amount: Decimal
    currency: str
    status: str
    item_name: str
    item_description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
