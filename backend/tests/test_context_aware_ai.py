"""
Task 2.2.3: Context-Aware AI Responses - Comprehensive Test Suite
Tests for context-aware AI response generation, analysis, and optimization.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.context_aware_ai import (
    ContextType,
    ResponseStrategy,
    ContextWindow,
    UserContext,
    ResponseContext,
    ContextAnalyzer,
    ResponseGenerator,
    ContextAwareAIService,
    context_aware_ai_service
)

class TestContextAwareAI:
    """Test suite for context-aware AI response system"""

    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing"""
        return {
            'user_id': 'test-user-123',
            'communication_style': 'professional',
            'learning_style': 'visual',
            'expertise_level': 'intermediate',
            'interests': ['technology', 'programming', 'AI']
        }

    @pytest.fixture
    def sample_conversation_history(self):
        """Sample conversation history for testing"""
        return [
            {
                'role': 'user',
                'content': 'What is machine learning?',
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat()
            },
            {
                'role': 'assistant',
                'content': 'Machine learning is a subset of artificial intelligence...',
                'timestamp': (datetime.utcnow() - timedelta(minutes=9)).isoformat()
            },
            {
                'role': 'user',
                'content': 'How do neural networks work?',
                'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            },
            {
                'role': 'assistant',
                'content': 'Neural networks are computing systems inspired by biological neural networks...',
                'timestamp': (datetime.utcnow() - timedelta(minutes=4)).isoformat()
            },
            {
                'role': 'user',
                'content': 'Can you explain deep learning in simple terms?',
                'timestamp': (datetime.utcnow() - timedelta(minutes=2)).isoformat()
            }
        ]

    # Context Analysis Tests
    
    @pytest.mark.asyncio
    async def test_context_analyzer_creation(self):
        """Test ContextAnalyzer initialization"""
        analyzer = ContextAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'emotion_patterns')
        assert 'positive' in analyzer.emotion_patterns
        assert 'negative' in analyzer.emotion_patterns

    @pytest.mark.asyncio
    async def test_conversation_context_analysis(self, sample_conversation_history):
        """Test conversation context analysis"""
        analyzer = ContextAnalyzer()
        
        context_window = await analyzer.analyze_conversation_context(
            sample_conversation_history
        )
        
        assert isinstance(context_window, ContextWindow)
        assert context_window.messages == sample_conversation_history
        assert context_window.relevance_score >= 0.0
        assert context_window.relevance_score <= 1.0
        assert context_window.topic_focus in ['technology', 'general', 'business', 'creative']
        assert context_window.emotional_tone in ['positive', 'negative', 'neutral', 'excited', 'confused']
        assert context_window.user_engagement >= 0.0
        assert context_window.user_engagement <= 1.0

    @pytest.mark.asyncio
    async def test_user_context_analysis(self, sample_user_profile, sample_conversation_history):
        """Test user context analysis"""
        analyzer = ContextAnalyzer()
        
        user_context = await analyzer.analyze_user_context(
            sample_user_profile,
            sample_conversation_history
        )
        
        assert isinstance(user_context, UserContext)
        assert user_context.user_id == sample_user_profile['user_id']
        assert user_context.communication_style == sample_user_profile['communication_style']
        assert user_context.learning_style == sample_user_profile['learning_style']
        assert user_context.expertise_level == sample_user_profile['expertise_level']
        assert user_context.interests == sample_user_profile['interests']
        assert isinstance(user_context.conversation_patterns, dict)
        assert isinstance(user_context.recent_topics, list)

    @pytest.mark.asyncio
    async def test_empty_conversation_analysis(self):
        """Test context analysis with empty conversation"""
        analyzer = ContextAnalyzer()
        
        context_window = await analyzer.analyze_conversation_context([])
        
        assert isinstance(context_window, ContextWindow)
        assert context_window.messages == []
        assert context_window.relevance_score == 0.0
        assert context_window.topic_focus == "general"
        assert context_window.emotional_tone == "neutral"
        assert context_window.user_engagement == 0.0

    @pytest.mark.asyncio
    async def test_topic_focus_extraction(self, sample_conversation_history):
        """Test topic focus extraction from messages"""
        analyzer = ContextAnalyzer()
        
        # Test with technology-focused conversation
        tech_messages = [
            {'content': 'What is Python programming?'},
            {'content': 'How do I write JavaScript code?'},
            {'content': 'Explain API development'}
        ]
        topic = await analyzer._extract_topic_focus(tech_messages)
        assert topic == 'technology'
        
        # Test with business-focused conversation
        business_messages = [
            {'content': 'What is our marketing strategy?'},
            {'content': 'How can we increase sales revenue?'},
            {'content': 'Business development opportunities'}
        ]
        topic = await analyzer._extract_topic_focus(business_messages)
        assert topic == 'business'

    @pytest.mark.asyncio
    async def test_emotional_tone_analysis(self):
        """Test emotional tone analysis"""
        analyzer = ContextAnalyzer()
        
        # Test positive emotion
        positive_messages = [
            {'content': 'This is great! I love this feature.'},
            {'content': 'Excellent work, amazing results!'}
        ]
        emotion = await analyzer._analyze_emotional_tone(positive_messages)
        assert emotion == 'positive'
        
        # Test negative emotion
        negative_messages = [
            {'content': 'This is terrible and frustrating.'},
            {'content': 'I hate this awful interface.'}
        ]
        emotion = await analyzer._analyze_emotional_tone(negative_messages)
        assert emotion == 'negative'

    # Response Generation Tests

    @pytest.mark.asyncio
    async def test_response_generator_creation(self):
        """Test ResponseGenerator initialization"""
        generator = ResponseGenerator()
        assert generator is not None
        assert hasattr(generator, 'strategy_prompts')
        assert len(generator.strategy_prompts) == len(ResponseStrategy)

    @pytest.mark.asyncio
    async def test_response_strategy_selection(self, sample_user_profile, sample_conversation_history):
        """Test response strategy selection"""
        generator = ResponseGenerator()
        analyzer = ContextAnalyzer()
        
        # Create response context
        conv_context = await analyzer.analyze_conversation_context(sample_conversation_history)
        user_context = await analyzer.analyze_user_context(sample_user_profile, sample_conversation_history)
        
        response_context = ResponseContext(
            query="How does AI work?",
            conversation_context=conv_context,
            user_context=user_context,
            temporal_context={'time_of_day': 'afternoon'},
            topic_context={'current_topic': 'technology'},
            strategy=ResponseStrategy.ADAPTIVE,
            constraints={}
        )
        
        strategy = await generator._select_response_strategy(response_context)
        assert isinstance(strategy, ResponseStrategy)

    @pytest.mark.asyncio
    async def test_adaptive_prompt_generation(self, sample_user_profile, sample_conversation_history):
        """Test adaptive prompt generation"""
        generator = ResponseGenerator()
        analyzer = ContextAnalyzer()
        
        conv_context = await analyzer.analyze_conversation_context(sample_conversation_history)
        user_context = await analyzer.analyze_user_context(sample_user_profile, sample_conversation_history)
        
        response_context = ResponseContext(
            query="Explain quantum computing",
            conversation_context=conv_context,
            user_context=user_context,
            temporal_context={'time_of_day': 'morning'},
            topic_context={'current_topic': 'technology'},
            strategy=ResponseStrategy.ADAPTIVE,
            constraints={}
        )
        
        prompt = await generator._create_adaptive_prompt(response_context)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'communication style' in prompt.lower()
        assert 'learning style' in prompt.lower()

    @pytest.mark.asyncio
    async def test_context_aware_response_generation(self, sample_user_profile, sample_conversation_history):
        """Test complete context-aware response generation"""
        generator = ResponseGenerator()
        analyzer = ContextAnalyzer()
        
        conv_context = await analyzer.analyze_conversation_context(sample_conversation_history)
        user_context = await analyzer.analyze_user_context(sample_user_profile, sample_conversation_history)
        
        response_context = ResponseContext(
            query="What are the applications of machine learning?",
            conversation_context=conv_context,
            user_context=user_context,
            temporal_context={'time_of_day': 'evening'},
            topic_context={'current_topic': 'technology'},
            strategy=ResponseStrategy.EDUCATIONAL,
            constraints={}
        )
        
        response = await generator.generate_context_aware_response(response_context)
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        assert 'strategy' in response
        assert 'context_summary' in response
        assert 'metadata' in response
        assert 'personalization_applied' in response
        assert 'confidence_score' in response
        
        assert isinstance(response['prompt'], str)
        assert len(response['prompt']) > 0
        assert response['personalization_applied'] is True
        assert 0.0 <= response['confidence_score'] <= 1.0

    # Main Service Tests

    @pytest.mark.asyncio
    async def test_context_aware_ai_service_creation(self):
        """Test ContextAwareAIService initialization"""
        service = ContextAwareAIService()
        assert service is not None
        assert hasattr(service, 'context_analyzer')
        assert hasattr(service, 'response_generator')
        assert hasattr(service, 'cache')
        assert hasattr(service, 'performance_metrics')

    @pytest.mark.asyncio
    async def test_service_response_generation(self, sample_user_profile, sample_conversation_history):
        """Test service response generation"""
        service = ContextAwareAIService()
        
        response = await service.generate_response(
            query="How can I improve my Python skills?",
            user_profile=sample_user_profile,
            conversation_history=sample_conversation_history,
            additional_context=None
        )
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        assert 'strategy' in response
        assert 'response_context' in response
        assert 'processing_time_ms' in response
        assert 'quality_indicators' in response
        assert 'suggestions' in response
        assert 'from_cache' in response
        
        assert isinstance(response['processing_time_ms'], (int, float))
        assert response['processing_time_ms'] >= 0
        assert isinstance(response['suggestions'], list)

    @pytest.mark.asyncio
    async def test_service_context_analysis(self, sample_conversation_history):
        """Test service context analysis"""
        service = ContextAwareAIService()
        
        analysis = await service.get_context_analysis(
            user_id='test-user',
            conversation_history=sample_conversation_history
        )
        
        assert isinstance(analysis, dict)
        assert 'conversation_analysis' in analysis
        assert 'user_analysis' in analysis
        assert 'recommendations' in analysis
        assert 'quality_score' in analysis
        
        assert isinstance(analysis['quality_score'], (int, float))
        assert 0.0 <= analysis['quality_score'] <= 1.0
        assert isinstance(analysis['recommendations'], list)

    @pytest.mark.asyncio
    async def test_service_performance_metrics(self):
        """Test service performance metrics"""
        service = ContextAwareAIService()
        
        # Make a request first to generate some metrics
        await service.generate_response(
            query="Test query",
            user_profile={'user_id': 'test', 'communication_style': 'balanced', 'learning_style': 'mixed', 'expertise_level': 'intermediate', 'interests': []},
            conversation_history=[],
            additional_context=None
        )
        
        metrics = await service.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert 'total_requests' in metrics
        assert 'cache_hit_rate' in metrics
        assert 'average_processing_time_ms' in metrics
        assert 'average_context_quality' in metrics
        assert 'cache_size' in metrics
        assert 'service_status' in metrics
        
        assert metrics['total_requests'] > 0
        assert metrics['service_status'] == 'operational'

    @pytest.mark.asyncio
    async def test_service_caching(self, sample_user_profile):
        """Test service response caching"""
        service = ContextAwareAIService()
        
        query = "What is artificial intelligence?"
        
        # First request should not be from cache
        response1 = await service.generate_response(
            query=query,
            user_profile=sample_user_profile,
            conversation_history=[],
            additional_context=None
        )
        assert response1['from_cache'] is False
        
        # Second identical request should be from cache
        response2 = await service.generate_response(
            query=query,
            user_profile=sample_user_profile,
            conversation_history=[],
            additional_context=None
        )
        assert response2['from_cache'] is True

    # Edge Case Tests

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, sample_user_profile):
        """Test handling of empty queries"""
        service = ContextAwareAIService()
        
        response = await service.generate_response(
            query="",
            user_profile=sample_user_profile,
            conversation_history=[],
            additional_context=None
        )
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        # Should handle empty query gracefully

    @pytest.mark.asyncio
    async def test_minimal_user_profile(self):
        """Test with minimal user profile"""
        service = ContextAwareAIService()
        
        minimal_profile = {
            'user_id': 'minimal-user',
            'communication_style': 'balanced',
            'learning_style': 'mixed',
            'expertise_level': 'intermediate',
            'interests': []
        }
        
        response = await service.generate_response(
            query="Hello, how are you?",
            user_profile=minimal_profile,
            conversation_history=[],
            additional_context=None
        )
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        assert response['personalization_applied'] is True

    @pytest.mark.asyncio
    async def test_large_conversation_history(self, sample_user_profile):
        """Test with large conversation history"""
        service = ContextAwareAIService()
        
        # Create large conversation history
        large_history = []
        for i in range(100):
            large_history.extend([
                {
                    'role': 'user',
                    'content': f'User message {i}',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat()
                },
                {
                    'role': 'assistant',
                    'content': f'Assistant response {i}',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat()
                }
            ])
        
        response = await service.generate_response(
            query="Summarize our conversation",
            user_profile=sample_user_profile,
            conversation_history=large_history,
            additional_context=None
        )
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        # Should handle large history without errors

    @pytest.mark.asyncio
    async def test_invalid_timestamps(self, sample_user_profile):
        """Test handling of invalid timestamps in conversation history"""
        service = ContextAwareAIService()
        
        invalid_history = [
            {
                'role': 'user',
                'content': 'Test message',
                'timestamp': 'invalid-timestamp'
            }
        ]
        
        response = await service.generate_response(
            query="Test query",
            user_profile=sample_user_profile,
            conversation_history=invalid_history,
            additional_context=None
        )
        
        assert isinstance(response, dict)
        assert 'prompt' in response
        # Should handle invalid timestamps gracefully

    # Performance Tests

    @pytest.mark.asyncio
    async def test_response_generation_performance(self, sample_user_profile, sample_conversation_history):
        """Test response generation performance"""
        service = ContextAwareAIService()
        
        start_time = datetime.utcnow()
        
        response = await service.generate_response(
            query="What is the future of AI?",
            user_profile=sample_user_profile,
            conversation_history=sample_conversation_history,
            additional_context=None
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        assert isinstance(response, dict)
        assert processing_time < 5000  # Should complete within 5 seconds
        assert 'processing_time_ms' in response
        assert response['processing_time_ms'] > 0

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, sample_user_profile):
        """Test handling of concurrent requests"""
        service = ContextAwareAIService()
        
        async def make_request(query_num):
            return await service.generate_response(
                query=f"Test query {query_num}",
                user_profile=sample_user_profile,
                conversation_history=[],
                additional_context=None
            )
        
        # Make 5 concurrent requests
        tasks = [make_request(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        for response in responses:
            assert isinstance(response, dict)
            assert 'prompt' in response

    # Integration Tests

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, sample_user_profile, sample_conversation_history):
        """Test complete workflow integration"""
        service = ContextAwareAIService()
        
        # Test response generation
        response = await service.generate_response(
            query="Explain machine learning algorithms",
            user_profile=sample_user_profile,
            conversation_history=sample_conversation_history,
            additional_context={'preferred_strategy': 'educational'}
        )
        
        assert isinstance(response, dict)
        assert response['personalization_applied'] is True
        
        # Test context analysis
        analysis = await service.get_context_analysis(
            user_id=sample_user_profile['user_id'],
            conversation_history=sample_conversation_history
        )
        
        assert isinstance(analysis, dict)
        assert analysis['quality_score'] > 0
        
        # Test performance metrics
        metrics = await service.get_performance_metrics()
        
        assert isinstance(metrics, dict)
        assert metrics['total_requests'] > 0

    @pytest.mark.asyncio
    async def test_strategy_specific_responses(self, sample_user_profile, sample_conversation_history):
        """Test responses for different strategies"""
        generator = ResponseGenerator()
        analyzer = ContextAnalyzer()
        
        conv_context = await analyzer.analyze_conversation_context(sample_conversation_history)
        user_context = await analyzer.analyze_user_context(sample_user_profile, sample_conversation_history)
        
        strategies_to_test = [
            ResponseStrategy.ADAPTIVE,
            ResponseStrategy.CONVERSATIONAL,
            ResponseStrategy.ANALYTICAL,
            ResponseStrategy.CREATIVE,
            ResponseStrategy.PROFESSIONAL,
            ResponseStrategy.EDUCATIONAL
        ]
        
        for strategy in strategies_to_test:
            response_context = ResponseContext(
                query="Explain artificial intelligence",
                conversation_context=conv_context,
                user_context=user_context,
                temporal_context={'time_of_day': 'afternoon'},
                topic_context={'current_topic': 'technology'},
                strategy=strategy,
                constraints={}
            )
            
            response = await generator.generate_context_aware_response(response_context)
            
            assert isinstance(response, dict)
            assert 'prompt' in response
            assert response['strategy'] == strategy.value

    # Error Handling Tests

    @pytest.mark.asyncio
    async def test_malformed_user_profile_handling(self):
        """Test handling of malformed user profiles"""
        service = ContextAwareAIService()
        
        malformed_profile = {
            'user_id': None,  # Invalid user_id
            'invalid_field': 'value'
        }
        
        response = await service.generate_response(
            query="Test query",
            user_profile=malformed_profile,
            conversation_history=[],
            additional_context=None
        )
        
        # Should handle gracefully and return a response
        assert isinstance(response, dict)
        assert 'prompt' in response

    @pytest.mark.asyncio
    async def test_malformed_conversation_history(self, sample_user_profile):
        """Test handling of malformed conversation history"""
        service = ContextAwareAIService()
        
        malformed_history = [
            {
                'role': 'invalid_role',
                'content': None,  # Invalid content
                'timestamp': 'bad_timestamp'
            }
        ]
        
        response = await service.generate_response(
            query="Test query",
            user_profile=sample_user_profile,
            conversation_history=malformed_history,
            additional_context=None
        )
        
        # Should handle gracefully
        assert isinstance(response, dict)
        assert 'prompt' in response

# Performance Benchmark Tests

class TestContextAwareAIPerformance:
    """Performance benchmark tests for context-aware AI"""

    @pytest.mark.asyncio
    async def test_response_generation_benchmark(self):
        """Benchmark response generation performance"""
        service = ContextAwareAIService()
        
        user_profile = {
            'user_id': 'benchmark-user',
            'communication_style': 'balanced',
            'learning_style': 'mixed',
            'expertise_level': 'intermediate',
            'interests': ['technology']
        }
        
        conversation_history = [
            {
                'role': 'user',
                'content': 'What is machine learning?',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        # Benchmark 10 requests
        times = []
        for i in range(10):
            start_time = datetime.utcnow()
            
            await service.generate_response(
                query=f"Benchmark query {i}",
                user_profile=user_profile,
                conversation_history=conversation_history,
                additional_context=None
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds() * 1000
            times.append(processing_time)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\nResponse Generation Benchmark:")
        print(f"Average time: {avg_time:.2f}ms")
        print(f"Min time: {min_time:.2f}ms")
        print(f"Max time: {max_time:.2f}ms")
        
        # Performance assertions
        assert avg_time < 1000  # Average should be under 1 second
        assert max_time < 2000  # Max should be under 2 seconds

    @pytest.mark.asyncio
    async def test_context_analysis_benchmark(self):
        """Benchmark context analysis performance"""
        service = ContextAwareAIService()
        
        # Create substantial conversation history
        conversation_history = []
        for i in range(50):
            conversation_history.extend([
                {
                    'role': 'user',
                    'content': f'User message {i} about technology and programming',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat()
                },
                {
                    'role': 'assistant',
                    'content': f'Assistant response {i} with detailed explanation',
                    'timestamp': (datetime.utcnow() - timedelta(minutes=i)).isoformat()
                }
            ])
        
        # Benchmark 5 analysis requests
        times = []
        for i in range(5):
            start_time = datetime.utcnow()
            
            await service.get_context_analysis(
                user_id=f'benchmark-user-{i}',
                conversation_history=conversation_history
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds() * 1000
            times.append(processing_time)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\nContext Analysis Benchmark:")
        print(f"Average time: {avg_time:.2f}ms")
        print(f"Min time: {min_time:.2f}ms")
        print(f"Max time: {max_time:.2f}ms")
        
        # Performance assertions
        assert avg_time < 2000  # Average should be under 2 seconds
        assert max_time < 5000  # Max should be under 5 seconds

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
