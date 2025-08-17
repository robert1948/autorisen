"""
Task 2.1.6: AI Analytics Test Suite
==================================

Comprehensive test suite for AI analytics functionality:
- Analytics service tests
- Quality scoring tests  
- Performance metrics tests
- Dashboard data tests
- API endpoint tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from app.services.ai_analytics_service import (
    AIAnalyticsService,
    ResponseAnalytics,
    ConversationAnalytics,
    QualityScore,
    QualityDimension,
    AnalyticsPeriod,
    ModelPerformanceMetrics
)


class TestAIAnalyticsService:
    """Test suite for AIAnalyticsService"""

    @pytest.fixture
    def analytics_service(self):
        """Create AIAnalyticsService with mocked dependencies"""
        with patch('app.services.ai_analytics_service.get_context_service') as mock_context, \
             patch('app.services.ai_analytics_service.get_personalization_service') as mock_personalization:
            
            mock_context_service = AsyncMock()
            mock_personalization_service = AsyncMock()
            
            mock_context.return_value = mock_context_service
            mock_personalization.return_value = mock_personalization_service
            
            service = AIAnalyticsService()
            return service

    @pytest.fixture
    def sample_response_analytics(self):
        """Create sample response analytics data"""
        return ResponseAnalytics(
            response_id="resp_001",
            conversation_id="conv_001",
            user_id="user_001",
            model_used="gpt-4",
            provider="openai",
            timestamp=datetime.now(),
            quality_score=QualityScore(
                overall_score=0.85,
                dimension_scores={
                    QualityDimension.RELEVANCE: 0.9,
                    QualityDimension.ACCURACY: 0.8,
                    QualityDimension.CLARITY: 0.85
                },
                factors={"test": "data"},
                calculated_at=datetime.now(),
                evaluation_method="test"
            ),
            user_rating=4.2,
            user_feedback="Great response!",
            response_time_ms=1500,
            tokens_used={"input": 100, "output": 200},
            cost_estimate=0.005,
            conversation_turn=1,
            personalization_applied=True,
            template_used="general_template",
            follow_up_generated=False,
            user_continued=True,
            session_ended=False
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, analytics_service):
        """Test analytics service initialization"""
        assert analytics_service is not None
        assert analytics_service.response_analytics == {}
        assert analytics_service.conversation_analytics == {}
        assert analytics_service.model_performance == {}
        assert len(analytics_service.quality_evaluators) == 5

    @pytest.mark.asyncio
    async def test_record_response_analytics(self, analytics_service):
        """Test recording response analytics"""
        # Mock context service
        with patch('app.services.ai_analytics_service.get_context_service') as mock_context:
            mock_context_service = AsyncMock()
            mock_context_service.get_conversation_context.return_value = {"test": "context"}
            mock_context.return_value = mock_context_service
            
            # Record analytics
            analytics = await analytics_service.record_response_analytics(
                response_id="test_response",
                conversation_id="test_conv",
                user_id="test_user",
                model_used="gpt-4",
                provider="openai",
                response_content="This is a test response",
                prompt_content="Test prompt",
                response_time_ms=1200,
                tokens_used={"input": 50, "output": 100},
                cost_estimate=0.003,
                conversation_turn=1,
                personalization_applied=True
            )
            
            assert analytics.response_id == "test_response"
            assert analytics.model_used == "gpt-4"
            assert analytics.provider == "openai"
            assert analytics.personalization_applied is True
            assert analytics.quality_score is not None
            assert analytics.quality_score.overall_score > 0

    @pytest.mark.asyncio
    async def test_quality_score_calculation(self, analytics_service):
        """Test quality score calculation"""
        with patch('app.services.ai_analytics_service.get_context_service') as mock_context:
            mock_context_service = AsyncMock()
            mock_context_service.get_conversation_context.return_value = {}
            mock_context.return_value = mock_context_service
            
            quality_score = await analytics_service._calculate_quality_score(
                response="This is a comprehensive and helpful response that addresses your question about Python programming.",
                prompt="How do I learn Python programming?",
                conversation_id="test_conv"
            )
            
            assert quality_score.overall_score > 0
            assert quality_score.overall_score <= 1.0
            assert QualityDimension.RELEVANCE in quality_score.dimension_scores
            assert QualityDimension.HELPFULNESS in quality_score.dimension_scores
            assert quality_score.evaluation_method == "multi_dimensional_weighted"

    @pytest.mark.asyncio
    async def test_relevance_evaluation(self, analytics_service):
        """Test relevance evaluation"""
        dimension, score, factors = await analytics_service._evaluate_relevance(
            response="Python is a programming language. You can learn it by practicing coding.",
            prompt="How do I learn Python programming?",
            context={}
        )
        
        assert dimension == QualityDimension.RELEVANCE
        assert 0 <= score <= 1
        assert "word_overlap" in factors
        assert "prompt_words" in factors

    @pytest.mark.asyncio
    async def test_accuracy_evaluation(self, analytics_service):
        """Test accuracy evaluation"""
        dimension, score, factors = await analytics_service._evaluate_accuracy(
            response="According to research, Python is used by 8.2 million developers worldwide.",
            prompt="How popular is Python?",
            context={}
        )
        
        assert dimension == QualityDimension.ACCURACY
        assert 0 <= score <= 1
        assert "has_numbers" in factors
        assert "has_citations" in factors

    @pytest.mark.asyncio
    async def test_completeness_evaluation(self, analytics_service):
        """Test completeness evaluation"""
        dimension, score, factors = await analytics_service._evaluate_completeness(
            response="To learn Python: 1. Start with basics 2. Practice coding 3. Build projects. For example, create a calculator app.",
            prompt="How do I learn Python?",
            context={}
        )
        
        assert dimension == QualityDimension.COMPLETENESS
        assert 0 <= score <= 1
        assert "response_length" in factors
        assert "has_structure" in factors
        assert "has_examples" in factors

    @pytest.mark.asyncio
    async def test_clarity_evaluation(self, analytics_service):
        """Test clarity evaluation"""
        dimension, score, factors = await analytics_service._evaluate_clarity(
            response="Python is easy to learn. It has simple syntax. You can start coding quickly.",
            prompt="Is Python easy to learn?",
            context={}
        )
        
        assert dimension == QualityDimension.CLARITY
        assert 0 <= score <= 1
        assert "avg_sentence_length" in factors
        assert "complex_word_ratio" in factors

    @pytest.mark.asyncio
    async def test_helpfulness_evaluation(self, analytics_service):
        """Test helpfulness evaluation"""
        dimension, score, factors = await analytics_service._evaluate_helpfulness(
            response="You should start with online tutorials. I recommend trying Python.org. Let me know if you need more help!",
            prompt="How do I start learning Python?",
            context={}
        )
        
        assert dimension == QualityDimension.HELPFULNESS
        assert 0 <= score <= 1
        assert "has_actionable_advice" in factors
        assert "offers_followup" in factors

    @pytest.mark.asyncio
    async def test_user_feedback_recording(self, analytics_service, sample_response_analytics):
        """Test user feedback recording"""
        # Add sample analytics
        analytics_service.response_analytics["resp_001"] = sample_response_analytics
        
        # Record feedback
        await analytics_service.record_user_feedback(
            response_id="resp_001",
            user_rating=4.5,
            feedback="Very helpful response!"
        )
        
        updated_analytics = analytics_service.response_analytics["resp_001"]
        assert updated_analytics.user_rating == 4.5
        assert updated_analytics.user_feedback == "Very helpful response!"

    @pytest.mark.asyncio
    async def test_conversation_analytics_update(self, analytics_service, sample_response_analytics):
        """Test conversation analytics update"""
        await analytics_service._update_conversation_analytics("conv_001", sample_response_analytics)
        
        conv_analytics = analytics_service.conversation_analytics["conv_001"]
        assert conv_analytics.conversation_id == "conv_001"
        assert conv_analytics.user_id == "user_001"
        assert conv_analytics.total_turns == 1
        assert conv_analytics.total_tokens == 300  # 100 + 200
        assert conv_analytics.total_cost == 0.005

    @pytest.mark.asyncio
    async def test_model_performance_update(self, analytics_service, sample_response_analytics):
        """Test model performance metrics update"""
        await analytics_service._update_model_performance("gpt-4", "openai", sample_response_analytics)
        
        model_key = "openai:gpt-4"
        model_metrics = analytics_service.model_performance[model_key]
        
        assert model_metrics.model_name == "gpt-4"
        assert model_metrics.provider == "openai"
        assert model_metrics.total_requests == 1
        assert model_metrics.total_tokens == 300
        assert model_metrics.total_cost == 0.005

    @pytest.mark.asyncio
    async def test_analytics_dashboard_generation(self, analytics_service, sample_response_analytics):
        """Test analytics dashboard generation"""
        # Add sample data
        analytics_service.response_analytics["resp_001"] = sample_response_analytics
        
        # Generate dashboard
        dashboard = await analytics_service.get_analytics_dashboard(
            period=AnalyticsPeriod.DAY
        )
        
        assert "overview" in dashboard
        assert "quality_metrics" in dashboard
        assert "performance_metrics" in dashboard
        assert "usage_metrics" in dashboard
        assert "cost_metrics" in dashboard
        assert "model_comparison" in dashboard
        assert "trends" in dashboard
        
        assert dashboard["overview"]["total_responses"] == 1
        assert dashboard["overview"]["unique_users"] == 1

    @pytest.mark.asyncio
    async def test_overview_metrics_calculation(self, analytics_service):
        """Test overview metrics calculation"""
        # Create sample responses
        responses = [
            ResponseAnalytics(
                response_id=f"resp_{i}",
                conversation_id=f"conv_{i//2}",  # 2 responses per conversation
                user_id=f"user_{i//3}",  # 3 responses per user
                model_used="gpt-4",
                provider="openai",
                timestamp=datetime.now(),
                quality_score=QualityScore(0.8, {}, {}, datetime.now(), "test"),
                user_rating=4.0,
                user_feedback=None,
                response_time_ms=1000,
                tokens_used={"input": 50, "output": 100},
                cost_estimate=0.001,
                conversation_turn=1,
                personalization_applied=True,
                template_used=None,
                follow_up_generated=False,
                user_continued=False,
                session_ended=False
            ) for i in range(6)
        ]
        
        overview = await analytics_service._calculate_overview_metrics(responses)
        
        assert overview["total_responses"] == 6
        assert overview["unique_conversations"] == 3  # 6//2
        assert overview["unique_users"] == 2  # 6//3
        assert overview["avg_quality_score"] == 0.8
        assert overview["avg_user_rating"] == 4.0

    @pytest.mark.asyncio
    async def test_quality_metrics_calculation(self, analytics_service):
        """Test quality metrics calculation"""
        responses = [
            ResponseAnalytics(
                response_id=f"resp_{i}",
                conversation_id="conv_001",
                user_id="user_001",
                model_used="gpt-4",
                provider="openai",
                timestamp=datetime.now(),
                quality_score=QualityScore(
                    overall_score=0.9 - i*0.1,  # Varying scores
                    dimension_scores={
                        QualityDimension.RELEVANCE: 0.9,
                        QualityDimension.CLARITY: 0.8
                    },
                    factors={},
                    calculated_at=datetime.now(),
                    evaluation_method="test"
                ),
                user_rating=None,
                user_feedback=None,
                response_time_ms=1000,
                tokens_used={"input": 50, "output": 100},
                cost_estimate=0.001,
                conversation_turn=1,
                personalization_applied=False,
                template_used=None,
                follow_up_generated=False,
                user_continued=False,
                session_ended=False
            ) for i in range(3)
        ]
        
        quality_metrics = await analytics_service._calculate_quality_metrics(responses)
        
        assert "dimension_scores" in quality_metrics
        assert "quality_distribution" in quality_metrics
        assert quality_metrics["dimension_scores"]["relevance"] == 0.9
        assert quality_metrics["dimension_scores"]["clarity"] == 0.8

    @pytest.mark.asyncio
    async def test_model_comparison(self, analytics_service):
        """Test model comparison generation"""
        # Create responses for different models
        responses = []
        for i, (provider, model) in enumerate([("openai", "gpt-4"), ("anthropic", "claude-3"), ("google", "gemini-pro")]):
            responses.append(ResponseAnalytics(
                response_id=f"resp_{i}",
                conversation_id="conv_001",
                user_id="user_001",
                model_used=model,
                provider=provider,
                timestamp=datetime.now(),
                quality_score=QualityScore(0.8 + i*0.05, {}, {}, datetime.now(), "test"),
                user_rating=4.0 + i*0.2,
                user_feedback=None,
                response_time_ms=1000 + i*200,
                tokens_used={"input": 50, "output": 100},
                cost_estimate=0.001 + i*0.001,
                conversation_turn=1,
                personalization_applied=False,
                template_used=None,
                follow_up_generated=False,
                user_continued=False,
                session_ended=False
            ))
        
        comparison = await analytics_service._get_model_comparison(responses)
        
        assert len(comparison) == 3
        assert all("provider" in model for model in comparison)
        assert all("model" in model for model in comparison)
        assert all("avg_quality_score" in model for model in comparison)
        
        # Should be sorted by quality score (highest first)
        assert comparison[0]["avg_quality_score"] >= comparison[1]["avg_quality_score"]

    @pytest.mark.asyncio
    async def test_trend_calculation(self, analytics_service):
        """Test trend data calculation"""
        # Create responses spread over time
        base_time = datetime.now() - timedelta(hours=5)
        responses = []
        
        for i in range(5):
            responses.append(ResponseAnalytics(
                response_id=f"resp_{i}",
                conversation_id="conv_001",
                user_id="user_001",
                model_used="gpt-4",
                provider="openai",
                timestamp=base_time + timedelta(hours=i),
                quality_score=QualityScore(0.7 + i*0.05, {}, {}, datetime.now(), "test"),
                user_rating=None,
                user_feedback=None,
                response_time_ms=1000 + i*100,
                tokens_used={"input": 50, "output": 100},
                cost_estimate=0.001,
                conversation_turn=1,
                personalization_applied=False,
                template_used=None,
                follow_up_generated=False,
                user_continued=False,
                session_ended=False
            ))
        
        trends = await analytics_service._calculate_trend_data(responses, AnalyticsPeriod.DAY)
        
        assert "timestamps" in trends
        assert "quality_trend" in trends
        assert "volume_trend" in trends
        assert "response_time_trend" in trends
        assert len(trends["timestamps"]) > 0

    @pytest.mark.asyncio
    async def test_empty_dashboard(self, analytics_service):
        """Test empty dashboard generation"""
        empty_dashboard = analytics_service._empty_dashboard()
        
        assert empty_dashboard["overview"]["total_responses"] == 0
        assert empty_dashboard["overview"]["unique_conversations"] == 0
        assert empty_dashboard["overview"]["avg_quality_score"] == 0
        assert len(empty_dashboard["model_comparison"]) == 0


class TestAIAnalyticsAPI:
    """Test suite for AI Analytics API endpoints"""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for authentication"""
        user = MagicMock()
        user.id = 123
        user.email = "test@example.com"
        return user

    @pytest.mark.asyncio
    async def test_analytics_dashboard_endpoint(self, mock_user):
        """Test analytics dashboard API endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.ai_analytics.get_current_user', return_value=mock_user):
            with patch('app.routes.ai_analytics.get_analytics_service') as mock_service:
                mock_analytics_service = AsyncMock()
                mock_dashboard_data = {
                    "period": "day",
                    "date_range": {"start": "2025-07-25T00:00:00", "end": "2025-07-25T23:59:59"},
                    "overview": {"total_responses": 10, "avg_quality_score": 0.85},
                    "quality_metrics": {"dimension_scores": {}},
                    "performance_metrics": {"avg_response_time": 1500},
                    "usage_metrics": {"provider_distribution": {}},
                    "cost_metrics": {"total_cost": 0.05},
                    "model_comparison": [],
                    "trends": {"timestamps": [], "quality_trend": []},
                    "generated_at": "2025-07-25T12:00:00"
                }
                mock_analytics_service.get_analytics_dashboard.return_value = mock_dashboard_data
                mock_service.return_value = mock_analytics_service
                
                client = TestClient(app)
                response = client.get("/api/analytics/dashboard?period=day")
                
                assert response.status_code == 200
                data = response.json()
                assert data["period"] == "day"
                assert data["overview"]["total_responses"] == 10

    @pytest.mark.asyncio
    async def test_user_feedback_endpoint(self, mock_user):
        """Test user feedback recording endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.ai_analytics.get_current_user', return_value=mock_user):
            with patch('app.routes.ai_analytics.get_analytics_service') as mock_service:
                mock_analytics_service = AsyncMock()
                mock_analytics_service.record_user_feedback.return_value = None
                mock_service.return_value = mock_analytics_service
                
                client = TestClient(app)
                response = client.post("/api/analytics/feedback", json={
                    "response_id": "resp_123",
                    "user_rating": 4.5,
                    "feedback_text": "Great response!"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                assert data["response_id"] == "resp_123"

    @pytest.mark.asyncio
    async def test_quality_analysis_endpoint(self, mock_user):
        """Test quality analysis endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.ai_analytics.get_current_user', return_value=mock_user):
            with patch('app.routes.ai_analytics.get_analytics_service') as mock_service:
                mock_analytics_service = AsyncMock()
                mock_quality_score = QualityScore(
                    overall_score=0.85,
                    dimension_scores={QualityDimension.RELEVANCE: 0.9},
                    factors={"test": "data"},
                    calculated_at=datetime.now(),
                    evaluation_method="test"
                )
                mock_analytics_service._calculate_quality_score.return_value = mock_quality_score
                mock_service.return_value = mock_analytics_service
                
                client = TestClient(app)
                response = client.post("/api/analytics/quality/analyze", json={
                    "response_content": "This is a test response",
                    "prompt_content": "Test prompt"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["overall_score"] == 0.85
                assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_analytics_health_endpoint(self):
        """Test analytics health check endpoint"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        with patch('app.routes.ai_analytics.get_analytics_service') as mock_service:
            mock_analytics_service = AsyncMock()
            mock_analytics_service.response_analytics = {"resp_1": None}
            mock_analytics_service.conversation_analytics = {"conv_1": None}
            mock_analytics_service.model_performance = {"model_1": None}
            mock_analytics_service.quality_evaluators = [1, 2, 3, 4, 5]
            mock_service.return_value = mock_analytics_service
            
            client = TestClient(app)
            response = client.get("/api/analytics/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "ai_analytics"
            assert data["metrics"]["total_responses_tracked"] == 1


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
