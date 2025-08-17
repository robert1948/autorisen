"""
Task 2.2.3: Context-Aware AI Responses - API Routes
REST API endpoints for context-aware AI response generation and analysis.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..services.context_aware_ai import (
    context_aware_ai_service,
    ContextType,
    ResponseStrategy
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/context-ai", tags=["Context-Aware AI"])

# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UserProfile(BaseModel):
    """User profile model"""
    user_id: str = Field(..., description="Unique user identifier")
    communication_style: str = Field(default="balanced", description="User's communication style")
    learning_style: str = Field(default="mixed", description="User's learning style")
    expertise_level: str = Field(default="intermediate", description="User's expertise level")
    interests: List[str] = Field(default_factory=list, description="User interests")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ContextAwareRequest(BaseModel):
    """Request for context-aware AI response"""
    query: str = Field(..., description="User query")
    user_profile: UserProfile = Field(..., description="User profile information")
    conversation_history: List[ChatMessage] = Field(default_factory=list, description="Recent conversation history")
    additional_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context information")
    preferred_strategy: Optional[str] = Field(default=None, description="Preferred response strategy")

class ContextAnalysisRequest(BaseModel):
    """Request for context analysis"""
    user_id: str = Field(..., description="User ID")
    conversation_history: List[ChatMessage] = Field(..., description="Conversation history to analyze")

class ResponseGenerationResult(BaseModel):
    """Result of context-aware response generation"""
    prompt: str = Field(..., description="Generated contextual prompt")
    strategy: str = Field(..., description="Response strategy used")
    context_summary: str = Field(..., description="Summary of context used")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")
    personalization_applied: bool = Field(..., description="Whether personalization was applied")
    confidence_score: float = Field(..., description="Confidence score for the response")
    response_context: Dict[str, Any] = Field(..., description="Full response context")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    quality_indicators: Dict[str, Any] = Field(..., description="Quality indicators")
    suggestions: List[str] = Field(..., description="Follow-up suggestions")
    from_cache: bool = Field(..., description="Whether response was served from cache")

class ContextAnalysisResult(BaseModel):
    """Result of context analysis"""
    conversation_analysis: Dict[str, Any] = Field(..., description="Conversation context analysis")
    user_analysis: Dict[str, Any] = Field(..., description="User context analysis")
    recommendations: List[str] = Field(..., description="Context improvement recommendations")
    quality_score: float = Field(..., description="Overall context quality score")

class PerformanceMetrics(BaseModel):
    """Service performance metrics"""
    total_requests: int = Field(..., description="Total requests processed")
    cache_hit_rate: str = Field(..., description="Cache hit rate percentage")
    average_processing_time_ms: float = Field(..., description="Average processing time")
    average_context_quality: str = Field(..., description="Average context quality score")
    cache_size: int = Field(..., description="Current cache size")
    service_status: str = Field(..., description="Service operational status")

# API Endpoints

@router.post("/generate-response", response_model=ResponseGenerationResult)
async def generate_context_aware_response(request: ContextAwareRequest) -> ResponseGenerationResult:
    """
    Generate a context-aware AI response using conversation history and user profile.
    
    This endpoint analyzes the user's profile, conversation history, and current query
    to generate an optimally contextualized prompt for AI response generation.
    """
    try:
        # Convert Pydantic models to dictionaries
        user_profile_dict = request.user_profile.dict()
        conversation_history_dict = [msg.dict() for msg in request.conversation_history]
        
        # Generate context-aware response
        response_data = await context_aware_ai_service.generate_response(
            query=request.query,
            user_profile=user_profile_dict,
            conversation_history=conversation_history_dict,
            additional_context=request.additional_context
        )
        
        return ResponseGenerationResult(**response_data)
        
    except Exception as e:
        logger.error(f"Error generating context-aware response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate context-aware response: {str(e)}"
        )

@router.post("/analyze-context", response_model=ContextAnalysisResult)
async def analyze_conversation_context(request: ContextAnalysisRequest) -> ContextAnalysisResult:
    """
    Analyze conversation context to understand user patterns and provide insights.
    
    This endpoint provides detailed analysis of conversation patterns, user behavior,
    and context quality to help improve AI interactions.
    """
    try:
        # Convert conversation history to dictionaries
        conversation_history_dict = [msg.dict() for msg in request.conversation_history]
        
        # Perform context analysis
        analysis_result = await context_aware_ai_service.get_context_analysis(
            user_id=request.user_id,
            conversation_history=conversation_history_dict
        )
        
        return ContextAnalysisResult(**analysis_result)
        
    except Exception as e:
        logger.error(f"Error analyzing context: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze context: {str(e)}"
        )

@router.get("/performance-metrics", response_model=PerformanceMetrics)
async def get_performance_metrics() -> PerformanceMetrics:
    """
    Get performance metrics for the context-aware AI service.
    
    Returns statistics about request processing, cache performance,
    and overall service health.
    """
    try:
        metrics = await context_aware_ai_service.get_performance_metrics()
        return PerformanceMetrics(**metrics)
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/strategies", response_model=List[Dict[str, str]])
async def get_response_strategies() -> List[Dict[str, str]]:
    """
    Get available response strategies and their descriptions.
    
    Returns a list of all available response strategies that can be used
    for context-aware AI response generation.
    """
    try:
        strategies = [
            {
                "name": ResponseStrategy.ADAPTIVE.value,
                "description": "Adapts to user style and context dynamically"
            },
            {
                "name": ResponseStrategy.CONVERSATIONAL.value,
                "description": "Maintains natural conversation flow"
            },
            {
                "name": ResponseStrategy.ANALYTICAL.value,
                "description": "Provides data-driven, logical responses"
            },
            {
                "name": ResponseStrategy.CREATIVE.value,
                "description": "Uses creative and engaging approaches"
            },
            {
                "name": ResponseStrategy.PROFESSIONAL.value,
                "description": "Maintains professional business tone"
            },
            {
                "name": ResponseStrategy.EDUCATIONAL.value,
                "description": "Focuses on teaching and explanation"
            }
        ]
        
        return strategies
        
    except Exception as e:
        logger.error(f"Error getting response strategies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get response strategies: {str(e)}"
        )

@router.get("/context-types", response_model=List[Dict[str, str]])
async def get_context_types() -> List[Dict[str, str]]:
    """
    Get available context types used in analysis.
    
    Returns information about different types of context that are
    analyzed for generating responses.
    """
    try:
        context_types = [
            {
                "name": ContextType.CONVERSATION_HISTORY.value,
                "description": "Historical conversation messages and patterns"
            },
            {
                "name": ContextType.USER_PROFILE.value,
                "description": "User preferences, style, and characteristics"
            },
            {
                "name": ContextType.TOPIC_CONTEXT.value,
                "description": "Current and related discussion topics"
            },
            {
                "name": ContextType.EMOTIONAL_CONTEXT.value,
                "description": "Emotional tone and sentiment analysis"
            },
            {
                "name": ContextType.TEMPORAL_CONTEXT.value,
                "description": "Time-based patterns and session information"
            },
            {
                "name": ContextType.BEHAVIORAL_CONTEXT.value,
                "description": "User behavior patterns and interaction style"
            }
        ]
        
        return context_types
        
    except Exception as e:
        logger.error(f"Error getting context types: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context types: {str(e)}"
        )

@router.post("/quick-response", response_model=Dict[str, Any])
async def generate_quick_response(
    query: str = Field(..., description="User query"),
    user_id: Optional[str] = Field(default=None, description="Optional user ID"),
    strategy: Optional[str] = Field(default=None, description="Optional response strategy")
) -> Dict[str, Any]:
    """
    Generate a quick context-aware response with minimal context.
    
    This is a simplified endpoint for cases where full context analysis
    is not needed but some personalization is desired.
    """
    try:
        # Create minimal user profile
        user_profile = {
            'user_id': user_id or 'anonymous',
            'communication_style': 'balanced',
            'learning_style': 'mixed',
            'expertise_level': 'intermediate',
            'interests': []
        }
        
        # Generate response with minimal context
        response_data = await context_aware_ai_service.generate_response(
            query=query,
            user_profile=user_profile,
            conversation_history=[],
            additional_context={'quick_mode': True, 'preferred_strategy': strategy}
        )
        
        # Return simplified response
        return {
            'prompt': response_data.get('prompt', ''),
            'strategy': response_data.get('strategy', 'adaptive'),
            'confidence_score': response_data.get('confidence_score', 0.5),
            'processing_time_ms': response_data.get('processing_time_ms', 0),
            'suggestions': response_data.get('suggestions', [])[:2]  # Limit suggestions
        }
        
    except Exception as e:
        logger.error(f"Error generating quick response: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quick response: {str(e)}"
        )

@router.post("/batch-analyze", response_model=List[Dict[str, Any]])
async def batch_analyze_conversations(
    requests: List[ContextAnalysisRequest]
) -> List[Dict[str, Any]]:
    """
    Analyze multiple conversations in batch for efficiency.
    
    Useful for analyzing conversation patterns across multiple users
    or sessions simultaneously.
    """
    try:
        if len(requests) > 50:  # Limit batch size
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 50 conversations"
            )
        
        results = []
        
        for request in requests:
            try:
                # Convert conversation history to dictionaries
                conversation_history_dict = [msg.dict() for msg in request.conversation_history]
                
                # Perform context analysis
                analysis_result = await context_aware_ai_service.get_context_analysis(
                    user_id=request.user_id,
                    conversation_history=conversation_history_dict
                )
                
                results.append({
                    'user_id': request.user_id,
                    'analysis': analysis_result,
                    'status': 'success'
                })
                
            except Exception as e:
                results.append({
                    'user_id': request.user_id,
                    'error': str(e),
                    'status': 'error'
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform batch analysis: {str(e)}"
        )

@router.post("/clear-cache", response_model=Dict[str, str])
async def clear_response_cache() -> Dict[str, str]:
    """
    Clear the response cache to force fresh context analysis.
    
    Useful for testing or when user profiles have been significantly updated.
    """
    try:
        # Clear the service cache
        context_aware_ai_service.cache.clear()
        
        return {
            'status': 'success',
            'message': 'Response cache cleared successfully',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the context-aware AI service.
    
    Returns service status and basic diagnostic information.
    """
    try:
        metrics = await context_aware_ai_service.get_performance_metrics()
        
        return {
            'status': 'healthy',
            'service': 'context-aware-ai',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {
                'total_requests': metrics.get('total_requests', 0),
                'cache_size': metrics.get('cache_size', 0),
                'service_status': metrics.get('service_status', 'unknown')
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'service': 'context-aware-ai',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@router.post("/simulate-conversation", response_model=List[Dict[str, Any]])
async def simulate_conversation_flow(
    user_profile: UserProfile,
    queries: List[str] = Field(..., description="List of queries to simulate"),
    max_queries: int = Field(default=10, description="Maximum number of queries to process")
) -> List[Dict[str, Any]]:
    """
    Simulate a conversation flow to test context evolution.
    
    This endpoint is useful for testing how context awareness evolves
    throughout a conversation.
    """
    try:
        if len(queries) > max_queries:
            queries = queries[:max_queries]
        
        conversation_history = []
        results = []
        
        for i, query in enumerate(queries):
            # Generate context-aware response
            response_data = await context_aware_ai_service.generate_response(
                query=query,
                user_profile=user_profile.dict(),
                conversation_history=[msg.dict() for msg in conversation_history],
                additional_context={'simulation_mode': True, 'query_index': i}
            )
            
            # Add user message to history
            user_msg = ChatMessage(
                role="user",
                content=query,
                timestamp=datetime.utcnow().isoformat()
            )
            conversation_history.append(user_msg)
            
            # Add AI response to history (simplified)
            ai_msg = ChatMessage(
                role="assistant",
                content=f"Response to: {query}",
                timestamp=datetime.utcnow().isoformat(),
                metadata={'strategy': response_data.get('strategy', 'unknown')}
            )
            conversation_history.append(ai_msg)
            
            # Store result
            results.append({
                'query_index': i,
                'query': query,
                'response_data': response_data,
                'conversation_length': len(conversation_history)
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Error simulating conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to simulate conversation: {str(e)}"
        )

# Additional utility endpoints

@router.get("/statistics", response_model=Dict[str, Any])
async def get_service_statistics() -> Dict[str, Any]:
    """Get detailed service statistics and analytics."""
    try:
        metrics = await context_aware_ai_service.get_performance_metrics()
        
        return {
            'service_metrics': metrics,
            'feature_usage': {
                'context_analysis_enabled': True,
                'personalization_enabled': True,
                'caching_enabled': True,
                'batch_processing_enabled': True
            },
            'capabilities': {
                'supported_strategies': len(list(ResponseStrategy)),
                'supported_context_types': len(list(ContextType)),
                'max_conversation_history': 1000,
                'max_batch_size': 50
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

# Export router
__all__ = ['router']
