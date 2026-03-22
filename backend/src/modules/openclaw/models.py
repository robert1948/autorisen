"""Pydantic models for OpenClaw task and approval APIs."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

TaskMode = Literal["assisted", "autonomous"]
TaskStatus = Literal["queued", "requires_approval", "completed", "failed", "rejected"]


class OpenClawInput(BaseModel):
    text: str = Field(..., description="Primary user instruction")
    channel: Optional[str] = Field(None, description="Source channel, e.g. slack")


class OpenClawTaskCreateRequest(BaseModel):
    workflow: str = Field(..., description="Workflow identifier")
    input: OpenClawInput
    context_refs: list[str] = Field(default_factory=list)
    mode: TaskMode = "assisted"
    idempotency_key: Optional[str] = None


class OpenClawTaskCreateResponse(BaseModel):
    task_id: str
    status: TaskStatus
    requires_approval: bool
    trace_id: str


class OpenClawCitation(BaseModel):
    source_id: str
    excerpt: str
    timestamp: datetime


class OpenClawEvidence(BaseModel):
    citations: list[OpenClawCitation] = Field(default_factory=list)


class OpenClawCost(BaseModel):
    input_tokens: int
    output_tokens: int
    estimated_usd: float


class OpenClawTaskOutput(BaseModel):
    summary: str
    actions: list[str] = Field(default_factory=list)


class OpenClawTaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    output: Optional[OpenClawTaskOutput] = None
    evidence: Optional[OpenClawEvidence] = None
    trace_id: str
    cost: Optional[OpenClawCost] = None
    requires_approval: bool = False
    approval_id: Optional[str] = None
    policy_reason: Optional[str] = None


class OpenClawApprovalDecisionRequest(BaseModel):
    comment: Optional[str] = None
    ttl_minutes: int = Field(30, ge=1, le=240)


class OpenClawApprovalDecisionResponse(BaseModel):
    approval_id: str
    status: Literal["approved", "rejected"]
    actor: str
    timestamp: datetime
    comment: Optional[str] = None


OpenClawEventType = Literal[
    "openclaw.task.created",
    "openclaw.policy.evaluated",
    "openclaw.model.invoked",
    "openclaw.approval.requested",
    "openclaw.approval.decided",
    "openclaw.tool.executed",
    "openclaw.task.completed",
    "openclaw.task.failed",
]


class OpenClawModelMetadata(BaseModel):
    provider: str
    model_id: str
    region: str


class OpenClawEventMetrics(BaseModel):
    latency_ms: int
    input_tokens: int
    output_tokens: int
    estimated_usd: float


class OpenClawEventPolicy(BaseModel):
    result: Literal["allow", "require_approval", "deny"]
    rules_triggered: list[str] = Field(default_factory=list)


class OpenClawEvent(BaseModel):
    event_type: OpenClawEventType
    timestamp: datetime
    trace_id: str
    task_id: str
    actor_id: str
    workflow: str
    model: OpenClawModelMetadata
    metrics: OpenClawEventMetrics
    policy: OpenClawEventPolicy
    metadata: dict[str, str] = Field(default_factory=dict)


class OpenClawStatsResponse(BaseModel):
    window_days: int
    since: datetime
    total_events: int
    event_breakdown: dict[str, int] = Field(default_factory=dict)
    approval_requested: int
    approval_approved: int
    approval_rejected: int
    task_completed: int
    task_failed: int
    total_tokens_in: int
    total_tokens_out: int
    total_cost_usd: float


class OpenClawRetentionResponse(BaseModel):
    retention_days: int
    cutoff: datetime
    dry_run: bool
    audit_events_affected: int
    usage_logs_affected: int


class OpenClawDailyRollup(BaseModel):
    rollup_date: str
    total_events: int
    task_completed: int
    task_failed: int
    approval_requested: int
    approval_approved: int
    approval_rejected: int
    total_tokens_in: int
    total_tokens_out: int
    total_cost_usd: float


class OpenClawAggregationResponse(BaseModel):
    days_back: int
    dry_run: bool
    generated_at: datetime
    rollups: list[OpenClawDailyRollup] = Field(default_factory=list)
