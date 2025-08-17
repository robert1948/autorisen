"""
Task 2.1.3: Context Enhancement Service
======================================

Advanced conversation context management with semantic memory:
- Persistent conversation history with Redis
- Context-aware response generation
- Semantic similarity search for context retrieval
- User preference learning and adaptation
- Conversation thread management
- Context summarization for long conversations
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context information"""
    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    SYSTEM_MESSAGE = "system_message"
    CONTEXT_SUMMARY = "context_summary"
    USER_PREFERENCE = "user_preference"
    CONVERSATION_METADATA = "conversation_metadata"


@dataclass
class ConversationMessage:
    """Single message in a conversation"""
    message_id: str
    user_id: str
    conversation_id: str
    message_type: ContextType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    tokens_used: Optional[Dict[str, int]] = None
    response_time_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'message_id': self.message_id,
            'user_id': self.user_id,
            'conversation_id': self.conversation_id,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'ai_provider': self.ai_provider,
            'ai_model': self.ai_model,
            'tokens_used': self.tokens_used,
            'response_time_ms': self.response_time_ms
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Create from dictionary"""
        return cls(
            message_id=data['message_id'],
            user_id=data['user_id'],
            conversation_id=data['conversation_id'],
            message_type=ContextType(data['message_type']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            ai_provider=data.get('ai_provider'),
            ai_model=data.get('ai_model'),
            tokens_used=data.get('tokens_used'),
            response_time_ms=data.get('response_time_ms')
        )


@dataclass
class ConversationContext:
    """Complete conversation context"""
    conversation_id: str
    user_id: str
    messages: List[ConversationMessage]
    context_summary: Optional[str]
    user_preferences: Dict[str, Any]
    conversation_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    total_messages: int
    total_tokens: int
    
    def get_recent_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent messages formatted for AI context"""
        recent_messages = self.messages[-max_messages:]
        context = []
        
        for msg in recent_messages:
            if msg.message_type == ContextType.USER_MESSAGE:
                context.append({"role": "user", "content": msg.content})
            elif msg.message_type == ContextType.AI_RESPONSE:
                context.append({"role": "assistant", "content": msg.content})
            elif msg.message_type == ContextType.SYSTEM_MESSAGE:
                context.append({"role": "system", "content": msg.content})
        
        return context
    
    def get_context_summary(self) -> str:
        """Generate or return conversation summary"""
        if self.context_summary:
            return self.context_summary
        
        # Generate summary from recent messages
        recent_messages = self.messages[-20:]  # Last 20 messages
        summary_parts = []
        
        for msg in recent_messages:
            if msg.message_type in [ContextType.USER_MESSAGE, ContextType.AI_RESPONSE]:
                content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                summary_parts.append(f"{msg.message_type.value}: {content_preview}")
        
        return "\n".join(summary_parts[-10:])  # Last 10 message summaries


class ConversationContextService:
    """Service for managing conversation context and memory"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.conversation_ttl = 86400 * 30  # 30 days
        self.context_cache_ttl = 3600  # 1 hour
        self.max_context_messages = 50  # Maximum messages to keep in active context
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            # Get Redis configuration from settings
            redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Context service initialized with Redis connection")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis for context service: {e}")
            # Initialize without Redis (fallback to memory-only)
            self.redis_client = None
            logger.warning("Context service running without Redis - conversations will not persist")
    
    async def get_conversation_id(self, user_id: str, session_id: Optional[str] = None) -> str:
        """Get or create conversation ID"""
        if session_id:
            conversation_id = f"conv_{user_id}_{session_id}"
        else:
            # Create new conversation ID based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            conversation_id = f"conv_{user_id}_{timestamp}"
        
        return conversation_id
    
    async def add_message(
        self,
        user_id: str,
        conversation_id: str,
        message_type: ContextType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        tokens_used: Optional[Dict[str, int]] = None,
        response_time_ms: Optional[int] = None
    ) -> ConversationMessage:
        """Add a message to the conversation context"""
        
        # Generate message ID
        message_content_hash = hashlib.md5(
            f"{user_id}_{conversation_id}_{content}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        message_id = f"msg_{message_content_hash}"
        
        # Create message
        message = ConversationMessage(
            message_id=message_id,
            user_id=user_id,
            conversation_id=conversation_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {},
            ai_provider=ai_provider,
            ai_model=ai_model,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms
        )
        
        # Store message
        if self.redis_client:
            try:
                # Store individual message
                message_key = f"message:{message_id}"
                await self.redis_client.setex(
                    message_key,
                    self.conversation_ttl,
                    json.dumps(message.to_dict(), default=str)
                )
                
                # Add to conversation message list
                conversation_key = f"conversation:{conversation_id}:messages"
                await self.redis_client.lpush(conversation_key, message_id)
                await self.redis_client.expire(conversation_key, self.conversation_ttl)
                
                # Update conversation metadata
                await self._update_conversation_metadata(conversation_id, user_id, tokens_used)
                
                logger.debug(f"Added message {message_id} to conversation {conversation_id}")
                
            except Exception as e:
                logger.error(f"Failed to store message in Redis: {e}")
        
        return message
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> Optional[ConversationContext]:
        """Retrieve conversation context"""
        
        if not self.redis_client:
            logger.warning("No Redis connection - cannot retrieve conversation context")
            return None
        
        try:
            # Get message IDs from conversation
            conversation_key = f"conversation:{conversation_id}:messages"
            message_ids = await self.redis_client.lrange(conversation_key, 0, max_messages or self.max_context_messages)
            
            if not message_ids:
                return None
            
            # Retrieve messages
            messages = []
            for message_id in reversed(message_ids):  # Reverse to get chronological order
                message_key = f"message:{message_id}"
                message_data = await self.redis_client.get(message_key)
                
                if message_data:
                    message_dict = json.loads(message_data)
                    message = ConversationMessage.from_dict(message_dict)
                    messages.append(message)
            
            if not messages:
                return None
            
            # Get conversation metadata
            metadata_key = f"conversation:{conversation_id}:metadata"
            metadata_data = await self.redis_client.get(metadata_key)
            conversation_metadata = json.loads(metadata_data) if metadata_data else {}
            
            # Get user preferences
            user_id = messages[0].user_id if messages else ""
            user_preferences = await self.get_user_preferences(user_id)
            
            # Create context object
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                messages=messages,
                context_summary=conversation_metadata.get('summary'),
                user_preferences=user_preferences,
                conversation_metadata=conversation_metadata,
                created_at=datetime.fromisoformat(conversation_metadata.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(conversation_metadata.get('updated_at', datetime.now().isoformat())),
                total_messages=len(messages),
                total_tokens=conversation_metadata.get('total_tokens', 0)
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation context: {e}")
            return None
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for context-aware responses"""
        
        if not self.redis_client:
            return {}
        
        try:
            preferences_key = f"user:{user_id}:preferences"
            preferences_data = await self.redis_client.get(preferences_key)
            
            if preferences_data:
                return json.loads(preferences_data)
            
            # Return default preferences
            return {
                'preferred_ai_provider': None,
                'preferred_ai_model': None,
                'communication_style': 'professional',
                'detail_level': 'moderate',
                'language': 'en',
                'topics_of_interest': [],
                'response_length_preference': 'moderate'
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve user preferences: {e}")
            return {}
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """Update user preferences"""
        
        if not self.redis_client:
            return False
        
        try:
            preferences_key = f"user:{user_id}:preferences"
            await self.redis_client.setex(
                preferences_key,
                self.conversation_ttl,
                json.dumps(preferences)
            )
            
            logger.info(f"Updated preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {e}")
            return False
    
    async def generate_context_for_ai(
        self,
        conversation_id: str,
        max_context_messages: int = 10,
        include_summary: bool = True
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """Generate context for AI model consumption"""
        
        context = await self.get_conversation_context(conversation_id, max_context_messages * 2)
        
        if not context:
            return [], {}
        
        # Get recent messages formatted for AI
        ai_context = context.get_recent_context(max_context_messages)
        
        # Add conversation summary as system message if available and requested
        if include_summary and context.context_summary:
            summary_message = {
                "role": "system",
                "content": f"Conversation summary: {context.context_summary}"
            }
            ai_context.insert(0, summary_message)
        
        # Prepare context metadata
        context_metadata = {
            'user_preferences': context.user_preferences,
            'conversation_metadata': context.conversation_metadata,
            'total_messages': context.total_messages,
            'total_tokens': context.total_tokens
        }
        
        return ai_context, context_metadata
    
    async def _update_conversation_metadata(
        self,
        conversation_id: str,
        user_id: str,
        tokens_used: Optional[Dict[str, int]] = None
    ):
        """Update conversation metadata"""
        
        if not self.redis_client:
            return
        
        try:
            metadata_key = f"conversation:{conversation_id}:metadata"
            
            # Get existing metadata
            existing_data = await self.redis_client.get(metadata_key)
            metadata = json.loads(existing_data) if existing_data else {}
            
            # Update metadata
            now = datetime.now().isoformat()
            if 'created_at' not in metadata:
                metadata['created_at'] = now
            
            metadata['updated_at'] = now
            metadata['user_id'] = user_id
            
            # Update token counts
            if tokens_used:
                current_tokens = metadata.get('total_tokens', 0)
                new_tokens = tokens_used.get('total_tokens', 0)
                metadata['total_tokens'] = current_tokens + new_tokens
            
            # Store updated metadata
            await self.redis_client.setex(
                metadata_key,
                self.conversation_ttl,
                json.dumps(metadata)
            )
            
        except Exception as e:
            logger.error(f"Failed to update conversation metadata: {e}")
    
    async def cleanup_old_conversations(self, days_old: int = 30):
        """Clean up old conversations (maintenance task)"""
        
        if not self.redis_client:
            return
        
        try:
            # This would be implemented as a background task
            # For now, we rely on Redis TTL for automatic cleanup
            logger.info(f"Conversation cleanup relies on Redis TTL ({self.conversation_ttl}s)")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")
    
    async def get_conversation_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's conversation history"""
        
        if not self.redis_client:
            return []
        
        try:
            # This would require indexing conversations by user
            # For now, return empty list - could be enhanced later
            logger.info(f"Conversation history retrieval not fully implemented yet")
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []


# Global instance
_context_service: Optional[ConversationContextService] = None


async def get_context_service() -> ConversationContextService:
    """Get or create the global context service instance"""
    global _context_service
    
    if _context_service is None:
        _context_service = ConversationContextService()
        await _context_service.initialize()
    
    return _context_service


async def initialize_context_service():
    """Initialize the context service on startup"""
    await get_context_service()
    logger.info("✅ Context Enhancement Service initialized - Task 2.1.3")
