# backend/app/services/conversation_service.py
# filepath: backend/app/services/conversation_service.py
"""
Enhanced Conversation Service for CapeAI Enterprise Platform
Integrates with advanced conversation management system
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from .cape_ai_service import get_cape_ai_service
from .conversation_context_service import get_context_service
from .conversation_manager import create_conversation_manager
from .user_service import get_user_service

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Enterprise conversation service that wraps the advanced ConversationManager
    with database integration and enterprise features.
    """
    
    def __init__(self):
        self.user_service = get_user_service()
        self.ai_service = get_cape_ai_service()
        
        # Initialize advanced conversation manager
        config = {
            'auto_threading_enabled': True,
            'default_threading_strategy': 'hybrid',
            'max_context_messages': 50,
            'auto_summary_threshold': 20
        }
        self.conversation_manager = create_conversation_manager(config)
        logger.info("Enhanced ConversationService initialized with advanced features")
    
    async def create_conversation(self, db: Session, user_id: str, title: str = None, context: dict[str, Any] = None) -> dict[str, Any]:
        """Create a new conversation using advanced conversation manager."""
        try:
            # Verify user exists
            user = await self.user_service.get_user_by_id(db, user_id)
            if not user:
                logger.warning(f"User not found for conversation creation: {user_id}")
                return None
            
            # Prepare conversation data for advanced manager
            conversation_data = {
                'title': title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                'description': context.get('description', ''),
                'conversation_type': context.get('type', 'general'),
                'tags': context.get('tags', []),
                'is_shared': context.get('is_shared', False),
                'auto_threading': context.get('auto_threading', True),
                'threading_strategy': context.get('threading_strategy', 'hybrid')
            }
            
            # Create using advanced manager
            conversation = await self.conversation_manager.create_conversation(user_id, conversation_data)
            
            if conversation:
                # Convert to API-compatible format
                return {
                    "id": conversation.conversation_id,
                    "user_id": conversation.user_id,
                    "title": conversation.title,
                    "description": conversation.description,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                    "context": context or {},
                    "messages": [],
                    "status": conversation.status.value,
                    "message_count": len(conversation.messages),
                    "thread_count": len(conversation.threads),
                    "conversation_type": conversation.conversation_type.value,
                    "tags": conversation.tags,
                    "auto_threading": conversation.auto_threading,
                    "threading_strategy": conversation.threading_strategy.value
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    async def get_conversation(self, db: Session, conversation_id: str, user_id: str) -> dict[str, Any] | None:
        """Get conversation using advanced manager."""
        try:
            conversation = await self.conversation_manager.get_conversation(conversation_id)
            
            if not conversation:
                return None
            
            # Verify user ownership
            if conversation.user_id != user_id:
                logger.warning(f"Unauthorized access to conversation {conversation_id} by user {user_id}")
                return None
            
            # Convert to API format with full message history
            messages = []
            for msg in conversation.messages:
                messages.append({
                    "id": msg.message_id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "thread_id": msg.thread_id,
                    "tokens": msg.tokens,
                    "edited": msg.edited
                })
            
            return {
                "id": conversation.conversation_id,
                "user_id": conversation.user_id,
                "title": conversation.title,
                "description": conversation.description,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "messages": messages,
                "status": conversation.status.value,
                "message_count": len(conversation.messages),
                "thread_count": len(conversation.threads),
                "conversation_type": conversation.conversation_type.value,
                "tags": conversation.tags,
                "threads": [thread.to_dict() for thread in conversation.threads.values()]
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None
    
    async def add_message(self, db: Session, conversation_id: str, user_id: str, message: str, role: str = "user") -> dict[str, Any]:
        """Add message using advanced conversation manager."""
        try:
            from .conversation_manager import MessageRole
            
            # Verify conversation ownership
            conversation = await self.conversation_manager.get_conversation(conversation_id)
            if not conversation or conversation.user_id != user_id:
                logger.warning(f"Unauthorized or invalid conversation access: {conversation_id}")
                return None
            
            # Add message using advanced manager
            message_role = MessageRole(role)
            message_obj = await self.conversation_manager.add_message(
                conversation_id, 
                message_role, 
                message, 
                {"user_id": user_id}
            )
            
            if message_obj:
                return {
                    "id": message_obj.message_id,
                    "conversation_id": message_obj.conversation_id,
                    "role": message_obj.role.value,
                    "content": message_obj.content,
                    "timestamp": message_obj.timestamp.isoformat(),
                    "thread_id": message_obj.thread_id,
                    "tokens": message_obj.tokens,
                    "edited": message_obj.edited
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {e}")
            return None
    
    async def process_ai_message(self, db: Session, conversation_id: str, user_id: str, user_message: str, ai_provider: str = "auto") -> dict[str, Any]:
        """Process AI message with context awareness."""
        try:
            # Add user message first
            user_msg = await self.add_message(db, conversation_id, user_id, user_message, "user")
            if not user_msg:
                return None
            
            # Get conversation context for AI
            context_service = await get_context_service()
            ai_context, context_metadata = await context_service.generate_context_for_ai(
                conversation_id, 
                max_context_messages=10, 
                include_summary=True
            )
            
            # Get user profile for personalization
            user_profile = await self.user_service.get_user_profile(db, user_id) or {}
            
            # Generate AI response using CapeAI service
            start_time = datetime.utcnow()
            
            # Prepare context for AI service
            full_context = {
                "conversation_history": ai_context,
                "user_profile": user_profile,
                "conversation_metadata": context_metadata,
                "page": "conversation",
                "conversation_id": conversation_id
            }
            
            # This would integrate with your CapeAI service
            ai_response = await self._generate_ai_response_with_context(
                user_message, 
                full_context, 
                ai_provider
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            if ai_response:
                # Add AI response to conversation
                ai_msg = await self.add_message(
                    db, 
                    conversation_id, 
                    user_id, 
                    ai_response["content"], 
                    "assistant"
                )
                
                if ai_msg:
                    # Add AI-specific metadata
                    ai_msg.update({
                        "ai_provider": ai_response.get("provider", ai_provider),
                        "processing_time": processing_time,
                        "model_used": ai_response.get("model"),
                        "tokens_used": ai_response.get("tokens_used")
                    })
                    
                    logger.info(f"AI response generated for conversation {conversation_id}")
                    return ai_msg
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing AI message: {e}")
            return None
    
    async def get_user_conversations(self, db: Session, user_id: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """Get user conversations using advanced manager."""
        try:
            conversations = await self.conversation_manager.get_user_conversations(user_id)
            
            # Convert to API format with pagination
            summaries = []
            for conv in conversations[offset:offset + limit]:
                summary = {
                    "id": conv.conversation_id,
                    "title": conv.title,
                    "description": conv.description,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "message_count": len(conv.messages),
                    "thread_count": len(conv.threads),
                    "status": conv.status.value,
                    "conversation_type": conv.conversation_type.value,
                    "tags": conv.tags,
                    "last_message": conv.messages[-1].content[:100] + "..." if conv.messages else None
                }
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []
    
    async def _generate_ai_response_with_context(self, message: str, context: dict[str, Any], provider: str) -> dict[str, Any] | None:
        """Generate AI response with full context awareness."""
        try:
            # This integrates with your existing CapeAI service
            response = await self.ai_service.process_prompt(
                user_id=context.get("conversation_metadata", {}).get("user_id"),
                message=message,
                context=context,
                provider=provider if provider != "auto" else None
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None

# Global conversation service instance
conversation_service = ConversationService()

def get_conversation_service() -> ConversationService:
    """Get the global conversation service instance."""
    return conversation_service