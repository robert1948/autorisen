"""
Tests for Enhanced CapeAI Service with Multi-Provider Support (Task 2.1.1)
==========================================================================

Test suite covering:
- Enhanced CapeAI service with multi-provider integration
- Model selection and intelligent routing
- Context-aware provider selection
- API endpoints for model management
- Performance monitoring integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from app.routes.cape_ai import (
    CapeAIService,
    AIPromptRequest,
    AIResponse,
    cape_ai_service
)
from app.services.multi_provider_ai_service import ModelProvider, AIProviderResponse


class TestEnhancedCapeAIService:
    """Test cases for the enhanced CapeAI service"""
    
    @pytest.fixture
    def mock_multi_ai(self):
        """Mock multi-provider AI service"""
        with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_service:
            multi_ai = Mock()
            mock_service.return_value = multi_ai
            
            # Mock available models
            multi_ai.get_available_models.return_value = {
                "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                "claude": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
            }
            
            # Mock model configs
            multi_ai.get_model_config.return_value = Mock(
                provider=ModelProvider.CLAUDE,
                model_name="claude-3-sonnet-20240229",
                temperature=0.7,
                max_tokens=4096,
                cost_per_1k_prompt=0.003
            )
            
            multi_ai.get_default_model.return_value = "claude-3-sonnet"
            
            yield multi_ai
    
    @pytest.fixture
    def service(self, mock_multi_ai):
        """Create enhanced CapeAI service instance"""
        service = CapeAIService()
        service.multi_ai = mock_multi_ai
        return service
    
    @pytest.fixture
    def mock_user(self):
        """Mock user object"""
        user = Mock()
        user.id = "test-user-123"
        user.created_at = datetime.now()
        user.role = "user"
        return user
    
    def test_service_initialization(self, mock_multi_ai):
        """Test service initializes with multi-provider support"""
        
        service = CapeAIService()
        assert hasattr(service, 'multi_ai')
        assert service.conversation_cache == {}
        assert service.user_profiles == {}
    
    def test_model_selection_technical_query(self, service, mock_user):
        """Test model selection for technical queries"""
        
        # Technical query should prefer Claude
        message = "Help me debug this Python code with algorithm optimization"
        user_context = {"expertise_level": "advanced", "platform_context": {"area": "general"}}
        
        model = service.select_optimal_model(message, user_context)
        
        # Should select Claude for technical reasoning
        assert "claude" in model.lower()
    
    def test_model_selection_creative_query(self, service, mock_user):
        """Test model selection for creative queries"""
        
        # Mock available models to include GPT-4
        service.multi_ai.get_available_models.return_value = {
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "claude": ["claude-3-sonnet"]
        }
        
        message = "Write a creative marketing campaign for our new product"
        user_context = {"expertise_level": "intermediate", "platform_context": {"area": "general"}}
        
        model = service.select_optimal_model(message, user_context)
        
        # Should prefer GPT-4 for creative tasks
        assert model == "gpt-4"
    
    def test_model_selection_beginner_query(self, service, mock_user):
        """Test model selection for beginner queries"""
        
        # Mock available models
        service.multi_ai.get_available_models.return_value = {
            "claude": ["claude-3-haiku", "claude-3-sonnet"],
            "openai": ["gpt-3.5-turbo", "gpt-4"]
        }
        
        message = "Hi"  # Short, simple query
        user_context = {"expertise_level": "beginner", "platform_context": {"area": "general"}}
        
        model = service.select_optimal_model(message, user_context)
        
        # Should prefer fast/cheap model for simple queries
        assert model == "claude-3-haiku"
    
    def test_model_selection_user_preference(self, service, mock_user):
        """Test model selection respects user preference"""
        
        # User explicitly requests a model
        message = "Any message"
        user_context = {"expertise_level": "intermediate", "platform_context": {"area": "general"}}
        user_preference = "gpt-4"
        
        # Mock model config for preference
        service.multi_ai.get_model_config.return_value = Mock(
            provider=ModelProvider.OPENAI,
            model_name="gpt-4"
        )
        
        model = service.select_optimal_model(message, user_context, user_preference=user_preference)
        
        assert model == "gpt-4"
    
    def test_model_selection_provider_preference(self, service, mock_user):
        """Test model selection with provider preference"""
        
        # Mock provider models
        service.multi_ai.get_available_models.return_value = {
            "openai": ["gpt-4", "gpt-3.5-turbo"],
            "claude": ["claude-3-sonnet"]
        }
        service.multi_ai.get_default_model.return_value = "gpt-4"
        
        message = "Any message"
        user_context = {"expertise_level": "intermediate", "platform_context": {"area": "general"}}
        
        model = service.select_optimal_model(
            message, user_context, provider_preference="openai"
        )
        
        assert model == "gpt-4"
    
    @pytest.mark.asyncio
    async def test_generate_contextual_response_success(self, service, mock_user):
        """Test successful response generation with multi-provider"""
        
        # Mock successful AI response
        mock_ai_response = AIProviderResponse(
            content="This is a helpful response from Claude",
            provider=ModelProvider.CLAUDE,
            model="claude-3-sonnet-20240229",
            usage={"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
            response_time_ms=1500,
            finish_reason="end_turn"
        )
        
        service.multi_ai.generate_response = AsyncMock(return_value=mock_ai_response)
        
        message = "How do I optimize my AI agents?"
        user_context = {
            "user_id": "test-user-123",
            "expertise_level": "intermediate",
            "platform_context": {"area": "agents"}
        }
        conversation_history = []
        
        result = await service.generate_contextual_response(
            message, user_context, conversation_history
        )
        
        # Verify response structure
        assert result["response"] == "This is a helpful response from Claude"
        assert result["model_used"] == "claude-3-sonnet-20240229"
        assert result["provider_used"] == "claude"
        assert result["response_time_ms"] == 1500
        assert result["usage"]["total_tokens"] == 18
        assert "suggestions" in result
        assert "actions" in result
    
    @pytest.mark.asyncio
    async def test_generate_contextual_response_with_parameters(self, service, mock_user):
        """Test response generation with custom parameters"""
        
        mock_ai_response = AIProviderResponse(
            content="Custom temperature response",
            provider=ModelProvider.OPENAI,
            model="gpt-4",
            usage={"prompt_tokens": 15, "completion_tokens": 12, "total_tokens": 27},
            response_time_ms=2000,
            finish_reason="stop"
        )
        
        service.multi_ai.generate_response = AsyncMock(return_value=mock_ai_response)
        
        message = "Test message"
        user_context = {"user_id": "test-user-123"}
        conversation_history = []
        
        result = await service.generate_contextual_response(
            message, user_context, conversation_history,
            model="gpt-4",
            temperature=0.9,
            max_tokens=1000
        )
        
        # Verify the multi_ai service was called with correct parameters
        service.multi_ai.generate_response.assert_called_once()
        call_args = service.multi_ai.generate_response.call_args
        
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["temperature"] == 0.9
        assert call_args[1]["max_tokens"] == 1000
    
    @pytest.mark.asyncio
    async def test_generate_contextual_response_error_fallback(self, service, mock_user):
        """Test fallback when AI service fails"""
        
        # Mock AI service to raise exception
        service.multi_ai.generate_response = AsyncMock(side_effect=Exception("API Error"))
        
        message = "Test message"
        user_context = {"user_id": "test-user-123", "platform_context": {"area": "general"}}
        conversation_history = []
        
        result = await service.generate_contextual_response(
            message, user_context, conversation_history
        )
        
        # Should return fallback response
        assert result["model_used"] == "fallback"
        assert result["provider_used"] == "local"
        assert result["response_time_ms"] == 0
        assert "response" in result
        assert result["usage"]["total_tokens"] == 0
    
    def test_build_system_prompt_with_model_optimization(self, service):
        """Test system prompt building with model-specific optimizations"""
        
        context = {
            "platform_context": {"area": "agents"},
            "expertise_level": "advanced"
        }
        
        # Test Claude-specific prompt
        service.multi_ai.get_model_config.return_value = Mock(
            provider=ModelProvider.CLAUDE
        )
        
        prompt = service._build_system_prompt(context, "claude-3-sonnet")
        
        assert "CapeAI" in prompt
        assert "Claude" in prompt
        assert "advanced features" in prompt
        assert "AI agents section" in prompt
    
    def test_build_system_prompt_openai_optimization(self, service):
        """Test system prompt for OpenAI models"""
        
        context = {
            "platform_context": {"area": "dashboard"},
            "expertise_level": "beginner"
        }
        
        # Test OpenAI-specific prompt
        service.multi_ai.get_model_config.return_value = Mock(
            provider=ModelProvider.OPENAI
        )
        
        prompt = service._build_system_prompt(context, "gpt-4")
        
        assert "OpenAI" in prompt
        assert "step-by-step guidance" in prompt
        assert "dashboard" in prompt


class TestAIPromptRequestValidation:
    """Test enhanced request validation"""
    
    def test_valid_request_with_model_selection(self):
        """Test valid request with model parameters"""
        
        request_data = {
            "message": "Test message",
            "context": {"currentPath": "/dashboard"},
            "model": "claude-3-sonnet",
            "provider": "claude",
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        request = AIPromptRequest(**request_data)
        
        assert request.message == "Test message"
        assert request.model == "claude-3-sonnet"
        assert request.provider == "claude"
        assert request.temperature == 0.8
        assert request.max_tokens == 2000
    
    def test_invalid_provider_validation(self):
        """Test provider validation"""
        
        with pytest.raises(ValueError, match="Invalid provider"):
            AIPromptRequest(
                message="Test",
                provider="invalid_provider"
            )
    
    def test_invalid_temperature_validation(self):
        """Test temperature validation"""
        
        with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
            AIPromptRequest(
                message="Test",
                temperature=3.0
            )
    
    def test_invalid_max_tokens_validation(self):
        """Test max_tokens validation"""
        
        with pytest.raises(ValueError, match="max_tokens must be between 1 and 8192"):
            AIPromptRequest(
                message="Test",
                max_tokens=10000
            )


class TestAIResponseModel:
    """Test enhanced response model"""
    
    def test_response_with_provider_info(self):
        """Test response includes provider information"""
        
        response_data = {
            "response": "Test response",
            "session_id": "test-session",
            "context": {},
            "suggestions": ["suggestion1"],
            "actions": [{"text": "Action", "action": "/test"}],
            "model_used": "claude-3-sonnet",
            "provider_used": "claude",
            "response_time_ms": 1500
        }
        
        response = AIResponse(**response_data)
        
        assert response.model_used == "claude-3-sonnet"
        assert response.provider_used == "claude"
        assert response.response_time_ms == 1500


class TestAPIEndpoints:
    """Test new API endpoints for model management"""
    
    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI app for testing"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        
        # Mock the router
        with patch('app.routes.cape_ai.router'):
            yield app
    
    def test_get_available_models_endpoint(self, mock_app):
        """Test the /models endpoint"""
        
        with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_service:
            multi_ai = Mock()
            multi_ai.get_available_models.return_value = {
                "openai": ["gpt-4", "gpt-3.5-turbo"],
                "claude": ["claude-3-sonnet", "claude-3-haiku"]
            }
            multi_ai.get_provider_status = AsyncMock(return_value={
                "openai": {"available": True},
                "claude": {"available": True}
            })
            multi_ai.get_default_model.return_value = "claude-3-sonnet"
            mock_service.return_value = multi_ai
            
            # Import the endpoint function
            from app.routes.cape_ai import get_available_models
            
            # Mock current user
            mock_user = Mock()
            mock_user.id = "test-user"
            
            # Test the endpoint
            response = asyncio.run(get_available_models(mock_user))
            
            assert "available_models" in response
            assert "provider_status" in response
            assert "default_model" in response
            assert response["default_model"] == "claude-3-sonnet"
    
    def test_get_model_info_endpoint(self):
        """Test the /models/{model_name} endpoint"""
        
        with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_service:
            multi_ai = Mock()
            mock_config = Mock()
            mock_config.provider.value = "claude"
            mock_config.max_tokens = 4096
            mock_config.temperature = 0.7
            mock_config.supports_streaming = True
            mock_config.context_window = 200000
            mock_config.cost_per_1k_prompt = 0.003
            mock_config.cost_per_1k_completion = 0.015
            
            multi_ai.get_model_config.return_value = mock_config
            mock_service.return_value = multi_ai
            
            # Import the endpoint function
            from app.routes.cape_ai import get_model_info
            
            # Mock current user
            mock_user = Mock()
            
            # Test the endpoint
            response = asyncio.run(get_model_info("claude-3-sonnet", mock_user))
            
            assert response["model_name"] == "claude-3-sonnet"
            assert response["provider"] == "claude"
            assert response["config"]["max_tokens"] == 4096
            assert response["config"]["context_window"] == 200000
    
    def test_recommend_model_endpoint(self):
        """Test the /models/recommend endpoint"""
        
        with patch('app.routes.cape_ai.cape_ai_service') as mock_service:
            mock_service.analyze_user_context = AsyncMock(return_value={
                "expertise_level": "intermediate",
                "platform_context": {"area": "agents"}
            })
            mock_service.select_optimal_model.return_value = "claude-3-sonnet"
            
            with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_multi:
                multi_ai = Mock()
                mock_config = Mock()
                mock_config.provider.value = "claude"
                multi_ai.get_model_config.return_value = mock_config
                mock_multi.return_value = multi_ai
                
                # Import the endpoint function
                from app.routes.cape_ai import recommend_model
                
                # Mock current user
                mock_user = Mock()
                
                request_data = {
                    "message": "Help me optimize my code",
                    "context": {"currentPath": "/agents"}
                }
                
                # Test the endpoint
                response = asyncio.run(recommend_model(request_data, mock_user))
                
                assert response["recommended_model"] == "claude-3-sonnet"
                assert response["provider"] == "claude"
                assert "reasoning" in response
                assert "alternatives" in response


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_conversation_flow_with_model_selection(self):
        """Test complete conversation flow with intelligent model selection"""
        
        with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_multi, \
             patch('app.routes.cape_ai.redis_client') as mock_redis:
            
            # Setup mocks
            multi_ai = Mock()
            multi_ai.get_available_models.return_value = {
                "claude": ["claude-3-sonnet", "claude-3-haiku"],
                "openai": ["gpt-4"]
            }
            multi_ai.get_model_config.return_value = Mock(
                provider=ModelProvider.CLAUDE,
                temperature=0.7,
                max_tokens=4096
            )
            multi_ai.get_default_model.return_value = "claude-3-sonnet"
            
            # Mock AI response
            mock_ai_response = AIProviderResponse(
                content="I can help you optimize your Python code. Here are some suggestions...",
                provider=ModelProvider.CLAUDE,
                model="claude-3-sonnet-20240229",
                usage={"prompt_tokens": 25, "completion_tokens": 35, "total_tokens": 60},
                response_time_ms=1800,
                finish_reason="end_turn"
            )
            multi_ai.generate_response = AsyncMock(return_value=mock_ai_response)
            mock_multi.return_value = multi_ai
            
            # Mock Redis
            mock_redis.lrange.return_value = []
            mock_redis.lpush = Mock()
            mock_redis.expire = Mock()
            
            # Create service and test
            service = CapeAIService()
            
            # Mock user
            user = Mock()
            user.id = "test-user"
            user.created_at = datetime.now()
            
            # Analyze context
            user_context = await service.analyze_user_context(user, {"currentPath": "/agents"})
            
            # Generate response
            result = await service.generate_contextual_response(
                "Help me optimize this Python algorithm for better performance",
                user_context,
                []
            )
            
            # Verify intelligent model selection (technical query -> Claude)
            assert result["provider_used"] == "claude"
            assert result["model_used"] == "claude-3-sonnet-20240229"
            assert "optimize" in result["response"]
            assert result["response_time_ms"] == 1800
    
    @pytest.mark.asyncio 
    async def test_fallback_behavior_on_provider_failure(self):
        """Test fallback behavior when preferred provider fails"""
        
        with patch('app.routes.cape_ai.get_multi_provider_ai_service') as mock_multi:
            # Setup service to fail
            multi_ai = Mock()
            multi_ai.get_available_models.return_value = {"claude": ["claude-3-sonnet"]}
            multi_ai.get_model_config.return_value = Mock(provider=ModelProvider.CLAUDE)
            multi_ai.get_default_model.return_value = "claude-3-sonnet"
            multi_ai.generate_response = AsyncMock(side_effect=Exception("API temporarily unavailable"))
            mock_multi.return_value = multi_ai
            
            # Create service and test fallback
            service = CapeAIService()
            user_context = {"user_id": "test-user", "platform_context": {"area": "general"}}
            
            result = await service.generate_contextual_response(
                "Hello", user_context, []
            )
            
            # Should use fallback
            assert result["model_used"] == "fallback"
            assert result["provider_used"] == "local"
            assert "response" in result
            assert result["response_time_ms"] == 0


if __name__ == "__main__":
    pytest.main([__file__])
