"""
Enhanced Pydantic Schemas for Secure Authentication
=================================================

This file implements schemas for the proposed secure authentication architecture:
- Role-based user creation and responses
- JWT token management
- Developer earnings tracking
- Password reset workflows
- Audit logging
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, validator


# Role enum for validation
class UserRole(str, Enum):
    CUSTOMER = "CUSTOMER"
    DEVELOPER = "DEVELOPER"
    ADMIN = "ADMIN"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"

# ================================
# User Schemas
# ================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    role: UserRole
    company: str | None = None
    phone: str | None = None
    website: str | None = None
    experience: str | None = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('role', pre=True)
    def normalize_role(cls, v):
        """Accept both uppercase and lowercase role values"""
        if isinstance(v, str):
            v = v.upper()
            # Map to valid enum values
            role_mapping = {
                'CUSTOMER': UserRole.CUSTOMER,
                'DEVELOPER': UserRole.DEVELOPER,
                'ADMIN': UserRole.ADMIN
            }
            return role_mapping.get(v, v)
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [UserRole.CUSTOMER, UserRole.DEVELOPER]:
            raise ValueError('Role must be customer or developer for registration')
        return v

class Phase2ProfileComplete(BaseModel):
    """Schema for completing Phase 2 profile"""
    # Common fields
    profile_completed: bool | None = Field(True, alias="profileCompleted")
    phase2_completed: bool | None = Field(True, alias="phase2Completed")
    
    # Customer-specific fields
    company_name: str | None = Field(None, alias="companyName")
    industry: str | None = None
    company_size: str | None = Field(None, alias="companySize")
    business_type: str | None = Field(None, alias="businessType")
    use_case: str | None = Field(None, alias="useCase")
    budget: str | None = None
    goals: list[str] | None = None
    preferred_integrations: list[str] | None = Field(None, alias="preferredIntegrations")
    timeline: str | None = None
    
    # Developer-specific fields
    experience_level: str | None = Field(None, alias="experienceLevel")
    primary_languages: list[str] | None = Field(None, alias="primaryLanguages")
    specializations: list[str] | None = None
    github_profile: str | None = Field(None, alias="githubProfile")
    portfolio_url: str | None = Field(None, alias="portfolioUrl")
    social_links: dict | None = Field(None, alias="socialLinks")
    previous_projects: str | None = Field(None, alias="previousProjects")
    availability: str | None = None
    hourly_rate: str | None = Field(None, alias="hourlyRate")
    earnings_target: str | None = Field(None, alias="earningsTarget")
    revenue_share: float | None = Field(None, alias="revenueShare")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user data response (excludes sensitive data)"""
    id: int
    email: str
    role: UserRole
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    phone: str | None = None
    website: str | None = None
    experience: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime | None = None
    
    # Phase 2 profile completion status
    profile_completed: bool | None = None
    phase2_completed: bool | None = None
    
    # Customer-specific fields (only returned if user is customer)
    company_name: str | None = None
    industry: str | None = None
    company_size: str | None = None
    business_type: str | None = None
    use_case: str | None = None
    budget: str | None = None
    goals: list[str] | None = None
    preferred_integrations: list[str] | None = None
    timeline: str | None = None
    
    # Developer-specific fields (only returned if user is developer)
    experience_level: str | None = None
    primary_languages: list[str] | None = None
    specializations: list[str] | None = None
    github_profile: str | None = None
    portfolio_url: str | None = None
    social_links: dict | None = None
    previous_projects: str | None = None
    availability: str | None = None
    hourly_rate: str | None = None
    earnings_target: str | None = None
    revenue_share: float | None = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    phone: str | None = None
    website: str | None = None
    experience: str | None = None

class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

# ================================
# Authentication Schemas
# ================================

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse

class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str

class TokenRevoke(BaseModel):
    """Schema for token revocation"""
    token: str
    token_type: TokenType = TokenType.ACCESS

# ================================
# Password Reset Schemas
# ================================

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v

class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    message: str
    email_sent: bool

# ================================
# Developer Earnings Schemas
# ================================

class DeveloperEarningResponse(BaseModel):
    """Schema for developer earnings response"""
    id: int
    agent_id: str
    agent_name: str | None = None
    revenue_share: Decimal
    total_sales: Decimal
    commission_rate: Decimal
    last_payout_amount: Decimal
    last_payout_at: datetime | None = None
    total_paid_out: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

class DeveloperEarningsCreate(BaseModel):
    """Schema for creating developer earnings record"""
    agent_id: str
    agent_name: str
    commission_rate: Decimal | None = Decimal('0.3000')
    currency: str | None = "USD"

class DeveloperEarningsUpdate(BaseModel):
    """Schema for updating developer earnings"""
    agent_name: str | None = None
    commission_rate: Decimal | None = None
    is_active: bool | None = None

class DeveloperEarningsSummary(BaseModel):
    """Schema for developer earnings summary"""
    total_agents: int
    total_revenue_share: Decimal
    total_sales: Decimal
    total_paid_out: Decimal
    pending_payout: Decimal
    currency: str
    earnings: list[DeveloperEarningResponse]

# ================================
# Audit Log Schemas
# ================================

class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: int | None = None
    event_type: str
    event_description: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    endpoint: str | None = None
    success: bool
    error_message: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ================================
# API Response Schemas
# ================================

class ApiResponse(BaseModel):
    """Generic API response schema"""
    success: bool
    message: str
    data: dict | None = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    detail: str | None = None
    code: str | None = None

# ================================
# Validation Schemas
# ================================

class EmailValidation(BaseModel):
    """Schema for email validation"""
    email: EmailStr

class TokenValidation(BaseModel):
    """Schema for token validation"""
    token: str
    token_type: TokenType | None = TokenType.ACCESS

# ================================
# Admin Schemas
# ================================

class UserAdminResponse(UserResponse):
    """Extended user response for admin endpoints"""
    email_verified_at: datetime | None = None
    terms_accepted_at: datetime | None = None
    privacy_accepted_at: datetime | None = None
    updated_at: datetime | None = None

class UserAdminUpdate(BaseModel):
    """Schema for admin user updates"""
    is_active: bool | None = None
    is_verified: bool | None = None
    role: UserRole | None = None
    
class BulkUserOperation(BaseModel):
    """Schema for bulk user operations"""
    user_ids: list[int]
    operation: str  # 'activate', 'deactivate', 'verify', 'delete'
