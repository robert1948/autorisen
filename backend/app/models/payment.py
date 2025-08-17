"""
Payment system models for Cape Control platform
Based on the comprehensive payment specification
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, CheckConstraint, Index, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
import uuid
from app.database import Base

# UUID type that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise String(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

# JSON type that works with both SQLite and PostgreSQL
def JSONType():
    """Returns JSONB for PostgreSQL, Text for SQLite"""
    from sqlalchemy import Text
    from sqlalchemy.dialects import postgresql
    return postgresql.JSONB().with_variant(Text, "sqlite")


class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False, unique=True)
    tier = Column(String(20), nullable=False)  # Basic, Pro, Enterprise
    status = Column(String(20), nullable=False, default="Active")  # Active, Cancelled, Expired
    start_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    end_date = Column(DateTime(timezone=True))
    stripe_subscription_id = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="subscription")


class Credits(Base):
    """User credit balance model"""
    __tablename__ = "credits"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False, unique=True)
    balance = Column(Integer, nullable=False, default=0)
    total_purchased = Column(Integer, nullable=False, default=0)
    total_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="credits")


class CreditTransaction(Base):
    """Credit purchase and usage history"""
    __tablename__ = "credit_transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'purchase', 'usage', 'bonus'
    amount = Column(Integer, nullable=False)  # positive for add, negative for deduct
    description = Column(String(255))
    stripe_payment_intent_id = Column(String(100))
    agent_id = Column(String(100))  # for usage transactions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint(transaction_type.in_(['purchase', 'usage', 'bonus', 'refund']), name='valid_transaction_type'),
    )
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="credit_transactions")


class CustomRequest(Base):
    """Custom agent development requests (upsell)"""
    __tablename__ = "custom_requests"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False)
    stripe_payment_intent_id = Column(String(100))
    description = Column(Text, nullable=False)
    requirements = Column(JSONType())  # detailed requirements
    quote_amount = Column(DECIMAL(10, 2))
    status = Column(String(20), default="Pending")
    budget_range = Column(String(50))
    timeline = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint(status.in_(['Pending', 'Quoted', 'Paid', 'InProgress', 'Completed', 'Rejected']), name='valid_status'),
    )
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="custom_requests")


class SupportTicket(Base):
    """Support tickets and priority support tracking"""
    __tablename__ = "support_tickets"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False)
    stripe_payment_intent_id = Column(String(100))  # for priority support add-on
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="Medium")
    status = Column(String(20), default="Open")
    assigned_to = Column(String(100))  # staff member
    resolution = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint(priority.in_(['Low', 'Medium', 'High', 'Critical']), name='valid_priority'),
        CheckConstraint(status.in_(['Open', 'InProgress', 'Resolved', 'Closed']), name='valid_status'),
    )
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="support_tickets")


class PaymentAnalyticsEvent(Base):
    """Analytics and event tracking for payments"""
    __tablename__ = "payment_analytics_events"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id"))
    data = Column(JSONType())  # flexible event data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships (no back_populates to avoid conflicts with main analytics)
    user = relationship("User", lazy="select")


class PaymentAnalytics(Base):
    """Payment analytics for developer earnings tracking"""
    __tablename__ = "payment_analytics"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey("users_v2.id"))
    event_type = Column(String(50), nullable=False, index=True)  # subscription_created, payment_succeeded, etc.
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    event_metadata = Column(JSONType())  # additional event data (renamed from metadata)
    stripe_payment_intent_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships (no back_populates to avoid circular imports)
    customer = relationship("User", lazy="select")


class Payment(Base):
    """Payment records for transaction tracking"""
    __tablename__ = "payments"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False)
    stripe_payment_intent_id = Column(String(100), unique=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default="pending")  # pending, succeeded, failed, cancelled
    description = Column(Text)
    payment_metadata = Column(JSONType())  # renamed from metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships (no back_populates to avoid circular imports)
    customer = relationship("User", lazy="select")


class PaymentMethod(Base):
    """Stored payment methods (references to Stripe)"""
    __tablename__ = "payment_methods"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users_v2.id"), nullable=False)
    stripe_payment_method_id = Column(String(100), nullable=False, unique=True)
    type = Column(String(20), default="card")  # card, bank_account, etc.
    last_four = Column(String(4))
    brand = Column(String(20))  # visa, mastercard, etc.
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="payment_methods")


# Pricing configuration (can be moved to environment or config)
SUBSCRIPTION_TIERS = {
    "Basic": {
        "price": 0,  # Free tier
        "api_calls": 100,
        "agent_access": ["basic"],
        "support": "community",
        "features": ["basic_agents", "community_support"]
    },
    "Pro": {
        "price": 2000,  # $20.00 in cents
        "api_calls": 1000,
        "agent_access": ["basic", "premium"],
        "support": "email_chat",
        "features": ["all_agents", "customization", "email_support", "chat_support"]
    },
    "Enterprise": {
        "price": 10000,  # $100.00 in cents
        "api_calls": -1,  # unlimited
        "agent_access": ["basic", "premium", "enterprise"],
        "support": "dedicated",
        "features": ["unlimited_agents", "custom_development", "dedicated_manager", "priority_support", "advanced_analytics"]
    }
}

CREDIT_PACKS = {
    "small": {
        "credits": 500,
        "price": 500,  # $5.00 in cents
        "bonus": 0
    },
    "medium": {
        "credits": 2000,
        "price": 2000,  # $20.00 in cents
        "bonus": 100  # 5% bonus
    },
    "large": {
        "credits": 10000,
        "price": 10000,  # $100.00 in cents
        "bonus": 1000  # 10% bonus
    }
}

AGENT_COSTS = {
    "basic": 10,  # credits per hour
    "premium": 50,  # credits per hour
    "enterprise": 100  # credits per hour
}
