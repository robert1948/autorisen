"""
Enhanced Database Models for Secure, Scalable Authentication
==========================================================

This file implements the proposed secure authentication architecture with:
- Enhanced Users table with proper roles and indexing
- Tokens table for JWT and session management
- Developer earnings table for revenue tracking
- Proper relationships and constraints
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.database import Base

# Define role enum for type safety
class UserRole(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    DEVELOPER = "DEVELOPER" 
    ADMIN = "ADMIN"

class UserV2(Base):
    """
    Enhanced Users table with secure architecture
    - Proper role enum with customer/developer/admin
    - Indexed email for fast lookups
    - Enhanced security fields
    - Audit timestamps
    """
    __tablename__ = "users_v2"
    __table_args__ = {"extend_existing": True}

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Role-based access control
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    website = Column(String(255))
    company = Column(String(255))
    
    # Account status and verification
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime(timezone=True))
    
    # Experience level (for both customers and developers)
    experience = Column(String(20))  # 'beginner', 'intermediate', 'advanced', 'expert'
    
    # Phase 2 Profile Completion Status - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # profile_completed = Column(Boolean, default=False, nullable=False)
    # phase2_completed = Column(Boolean, default=False, nullable=False)
    
    # Customer-specific Phase 2 fields
    company_name = Column(String(255))
    industry = Column(String(100))
    company_size = Column(String(50))
    business_type = Column(String(50))
    use_case = Column(String(100))
    budget = Column(String(50))
    goals = Column(JSON)  # Array of customer goals
    preferred_integrations = Column(JSON)  # Array of preferred integrations
    timeline = Column(String(50))
    
    # Developer-specific Phase 2 fields
    experience_level = Column(String(50))  # Developer-specific experience level
    primary_languages = Column(JSON)  # Array of programming languages
    specializations = Column(JSON)  # Array of developer specializations
    github_profile = Column(String(255))
    portfolio_url = Column(String(255))
    social_links = Column(JSON)  # Object with social media links
    previous_projects = Column(Text)  # Description of previous projects
    availability = Column(String(50))
    hourly_rate = Column(String(50))
    earnings_target = Column(String(50))
    # revenue_share = Column(Numeric(5, 4), default=0.3000)  # TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    # Terms and privacy
    terms_accepted_at = Column(DateTime(timezone=True))
    # privacy_accepted_at = Column(DateTime(timezone=True))  # TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    # developer_earnings = relationship("DeveloperEarning", back_populates="user", cascade="all, delete-orphan")

class Token(Base):
    """
    Tokens table for JWT and session management
    - Supports both access tokens and refresh tokens
    - Automatic expiration handling
    - User relationship for easy cleanup
    """
    __tablename__ = "tokens_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token details
    token = Column(String(500), nullable=False, index=True)  # JWT or session token
    token_type = Column(String(20), nullable=False, default="access")  # 'access', 'refresh', 'reset'
    
    # Expiration and status
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True))  # When token was last used
    
    # Device/session tracking
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("UserV2", back_populates="tokens")

class DeveloperEarning(Base):
    """
    Developer earnings table for revenue tracking
    - Links developers to their AI agents
    - Tracks revenue share and payments
    - Supports analytics and reporting
    """
    __tablename__ = "developer_earnings_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # AI Agent identification
    agent_id = Column(String(100), nullable=False, index=True)  # Identifier for the AI agent
    agent_name = Column(String(255))  # Human-readable agent name
    
    # Revenue details
    revenue_share = Column(Numeric(10, 2), nullable=False, default=0.00)  # Amount owed
    total_sales = Column(Numeric(10, 2), default=0.00)  # Total sales for this agent
    commission_rate = Column(Numeric(5, 4), default=0.3000)  # Commission percentage (30% default)
    
    # Payment tracking
    last_payout_amount = Column(Numeric(10, 2), default=0.00)
    last_payout_at = Column(DateTime(timezone=True))
    total_paid_out = Column(Numeric(10, 2), default=0.00)
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - TEMPORARILY COMMENTED OUT FOR REGISTRATION FIX
    # user = relationship("UserV2", back_populates="developer_earnings")

class PasswordReset(Base):
    """
    Password reset tokens table
    - Secure password reset workflow
    - Time-limited tokens
    - Single-use tokens
    """
    __tablename__ = "password_resets_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Reset token details
    token = Column(String(255), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    
    # Security tracking
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    used_at = Column(DateTime(timezone=True))

class AuditLog(Base):
    """
    Audit log for security and compliance
    - Track important user actions
    - Security event monitoring
    - Compliance reporting
    """
    __tablename__ = "audit_logs_v2"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_v2.id", ondelete="SET NULL"), index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # 'login', 'register', 'password_change', etc.
    event_description = Column(Text)
    
    # Request details
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    endpoint = Column(String(255))
    
    # Status and metadata
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    event_metadata = Column(Text)  # JSON string for additional data
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
