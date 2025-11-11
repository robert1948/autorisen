"""
Pydantic schemas for the CapeAI Domain Specialist agent.

Closely mirrors the CapeAI Guide schemas but introduces a required domain field
so that downstream services can tailor prompts, resources, and KPIs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

DomainLiteral = Literal[
    "workflow_automation", "data_analytics", "security_audit", "integration_helper"
]


class DomainSpecialistTaskInput(BaseModel):
    """Input schema for domain-specialized assistance."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=1200,
        description="User prompt describing the goal or issue.",
    )
    domain: DomainLiteral = Field(
        ...,
        description="Domain focus for the assistant. "
        "Options: workflow_automation, data_analytics, security_audit, integration_helper.",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional execution context such as environment, stage, or owner.",
    )
    objectives: List[str] = Field(
        default_factory=list,
        description="Key objectives or KPIs the user wants to achieve.",
    )
    preferred_format: Optional[str] = Field(
        default="summary",
        description="Optional formatting preference (summary, checklist, playbook, metrics).",
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "Design a rollback-aware workflow for provisioning environments.",
                "domain": "workflow_automation",
                "context": {
                    "stage": "staging",
                    "owner": "platform-team",
                    "tools": ["capecontrol", "pagerduty"],
                },
                "objectives": ["zero-downtime", "auditable"],
                "preferred_format": "playbook",
            }
        }


class ResourceLink(BaseModel):
    """Hyperlink metadata returned by the agent."""

    title: str = Field(..., description="Display name for the resource.")
    url: str = Field(..., description="URL to internal or external documentation.")
    type: Optional[str] = Field(
        default=None, description="Resource classification (doc, playbook, tutorial)."
    )


class DomainInsight(BaseModel):
    """Structured insight describing a risk, metric, or opportunity."""

    label: str = Field(..., description="Short label for the insight.")
    detail: str = Field(..., description="Human-readable explanation.")
    severity: Optional[str] = Field(
        default=None, description="Optional severity (low, medium, high)."
    )


class DomainSpecialistTaskOutput(BaseModel):
    """Output schema for the domain specialist agent."""

    response: str = Field(..., description="LLM-generated narrative guidance.")
    playbook_steps: List[str] = Field(
        default_factory=list,
        description="Ordered steps or recommendations tailored to the domain.",
    )
    insights: List[DomainInsight] = Field(
        default_factory=list,
        description="Structured insights or risk flags derived from the query.",
    )
    resources: List[ResourceLink] = Field(
        default_factory=list, description="Supplemental documentation links."
    )
    domain_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for the provided guidance.",
    )
    processing_time_ms: Optional[int] = Field(
        default=None, description="Processing time for the task in milliseconds."
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "For workflow automation, start by validating the trigger...",
                "playbook_steps": [
                    "Document trigger inputs and fallback paths",
                    "Simulate critical branches with synthetic payloads",
                    "Enable observability dashboards with alert thresholds",
                ],
                "insights": [
                    {
                        "label": "Rollback coverage",
                        "detail": "Define rollback hooks before enabling production triggers.",
                        "severity": "medium",
                    }
                ],
                "resources": [
                    {
                        "title": "Webhook Orchestration Guide",
                        "url": "/docs/integrations/webhooks",
                        "type": "doc",
                    }
                ],
                "domain_score": 0.89,
                "processing_time_ms": 980,
            }
        }
