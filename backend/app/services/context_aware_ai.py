"""
Task 2.2.3: Context-Aware AI Responses
Advanced AI response generation using conversation history, user profiles, and contextual intelligence.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from collections import defaultdict, Counter
import re
import hashlib

# Mock imports for dependencies that would be available in production
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
except ImportError:
    # Fallback for environments without ML libraries
    np = None
    TfidfVectorizer = None
    cosine_similarity = None
    KMeans = None

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context for AI response generation"""
    CONVERSATION_HISTORY = "conversation_history"
    USER_PROFILE = "user_profile"
    TOPIC_CONTEXT = "topic_context"
    EMOTIONAL_CONTEXT = "emotional_context"
    TEMPORAL_CONTEXT = "temporal_context"
    BEHAVIORAL_CONTEXT = "behavioral_context"

class ResponseStrategy(Enum):
    """AI response generation strategies"""
    ADAPTIVE = "adaptive"          # Adapts to user style and context
    CONVERSATIONAL = "conversational"  # Maintains conversation flow
    ANALYTICAL = "analytical"     # Data-driven responses
    CREATIVE = "creative"         # Creative and engaging responses
    PROFESSIONAL = "professional" # Formal business responses
    EDUCATIONAL = "educational"   # Teaching-focused responses

@dataclass
class ContextWindow:
    """Represents a context window for AI processing"""
    messages: List[Dict[str, Any]]
    timeframe: timedelta
    relevance_score: float
    topic_focus: str
    emotional_tone: str
    user_engagement: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'messages': self.messages,
            'timeframe_seconds': self.timeframe.total_seconds(),
            'relevance_score': self.relevance_score,
            'topic_focus': self.topic_focus,
            'emotional_tone': self.emotional_tone,
            'user_engagement': self.user_engagement
        }

@dataclass
class UserContext:
    """User-specific context for personalized responses"""
    user_id: str
    communication_style: str
    learning_style: str
    expertise_level: str
    interests: List[str]
    conversation_patterns: Dict[str, Any]
    recent_topics: List[str]
    preferred_response_length: str
    emotional_state: str
    interaction_history: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ResponseContext:
    """Complete context for generating AI responses"""
    query: str
    conversation_context: ContextWindow
    user_context: UserContext
    temporal_context: Dict[str, Any]
    topic_context: Dict[str, Any]
    strategy: ResponseStrategy
    constraints: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'conversation_context': self.conversation_context.to_dict(),
            'user_context': self.user_context.to_dict(),
            'temporal_context': self.temporal_context,
            'topic_context': self.topic_context,
            'strategy': self.strategy.value,
            'constraints': self.constraints
        }

class ContextAnalyzer:
    """Analyzes and extracts context from conversations and user data"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english') if TfidfVectorizer else None
        self.topic_cache = {}
        self.emotion_patterns = {
            'positive': ['great', 'excellent', 'love', 'amazing', 'wonderful', 'perfect'],
            'negative': ['terrible', 'awful', 'hate', 'horrible', 'disappointing', 'frustrating'],
            'neutral': ['okay', 'fine', 'average', 'normal', 'standard'],
            'excited': ['excited', 'thrilled', 'enthusiastic', 'eager', 'passionate'],
            'confused': ['confused', 'unclear', 'puzzled', 'lost', 'uncertain']
        }
    
    async def analyze_conversation_context(self, messages: List[Dict[str, Any]], 
                                         timeframe: timedelta = timedelta(hours=2)) -> ContextWindow:
        """Analyze conversation context from recent messages"""
        try:
            # Filter messages by timeframe
            cutoff_time = datetime.utcnow() - timeframe
            recent_messages = [
                msg for msg in messages 
                if datetime.fromisoformat(msg.get('timestamp', '2025-01-01')) > cutoff_time
            ]
            
            if not recent_messages:
                return ContextWindow(
                    messages=[],
                    timeframe=timeframe,
                    relevance_score=0.0,
                    topic_focus="general",
                    emotional_tone="neutral",
                    user_engagement=0.0
                )
            
            # Analyze topic focus
            topic_focus = await self._extract_topic_focus(recent_messages)
            
            # Analyze emotional tone
            emotional_tone = await self._analyze_emotional_tone(recent_messages)
            
            # Calculate relevance score
            relevance_score = await self._calculate_relevance_score(recent_messages)
            
            # Calculate user engagement
            user_engagement = await self._calculate_user_engagement(recent_messages)
            
            return ContextWindow(
                messages=recent_messages,
                timeframe=timeframe,
                relevance_score=relevance_score,
                topic_focus=topic_focus,
                emotional_tone=emotional_tone,
                user_engagement=user_engagement
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversation context: {e}")
            return ContextWindow(
                messages=messages[-5:] if messages else [],  # Fallback to last 5 messages
                timeframe=timeframe,
                relevance_score=0.5,
                topic_focus="general",
                emotional_tone="neutral",
                user_engagement=0.5
            )
    
    async def analyze_user_context(self, user_profile: Dict[str, Any], 
                                  conversation_history: List[Dict[str, Any]]) -> UserContext:
        """Analyze user-specific context from profile and history"""
        try:
            # Extract user preferences
            communication_style = user_profile.get('communication_style', 'balanced')
            learning_style = user_profile.get('learning_style', 'mixed')
            expertise_level = user_profile.get('expertise_level', 'intermediate')
            interests = user_profile.get('interests', [])
            
            # Analyze conversation patterns
            conversation_patterns = await self._analyze_conversation_patterns(conversation_history)
            
            # Extract recent topics
            recent_topics = await self._extract_recent_topics(conversation_history)
            
            # Determine preferred response length
            preferred_response_length = await self._determine_response_length_preference(conversation_history)
            
            # Analyze current emotional state
            emotional_state = await self._analyze_current_emotional_state(conversation_history)
            
            # Build interaction history summary
            interaction_history = await self._build_interaction_history(conversation_history)
            
            return UserContext(
                user_id=user_profile.get('user_id', ''),
                communication_style=communication_style,
                learning_style=learning_style,
                expertise_level=expertise_level,
                interests=interests,
                conversation_patterns=conversation_patterns,
                recent_topics=recent_topics,
                preferred_response_length=preferred_response_length,
                emotional_state=emotional_state,
                interaction_history=interaction_history
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user context: {e}")
            # Return default user context
            return UserContext(
                user_id=user_profile.get('user_id', ''),
                communication_style='balanced',
                learning_style='mixed',
                expertise_level='intermediate',
                interests=[],
                conversation_patterns={},
                recent_topics=[],
                preferred_response_length='medium',
                emotional_state='neutral',
                interaction_history={}
            )
    
    async def _extract_topic_focus(self, messages: List[Dict[str, Any]]) -> str:
        """Extract the main topic focus from messages"""
        try:
            if not messages:
                return "general"
            
            # Combine all message content
            text_content = " ".join([msg.get('content', '') for msg in messages])
            
            # Simple keyword-based topic extraction
            tech_keywords = ['python', 'javascript', 'api', 'database', 'code', 'programming', 'development']
            business_keywords = ['marketing', 'sales', 'strategy', 'revenue', 'business', 'client']
            creative_keywords = ['design', 'creative', 'art', 'writing', 'content', 'visual']
            
            text_lower = text_content.lower()
            
            tech_score = sum(1 for keyword in tech_keywords if keyword in text_lower)
            business_score = sum(1 for keyword in business_keywords if keyword in text_lower)
            creative_score = sum(1 for keyword in creative_keywords if keyword in text_lower)
            
            if tech_score > business_score and tech_score > creative_score:
                return "technology"
            elif business_score > creative_score:
                return "business"
            elif creative_score > 0:
                return "creative"
            else:
                return "general"
                
        except Exception:
            return "general"
    
    async def _analyze_emotional_tone(self, messages: List[Dict[str, Any]]) -> str:
        """Analyze the emotional tone of the conversation"""
        try:
            if not messages:
                return "neutral"
            
            text_content = " ".join([msg.get('content', '') for msg in messages])
            text_lower = text_content.lower()
            
            emotion_scores = {}
            for emotion, keywords in self.emotion_patterns.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                emotion_scores[emotion] = score
            
            # Return the emotion with the highest score, default to neutral
            if max(emotion_scores.values()) == 0:
                return "neutral"
            
            return max(emotion_scores, key=emotion_scores.get)
            
        except Exception:
            return "neutral"
    
    async def _calculate_relevance_score(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate relevance score based on message quality and coherence"""
        try:
            if not messages:
                return 0.0
            
            # Simple heuristic: score based on message length and question marks
            total_length = sum(len(msg.get('content', '')) for msg in messages)
            question_count = sum(msg.get('content', '').count('?') for msg in messages)
            
            # Normalize scores
            length_score = min(total_length / 1000, 1.0)  # Cap at 1000 chars
            question_score = min(question_count / 5, 1.0)  # Cap at 5 questions
            
            return (length_score + question_score) / 2
            
        except Exception:
            return 0.5
    
    async def _calculate_user_engagement(self, messages: List[Dict[str, Any]]) -> float:
        """Calculate user engagement level"""
        try:
            if not messages:
                return 0.0
            
            user_messages = [msg for msg in messages if msg.get('role') == 'user']
            
            if not user_messages:
                return 0.0
            
            # Calculate engagement based on message frequency and length
            avg_length = sum(len(msg.get('content', '')) for msg in user_messages) / len(user_messages)
            message_frequency = len(user_messages) / max(len(messages), 1)
            
            # Normalize scores
            length_engagement = min(avg_length / 100, 1.0)
            frequency_engagement = min(message_frequency * 2, 1.0)
            
            return (length_engagement + frequency_engagement) / 2
            
        except Exception:
            return 0.5
    
    async def _analyze_conversation_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's conversation patterns"""
        try:
            if not history:
                return {}
            
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            
            return {
                'avg_message_length': sum(len(msg.get('content', '')) for msg in user_messages) / max(len(user_messages), 1),
                'question_frequency': sum(msg.get('content', '').count('?') for msg in user_messages) / max(len(user_messages), 1),
                'exclamation_frequency': sum(msg.get('content', '').count('!') for msg in user_messages) / max(len(user_messages), 1),
                'most_active_time': 'afternoon',  # Simplified
                'preferred_topics': ['general'],  # Simplified
                'interaction_style': 'conversational'
            }
            
        except Exception:
            return {}
    
    async def _extract_recent_topics(self, history: List[Dict[str, Any]]) -> List[str]:
        """Extract recent conversation topics"""
        try:
            if not history:
                return []
            
            # Simple topic extraction from recent messages
            recent_messages = history[-10:] if len(history) > 10 else history
            topics = set()
            
            for msg in recent_messages:
                content = msg.get('content', '').lower()
                if 'python' in content or 'code' in content:
                    topics.add('programming')
                if 'business' in content or 'marketing' in content:
                    topics.add('business')
                if 'design' in content or 'creative' in content:
                    topics.add('design')
            
            return list(topics) if topics else ['general']
            
        except Exception:
            return ['general']
    
    async def _determine_response_length_preference(self, history: List[Dict[str, Any]]) -> str:
        """Determine user's preferred response length"""
        try:
            if not history:
                return 'medium'
            
            ai_messages = [msg for msg in history if msg.get('role') == 'assistant']
            user_messages = [msg for msg in history if msg.get('role') == 'user']
            
            if not ai_messages or not user_messages:
                return 'medium'
            
            avg_ai_length = sum(len(msg.get('content', '')) for msg in ai_messages) / len(ai_messages)
            avg_user_length = sum(len(msg.get('content', '')) for msg in user_messages) / len(user_messages)
            
            # If user writes long messages, they might prefer detailed responses
            if avg_user_length > 200:
                return 'long'
            elif avg_user_length < 50:
                return 'short'
            else:
                return 'medium'
                
        except Exception:
            return 'medium'
    
    async def _analyze_current_emotional_state(self, history: List[Dict[str, Any]]) -> str:
        """Analyze user's current emotional state"""
        try:
            if not history:
                return 'neutral'
            
            # Analyze recent user messages
            recent_user_messages = [
                msg for msg in history[-5:] 
                if msg.get('role') == 'user'
            ]
            
            if not recent_user_messages:
                return 'neutral'
            
            return await self._analyze_emotional_tone(recent_user_messages)
            
        except Exception:
            return 'neutral'
    
    async def _build_interaction_history(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build interaction history summary"""
        try:
            if not history:
                return {}
            
            return {
                'total_messages': len(history),
                'user_messages': len([msg for msg in history if msg.get('role') == 'user']),
                'ai_messages': len([msg for msg in history if msg.get('role') == 'assistant']),
                'first_interaction': history[0].get('timestamp', '') if history else '',
                'last_interaction': history[-1].get('timestamp', '') if history else '',
                'session_count': 1,  # Simplified
                'favorite_features': ['chat'],  # Simplified
            }
            
        except Exception:
            return {}

class ResponseGenerator:
    """Generates context-aware AI responses"""
    
    def __init__(self):
        self.strategy_prompts = {
            ResponseStrategy.ADAPTIVE: self._create_adaptive_prompt,
            ResponseStrategy.CONVERSATIONAL: self._create_conversational_prompt,
            ResponseStrategy.ANALYTICAL: self._create_analytical_prompt,
            ResponseStrategy.CREATIVE: self._create_creative_prompt,
            ResponseStrategy.PROFESSIONAL: self._create_professional_prompt,
            ResponseStrategy.EDUCATIONAL: self._create_educational_prompt,
        }
    
    async def generate_context_aware_response(self, context: ResponseContext) -> Dict[str, Any]:
        """Generate a context-aware AI response"""
        try:
            # Select appropriate strategy based on context
            strategy = await self._select_response_strategy(context)
            
            # Generate prompt with context
            prompt = await self._generate_contextual_prompt(context, strategy)
            
            # Generate response metadata
            metadata = await self._generate_response_metadata(context, strategy)
            
            return {
                'prompt': prompt,
                'strategy': strategy.value,
                'context_summary': await self._summarize_context(context),
                'metadata': metadata,
                'personalization_applied': True,
                'confidence_score': await self._calculate_confidence_score(context)
            }
            
        except Exception as e:
            logger.error(f"Error generating context-aware response: {e}")
            return {
                'prompt': f"I understand you're asking: {context.query}",
                'strategy': 'fallback',
                'context_summary': 'Limited context available',
                'metadata': {},
                'personalization_applied': False,
                'confidence_score': 0.5
            }
    
    async def _select_response_strategy(self, context: ResponseContext) -> ResponseStrategy:
        """Select the most appropriate response strategy"""
        try:
            user_style = context.user_context.communication_style.lower()
            topic_focus = context.conversation_context.topic_focus.lower()
            emotional_tone = context.conversation_context.emotional_tone.lower()
            
            # Strategy selection logic
            if 'creative' in user_style or topic_focus == 'creative':
                return ResponseStrategy.CREATIVE
            elif 'professional' in user_style or 'business' in topic_focus:
                return ResponseStrategy.PROFESSIONAL
            elif 'analytical' in user_style or 'technology' in topic_focus:
                return ResponseStrategy.ANALYTICAL
            elif context.user_context.learning_style == 'visual' or 'confused' in emotional_tone:
                return ResponseStrategy.EDUCATIONAL
            elif 'excited' in emotional_tone or context.conversation_context.user_engagement > 0.7:
                return ResponseStrategy.CONVERSATIONAL
            else:
                return ResponseStrategy.ADAPTIVE
                
        except Exception:
            return ResponseStrategy.ADAPTIVE
    
    async def _generate_contextual_prompt(self, context: ResponseContext, strategy: ResponseStrategy) -> str:
        """Generate a contextual prompt for the AI"""
        try:
            # Get strategy-specific prompt generator
            prompt_generator = self.strategy_prompts.get(strategy, self._create_adaptive_prompt)
            
            # Generate base prompt
            base_prompt = await prompt_generator(context)
            
            # Add context enrichment
            context_enrichment = await self._create_context_enrichment(context)
            
            # Combine into final prompt
            final_prompt = f"{base_prompt}\n\n{context_enrichment}\n\nUser Query: {context.query}"
            
            return final_prompt
            
        except Exception as e:
            logger.error(f"Error generating contextual prompt: {e}")
            return f"Please respond to: {context.query}"
    
    async def _create_adaptive_prompt(self, context: ResponseContext) -> str:
        """Create an adaptive prompt that adjusts to user context"""
        user_ctx = context.user_context
        conv_ctx = context.conversation_context
        
        prompt = f"""You are an AI assistant adapting to the user's communication style and preferences.

User Profile:
- Communication Style: {user_ctx.communication_style}
- Learning Style: {user_ctx.learning_style}
- Expertise Level: {user_ctx.expertise_level}
- Current Emotional State: {user_ctx.emotional_state}
- Preferred Response Length: {user_ctx.preferred_response_length}

Conversation Context:
- Topic Focus: {conv_ctx.topic_focus}
- Emotional Tone: {conv_ctx.emotional_tone}
- User Engagement: {conv_ctx.user_engagement:.2f}
- Recent Topics: {', '.join(user_ctx.recent_topics)}

Adapt your response style, tone, and detail level to match the user's preferences and current context."""
        return prompt
    
    async def _create_conversational_prompt(self, context: ResponseContext) -> str:
        """Create a conversational prompt for natural dialogue"""
        return f"""You are having a natural, engaging conversation with the user. 

Keep the tone friendly and conversational, building on the recent discussion about {context.conversation_context.topic_focus}. 
The user seems {context.conversation_context.emotional_tone} and is highly engaged.

Maintain the conversational flow while providing helpful and relevant information."""
    
    async def _create_analytical_prompt(self, context: ResponseContext) -> str:
        """Create an analytical prompt for data-driven responses"""
        return f"""You are an analytical AI assistant providing data-driven, logical responses.

Focus on:
- Clear, structured information
- Evidence-based reasoning  
- Step-by-step analysis
- Practical implications

The user has {context.user_context.expertise_level} expertise level in {context.conversation_context.topic_focus}."""
    
    async def _create_creative_prompt(self, context: ResponseContext) -> str:
        """Create a creative prompt for engaging responses"""
        return f"""You are a creative AI assistant that provides engaging, imaginative responses.

Use:
- Creative examples and analogies
- Engaging storytelling elements
- Visual descriptions when appropriate
- Interactive elements

The user appreciates creative approaches and is interested in {', '.join(context.user_context.interests)}."""
    
    async def _create_professional_prompt(self, context: ResponseContext) -> str:
        """Create a professional prompt for business contexts"""
        return f"""You are a professional AI assistant providing business-focused responses.

Maintain:
- Professional tone and language
- Structured, actionable advice
- Industry best practices
- Clear next steps

Context: {context.conversation_context.topic_focus} discussion with {context.user_context.expertise_level} expertise level."""
    
    async def _create_educational_prompt(self, context: ResponseContext) -> str:
        """Create an educational prompt for teaching-focused responses"""
        return f"""You are an educational AI assistant focused on helping users learn effectively.

Approach:
- Break down complex concepts
- Use examples and analogies
- Check for understanding
- Adapt to {context.user_context.learning_style} learning style

The user's current emotional state is {context.user_context.emotional_state}, so adjust your teaching approach accordingly."""
    
    async def _create_context_enrichment(self, context: ResponseContext) -> str:
        """Create context enrichment information"""
        try:
            enrichment_parts = []
            
            # Add conversation history context
            if context.conversation_context.messages:
                recent_topics = set()
                for msg in context.conversation_context.messages[-3:]:
                    content = msg.get('content', '')[:100]  # First 100 chars
                    if content:
                        recent_topics.add(content)
                
                if recent_topics:
                    enrichment_parts.append(f"Recent conversation context: {list(recent_topics)}")
            
            # Add user interest context
            if context.user_context.interests:
                enrichment_parts.append(f"User interests: {', '.join(context.user_context.interests)}")
            
            # Add temporal context
            if context.temporal_context:
                time_of_day = context.temporal_context.get('time_of_day', 'unknown')
                enrichment_parts.append(f"Current context: {time_of_day}")
            
            return "Context Information:\n" + "\n".join(f"- {part}" for part in enrichment_parts)
            
        except Exception:
            return "Context Information: General conversation context available."
    
    async def _generate_response_metadata(self, context: ResponseContext, strategy: ResponseStrategy) -> Dict[str, Any]:
        """Generate metadata for the response"""
        return {
            'strategy_used': strategy.value,
            'personalization_level': 'high' if context.user_context.user_id else 'low',
            'context_richness': len(context.conversation_context.messages),
            'user_engagement_level': context.conversation_context.user_engagement,
            'topic_focus': context.conversation_context.topic_focus,
            'emotional_adaptation': context.conversation_context.emotional_tone,
            'response_length_target': context.user_context.preferred_response_length,
            'expertise_adaptation': context.user_context.expertise_level
        }
    
    async def _summarize_context(self, context: ResponseContext) -> str:
        """Create a summary of the context used"""
        try:
            summary_parts = [
                f"Strategy: {context.strategy.value}",
                f"Topic: {context.conversation_context.topic_focus}",
                f"Tone: {context.conversation_context.emotional_tone}",
                f"Engagement: {context.conversation_context.user_engagement:.2f}",
                f"User Style: {context.user_context.communication_style}"
            ]
            return " | ".join(summary_parts)
        except Exception:
            return "Context summary unavailable"
    
    async def _calculate_confidence_score(self, context: ResponseContext) -> float:
        """Calculate confidence score for the response"""
        try:
            # Factors that increase confidence
            factors = []
            
            # Context availability
            if context.conversation_context.messages:
                factors.append(0.2)
            
            # User profile completeness
            if context.user_context.user_id:
                factors.append(0.2)
            
            # Recent engagement
            if context.conversation_context.user_engagement > 0.5:
                factors.append(0.2)
            
            # Topic clarity
            if context.conversation_context.topic_focus != 'general':
                factors.append(0.2)
            
            # Query clarity (simple heuristic)
            if len(context.query.split()) > 3:
                factors.append(0.2)
            
            return min(sum(factors), 1.0)
            
        except Exception:
            return 0.5

class ContextAwareAIService:
    """Main service for context-aware AI responses"""
    
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        self.response_generator = ResponseGenerator()
        self.cache = {}
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'avg_processing_time': 0,
            'context_quality_scores': []
        }
    
    async def generate_response(self, 
                               query: str,
                               user_profile: Dict[str, Any],
                               conversation_history: List[Dict[str, Any]],
                               additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a context-aware AI response"""
        start_time = datetime.utcnow()
        
        try:
            self.performance_metrics['total_requests'] += 1
            
            # Check cache
            cache_key = self._generate_cache_key(query, user_profile.get('user_id', ''))
            if cache_key in self.cache:
                self.performance_metrics['cache_hits'] += 1
                cached_response = self.cache[cache_key]
                cached_response['from_cache'] = True
                return cached_response
            
            # Analyze conversation context
            conversation_context = await self.context_analyzer.analyze_conversation_context(
                conversation_history
            )
            
            # Analyze user context
            user_context = await self.context_analyzer.analyze_user_context(
                user_profile, conversation_history
            )
            
            # Build temporal context
            temporal_context = {
                'timestamp': datetime.utcnow().isoformat(),
                'time_of_day': self._get_time_of_day(),
                'day_of_week': datetime.utcnow().strftime('%A'),
                'session_duration': self._calculate_session_duration(conversation_history)
            }
            
            # Build topic context
            topic_context = {
                'current_topic': conversation_context.topic_focus,
                'topic_transitions': await self._analyze_topic_transitions(conversation_history),
                'related_topics': user_context.recent_topics
            }
            
            # Determine response strategy
            strategy = await self.response_generator._select_response_strategy(
                ResponseContext(
                    query=query,
                    conversation_context=conversation_context,
                    user_context=user_context,
                    temporal_context=temporal_context,
                    topic_context=topic_context,
                    strategy=ResponseStrategy.ADAPTIVE,  # Will be overridden
                    constraints=additional_context or {}
                )
            )
            
            # Create complete response context
            response_context = ResponseContext(
                query=query,
                conversation_context=conversation_context,
                user_context=user_context,
                temporal_context=temporal_context,
                topic_context=topic_context,
                strategy=strategy,
                constraints=additional_context or {}
            )
            
            # Generate context-aware response
            response_data = await self.response_generator.generate_context_aware_response(
                response_context
            )
            
            # Add performance metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_metrics(processing_time, response_context)
            
            # Enhance response with additional data
            enhanced_response = {
                **response_data,
                'response_context': response_context.to_dict(),
                'processing_time_ms': processing_time * 1000,
                'quality_indicators': await self._generate_quality_indicators(response_context),
                'suggestions': await self._generate_follow_up_suggestions(response_context),
                'from_cache': False
            }
            
            # Cache the response
            self.cache[cache_key] = enhanced_response
            
            # Limit cache size
            if len(self.cache) > 1000:
                # Remove oldest entries
                oldest_keys = list(self.cache.keys())[:100]
                for key in oldest_keys:
                    del self.cache[key]
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error in context-aware AI service: {e}")
            # Return fallback response
            return {
                'prompt': f"I understand you're asking: {query}. Let me help you with that.",
                'strategy': 'fallback',
                'context_summary': 'Error processing context',
                'metadata': {},
                'personalization_applied': False,
                'confidence_score': 0.3,
                'error': str(e),
                'from_cache': False
            }
    
    async def get_context_analysis(self, user_id: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed context analysis for a user and conversation"""
        try:
            # Mock user profile for analysis
            user_profile = {
                'user_id': user_id,
                'communication_style': 'balanced',
                'learning_style': 'mixed',
                'expertise_level': 'intermediate',
                'interests': []
            }
            
            conversation_context = await self.context_analyzer.analyze_conversation_context(
                conversation_history
            )
            
            user_context = await self.context_analyzer.analyze_user_context(
                user_profile, conversation_history
            )
            
            return {
                'conversation_analysis': conversation_context.to_dict(),
                'user_analysis': user_context.to_dict(),
                'recommendations': await self._generate_context_recommendations(
                    conversation_context, user_context
                ),
                'quality_score': await self._calculate_context_quality(
                    conversation_context, user_context
                )
            }
            
        except Exception as e:
            logger.error(f"Error in context analysis: {e}")
            return {
                'error': str(e),
                'conversation_analysis': {},
                'user_analysis': {},
                'recommendations': [],
                'quality_score': 0.0
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        try:
            cache_hit_rate = (
                self.performance_metrics['cache_hits'] / 
                max(self.performance_metrics['total_requests'], 1)
            ) * 100
            
            avg_context_quality = (
                sum(self.performance_metrics['context_quality_scores']) / 
                max(len(self.performance_metrics['context_quality_scores']), 1)
            )
            
            return {
                'total_requests': self.performance_metrics['total_requests'],
                'cache_hit_rate': f"{cache_hit_rate:.1f}%",
                'average_processing_time_ms': self.performance_metrics['avg_processing_time'] * 1000,
                'average_context_quality': f"{avg_context_quality:.2f}",
                'cache_size': len(self.cache),
                'service_status': 'operational'
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'error': str(e),
                'service_status': 'error'
            }
    
    def _generate_cache_key(self, query: str, user_id: str) -> str:
        """Generate cache key for responses"""
        combined = f"{user_id}:{query[:100]}"  # Limit query length for key
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_time_of_day(self) -> str:
        """Get current time of day classification"""
        hour = datetime.utcnow().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _calculate_session_duration(self, conversation_history: List[Dict[str, Any]]) -> float:
        """Calculate current session duration in minutes"""
        try:
            if not conversation_history:
                return 0.0
            
            first_msg_time = datetime.fromisoformat(conversation_history[0].get('timestamp', '2025-01-01'))
            last_msg_time = datetime.fromisoformat(conversation_history[-1].get('timestamp', '2025-01-01'))
            
            duration = (last_msg_time - first_msg_time).total_seconds() / 60
            return max(duration, 0.0)
            
        except Exception:
            return 0.0
    
    async def _analyze_topic_transitions(self, conversation_history: List[Dict[str, Any]]) -> List[str]:
        """Analyze how topics have changed throughout the conversation"""
        try:
            if len(conversation_history) < 5:
                return []
            
            # Simple topic transition analysis
            transitions = []
            prev_topic = None
            
            # Analyze every 5 messages for topic changes
            for i in range(0, len(conversation_history), 5):
                chunk = conversation_history[i:i+5]
                current_topic = await self.context_analyzer._extract_topic_focus(chunk)
                
                if prev_topic and prev_topic != current_topic:
                    transitions.append(f"{prev_topic} -> {current_topic}")
                
                prev_topic = current_topic
            
            return transitions
            
        except Exception:
            return []
    
    def _update_performance_metrics(self, processing_time: float, context: ResponseContext):
        """Update performance metrics"""
        try:
            # Update average processing time
            current_avg = self.performance_metrics['avg_processing_time']
            total_requests = self.performance_metrics['total_requests']
            
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.performance_metrics['avg_processing_time'] = new_avg
            
            # Calculate context quality score
            quality_score = (
                context.conversation_context.relevance_score * 0.3 +
                context.conversation_context.user_engagement * 0.3 +
                (1.0 if context.user_context.user_id else 0.0) * 0.2 +
                (len(context.conversation_context.messages) / 10) * 0.2
            )
            
            self.performance_metrics['context_quality_scores'].append(min(quality_score, 1.0))
            
            # Limit context quality scores history
            if len(self.performance_metrics['context_quality_scores']) > 1000:
                self.performance_metrics['context_quality_scores'] = \
                    self.performance_metrics['context_quality_scores'][-500:]
                    
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    async def _generate_quality_indicators(self, context: ResponseContext) -> Dict[str, Any]:
        """Generate quality indicators for the response"""
        try:
            return {
                'context_richness': 'high' if len(context.conversation_context.messages) > 5 else 'low',
                'personalization_level': 'high' if context.user_context.user_id else 'none',
                'topic_clarity': 'clear' if context.conversation_context.topic_focus != 'general' else 'unclear',
                'user_engagement': 'high' if context.conversation_context.user_engagement > 0.7 else 'moderate',
                'emotional_awareness': context.conversation_context.emotional_tone,
                'strategy_match': 'optimal' if context.strategy != ResponseStrategy.ADAPTIVE else 'default'
            }
        except Exception:
            return {}
    
    async def _generate_follow_up_suggestions(self, context: ResponseContext) -> List[str]:
        """Generate follow-up suggestions based on context"""
        try:
            suggestions = []
            
            # Based on topic focus
            if context.conversation_context.topic_focus == 'technology':
                suggestions.extend([
                    "Would you like me to explain any technical concepts in more detail?",
                    "Are you interested in related programming resources?",
                    "Would you like to see some code examples?"
                ])
            elif context.conversation_context.topic_focus == 'business':
                suggestions.extend([
                    "Would you like to explore business implications further?",
                    "Are you interested in market analysis or trends?",
                    "Would strategic recommendations be helpful?"
                ])
            
            # Based on user engagement
            if context.conversation_context.user_engagement > 0.8:
                suggestions.append("You seem very engaged! What aspect interests you most?")
            elif context.conversation_context.user_engagement < 0.3:
                suggestions.append("Would you like me to approach this differently?")
            
            # Based on learning style
            if context.user_context.learning_style == 'visual':
                suggestions.append("Would visual examples or diagrams be helpful?")
            elif context.user_context.learning_style == 'hands-on':
                suggestions.append("Would you like to try a practical exercise?")
            
            return suggestions[:3]  # Limit to 3 suggestions
            
        except Exception:
            return []
    
    async def _generate_context_recommendations(self, conv_context: ContextWindow, 
                                               user_context: UserContext) -> List[str]:
        """Generate recommendations for improving context"""
        try:
            recommendations = []
            
            # Check context completeness
            if conv_context.relevance_score < 0.5:
                recommendations.append("Consider providing more specific information in your queries")
            
            if user_context.communication_style == 'balanced':
                recommendations.append("Your communication style could be further personalized")
            
            if not user_context.interests:
                recommendations.append("Adding interests to your profile would improve personalization")
            
            if conv_context.user_engagement < 0.5:
                recommendations.append("Try asking more specific questions to get better responses")
            
            return recommendations
            
        except Exception:
            return []
    
    async def _calculate_context_quality(self, conv_context: ContextWindow, 
                                        user_context: UserContext) -> float:
        """Calculate overall context quality score"""
        try:
            factors = []
            
            # Conversation context quality
            factors.append(conv_context.relevance_score * 0.25)
            factors.append(conv_context.user_engagement * 0.25)
            
            # User context quality
            factors.append((1.0 if user_context.user_id else 0.0) * 0.2)
            factors.append((len(user_context.interests) / 5) * 0.1)  # Up to 5 interests
            factors.append((1.0 if user_context.communication_style != 'balanced' else 0.5) * 0.1)
            factors.append((len(conv_context.messages) / 10) * 0.1)  # Up to 10 messages
            
            return min(sum(factors), 1.0)
            
        except Exception:
            return 0.0

# Global service instance
context_aware_ai_service = ContextAwareAIService()

# Export main functions
__all__ = [
    'ContextType',
    'ResponseStrategy', 
    'ContextWindow',
    'UserContext',
    'ResponseContext',
    'ContextAnalyzer',
    'ResponseGenerator',
    'ContextAwareAIService',
    'context_aware_ai_service'
]
