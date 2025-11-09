"""User profile and onboarding Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserProfileBase(BaseModel):
    """Base user profile fields."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    company: Optional[str] = Field(None, max_length=100)
    role: str = Field(..., max_length=32)
    experience_level: Optional[str] = Field(None, max_length=32)


class UserProfileUpdate(UserProfileBase):
    """User profile update request."""

    interests: Optional[list[str]] = Field(default_factory=list)
    notifications_email: bool = Field(default=True)
    notifications_push: bool = Field(default=True)
    notifications_sms: bool = Field(default=False)


class UserProfileResponse(UserProfileBase):
    """User profile response."""

    id: str
    email: str
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    interests: list[str] = Field(default_factory=list)
    notifications_email: bool = Field(default=True)
    notifications_push: bool = Field(default=True)
    notifications_sms: bool = Field(default=False)

    class Config:
        from_attributes = True


class OnboardingChecklistItem(BaseModel):
    """Individual onboarding checklist item."""

    id: str
    title: str
    description: str
    completed: bool
    required: bool
    order: int


class OnboardingChecklistResponse(BaseModel):
    """Onboarding checklist response."""

    items: list[OnboardingChecklistItem]
    completion_percentage: int
    required_completed: int
    required_total: int
    optional_completed: int
    optional_total: int


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response."""

    active_agents: int
    tasks_complete: int
    system_status: str
    agents_deployed: int
    total_runs: int
    success_rate: float


class ActivityItem(BaseModel):
    """Recent activity item."""

    id: str
    type: str  # "agent_deploy", "task_complete", "login", etc.
    title: str
    description: str
    timestamp: datetime
    status: str = "success"  # "success", "error", "pending"
    metadata: Optional[dict] = Field(default_factory=dict)
