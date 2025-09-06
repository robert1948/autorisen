# backend/app/api/integrations.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.database import get_db
from app.models.integrations import CRMLead, POSOrder
from app.services.integrations_provider import (
    IntegrationsProvider,
    get_integrations_provider,
)


router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/integrations", tags=["integrations"]
)


class CRMLeadIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("email")
    def validate_email(cls, v):  # simple, not strict
        if v and ("@" not in v or "." not in v):
            raise ValueError("invalid email format")
        return v


class CRMLeadOut(BaseModel):
    id: str
    status: str
    external: Dict[str, Any]


@router.post("/crm/leads", response_model=CRMLeadOut)
async def create_crm_lead(
    payload: CRMLeadIn,
    db: Session = Depends(get_db),
    provider: IntegrationsProvider = Depends(get_integrations_provider),
):
    lead = CRMLead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        source=payload.source,
        notes=payload.notes,
        lead_metadata=payload.metadata,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    external = await provider.send_crm_lead(
        {
            "id": str(lead.id),
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
        }
    )

    return CRMLeadOut(id=str(lead.id), status="stored", external=external)


class POSOrderIn(BaseModel):
    item: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(1, ge=1, le=100000)
    total_cents: int = Field(..., ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    customer_name: Optional[str] = Field(None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None


class POSOrderOut(BaseModel):
    id: str
    status: str
    external: Dict[str, Any]


@router.post("/pos/orders", response_model=POSOrderOut)
async def create_pos_order(
    payload: POSOrderIn,
    db: Session = Depends(get_db),
    provider: IntegrationsProvider = Depends(get_integrations_provider),
):
    order = POSOrder(
        customer_name=payload.customer_name,
        item=payload.item,
        quantity=payload.quantity,
        total_cents=payload.total_cents,
        currency=payload.currency,
        order_metadata=payload.metadata,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    external = await provider.send_pos_order(
        {
            "id": str(order.id),
            "item": order.item,
            "quantity": order.quantity,
            "total_cents": order.total_cents,
            "currency": order.currency,
        }
    )

    return POSOrderOut(id=str(order.id), status=order.status, external=external)
