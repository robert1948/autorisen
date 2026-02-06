"""Schemas for account, profile, projects, and billing endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AccountDetails(BaseModel):
    """Account details response."""

    id: str
    email: str
    display_name: str
    status: str
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    company_name: Optional[str] = None


class AccountUpdate(BaseModel):
    """Account details update payload."""

    display_name: Optional[str] = Field(default=None, max_length=100)
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=100)


class PersonalInfo(BaseModel):
    """Personal info response."""

    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    updated_at: Optional[datetime] = None


class PersonalInfoUpdate(BaseModel):
    """Personal info update payload."""

    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ProjectStatusItem(BaseModel):
    """Project status item."""

    id: str
    title: str
    status: str
    created_at: datetime


class AccountBalance(BaseModel):
    """Account balance summary."""

    total_paid: float
    total_pending: float
    currency: str = "ZAR"


class DeleteAccountResponse(BaseModel):
    """Account deletion response."""

    status: str
    message: str
