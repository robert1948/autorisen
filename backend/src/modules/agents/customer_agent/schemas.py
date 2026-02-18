"""
Customer Agent Pydantic Schemas

Defines the input/output models for the Customer Agent task execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CustomerAgentTaskInput(BaseModel):
    """Input schema for Customer Agent tasks."""

    query: str = Field(
        ...,
        description="Customer's question, goal description, or support request",
        min_length=1,
        max_length=2000,
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Current customer context (industry, existing workflows, subscription tier, etc.)",
    )
    intent: Optional[str] = Field(
        default="general",
        description="Intent category: general, goal_expression, workflow_suggestion, support, onboarding",
    )
    industry: Optional[str] = Field(
        default=None,
        description="Customer's industry: finance, energy, legal, healthcare, retail, other",
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "I want to automate my invoice processing workflow",
                "context": {
                    "subscription_tier": "pro",
                    "existing_workflows": ["email_notifications"],
                },
                "intent": "goal_expression",
                "industry": "finance",
            }
        }


class WorkflowSuggestion(BaseModel):
    """A suggested workflow based on the customer's goals."""

    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="What this workflow does")
    estimated_setup_time: str = Field(..., description="Estimated time to set up")
    complexity: str = Field(..., description="Complexity level: simple, moderate, advanced")
    agents_required: List[str] = Field(default_factory=list, description="AI agents involved")


class CustomerAgentTaskOutput(BaseModel):
    """Output schema for Customer Agent tasks."""

    response: str = Field(..., description="AI assistant response to the customer")
    workflow_suggestions: List[WorkflowSuggestion] = Field(
        default_factory=list,
        description="Recommended workflows based on the customer's goals",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Actionable next steps for the customer",
    )
    recommended_plan: Optional[str] = Field(
        None,
        description="Recommended subscription plan if upgrade needed",
    )
    confidence_score: float = Field(
        ..., description="Response confidence score (0.0-1.0)", ge=0.0, le=1.0
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Time taken to process the request in milliseconds"
    )

    class Config:
        schema_extra = {
            "example": {
                "response": "Based on your needs, I'd recommend setting up an automated invoice processing pipeline...",
                "workflow_suggestions": [
                    {
                        "name": "Invoice Processing Pipeline",
                        "description": "Automatically extract, validate, and route invoices",
                        "estimated_setup_time": "30 minutes",
                        "complexity": "moderate",
                        "agents_required": ["data-analyst", "finance-agent"],
                    }
                ],
                "next_steps": [
                    "Review the suggested workflow template",
                    "Connect your document source",
                    "Configure approval rules",
                ],
                "recommended_plan": None,
                "confidence_score": 0.88,
                "processing_time_ms": 1800,
            }
        }
