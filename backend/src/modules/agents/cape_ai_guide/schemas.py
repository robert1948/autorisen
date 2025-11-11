"""
CapeAI Guide Agent Pydantic Schemas

Defines the input/output models for the CapeAI Guide agent task execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CapeAIGuideTaskInput(BaseModel):
    """Input schema for CapeAI Guide agent tasks."""

    query: str = Field(
        ...,
        description="User's question or request for assistance",
        min_length=1,
        max_length=1000,
    )
    context: Optional[Dict[str, Any]] = Field(
        default={}, description="Current user context (page, feature, user data, etc.)"
    )
    user_level: Optional[str] = Field(
        default="beginner",
        description="User experience level: beginner, intermediate, advanced",
    )
    preferred_format: Optional[str] = Field(
        default="text", description="Response format: text, steps, checklist, code"
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "How do I set up automated workflows?",
                "context": {
                    "current_page": "/dashboard/workflows",
                    "user_role": "admin",
                    "features_used": ["basic_workflows"],
                },
                "user_level": "intermediate",
                "preferred_format": "steps",
            }
        }


class ResourceLink(BaseModel):
    """Resource link with title and URL."""

    title: str = Field(..., description="Display title for the resource")
    url: str = Field(..., description="URL to the resource")
    type: Optional[str] = Field(None, description="Resource type: doc, tutorial, video")


class CapeAIGuideTaskOutput(BaseModel):
    """Output schema for CapeAI Guide agent tasks."""

    response: str = Field(..., description="AI assistant response to the user query")
    suggestions: List[str] = Field(
        default_factory=list, description="Related suggestions or next steps"
    )
    resources: List[ResourceLink] = Field(
        default_factory=list, description="Helpful links, documentation, or tutorials"
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
                "response": "To set up automated workflows, follow these steps...",
                "suggestions": [
                    "Learn about workflow triggers",
                    "Explore advanced automation features",
                    "Set up your first automation rule",
                ],
                "resources": [
                    {
                        "title": "Workflow Setup Guide",
                        "url": "/docs/workflows/setup",
                        "type": "doc",
                    },
                    {
                        "title": "Automation Best Practices",
                        "url": "/docs/workflows/best-practices",
                        "type": "tutorial",
                    },
                ],
                "confidence_score": 0.92,
                "processing_time_ms": 1250,
            }
        }
