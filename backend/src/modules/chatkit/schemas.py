"""Pydantic schemas for ChatKit routes."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatTokenRequest(BaseModel):
    """Request payload for issuing a ChatKit session token."""

    placement: str = Field(..., min_length=2, max_length=64, examples=["support"])
    thread_id: Optional[str] = Field(default=None, description="Existing thread identifier")


class ChatTokenResponse(BaseModel):
    """Response payload returned to the frontend ChatKit client."""

    token: str
    expires_at: datetime
    thread_id: str
    placement: str
    allowed_tools: list[str] = Field(default_factory=list)


class ToolInvokeRequest(BaseModel):
    """Invoke a backend tool for a given placement/thread."""

    placement: str = Field(..., min_length=2, max_length=64)
    thread_id: Optional[str] = Field(default=None)
    payload: dict = Field(default_factory=dict)


class ToolInvokeResponse(BaseModel):
    """Result of a tool invocation including audit event reference."""

    thread_id: str
    tool_name: str
    result: dict
    event_id: str
    allowed_tools: list[str] = Field(default_factory=list)
