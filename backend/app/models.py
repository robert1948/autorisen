from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base  # Updated import for new structure

class User(Base):
    """
    SQLAlchemy model for the users_v2 table.
    Updated for production schema compatibility - August 1, 2025
    Matches actual production database schema
    """
    __tablename__ = "users_v2"
    __table_args__ = {"extend_existing": True}
    
    # Production database columns - matching actual schema
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='CUSTOMER')  # Note: 'role' not 'user_role'
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    website = Column(String(255))
    company = Column(String(255))
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(DateTime(timezone=True))
    experience = Column(String(20))  # beginner, intermediate, advanced, expert
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    terms_accepted_at = Column(DateTime(timezone=True))
    privacy_accepted_at = Column(DateTime(timezone=True))
    
    # Stripe integration fields
    stripe_customer_id = Column(String(255), index=True)  # Stripe customer ID
    subscription_status = Column(String(50))  # active, canceled, past_due, trialing, etc.
    subscription_id = Column(String(255))  # Current Stripe subscription ID
    plan_id = Column(String(100))  # Current plan (basic, pro, enterprise)
    subscription_ends_at = Column(DateTime(timezone=True))  # When subscription ends
    
    # Password reset fields - TEMPORARILY COMMENTED OUT FOR PRODUCTION COMPATIBILITY
    # password_reset_token = Column(String(255))
    # password_reset_expires = Column(DateTime(timezone=True))

    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # conversations = relationship("Conversation", back_populates="user")
    # Payment system relationships
    # subscription = relationship("Subscription", back_populates="user", uselist=False)
    # credits = relationship("Credits", back_populates="user", uselist=False)
    # credit_transactions = relationship("CreditTransaction", back_populates="user")
    # custom_requests = relationship("CustomRequest", back_populates="user")
    # support_tickets = relationship("SupportTicket", back_populates="user")
    # payment_methods = relationship("PaymentMethod", back_populates="user")
    
    # Analytics relationships (using string references to avoid import conflicts) 
    # analytics_events = relationship("AnalyticsEvent", back_populates="user", lazy="dynamic")
    # sessions = relationship("UserSession", back_populates="user", lazy="dynamic")
    # api_usage_stats = relationship("APIUsageStats", back_populates="user", lazy="dynamic")
    # audit_logs relationship handled in AuditLog model to avoid circular imports
    
    # Backward compatibility properties
    @property
    def user_role(self):
        """Backward compatibility for user_role field"""
        return self.role
    
    @user_role.setter
    def user_role(self, value):
        """Backward compatibility setter for user_role field"""
        self.role = value
    
    @property
    def full_name(self):
        """Backward compatibility for full_name field"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return None
    
    @full_name.setter
    def full_name(self, value):
        """Backward compatibility setter for full_name field"""
        if value:
            parts = value.strip().split(' ', 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else None
        else:
            self.first_name = None
            self.last_name = None
    
    @property
    def tos_accepted_at(self):
        """Backward compatibility for tos_accepted_at field"""
        return self.terms_accepted_at
    
    @tos_accepted_at.setter
    def tos_accepted_at(self, value):
        """Backward compatibility setter for tos_accepted_at field"""
        self.terms_accepted_at = value
    
    @property
    def company_name(self):
        """Backward compatibility for company_name field"""
        return self.company
    
    @company_name.setter
    def company_name(self, value):
        """Backward compatibility setter for company_name field"""
        self.company = value

class UserProfile(Base):
    """
    Extended profile information for users based on their role.
    """
    __tablename__ = "user_profiles"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id"), index=True)  # Foreign key to users_v2.id
    
    # Role-specific data (stored as JSON-like text)
    profile_data = Column(Text)  # JSON string with role-specific fields
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Conversation(Base):
    """
    SQLAlchemy model for conversations between users and AI.
    """
    __tablename__ = "conversations"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users_v2.id"), index=True)
    title = Column(String(255))
    status = Column(String(20), default="active")  # active, archived, deleted
    
    # Conversation metadata
    total_messages = Column(Integer, default=0)
    ai_provider = Column(String(50))  # openai, anthropic, gemini
    model_name = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("User", back_populates="conversations")
    # messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    """
    SQLAlchemy model for individual messages within conversations.
    """
    __tablename__ = "conversation_messages"
    __table_args__ = {"extend_existing": True}
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    
    # Message content
    role = Column(String(20))  # user, assistant, system
    content = Column(Text)
    tokens_used = Column(Integer, default=0)
    
    # Message metadata
    ai_provider = Column(String(50))
    model_name = Column(String(100))
    response_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # conversation = relationship("Conversation", back_populates="messages")