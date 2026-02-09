"""Pydantic schemas for onboarding flows."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class OnboardingSessionOut(BaseModel):
    id: str
    status: str
    onboarding_completed: bool
    last_step_key: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OnboardingStepStateOut(BaseModel):
    status: str
    completed_at: Optional[datetime] = None
    skipped_at: Optional[datetime] = None


class OnboardingStepOut(BaseModel):
    step_key: str
    title: str
    order_index: int
    required: bool
    role_scope_json: Optional[dict[str, Any]] = None
    state: Optional[OnboardingStepStateOut] = None


class OnboardingStatusResponse(BaseModel):
    session: Optional[OnboardingSessionOut] = None
    steps: list[OnboardingStepOut] = Field(default_factory=list)
    progress: int = 0


class OnboardingStartResponse(OnboardingStatusResponse):
    pass


class OnboardingProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    company_name: Optional[str] = Field(default=None, max_length=100)
    role: Optional[str] = Field(default=None, max_length=32)
    profile: Optional[dict[str, Any]] = None


class OnboardingProfileResponse(BaseModel):
    profile: dict[str, Any]


class OnboardingStepActionResponse(BaseModel):
    step: OnboardingStepOut
    progress: int


class OnboardingNextStepResponse(BaseModel):
    step: Optional[OnboardingStepOut] = None
    progress: int


class OnboardingProgressResponse(BaseModel):
    progress: int


class OnboardingStepCompleteRequest(BaseModel):
    step_key: str = Field(..., min_length=1)


class OnboardingStepBlockedRequest(BaseModel):
    step_key: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=1000)


class OnboardingStepBlockedResponse(BaseModel):
    step: OnboardingStepOut
    progress: int


class TrustAckResponse(BaseModel):
    key: str
    acknowledged_at: datetime


class TrustAckPayload(BaseModel):
    metadata: Optional[dict[str, Any]] = None


class OnboardingCompleteResponse(BaseModel):
    session: OnboardingSessionOut
    progress: int
