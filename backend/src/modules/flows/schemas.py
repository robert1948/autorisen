"""Schemas for orchestrator flow runs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.src.schemas.base import SchemaBase


class ToolCall(BaseModel):
    """Single tool invocation requested by the client."""

    name: str = Field(..., min_length=2, max_length=80)
    payload: Dict[str, Any] = Field(default_factory=dict)


class FlowRunRequest(BaseModel):
    """Request body for launching a flow run."""

    placement: Optional[str] = Field(default=None, min_length=2, max_length=64)
    agent_slug: Optional[str] = Field(default=None, min_length=3, max_length=100)
    agent_version: Optional[str] = Field(default=None, min_length=1, max_length=20)
    thread_id: Optional[str] = Field(default=None)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    idempotency_key: Optional[str] = Field(default=None, max_length=128)
    max_attempts: int = Field(default=3, ge=1, le=5)


class RunStep(BaseModel):
    """Trace entry from orchestrator execution."""

    tool: str
    payload: Dict[str, Any]
    result: Dict[str, Any]
    event_id: str


class FlowRunResponse(BaseModel):
    """Aggregated response payload."""

    run_id: str
    thread_id: str
    placement: str
    steps: List[RunStep] = Field(default_factory=list)
    agent_id: Optional[str] = None
    agent_version_id: Optional[str] = None
    status: str
    attempt: int
    max_attempts: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FlowRunRecord(SchemaBase):
    id: str
    placement: str
    thread_id: str
    agent_id: Optional[str]
    agent_version_id: Optional[str]
    steps: List[Dict[str, Any]]
    created_at: datetime
    status: str
    attempt: int
    max_attempts: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

class ChecklistUpdateRequest(BaseModel):
    task_id: str = Field(..., min_length=2, max_length=100)
    label: Optional[str] = Field(default=None, max_length=160)
    done: bool = Field(default=True)
    thread_id: Optional[str] = Field(default=None, max_length=64)
