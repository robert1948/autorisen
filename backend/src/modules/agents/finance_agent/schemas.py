"""
Finance Agent Pydantic Schemas

Defines the input/output models for the Finance Agent task execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FinanceAgentTaskInput(BaseModel):
    """Input schema for Finance Agent tasks."""

    query: str = Field(
        ...,
        description="Financial question or analysis request",
        min_length=1,
        max_length=3000,
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Financial context (company data, metrics, constraints, etc.)",
    )
    analysis_type: Optional[str] = Field(
        default="general",
        description="Analysis type: general, forecasting, budgeting, compliance, risk, reporting",
    )
    currency: Optional[str] = Field(
        default="ZAR",
        description="Primary currency for analysis (ISO 4217)",
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period for analysis: monthly, quarterly, yearly",
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "Analyze our Q4 spending trends and forecast Q1 budget needs",
                "analysis_type": "forecasting",
                "currency": "ZAR",
                "time_period": "quarterly",
            }
        }


class FinancialInsight(BaseModel):
    """A financial insight or finding."""

    category: str = Field(..., description="Insight category")
    title: str = Field(..., description="Brief insight title")
    detail: str = Field(..., description="Detailed explanation")
    severity: str = Field(default="info", description="Severity: info, warning, critical")
    metric_value: Optional[str] = Field(None, description="Associated metric value")


class FinanceAgentTaskOutput(BaseModel):
    """Output schema for Finance Agent tasks."""

    response: str = Field(..., description="AI assistant response with financial analysis")
    insights: List[FinancialInsight] = Field(
        default_factory=list,
        description="Key financial insights and findings",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable financial recommendations",
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Identified risk factors",
    )
    compliance_notes: List[str] = Field(
        default_factory=list,
        description="Compliance-related observations",
    )
    next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps",
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
                "response": "Based on the Q4 spending analysis...",
                "insights": [
                    {
                        "category": "spending",
                        "title": "Operating costs increased 12%",
                        "detail": "Driven primarily by infrastructure scaling",
                        "severity": "warning",
                        "metric_value": "+12% QoQ",
                    }
                ],
                "recommendations": [
                    "Review infrastructure costs for optimization opportunities",
                    "Consider reserved instances for predictable workloads",
                ],
                "risk_factors": ["Cash flow timing risk in Q1"],
                "compliance_notes": ["Ensure Q4 reports meet IFRS requirements"],
                "next_steps": ["Generate detailed Q1 budget proposal"],
                "confidence_score": 0.85,
                "processing_time_ms": 2200,
            }
        }
