import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ----------------------------
# Schema: Enhanced User Registration (V2)
# ----------------------------
class UserCreateV2(BaseModel):
    """
    Schema for creating a new user with enhanced validation (2-step flow).
    """
    # Basic information
    email: EmailStr
    password: str
    firstName: str
    lastName: str

    # Role and company information
    role: str  # 'customer' or 'developer'
    company: str | None = None
    phone: str | None = None
    website: str | None = None
    experience: str | None = None

    # Pydantic v2 config
    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Enhanced password validation for V2 registration"""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator("firstName", "lastName")
    @classmethod
    def validate_names(cls, v: str) -> str:
        """Validate and sanitize names"""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        cleaned = v.strip()
        if len(cleaned) > 50:
            raise ValueError("Name must be 50 characters or less")
        return cleaned

    @field_validator("company")
    @classmethod
    def validate_company(cls, v: str | None) -> str | None:
        """Validate and sanitize company name"""
        if v:
            cleaned = v.strip()
            if len(cleaned) > 100:
                raise ValueError("Company name must be 100 characters or less")
            return cleaned
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role selection"""
        if v not in ["customer", "developer"]:
            raise ValueError('Role must be either "customer" or "developer"')
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        """Validate website URL format"""
        if v and v.strip():
            url = v.strip()
            if not re.match(r"^https?://", url):
                url = f"https://{url}"
            # Basic URL validation
            if not re.match(r"^https?://[^\s/$.?#].[^\s]*$", url):
                raise ValueError("Please enter a valid website URL")
            return url
        return v

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v: str | None) -> str | None:
        """Validate experience level"""
        if v and v not in ["beginner", "intermediate", "advanced", "expert"]:
            raise ValueError(
                "Experience must be one of: beginner, intermediate, advanced, expert"
            )
        return v


# ----------------------------
# Schema: User Registration (Original - for compatibility)
# ----------------------------
class UserCreate(BaseModel):
    """
    Schema for creating a new user with enhanced registration data.
    """
    # Basic information
    email: EmailStr
    password: str
    firstName: str
    lastName: str

    # Role and company information
    role: str  # 'user' or 'developer'
    company: str | None = None
    phone: str | None = None
    website: str | None = None
    experience: str | None = None

    model_config = {"from_attributes": True}


# ----------------------------
# Schema: Basic User Registration (Step 1)
# ----------------------------
class BasicUserCreate(BaseModel):
    """
    Schema for the first step of registration.
    """
    email: EmailStr
    password: str
    firstName: str
    lastName: str


# ----------------------------
# Schema: User Login (JSON input)
# ----------------------------
class LoginInput(BaseModel):
    """
    Schema for user login via JSON.
    """
    email: EmailStr
    password: str


# ----------------------------
# Schema: Public User Info (safe output)
# ----------------------------
class UserOut(BaseModel):
    """
    Schema for returning user information (excluding sensitive data).
    Updated for production database compatibility - July 13, 2025
    """
    id: str  # UUID string in production database
    email: EmailStr
    full_name: str | None = None
    user_role: str | None = None
    company_name: str | None = None
    access_token: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


# ----------------------------
# Schema: Minimal Registration for Debugging
# ----------------------------
class UserCreateMinimal(BaseModel):
    """
    Minimal schema for debugging registration issues without complex validation.
    """
    email: str
    password: str
    full_name: str

    model_config = {"from_attributes": True}


# ----------------------------
# Schema: Production Database Compatible Registration
# ----------------------------
class UserCreateV2Production(BaseModel):
    """
    Schema for creating a new user that matches production database schema.
    Updated for production compatibility - July 13, 2025
    """
    # Basic information - matches production columns
    email: EmailStr
    password: str
    full_name: str  # Single field instead of firstName/lastName

    # Role and company information - matches production columns
    user_role: str | None = "client"  # Default to 'client' if not provided
    company_name: str | None = None

    # Production database additional fields
    industry: str | None = None
    project_budget: str | None = None
    skills: str | None = None
    portfolio: str | None = None
    github: str | None = None

    # Terms acceptance - allow missing for API compatibility
    tos_accepted: bool | None = True

    model_config = {"from_attributes": True, "populate_by_name": True}

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Enhanced password validation for V2 registration (prod rules)"""
        if len(v) < 8:  # Reduced from 12 for production compatibility
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate and sanitize full name"""
        if not v or not v.strip():
            raise ValueError("Full name cannot be empty")
        cleaned = v.strip()
        if len(cleaned) > 100:  # Match database column length
            raise ValueError("Full name must be 100 characters or less")
        return cleaned

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str | None) -> str | None:
        """Validate and sanitize company name"""
        if v:
            cleaned = v.strip()
            if len(cleaned) > 255:  # Reasonable limit
                raise ValueError("Company name must be 255 characters or less")
            return cleaned
        return v

    @field_validator("user_role")
    @classmethod
    def validate_user_role(cls, v: str | None) -> str:
        """Validate role selection"""
        if v and v not in ["client", "developer"]:
            raise ValueError('Role must be either "client" or "developer"')
        return v or "client"  # Default to 'client' if None

    @field_validator("tos_accepted")
    @classmethod
    def validate_tos_accepted(cls, v: bool | None) -> bool:
        """Ensure terms of service are accepted"""
        if v is None:
            return True
        if not v:
            raise ValueError("Terms of service must be accepted")
        return v


# ----------------------------
# Schema: 2-Step Registration Requests
# ----------------------------
class RegisterStep1Request(BaseModel):
    """Step 1: Email validation request"""
    email: EmailStr


class RegisterStep2Request(BaseModel):
    """Step 2: Complete registration request"""
    email: EmailStr
    password: str
    full_name: str
    user_role: str | None = "client"  # Fixed: match database constraint
    company_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Password validation for step 2"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("user_role")
    @classmethod
    def validate_user_role(cls, v: str | None) -> str:
        """Validate role selection to match database constraint"""
        if v not in ["client", "developer"]:
            raise ValueError('Role must be either "client" or "developer"')
        return v
