"""
Content Agent Pydantic Schemas

Defines the input/output models for the Content Agent task execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContentAgentTaskInput(BaseModel):
    """Input schema for Content Agent tasks."""

    query: str = Field(
        ...,
        description="Content request or editing instructions",
        min_length=1,
        max_length=5000,
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Context (brand guidelines, target audience, prior content, etc.)",
    )
    content_type: Optional[str] = Field(
        default="general",
        description="Content type: general, blog_post, social_media, email, documentation, landing_page",
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Desired tone: professional, casual, technical, persuasive, friendly",
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="Target audience description",
    )
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum content length in words",
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "Write a blog post about AI automation benefits for small businesses",
                "content_type": "blog_post",
                "tone": "professional",
                "target_audience": "small business owners",
                "max_length": 800,
            }
        }


class ContentPiece(BaseModel):
    """A generated content piece."""

    title: str = Field(..., description="Content title or heading")
    body: str = Field(..., description="Content body text")
    content_type: str = Field(..., description="Type of content")
    word_count: int = Field(..., description="Word count")
    seo_keywords: List[str] = Field(default_factory=list, description="SEO keywords if applicable")


class ContentAgentTaskOutput(BaseModel):
    """Output schema for Content Agent tasks."""

    response: str = Field(..., description="AI assistant response with the generated content")
    content_pieces: List[ContentPiece] = Field(
        default_factory=list,
        description="Generated content pieces",
    )
    editing_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for improving the content",
    )
    seo_recommendations: List[str] = Field(
        default_factory=list,
        description="SEO optimization tips",
    )
    alternative_headlines: List[str] = Field(
        default_factory=list,
        description="Alternative headline options",
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
                "response": "Here's a blog post about AI automation for small businesses...",
                "content_pieces": [
                    {
                        "title": "5 Ways AI Automation Transforms Small Businesses",
                        "body": "Artificial intelligence is no longer just for large corporations...",
                        "content_type": "blog_post",
                        "word_count": 750,
                        "seo_keywords": ["AI automation", "small business", "productivity"],
                    }
                ],
                "editing_suggestions": [
                    "Add specific case studies or examples",
                    "Include a call-to-action at the end",
                ],
                "seo_recommendations": [
                    "Target 'AI automation small business' as primary keyword",
                ],
                "alternative_headlines": [
                    "How AI Automation Is Leveling the Playing Field for Small Businesses",
                ],
                "next_steps": [
                    "Review and personalize the content",
                    "Add relevant images",
                    "Schedule for publication",
                ],
                "confidence_score": 0.88,
                "processing_time_ms": 3500,
            }
        }
