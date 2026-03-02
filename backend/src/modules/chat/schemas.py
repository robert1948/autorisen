"""Pydantic schemas for the Chat module."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Thread schemas ────────────────────────────────────────────────────────────

class ThreadCreate(BaseModel):
    placement: str = Field(..., min_length=1, max_length=64)
    title: Optional[str] = Field(default=None, max_length=200)
    context: Optional[dict[str, Any]] = None


class ThreadResponse(BaseModel):
    id: str
    placement: str
    title: Optional[str] = None
    status: Optional[str] = "active"
    context: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_event_at: Optional[datetime] = None
    metadata: Optional[dict[str, Any]] = None


class ThreadListResponse(BaseModel):
    results: list[ThreadResponse]


# ── Event / message schemas ───────────────────────────────────────────────────

class EventCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=16000)
    role: str = Field(default="user", pattern=r"^(user|system)$")
    tool_name: Optional[str] = None
    event_metadata: Optional[dict[str, Any]] = None


class EventResponse(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    tool_name: Optional[str] = None
    event_metadata: Optional[dict[str, Any]] = None
    created_at: datetime


class EventListResponse(BaseModel):
    results: list[EventResponse]
