"""
Tests for Multi-Provider AI Service (Task 2.1.1: Claude Integration)
===================================================================

Test suite covering:
- Multi-provider initialization and configuration
- Model selection and intelligent routing
- Claude API integration
- OpenAI compatibility
- Error handling and fallbacks
- Performance monitoring integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from app.services.multi_provider_ai_service import (
    MultiProviderAIService,
    ModelProvider,
    AIModelConfig,
    AIProviderResponse,
    get_multi_provider_ai_service
)
from app.services.ai_performance_service import AIProvider


class TestMultiProviderAIService:
    """Test cases for the multi-provider AI service"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings with API keys"""
        with patch('app.services.multi_provider_ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-openai-key"
            mock_settings.CLAUDE_API_KEY = "test-claude-key"
            yield mock_settings
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock AI performance monitor"""
        with patch('app.services.multi_provider_ai_service.get_ai_performance_monitor') as mock_monitor:
            monitor = Mock()
            monitor.record_ai_request = Mock()
            mock_monitor.return_value = monitor
            yield monitor
    
    @pytest.fixture
    def service(self, mock_settings, mock_performance_monitor):
        """Create service instance with mocked dependencies"""
        with patch('app.services.multi_provider_ai_service.AsyncOpenAI') as mock_openai, \
             patch('app.services.multi_provider_ai_service.anthropic.AsyncAnthropic') as mock_claude:
            
            # Mock OpenAI client
            openai_client = Mock()
            mock_openai.return_value = openai_client
            
            # Mock Claude client
            claude_client = Mock()
            mock_claude.return_value = claude_client
            
            service = MultiProviderAIService()
            service.clients[ModelProvider.OPENAI] = openai_client
            service.clients[ModelProvider.CLAUDE] = claude_client
            
            yield service
    
    def test_service_initialization(self, mock_settings, mock_performance_monitor):
        """Test service initializes with correct providers"""
        
        with patch('app.services.multi_provider_ai_service.AsyncOpenAI') as mock_openai, \
             patch('app.services.multi_provider_ai_service.anthropic.AsyncAnthropic') as mock_claude:
            
            service = MultiProviderAIService()
            
            # Verify clients are initialized
            mock_openai.assert_called_once_with(api_key="test-openai-key")
            mock_claude.assert_called_once_with(api_key="test-claude-key")
    
    def test_model_configurations(self, service):
        """Test that all models are properly configured"""
        
        # Check OpenAI models
        assert "gpt-4" in service.model_configs
        assert "gpt-4-turbo" in service.model_configs
        assert "gpt-3.5-turbo" in service.model_configs
        
        # Check Claude models
        assert "claude-3-opus" in service.model_configs
        assert "claude-3-sonnet" in service.model_configs
        assert "claude-3-haiku" in service.model_configs
        
        # Verify configuration details
        gpt4_config = service.model_configs["gpt-4"]
        assert gpt4_config.provider == ModelProvider.OPENAI
        assert gpt4_config.context_window == 8192
        
        claude_sonnet_config = service.model_configs["claude-3-sonnet"]
        assert claude_sonnet_config.provider == ModelProvider.CLAUDE
        assert claude_sonnet_config.context_window == 200000
    
    def test_get_available_models(self, service):
        """Test available models retrieval"""
        
        available = service.get_available_models()
        
        assert "openai" in available
        assert "claude" in available
        assert "gpt-4" in available["openai"]
        assert "claude-3-sonnet" in available["claude"]
    
    def test_get_default_model(self, service):
        """Test default model selection"""
        
        # Test provider-specific defaults
        openai_default = service.get_default_model(ModelProvider.OPENAI)
        assert openai_default == "gpt-4"
        
        claude_default = service.get_default_model(ModelProvider.CLAUDE)
        assert claude_default == "claude-3-sonnet"
        
        # Test overall default (should prefer Claude)
        overall_default = service.get_default_model()
        assert overall_default == "claude-3-sonnet"
    
    @pytest.mark.asyncio
    async def test_openai_response_generation(self, service):
        """Test OpenAI response generation"""
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response from OpenAI"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        mock_response.model = "gpt-4"
        
        # Configure mock client
        service.clients[ModelProvider.OPENAI].chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Test message
        messages = [{"role": "user", "content": "Hello"}]
        
        # Generate response
        response = await service.generate_response(messages, model="gpt-4", user_id="test-user")
        
        # Verify response
        assert isinstance(response, AIProviderResponse)
        assert response.content == "Test response from OpenAI"
        assert response.provider == ModelProvider.OPENAI
        assert response.model == "gpt-4"
        assert response.usage["prompt_tokens"] == 10
        assert response.usage["completion_tokens"] == 5
        assert response.finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_claude_response_generation(self, service):
        """Test Claude response generation"""
        
        # Mock Claude response
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response from Claude"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 12
        mock_response.usage.output_tokens = 8
        mock_response.id = "test-claude-id"
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.stop_sequence = None
        
        # Configure mock client
        service.clients[ModelProvider.CLAUDE].messages.create = AsyncMock(return_value=mock_response)
        
        # Test message
        messages = [{"role": "user", "content": "Hello Claude"}]
        
        # Generate response
        response = await service.generate_response(messages, model="claude-3-sonnet", user_id="test-user")
        
        # Verify response
        assert isinstance(response, AIProviderResponse)
        assert response.content == "Test response from Claude"
        assert response.provider == ModelProvider.CLAUDE
        assert response.model == "claude-3-sonnet-20240229"
        assert response.usage["prompt_tokens"] == 12
        assert response.usage["completion_tokens"] == 8
        assert response.finish_reason == "end_turn"
    
    @pytest.mark.asyncio
    async def test_claude_message_conversion(self, service):
        """Test OpenAI to Claude message format conversion"""
        
        # Test messages with system prompt
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        converted = service._convert_messages_to_claude_format(messages)
        
        # System message should be handled separately
        assert len(converted) == 4
        assert converted[0]["role"] == "system"
        assert converted[1]["role"] == "user"
        assert converted[2]["role"] == "assistant"
        assert converted[3]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service, mock_performance_monitor):
        """Test error handling and monitoring"""
        
        # Configure client to raise exception
        service.clients[ModelProvider.OPENAI].chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Should raise exception and record failure
        with pytest.raises(Exception, match="API Error"):
            await service.generate_response(messages, model="gpt-4", user_id="test-user")
        
        # Verify error was recorded
        mock_performance_monitor.record_ai_request.assert_called()
        call_args = mock_performance_monitor.record_ai_request.call_args
        assert call_args[1]["success"] is False
        assert call_args[1]["error_type"] == "Exception"
        assert call_args[1]["error_message"] == "API Error"
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, service, mock_performance_monitor):
        """Test performance monitoring integration"""
        
        # Mock successful OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.id = "test-id"
        mock_response.created = 1234567890
        mock_response.model = "gpt-4"
        
        service.clients[ModelProvider.OPENAI].chat.completions.create = AsyncMock(return_value=mock_response)
        
        messages = [{"role": "user", "content": "Test monitoring"}]
        
        # Generate response
        await service.generate_response(messages, model="gpt-4", user_id="test-user")
        
        # Verify monitoring was called
        mock_performance_monitor.record_ai_request.assert_called()
        call_args = mock_performance_monitor.record_ai_request.call_args
        
        assert call_args[1]["provider"] == AIProvider.OPENAI
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["success"] is True
        assert call_args[1]["user_id"] == "test-user"
        assert call_args[1]["prompt_tokens"] == 10
        assert call_args[1]["completion_tokens"] == 5
    
    @pytest.mark.asyncio
    async def test_provider_status(self, service):
        """Test provider status reporting"""
        
        status = await service.get_provider_status()
        
        assert "openai" in status
        assert "claude" in status
        
        # Check OpenAI status
        openai_status = status["openai"]
        assert openai_status["available"] is True
        assert "gpt-4" in openai_status["models"]
        assert openai_status["default_model"] == "gpt-4"
        
        # Check Claude status
        claude_status = status["claude"]
        assert claude_status["available"] is True
        assert "claude-3-sonnet" in claude_status["models"]
        assert claude_status["default_model"] == "claude-3-sonnet"
    
    def test_invalid_model_handling(self, service):
        """Test handling of invalid model requests"""
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Should raise ValueError for invalid model
        with pytest.raises(ValueError, match="Model 'invalid-model' not found"):
            asyncio.run(service.generate_response(messages, model="invalid-model"))
    
    def test_unavailable_provider_handling(self, service):
        """Test handling when provider is unavailable"""
        
        # Remove Claude client to simulate unavailable provider
        del service.clients[ModelProvider.CLAUDE]
        
        messages = [{"role": "user", "content": "Test"}]
        
        # Should raise ValueError for unavailable provider
        with pytest.raises(ValueError, match="Provider 'claude' not available"):
            asyncio.run(service.generate_response(messages, model="claude-3-sonnet"))


class TestGlobalServiceInstance:
    """Test the global service instance functionality"""
    
    def test_singleton_pattern(self):
        """Test that get_multi_provider_ai_service returns singleton"""
        
        with patch('app.services.multi_provider_ai_service.MultiProviderAIService') as MockService:
            mock_instance = Mock()
            MockService.return_value = mock_instance
            
            # First call should create instance
            service1 = get_multi_provider_ai_service()
            
            # Second call should return same instance
            service2 = get_multi_provider_ai_service()
            
            assert service1 is service2
            MockService.assert_called_once()


class TestModelConfigurations:
    """Test model configuration details"""
    
    def test_openai_model_configs(self):
        """Test OpenAI model configurations are correct"""
        
        with patch('app.services.multi_provider_ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.CLAUDE_API_KEY = "test-key"
            
            with patch('app.services.multi_provider_ai_service.AsyncOpenAI'), \
                 patch('app.services.multi_provider_ai_service.anthropic.AsyncAnthropic'), \
                 patch('app.services.multi_provider_ai_service.get_ai_performance_monitor'):
                
                service = MultiProviderAIService()
                
                # Test GPT-4 config
                gpt4_config = service.model_configs["gpt-4"]
                assert gpt4_config.provider == ModelProvider.OPENAI
                assert gpt4_config.model_name == "gpt-4"
                assert gpt4_config.max_tokens == 4096
                assert gpt4_config.supports_streaming is True
                assert gpt4_config.context_window == 8192
                
                # Test GPT-4 Turbo config
                gpt4_turbo_config = service.model_configs["gpt-4-turbo"]
                assert gpt4_turbo_config.context_window == 128000
                assert gpt4_turbo_config.cost_per_1k_prompt == 0.01
    
    def test_claude_model_configs(self):
        """Test Claude model configurations are correct"""
        
        with patch('app.services.multi_provider_ai_service.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.CLAUDE_API_KEY = "test-key"
            
            with patch('app.services.multi_provider_ai_service.AsyncOpenAI'), \
                 patch('app.services.multi_provider_ai_service.anthropic.AsyncAnthropic'), \
                 patch('app.services.multi_provider_ai_service.get_ai_performance_monitor'):
                
                service = MultiProviderAIService()
                
                # Test Claude Opus config
                opus_config = service.model_configs["claude-3-opus"]
                assert opus_config.provider == ModelProvider.CLAUDE
                assert opus_config.model_name == "claude-3-opus-20240229"
                assert opus_config.context_window == 200000
                assert opus_config.cost_per_1k_prompt == 0.015
                
                # Test Claude Haiku config (fastest/cheapest)
                haiku_config = service.model_configs["claude-3-haiku"]
                assert haiku_config.cost_per_1k_prompt == 0.00025
                assert haiku_config.cost_per_1k_completion == 0.00125


# Integration Tests
class TestMultiProviderIntegration:
    """Integration tests for multi-provider functionality"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_openai_flow(self):
        """Test complete OpenAI flow"""
        
        with patch('app.services.multi_provider_ai_service.settings') as mock_settings, \
             patch('app.services.multi_provider_ai_service.AsyncOpenAI') as mock_openai_class, \
             patch('app.services.multi_provider_ai_service.get_ai_performance_monitor') as mock_monitor:
            
            # Setup mocks
            mock_settings.OPENAI_API_KEY = "test-key"
            mock_settings.CLAUDE_API_KEY = None
            
            mock_client = Mock()
            mock_openai_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Hello from OpenAI!"
            mock_response.choices[0].finish_reason = "stop"
            mock_response.usage.prompt_tokens = 5
            mock_response.usage.completion_tokens = 3
            mock_response.usage.total_tokens = 8
            mock_response.id = "test-id"
            mock_response.created = 1234567890
            mock_response.model = "gpt-4"
            
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            monitor = Mock()
            monitor.record_ai_request = Mock()
            mock_monitor.return_value = monitor
            
            # Test the flow
            service = MultiProviderAIService()
            messages = [{"role": "user", "content": "Hello"}]
            
            response = await service.generate_response(messages, model="gpt-4")
            
            assert response.content == "Hello from OpenAI!"
            assert response.provider == ModelProvider.OPENAI
            monitor.record_ai_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_end_to_end_claude_flow(self):
        """Test complete Claude flow"""
        
        with patch('app.services.multi_provider_ai_service.settings') as mock_settings, \
             patch('app.services.multi_provider_ai_service.anthropic.AsyncAnthropic') as mock_claude_class, \
             patch('app.services.multi_provider_ai_service.get_ai_performance_monitor') as mock_monitor:
            
            # Setup mocks
            mock_settings.OPENAI_API_KEY = None
            mock_settings.CLAUDE_API_KEY = "test-claude-key"
            
            mock_client = Mock()
            mock_claude_class.return_value = mock_client
            
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Hello from Claude!"
            mock_response.stop_reason = "end_turn"
            mock_response.usage.input_tokens = 6
            mock_response.usage.output_tokens = 4
            mock_response.id = "claude-test-id"
            mock_response.model = "claude-3-sonnet-20240229"
            mock_response.stop_sequence = None
            
            mock_client.messages.create = AsyncMock(return_value=mock_response)
            
            monitor = Mock()
            monitor.record_ai_request = Mock()
            mock_monitor.return_value = monitor
            
            # Test the flow
            service = MultiProviderAIService()
            messages = [{"role": "user", "content": "Hello Claude"}]
            
            response = await service.generate_response(messages, model="claude-3-sonnet")
            
            assert response.content == "Hello from Claude!"
            assert response.provider == ModelProvider.CLAUDE
            monitor.record_ai_request.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
