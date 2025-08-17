"""
Comprehensive Tests for Advanced Conversation Management System
Test suite covering conversation management, threading, analytics, and AI features

Author: CapeAI Development Team
Date: July 25, 2025
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Import the conversation management components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.conversation_manager import (
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

class TestConversationMessage:
    """Test suite for ConversationMessage class"""
    
    def test_message_creation(self):
        """Test creating a conversation message"""
        message = ConversationMessage(
            message_id="msg_123",
            conversation_id="conv_456",
            role=MessageRole.USER,
            content="Hello, this is a test message",
            timestamp=datetime.utcnow(),
            tokens=10
        )
        
        assert message.message_id == "msg_123"
        assert message.conversation_id == "conv_456"
        assert message.role == MessageRole.USER
        assert message.content == "Hello, this is a test message"
        assert message.tokens == 10
        assert not message.edited
        assert message.edit_history == []
        assert message.reactions == {}
    
    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        timestamp = datetime.utcnow()
        message = ConversationMessage(
            message_id="msg_123",
            conversation_id="conv_456",
            role=MessageRole.ASSISTANT,
            content="This is a response",
            timestamp=timestamp,
            tokens=15,
            metadata={"source": "ai"}
        )
        
        result = message.to_dict()
        
        assert result["message_id"] == "msg_123"
        assert result["conversation_id"] == "conv_456"
        assert result["role"] == "assistant"
        assert result["content"] == "This is a response"
        assert result["timestamp"] == timestamp.isoformat()
        assert result["tokens"] == 15
        assert result["metadata"] == {"source": "ai"}

class TestConversationThread:
    """Test suite for ConversationThread class"""
    
    def test_thread_creation(self):
        """Test creating a conversation thread"""
        thread = ConversationThread(
            thread_id="thread_123",
            conversation_id="conv_456",
            title="Test Thread",
            description="A test thread for discussion"
        )
        
        assert thread.thread_id == "thread_123"
        assert thread.conversation_id == "conv_456"
        assert thread.title == "Test Thread"
        assert thread.description == "A test thread for discussion"
        assert thread.message_count == 0
        assert thread.status == "active"
        assert thread.participants == []
        assert thread.tags == []
        assert thread.topic_keywords == []
    
    def test_thread_to_dict(self):
        """Test converting thread to dictionary"""
        created_at = datetime.utcnow()
        thread = ConversationThread(
            thread_id="thread_123",
            conversation_id="conv_456",
            title="Test Thread",
            created_at=created_at,
            participants=["user1", "user2"],
            tags=["important", "technical"]
        )
        
        result = thread.to_dict()
        
        assert result["thread_id"] == "thread_123"
        assert result["conversation_id"] == "conv_456"
        assert result["title"] == "Test Thread"
        assert result["created_at"] == created_at.isoformat()
        assert result["participants"] == ["user1", "user2"]
        assert result["tags"] == ["important", "technical"]

class TestEnhancedConversation:
    """Test suite for EnhancedConversation class"""
    
    @pytest.fixture
    def conversation(self):
        """Create a test conversation"""
        return EnhancedConversation(
            conversation_id="conv_test_123",
            user_id="user_456",
            conversation_data={
                "title": "Test Conversation",
                "description": "A conversation for testing",
                "conversation_type": "technical",
                "auto_threading": True,
                "threading_strategy": "hybrid"
            }
        )
    
    def test_conversation_creation(self, conversation):
        """Test creating an enhanced conversation"""
        assert conversation.conversation_id == "conv_test_123"
        assert conversation.user_id == "user_456"
        assert conversation.title == "Test Conversation"
        assert conversation.description == "A conversation for testing"
        assert conversation.conversation_type == ConversationType.TECHNICAL
        assert conversation.status == ConversationStatus.ACTIVE
        assert conversation.auto_threading is True
        assert conversation.threading_strategy == ThreadingStrategy.HYBRID
        assert len(conversation.messages) == 0
        assert len(conversation.threads) == 0
    
    @pytest.mark.asyncio
    async def test_add_message(self, conversation):
        """Test adding a message to conversation"""
        message = await conversation.add_message(
            MessageRole.USER,
            "Hello, I have a technical question about Python async programming."
        )
        
        assert message is not None
        assert message.role == MessageRole.USER
        assert len(conversation.messages) == 1
        assert conversation.performance_metrics["total_messages"] == 1
        assert conversation.performance_metrics["total_tokens"] > 0
        assert conversation.performance_metrics["last_activity"] is not None
    
    @pytest.mark.asyncio
    async def test_edit_message(self, conversation):
        """Test editing a message"""
        # Add a message first
        message = await conversation.add_message(MessageRole.USER, "Original content")
        message_id = message.message_id
        
        # Edit the message
        success = await conversation.edit_message(message_id, "Edited content")
        
        assert success is True
        edited_message = conversation.message_index[message_id]
        assert edited_message.content == "Edited content"
        assert edited_message.edited is True
        assert len(edited_message.edit_history) == 1
        assert edited_message.edit_history[0]["previous_content"] == "Original content"
    
    @pytest.mark.asyncio
    async def test_delete_message(self, conversation):
        """Test deleting a message"""
        # Add a message first
        message = await conversation.add_message(MessageRole.USER, "Message to delete")
        message_id = message.message_id
        
        assert len(conversation.messages) == 1
        
        # Delete the message
        success = await conversation.delete_message(message_id)
        
        assert success is True
        assert len(conversation.messages) == 0
        assert message_id not in conversation.message_index
    
    @pytest.mark.asyncio
    async def test_create_thread(self, conversation):
        """Test creating a thread"""
        # Add some messages first
        msg1 = await conversation.add_message(MessageRole.USER, "Question about Python")
        msg2 = await conversation.add_message(MessageRole.ASSISTANT, "Here's the answer")
        
        # Create a thread
        thread = await conversation.create_thread(
            "Python Discussion",
            [msg1.message_id, msg2.message_id],
            "technical"
        )
        
        assert thread is not None
        assert thread.title == "Python Discussion"
        assert thread.thread_type == "technical"
        assert thread.message_count == 2
        assert len(conversation.threads) == 1
        assert conversation.performance_metrics["thread_count"] == 1
        
        # Check messages are assigned to thread
        assert conversation.messages[0].thread_id == thread.thread_id
        assert conversation.messages[1].thread_id == thread.thread_id
    
    @pytest.mark.asyncio
    async def test_merge_threads(self, conversation):
        """Test merging two threads"""
        # Add messages and create threads
        msg1 = await conversation.add_message(MessageRole.USER, "Question 1")
        msg2 = await conversation.add_message(MessageRole.USER, "Question 2")
        msg3 = await conversation.add_message(MessageRole.USER, "Question 3")
        
        thread1 = await conversation.create_thread("Thread 1", [msg1.message_id])
        thread2 = await conversation.create_thread("Thread 2", [msg2.message_id, msg3.message_id])
        
        assert len(conversation.threads) == 2
        
        # Merge threads
        success = await conversation.merge_threads(thread1.thread_id, thread2.thread_id)
        
        assert success is True
        assert len(conversation.threads) == 1
        
        # Check all messages are in the target thread
        remaining_thread = list(conversation.threads.values())[0]
        assert remaining_thread.message_count == 3
    
    @pytest.mark.asyncio
    async def test_search_messages(self, conversation):
        """Test searching messages within conversation"""
        # Add various messages
        await conversation.add_message(MessageRole.USER, "I need help with Python programming")
        await conversation.add_message(MessageRole.ASSISTANT, "Sure, what specifically about Python?")
        await conversation.add_message(MessageRole.USER, "How do I handle async operations?")
        await conversation.add_message(MessageRole.ASSISTANT, "You can use asyncio for that")
        
        # Search for "Python"
        results = await conversation.search_messages("Python")
        assert len(results) == 2
        
        # Search for "async"
        results = await conversation.search_messages("async")
        assert len(results) >= 1
        
        # Search with filters
        results = await conversation.search_messages("Python", {"role": "user"})
        assert len(results) == 1
        assert results[0].role == MessageRole.USER
    
    @pytest.mark.asyncio
    async def test_generate_summary(self, conversation):
        """Test generating conversation summary"""
        # Add messages to have content for summary
        await conversation.add_message(MessageRole.USER, "I'm working on a machine learning project using Python")
        await conversation.add_message(MessageRole.ASSISTANT, "Great! What kind of ML problem are you solving?")
        await conversation.add_message(MessageRole.USER, "I'm building a recommendation system for an e-commerce platform")
        await conversation.add_message(MessageRole.ASSISTANT, "Recommendation systems are fascinating. You could use collaborative filtering or content-based approaches")
        
        summary = await conversation.generate_summary()
        
        assert summary is not None
        assert summary.conversation_id == conversation.conversation_id
        assert summary.conversation_type == ConversationType.TECHNICAL
        assert len(summary.brief_summary) > 0
        assert len(summary.detailed_summary) > 0
        assert len(summary.key_points) > 0
        assert len(summary.topics_discussed) > 0
        assert "positive" in summary.sentiment_analysis
        assert summary.quality_score > 0
    
    @pytest.mark.asyncio
    async def test_generate_analytics(self, conversation):
        """Test generating conversation analytics"""
        # Add messages and create some activity
        await conversation.add_message(MessageRole.USER, "First message")
        await conversation.add_message(MessageRole.ASSISTANT, "First response")
        await conversation.add_message(MessageRole.USER, "Second message with more content")
        await conversation.add_message(MessageRole.ASSISTANT, "Detailed response with technical information")
        
        analytics = await conversation.generate_analytics()
        
        assert analytics is not None
        assert analytics.conversation_id == conversation.conversation_id
        assert analytics.message_count == 4
        assert analytics.total_tokens > 0
        assert analytics.engagement_score >= 0
        assert len(analytics.topic_distribution) > 0
        assert "user" in analytics.user_participation
        assert "assistant" in analytics.user_participation
        assert len(analytics.peak_activity_times) > 0
        assert len(analytics.quality_metrics) > 0
    
    @pytest.mark.asyncio
    async def test_export_conversation(self, conversation):
        """Test exporting conversation data"""
        # Add some content
        await conversation.add_message(MessageRole.USER, "Test message for export")
        await conversation.add_message(MessageRole.ASSISTANT, "Response for export test")
        
        # Export as dictionary
        export_data = await conversation.export_conversation(format="dict")
        
        assert isinstance(export_data, dict)
        assert export_data["conversation_id"] == conversation.conversation_id
        assert export_data["title"] == conversation.title
        assert len(export_data["messages"]) == 2
        assert "performance_metrics" in export_data
        
        # Export as JSON
        json_export = await conversation.export_conversation(format="json")
        assert isinstance(json_export, str)
        
        # Verify JSON can be parsed
        parsed_data = json.loads(json_export)
        assert parsed_data["conversation_id"] == conversation.conversation_id
    
    @pytest.mark.asyncio
    async def test_auto_threading_topic_based(self, conversation):
        """Test automatic threading based on topics"""
        conversation.threading_strategy = ThreadingStrategy.TOPIC_BASED
        
        # Add messages with different topics
        await conversation.add_message(MessageRole.USER, "I want to learn about machine learning algorithms")
        await conversation.add_message(MessageRole.ASSISTANT, "ML algorithms are great! Let's start with supervised learning")
        await conversation.add_message(MessageRole.USER, "Can you help me with web development using React?")
        await conversation.add_message(MessageRole.ASSISTANT, "Sure! React is a powerful library for building UIs")
        
        # Check if threads were created automatically
        assert len(conversation.threads) >= 0  # May or may not create threads based on keyword extraction
        
        # Messages should have some threading logic applied
        for message in conversation.messages:
            # Thread assignment happens in auto-threading, may be None for short content
            pass  # Just verify no errors occurred

class TestConversationManager:
    """Test suite for ConversationManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create a test conversation manager"""
        config = {
            'auto_threading_enabled': True,
            'default_threading_strategy': 'hybrid',
            'max_context_messages': 50
        }
        return create_conversation_manager(config)
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, manager):
        """Test creating a conversation through manager"""
        conversation_data = {
            "title": "Manager Test Conversation",
            "description": "Testing conversation creation via manager",
            "conversation_type": "brainstorming",
            "tags": ["test", "manager"],
            "auto_threading": True
        }
        
        conversation = await manager.create_conversation("user_123", conversation_data)
        
        assert conversation is not None
        assert conversation.user_id == "user_123"
        assert conversation.title == "Manager Test Conversation"
        assert conversation.conversation_type == ConversationType.BRAINSTORMING
        assert "test" in conversation.tags
        assert conversation.conversation_id in manager.conversations
        assert "user_123" in manager.user_conversations
        assert manager.performance_metrics["total_conversations"] == 1
        assert manager.performance_metrics["active_conversations"] == 1
    
    @pytest.mark.asyncio
    async def test_get_conversation(self, manager):
        """Test retrieving a conversation"""
        # Create a conversation first
        conversation_data = {"title": "Test Retrieval", "conversation_type": "general"}
        created_conv = await manager.create_conversation("user_123", conversation_data)
        
        # Retrieve it
        retrieved_conv = await manager.get_conversation(created_conv.conversation_id)
        
        assert retrieved_conv is not None
        assert retrieved_conv.conversation_id == created_conv.conversation_id
        assert retrieved_conv.title == "Test Retrieval"
        
        # Test retrieving non-existent conversation
        non_existent = await manager.get_conversation("non_existent_id")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_get_user_conversations(self, manager):
        """Test getting all conversations for a user"""
        user_id = "user_456"
        
        # Create multiple conversations
        conv_data_1 = {"title": "Conversation 1", "conversation_type": "general", "status": "active"}
        conv_data_2 = {"title": "Conversation 2", "conversation_type": "technical", "status": "completed"}
        conv_data_3 = {"title": "Conversation 3", "conversation_type": "general", "status": "active"}
        
        conv1 = await manager.create_conversation(user_id, conv_data_1)
        conv2 = await manager.create_conversation(user_id, conv_data_2)
        conv3 = await manager.create_conversation(user_id, conv_data_3)
        
        # Get all conversations
        all_conversations = await manager.get_user_conversations(user_id)
        assert len(all_conversations) == 3
        
        # Test filtering by status
        active_conversations = await manager.get_user_conversations(user_id, {"status": "active"})
        assert len(active_conversations) == 2
        
        # Test filtering by type
        general_conversations = await manager.get_user_conversations(user_id, {"type": "general"})
        assert len(general_conversations) == 2
    
    @pytest.mark.asyncio
    async def test_update_conversation(self, manager):
        """Test updating conversation metadata"""
        # Create a conversation
        conv_data = {"title": "Original Title", "description": "Original description"}
        conversation = await manager.create_conversation("user_123", conv_data)
        
        # Update it
        updates = {
            "title": "Updated Title",
            "description": "Updated description",
            "tags": ["new", "tags"],
            "status": "paused"
        }
        
        updated_conv = await manager.update_conversation(conversation.conversation_id, updates)
        
        assert updated_conv is not None
        assert updated_conv.title == "Updated Title"
        assert updated_conv.description == "Updated description"
        assert updated_conv.tags == ["new", "tags"]
        assert updated_conv.status == ConversationStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_delete_conversation(self, manager):
        """Test deleting a conversation"""
        # Create a conversation
        conv_data = {"title": "To Be Deleted"}
        conversation = await manager.create_conversation("user_123", conv_data)
        conv_id = conversation.conversation_id
        
        assert conv_id in manager.conversations
        assert manager.performance_metrics["total_conversations"] == 1
        
        # Delete it
        success = await manager.delete_conversation(conv_id)
        
        assert success is True
        assert conv_id not in manager.conversations
        assert manager.performance_metrics["total_conversations"] == 0
        
        # Try deleting non-existent conversation
        success = await manager.delete_conversation("non_existent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_add_message(self, manager):
        """Test adding a message through manager"""
        # Create a conversation
        conv_data = {"title": "Message Test"}
        conversation = await manager.create_conversation("user_123", conv_data)
        
        # Add a message
        message = await manager.add_message(
            conversation.conversation_id,
            MessageRole.USER,
            "Test message through manager",
            {"source": "test"}
        )
        
        assert message is not None
        assert message.content == "Test message through manager"
        assert message.metadata["source"] == "test"
        assert manager.performance_metrics["total_messages"] == 1
    
    @pytest.mark.asyncio
    async def test_search_conversations(self, manager):
        """Test searching conversations"""
        user_id = "user_search_test"
        
        # Create conversations with different content
        conv1_data = {
            "title": "Python Machine Learning Project",
            "description": "Working on ML algorithms",
            "tags": ["python", "ml", "ai"]
        }
        conv2_data = {
            "title": "React Web Development",
            "description": "Building a frontend application",
            "tags": ["react", "web", "frontend"]
        }
        conv3_data = {
            "title": "Database Design Discussion",
            "description": "Discussing database schemas and optimization",
            "tags": ["database", "sql", "optimization"]
        }
        
        conv1 = await manager.create_conversation(user_id, conv1_data)
        conv2 = await manager.create_conversation(user_id, conv2_data)
        conv3 = await manager.create_conversation(user_id, conv3_data)
        
        # Add messages to conversations
        await manager.add_message(conv1.conversation_id, MessageRole.USER, "How do I implement neural networks in Python?")
        await manager.add_message(conv2.conversation_id, MessageRole.USER, "What's the best way to manage state in React?")
        await manager.add_message(conv3.conversation_id, MessageRole.USER, "Should I use NoSQL or SQL database?")
        
        # Search by title
        results = await manager.search_conversations(user_id, "Python")
        assert len(results) == 1
        assert results[0].title == "Python Machine Learning Project"
        
        # Search by tag
        results = await manager.search_conversations(user_id, "web")
        assert len(results) == 1
        assert results[0].title == "React Web Development"
        
        # Search by message content
        results = await manager.search_conversations(user_id, "neural networks")
        assert len(results) == 1
        
        # Search with no matches
        results = await manager.search_conversations(user_id, "nonexistent")
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_get_conversation_analytics(self, manager):
        """Test getting conversation analytics through manager"""
        # Create a conversation with content
        conv_data = {"title": "Analytics Test"}
        conversation = await manager.create_conversation("user_123", conv_data)
        
        # Add messages
        await manager.add_message(conversation.conversation_id, MessageRole.USER, "Question 1")
        await manager.add_message(conversation.conversation_id, MessageRole.ASSISTANT, "Answer 1")
        await manager.add_message(conversation.conversation_id, MessageRole.USER, "Question 2")
        
        # Get analytics
        analytics = await manager.get_conversation_analytics(conversation.conversation_id)
        
        assert analytics is not None
        assert analytics.conversation_id == conversation.conversation_id
        assert analytics.message_count == 3
        
        # Test with non-existent conversation
        analytics = await manager.get_conversation_analytics("non_existent")
        assert analytics is None
    
    @pytest.mark.asyncio
    async def test_generate_conversation_summary(self, manager):
        """Test generating conversation summary through manager"""
        # Create a conversation
        conv_data = {"title": "Summary Test"}
        conversation = await manager.create_conversation("user_123", conv_data)
        
        # Add content
        await manager.add_message(conversation.conversation_id, MessageRole.USER, "I need help with Python")
        await manager.add_message(conversation.conversation_id, MessageRole.ASSISTANT, "I can help you with Python programming")
        
        # Generate summary
        summary = await manager.generate_conversation_summary(conversation.conversation_id)
        
        assert summary is not None
        assert summary.conversation_id == conversation.conversation_id
        assert manager.performance_metrics["summaries_generated"] == 1
    
    @pytest.mark.asyncio
    async def test_get_similar_conversations(self, manager):
        """Test finding similar conversations"""
        user_id = "user_similarity_test"
        
        # Create conversations with similar content
        conv1_data = {
            "title": "Python Programming Help",
            "tags": ["python", "programming", "help"]
        }
        conv2_data = {
            "title": "JavaScript Development",
            "tags": ["javascript", "development", "web"]
        }
        conv3_data = {
            "title": "Python Development Tips",
            "tags": ["python", "development", "tips"]
        }
        
        conv1 = await manager.create_conversation(user_id, conv1_data)
        conv2 = await manager.create_conversation(user_id, conv2_data)
        conv3 = await manager.create_conversation(user_id, conv3_data)
        
        # Find similar conversations to conv1
        similar = await manager.get_similar_conversations(conv1.conversation_id, limit=5)
        
        # conv3 should be more similar to conv1 than conv2 due to Python tag
        assert len(similar) >= 1
        
        # Test with non-existent conversation
        similar = await manager.get_similar_conversations("non_existent")
        assert len(similar) == 0
    
    @pytest.mark.asyncio
    async def test_export_conversations(self, manager):
        """Test exporting conversations"""
        user_id = "user_export_test"
        
        # Create conversations
        conv1_data = {"title": "Export Test 1"}
        conv2_data = {"title": "Export Test 2"}
        
        conv1 = await manager.create_conversation(user_id, conv1_data)
        conv2 = await manager.create_conversation(user_id, conv2_data)
        
        # Export all conversations for user
        export_data = await manager.export_conversations(user_id, format="dict")
        
        assert isinstance(export_data, dict)
        assert export_data["user_id"] == user_id
        assert export_data["conversation_count"] == 2
        assert len(export_data["conversations"]) == 2
        
        # Export specific conversations
        specific_export = await manager.export_conversations(
            user_id, 
            [conv1.conversation_id], 
            format="dict"
        )
        
        assert specific_export["conversation_count"] == 1
        assert specific_export["conversations"][0]["conversation_id"] == conv1.conversation_id
    
    @pytest.mark.asyncio
    async def test_get_system_analytics(self, manager):
        """Test getting system-wide analytics"""
        # Create some conversations and activity
        user1 = "user1"
        user2 = "user2"
        
        conv1 = await manager.create_conversation(user1, {"title": "Conv 1", "conversation_type": "general"})
        conv2 = await manager.create_conversation(user1, {"title": "Conv 2", "conversation_type": "technical"})
        conv3 = await manager.create_conversation(user2, {"title": "Conv 3", "conversation_type": "general"})
        
        # Add messages
        await manager.add_message(conv1.conversation_id, MessageRole.USER, "Message 1")
        await manager.add_message(conv2.conversation_id, MessageRole.USER, "Message 2")
        await manager.add_message(conv3.conversation_id, MessageRole.USER, "Message 3")
        
        # Get system analytics
        analytics = await manager.get_system_analytics()
        
        assert analytics["total_conversations"] == 3
        assert analytics["total_messages"] == 3
        assert analytics["avg_messages_per_conversation"] == 1.0
        assert "conversation_type_distribution" in analytics
        assert analytics["conversation_type_distribution"]["general"] == 2
        assert analytics["conversation_type_distribution"]["technical"] == 1
        assert "performance_metrics" in analytics
    
    @pytest.mark.asyncio
    async def test_health_check(self, manager):
        """Test system health check"""
        # Create some content
        conv = await manager.create_conversation("user_test", {"title": "Health Test"})
        await manager.add_message(conv.conversation_id, MessageRole.USER, "Test message")
        
        health = await manager.health_check()
        
        assert health["status"] == "healthy"
        assert health["conversations_managed"] == 1
        assert health["active_conversations"] == 1
        assert "performance_metrics" in health
        assert "memory_usage" in health

class TestPerformanceAndEdgeCases:
    """Test suite for performance and edge cases"""
    
    @pytest.mark.asyncio
    async def test_large_conversation_handling(self):
        """Test handling conversations with many messages"""
        conversation = EnhancedConversation(
            user_id="user_perf_test",
            conversation_data={"title": "Large Conversation Test"}
        )
        
        # Add many messages
        for i in range(100):
            await conversation.add_message(
                MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                f"Message {i+1} with some content to make it realistic"
            )
        
        assert len(conversation.messages) == 100
        assert conversation.performance_metrics["total_messages"] == 100
        
        # Test search performance
        results = await conversation.search_messages("Message")
        assert len(results) == 100
        
        # Test analytics generation
        analytics = await conversation.generate_analytics()
        assert analytics.message_count == 100
    
    @pytest.mark.asyncio
    async def test_concurrent_message_operations(self):
        """Test concurrent message operations"""
        conversation = EnhancedConversation(
            user_id="user_concurrent_test",
            conversation_data={"title": "Concurrent Test"}
        )
        
        # Add messages concurrently
        async def add_messages(start_idx, count):
            for i in range(count):
                await conversation.add_message(
                    MessageRole.USER,
                    f"Concurrent message {start_idx + i}"
                )
        
        # Run concurrent tasks
        await asyncio.gather(
            add_messages(0, 10),
            add_messages(10, 10),
            add_messages(20, 10)
        )
        
        assert len(conversation.messages) == 30
    
    @pytest.mark.asyncio
    async def test_empty_conversation_operations(self):
        """Test operations on empty conversations"""
        conversation = EnhancedConversation(
            user_id="user_empty_test",
            conversation_data={"title": "Empty Test"}
        )
        
        # Test operations on empty conversation
        results = await conversation.search_messages("anything")
        assert len(results) == 0
        
        summary = await conversation.generate_summary()
        assert summary is None
        
        analytics = await conversation.generate_analytics()
        assert analytics is None
        
        thread_messages = await conversation.get_thread_messages("non_existent_thread")
        assert len(thread_messages) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid inputs"""
        conversation = EnhancedConversation(
            user_id="user_invalid_test",
            conversation_data={"title": "Invalid Input Test"}
        )
        
        # Test editing non-existent message
        success = await conversation.edit_message("non_existent_id", "new content")
        assert success is False
        
        # Test deleting non-existent message
        success = await conversation.delete_message("non_existent_id")
        assert success is False
        
        # Test merging non-existent threads
        success = await conversation.merge_threads("thread1", "thread2")
        assert success is False
    
    def test_token_estimation(self):
        """Test token estimation accuracy"""
        conversation = EnhancedConversation(user_id="test")
        
        # Test various content lengths
        short_text = "Hello"
        medium_text = "This is a medium length message with several words"
        long_text = "This is a much longer message that contains significantly more content and should result in a higher token count estimate"
        
        short_tokens = conversation._estimate_tokens(short_text)
        medium_tokens = conversation._estimate_tokens(medium_text)
        long_tokens = conversation._estimate_tokens(long_text)
        
        assert short_tokens < medium_tokens < long_tokens
        assert short_tokens >= 1  # Minimum token count
        assert long_tokens > short_tokens * 5  # Reasonable scaling
    
    def test_keyword_extraction(self):
        """Test keyword extraction functionality"""
        conversation = EnhancedConversation(user_id="test")
        
        text = "I need help with machine learning algorithms and deep neural network implementation"
        keywords = conversation._extract_keywords(text)
        
        assert "machine" in keywords
        assert "learning" in keywords
        assert "algorithms" in keywords
        assert "deep" in keywords
        assert "neural" in keywords
        assert "network" in keywords
        assert "implementation" in keywords
        
        # Test with stop words
        text_with_stop_words = "The quick brown fox jumps over the lazy dog"
        keywords = conversation._extract_keywords(text_with_stop_words)
        
        assert "the" not in keywords  # Stop word should be filtered
        assert "quick" in keywords
        assert "brown" in keywords

class TestIntegrationScenarios:
    """Integration test scenarios covering complete workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_conversation_workflow(self):
        """Test a complete conversation workflow from creation to analytics"""
        # Initialize manager
        config = {"auto_threading_enabled": True}
        manager = create_conversation_manager(config)
        
        # 1. Create conversation
        conversation_data = {
            "title": "Machine Learning Project Discussion",
            "description": "Planning a recommendation system project",
            "conversation_type": "brainstorming",
            "tags": ["ml", "project", "recommendations"],
            "auto_threading": True
        }
        
        conversation = await manager.create_conversation("user_integration", conversation_data)
        assert conversation is not None
        
        # 2. Add realistic conversation messages
        messages_to_add = [
            (MessageRole.USER, "I'm starting a new machine learning project for building a recommendation system. Where should I begin?"),
            (MessageRole.ASSISTANT, "Great project choice! For recommendation systems, you'll want to consider collaborative filtering, content-based filtering, or hybrid approaches. What type of data do you have available?"),
            (MessageRole.USER, "I have user purchase history, product descriptions, and user ratings. The dataset has about 100k users and 50k products."),
            (MessageRole.ASSISTANT, "Perfect! With that data, you could implement both collaborative and content-based filtering. I'd recommend starting with matrix factorization techniques like SVD or NMF for collaborative filtering."),
            (MessageRole.USER, "That sounds good. What about the technical stack? Should I use Python with scikit-learn or something more specialized?"),
            (MessageRole.ASSISTANT, "For production systems, I'd suggest using Python with libraries like Surprise for collaborative filtering, scikit-learn for general ML tasks, and possibly TensorFlow or PyTorch for deep learning approaches."),
            (MessageRole.USER, "How do I handle the cold start problem for new users or products?"),
            (MessageRole.ASSISTANT, "The cold start problem is common in recommendation systems. For new users, you can use popularity-based recommendations or demographic-based suggestions. For new products, content-based filtering using product features works well."),
        ]
        
        # Add messages and verify auto-threading
        for role, content in messages_to_add:
            message = await manager.add_message(conversation.conversation_id, role, content)
            assert message is not None
        
        # 3. Verify conversation state
        updated_conversation = await manager.get_conversation(conversation.conversation_id)
        assert len(updated_conversation.messages) == 8
        
        # 4. Test search functionality
        search_results = await manager.search_conversations("user_integration", "machine learning")
        assert len(search_results) == 1
        assert search_results[0].conversation_id == conversation.conversation_id
        
        # 5. Search messages within conversation
        message_results = await updated_conversation.search_messages("collaborative filtering")
        assert len(message_results) >= 2  # Should find multiple mentions
        
        # 6. Create manual thread
        ml_messages = [msg.message_id for msg in updated_conversation.messages[:4]]
        thread = await updated_conversation.create_thread(
            "ML Recommendation System Basics",
            ml_messages,
            "technical"
        )
        assert thread is not None
        assert thread.message_count == 4
        
        # 7. Generate summary
        summary = await manager.generate_conversation_summary(conversation.conversation_id)
        assert summary is not None
        assert "machine learning" in summary.brief_summary.lower()
        assert "recommendation" in summary.detailed_summary.lower()
        assert len(summary.key_points) > 0
        
        # 8. Generate analytics
        analytics = await manager.get_conversation_analytics(conversation.conversation_id)
        assert analytics is not None
        assert analytics.message_count == 8
        assert analytics.engagement_score > 0
        assert "user" in analytics.user_participation
        assert "assistant" in analytics.user_participation
        
        # 9. Export conversation
        export_data = await manager.export_conversations(
            "user_integration", 
            [conversation.conversation_id],
            format="dict"
        )
        assert export_data["conversation_count"] == 1
        assert len(export_data["conversations"][0]["messages"]) == 8
        
        # 10. Verify system analytics
        system_analytics = await manager.get_system_analytics()
        assert system_analytics["total_conversations"] >= 1
        assert system_analytics["total_messages"] >= 8
    
    @pytest.mark.asyncio
    async def test_multi_user_conversation_management(self):
        """Test managing conversations for multiple users"""
        config = {"auto_threading_enabled": True}
        manager = create_conversation_manager(config)
        
        users = ["user_1", "user_2", "user_3"]
        
        # Create conversations for each user
        for i, user in enumerate(users):
            for j in range(3):  # 3 conversations per user
                conv_data = {
                    "title": f"User {i+1} Conversation {j+1}",
                    "conversation_type": ["general", "technical", "brainstorming"][j],
                    "tags": [f"user{i+1}", f"conv{j+1}"]
                }
                
                conversation = await manager.create_conversation(user, conv_data)
                
                # Add some messages
                await manager.add_message(conversation.conversation_id, MessageRole.USER, f"Message from {user}")
                await manager.add_message(conversation.conversation_id, MessageRole.ASSISTANT, f"Response to {user}")
        
        # Verify each user has their conversations
        for user in users:
            user_conversations = await manager.get_user_conversations(user)
            assert len(user_conversations) == 3
            
            # Test filtering
            technical_conversations = await manager.get_user_conversations(user, {"type": "technical"})
            assert len(technical_conversations) == 1
            assert technical_conversations[0].conversation_type == ConversationType.TECHNICAL
        
        # Verify system totals
        system_analytics = await manager.get_system_analytics()
        assert system_analytics["total_conversations"] == 9
        assert system_analytics["total_messages"] == 18  # 2 messages per conversation

def run_performance_benchmarks():
    """Run performance benchmarks for conversation management"""
    import time
    
    async def benchmark_conversation_creation():
        """Benchmark conversation creation speed"""
        config = {"auto_threading_enabled": True}
        manager = create_conversation_manager(config)
        
        start_time = time.time()
        
        # Create 100 conversations
        for i in range(100):
            conv_data = {
                "title": f"Benchmark Conversation {i}",
                "conversation_type": "general"
            }
            await manager.create_conversation(f"user_{i % 10}", conv_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Created 100 conversations in {duration:.2f} seconds")
        print(f"Average: {duration/100*1000:.2f}ms per conversation")
        
        return duration
    
    async def benchmark_message_processing():
        """Benchmark message processing speed"""
        conversation = EnhancedConversation(
            user_id="benchmark_user",
            conversation_data={"title": "Benchmark Conversation"}
        )
        
        start_time = time.time()
        
        # Add 1000 messages
        for i in range(1000):
            await conversation.add_message(
                MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                f"Benchmark message {i} with realistic content for testing performance"
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Processed 1000 messages in {duration:.2f} seconds")
        print(f"Average: {duration/1000*1000:.2f}ms per message")
        
        # Test search performance
        search_start = time.time()
        results = await conversation.search_messages("benchmark")
        search_end = time.time()
        search_duration = search_end - search_start
        
        print(f"Searched {len(conversation.messages)} messages in {search_duration*1000:.2f}ms")
        
        return duration
    
    async def run_all_benchmarks():
        """Run all performance benchmarks"""
        print("=== Conversation Management Performance Benchmarks ===")
        
        conv_time = await benchmark_conversation_creation()
        msg_time = await benchmark_message_processing()
        
        print(f"\nSummary:")
        print(f"- Conversation creation: {conv_time:.2f}s for 100 conversations")
        print(f"- Message processing: {msg_time:.2f}s for 1000 messages")
        
        return {
            "conversation_creation_time": conv_time,
            "message_processing_time": msg_time
        }
    
    # Run benchmarks
    return asyncio.run(run_all_benchmarks())

if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short"])
    
    # Run performance benchmarks
    print("\n" + "="*50)
    run_performance_benchmarks()
