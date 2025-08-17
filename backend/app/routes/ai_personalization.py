"""
Task 2.1.4: AI Personalization API Routes
=========================================

API endpoints for managing AI personalization:
- Personality profile management
- Personalization preferences
- Learning goal tracking
- Behavior adaptation controls
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from app.services.ai_personalization_service import (
    get_personalization_service,
    UserPersonalityProfile,
    LearningStyle,
    CommunicationStyle,
    ExpertiseLevel,
    PersonalityTrait
)
from app.dependencies import get_current_user
# Import User directly from models.py to avoid circular import issues
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/personalization", tags=["AI Personalization"])


class PersonalityProfileResponse(BaseModel):
    """Response model for personality profiles"""
    user_id: str
    learning_style: str
    communication_style: str
    expertise_level: str
    preferred_response_length: str
    topics_of_interest: List[str]
    personality_traits: List[str]
    preferred_providers: List[str]
    preferred_models: List[str]
    response_preferences: Dict[str, Any]
    learning_goals: List[str]
    confidence_score: float
    created_at: str
    updated_at: str


class UpdatePersonalityRequest(BaseModel):
    """Request model for updating personality preferences"""
    learning_style: Optional[str] = Field(None, description="Preferred learning style")
    communication_style: Optional[str] = Field(None, description="Preferred communication style")
    expertise_level: Optional[str] = Field(None, description="User expertise level")
    preferred_response_length: Optional[str] = Field(None, description="Preferred response length (short/medium/long)")
    topics_of_interest: Optional[List[str]] = Field(None, description="Topics of interest")
    personality_traits: Optional[List[str]] = Field(None, description="Preferred AI personality traits")
    preferred_providers: Optional[List[str]] = Field(None, description="Preferred AI providers")
    preferred_models: Optional[List[str]] = Field(None, description="Preferred AI models")
    learning_goals: Optional[List[str]] = Field(None, description="Learning goals")


class PersonalizationSettingsResponse(BaseModel):
    """Response model for personalization settings"""
    personalization_enabled: bool
    auto_adapt_enabled: bool
    learning_tracking_enabled: bool
    profile_confidence: float
    last_updated: Optional[str]


class PersonalizedChatRequest(BaseModel):
    """Request model for personalized chat"""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Response creativity")
    max_tokens: Optional[int] = Field(None, ge=1, le=8192, description="Maximum response length")
    use_personalization: bool = Field(True, description="Apply personalization")


class PersonalizedChatResponse(BaseModel):
    """Response model for personalized chat"""
    response: str
    model_used: str
    provider_used: str
    personalization_applied: bool
    personality_confidence: float
    conversation_id: str
    response_time_ms: int
    tokens_used: Dict[str, int]


@router.get("/profile", response_model=PersonalityProfileResponse)
async def get_personality_profile(current_user: User = Depends(get_current_user)):
    """Get user's personality profile"""
    try:
        personalization_service = await get_personalization_service()
        profile = await personalization_service.get_personality_profile(str(current_user.id))
        
        if not profile:
            raise HTTPException(status_code=404, detail="Personality profile not found")
        
        return PersonalityProfileResponse(
            user_id=profile.user_id,
            learning_style=profile.learning_style.value,
            communication_style=profile.communication_style.value,
            expertise_level=profile.expertise_level.value,
            preferred_response_length=profile.preferred_response_length,
            topics_of_interest=profile.topics_of_interest,
            personality_traits=[trait.value for trait in profile.personality_traits],
            preferred_providers=profile.preferred_providers,
            preferred_models=profile.preferred_models,
            response_preferences=profile.response_preferences,
            learning_goals=profile.learning_goals,
            confidence_score=profile.confidence_score,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to get personality profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve personality profile")


@router.post("/profile", response_model=PersonalityProfileResponse)
async def create_personality_profile(current_user: User = Depends(get_current_user)):
    """Create or refresh user's personality profile"""
    try:
        personalization_service = await get_personalization_service()
        profile = await personalization_service.create_personality_profile(str(current_user.id))
        
        return PersonalityProfileResponse(
            user_id=profile.user_id,
            learning_style=profile.learning_style.value,
            communication_style=profile.communication_style.value,
            expertise_level=profile.expertise_level.value,
            preferred_response_length=profile.preferred_response_length,
            topics_of_interest=profile.topics_of_interest,
            personality_traits=[trait.value for trait in profile.personality_traits],
            preferred_providers=profile.preferred_providers,
            preferred_models=profile.preferred_models,
            response_preferences=profile.response_preferences,
            learning_goals=profile.learning_goals,
            confidence_score=profile.confidence_score,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to create personality profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to create personality profile")


@router.put("/profile", response_model=PersonalityProfileResponse)
async def update_personality_profile(
    update_request: UpdatePersonalityRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's personality profile preferences"""
    try:
        personalization_service = await get_personalization_service()
        profile = await personalization_service.get_personality_profile(str(current_user.id))
        
        if not profile:
            raise HTTPException(status_code=404, detail="Personality profile not found")
        
        # Update profile fields
        if update_request.learning_style:
            try:
                profile.learning_style = LearningStyle(update_request.learning_style)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid learning style")
        
        if update_request.communication_style:
            try:
                profile.communication_style = CommunicationStyle(update_request.communication_style)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid communication style")
        
        if update_request.expertise_level:
            try:
                profile.expertise_level = ExpertiseLevel(update_request.expertise_level)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid expertise level")
        
        if update_request.preferred_response_length:
            if update_request.preferred_response_length not in ['short', 'medium', 'long']:
                raise HTTPException(status_code=400, detail="Invalid response length preference")
            profile.preferred_response_length = update_request.preferred_response_length
        
        if update_request.topics_of_interest is not None:
            profile.topics_of_interest = update_request.topics_of_interest
        
        if update_request.personality_traits:
            try:
                profile.personality_traits = [PersonalityTrait(trait) for trait in update_request.personality_traits]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid personality trait")
        
        if update_request.preferred_providers is not None:
            profile.preferred_providers = update_request.preferred_providers
        
        if update_request.preferred_models is not None:
            profile.preferred_models = update_request.preferred_models
        
        if update_request.learning_goals is not None:
            profile.learning_goals = update_request.learning_goals
        
        # Update timestamp and confidence
        profile.updated_at = datetime.now()
        profile.confidence_score = min(profile.confidence_score + 0.1, 1.0)  # Increase confidence for manual updates
        
        # Store updated profile
        await personalization_service._store_personality_profile(profile)
        personalization_service.personality_cache[str(current_user.id)] = profile
        
        return PersonalityProfileResponse(
            user_id=profile.user_id,
            learning_style=profile.learning_style.value,
            communication_style=profile.communication_style.value,
            expertise_level=profile.expertise_level.value,
            preferred_response_length=profile.preferred_response_length,
            topics_of_interest=profile.topics_of_interest,
            personality_traits=[trait.value for trait in profile.personality_traits],
            preferred_providers=profile.preferred_providers,
            preferred_models=profile.preferred_models,
            response_preferences=profile.response_preferences,
            learning_goals=profile.learning_goals,
            confidence_score=profile.confidence_score,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update personality profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update personality profile")


@router.post("/chat", response_model=PersonalizedChatResponse)
async def personalized_chat(
    chat_request: PersonalizedChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate personalized AI response"""
    try:
        from app.services.multi_provider_ai_service import MultiProviderAIService
        import uuid
        
        # Initialize services
        ai_service = MultiProviderAIService()
        personalization_service = await get_personalization_service()
        
        # Get or create conversation ID
        conversation_id = chat_request.conversation_id or str(uuid.uuid4())
        
        # Prepare messages
        messages = [{"role": "user", "content": chat_request.message}]
        
        # Generate personalized response
        response = await ai_service.generate_response(
            messages=messages,
            model=chat_request.model,
            temperature=chat_request.temperature,
            max_tokens=chat_request.max_tokens,
            user_id=str(current_user.id),
            conversation_id=conversation_id,
            use_context=True,
            use_personalization=chat_request.use_personalization
        )
        
        # Get personality confidence
        profile = await personalization_service.get_personality_profile(str(current_user.id))
        personality_confidence = profile.confidence_score if profile else 0.0
        
        return PersonalizedChatResponse(
            response=response.content,
            model_used=response.model,
            provider_used=response.provider.value,
            personalization_applied=chat_request.use_personalization,
            personality_confidence=personality_confidence,
            conversation_id=conversation_id,
            response_time_ms=response.response_time_ms,
            tokens_used=response.usage
        )
        
    except Exception as e:
        logger.error(f"Failed to generate personalized chat response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate personalized response")


@router.get("/settings", response_model=PersonalizationSettingsResponse)
async def get_personalization_settings(current_user: User = Depends(get_current_user)):
    """Get user's personalization settings"""
    try:
        personalization_service = await get_personalization_service()
        profile = await personalization_service.get_personality_profile(str(current_user.id))
        
        return PersonalizationSettingsResponse(
            personalization_enabled=True,  # Always enabled in this implementation
            auto_adapt_enabled=True,
            learning_tracking_enabled=True,
            profile_confidence=profile.confidence_score if profile else 0.0,
            last_updated=profile.updated_at.isoformat() if profile else None
        )
        
    except Exception as e:
        logger.error(f"Failed to get personalization settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve personalization settings")


@router.get("/learning-styles")
async def get_learning_styles():
    """Get available learning styles"""
    return {
        "learning_styles": [
            {"value": style.value, "name": style.value.replace("_", " ").title()}
            for style in LearningStyle
        ]
    }


@router.get("/communication-styles")
async def get_communication_styles():
    """Get available communication styles"""
    return {
        "communication_styles": [
            {"value": style.value, "name": style.value.replace("_", " ").title()}
            for style in CommunicationStyle
        ]
    }


@router.get("/expertise-levels")
async def get_expertise_levels():
    """Get available expertise levels"""
    return {
        "expertise_levels": [
            {"value": level.value, "name": level.value.title()}
            for level in ExpertiseLevel
        ]
    }


@router.get("/personality-traits")
async def get_personality_traits():
    """Get available personality traits"""
    return {
        "personality_traits": [
            {"value": trait.value, "name": trait.value.replace("_", " ").title()}
            for trait in PersonalityTrait
        ]
    }


@router.post("/feedback")
async def provide_personalization_feedback(
    feedback_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Provide feedback on AI responses for personalization improvement"""
    try:
        personalization_service = await get_personalization_service()
        
        # Process feedback
        interaction_data = {
            'positive_feedback': feedback_data.get('positive', False),
            'negative_feedback': feedback_data.get('negative', False),
            'response_rating': feedback_data.get('rating', 0),
            'topic': feedback_data.get('topic', 'general'),
            'feedback_text': feedback_data.get('feedback_text', '')
        }
        
        await personalization_service.update_profile_from_interaction(
            user_id=str(current_user.id),
            interaction_data=interaction_data
        )
        
        return {"status": "success", "message": "Feedback recorded successfully"}
        
    except Exception as e:
        logger.error(f"Failed to record personalization feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@router.get("/analytics")
async def get_personalization_analytics(current_user: User = Depends(get_current_user)):
    """Get personalization analytics and insights"""
    try:
        personalization_service = await get_personalization_service()
        profile = await personalization_service.get_personality_profile(str(current_user.id))
        
        if not profile:
            raise HTTPException(status_code=404, detail="Personality profile not found")
        
        # Calculate analytics
        analytics = {
            "profile_completion": {
                "confidence_score": profile.confidence_score,
                "topics_identified": len(profile.topics_of_interest),
                "learning_goals_set": len(profile.learning_goals),
                "preferences_configured": len([
                    p for p in [
                        profile.learning_style.value if profile.learning_style else None,
                        profile.communication_style.value if profile.communication_style else None,
                        profile.expertise_level.value if profile.expertise_level else None
                    ] if p
                ])
            },
            "learning_progress": {
                "learning_style": profile.learning_style.value,
                "expertise_level": profile.expertise_level.value,
                "goals": profile.learning_goals,
                "interests": profile.topics_of_interest
            },
            "ai_preferences": {
                "preferred_providers": profile.preferred_providers,
                "preferred_models": profile.preferred_models,
                "communication_style": profile.communication_style.value,
                "response_length": profile.preferred_response_length
            },
            "adaptation_insights": {
                "personality_traits": [trait.value for trait in profile.personality_traits],
                "response_preferences": profile.response_preferences,
                "interaction_patterns": profile.interaction_patterns
            }
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get personalization analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")
