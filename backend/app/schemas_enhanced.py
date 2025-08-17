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

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

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
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    experience: Optional[str] = None
    
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
    profile_completed: Optional[bool] = Field(True, alias="profileCompleted")
    phase2_completed: Optional[bool] = Field(True, alias="phase2Completed")
    
    # Customer-specific fields
    company_name: Optional[str] = Field(None, alias="companyName")
    industry: Optional[str] = None
    company_size: Optional[str] = Field(None, alias="companySize")
    business_type: Optional[str] = Field(None, alias="businessType")
    use_case: Optional[str] = Field(None, alias="useCase")
    budget: Optional[str] = None
    goals: Optional[List[str]] = None
    preferred_integrations: Optional[List[str]] = Field(None, alias="preferredIntegrations")
    timeline: Optional[str] = None
    
    # Developer-specific fields
    experience_level: Optional[str] = Field(None, alias="experienceLevel")
    primary_languages: Optional[List[str]] = Field(None, alias="primaryLanguages")
    specializations: Optional[List[str]] = None
    github_profile: Optional[str] = Field(None, alias="githubProfile")
    portfolio_url: Optional[str] = Field(None, alias="portfolioUrl")
    social_links: Optional[dict] = Field(None, alias="socialLinks")
    previous_projects: Optional[str] = Field(None, alias="previousProjects")
    availability: Optional[str] = None
    hourly_rate: Optional[str] = Field(None, alias="hourlyRate")
    earnings_target: Optional[str] = Field(None, alias="earningsTarget")
    revenue_share: Optional[float] = Field(None, alias="revenueShare")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user data response (excludes sensitive data)"""
    id: int
    email: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    experience: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    # Phase 2 profile completion status
    profile_completed: Optional[bool] = None
    phase2_completed: Optional[bool] = None
    
    # Customer-specific fields (only returned if user is customer)
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    business_type: Optional[str] = None
    use_case: Optional[str] = None
    budget: Optional[str] = None
    goals: Optional[List[str]] = None
    preferred_integrations: Optional[List[str]] = None
    timeline: Optional[str] = None
    
    # Developer-specific fields (only returned if user is developer)
    experience_level: Optional[str] = None
    primary_languages: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    github_profile: Optional[str] = None
    portfolio_url: Optional[str] = None
    social_links: Optional[dict] = None
    previous_projects: Optional[str] = None
    availability: Optional[str] = None
    hourly_rate: Optional[str] = None
    earnings_target: Optional[str] = None
    revenue_share: Optional[float] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    experience: Optional[str] = None

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
    refresh_token: Optional[str] = None
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
    agent_name: Optional[str] = None
    revenue_share: Decimal
    total_sales: Decimal
    commission_rate: Decimal
    last_payout_amount: Decimal
    last_payout_at: Optional[datetime] = None
    total_paid_out: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DeveloperEarningsCreate(BaseModel):
    """Schema for creating developer earnings record"""
    agent_id: str
    agent_name: str
    commission_rate: Optional[Decimal] = Decimal('0.3000')
    currency: Optional[str] = "USD"

class DeveloperEarningsUpdate(BaseModel):
    """Schema for updating developer earnings"""
    agent_name: Optional[str] = None
    commission_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None

class DeveloperEarningsSummary(BaseModel):
    """Schema for developer earnings summary"""
    total_agents: int
    total_revenue_share: Decimal
    total_sales: Decimal
    total_paid_out: Decimal
    pending_payout: Decimal
    currency: str
    earnings: List[DeveloperEarningResponse]

# ================================
# Audit Log Schemas
# ================================

class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: Optional[int] = None
    event_type: str
    event_description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
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
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

# ================================
# Validation Schemas
# ================================

class EmailValidation(BaseModel):
    """Schema for email validation"""
    email: EmailStr

class TokenValidation(BaseModel):
    """Schema for token validation"""
    token: str
    token_type: Optional[TokenType] = TokenType.ACCESS

# ================================
# Admin Schemas
# ================================

class UserAdminResponse(UserResponse):
    """Extended user response for admin endpoints"""
    email_verified_at: Optional[datetime] = None
    terms_accepted_at: Optional[datetime] = None
    privacy_accepted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserAdminUpdate(BaseModel):
    """Schema for admin user updates"""
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None
    
class BulkUserOperation(BaseModel):
    """Schema for bulk user operations"""
    user_ids: List[int]
    operation: str  # 'activate', 'deactivate', 'verify', 'delete'
