"""
Advanced Conversation Management Service
Intelligent conversation threading, organization, and management system

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import re

# Vector similarity imports
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class ConversationStatus(Enum):
    """Conversation status types"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ConversationType(Enum):
    """Conversation type categories"""
    GENERAL = "general"
    QUESTION_ANSWER = "question_answer"
    BRAINSTORMING = "brainstorming"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    RESEARCH = "research"
    PLANNING = "planning"
    DISCUSSION = "discussion"

class MessageRole(Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"

class ThreadingStrategy(Enum):
    """Conversation threading strategies"""
    TOPIC_BASED = "topic_based"
    TIME_BASED = "time_based"
    CONTEXT_BASED = "context_based"
    SEMANTIC_BASED = "semantic_based"
    HYBRID = "hybrid"

@dataclass
class ConversationMessage:
    """Individual message within a conversation"""
    message_id: str
    conversation_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    thread_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    edited: bool = False
    edit_history: List[Dict[str, Any]] = field(default_factory=list)
    reactions: Dict[str, int] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message_id': self.message_id,
            'conversation_id': self.conversation_id,
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'tokens': self.tokens,
            'metadata': self.metadata,
            'thread_id': self.thread_id,
            'parent_message_id': self.parent_message_id,
            'edited': self.edited,
            'edit_history': self.edit_history,
            'reactions': self.reactions,
            'attachments': self.attachments
        }

@dataclass
class ConversationThread:
    """Conversation thread for organizing related messages"""
    thread_id: str
    conversation_id: str
    title: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0
    participants: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    topic_keywords: List[str] = field(default_factory=list)
    thread_type: str = "general"
    status: str = "active"
    parent_thread_id: Optional[str] = None
    child_thread_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'thread_id': self.thread_id,
            'conversation_id': self.conversation_id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'message_count': self.message_count,
            'participants': self.participants,
            'tags': self.tags,
            'topic_keywords': self.topic_keywords,
            'thread_type': self.thread_type,
            'status': self.status,
            'parent_thread_id': self.parent_thread_id,
            'child_thread_ids': self.child_thread_ids
        }

@dataclass
class ConversationSummary:
    """Summary of conversation content and insights"""
    summary_id: str
    conversation_id: str
    title: str
    brief_summary: str
    detailed_summary: str
    key_points: List[str]
    topics_discussed: List[str]
    decisions_made: List[str]
    action_items: List[str]
    participants: List[str]
    sentiment_analysis: Dict[str, float]
    conversation_type: ConversationType
    quality_score: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'summary_id': self.summary_id,
            'conversation_id': self.conversation_id,
            'title': self.title,
            'brief_summary': self.brief_summary,
            'detailed_summary': self.detailed_summary,
            'key_points': self.key_points,
            'topics_discussed': self.topics_discussed,
            'decisions_made': self.decisions_made,
            'action_items': self.action_items,
            'participants': self.participants,
            'sentiment_analysis': self.sentiment_analysis,
            'conversation_type': self.conversation_type.value,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class ConversationAnalytics:
    """Analytics data for conversation insights"""
    analytics_id: str
    conversation_id: str
    message_count: int
    total_tokens: int
    avg_response_time: float
    engagement_score: float
    topic_distribution: Dict[str, float]
    sentiment_trend: List[Dict[str, Any]]
    user_participation: Dict[str, Dict[str, Any]]
    peak_activity_times: List[str]
    conversation_flow: Dict[str, Any]
    quality_metrics: Dict[str, float]
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'analytics_id': self.analytics_id,
            'conversation_id': self.conversation_id,
            'message_count': self.message_count,
            'total_tokens': self.total_tokens,
            'avg_response_time': self.avg_response_time,
            'engagement_score': self.engagement_score,
            'topic_distribution': self.topic_distribution,
            'sentiment_trend': self.sentiment_trend,
            'user_participation': self.user_participation,
            'peak_activity_times': self.peak_activity_times,
            'conversation_flow': self.conversation_flow,
            'quality_metrics': self.quality_metrics,
            'generated_at': self.generated_at.isoformat()
        }

class EnhancedConversation:
    """
    Enhanced conversation with advanced management capabilities
    """
    
    def __init__(self, conversation_id: str = None, user_id: str = None, conversation_data: Dict[str, Any] = None):
        """Initialize enhanced conversation"""
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Basic conversation properties
        data = conversation_data or {}
        self.title = data.get('title', 'New Conversation')
        self.description = data.get('description', '')
        self.conversation_type = ConversationType(data.get('conversation_type', 'general'))
        self.status = ConversationStatus(data.get('status', 'active'))
        
        # Messages and threads
        self.messages: List[ConversationMessage] = []
        self.threads: Dict[str, ConversationThread] = {}
        self.message_index: Dict[str, ConversationMessage] = {}
        
        # Organization and metadata
        self.tags = data.get('tags', [])
        self.participants = data.get('participants', [user_id] if user_id else [])
        self.is_shared = data.get('is_shared', False)
        self.sharing_permissions = data.get('sharing_permissions', {})
        
        # Analytics and insights
        self.summary: Optional[ConversationSummary] = None
        self.analytics: Optional[ConversationAnalytics] = None
        
        # Configuration
        self.auto_threading = data.get('auto_threading', True)
        self.threading_strategy = ThreadingStrategy(data.get('threading_strategy', 'hybrid'))
        self.max_context_messages = data.get('max_context_messages', 50)
        
        # Performance tracking
        self.performance_metrics = {
            'total_messages': 0,
            'total_tokens': 0,
            'avg_response_time': 0.0,
            'last_activity': None,
            'thread_count': 0,
            'auto_summaries_generated': 0
        }
    
    async def add_message(self, role: MessageRole, content: str, metadata: Dict[str, Any] = None) -> ConversationMessage:
        """Add a new message to the conversation"""
        message = ConversationMessage(
            message_id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            tokens=self._estimate_tokens(content),
            metadata=metadata or {}
        )
        
        # Add to messages list and index
        self.messages.append(message)
        self.message_index[message.message_id] = message
        
        # Auto-threading if enabled
        if self.auto_threading:
            await self._auto_thread_message(message)
        
        # Update conversation metadata
        self.updated_at = datetime.utcnow()
        self.performance_metrics['total_messages'] += 1
        self.performance_metrics['total_tokens'] += message.tokens
        self.performance_metrics['last_activity'] = datetime.utcnow()
        
        # Trigger auto-summary if needed
        if len(self.messages) % 20 == 0:  # Every 20 messages
            await self._generate_auto_summary()
        
        return message
    
    async def edit_message(self, message_id: str, new_content: str) -> bool:
        """Edit an existing message"""
        if message_id not in self.message_index:
            return False
        
        message = self.message_index[message_id]
        
        # Store edit history
        edit_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'previous_content': message.content,
            'editor': self.user_id
        }
        message.edit_history.append(edit_record)
        
        # Update message
        message.content = new_content
        message.tokens = self._estimate_tokens(new_content)
        message.edited = True
        
        self.updated_at = datetime.utcnow()
        return True
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message from the conversation"""
        if message_id not in self.message_index:
            return False
        
        message = self.message_index[message_id]
        
        # Remove from messages list
        self.messages = [m for m in self.messages if m.message_id != message_id]
        
        # Remove from index
        del self.message_index[message_id]
        
        # Update thread if message was threaded
        if message.thread_id and message.thread_id in self.threads:
            thread = self.threads[message.thread_id]
            thread.message_count -= 1
            if thread.message_count == 0:
                del self.threads[message.thread_id]
        
        self.updated_at = datetime.utcnow()
        self.performance_metrics['total_messages'] -= 1
        return True
    
    async def create_thread(self, title: str, message_ids: List[str] = None, thread_type: str = "general") -> ConversationThread:
        """Create a new conversation thread"""
        thread = ConversationThread(
            thread_id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            title=title,
            thread_type=thread_type,
            participants=self.participants.copy()
        )
        
        # Assign messages to thread
        if message_ids:
            for message_id in message_ids:
                if message_id in self.message_index:
                    self.message_index[message_id].thread_id = thread.thread_id
                    thread.message_count += 1
        
        self.threads[thread.thread_id] = thread
        self.performance_metrics['thread_count'] += 1
        
        return thread
    
    async def merge_threads(self, source_thread_id: str, target_thread_id: str) -> bool:
        """Merge two conversation threads"""
        if source_thread_id not in self.threads or target_thread_id not in self.threads:
            return False
        
        source_thread = self.threads[source_thread_id]
        target_thread = self.threads[target_thread_id]
        
        # Move all messages from source to target
        for message in self.messages:
            if message.thread_id == source_thread_id:
                message.thread_id = target_thread_id
                target_thread.message_count += 1
        
        # Update target thread metadata
        target_thread.tags.extend(source_thread.tags)
        target_thread.topic_keywords.extend(source_thread.topic_keywords)
        target_thread.updated_at = datetime.utcnow()
        
        # Remove source thread
        del self.threads[source_thread_id]
        self.performance_metrics['thread_count'] -= 1
        
        return True
    
    async def get_thread_messages(self, thread_id: str) -> List[ConversationMessage]:
        """Get all messages in a specific thread"""
        if thread_id not in self.threads:
            return []
        
        return [msg for msg in self.messages if msg.thread_id == thread_id]
    
    async def search_messages(self, query: str, filters: Dict[str, Any] = None) -> List[ConversationMessage]:
        """Search messages within the conversation"""
        results = []
        query_lower = query.lower()
        filters = filters or {}
        
        for message in self.messages:
            # Text search
            if query_lower in message.content.lower():
                # Apply filters
                if filters.get('role') and message.role.value != filters['role']:
                    continue
                if filters.get('thread_id') and message.thread_id != filters['thread_id']:
                    continue
                if filters.get('start_date'):
                    start_date = datetime.fromisoformat(filters['start_date'])
                    if message.timestamp < start_date:
                        continue
                if filters.get('end_date'):
                    end_date = datetime.fromisoformat(filters['end_date'])
                    if message.timestamp > end_date:
                        continue
                
                results.append(message)
        
        # Sort by relevance (simple approach - by timestamp)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results
    
    async def generate_summary(self, summary_type: str = "detailed") -> ConversationSummary:
        """Generate a conversation summary"""
        if not self.messages:
            return None
        
        # Extract conversation content
        conversation_text = " ".join([msg.content for msg in self.messages if msg.role != MessageRole.SYSTEM])
        
        # Generate summary using simple extraction (in production, would use AI)
        summary_data = self._extract_summary_data(conversation_text)
        
        self.summary = ConversationSummary(
            summary_id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            title=self.title,
            brief_summary=summary_data['brief'],
            detailed_summary=summary_data['detailed'],
            key_points=summary_data['key_points'],
            topics_discussed=summary_data['topics'],
            decisions_made=summary_data['decisions'],
            action_items=summary_data['actions'],
            participants=self.participants,
            sentiment_analysis=summary_data['sentiment'],
            conversation_type=self.conversation_type,
            quality_score=summary_data['quality_score']
        )
        
        self.performance_metrics['auto_summaries_generated'] += 1
        return self.summary
    
    async def generate_analytics(self) -> ConversationAnalytics:
        """Generate conversation analytics"""
        if not self.messages:
            return None
        
        # Calculate analytics
        message_count = len(self.messages)
        total_tokens = sum(msg.tokens for msg in self.messages)
        
        # User participation analysis
        user_participation = {}
        for msg in self.messages:
            role = msg.role.value
            if role not in user_participation:
                user_participation[role] = {'message_count': 0, 'token_count': 0}
            user_participation[role]['message_count'] += 1
            user_participation[role]['token_count'] += msg.tokens
        
        # Topic distribution (simplified)
        topic_distribution = self._analyze_topic_distribution()
        
        # Engagement score calculation
        engagement_score = self._calculate_engagement_score()
        
        self.analytics = ConversationAnalytics(
            analytics_id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            message_count=message_count,
            total_tokens=total_tokens,
            avg_response_time=self.performance_metrics['avg_response_time'],
            engagement_score=engagement_score,
            topic_distribution=topic_distribution,
            sentiment_trend=[],  # Would be populated with actual sentiment analysis
            user_participation=user_participation,
            peak_activity_times=self._get_peak_activity_times(),
            conversation_flow={},  # Would be populated with flow analysis
            quality_metrics=self._calculate_quality_metrics()
        )
        
        return self.analytics
    
    async def export_conversation(self, format: str = "json", include_metadata: bool = True) -> Union[str, Dict[str, Any]]:
        """Export conversation data"""
        export_data = {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'description': self.description,
            'conversation_type': self.conversation_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'participants': self.participants,
            'tags': self.tags,
            'messages': [msg.to_dict() for msg in self.messages],
            'threads': [thread.to_dict() for thread in self.threads.values()]
        }
        
        if include_metadata:
            export_data['performance_metrics'] = self.performance_metrics
            if self.summary:
                export_data['summary'] = self.summary.to_dict()
            if self.analytics:
                export_data['analytics'] = self.analytics.to_dict()
        
        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            return export_data
    
    # Private helper methods
    
    async def _auto_thread_message(self, message: ConversationMessage):
        """Automatically thread a message based on strategy"""
        if self.threading_strategy == ThreadingStrategy.TOPIC_BASED:
            await self._thread_by_topic(message)
        elif self.threading_strategy == ThreadingStrategy.SEMANTIC_BASED:
            await self._thread_by_semantics(message)
        elif self.threading_strategy == ThreadingStrategy.HYBRID:
            await self._thread_hybrid(message)
    
    async def _thread_by_topic(self, message: ConversationMessage):
        """Thread message based on topic keywords"""
        # Extract keywords from message content
        keywords = self._extract_keywords(message.content)
        
        # Find matching threads
        for thread in self.threads.values():
            if any(keyword in thread.topic_keywords for keyword in keywords):
                message.thread_id = thread.thread_id
                thread.message_count += 1
                thread.updated_at = datetime.utcnow()
                return
        
        # Create new thread if no match found and message is substantial
        if len(keywords) >= 2 and len(message.content) > 50:
            thread_title = f"Discussion: {', '.join(keywords[:3])}"
            thread = await self.create_thread(thread_title, [message.message_id], "topic_based")
            thread.topic_keywords = keywords
    
    async def _thread_by_semantics(self, message: ConversationMessage):
        """Thread message based on semantic similarity"""
        if not self.messages or len(self.messages) < 2:
            return
        
        # Get recent messages for comparison
        recent_messages = self.messages[-10:]  # Last 10 messages
        
        # Calculate semantic similarity (simplified using TF-IDF)
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            texts = [msg.content for msg in recent_messages] + [message.content]
            
            if len(texts) >= 2:
                tfidf_matrix = vectorizer.fit_transform(texts)
                similarity_scores = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:-1])
                
                # Find most similar message
                max_similarity_idx = similarity_scores.argmax()
                max_similarity = similarity_scores.max()
                
                if max_similarity > 0.3:  # Threshold for similarity
                    similar_message = recent_messages[max_similarity_idx]
                    if similar_message.thread_id:
                        message.thread_id = similar_message.thread_id
                        self.threads[similar_message.thread_id].message_count += 1
        except Exception as e:
            logger.warning(f"Semantic threading failed: {e}")
    
    async def _thread_hybrid(self, message: ConversationMessage):
        """Hybrid threading strategy combining multiple approaches"""
        # Try semantic threading first
        await self._thread_by_semantics(message)
        
        # If not threaded, try topic-based
        if not message.thread_id:
            await self._thread_by_topic(message)
    
    async def _generate_auto_summary(self):
        """Generate automatic summary for long conversations"""
        if len(self.messages) < 10:
            return
        
        try:
            await self.generate_summary("brief")
        except Exception as e:
            logger.warning(f"Auto-summary generation failed: {e}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: ~4 characters per token
        return max(1, len(text) // 4)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'but', 'for', 'are', 'with', 'this', 'that', 'they', 'have'}
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords
        return list(set(keywords))
    
    def _extract_summary_data(self, text: str) -> Dict[str, Any]:
        """Extract summary data from conversation text"""
        # This is a simplified implementation
        # In production, would use advanced NLP/AI for better summaries
        
        sentences = text.split('.')[:5]  # First 5 sentences
        brief_summary = '. '.join(sentences[:2])
        detailed_summary = '. '.join(sentences)
        
        keywords = self._extract_keywords(text)
        
        return {
            'brief': brief_summary,
            'detailed': detailed_summary,
            'key_points': keywords[:5],
            'topics': keywords[:10],
            'decisions': [],  # Would extract decision-making phrases
            'actions': [],   # Would extract action items
            'sentiment': {'positive': 0.6, 'neutral': 0.3, 'negative': 0.1},
            'quality_score': 0.75  # Would calculate based on various factors
        }
    
    def _analyze_topic_distribution(self) -> Dict[str, float]:
        """Analyze topic distribution in conversation"""
        all_text = " ".join([msg.content for msg in self.messages])
        keywords = self._extract_keywords(all_text)
        
        # Simple frequency analysis
        topic_counts = {}
        for keyword in keywords:
            topic_counts[keyword] = topic_counts.get(keyword, 0) + 1
        
        total_keywords = sum(topic_counts.values())
        if total_keywords == 0:
            return {}
        
        # Convert to percentages
        return {topic: count/total_keywords for topic, count in topic_counts.items()}
    
    def _calculate_engagement_score(self) -> float:
        """Calculate conversation engagement score"""
        if not self.messages:
            return 0.0
        
        # Factors for engagement:
        # 1. Message frequency
        # 2. Message length variation
        # 3. Response time patterns
        # 4. Thread diversity
        
        message_count = len(self.messages)
        avg_message_length = sum(len(msg.content) for msg in self.messages) / message_count
        thread_count = len(self.threads)
        
        # Simple engagement calculation
        engagement = min(1.0, (message_count / 50) * 0.4 +
                        (avg_message_length / 200) * 0.3 +
                        (thread_count / 5) * 0.3)
        
        return round(engagement, 2)
    
    def _get_peak_activity_times(self) -> List[str]:
        """Get peak activity times from message timestamps"""
        if not self.messages:
            return []
        
        # Group messages by hour
        hour_counts = {}
        for msg in self.messages:
            hour = msg.timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find peak hours (top 3)
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{hour:02d}:00" for hour, _ in sorted_hours[:3]]
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate conversation quality metrics"""
        if not self.messages:
            return {}
        
        # Calculate various quality metrics
        avg_message_length = sum(len(msg.content) for msg in self.messages) / len(self.messages)
        thread_organization = len(self.threads) / max(1, len(self.messages) / 10)  # Threads per 10 messages
        
        return {
            'coherence': 0.75,  # Would calculate based on topic consistency
            'depth': min(1.0, avg_message_length / 100),  # Based on message depth
            'organization': min(1.0, thread_organization),
            'completeness': 0.8  # Would calculate based on conversation resolution
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'conversation_type': self.conversation_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': self.tags,
            'participants': self.participants,
            'is_shared': self.is_shared,
            'sharing_permissions': self.sharing_permissions,
            'auto_threading': self.auto_threading,
            'threading_strategy': self.threading_strategy.value,
            'max_context_messages': self.max_context_messages,
            'performance_metrics': self.performance_metrics,
            'message_count': len(self.messages),
            'thread_count': len(self.threads)
        }

class ConversationManager:
    """
    Service for managing enhanced conversations with advanced features
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize conversation manager"""
        self.config = config
        self.conversations: Dict[str, EnhancedConversation] = {}
        self.user_conversations: Dict[str, List[str]] = {}  # user_id -> conversation_ids
        
        # Indexing for search and discovery
        self.conversation_index = {}
        self.tag_index = {}
        self.participant_index = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_conversations': 0,
            'active_conversations': 0,
            'total_messages': 0,
            'total_threads': 0,
            'summaries_generated': 0,
            'searches_performed': 0,
            'auto_threading_events': 0
        }
        
        logger.info("Advanced conversation manager initialized")
    
    async def create_conversation(self, user_id: str, conversation_data: Dict[str, Any]) -> EnhancedConversation:
        """Create a new enhanced conversation"""
        try:
            conversation = EnhancedConversation(
                user_id=user_id,
                conversation_data=conversation_data
            )
            
            # Store conversation
            self.conversations[conversation.conversation_id] = conversation
            
            # Update user index
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
            self.user_conversations[user_id].append(conversation.conversation_id)
            
            # Update indexes
            await self._update_indexes(conversation)
            
            # Update metrics
            self.performance_metrics['total_conversations'] += 1
            if conversation.status == ConversationStatus.ACTIVE:
                self.performance_metrics['active_conversations'] += 1
            
            logger.info(f"Created conversation {conversation.conversation_id} for user {user_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create conversation for user {user_id}: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[EnhancedConversation]:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)
    
    async def get_user_conversations(self, user_id: str, filters: Dict[str, Any] = None) -> List[EnhancedConversation]:
        """Get all conversations for a user with optional filters"""
        conversation_ids = self.user_conversations.get(user_id, [])
        conversations = [self.conversations[cid] for cid in conversation_ids if cid in self.conversations]
        
        # Apply filters if provided
        if filters:
            filtered_conversations = []
            for conv in conversations:
                if self._matches_filters(conv, filters):
                    filtered_conversations.append(conv)
            conversations = filtered_conversations
        
        # Sort by updated time (most recent first)
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return conversations
    
    async def update_conversation(self, conversation_id: str, updates: Dict[str, Any]) -> Optional[EnhancedConversation]:
        """Update conversation metadata"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        # Update allowed fields
        updateable_fields = ['title', 'description', 'tags', 'status', 'is_shared', 'sharing_permissions']
        for field, value in updates.items():
            if field in updateable_fields:
                if field == 'status':
                    conversation.status = ConversationStatus(value)
                else:
                    setattr(conversation, field, value)
        
        conversation.updated_at = datetime.utcnow()
        
        # Update indexes
        await self._update_indexes(conversation)
        
        return conversation
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        
        # Remove from user index
        for user_id, conv_ids in self.user_conversations.items():
            if conversation_id in conv_ids:
                conv_ids.remove(conversation_id)
        
        # Remove from other indexes
        await self._remove_from_indexes(conversation)
        
        # Remove conversation
        del self.conversations[conversation_id]
        
        # Update metrics
        self.performance_metrics['total_conversations'] -= 1
        if conversation.status == ConversationStatus.ACTIVE:
            self.performance_metrics['active_conversations'] -= 1
        
        return True
    
    async def add_message(self, conversation_id: str, role: MessageRole, content: str, metadata: Dict[str, Any] = None) -> Optional[ConversationMessage]:
        """Add message to conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        message = await conversation.add_message(role, content, metadata)
        
        # Update global metrics
        self.performance_metrics['total_messages'] += 1
        if conversation.auto_threading:
            self.performance_metrics['auto_threading_events'] += 1
        
        return message
    
    async def search_conversations(self, user_id: str, query: str, filters: Dict[str, Any] = None) -> List[EnhancedConversation]:
        """Search conversations for a user"""
        user_conversations = await self.get_user_conversations(user_id, filters)
        results = []
        query_lower = query.lower()
        
        for conversation in user_conversations:
            # Search in title, description, and tags
            if (query_lower in conversation.title.lower() or
                query_lower in conversation.description.lower() or
                any(query_lower in tag.lower() for tag in conversation.tags)):
                results.append(conversation)
                continue
            
            # Search in message content
            for message in conversation.messages:
                if query_lower in message.content.lower():
                    results.append(conversation)
                    break
        
        self.performance_metrics['searches_performed'] += 1
        return results
    
    async def get_conversation_analytics(self, conversation_id: str) -> Optional[ConversationAnalytics]:
        """Get analytics for a specific conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        return await conversation.generate_analytics()
    
    async def generate_conversation_summary(self, conversation_id: str, summary_type: str = "detailed") -> Optional[ConversationSummary]:
        """Generate summary for a conversation"""
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            return None
        
        summary = await conversation.generate_summary(summary_type)
        if summary:
            self.performance_metrics['summaries_generated'] += 1
        
        return summary
    
    async def get_similar_conversations(self, conversation_id: str, limit: int = 5) -> List[EnhancedConversation]:
        """Find similar conversations based on content and metadata"""
        source_conversation = self.conversations.get(conversation_id)
        if not source_conversation:
            return []
        
        # Get user's conversations
        user_conversations = await self.get_user_conversations(source_conversation.user_id)
        user_conversations = [c for c in user_conversations if c.conversation_id != conversation_id]
        
        # Calculate similarity scores
        similarities = []
        for conv in user_conversations:
            similarity_score = await self._calculate_conversation_similarity(source_conversation, conv)
            similarities.append((similarity_score, conv))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [conv for _, conv in similarities[:limit]]
    
    async def export_conversations(self, user_id: str, conversation_ids: List[str] = None, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export conversations for a user"""
        if conversation_ids:
            conversations = [self.conversations[cid] for cid in conversation_ids if cid in self.conversations]
        else:
            conversations = await self.get_user_conversations(user_id)
        
        export_data = {
            'user_id': user_id,
            'export_timestamp': datetime.utcnow().isoformat(),
            'conversation_count': len(conversations),
            'conversations': []
        }
        
        for conv in conversations:
            conv_data = await conv.export_conversation(format="dict", include_metadata=True)
            export_data['conversations'].append(conv_data)
        
        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            return export_data
    
    async def get_system_analytics(self) -> Dict[str, Any]:
        """Get system-wide conversation analytics"""
        total_conversations = len(self.conversations)
        if total_conversations == 0:
            return {'message': 'No conversations available'}
        
        # Aggregate statistics
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        total_threads = sum(len(conv.threads) for conv in self.conversations.values())
        
        # Conversation type distribution
        type_distribution = {}
        status_distribution = {}
        
        for conv in self.conversations.values():
            conv_type = conv.conversation_type.value
            conv_status = conv.status.value
            
            type_distribution[conv_type] = type_distribution.get(conv_type, 0) + 1
            status_distribution[conv_status] = status_distribution.get(conv_status, 0) + 1
        
        # Calculate averages
        avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
        avg_threads_per_conversation = total_threads / total_conversations if total_conversations > 0 else 0
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'total_threads': total_threads,
            'avg_messages_per_conversation': round(avg_messages_per_conversation, 2),
            'avg_threads_per_conversation': round(avg_threads_per_conversation, 2),
            'conversation_type_distribution': type_distribution,
            'conversation_status_distribution': status_distribution,
            'performance_metrics': self.performance_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            return {
                'status': 'healthy',
                'conversations_managed': len(self.conversations),
                'active_conversations': sum(1 for c in self.conversations.values() if c.status == ConversationStatus.ACTIVE),
                'performance_metrics': self.performance_metrics,
                'memory_usage': {
                    'conversations_stored': len(self.conversations),
                    'indexes_maintained': len(self.conversation_index)
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}
    
    # Private helper methods
    
    async def _update_indexes(self, conversation: EnhancedConversation):
        """Update conversation indexes"""
        conv_id = conversation.conversation_id
        
        # Update conversation index
        self.conversation_index[conv_id] = {
            'title': conversation.title.lower(),
            'description': conversation.description.lower(),
            'type': conversation.conversation_type.value,
            'tags': [tag.lower() for tag in conversation.tags]
        }
        
        # Update tag index
        for tag in conversation.tags:
            tag_lower = tag.lower()
            if tag_lower not in self.tag_index:
                self.tag_index[tag_lower] = []
            if conv_id not in self.tag_index[tag_lower]:
                self.tag_index[tag_lower].append(conv_id)
        
        # Update participant index
        for participant in conversation.participants:
            if participant not in self.participant_index:
                self.participant_index[participant] = []
            if conv_id not in self.participant_index[participant]:
                self.participant_index[participant].append(conv_id)
    
    async def _remove_from_indexes(self, conversation: EnhancedConversation):
        """Remove conversation from indexes"""
        conv_id = conversation.conversation_id
        
        # Remove from conversation index
        if conv_id in self.conversation_index:
            del self.conversation_index[conv_id]
        
        # Remove from tag index
        for tag in conversation.tags:
            tag_lower = tag.lower()
            if tag_lower in self.tag_index and conv_id in self.tag_index[tag_lower]:
                self.tag_index[tag_lower].remove(conv_id)
        
        # Remove from participant index
        for participant in conversation.participants:
            if participant in self.participant_index and conv_id in self.participant_index[participant]:
                self.participant_index[participant].remove(conv_id)
    
    def _matches_filters(self, conversation: EnhancedConversation, filters: Dict[str, Any]) -> bool:
        """Check if conversation matches the given filters"""
        if 'status' in filters and conversation.status.value != filters['status']:
            return False
        if 'type' in filters and conversation.conversation_type.value != filters['type']:
            return False
        if 'tags' in filters:
            required_tags = filters['tags']
            if not any(tag in conversation.tags for tag in required_tags):
                return False
        if 'start_date' in filters:
            start_date = datetime.fromisoformat(filters['start_date'])
            if conversation.created_at < start_date:
                return False
        if 'end_date' in filters:
            end_date = datetime.fromisoformat(filters['end_date'])
            if conversation.created_at > end_date:
                return False
        
        return True
    
    async def _calculate_conversation_similarity(self, conv1: EnhancedConversation, conv2: EnhancedConversation) -> float:
        """Calculate similarity score between two conversations"""
        similarity_score = 0.0
        
        # Tag similarity
        common_tags = set(conv1.tags) & set(conv2.tags)
        total_tags = set(conv1.tags) | set(conv2.tags)
        if total_tags:
            tag_similarity = len(common_tags) / len(total_tags)
            similarity_score += tag_similarity * 0.3
        
        # Type similarity
        if conv1.conversation_type == conv2.conversation_type:
            similarity_score += 0.2
        
        # Content similarity (simplified)
        conv1_text = " ".join([msg.content for msg in conv1.messages])
        conv2_text = " ".join([msg.content for msg in conv2.messages])
        
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            texts = [conv1_text, conv2_text]
            if len(conv1_text) > 0 and len(conv2_text) > 0:
                tfidf_matrix = vectorizer.fit_transform(texts)
                content_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                similarity_score += content_similarity * 0.5
        except Exception:
            pass  # Handle cases where text is too short or vectorization fails
        
        return min(1.0, similarity_score)

def create_conversation_manager(config: Dict[str, Any]) -> ConversationManager:
    """Factory function to create conversation manager"""
    return ConversationManager(config)
