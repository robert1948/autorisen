"""
Task 2.1.5: Advanced Prompting Templates Test Suite
==================================================

Comprehensive test suite for advanced prompting functionality:
- Template management tests
- Prompt generation tests  
- Performance tracking tests
- Personalization integration tests
- API endpoint tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from app.services.advanced_prompting_service import (
    AdvancedPromptingService,
    PromptTemplate,
    PromptGenerationRequest,
    GeneratedPrompt,
    PromptCategory,
    PromptRole,
    PromptComplexity,
    TemplateVersion
)


class TestAdvancedPromptingService:
    """Test suite for AdvancedPromptingService"""

    @pytest.fixture
    def mock_template(self):
        """Create a mock prompt template"""
        return PromptTemplate(
            template_id="test_template_001",
            name="Test Template",
            description="A test template for unit testing",
            category=PromptCategory.GENERAL_CHAT,
            role=PromptRole.ASSISTANT,
            complexity=PromptComplexity.INTERMEDIATE,
            version=TemplateVersion.V1,
            template_content="Hello {{user_name}}, I'm here to help with {{topic}}.",
            variables=["user_name", "topic"],
            requirements={},
            effectiveness_score=0.85,
            usage_count=100,
            success_rate=0.92,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="test_user",
            tags=["general", "assistance"],
            language="en"
        )

    @pytest.fixture
    def prompting_service(self):
        """Create AdvancedPromptingService with mocked dependencies"""
        with patch('app.services.advanced_prompting_service.get_context_service') as mock_context, \
             patch('app.services.advanced_prompting_service.get_personalization_service') as mock_personalization:
            
            mock_context_service = AsyncMock()
            mock_personalization_service = AsyncMock()
            
            mock_context.return_value = mock_context_service
            mock_personalization.return_value = mock_personalization_service
            
            service = AdvancedPromptingService()
            return service

    @pytest.mark.asyncio
    async def test_service_initialization(self, prompting_service):
        """Test service initialization with default templates"""
        assert prompting_service is not None
        
        # Test default templates are loaded
        templates = await prompting_service.list_templates()
        assert len(templates) >= 6  # Should have default templates
        
        # Check for key default templates
        template_names = [t.name for t in templates]
        assert "General Chat Assistant" in template_names
        assert "Code Assistant" in template_names
        assert "Educational Tutor" in template_names

    @pytest.mark.asyncio
    async def test_create_custom_template(self, prompting_service):
        """Test creating custom templates"""
        template = await prompting_service.create_custom_template(
            name="Custom Test Template",
            description="A custom template for testing",
            category=PromptCategory.BUSINESS,
            role=PromptRole.CONSULTANT,
            complexity=PromptComplexity.ADVANCED,
            template_content="As a business consultant, I recommend {{strategy}} for {{business_type}}.",
            variables=["strategy", "business_type"],
            created_by="test_user",
            tags=["business", "consulting"]
        )
        
        assert template.name == "Custom Test Template"
        assert template.category == PromptCategory.BUSINESS
        assert template.role == PromptRole.CONSULTANT
        assert template.complexity == PromptComplexity.ADVANCED
        assert "strategy" in template.variables
        assert "business_type" in template.variables
        assert "business" in template.tags

    @pytest.mark.asyncio
    async def test_template_filtering(self, prompting_service):
        """Test template filtering functionality"""
        # Create test templates with different categories
        await prompting_service.create_custom_template(
            name="Code Helper",
            description="Help with coding",
            category=PromptCategory.CODE_ASSISTANCE,
            role=PromptRole.EXPERT,
            complexity=PromptComplexity.INTERMEDIATE,
            template_content="I'll help you with {{programming_language}} code.",
            variables=["programming_language"],
            created_by="test_user",
            tags=["coding"]
        )
        
        # Filter by category
        code_templates = await prompting_service.list_templates(
            category=PromptCategory.CODE_ASSISTANCE
        )
        assert all(t.category == PromptCategory.CODE_ASSISTANCE for t in code_templates)
        
        # Filter by role
        expert_templates = await prompting_service.list_templates(
            role=PromptRole.EXPERT
        )
        assert all(t.role == PromptRole.EXPERT for t in expert_templates)
        
        # Filter by complexity
        intermediate_templates = await prompting_service.list_templates(
            complexity=PromptComplexity.INTERMEDIATE
        )
        assert all(t.complexity == PromptComplexity.INTERMEDIATE for t in intermediate_templates)

    @pytest.mark.asyncio
    async def test_prompt_generation_basic(self, prompting_service, mock_template):
        """Test basic prompt generation without personalization"""
        # Add mock template to service
        prompting_service.templates[mock_template.template_id] = mock_template
        
        request = PromptGenerationRequest(
            template_id=mock_template.template_id,
            user_id="test_user",
            context_variables={"user_name": "Alice", "topic": "Python programming"},
            personalization_enabled=False
        )
        
        result = await prompting_service.generate_prompt(request)
        
        assert result.prompt_content == "Hello Alice, I'm here to help with Python programming."
        assert result.template_used == mock_template.template_id
        assert result.variables_substituted == {"user_name": "Alice", "topic": "Python programming"}
        assert not result.personalization_applied

    @pytest.mark.asyncio
    async def test_prompt_generation_with_personalization(self, prompting_service, mock_template):
        """Test prompt generation with personalization"""
        # Add mock template to service
        prompting_service.templates[mock_template.template_id] = mock_template
        
        # Mock personalization service
        mock_profile = MagicMock()
        mock_profile.communication_style.value = "professional"
        mock_profile.expertise_level.value = "intermediate"
        mock_profile.learning_style.value = "visual"
        mock_profile.personality_traits = {"openness": 0.8, "conscientiousness": 0.7}
        
        with patch('app.services.advanced_prompting_service.get_personalization_service') as mock_personalization:
            mock_personalization_service = AsyncMock()
            mock_personalization_service.get_personality_profile.return_value = mock_profile
            mock_personalization.return_value = mock_personalization_service
            
            request = PromptGenerationRequest(
                template_id=mock_template.template_id,
                user_id="test_user",
                context_variables={"user_name": "Alice", "topic": "Python programming"},
                personalization_enabled=True
            )
            
            result = await prompting_service.generate_prompt(request)
            
            assert result.personalization_applied
            assert "Alice" in result.prompt_content
            assert "Python programming" in result.prompt_content

    @pytest.mark.asyncio
    async def test_template_performance_tracking(self, prompting_service, mock_template):
        """Test template performance tracking"""
        # Add mock template to service
        prompting_service.templates[mock_template.template_id] = mock_template
        initial_usage = mock_template.usage_count
        initial_success_rate = mock_template.success_rate
        
        # Update performance with success
        await prompting_service.update_template_performance(
            template_id=mock_template.template_id,
            success=True,
            user_rating=4.5,
            response_time_ms=250
        )
        
        updated_template = prompting_service.templates[mock_template.template_id]
        assert updated_template.usage_count == initial_usage + 1
        
        # Update performance with failure
        await prompting_service.update_template_performance(
            template_id=mock_template.template_id,
            success=False,
            user_rating=2.0,
            response_time_ms=500
        )
        
        updated_template = prompting_service.templates[mock_template.template_id]
        assert updated_template.usage_count == initial_usage + 2

    @pytest.mark.asyncio
    async def test_template_analytics(self, prompting_service):
        """Test template analytics generation"""
        analytics = await prompting_service.get_template_analytics()
        
        assert "total_templates" in analytics["overview"]
        assert "category_distribution" in analytics
        assert "role_distribution" in analytics
        assert "top_performing_templates" in analytics
        
        assert analytics["overview"]["total_templates"] >= 0
        assert isinstance(analytics["category_distribution"], dict)
        assert isinstance(analytics["top_performing_templates"], list)

    @pytest.mark.asyncio
    async def test_jinja2_template_rendering(self, prompting_service):
        """Test complex Jinja2 template rendering"""
        complex_template = await prompting_service.create_custom_template(
            name="Complex Template",
            description="Template with complex Jinja2 features",
            category=PromptCategory.EDUCATIONAL,
            role=PromptRole.TEACHER,
            complexity=PromptComplexity.ADVANCED,
            template_content="""
Hello {{name}}! 
{% if difficulty == 'beginner' %}
Let's start with the basics of {{subject}}.
{% elif difficulty == 'intermediate' %}
Now that you know the basics, let's dive deeper into {{subject}}.
{% else %}
As an advanced learner, let's explore complex {{subject}} concepts.
{% endif %}

{% for topic in topics %}
- {{topic}}
{% endfor %}
            """.strip(),
            variables=["name", "difficulty", "subject", "topics"],
            created_by="test_user"
        )
        
        request = PromptGenerationRequest(
            template_id=complex_template.template_id,
            user_id="test_user",
            context_variables={
                "name": "Bob",
                "difficulty": "intermediate",
                "subject": "machine learning",
                "topics": ["neural networks", "deep learning", "transformers"]
            },
            personalization_enabled=False
        )
        
        result = await prompting_service.generate_prompt(request)
        
        assert "Hello Bob!" in result.prompt_content
        assert "dive deeper into machine learning" in result.prompt_content
        assert "neural networks" in result.prompt_content
        assert "deep learning" in result.prompt_content
        assert "transformers" in result.prompt_content

    @pytest.mark.asyncio
    async def test_template_versioning(self, prompting_service):
        """Test template versioning functionality"""
        # Create initial template
        template = await prompting_service.create_custom_template(
            name="Version Test Template",
            description="Template for testing versioning",
            category=PromptCategory.GENERAL_CHAT,
            role=PromptRole.ASSISTANT,
            complexity=PromptComplexity.SIMPLE,
            template_content="Version 1.0 content: {{message}}",
            variables=["message"],
            created_by="test_user"
        )
        
        assert template.version == TemplateVersion.V1
        
        # Update template (simulate version update)
        template.template_content = "Version 2.0 content with improvements: {{message}}"
        template.version = TemplateVersion.V2
        
        assert template.version == TemplateVersion.V2
        assert "Version 2.0" in template.template_content

    @pytest.mark.asyncio
    async def test_error_handling(self, prompting_service):
        """Test error handling in various scenarios"""
        # Test non-existent template
        request = PromptGenerationRequest(
            template_id="non_existent_template",
            user_id="test_user",
            context_variables={}
        )
        
        with pytest.raises(ValueError, match="Template .* not found"):
            await prompting_service.generate_prompt(request)
        
        # Test template with missing variables
        template = await prompting_service.create_custom_template(
            name="Missing Variables Template",
            description="Template missing required variables",
            category=PromptCategory.GENERAL_CHAT,
            role=PromptRole.ASSISTANT,
            complexity=PromptComplexity.SIMPLE,
            template_content="Hello {{name}}, your {{item}} is ready.",
            variables=["name", "item"],
            created_by="test_user"
        )
        
        request = PromptGenerationRequest(
            template_id=template.template_id,
            user_id="test_user",
            context_variables={"name": "Alice"}  # Missing 'item'
        )
        
        # Should handle gracefully with default values
        result = await prompting_service.generate_prompt(request)
        assert "Alice" in result.prompt_content

    @pytest.mark.asyncio
    async def test_context_integration(self, prompting_service, mock_template):
        """Test integration with context service"""
        # Add mock template to service
        prompting_service.templates[mock_template.template_id] = mock_template
        
        # Mock context service
        mock_context = {
            "conversation_history": [
                {"role": "user", "content": "I need help with coding"},
                {"role": "assistant", "content": "I'd be happy to help with coding!"}
            ],
            "user_preferences": {"language": "Python", "experience": "intermediate"}
        }
        
        with patch('app.services.advanced_prompting_service.get_context_service') as mock_context_service_getter:
            mock_context_service = AsyncMock()
            mock_context_service.get_conversation_context.return_value = mock_context
            mock_context_service_getter.return_value = mock_context_service
            
            request = PromptGenerationRequest(
                template_id=mock_template.template_id,
                user_id="test_user",
                context_variables={"user_name": "Alice", "topic": "Python programming"},
                conversation_id="conv_123"
            )
            
            result = await prompting_service.generate_prompt(request)
            
            assert result.template_used == mock_template.template_id
            # Context should be available in generation metadata
            assert "context_applied" in result.generation_metadata


class TestAdvancedPromptingAPI:
    """Test suite for Advanced Prompting API endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for authentication"""
        user = MagicMock()
        user.id = 123
        user.email = "test@example.com"
        return user

    @pytest.mark.asyncio
    async def test_list_templates_endpoint(self, mock_user):
        """Test the list templates API endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.advanced_prompting.get_current_user', return_value=mock_user):
            with patch('app.routes.advanced_prompting.get_prompting_service') as mock_service:
                mock_prompting_service = AsyncMock()
                mock_templates = [
                    MagicMock(
                        template_id="test_001",
                        name="Test Template",
                        description="A test template",
                        category=PromptCategory.GENERAL_CHAT,
                        role=PromptRole.ASSISTANT,
                        complexity=PromptComplexity.SIMPLE,
                        version=TemplateVersion.V1,
                        template_content="Test content",
                        variables=["test_var"],
                        requirements={},
                        effectiveness_score=0.8,
                        usage_count=10,
                        success_rate=0.9,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by="test_user",
                        tags=["test"],
                        language="en"
                    )
                ]
                mock_prompting_service.list_templates.return_value = mock_templates
                mock_service.return_value = mock_prompting_service
                
                client = TestClient(app)
                response = client.get("/api/prompting/templates")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["template_id"] == "test_001"
                assert data[0]["name"] == "Test Template"

    @pytest.mark.asyncio
    async def test_generate_prompt_endpoint(self, mock_user):
        """Test the generate prompt API endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.advanced_prompting.get_current_user', return_value=mock_user):
            with patch('app.routes.advanced_prompting.get_prompting_service') as mock_service:
                mock_prompting_service = AsyncMock()
                mock_result = MagicMock(
                    prompt_content="Generated prompt content",
                    template_used="test_template",
                    variables_substituted={"var": "value"},
                    personalization_applied=True,
                    complexity_level=PromptComplexity.INTERMEDIATE,
                    role_used=PromptRole.ASSISTANT,
                    generation_metadata={"test": "metadata"},
                    generated_at=datetime.now()
                )
                mock_prompting_service.generate_prompt.return_value = mock_result
                mock_service.return_value = mock_prompting_service
                
                client = TestClient(app)
                response = client.post("/api/prompting/generate", json={
                    "template_id": "test_template",
                    "context_variables": {"var": "value"},
                    "personalization_enabled": True
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["prompt_content"] == "Generated prompt content"
                assert data["template_used"] == "test_template"
                assert data["personalization_applied"] is True

    @pytest.mark.asyncio
    async def test_create_custom_template_endpoint(self, mock_user):
        """Test the create custom template API endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.advanced_prompting.get_current_user', return_value=mock_user):
            with patch('app.routes.advanced_prompting.get_prompting_service') as mock_service:
                mock_prompting_service = AsyncMock()
                mock_template = MagicMock(
                    template_id="custom_001",
                    name="Custom Template",
                    description="A custom template",
                    category=PromptCategory.BUSINESS,
                    role=PromptRole.CONSULTANT,
                    complexity=PromptComplexity.ADVANCED,
                    version=TemplateVersion.V1,
                    template_content="Custom content {{var}}",
                    variables=["var"],
                    requirements={},
                    effectiveness_score=0.0,
                    usage_count=0,
                    success_rate=0.0,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by=str(mock_user.id),
                    tags=["custom"],
                    language="en"
                )
                mock_prompting_service.create_custom_template.return_value = mock_template
                mock_service.return_value = mock_prompting_service
                
                client = TestClient(app)
                response = client.post("/api/prompting/templates", json={
                    "name": "Custom Template",
                    "description": "A custom template",
                    "category": "BUSINESS",
                    "role": "CONSULTANT",
                    "complexity": "ADVANCED",
                    "template_content": "Custom content {{var}}",
                    "variables": ["var"],
                    "tags": ["custom"]
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["template_id"] == "custom_001"
                assert data["name"] == "Custom Template"
                assert data["category"] == "BUSINESS"

    @pytest.mark.asyncio
    async def test_template_analytics_endpoint(self, mock_user):
        """Test the template analytics API endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.advanced_prompting.get_current_user', return_value=mock_user):
            with patch('app.routes.advanced_prompting.get_prompting_service') as mock_service:
                mock_prompting_service = AsyncMock()
                mock_analytics = {
                    "total_templates": 10,
                    "category_distribution": {"GENERAL_CHAT": 5, "CODE_ASSISTANCE": 3},
                    "role_distribution": {"ASSISTANT": 6, "EXPERT": 2},
                    "complexity_distribution": {"BASIC": 4, "INTERMEDIATE": 4, "ADVANCED": 2},
                    "top_templates": [],
                    "performance_metrics": {"average_effectiveness": 0.8}
                }
                mock_prompting_service.get_template_analytics.return_value = mock_analytics
                mock_service.return_value = mock_prompting_service
                
                client = TestClient(app)
                response = client.get("/api/prompting/analytics")
                
                assert response.status_code == 200
                data = response.json()
                assert data["total_templates"] == 10
                assert "category_distribution" in data
                assert "performance_metrics" in data


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
