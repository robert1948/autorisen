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
    currency: Optional[str] = "ZAR"
    updated_at: Optional[datetime] = None


class PersonalInfoUpdate(BaseModel):
    """Personal info update payload."""

    phone: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    currency: Optional[str] = None


class ProjectCreate(BaseModel):
    """Create a new project."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update a project."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(pending|in-progress|completed|cancelled)$")


class ProjectDetail(BaseModel):
    """Full project detail response."""

    id: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ProjectStatusItem(BaseModel):
    """Project status item."""

    id: str
    title: str
    status: str
    created_at: datetime


class ProjectStatusSummary(BaseModel):
    """Project status summary for dashboard module."""

    value: str
    total: int
    projects: list[ProjectStatusItem]


class AccountBalance(BaseModel):
    """Account balance summary."""

    total_paid: float
    total_pending: float
    currency: str = "ZAR"


class DeleteAccountResponse(BaseModel):
    """Account deletion response."""

    status: str
    message: str
