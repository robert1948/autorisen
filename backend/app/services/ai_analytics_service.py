"""
Task 2.1.6: AI Analytics Service
==============================

Comprehensive AI analytics and quality metrics tracking system:
- Response quality analysis and scoring
- User satisfaction metrics and feedback tracking  
- AI model performance comparison and optimization
- Usage patterns and trend analysis
- Cost optimization and efficiency metrics
- Real-time analytics dashboard data
- Predictive analytics for AI improvements
- A/B testing for AI configurations
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import hashlib
from collections import defaultdict

# Import services for data collection
from app.services.conversation_context_service import get_context_service
from app.services.ai_personalization_service import get_personalization_service
from app.services.advanced_prompting_service import get_prompting_service

logger = logging.getLogger(__name__)


class AnalyticsMetric(str, Enum):
    """Types of analytics metrics"""
    RESPONSE_QUALITY = "response_quality"
    USER_SATISFACTION = "user_satisfaction"
    RESPONSE_TIME = "response_time"
    TOKEN_USAGE = "token_usage"
    COST_EFFICIENCY = "cost_efficiency"
    MODEL_PERFORMANCE = "model_performance"
    CONVERSATION_LENGTH = "conversation_length"
    ERROR_RATE = "error_rate"
    PERSONALIZATION_EFFECTIVENESS = "personalization_effectiveness"
    TEMPLATE_USAGE = "template_usage"


class QualityDimension(str, Enum):
    """Dimensions of response quality"""
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    HELPFULNESS = "helpfulness"
    CREATIVITY = "creativity"
    COHERENCE = "coherence"
    APPROPRIATENESS = "appropriateness"


class AnalyticsPeriod(str, Enum):
    """Time periods for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class QualityScore:
    """AI response quality scoring"""
    overall_score: float  # 0-1
    dimension_scores: Dict[QualityDimension, float]
    factors: Dict[str, Any]
    calculated_at: datetime
    evaluation_method: str


@dataclass
class ResponseAnalytics:
    """Analytics for individual AI responses"""
    response_id: str
    conversation_id: str
    user_id: str
    model_used: str
    provider: str
    timestamp: datetime
    
    # Quality metrics
    quality_score: Optional[QualityScore]
    user_rating: Optional[float]  # 1-5 stars
    user_feedback: Optional[str]
    
    # Performance metrics
    response_time_ms: int
    tokens_used: Dict[str, int]  # input/output tokens
    cost_estimate: float
    
    # Context metrics
    conversation_turn: int
    personalization_applied: bool
    template_used: Optional[str]
    
    # Engagement metrics
    follow_up_generated: bool
    user_continued: bool
    session_ended: bool


@dataclass
class ConversationAnalytics:
    """Analytics for entire conversations"""
    conversation_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    
    # Conversation metrics
    total_turns: int
    avg_response_time: float
    total_tokens: int
    total_cost: float
    
    # Quality metrics
    avg_quality_score: float
    user_satisfaction_rating: Optional[float]
    goal_achieved: Optional[bool]
    
    # Engagement metrics
    conversation_length_minutes: float
    user_dropout_point: Optional[int]
    successful_completion: bool


@dataclass
class ModelPerformanceMetrics:
    """Performance metrics for AI models"""
    model_name: str
    provider: str
    period_start: datetime
    period_end: datetime
    
    # Usage metrics
    total_requests: int
    total_tokens: int
    avg_response_time: float
    
    # Quality metrics
    avg_quality_score: float
    avg_user_rating: float
    success_rate: float
    
    # Cost metrics
    total_cost: float
    cost_per_token: float
    cost_per_request: float
    
    # Reliability metrics
    error_rate: float
    timeout_rate: float
    availability: float


class AIAnalyticsService:
    """Comprehensive AI analytics and quality metrics service"""
    
    def __init__(self):
        self.response_analytics: Dict[str, ResponseAnalytics] = {}
        self.conversation_analytics: Dict[str, ConversationAnalytics] = {}
        self.model_performance: Dict[str, ModelPerformanceMetrics] = {}
        self.quality_evaluators = []
        
        # Initialize analytics collectors
        asyncio.create_task(self._initialize_collectors())
    
    async def _initialize_collectors(self):
        """Initialize analytics collectors and evaluators"""
        try:
            # Initialize quality evaluators
            self.quality_evaluators = [
                self._evaluate_relevance,
                self._evaluate_accuracy,
                self._evaluate_completeness,
                self._evaluate_clarity,
                self._evaluate_helpfulness
            ]
            
            logger.info("AI Analytics Service initialized with quality evaluators")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics collectors: {e}")
    
    async def record_response_analytics(
        self,
        response_id: str,
        conversation_id: str,
        user_id: str,
        model_used: str,
        provider: str,
        response_content: str,
        prompt_content: str,
        response_time_ms: int,
        tokens_used: Dict[str, int],
        cost_estimate: float,
        conversation_turn: int,
        personalization_applied: bool = False,
        template_used: Optional[str] = None
    ) -> ResponseAnalytics:
        """Record analytics for an AI response"""
        
        try:
            # Calculate quality score
            quality_score = await self._calculate_quality_score(
                response_content, prompt_content, conversation_id
            )
            
            # Create response analytics
            analytics = ResponseAnalytics(
                response_id=response_id,
                conversation_id=conversation_id,
                user_id=user_id,
                model_used=model_used,
                provider=provider,
                timestamp=datetime.now(),
                quality_score=quality_score,
                user_rating=None,
                user_feedback=None,
                response_time_ms=response_time_ms,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                conversation_turn=conversation_turn,
                personalization_applied=personalization_applied,
                template_used=template_used,
                follow_up_generated=False,
                user_continued=False,
                session_ended=False
            )
            
            # Store analytics
            self.response_analytics[response_id] = analytics
            
            # Update conversation analytics
            await self._update_conversation_analytics(conversation_id, analytics)
            
            # Update model performance metrics
            await self._update_model_performance(model_used, provider, analytics)
            
            logger.info(f"Recorded analytics for response {response_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to record response analytics: {e}")
            raise
    
    async def _calculate_quality_score(
        self, 
        response: str, 
        prompt: str, 
        conversation_id: str
    ) -> QualityScore:
        """Calculate comprehensive quality score for AI response"""
        
        dimension_scores = {}
        factors = {}
        
        try:
            # Get conversation context for evaluation
            context_service = await get_context_service()
            context = await context_service.get_conversation_context(conversation_id)
            
            # Evaluate each quality dimension
            for evaluator in self.quality_evaluators:
                dimension, score, factor_data = await evaluator(response, prompt, context)
                dimension_scores[dimension] = score
                factors.update(factor_data)
            
            # Calculate overall score (weighted average)
            weights = {
                QualityDimension.RELEVANCE: 0.25,
                QualityDimension.ACCURACY: 0.20,
                QualityDimension.COMPLETENESS: 0.15,
                QualityDimension.CLARITY: 0.20,
                QualityDimension.HELPFULNESS: 0.20
            }
            
            overall_score = sum(
                dimension_scores.get(dim, 0.5) * weight
                for dim, weight in weights.items()
            )
            
            return QualityScore(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                factors=factors,
                calculated_at=datetime.now(),
                evaluation_method="multi_dimensional_weighted"
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {e}")
            # Return default score on error
            return QualityScore(
                overall_score=0.5,
                dimension_scores={},
                factors={"error": str(e)},
                calculated_at=datetime.now(),
                evaluation_method="fallback"
            )
    
    async def _evaluate_relevance(self, response: str, prompt: str, context: Dict) -> Tuple[QualityDimension, float, Dict]:
        """Evaluate response relevance to user query"""
        
        # Simple keyword matching for relevance
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        # Calculate word overlap
        overlap = len(prompt_words.intersection(response_words))
        relevance_score = min(overlap / max(len(prompt_words), 1), 1.0)
        
        # Boost score if response directly addresses question words
        question_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which'}
        if any(word in prompt_words for word in question_words):
            if any(word in response.lower() for word in ['because', 'since', 'due to', 'therefore']):
                relevance_score = min(relevance_score + 0.2, 1.0)
        
        factors = {
            "word_overlap": overlap,
            "prompt_words": len(prompt_words),
            "response_words": len(response_words)
        }
        
        return QualityDimension.RELEVANCE, relevance_score, factors
    
    async def _evaluate_accuracy(self, response: str, prompt: str, context: Dict) -> Tuple[QualityDimension, float, Dict]:
        """Evaluate response accuracy (simplified heuristic-based)"""
        
        # Heuristic accuracy evaluation
        accuracy_score = 0.7  # Default baseline
        
        # Boost for specific, concrete information
        if any(char.isdigit() for char in response):
            accuracy_score += 0.1
        
        # Boost for citations or references
        if any(word in response.lower() for word in ['according to', 'research shows', 'studies', 'source']):
            accuracy_score += 0.1
        
        # Penalize for uncertainty indicators without explanation
        uncertainty_words = ['might', 'possibly', 'perhaps', 'maybe']
        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        if uncertainty_count > 2:
            accuracy_score -= 0.1
        
        accuracy_score = max(0.0, min(accuracy_score, 1.0))
        
        factors = {
            "has_numbers": any(char.isdigit() for char in response),
            "has_citations": any(word in response.lower() for word in ['according to', 'research', 'source']),
            "uncertainty_count": uncertainty_count
        }
        
        return QualityDimension.ACCURACY, accuracy_score, factors
    
    async def _evaluate_completeness(self, response: str, prompt: str, context: Dict) -> Tuple[QualityDimension, float, Dict]:
        """Evaluate response completeness"""
        
        # Basic completeness evaluation
        completeness_score = 0.6  # Default baseline
        
        # Response length factor
        response_length = len(response.split())
        if response_length > 50:
            completeness_score += 0.2
        elif response_length < 10:
            completeness_score -= 0.2
        
        # Check for structured response (lists, steps, etc.)
        if any(indicator in response for indicator in ['1.', '2.', '•', '-', 'First', 'Second']):
            completeness_score += 0.1
        
        # Check for examples
        if any(word in response.lower() for word in ['example', 'instance', 'such as', 'like']):
            completeness_score += 0.1
        
        completeness_score = max(0.0, min(completeness_score, 1.0))
        
        factors = {
            "response_length": response_length,
            "has_structure": any(indicator in response for indicator in ['1.', '2.', '•', '-']),
            "has_examples": any(word in response.lower() for word in ['example', 'instance'])
        }
        
        return QualityDimension.COMPLETENESS, completeness_score, factors
    
    async def _evaluate_clarity(self, response: str, prompt: str, context: Dict) -> Tuple[QualityDimension, float, Dict]:
        """Evaluate response clarity and readability"""
        
        # Simple clarity evaluation
        clarity_score = 0.7  # Default baseline
        
        # Sentence length analysis
        sentences = response.split('.')
        avg_sentence_length = statistics.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Optimal sentence length is 15-20 words
        if 15 <= avg_sentence_length <= 20:
            clarity_score += 0.1
        elif avg_sentence_length > 30:
            clarity_score -= 0.2
        
        # Check for jargon (simplified)
        complex_words = sum(1 for word in response.split() if len(word) > 12)
        if complex_words > len(response.split()) * 0.1:  # More than 10% complex words
            clarity_score -= 0.1
        
        clarity_score = max(0.0, min(clarity_score, 1.0))
        
        factors = {
            "avg_sentence_length": avg_sentence_length,
            "complex_word_ratio": complex_words / max(len(response.split()), 1),
            "sentence_count": len(sentences)
        }
        
        return QualityDimension.CLARITY, clarity_score, factors
    
    async def _evaluate_helpfulness(self, response: str, prompt: str, context: Dict) -> Tuple[QualityDimension, float, Dict]:
        """Evaluate response helpfulness"""
        
        # Basic helpfulness evaluation
        helpfulness_score = 0.6  # Default baseline
        
        # Check for actionable advice
        action_words = ['should', 'can', 'try', 'consider', 'recommend', 'suggest', 'steps']
        if any(word in response.lower() for word in action_words):
            helpfulness_score += 0.2
        
        # Check for follow-up offers
        if any(phrase in response.lower() for phrase in ['let me know', 'feel free to ask', 'need help']):
            helpfulness_score += 0.1
        
        # Check for resources or next steps
        if any(word in response.lower() for word in ['link', 'resource', 'documentation', 'guide']):
            helpfulness_score += 0.1
        
        helpfulness_score = max(0.0, min(helpfulness_score, 1.0))
        
        factors = {
            "has_actionable_advice": any(word in response.lower() for word in action_words),
            "offers_followup": any(phrase in response.lower() for phrase in ['let me know', 'feel free']),
            "provides_resources": any(word in response.lower() for word in ['link', 'resource'])
        }
        
        return QualityDimension.HELPFULNESS, helpfulness_score, factors
    
    async def _update_conversation_analytics(self, conversation_id: str, response_analytics: ResponseAnalytics):
        """Update conversation-level analytics"""
        
        if conversation_id not in self.conversation_analytics:
            self.conversation_analytics[conversation_id] = ConversationAnalytics(
                conversation_id=conversation_id,
                user_id=response_analytics.user_id,
                start_time=response_analytics.timestamp,
                end_time=None,
                total_turns=0,
                avg_response_time=0.0,
                total_tokens=0,
                total_cost=0.0,
                avg_quality_score=0.0,
                user_satisfaction_rating=None,
                goal_achieved=None,
                conversation_length_minutes=0.0,
                user_dropout_point=None,
                successful_completion=False
            )
        
        conv_analytics = self.conversation_analytics[conversation_id]
        conv_analytics.total_turns += 1
        conv_analytics.total_tokens += sum(response_analytics.tokens_used.values())
        conv_analytics.total_cost += response_analytics.cost_estimate
        
        # Update averages
        response_times = [ra.response_time_ms for ra in self.response_analytics.values() 
                         if ra.conversation_id == conversation_id]
        conv_analytics.avg_response_time = statistics.mean(response_times)
        
        quality_scores = [ra.quality_score.overall_score for ra in self.response_analytics.values() 
                         if ra.conversation_id == conversation_id and ra.quality_score]
        if quality_scores:
            conv_analytics.avg_quality_score = statistics.mean(quality_scores)
    
    async def _update_model_performance(self, model_name: str, provider: str, response_analytics: ResponseAnalytics):
        """Update model performance metrics"""
        
        model_key = f"{provider}:{model_name}"
        
        if model_key not in self.model_performance:
            self.model_performance[model_key] = ModelPerformanceMetrics(
                model_name=model_name,
                provider=provider,
                period_start=datetime.now(),
                period_end=datetime.now(),
                total_requests=0,
                total_tokens=0,
                avg_response_time=0.0,
                avg_quality_score=0.0,
                avg_user_rating=0.0,
                success_rate=0.0,
                total_cost=0.0,
                cost_per_token=0.0,
                cost_per_request=0.0,
                error_rate=0.0,
                timeout_rate=0.0,
                availability=1.0
            )
        
        metrics = self.model_performance[model_key]
        metrics.total_requests += 1
        metrics.total_tokens += sum(response_analytics.tokens_used.values())
        metrics.total_cost += response_analytics.cost_estimate
        metrics.period_end = datetime.now()
        
        # Update averages
        model_responses = [ra for ra in self.response_analytics.values() 
                          if ra.model_used == model_name and ra.provider == provider]
        
        if model_responses:
            metrics.avg_response_time = statistics.mean([ra.response_time_ms for ra in model_responses])
            
            quality_scores = [ra.quality_score.overall_score for ra in model_responses if ra.quality_score]
            if quality_scores:
                metrics.avg_quality_score = statistics.mean(quality_scores)
            
            user_ratings = [ra.user_rating for ra in model_responses if ra.user_rating]
            if user_ratings:
                metrics.avg_user_rating = statistics.mean(user_ratings)
        
        # Update cost metrics
        if metrics.total_tokens > 0:
            metrics.cost_per_token = metrics.total_cost / metrics.total_tokens
        if metrics.total_requests > 0:
            metrics.cost_per_request = metrics.total_cost / metrics.total_requests
    
    async def record_user_feedback(
        self, 
        response_id: str, 
        user_rating: Optional[float], 
        feedback: Optional[str]
    ):
        """Record user feedback for a response"""
        
        if response_id in self.response_analytics:
            analytics = self.response_analytics[response_id]
            analytics.user_rating = user_rating
            analytics.user_feedback = feedback
            
            logger.info(f"Recorded user feedback for response {response_id}: {user_rating}/5")
        else:
            logger.warning(f"Response {response_id} not found for feedback recording")
    
    async def get_analytics_dashboard(
        self,
        period: AnalyticsPeriod,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard data"""
        
        try:
            # Calculate time range
            now = datetime.now()
            if period == AnalyticsPeriod.HOUR:
                start_time = now - timedelta(hours=1)
            elif period == AnalyticsPeriod.DAY:
                start_time = now - timedelta(days=1)
            elif period == AnalyticsPeriod.WEEK:
                start_time = now - timedelta(weeks=1)
            elif period == AnalyticsPeriod.MONTH:
                start_time = now - timedelta(days=30)
            else:
                start_time = now - timedelta(days=1)
            
            # Filter data by time range and user
            filtered_responses = [
                ra for ra in self.response_analytics.values()
                if ra.timestamp >= start_time and (not user_id or ra.user_id == user_id)
            ]
            
            if not filtered_responses:
                return self._empty_dashboard()
            
            # Calculate overview metrics
            overview = await self._calculate_overview_metrics(filtered_responses)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(filtered_responses)
            
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics(filtered_responses)
            
            # Calculate usage metrics
            usage_metrics = await self._calculate_usage_metrics(filtered_responses)
            
            # Calculate cost metrics
            cost_metrics = await self._calculate_cost_metrics(filtered_responses)
            
            # Get model comparison
            model_comparison = await self._get_model_comparison(filtered_responses)
            
            # Get trend data
            trend_data = await self._calculate_trend_data(filtered_responses, period)
            
            return {
                "period": period.value,
                "date_range": {
                    "start": start_time.isoformat(),
                    "end": now.isoformat()
                },
                "overview": overview,
                "quality_metrics": quality_metrics,
                "performance_metrics": performance_metrics,
                "usage_metrics": usage_metrics,
                "cost_metrics": cost_metrics,
                "model_comparison": model_comparison,
                "trends": trend_data,
                "generated_at": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate analytics dashboard: {e}")
            return self._empty_dashboard()
    
    async def _calculate_overview_metrics(self, responses: List[ResponseAnalytics]) -> Dict[str, Any]:
        """Calculate overview metrics"""
        
        total_responses = len(responses)
        unique_conversations = len(set(r.conversation_id for r in responses))
        unique_users = len(set(r.user_id for r in responses))
        
        avg_quality = statistics.mean([
            r.quality_score.overall_score for r in responses if r.quality_score
        ]) if responses else 0
        
        user_ratings = [r.user_rating for r in responses if r.user_rating]
        avg_user_rating = statistics.mean(user_ratings) if user_ratings else 0
        
        return {
            "total_responses": total_responses,
            "unique_conversations": unique_conversations,
            "unique_users": unique_users,
            "avg_quality_score": round(avg_quality, 3),
            "avg_user_rating": round(avg_user_rating, 2),
            "response_rate": len(user_ratings) / max(total_responses, 1)
        }
    
    async def _calculate_quality_metrics(self, responses: List[ResponseAnalytics]) -> Dict[str, Any]:
        """Calculate quality metrics breakdown"""
        
        quality_responses = [r for r in responses if r.quality_score]
        
        if not quality_responses:
            return {"dimension_scores": {}, "quality_distribution": {}}
        
        # Calculate average scores by dimension
        dimension_scores = {}
        for dimension in QualityDimension:
            scores = [
                r.quality_score.dimension_scores.get(dimension, 0)
                for r in quality_responses
                if r.quality_score.dimension_scores
            ]
            if scores:
                dimension_scores[dimension.value] = round(statistics.mean(scores), 3)
        
        # Quality distribution
        overall_scores = [r.quality_score.overall_score for r in quality_responses]
        quality_distribution = {
            "excellent": len([s for s in overall_scores if s >= 0.9]),
            "good": len([s for s in overall_scores if 0.7 <= s < 0.9]),
            "average": len([s for s in overall_scores if 0.5 <= s < 0.7]),
            "poor": len([s for s in overall_scores if s < 0.5])
        }
        
        return {
            "dimension_scores": dimension_scores,
            "quality_distribution": quality_distribution
        }
    
    async def _calculate_performance_metrics(self, responses: List[ResponseAnalytics]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        
        response_times = [r.response_time_ms for r in responses]
        
        return {
            "avg_response_time": round(statistics.mean(response_times), 2) if response_times else 0,
            "median_response_time": round(statistics.median(response_times), 2) if response_times else 0,
            "p95_response_time": round(sorted(response_times)[int(0.95 * len(response_times))], 2) if response_times else 0,
            "fast_responses": len([t for t in response_times if t < 2000]),  # Under 2 seconds
            "slow_responses": len([t for t in response_times if t > 5000])   # Over 5 seconds
        }
    
    async def _calculate_usage_metrics(self, responses: List[ResponseAnalytics]) -> Dict[str, Any]:
        """Calculate usage metrics"""
        
        # Provider distribution
        provider_counts = defaultdict(int)
        for r in responses:
            provider_counts[r.provider] += 1
        
        # Model distribution
        model_counts = defaultdict(int)
        for r in responses:
            model_counts[r.model_used] += 1
        
        # Template usage
        template_counts = defaultdict(int)
        for r in responses:
            if r.template_used:
                template_counts[r.template_used] += 1
        
        # Personalization usage
        personalized_count = len([r for r in responses if r.personalization_applied])
        
        return {
            "provider_distribution": dict(provider_counts),
            "model_distribution": dict(model_counts),
            "template_usage": dict(template_counts),
            "personalization_rate": personalized_count / max(len(responses), 1)
        }
    
    async def _calculate_cost_metrics(self, responses: List[ResponseAnalytics]) -> Dict[str, Any]:
        """Calculate cost metrics"""
        
        total_cost = sum(r.cost_estimate for r in responses)
        total_tokens = sum(sum(r.tokens_used.values()) for r in responses)
        
        return {
            "total_cost": round(total_cost, 4),
            "avg_cost_per_response": round(total_cost / max(len(responses), 1), 4),
            "total_tokens": total_tokens,
            "avg_cost_per_token": round(total_cost / max(total_tokens, 1), 6)
        }
    
    async def _get_model_comparison(self, responses: List[ResponseAnalytics]) -> List[Dict[str, Any]]:
        """Get model performance comparison"""
        
        model_stats = defaultdict(lambda: {
            "responses": [],
            "quality_scores": [],
            "response_times": [],
            "costs": [],
            "user_ratings": []
        })
        
        for r in responses:
            key = f"{r.provider}:{r.model_used}"
            model_stats[key]["responses"].append(r)
            if r.quality_score:
                model_stats[key]["quality_scores"].append(r.quality_score.overall_score)
            model_stats[key]["response_times"].append(r.response_time_ms)
            model_stats[key]["costs"].append(r.cost_estimate)
            if r.user_rating:
                model_stats[key]["user_ratings"].append(r.user_rating)
        
        comparison = []
        for model_key, stats in model_stats.items():
            provider, model = model_key.split(":", 1)
            comparison.append({
                "provider": provider,
                "model": model,
                "total_responses": len(stats["responses"]),
                "avg_quality_score": round(statistics.mean(stats["quality_scores"]), 3) if stats["quality_scores"] else 0,
                "avg_response_time": round(statistics.mean(stats["response_times"]), 2),
                "avg_cost": round(statistics.mean(stats["costs"]), 4),
                "avg_user_rating": round(statistics.mean(stats["user_ratings"]), 2) if stats["user_ratings"] else 0
            })
        
        return sorted(comparison, key=lambda x: x["avg_quality_score"], reverse=True)
    
    async def _calculate_trend_data(self, responses: List[ResponseAnalytics], period: AnalyticsPeriod) -> Dict[str, List]:
        """Calculate trend data over time"""
        
        # Group responses by time intervals
        time_groups = defaultdict(list)
        
        if period == AnalyticsPeriod.DAY:
            interval = timedelta(hours=1)
        elif period == AnalyticsPeriod.WEEK:
            interval = timedelta(days=1)
        else:
            interval = timedelta(hours=1)
        
        for r in responses:
            # Round timestamp to interval
            rounded_time = r.timestamp.replace(minute=0, second=0, microsecond=0)
            if interval == timedelta(days=1):
                rounded_time = rounded_time.replace(hour=0)
            
            time_groups[rounded_time].append(r)
        
        # Calculate trends
        timestamps = []
        quality_trend = []
        volume_trend = []
        response_time_trend = []
        
        for timestamp in sorted(time_groups.keys()):
            group_responses = time_groups[timestamp]
            
            timestamps.append(timestamp.isoformat())
            volume_trend.append(len(group_responses))
            
            quality_scores = [r.quality_score.overall_score for r in group_responses if r.quality_score]
            quality_trend.append(round(statistics.mean(quality_scores), 3) if quality_scores else 0)
            
            response_times = [r.response_time_ms for r in group_responses]
            response_time_trend.append(round(statistics.mean(response_times), 2) if response_times else 0)
        
        return {
            "timestamps": timestamps,
            "quality_trend": quality_trend,
            "volume_trend": volume_trend,
            "response_time_trend": response_time_trend
        }
    
    def _empty_dashboard(self) -> Dict[str, Any]:
        """Return empty dashboard structure"""
        return {
            "period": "day",
            "date_range": {
                "start": datetime.now().isoformat(),
                "end": datetime.now().isoformat()
            },
            "overview": {
                "total_responses": 0,
                "unique_conversations": 0,
                "unique_users": 0,
                "avg_quality_score": 0,
                "avg_user_rating": 0,
                "response_rate": 0
            },
            "quality_metrics": {"dimension_scores": {}, "quality_distribution": {}},
            "performance_metrics": {},
            "usage_metrics": {},
            "cost_metrics": {},
            "model_comparison": [],
            "trends": {"timestamps": [], "quality_trend": [], "volume_trend": []},
            "generated_at": datetime.now().isoformat()
        }


# Global service instance
_analytics_service = None

async def get_analytics_service() -> AIAnalyticsService:
    """Get global analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AIAnalyticsService()
    return _analytics_service
