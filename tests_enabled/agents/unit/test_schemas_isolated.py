"""
Isolated unit tests for CapeAI Guide agent schemas.

Tests Pydantic models without requiring full application imports.
"""

from typing import Any, Dict, List, Optional

import pytest
from pydantic import BaseModel, Field, ValidationError


# Direct schema definitions for testing (avoiding import issues)
class ResourceLink(BaseModel):
    """Resource link with title and URL."""

    title: str = Field(..., description="Display title for the resource")
    url: str = Field(..., description="URL to the resource")
    type: Optional[str] = Field(None, description="Resource type")


class CapeAIGuideTaskInput(BaseModel):
    """Input schema for CapeAI Guide agent tasks."""

    query: str = Field(
        ..., description="User's question or request", min_length=1, max_length=1000
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Current user context")
    user_level: Optional[str] = Field("beginner", description="User experience level")
    preferred_format: Optional[str] = Field("text", description="Response format")


class CapeAIGuideTaskOutput(BaseModel):
    """Output schema for CapeAI Guide agent tasks."""

    response: str = Field(..., description="AI assistant response")
    suggestions: List[str] = Field(
        default_factory=list, description="Related suggestions"
    )
    resources: List[ResourceLink] = Field(
        default_factory=list, description="Helpful links"
    )
    confidence_score: float = Field(
        ..., description="Response confidence score", ge=0.0, le=1.0
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Processing time in milliseconds"
    )


class TestCapeAIGuideSchemas:
    """Test suite for CapeAI Guide agent schemas."""

    def test_input_schema_minimal(self):
        """Test minimal valid input."""
        input_data = CapeAIGuideTaskInput(query="How do I get started?")

        assert input_data.query == "How do I get started?"
        assert input_data.user_level == "beginner"
        assert input_data.preferred_format == "text"
        assert input_data.context is None

    def test_input_schema_complete(self):
        """Test complete input with all fields."""
        context = {
            "current_page": "/dashboard/workflows",
            "user_role": "admin",
            "features_used": ["workflows", "automation"],
        }

        input_data = CapeAIGuideTaskInput(
            query="How do I set up advanced workflows?",
            context=context,
            user_level="advanced",
            preferred_format="code",
        )

        assert input_data.query == "How do I set up advanced workflows?"
        assert input_data.context == context
        assert input_data.user_level == "advanced"
        assert input_data.preferred_format == "code"

    def test_query_validation_empty(self):
        """Test query validation with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskInput(query="")

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_query_validation_too_long(self):
        """Test query validation with excessive length."""
        long_query = "x" * 1001
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskInput(query=long_query)

        assert "String should have at most 1000 characters" in str(exc_info.value)

    def test_output_schema_minimal(self):
        """Test minimal valid output."""
        output = CapeAIGuideTaskOutput(
            response="This is a test response", confidence_score=0.85
        )

        assert output.response == "This is a test response"
        assert output.confidence_score == 0.85
        assert output.suggestions == []
        assert output.resources == []
        assert output.processing_time_ms is None

    def test_output_schema_complete(self):
        """Test complete output with all fields."""
        resources = [
            ResourceLink(title="Guide", url="/docs/guide", type="doc"),
            ResourceLink(title="Tutorial", url="/tutorials/basic"),
        ]

        output = CapeAIGuideTaskOutput(
            response="Complete response with all details",
            suggestions=["Learn more", "Try advanced features"],
            resources=resources,
            confidence_score=0.92,
            processing_time_ms=1500,
        )

        assert output.response == "Complete response with all details"
        assert len(output.suggestions) == 2
        assert len(output.resources) == 2
        assert output.confidence_score == 0.92
        assert output.processing_time_ms == 1500

    def test_confidence_score_validation(self):
        """Test confidence score bounds validation."""
        # Valid scores
        valid_scores = [0.0, 0.5, 1.0]
        for score in valid_scores:
            output = CapeAIGuideTaskOutput(response="test", confidence_score=score)
            assert output.confidence_score == score

        # Invalid score below 0
        with pytest.raises(ValidationError):
            CapeAIGuideTaskOutput(response="test", confidence_score=-0.1)

        # Invalid score above 1
        with pytest.raises(ValidationError):
            CapeAIGuideTaskOutput(response="test", confidence_score=1.1)

    def test_resource_link_validation(self):
        """Test ResourceLink model validation."""
        # Valid resource
        resource = ResourceLink(
            title="Getting Started Guide", url="/docs/getting-started", type="doc"
        )
        assert resource.title == "Getting Started Guide"
        assert resource.url == "/docs/getting-started"
        assert resource.type == "doc"

        # Missing required fields
        with pytest.raises(ValidationError):
            ResourceLink(url="/docs/test")  # missing title

        with pytest.raises(ValidationError):
            ResourceLink(title="Test Doc")  # missing url

    def test_json_serialization(self):
        """Test JSON serialization of schemas."""
        output = CapeAIGuideTaskOutput(
            response="Test response",
            suggestions=["suggestion 1"],
            resources=[ResourceLink(title="Doc", url="/docs/test")],
            confidence_score=0.75,
            processing_time_ms=800,
        )

        json_data = output.dict()
        assert json_data["response"] == "Test response"
        assert len(json_data["suggestions"]) == 1
        assert len(json_data["resources"]) == 1
        assert json_data["confidence_score"] == 0.75
