"""
Minimal models for Custom Integrations (CRM & POS)

Opt-in, non-invasive tables to persist basic lead and order data.
"""

import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base
from app.models.payment import GUID, JSONType


class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="new")
    notes = Column(Text, nullable=True)
    # 'metadata' attribute name is reserved by SQLAlchemy; use a safe attribute name but keep DB column as 'metadata'
    lead_metadata = Column("metadata", JSONType())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class POSOrder(Base):
    __tablename__ = "pos_orders"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_name = Column(String(255), nullable=True)
    item = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_cents = Column(Integer, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="pending")
    # Use a safe attribute name while keeping DB column as 'metadata'
    order_metadata = Column("metadata", JSONType())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
