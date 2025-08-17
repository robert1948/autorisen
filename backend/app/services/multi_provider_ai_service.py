"""
Multi-Provider AI Service for Task 2.1.1: Claude Integration
============================================================

Enhanced AI service supporting multiple providers:
- OpenAI (existing)
- Claude (Anthropic) - NEW
- Unified interface for seamless provider switching
- Provider-specific optimizations and configurations
- Task 2.4.2: Rate limiting integration for production security
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# Provider-specific imports
from openai import AsyncOpenAI
import anthropic
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    # Logger will be defined later

# Rate limiting integration - Task 2.4.2
try:
    from .ai_rate_limit_service import check_ai_rate_limit, RateLimitResult
    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False

from pydantic import BaseModel

from app.config import settings
from app.services.ai_performance_service import get_ai_performance_monitor, AIModelType
from app.services.conversation_context_service import get_context_service, ContextType
# Task 2.1.4: AI Personalization integration (imported lazily to avoid circular import)

logger = logging.getLogger(__name__)


class ModelProvider(str, Enum):
    """Available AI model providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"  # Added in Task 2.1.2


@dataclass
class AIModelConfig:
    """Configuration for AI models"""
    provider: ModelProvider
    model_name: str
    max_tokens: int
    temperature: float
    supports_streaming: bool
    cost_per_1k_prompt: float
    cost_per_1k_completion: float
    context_window: int


@dataclass
class AIProviderResponse:
    """Standardized response from AI providers"""
    content: str
    provider: ModelProvider
    model: str
    usage: Dict[str, int]
    response_time_ms: int
    finish_reason: str
    metadata: Dict[str, Any] = None


class MultiProviderAIService:
    """Enhanced AI service with multi-provider support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_monitor = get_ai_performance_monitor()
        
        # Initialize provider clients
        self.clients = {}
        self.model_configs = {}
        
        self._initialize_providers()
        self._setup_model_configurations()
    
    def _initialize_providers(self):
        """Initialize all available AI provider clients"""
        
        # OpenAI client (existing)
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.clients[ModelProvider.OPENAI] = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY
            )
            self.logger.info("OpenAI client initialized successfully")
        else:
            self.logger.warning("OpenAI API key not found - OpenAI models unavailable")
        
        # Claude (Anthropic) client - NEW
        claude_api_key = getattr(settings, 'CLAUDE_API_KEY', os.getenv('CLAUDE_API_KEY'))
        if claude_api_key:
            self.clients[ModelProvider.CLAUDE] = anthropic.AsyncAnthropic(
                api_key=claude_api_key
            )
            self.logger.info("Claude client initialized successfully")
        else:
            self.logger.warning("Claude API key not found - Claude models unavailable")
        
        # Gemini (Google) client - Task 2.1.2
        if GEMINI_AVAILABLE:
            gemini_api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY'))
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                self.clients[ModelProvider.GEMINI] = genai
                self.logger.info("Gemini client initialized successfully")
            else:
                self.logger.warning("Gemini API key not found - Gemini models unavailable")
        else:
            self.logger.warning("Google Generative AI library not found - Gemini models unavailable")
    
    def _setup_model_configurations(self):
        """Setup configurations for all supported models"""
        
        # OpenAI model configurations
        self.model_configs.update({
            "gpt-4": AIModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.03,
                cost_per_1k_completion=0.06,
                context_window=8192
            ),
            "gpt-4-turbo": AIModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4-turbo",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.01,
                cost_per_1k_completion=0.03,
                context_window=128000
            ),
            "gpt-3.5-turbo": AIModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.0015,
                cost_per_1k_completion=0.002,
                context_window=16385
            )
        })
        
        # Claude model configurations - NEW
        self.model_configs.update({
            "claude-3-opus": AIModelConfig(
                provider=ModelProvider.CLAUDE,
                model_name="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.015,
                cost_per_1k_completion=0.075,
                context_window=200000
            ),
            "claude-3-sonnet": AIModelConfig(
                provider=ModelProvider.CLAUDE,
                model_name="claude-3-sonnet-20240229",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.003,
                cost_per_1k_completion=0.015,
                context_window=200000
            ),
            "claude-3-haiku": AIModelConfig(
                provider=ModelProvider.CLAUDE,
                model_name="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                cost_per_1k_prompt=0.00025,
                cost_per_1k_completion=0.00125,
                context_window=200000
            )
        })
        
        # Gemini model configurations - Task 2.1.2
        if GEMINI_AVAILABLE:
            self.model_configs.update({
                "gemini-pro": AIModelConfig(
                    provider=ModelProvider.GEMINI,
                    model_name="gemini-pro",
                    max_tokens=8192,
                    temperature=0.7,
                    supports_streaming=True,
                    cost_per_1k_prompt=0.0005,
                    cost_per_1k_completion=0.0015,
                    context_window=32768
                ),
                "gemini-pro-vision": AIModelConfig(
                    provider=ModelProvider.GEMINI,
                    model_name="gemini-pro-vision",
                    max_tokens=4096,
                    temperature=0.7,
                    supports_streaming=False,
                    cost_per_1k_prompt=0.00025,
                    cost_per_1k_completion=0.00025,
                    context_window=16384
                ),
                "gemini-1.5-pro": AIModelConfig(
                    provider=ModelProvider.GEMINI,
                    model_name="gemini-1.5-pro",
                    max_tokens=8192,
                    temperature=0.7,
                    supports_streaming=True,
                    cost_per_1k_prompt=0.0035,
                    cost_per_1k_completion=0.0105,
                    context_window=1048576
                )
            })
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models grouped by provider"""
        
        available = {}
        
        for model_key, config in self.model_configs.items():
            provider_name = config.provider.value
            if config.provider in self.clients:
                if provider_name not in available:
                    available[provider_name] = []
                available[provider_name].append(model_key)
        
        return available
    
    def get_model_config(self, model_name: str) -> Optional[AIModelConfig]:
        """Get configuration for a specific model"""
        return self.model_configs.get(model_name)
    
    def get_default_model(self, provider: Optional[ModelProvider] = None) -> str:
        """Get the default model for a provider or overall default"""
        
        # Provider-specific defaults
        if provider == ModelProvider.OPENAI:
            return "gpt-4"
        elif provider == ModelProvider.CLAUDE:
            return "claude-3-sonnet"
        elif provider == ModelProvider.GEMINI:
            return "gemini-pro"
        
        # Overall default - prefer Claude Sonnet for better performance/cost ratio
        if ModelProvider.CLAUDE in self.clients:
            return "claude-3-sonnet"
        elif ModelProvider.GEMINI in self.clients:
            return "gemini-pro"
        elif ModelProvider.OPENAI in self.clients:
            return "gpt-4"
        
        # Fallback
        available_models = list(self.model_configs.keys())
        return available_models[0] if available_models else "gpt-3.5-turbo"
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        use_context: bool = True,
        use_personalization: bool = True,
        **kwargs
    ) -> AIProviderResponse:
        """
        Generate AI response using specified or default model
        
        Enhanced with Task 2.1.3: Context Enhancement
        - Automatic conversation context integration
        - User preference-aware model selection
        - Context-aware response generation
        
        Enhanced with Task 2.1.4: AI Personalization
        - User personality profile integration
        - Personalized prompt adaptation
        - Dynamic parameter adjustment
        """
        
        # Initialize services
        context_service = await get_context_service()
        
        # Initialize personalization service (lazy import to avoid circular dependency)
        personalization_service = None
        if use_personalization and user_id:
            try:
                from app.services.ai_personalization_service import get_personalization_service
                personalization_service = await get_personalization_service()
            except Exception as e:
                logger.warning(f"Failed to initialize personalization service: {e}")
        
        # Handle conversation context if enabled
        enhanced_messages = messages.copy()
        context_metadata = {}
        
        if use_context and user_id and conversation_id:
            try:
                # Get conversation context
                ai_context, context_metadata = await context_service.generate_context_for_ai(
                    conversation_id=conversation_id,
                    max_context_messages=8,  # Keep reasonable context window
                    include_summary=True
                )
                
                # Merge with current messages, avoiding duplicates
                if ai_context:
                    # Find the last user message in current messages
                    current_user_message = None
                    for msg in reversed(messages):
                        if msg.get('role') == 'user':
                            current_user_message = msg
                            break
                    
                    # If context doesn't end with the same user message, merge
                    if ai_context and current_user_message:
                        last_context_msg = ai_context[-1] if ai_context else None
                        if (not last_context_msg or 
                            last_context_msg.get('role') != 'user' or 
                            last_context_msg.get('content') != current_user_message.get('content')):
                            enhanced_messages = ai_context + messages
                        else:
                            # Replace the last context message with current
                            enhanced_messages = ai_context[:-1] + messages
                    else:
                        enhanced_messages = ai_context + messages
                
                logger.debug(f"Enhanced messages with context: {len(ai_context)} context + {len(messages)} new = {len(enhanced_messages)} total")
                
            except Exception as e:
                logger.warning(f"Failed to load conversation context: {e}")
                # Continue without context
        
        # Apply personalization to messages
        if personalization_service and user_id and enhanced_messages:
            try:
                # Personalize the system message or first assistant message
                for i, msg in enumerate(enhanced_messages):
                    if msg.get('role') in ['system', 'assistant']:
                        # Find a suitable message to personalize
                        if 'You are' in msg.get('content', '') or msg.get('role') == 'system':
                            personalized_content = await personalization_service.personalize_prompt(
                                base_prompt=msg['content'],
                                user_id=user_id,
                                context_type='general_chat'
                            )
                            enhanced_messages[i] = {**msg, 'content': personalized_content}
                            logger.debug(f"Applied personalization to message {i}")
                            break
                else:
                    # If no system message, add a personalized system message
                    if enhanced_messages and enhanced_messages[0].get('role') != 'system':
                        base_system_prompt = "You are a helpful AI assistant."
                        personalized_prompt = await personalization_service.personalize_prompt(
                            base_prompt=base_system_prompt,
                            user_id=user_id,
                            context_type='general_chat'
                        )
                        enhanced_messages.insert(0, {'role': 'system', 'content': personalized_prompt})
                        logger.debug("Added personalized system message")
                        
            except Exception as e:
                logger.warning(f"Failed to apply personalization to messages: {e}")
        
        # Use default model if none specified, considering user preferences
        if not model:
            # Check personalization service for model preference
            if personalization_service and user_id:
                try:
                    profile = await personalization_service.get_personality_profile(user_id)
                    if profile and profile.preferred_models:
                        preferred_model = profile.preferred_models[0]
                        if self.get_model_config(preferred_model):
                            model = preferred_model
                            logger.debug(f"Using personalized preferred model: {model}")
                except Exception as e:
                    logger.warning(f"Failed to get personalized model preference: {e}")
            
            # Fallback to context-based preference
            if not model and context_metadata and context_metadata.get('user_preferences', {}).get('preferred_ai_model'):
                preferred_model = context_metadata['user_preferences']['preferred_ai_model']
                if self.get_model_config(preferred_model):
                    model = preferred_model
                    logger.debug(f"Using context preferred model: {model}")
            
            if not model:
                model = self.get_default_model()
        
        # Get model configuration
        config = self.get_model_config(model)
        if not config:
            raise ValueError(f"Model '{model}' not found or not configured")
        
        # Check if provider client is available
        if config.provider not in self.clients:
            raise ValueError(f"Provider '{config.provider.value}' not available")
        
        # Use config defaults if parameters not specified
        temperature = temperature if temperature is not None else config.temperature
        max_tokens = max_tokens if max_tokens is not None else config.max_tokens
        
        # Apply personalization to AI parameters
        if personalization_service and user_id:
            try:
                base_params = {
                    'temperature': temperature,
                    'max_tokens': max_tokens,
                    'model': model
                }
                
                personalized_params = await personalization_service.adapt_ai_parameters(
                    user_id=user_id,
                    base_params=base_params
                )
                
                temperature = personalized_params.get('temperature', temperature)
                max_tokens = personalized_params.get('max_tokens', max_tokens)
                
                # Log personalization applied
                if personalized_params != base_params:
                    logger.debug(f"Applied personalized parameters for user {user_id}: {personalized_params}")
                    
            except Exception as e:
                logger.warning(f"Failed to apply personalized parameters: {e}")
        
        # Adjust parameters based on user preferences (legacy support)
        if context_metadata and context_metadata.get('user_preferences'):
            prefs = context_metadata['user_preferences']
            
            # Adjust response style based on communication preference
            if prefs.get('communication_style') == 'casual' and temperature is not None:
                temperature = min(temperature + 0.1, 1.0)  # Slightly more creative
            elif prefs.get('communication_style') == 'formal' and temperature is not None:
                temperature = max(temperature - 0.1, 0.0)  # More deterministic
        
        # Store user message in context if enabled
        if use_context and user_id and conversation_id and messages:
            try:
                # Find the user message to store
                user_message = None
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        user_message = msg
                        break
                
                if user_message:
                    await context_service.add_message(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message_type=ContextType.USER_MESSAGE,
                        content=user_message['content'],
                        metadata={'original_messages_count': len(messages)}
                    )
            except Exception as e:
                logger.warning(f"Failed to store user message in context: {e}")
        
        # Route to appropriate provider
        start_time = asyncio.get_event_loop().time()
        
        # Task 2.4.2: Rate limiting check before AI generation
        if RATE_LIMITING_AVAILABLE and user_id:
            try:
                # Estimate token count for rate limiting (basic estimation)
                estimated_tokens = sum(len(msg.get('content', '').split()) for msg in enhanced_messages) * 1.3
                estimated_tokens = int(estimated_tokens)  # Convert to int
                
                # Get user tier (default to free for now)
                user_tier = kwargs.get('user_tier', 'free')  # TODO: Get from user service
                
                # Check rate limits
                rate_limit_result = await check_ai_rate_limit(
                    user_id=user_id,
                    provider=config.provider.value.lower(),
                    user_tier=user_tier,
                    token_count=estimated_tokens
                )
                
                if not rate_limit_result.allowed:
                    logger.warning(f"Rate limit exceeded for user {user_id}: {rate_limit_result.error_message}")
                    # Return rate limit error response
                    return AIProviderResponse(
                        provider=config.provider,
                        model=config.model,
                        content=f"Rate limit exceeded. {rate_limit_result.error_message}",
                        token_usage=AITokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                        response_time_ms=0,
                        is_error=True,
                        error_message=rate_limit_result.error_message,
                        metadata={
                            "rate_limit_exceeded": True,
                            "retry_after": rate_limit_result.retry_after,
                            "reset_time": rate_limit_result.reset_time.isoformat() if rate_limit_result.reset_time else None
                        }
                    )
                
                logger.debug(f"Rate limit check passed for user {user_id}: {rate_limit_result.remaining} remaining")
                
            except Exception as e:
                logger.warning(f"Rate limiting check failed, proceeding: {e}")
        
        try:
            if config.provider == ModelProvider.OPENAI:
                response = await self._generate_openai_response(
                    enhanced_messages, config, temperature, max_tokens, **kwargs
                )
            elif config.provider == ModelProvider.CLAUDE:
                response = await self._generate_claude_response(
                    enhanced_messages, config, temperature, max_tokens, **kwargs
                )
            elif config.provider == ModelProvider.GEMINI:
                response = await self._generate_gemini_response(
                    enhanced_messages, config, temperature, max_tokens, **kwargs
                )
            else:
                raise ValueError(f"Provider '{config.provider.value}' not implemented")
            
            end_time = asyncio.get_event_loop().time()
            response.response_time_ms = int((end_time - start_time) * 1000)
            
            # Store AI response in context if enabled
            if use_context and user_id and conversation_id:
                try:
                    await context_service.add_message(
                        user_id=user_id,
                        conversation_id=conversation_id,
                        message_type=ContextType.AI_RESPONSE,
                        content=response.content,
                        metadata={
                            'context_messages_used': len(enhanced_messages),
                            'personalization_applied': use_personalization and personalization_service is not None,
                            'model_selected_by_personalization': model if personalization_service else None
                        },
                        ai_provider=response.provider.value,
                        ai_model=response.model,
                        tokens_used=response.usage,
                        response_time_ms=response.response_time_ms
                    )
                except Exception as e:
                    logger.warning(f"Failed to store AI response in context: {e}")
            
            # Update personalization profile based on successful interaction
            if personalization_service and user_id:
                try:
                    interaction_data = {
                        'response_time': response.response_time_ms,
                        'model_used': response.model,
                        'provider_used': response.provider.value,
                        'tokens_used': response.usage.get('total_tokens', 0),
                        'positive_feedback': True,  # Assume positive for successful generation
                        'topic': 'general'  # Could be enhanced with topic detection
                    }
                    
                    await personalization_service.update_profile_from_interaction(
                        user_id=user_id,
                        interaction_data=interaction_data
                    )
                except Exception as e:
                    logger.warning(f"Failed to update personalization profile: {e}")
            
            # Record performance metrics
            self.performance_monitor.record_ai_request(
                provider=AIModelType(config.provider.value),
                model=config.model_name,
                endpoint=f"/{config.provider.value}/chat",
                prompt_tokens=response.usage.get('prompt_tokens', 0),
                completion_tokens=response.usage.get('completion_tokens', 0),
                response_time_ms=response.response_time_ms,
                success=True,
                user_id=user_id,
                response_length=len(response.content),
                quality_score=None  # Could add quality assessment later
            )
            
            return response
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Record failed request
            self.performance_monitor.record_ai_request(
                provider=AIModelType(config.provider.value),
                model=config.model_name,
                endpoint=f"/{config.provider.value}/chat",
                prompt_tokens=0,
                completion_tokens=0,
                response_time_ms=response_time_ms,
                success=False,
                user_id=user_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            self.logger.error(f"AI generation failed for model {model}: {str(e)}")
            raise
    
    async def _generate_openai_response(
        self,
        messages: List[Dict[str, str]],
        config: AIModelConfig,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> AIProviderResponse:
        """Generate response using OpenAI API"""
        
        client = self.clients[ModelProvider.OPENAI]
        
        response = await client.chat.completions.create(
            model=config.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        return AIProviderResponse(
            content=response.choices[0].message.content,
            provider=ModelProvider.OPENAI,
            model=config.model_name,
            usage={
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            response_time_ms=0,  # Will be set by caller
            finish_reason=response.choices[0].finish_reason,
            metadata={
                'response_id': response.id,
                'created': response.created,
                'model': response.model
            }
        )
    
    async def _generate_claude_response(
        self,
        messages: List[Dict[str, str]],
        config: AIModelConfig,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> AIProviderResponse:
        """Generate response using Claude (Anthropic) API"""
        
        client = self.clients[ModelProvider.CLAUDE]
        
        # Convert OpenAI-style messages to Claude format
        claude_messages = self._convert_messages_to_claude_format(messages)
        
        # Extract system message if present
        system_message = None
        if claude_messages and claude_messages[0].get('role') == 'system':
            system_message = claude_messages.pop(0)['content']
        
        # Create Claude request
        request_params = {
            'model': config.model_name,
            'messages': claude_messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        if system_message:
            request_params['system'] = system_message
        
        response = await client.messages.create(**request_params)
        
        # Extract usage information
        usage = {
            'prompt_tokens': response.usage.input_tokens,
            'completion_tokens': response.usage.output_tokens,
            'total_tokens': response.usage.input_tokens + response.usage.output_tokens
        }
        
        return AIProviderResponse(
            content=response.content[0].text,
            provider=ModelProvider.CLAUDE,
            model=config.model_name,
            usage=usage,
            response_time_ms=0,  # Will be set by caller
            finish_reason=response.stop_reason,
            metadata={
                'response_id': response.id,
                'model': response.model,
                'stop_sequence': response.stop_sequence
            }
        )
    
    def _convert_messages_to_claude_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert OpenAI-style messages to Claude format"""
        
        claude_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Claude uses 'user' and 'assistant' roles, system messages handled separately
            if role in ['user', 'assistant', 'system']:
                claude_messages.append({
                    'role': role,
                    'content': content
                })
            else:
                # Convert unknown roles to user messages
                claude_messages.append({
                    'role': 'user',
                    'content': content
                })
        
        return claude_messages
    
    async def _generate_gemini_response(
        self,
        messages: List[Dict[str, str]],
        config: AIModelConfig,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> AIProviderResponse:
        """Generate response using Google Gemini models"""
        
        client = self.clients[ModelProvider.GEMINI]
        
        # Create Gemini model instance
        model = client.GenerativeModel(
            model_name=config.model_name,
            generation_config=client.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        # Convert messages to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        try:
            # Generate response
            if len(gemini_messages) == 1:
                # Single message - use generate_content
                response = await model.generate_content_async(gemini_messages[0])
            else:
                # Multiple messages - start chat
                chat = model.start_chat(history=gemini_messages[:-1])
                response = await chat.send_message_async(gemini_messages[-1])
            
            # Extract response content
            if response.text:
                content = response.text.strip()
            else:
                content = "I'm sorry, I couldn't generate a response."
            
            # Calculate token usage (approximate for Gemini)
            prompt_tokens = sum(len(msg.split()) for msg in gemini_messages if isinstance(msg, str))
            completion_tokens = len(content.split())
            
            return AIProviderResponse(
                content=content,
                provider=ModelProvider.GEMINI,
                model=config.model_name,
                usage={
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': prompt_tokens + completion_tokens
                },
                response_time_ms=0,  # Will be set by caller
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else "stop",
                metadata={
                    'safety_ratings': [
                        {
                            'category': rating.category.name,
                            'probability': rating.probability.name
                        }
                        for rating in response.candidates[0].safety_ratings
                    ] if response.candidates else []
                }
            )
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[str]:
        """Convert standard messages to Gemini format"""
        
        gemini_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                # Gemini doesn't have system role - prepend to first user message
                gemini_messages.append(f"System: {content}")
            elif role == 'assistant':
                # Gemini uses model responses in chat history
                gemini_messages.append(content)
            else:  # user or other
                gemini_messages.append(content)
        
        return gemini_messages
    
    async def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all AI providers"""
        
        status = {}
        
        for provider in ModelProvider:
            provider_status = {
                'available': provider in self.clients,
                'models': [],
                'default_model': None
            }
            
            if provider in self.clients:
                # Get models for this provider
                provider_models = [
                    model_key for model_key, config in self.model_configs.items()
                    if config.provider == provider
                ]
                provider_status['models'] = provider_models
                provider_status['default_model'] = self.get_default_model(provider)
            
            status[provider.value] = provider_status
        
        return status


# Global service instance
_multi_provider_service = None

def get_multi_provider_ai_service() -> MultiProviderAIService:
    """Get the global multi-provider AI service instance"""
    global _multi_provider_service
    
    if _multi_provider_service is None:
        _multi_provider_service = MultiProviderAIService()
    
    return _multi_provider_service


# Export for other modules
__all__ = [
    'MultiProviderAIService',
    'ModelProvider', 
    'AIModelConfig',
    'AIProviderResponse',
    'get_multi_provider_ai_service'
]
