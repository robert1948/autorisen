"""
Advanced Conversation Management API Routes
RESTful endpoints for intelligent conversation threading and management

Author: CapeAI Development Team
Date: July 25, 2025
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging

from ..services.conversation_manager import (
    ConversationManager,
    EnhancedConversation,
    ConversationMessage,
    ConversationThread,
    ConversationSummary,
    ConversationAnalytics,
    MessageRole,
    ConversationType,
    ConversationStatus,
    ThreadingStrategy,
    create_conversation_manager
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/conversations", tags=["Advanced Conversations"])

# Global conversation manager instance
conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get conversation manager instance"""
    global conversation_manager
    if not conversation_manager:
        config = {
            'auto_threading_enabled': True,
            'default_threading_strategy': 'hybrid',
            'max_context_messages': 50,
            'auto_summary_threshold': 20
        }
        conversation_manager = create_conversation_manager(config)
    return conversation_manager

# Pydantic models for API requests/responses

class CreateConversationRequest(BaseModel):
    """Request model for creating a conversation"""
    title: str = Field(..., description="Conversation title")
    description: str = Field("", description="Conversation description")
    conversation_type: str = Field("general", description="Type of conversation")
    tags: List[str] = Field(default_factory=list, description="Conversation tags")
    is_shared: bool = Field(False, description="Whether conversation is shared")
    auto_threading: bool = Field(True, description="Enable automatic threading")
    threading_strategy: str = Field("hybrid", description="Threading strategy")

class AddMessageRequest(BaseModel):
    """Request model for adding a message"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class EditMessageRequest(BaseModel):
    """Request model for editing a message"""
    content: str = Field(..., description="New message content")

class CreateThreadRequest(BaseModel):
    """Request model for creating a thread"""
    title: str = Field(..., description="Thread title")
    message_ids: List[str] = Field(default_factory=list, description="Message IDs to include")
    thread_type: str = Field("general", description="Thread type")

class UpdateConversationRequest(BaseModel):
    """Request model for updating conversation"""
    title: Optional[str] = Field(None, description="New title")
    description: Optional[str] = Field(None, description="New description")
    tags: Optional[List[str]] = Field(None, description="New tags")
    status: Optional[str] = Field(None, description="New status")
    is_shared: Optional[bool] = Field(None, description="Sharing status")

class SearchConversationsRequest(BaseModel):
    """Request model for searching conversations"""
    query: str = Field(..., description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")

class MessageSearchRequest(BaseModel):
    """Request model for searching messages within a conversation"""
    query: str = Field(..., description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")

class ConversationResponse(BaseModel):
    """Response model for conversation data"""
    conversation_id: str
    user_id: str
    title: str
    description: str
    conversation_type: str
    status: str
    created_at: str
    updated_at: str
    tags: List[str]
    participants: List[str]
    is_shared: bool
    auto_threading: bool
    threading_strategy: str
    message_count: int
    thread_count: int

class MessageResponse(BaseModel):
    """Response model for message data"""
    message_id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    tokens: int
    thread_id: Optional[str] = None
    edited: bool = False
    reactions: Dict[str, int] = Field(default_factory=dict)

class ThreadResponse(BaseModel):
    """Response model for thread data"""
    thread_id: str
    conversation_id: str
    title: str
    description: str
    created_at: str
    updated_at: str
    message_count: int
    participants: List[str]
    tags: List[str]
    topic_keywords: List[str]
    thread_type: str
    status: str
    parent_thread_id: Optional[str] = None
    child_thread_ids: List[str] = Field(default_factory=list)

# API Endpoints

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    user_id: str = Query(..., description="User ID")
) -> ConversationResponse:
    """Create a new enhanced conversation"""
    try:
        manager = get_conversation_manager()
        
        conversation_data = {
            'title': request.title,
            'description': request.description,
            'conversation_type': request.conversation_type,
            'tags': request.tags,
            'is_shared': request.is_shared,
            'auto_threading': request.auto_threading,
            'threading_strategy': request.threading_strategy
        }
        
        conversation = await manager.create_conversation(user_id, conversation_data)
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            description=conversation.description,
            conversation_type=conversation.conversation_type.value,
            status=conversation.status.value,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            tags=conversation.tags,
            participants=conversation.participants,
            is_shared=conversation.is_shared,
            auto_threading=conversation.auto_threading,
            threading_strategy=conversation.threading_strategy.value,
            message_count=len(conversation.messages),
            thread_count=len(conversation.threads)
        )
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")

@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    user_id: str = Query(..., description="User ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    type_filter: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(50, description="Maximum number of conversations to return")
) -> List[ConversationResponse]:
    """Get all conversations for a user with optional filters"""
    try:
        manager = get_conversation_manager()
        
        filters = {}
        if status_filter:
            filters['status'] = status_filter
        if type_filter:
            filters['type'] = type_filter
        
        conversations = await manager.get_user_conversations(user_id, filters)
        conversations = conversations[:limit]  # Apply limit
        
        return [
            ConversationResponse(
                conversation_id=conv.conversation_id,
                user_id=conv.user_id,
                title=conv.title,
                description=conv.description,
                conversation_type=conv.conversation_type.value,
                status=conv.status.value,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                tags=conv.tags,
                participants=conv.participants,
                is_shared=conv.is_shared,
                auto_threading=conv.auto_threading,
                threading_strategy=conv.threading_strategy.value,
                message_count=len(conv.messages),
                thread_count=len(conv.threads)
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str) -> ConversationResponse:
    """Get a specific conversation by ID"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            description=conversation.description,
            conversation_type=conversation.conversation_type.value,
            status=conversation.status.value,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            tags=conversation.tags,
            participants=conversation.participants,
            is_shared=conversation.is_shared,
            auto_threading=conversation.auto_threading,
            threading_strategy=conversation.threading_strategy.value,
            message_count=len(conversation.messages),
            thread_count=len(conversation.threads)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation: {str(e)}")

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest
) -> ConversationResponse:
    """Update conversation metadata"""
    try:
        manager = get_conversation_manager()
        
        # Build updates dictionary
        updates = {}
        if request.title is not None:
            updates['title'] = request.title
        if request.description is not None:
            updates['description'] = request.description
        if request.tags is not None:
            updates['tags'] = request.tags
        if request.status is not None:
            updates['status'] = request.status
        if request.is_shared is not None:
            updates['is_shared'] = request.is_shared
        
        conversation = await manager.update_conversation(conversation_id, updates)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            title=conversation.title,
            description=conversation.description,
            conversation_type=conversation.conversation_type.value,
            status=conversation.status.value,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            tags=conversation.tags,
            participants=conversation.participants,
            is_shared=conversation.is_shared,
            auto_threading=conversation.auto_threading,
            threading_strategy=conversation.threading_strategy.value,
            message_count=len(conversation.messages),
            thread_count=len(conversation.threads)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}")

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str) -> JSONResponse:
    """Delete a conversation"""
    try:
        manager = get_conversation_manager()
        success = await manager.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Conversation deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")

# Message management endpoints

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: str,
    request: AddMessageRequest
) -> MessageResponse:
    """Add a message to a conversation"""
    try:
        manager = get_conversation_manager()
        
        # Validate role
        try:
            role = MessageRole(request.role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {request.role}")
        
        message = await manager.add_message(conversation_id, role, request.content, request.metadata)
        
        if not message:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return MessageResponse(
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp.isoformat(),
            tokens=message.tokens,
            thread_id=message.thread_id,
            edited=message.edited,
            reactions=message.reactions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    thread_id: Optional[str] = Query(None, description="Filter by thread ID"),
    limit: int = Query(100, description="Maximum number of messages to return"),
    offset: int = Query(0, description="Number of messages to skip")
) -> List[MessageResponse]:
    """Get messages from a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = conversation.messages
        
        # Filter by thread if specified
        if thread_id:
            messages = [msg for msg in messages if msg.thread_id == thread_id]
        
        # Apply pagination
        messages = messages[offset:offset + limit]
        
        return [
            MessageResponse(
                message_id=msg.message_id,
                conversation_id=msg.conversation_id,
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                tokens=msg.tokens,
                thread_id=msg.thread_id,
                edited=msg.edited,
                reactions=msg.reactions
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.put("/{conversation_id}/messages/{message_id}")
async def edit_message(
    conversation_id: str,
    message_id: str,
    request: EditMessageRequest
) -> MessageResponse:
    """Edit a message in a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = await conversation.edit_message(message_id, request.content)
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        message = conversation.message_index[message_id]
        
        return MessageResponse(
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            role=message.role.value,
            content=message.content,
            timestamp=message.timestamp.isoformat(),
            tokens=message.tokens,
            thread_id=message.thread_id,
            edited=message.edited,
            reactions=message.reactions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to edit message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to edit message: {str(e)}")

@router.delete("/{conversation_id}/messages/{message_id}")
async def delete_message(conversation_id: str, message_id: str) -> JSONResponse:
    """Delete a message from a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = await conversation.delete_message(message_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Message deleted successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete message {message_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")

@router.post("/{conversation_id}/messages/search", response_model=List[MessageResponse])
async def search_messages(
    conversation_id: str,
    request: MessageSearchRequest
) -> List[MessageResponse]:
    """Search messages within a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await conversation.search_messages(request.query, request.filters)
        
        return [
            MessageResponse(
                message_id=msg.message_id,
                conversation_id=msg.conversation_id,
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                tokens=msg.tokens,
                thread_id=msg.thread_id,
                edited=msg.edited,
                reactions=msg.reactions
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search messages in conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search messages: {str(e)}")

# Thread management endpoints

@router.post("/{conversation_id}/threads", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    conversation_id: str,
    request: CreateThreadRequest
) -> ThreadResponse:
    """Create a new thread in a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        thread = await conversation.create_thread(
            request.title,
            request.message_ids,
            request.thread_type
        )
        
        return ThreadResponse(
            thread_id=thread.thread_id,
            conversation_id=thread.conversation_id,
            title=thread.title,
            description=thread.description,
            created_at=thread.created_at.isoformat(),
            updated_at=thread.updated_at.isoformat(),
            message_count=thread.message_count,
            participants=thread.participants,
            tags=thread.tags,
            topic_keywords=thread.topic_keywords,
            thread_type=thread.thread_type,
            status=thread.status,
            parent_thread_id=thread.parent_thread_id,
            child_thread_ids=thread.child_thread_ids
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create thread in conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@router.get("/{conversation_id}/threads", response_model=List[ThreadResponse])
async def get_conversation_threads(conversation_id: str) -> List[ThreadResponse]:
    """Get all threads in a conversation"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return [
            ThreadResponse(
                thread_id=thread.thread_id,
                conversation_id=thread.conversation_id,
                title=thread.title,
                description=thread.description,
                created_at=thread.created_at.isoformat(),
                updated_at=thread.updated_at.isoformat(),
                message_count=thread.message_count,
                participants=thread.participants,
                tags=thread.tags,
                topic_keywords=thread.topic_keywords,
                thread_type=thread.thread_type,
                status=thread.status,
                parent_thread_id=thread.parent_thread_id,
                child_thread_ids=thread.child_thread_ids
            )
            for thread in conversation.threads.values()
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get threads for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get threads: {str(e)}")

@router.get("/{conversation_id}/threads/{thread_id}/messages", response_model=List[MessageResponse])
async def get_thread_messages(conversation_id: str, thread_id: str) -> List[MessageResponse]:
    """Get all messages in a specific thread"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await conversation.get_thread_messages(thread_id)
        
        return [
            MessageResponse(
                message_id=msg.message_id,
                conversation_id=msg.conversation_id,
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp.isoformat(),
                tokens=msg.tokens,
                thread_id=msg.thread_id,
                edited=msg.edited,
                reactions=msg.reactions
            )
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get thread messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get thread messages: {str(e)}")

@router.post("/{conversation_id}/threads/{source_thread_id}/merge/{target_thread_id}")
async def merge_threads(
    conversation_id: str,
    source_thread_id: str,
    target_thread_id: str
) -> JSONResponse:
    """Merge two threads"""
    try:
        manager = get_conversation_manager()
        conversation = await manager.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        success = await conversation.merge_threads(source_thread_id, target_thread_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="One or both threads not found")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Threads merged successfully"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to merge threads: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to merge threads: {str(e)}")

# Analytics and insights endpoints

@router.get("/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    summary_type: str = Query("detailed", description="Type of summary (brief/detailed)")
) -> Dict[str, Any]:
    """Generate and get conversation summary"""
    try:
        manager = get_conversation_manager()
        summary = await manager.generate_conversation_summary(conversation_id, summary_type)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return summary.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/{conversation_id}/analytics")
async def get_conversation_analytics(conversation_id: str) -> Dict[str, Any]:
    """Get conversation analytics"""
    try:
        manager = get_conversation_manager()
        analytics = await manager.get_conversation_analytics(conversation_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return analytics.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/{conversation_id}/similar")
async def get_similar_conversations(
    conversation_id: str,
    limit: int = Query(5, description="Maximum number of similar conversations to return")
) -> List[ConversationResponse]:
    """Get similar conversations"""
    try:
        manager = get_conversation_manager()
        similar_conversations = await manager.get_similar_conversations(conversation_id, limit)
        
        return [
            ConversationResponse(
                conversation_id=conv.conversation_id,
                user_id=conv.user_id,
                title=conv.title,
                description=conv.description,
                conversation_type=conv.conversation_type.value,
                status=conv.status.value,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                tags=conv.tags,
                participants=conv.participants,
                is_shared=conv.is_shared,
                auto_threading=conv.auto_threading,
                threading_strategy=conv.threading_strategy.value,
                message_count=len(conv.messages),
                thread_count=len(conv.threads)
            )
            for conv in similar_conversations
        ]
        
    except Exception as e:
        logger.error(f"Failed to get similar conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get similar conversations: {str(e)}")

# Search and discovery endpoints

@router.post("/search", response_model=List[ConversationResponse])
async def search_conversations(
    request: SearchConversationsRequest,
    user_id: str = Query(..., description="User ID")
) -> List[ConversationResponse]:
    """Search conversations for a user"""
    try:
        manager = get_conversation_manager()
        conversations = await manager.search_conversations(user_id, request.query, request.filters)
        
        return [
            ConversationResponse(
                conversation_id=conv.conversation_id,
                user_id=conv.user_id,
                title=conv.title,
                description=conv.description,
                conversation_type=conv.conversation_type.value,
                status=conv.status.value,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                tags=conv.tags,
                participants=conv.participants,
                is_shared=conv.is_shared,
                auto_threading=conv.auto_threading,
                threading_strategy=conv.threading_strategy.value,
                message_count=len(conv.messages),
                thread_count=len(conv.threads)
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Failed to search conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search conversations: {str(e)}")

# Export and import endpoints

@router.get("/export")
async def export_conversations(
    user_id: str = Query(..., description="User ID"),
    conversation_ids: Optional[str] = Query(None, description="Comma-separated conversation IDs"),
    format: str = Query("json", description="Export format")
) -> Dict[str, Any]:
    """Export conversations"""
    try:
        manager = get_conversation_manager()
        
        # Parse conversation IDs if provided
        conv_ids = None
        if conversation_ids:
            conv_ids = [cid.strip() for cid in conversation_ids.split(',')]
        
        export_data = await manager.export_conversations(user_id, conv_ids, format)
        
        if format == "json":
            return {"export_data": export_data}
        else:
            return export_data
        
    except Exception as e:
        logger.error(f"Failed to export conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export conversations: {str(e)}")

# System endpoints

@router.get("/system/analytics")
async def get_system_analytics() -> Dict[str, Any]:
    """Get system-wide conversation analytics"""
    try:
        manager = get_conversation_manager()
        return await manager.get_system_analytics()
        
    except Exception as e:
        logger.error(f"Failed to get system analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system analytics: {str(e)}")

@router.get("/system/health")
async def health_check() -> Dict[str, Any]:
    """Check conversation management system health"""
    try:
        manager = get_conversation_manager()
        return await manager.health_check()
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# Utility endpoints

@router.get("/types")
async def get_conversation_types() -> Dict[str, List[str]]:
    """Get available conversation types and statuses"""
    return {
        "conversation_types": [ct.value for ct in ConversationType],
        "conversation_statuses": [cs.value for cs in ConversationStatus],
        "message_roles": [mr.value for mr in MessageRole],
        "threading_strategies": [ts.value for ts in ThreadingStrategy]
    }
