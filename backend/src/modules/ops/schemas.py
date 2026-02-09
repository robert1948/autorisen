"""Schemas for ops insights."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OpsInsightIntent(str, Enum):
    project_status = "project_status"
    top_blockers = "top_blockers"
    onboarding_completion_rate = "onboarding_completion_rate"
    agent_usage_last_7d = "agent_usage_last_7d"
    open_support_tickets = "open_support_tickets"


class OpsInsightResponse(BaseModel):
    title: str
    summary: str
    key_metrics: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
