"""
Unit tests for CapeAI Guide agent schemas and data models.

Tests Pydantic models, validation, serialization, and edge cases.
"""

import pytest
from typing import Dict, Any
from pydantic import ValidationError

from backend.src.modules.agents.cape_ai_guide.schemas import (
    CapeAIGuideTaskInput,
    CapeAIGuideTaskOutput,
    ResourceLink,
)


class TestCapeAIGuideTaskInput:
    """Test CapeAI Guide input schema validation."""

    def test_minimal_valid_input(self):
        """Test minimal valid input with only required fields."""
        input_data = CapeAIGuideTaskInput(query="How do I get started?")

        assert input_data.query == "How do I get started?"
        assert input_data.user_level == "beginner"  # default value
        assert input_data.preferred_format == "text"  # default value
        assert input_data.context is None  # optional field

    def test_complete_valid_input(self):
        """Test complete input with all fields populated."""
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

    def test_query_validation(self):
        """Test query field validation."""
        # Test empty query should fail
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskInput(query="")

        assert "String should have at least 1 character" in str(exc_info.value)

        # Test very long query
        long_query = "x" * 1001
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskInput(query=long_query)

        assert "String should have at most 1000 characters" in str(exc_info.value)

    def test_user_level_validation(self):
        """Test user level field accepts valid values."""
        valid_levels = ["beginner", "intermediate", "advanced"]

        for level in valid_levels:
            input_data = CapeAIGuideTaskInput(query="test query", user_level=level)
            assert input_data.user_level == level

    def test_preferred_format_validation(self):
        """Test preferred format field accepts valid values."""
        valid_formats = ["text", "steps", "checklist", "code"]

        for format_type in valid_formats:
            input_data = CapeAIGuideTaskInput(
                query="test query", preferred_format=format_type
            )
            assert input_data.preferred_format == format_type

    def test_context_flexibility(self):
        """Test context field accepts various data structures."""
        contexts = [
            {"page": "/dashboard"},
            {"user_role": "admin", "permissions": ["read", "write"]},
            {"nested": {"data": {"value": 123}}},
            {},  # empty context
        ]

        for context in contexts:
            input_data = CapeAIGuideTaskInput(query="test query", context=context)
            assert input_data.context == context


class TestResourceLink:
    """Test ResourceLink model validation."""

    def test_valid_resource_link(self):
        """Test valid resource link creation."""
        resource = ResourceLink(
            title="Getting Started Guide", url="/docs/getting-started", type="doc"
        )

        assert resource.title == "Getting Started Guide"
        assert resource.url == "/docs/getting-started"
        assert resource.type == "doc"

    def test_optional_type_field(self):
        """Test resource link with optional type field."""
        resource = ResourceLink(title="Help Page", url="/help")

        assert resource.title == "Help Page"
        assert resource.url == "/help"
        assert resource.type is None

    def test_required_fields_validation(self):
        """Test that required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ResourceLink(url="/docs/test")  # missing title

        assert "Field required" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            ResourceLink(title="Test Doc")  # missing url

        assert "Field required" in str(exc_info.value)


class TestCapeAIGuideTaskOutput:
    """Test CapeAI Guide output schema validation."""

    def test_minimal_valid_output(self):
        """Test minimal valid output with required fields only."""
        output = CapeAIGuideTaskOutput(
            response="This is a test response", confidence_score=0.85
        )

        assert output.response == "This is a test response"
        assert output.confidence_score == 0.85
        assert output.suggestions == []  # default empty list
        assert output.resources == []  # default empty list
        assert output.processing_time_ms is None  # optional field

    def test_complete_valid_output(self):
        """Test complete output with all fields populated."""
        resources = [
            ResourceLink(title="Guide", url="/docs/guide", type="doc"),
            ResourceLink(title="Tutorial", url="/tutorials/basic"),
        ]

        output = CapeAIGuideTaskOutput(
            response="Complete response with all details",
            suggestions=["Learn more", "Try advanced features", "Contact support"],
            resources=resources,
            confidence_score=0.92,
            processing_time_ms=1500,
        )

        assert output.response == "Complete response with all details"
        assert len(output.suggestions) == 3
        assert output.suggestions[0] == "Learn more"
        assert len(output.resources) == 2
        assert output.confidence_score == 0.92
        assert output.processing_time_ms == 1500

    def test_confidence_score_validation(self):
        """Test confidence score bounds validation."""
        # Test valid range
        valid_scores = [0.0, 0.5, 1.0, 0.123, 0.999]

        for score in valid_scores:
            output = CapeAIGuideTaskOutput(response="test", confidence_score=score)
            assert output.confidence_score == score

        # Test invalid values below 0
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskOutput(response="test", confidence_score=-0.1)

        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Test invalid values above 1
        with pytest.raises(ValidationError) as exc_info:
            CapeAIGuideTaskOutput(response="test", confidence_score=1.1)

        assert "Input should be less than or equal to 1" in str(exc_info.value)

    def test_processing_time_validation(self):
        """Test processing time field validation."""
        # Positive values should work
        output = CapeAIGuideTaskOutput(
            response="test", confidence_score=0.8, processing_time_ms=1000
        )
        assert output.processing_time_ms == 1000

        # Zero should work
        output = CapeAIGuideTaskOutput(
            response="test", confidence_score=0.8, processing_time_ms=0
        )
        assert output.processing_time_ms == 0

    def test_json_serialization(self):
        """Test that schemas can be serialized to JSON."""
        output = CapeAIGuideTaskOutput(
            response="Test response",
            suggestions=["suggestion 1", "suggestion 2"],
            resources=[ResourceLink(title="Doc", url="/docs/test")],
            confidence_score=0.75,
            processing_time_ms=800,
        )

        # Should serialize without errors
        json_data = output.dict()

        assert json_data["response"] == "Test response"
        assert len(json_data["suggestions"]) == 2
        assert len(json_data["resources"]) == 1
        assert json_data["confidence_score"] == 0.75
        assert json_data["processing_time_ms"] == 800

    def test_schema_examples(self):
        """Test that schema examples are valid."""
        # Test input schema example
        input_example = {
            "query": "How do I set up automated workflows?",
            "context": {
                "current_page": "/dashboard/workflows",
                "user_role": "admin",
                "features_used": ["basic_workflows"],
            },
            "user_level": "intermediate",
            "preferred_format": "steps",
        }

        input_obj = CapeAIGuideTaskInput(**input_example)
        assert input_obj.query == input_example["query"]

        # Test output schema example
        output_example = {
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
                }
            ],
            "confidence_score": 0.92,
            "processing_time_ms": 1250,
        }

        output_obj = CapeAIGuideTaskOutput(**output_example)
        assert output_obj.confidence_score == output_example["confidence_score"]
