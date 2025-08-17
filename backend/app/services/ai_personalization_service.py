"""
Task 2.1.4: AI Personalization Service
=====================================

Advanced AI personalization system that adapts to individual users:
- User behavior pattern analysis
- Dynamic communication style adaptation
- Learning preference detection
- Expertise level tracking
- Response style customization
- Personal AI assistant creation
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

from app.services.conversation_context_service import get_context_service, ContextType
from app.services.multi_provider_ai_service import MultiProviderAIService, ModelProvider

logger = logging.getLogger(__name__)


class LearningStyle(str, Enum):
    """User learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"


class CommunicationStyle(str, Enum):
    """Communication style preferences"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    SIMPLE = "simple"


class ExpertiseLevel(str, Enum):
    """User expertise levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PersonalityTrait(str, Enum):
    """AI personality traits"""
    HELPFUL = "helpful"
    PATIENT = "patient"
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    DIRECT = "direct"
    DETAILED = "detailed"
    CONCISE = "concise"


@dataclass
class UserPersonalityProfile:
    """Comprehensive user personality and preference profile"""
    user_id: str
    learning_style: LearningStyle
    communication_style: CommunicationStyle
    expertise_level: ExpertiseLevel
    preferred_response_length: str  # short, medium, long
    topics_of_interest: List[str]
    interaction_patterns: Dict[str, Any]
    personality_traits: List[PersonalityTrait]
    preferred_providers: List[str]
    preferred_models: List[str]
    response_preferences: Dict[str, Any]
    learning_goals: List[str]
    created_at: datetime
    updated_at: datetime
    confidence_score: float  # How confident we are in this profile (0-1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'user_id': self.user_id,
            'learning_style': self.learning_style.value,
            'communication_style': self.communication_style.value,
            'expertise_level': self.expertise_level.value,
            'preferred_response_length': self.preferred_response_length,
            'topics_of_interest': self.topics_of_interest,
            'interaction_patterns': self.interaction_patterns,
            'personality_traits': [trait.value for trait in self.personality_traits],
            'preferred_providers': self.preferred_providers,
            'preferred_models': self.preferred_models,
            'response_preferences': self.response_preferences,
            'learning_goals': self.learning_goals,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confidence_score': self.confidence_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPersonalityProfile':
        """Create from dictionary"""
        return cls(
            user_id=data['user_id'],
            learning_style=LearningStyle(data['learning_style']),
            communication_style=CommunicationStyle(data['communication_style']),
            expertise_level=ExpertiseLevel(data['expertise_level']),
            preferred_response_length=data['preferred_response_length'],
            topics_of_interest=data['topics_of_interest'],
            interaction_patterns=data['interaction_patterns'],
            personality_traits=[PersonalityTrait(trait) for trait in data['personality_traits']],
            preferred_providers=data['preferred_providers'],
            preferred_models=data['preferred_models'],
            response_preferences=data['response_preferences'],
            learning_goals=data['learning_goals'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            confidence_score=data['confidence_score']
        )


@dataclass
class PersonalizedPrompt:
    """Personalized prompt template for specific users"""
    prompt_id: str
    user_id: str
    base_prompt: str
    personalization_rules: Dict[str, Any]
    generated_prompt: str
    effectiveness_score: float  # How well this prompt works for the user
    usage_count: int
    created_at: datetime
    last_used: datetime


class AIPersonalizationService:
    """Service for AI personalization and user adaptation"""
    
    def __init__(self):
        self.context_service = None
        self.ai_service = MultiProviderAIService()
        self.personality_cache = {}  # In-memory cache for active profiles
        self.prompt_templates = self._load_prompt_templates()
        
    async def initialize(self):
        """Initialize the personalization service"""
        self.context_service = await get_context_service()
        logger.info("AI Personalization Service initialized")
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load base prompt templates for personalization"""
        return {
            'general_chat': "You are a helpful AI assistant. Respond to the user's question or request.",
            'code_help': "You are a programming assistant. Help the user with their coding question.",
            'learning': "You are a patient teacher. Help the user learn about the topic they're asking about.",
            'analysis': "You are an analytical assistant. Provide detailed analysis of the user's request.",
            'creative': "You are a creative assistant. Help the user with their creative endeavor.",
            'problem_solving': "You are a problem-solving assistant. Help the user find solutions to their challenge."
        }
    
    async def analyze_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user interaction patterns from conversation history"""
        try:
            # Get user's conversation history
            conversations = await self.context_service.get_conversation_history(user_id, limit=50)
            
            if not conversations:
                return self._get_default_patterns()
            
            patterns = {
                'message_length_preference': 'medium',
                'question_types': [],
                'response_engagement': 0.5,
                'topic_interests': [],
                'time_patterns': {},
                'interaction_style': 'neutral',
                'learning_indicators': []
            }
            
            # Analyze message patterns (this would be enhanced with actual conversation data)
            # For now, return patterns based on context service data
            user_prefs = await self.context_service.get_user_preferences(user_id)
            
            if user_prefs:
                patterns.update({
                    'message_length_preference': user_prefs.get('response_length_preference', 'medium'),
                    'topic_interests': user_prefs.get('topics_of_interest', []),
                    'interaction_style': user_prefs.get('communication_style', 'professional')
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze user patterns: {e}")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Get default interaction patterns for new users"""
        return {
            'message_length_preference': 'medium',
            'question_types': ['general'],
            'response_engagement': 0.5,
            'topic_interests': [],
            'time_patterns': {},
            'interaction_style': 'professional',
            'learning_indicators': []
        }
    
    async def create_personality_profile(self, user_id: str) -> UserPersonalityProfile:
        """Create or update a user's personality profile"""
        try:
            # Analyze user patterns
            patterns = await self.analyze_user_patterns(user_id)
            
            # Get existing preferences
            user_prefs = await self.context_service.get_user_preferences(user_id)
            
            # Determine learning style
            learning_style = self._infer_learning_style(patterns, user_prefs)
            
            # Determine communication style
            comm_style = self._infer_communication_style(patterns, user_prefs)
            
            # Determine expertise level
            expertise = self._infer_expertise_level(patterns, user_prefs)
            
            # Determine personality traits
            traits = self._infer_personality_traits(patterns, user_prefs)
            
            # Create profile
            profile = UserPersonalityProfile(
                user_id=user_id,
                learning_style=learning_style,
                communication_style=comm_style,
                expertise_level=expertise,
                preferred_response_length=patterns.get('message_length_preference', 'medium'),
                topics_of_interest=patterns.get('topic_interests', []),
                interaction_patterns=patterns,
                personality_traits=traits,
                preferred_providers=user_prefs.get('preferred_ai_provider', ['openai']) if isinstance(user_prefs.get('preferred_ai_provider'), list) else [user_prefs.get('preferred_ai_provider', 'openai')],
                preferred_models=user_prefs.get('preferred_ai_model', ['gpt-4']) if isinstance(user_prefs.get('preferred_ai_model'), list) else [user_prefs.get('preferred_ai_model', 'gpt-4')],
                response_preferences={
                    'include_examples': expertise in [ExpertiseLevel.BEGINNER, ExpertiseLevel.INTERMEDIATE],
                    'detailed_explanations': expertise == ExpertiseLevel.BEGINNER,
                    'step_by_step': learning_style in [LearningStyle.READING_WRITING, LearningStyle.KINESTHETIC],
                    'visual_aids': learning_style == LearningStyle.VISUAL,
                    'concise_summaries': comm_style == CommunicationStyle.PROFESSIONAL
                },
                learning_goals=self._infer_learning_goals(patterns, user_prefs),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                confidence_score=self._calculate_confidence_score(patterns, user_prefs)
            )
            
            # Store profile
            await self._store_personality_profile(profile)
            
            # Cache profile
            self.personality_cache[user_id] = profile
            
            logger.info(f"Created personality profile for user {user_id} with confidence {profile.confidence_score:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create personality profile: {e}")
            return self._get_default_profile(user_id)
    
    def _infer_learning_style(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> LearningStyle:
        """Infer user's learning style from patterns"""
        # Simple heuristics - would be enhanced with ML in production
        if 'visual' in str(prefs.get('topics_of_interest', [])).lower():
            return LearningStyle.VISUAL
        elif patterns.get('question_types') and 'how-to' in patterns['question_types']:
            return LearningStyle.KINESTHETIC
        elif patterns.get('message_length_preference') == 'long':
            return LearningStyle.READING_WRITING
        else:
            return LearningStyle.MULTIMODAL
    
    def _infer_communication_style(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> CommunicationStyle:
        """Infer user's preferred communication style"""
        interaction_style = patterns.get('interaction_style', 'professional')
        
        if interaction_style in ['casual', 'friendly']:
            return CommunicationStyle.CASUAL
        elif interaction_style == 'formal':
            return CommunicationStyle.FORMAL
        elif interaction_style == 'technical':
            return CommunicationStyle.TECHNICAL
        else:
            return CommunicationStyle.PROFESSIONAL
    
    def _infer_expertise_level(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> ExpertiseLevel:
        """Infer user's expertise level"""
        topics = prefs.get('topics_of_interest', [])
        
        # Simple heuristics
        if len(topics) > 5:
            return ExpertiseLevel.ADVANCED
        elif len(topics) > 2:
            return ExpertiseLevel.INTERMEDIATE
        else:
            return ExpertiseLevel.BEGINNER
    
    def _infer_personality_traits(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> List[PersonalityTrait]:
        """Infer which AI personality traits would work best for this user"""
        traits = [PersonalityTrait.HELPFUL]  # Always helpful
        
        comm_style = patterns.get('interaction_style', 'professional')
        
        if comm_style == 'casual':
            traits.extend([PersonalityTrait.FRIENDLY, PersonalityTrait.ENCOURAGING])
        elif comm_style == 'technical':
            traits.extend([PersonalityTrait.ANALYTICAL, PersonalityTrait.DETAILED])
        elif comm_style == 'formal':
            traits.extend([PersonalityTrait.PROFESSIONAL, PersonalityTrait.DIRECT])
        else:
            traits.extend([PersonalityTrait.PATIENT, PersonalityTrait.DETAILED])
        
        return traits
    
    def _infer_learning_goals(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> List[str]:
        """Infer user's learning goals"""
        topics = prefs.get('topics_of_interest', [])
        goals = []
        
        for topic in topics:
            if topic.lower() in ['python', 'programming', 'coding']:
                goals.append('Learn programming fundamentals')
            elif topic.lower() in ['data', 'analysis', 'analytics']:
                goals.append('Master data analysis')
            elif topic.lower() in ['ai', 'machine learning', 'ml']:
                goals.append('Understand AI/ML concepts')
        
        if not goals:
            goals.append('General knowledge improvement')
        
        return goals
    
    def _calculate_confidence_score(self, patterns: Dict[str, Any], prefs: Dict[str, Any]) -> float:
        """Calculate confidence in the personality profile"""
        score = 0.5  # Base confidence
        
        # Increase confidence based on available data
        if prefs.get('topics_of_interest'):
            score += 0.2
        if patterns.get('interaction_style') != 'neutral':
            score += 0.1
        if len(patterns.get('topic_interests', [])) > 2:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _store_personality_profile(self, profile: UserPersonalityProfile):
        """Store personality profile in Redis"""
        if not self.context_service or not self.context_service.redis_client:
            return
        
        try:
            profile_key = f"personality:{profile.user_id}"
            profile_data = json.dumps(profile.to_dict(), default=str)
            
            await self.context_service.redis_client.setex(
                profile_key,
                86400 * 90,  # 90 days TTL
                profile_data
            )
            
        except Exception as e:
            logger.error(f"Failed to store personality profile: {e}")
    
    async def get_personality_profile(self, user_id: str) -> Optional[UserPersonalityProfile]:
        """Get user's personality profile"""
        try:
            # Check cache first
            if user_id in self.personality_cache:
                return self.personality_cache[user_id]
            
            # Try to load from Redis
            if self.context_service and self.context_service.redis_client:
                profile_key = f"personality:{user_id}"
                profile_data = await self.context_service.redis_client.get(profile_key)
                
                if profile_data:
                    profile_dict = json.loads(profile_data)
                    profile = UserPersonalityProfile.from_dict(profile_dict)
                    self.personality_cache[user_id] = profile
                    return profile
            
            # Create new profile if none exists
            return await self.create_personality_profile(user_id)
            
        except Exception as e:
            logger.error(f"Failed to get personality profile: {e}")
            return self._get_default_profile(user_id)
    
    def _get_default_profile(self, user_id: str) -> UserPersonalityProfile:
        """Get default personality profile for new users"""
        return UserPersonalityProfile(
            user_id=user_id,
            learning_style=LearningStyle.MULTIMODAL,
            communication_style=CommunicationStyle.PROFESSIONAL,
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            preferred_response_length='medium',
            topics_of_interest=[],
            interaction_patterns=self._get_default_patterns(),
            personality_traits=[PersonalityTrait.HELPFUL, PersonalityTrait.PATIENT],
            preferred_providers=['openai'],
            preferred_models=['gpt-4'],
            response_preferences={
                'include_examples': True,
                'detailed_explanations': False,
                'step_by_step': False,
                'visual_aids': False,
                'concise_summaries': True
            },
            learning_goals=['General assistance'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            confidence_score=0.3
        )
    
    async def personalize_prompt(
        self,
        base_prompt: str,
        user_id: str,
        context_type: str = 'general_chat'
    ) -> str:
        """Personalize a prompt based on user's personality profile"""
        try:
            profile = await self.get_personality_profile(user_id)
            
            if not profile:
                return base_prompt
            
            # Build personalized prompt
            personalized_parts = []
            
            # Add personality context
            personality_context = self._build_personality_context(profile)
            personalized_parts.append(personality_context)
            
            # Add learning context
            learning_context = self._build_learning_context(profile)
            if learning_context:
                personalized_parts.append(learning_context)
            
            # Add communication style context
            comm_context = self._build_communication_context(profile)
            if comm_context:
                personalized_parts.append(comm_context)
            
            # Combine with base prompt
            if personalized_parts:
                personalization = "\n".join(personalized_parts)
                personalized_prompt = f"{personalization}\n\n{base_prompt}"
            else:
                personalized_prompt = base_prompt
            
            logger.debug(f"Personalized prompt for user {user_id} (confidence: {profile.confidence_score:.2f})")
            return personalized_prompt
            
        except Exception as e:
            logger.error(f"Failed to personalize prompt: {e}")
            return base_prompt
    
    def _build_personality_context(self, profile: UserPersonalityProfile) -> str:
        """Build personality context for prompts"""
        traits_text = ", ".join([trait.value for trait in profile.personality_traits])
        
        context = f"You are an AI assistant with the following personality traits: {traits_text}. "
        
        if profile.expertise_level == ExpertiseLevel.BEGINNER:
            context += "The user is a beginner, so explain concepts clearly and provide examples. "
        elif profile.expertise_level == ExpertiseLevel.ADVANCED:
            context += "The user is advanced, so you can use technical terminology and assume prior knowledge. "
        
        return context
    
    def _build_learning_context(self, profile: UserPersonalityProfile) -> str:
        """Build learning style context for prompts"""
        learning_style = profile.learning_style
        
        if learning_style == LearningStyle.VISUAL:
            return "When possible, describe things visually or suggest visual aids. "
        elif learning_style == LearningStyle.KINESTHETIC:
            return "Provide hands-on examples and step-by-step instructions. "
        elif learning_style == LearningStyle.READING_WRITING:
            return "Provide detailed written explanations and encourage note-taking. "
        else:
            return ""
    
    def _build_communication_context(self, profile: UserPersonalityProfile) -> str:
        """Build communication style context for prompts"""
        comm_style = profile.communication_style
        
        if comm_style == CommunicationStyle.CASUAL:
            return "Use a casual, friendly tone in your responses. "
        elif comm_style == CommunicationStyle.FORMAL:
            return "Use a formal, professional tone in your responses. "
        elif comm_style == CommunicationStyle.TECHNICAL:
            return "Use precise, technical language appropriate for the domain. "
        elif comm_style == CommunicationStyle.SIMPLE:
            return "Use simple, clear language and avoid jargon. "
        else:
            return "Use a professional but approachable tone. "
    
    async def adapt_ai_parameters(
        self,
        user_id: str,
        base_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt AI parameters based on user personality"""
        try:
            profile = await self.get_personality_profile(user_id)
            
            if not profile:
                return base_params
            
            adapted_params = base_params.copy()
            
            # Adjust temperature based on personality
            if PersonalityTrait.CREATIVE in profile.personality_traits:
                adapted_params['temperature'] = min(adapted_params.get('temperature', 0.7) + 0.2, 1.0)
            elif PersonalityTrait.ANALYTICAL in profile.personality_traits:
                adapted_params['temperature'] = max(adapted_params.get('temperature', 0.7) - 0.2, 0.0)
            
            # Adjust max_tokens based on response length preference
            length_pref = profile.preferred_response_length
            current_tokens = adapted_params.get('max_tokens', 1000)
            
            if length_pref == 'short':
                adapted_params['max_tokens'] = min(current_tokens, 500)
            elif length_pref == 'long':
                adapted_params['max_tokens'] = max(current_tokens, 1500)
            
            # Select preferred model if available
            if profile.preferred_models and profile.preferred_models[0]:
                adapted_params['model'] = profile.preferred_models[0]
            
            return adapted_params
            
        except Exception as e:
            logger.error(f"Failed to adapt AI parameters: {e}")
            return base_params
    
    async def update_profile_from_interaction(
        self,
        user_id: str,
        interaction_data: Dict[str, Any]
    ):
        """Update user profile based on interaction feedback"""
        try:
            profile = await self.get_personality_profile(user_id)
            
            if not profile:
                return
            
            # Update confidence score based on interaction success
            if interaction_data.get('positive_feedback', False):
                profile.confidence_score = min(profile.confidence_score + 0.05, 1.0)
            elif interaction_data.get('negative_feedback', False):
                profile.confidence_score = max(profile.confidence_score - 0.05, 0.1)
            
            # Update interaction patterns
            if 'response_time' in interaction_data:
                profile.interaction_patterns['avg_response_time'] = interaction_data['response_time']
            
            # Update topics of interest
            if 'topic' in interaction_data and interaction_data['topic'] not in profile.topics_of_interest:
                profile.topics_of_interest.append(interaction_data['topic'])
            
            profile.updated_at = datetime.now()
            
            # Store updated profile
            await self._store_personality_profile(profile)
            self.personality_cache[user_id] = profile
            
            logger.debug(f"Updated profile for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update profile from interaction: {e}")


# Global instance
_personalization_service: Optional[AIPersonalizationService] = None


async def get_personalization_service() -> AIPersonalizationService:
    """Get or create the global personalization service instance"""
    global _personalization_service
    
    if _personalization_service is None:
        _personalization_service = AIPersonalizationService()
        await _personalization_service.initialize()
    
    return _personalization_service


async def initialize_personalization_service():
    """Initialize the personalization service on startup"""
    await get_personalization_service()
    logger.info("✅ AI Personalization Service initialized - Task 2.1.4")
