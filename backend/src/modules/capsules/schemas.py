"""Capsule module — Pydantic schemas for workflow capsule definitions and runs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CapsuleCategory(str, Enum):
    """Broad classification of capsule purpose."""

    SOP_ANSWERING = "sop_answering"
    AUDIT_SUMMARY = "audit_summary"
    CLAUSE_FINDING = "clause_finding"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_REPORT = "incident_report"
    GENERAL = "general"


class CapsuleDefinition(BaseModel):
    """A workflow capsule template.

    Capsules are registered templates that encode how a specific
    domain task should be executed: what documents to search,
    what prompt to use, and how to format the output.
    """

    id: str = Field(..., description="Unique capsule identifier (slug)")
    name: str = Field(..., description="Human-readable capsule name")
    description: str = Field(..., description="What this capsule does")
    category: CapsuleCategory = Field(
        default=CapsuleCategory.GENERAL,
        description="Capsule classification",
    )
    system_prompt: str = Field(
        ..., description="System prompt template for the LLM"
    )
    doc_types: Optional[List[str]] = Field(
        default=None,
        description="Document types this capsule retrieves from (None = all)",
    )
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.25, ge=0.0, le=1.0)
    output_format: str = Field(
        default="markdown",
        description="Expected output format: markdown, json, checklist, table",
    )
    required_fields: Optional[List[str]] = Field(
        default=None,
        description="Required input fields beyond 'query'",
    )
    version: str = Field(default="1.0", description="Capsule template version")
    enabled: bool = Field(default=True)


class CapsuleRunRequest(BaseModel):
    """Input for executing a capsule."""

    capsule_id: str = Field(..., description="Which capsule to run")
    query: str = Field(..., min_length=1, max_length=4000)
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context fields (e.g., department, date range)",
    )
    unsupported_policy: str = Field(
        default="flag",
        description="What to do when no documents match: refuse, flag, allow",
    )


class CapsuleCitation(BaseModel):
    """Citation from a capsule run."""

    document_id: str
    document_title: str
    chunk_text: str
    similarity_score: float
    doc_type: str


class CapsuleRunResponse(BaseModel):
    """Output of a capsule execution."""

    capsule_id: str
    capsule_name: str
    category: str
    response: Optional[str] = None
    output_format: str
    grounded: bool
    refused: bool = False
    refusal_reason: Optional[str] = None
    citations: List[CapsuleCitation] = Field(default_factory=list)
    query: str
    actor_id: str
    actor_email: str
    timestamp: datetime
    processing_time_ms: Optional[int] = None
    capsule_version: str


class CapsuleListResponse(BaseModel):
    """List of available capsules."""

    capsules: List[CapsuleDefinition]
    total: int
