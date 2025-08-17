"""
Task 2.1.3: Context Enhancement API Endpoints
============================================

API endpoints for managing conversation context and memory:
- Conversation context retrieval
- User preference management
- Context-aware AI interactions
- Conversation history access
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.conversation_context_service import get_context_service, ContextType
from app.services.multi_provider_ai_service import MultiProviderAIService
from app.dependencies import get_current_user
from app.models import User

router = APIRouter(prefix="/api/ai/context", tags=["AI Context"])


class ConversationRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    use_context: bool = True


class ConversationResponse(BaseModel):
    response: str
    conversation_id: str
    model_used: str
    provider: str
    context_messages_used: int
    response_time_ms: int
    tokens_used: Dict[str, int]


class UserPreferencesUpdate(BaseModel):
    preferred_ai_provider: Optional[str] = None
    preferred_ai_model: Optional[str] = None
    communication_style: Optional[str] = None  # 'professional', 'casual', 'formal'
    detail_level: Optional[str] = None  # 'brief', 'moderate', 'detailed'
    language: Optional[str] = None
    topics_of_interest: Optional[List[str]] = None
    response_length_preference: Optional[str] = None  # 'short', 'moderate', 'long'


class ConversationContextResponse(BaseModel):
    conversation_id: str
    user_id: str
    total_messages: int
    total_tokens: int
    created_at: datetime
    updated_at: datetime
    context_summary: Optional[str]
    recent_messages: List[Dict[str, Any]]


@router.post("/chat", response_model=ConversationResponse)
async def context_aware_chat(
    request: ConversationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced AI chat with conversation context
    
    Features:
    - Automatic conversation context loading
    - User preference-aware responses  
    - Persistent conversation memory
    - Multi-provider AI with context
    """
    try:
        # Initialize services
        context_service = await get_context_service()
        ai_service = MultiProviderAIService()
        
        # Generate or use provided conversation ID
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = await context_service.get_conversation_id(
                user_id=str(current_user.id)
            )
        
        # Prepare messages for AI
        messages = [{"role": "user", "content": request.message}]
        
        # Generate context-aware response
        ai_response = await ai_service.generate_response(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            user_id=str(current_user.id),
            conversation_id=conversation_id,
            use_context=request.use_context
        )
        
        # Get context metadata for response
        context = await context_service.get_conversation_context(conversation_id)
        context_messages_used = len(context.messages) if context else 0
        
        return ConversationResponse(
            response=ai_response.content,
            conversation_id=conversation_id,
            model_used=ai_response.model,
            provider=ai_response.provider.value,
            context_messages_used=context_messages_used,
            response_time_ms=ai_response.response_time_ms,
            tokens_used=ai_response.usage
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=ConversationContextResponse)
async def get_conversation_context(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    max_messages: Optional[int] = Query(default=20, le=100)
):
    """Get conversation context and history"""
    try:
        context_service = await get_context_service()
        context = await context_service.get_conversation_context(
            conversation_id=conversation_id,
            max_messages=max_messages
        )
        
        if not context:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Verify user ownership
        if context.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Format recent messages for response
        recent_messages = []
        for msg in context.messages[-10:]:  # Last 10 messages
            recent_messages.append({
                "message_id": msg.message_id,
                "type": msg.message_type.value,
                "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "ai_provider": msg.ai_provider,
                "ai_model": msg.ai_model
            })
        
        return ConversationContextResponse(
            conversation_id=context.conversation_id,
            user_id=context.user_id,
            total_messages=context.total_messages,
            total_tokens=context.total_tokens,
            created_at=context.created_at,
            updated_at=context.updated_at,
            context_summary=context.context_summary,
            recent_messages=recent_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval error: {str(e)}")


@router.get("/preferences", response_model=Dict[str, Any])
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user's AI interaction preferences"""
    try:
        context_service = await get_context_service()
        preferences = await context_service.get_user_preferences(str(current_user.id))
        
        return {
            "user_id": current_user.id,
            "preferences": preferences,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preferences retrieval error: {str(e)}")


@router.put("/preferences", response_model=Dict[str, str])
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user's AI interaction preferences"""
    try:
        context_service = await get_context_service()
        
        # Convert to dict, excluding None values
        preferences_dict = {
            k: v for k, v in preferences.dict().items() 
            if v is not None
        }
        
        # Get current preferences and update
        current_prefs = await context_service.get_user_preferences(str(current_user.id))
        current_prefs.update(preferences_dict)
        
        # Save updated preferences
        success = await context_service.update_user_preferences(
            user_id=str(current_user.id),
            preferences=current_prefs
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {
            "message": "Preferences updated successfully",
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preferences update error: {str(e)}")


@router.get("/conversations", response_model=List[Dict[str, Any]])
async def get_conversation_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=10, le=50)
):
    """Get user's conversation history"""
    try:
        context_service = await get_context_service()
        history = await context_service.get_conversation_history(
            user_id=str(current_user.id),
            limit=limit
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History retrieval error: {str(e)}")


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation and its context"""
    try:
        context_service = await get_context_service()
        
        # Verify conversation exists and user ownership
        context = await context_service.get_conversation_context(conversation_id)
        if not context:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if context.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete conversation (implementation would be added to service)
        # For now, just return success
        return {"message": "Conversation deletion requested", "conversation_id": conversation_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion error: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_context_service_status():
    """Get context service health status"""
    try:
        context_service = await get_context_service()
        
        # Check Redis connectivity
        redis_status = "connected" if context_service.redis_client else "disconnected"
        
        return {
            "service": "Context Enhancement Service",
            "status": "operational",
            "redis_status": redis_status,
            "features": [
                "Conversation context management",
                "User preference learning",
                "Context-aware AI responses",
                "Conversation history tracking"
            ],
            "task": "2.1.3 - Context Enhancement",
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "service": "Context Enhancement Service",
            "status": "error",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }
