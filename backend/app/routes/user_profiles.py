"""
Enhanced User Profile API Routes
REST API endpoints for comprehensive user profile management

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
import io

# Import the enhanced user profile service
from ..services.user_profile_service import (
    UserProfileService, EnhancedUserProfile, UserRole, UserStatus,
    PrivacyLevel, LearningStyle, CommunicationStyle, create_user_profile_service
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/profiles", tags=["user_profiles"])

# Initialize service (in production, this would be dependency injected)
profile_service_config = {
    'cache_enabled': True,
    'analytics_enabled': True,
    'recommendation_engine': True
}
profile_service = create_user_profile_service(profile_service_config)

# Pydantic models for request/response
class ProfileCreateRequest(BaseModel):
    """Request model for creating user profile"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    role: str = Field(default="standard", regex=r'^(admin|moderator|premium|standard|guest)$')
    location: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    interests: List[str] = Field(default=[])
    skills: List[str] = Field(default=[])
    expertise_areas: List[str] = Field(default=[])
    learning_style: str = Field(default="multimodal", regex=r'^(visual|auditory|kinesthetic|reading_writing|multimodal)$')
    communication_style: str = Field(default="balanced", regex=r'^(formal|casual|technical|simple|detailed)$')
    preferences: Optional[Dict[str, Any]] = Field(default={})
    custom_fields: Optional[Dict[str, Any]] = Field(default={})

class ProfileUpdateRequest(BaseModel):
    """Request model for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, regex=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    occupation: Optional[str] = Field(None, max_length=100)
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    expertise_areas: Optional[List[str]] = None
    learning_style: Optional[str] = Field(None, regex=r'^(visual|auditory|kinesthetic|reading_writing|multimodal)$')
    communication_style: Optional[str] = Field(None, regex=r'^(formal|casual|technical|simple|detailed)$')
    preferences: Optional[Dict[str, Any]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class BehaviorTrackingRequest(BaseModel):
    """Request model for behavior tracking"""
    session_data: Optional[Dict[str, Any]] = None
    conversation_data: Optional[Dict[str, Any]] = None
    achievements: Optional[List[Dict[str, Any]]] = None

class AchievementRequest(BaseModel):
    """Request model for adding achievements"""
    achievement_type: str = Field(..., regex=r'^(badge|milestone|streak)$')
    achievement_data: Dict[str, Any]

class SocialConnectionRequest(BaseModel):
    """Request model for social connections"""
    connection_type: str = Field(..., regex=r'^(friends|followers|following|groups)$')
    user_ids: List[str]
    action: str = Field(default="add", regex=r'^(add|remove)$')

class ProfileSearchRequest(BaseModel):
    """Request model for profile search"""
    role: Optional[str] = None
    status: Optional[str] = None
    interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    min_engagement: Optional[float] = Field(None, ge=0, le=1)
    min_completeness: Optional[float] = Field(None, ge=0, le=100)

class ProfileResponse(BaseModel):
    """Response model for profile data"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

# API Routes

@router.post("/create/{user_id}", response_model=ProfileResponse)
async def create_user_profile(user_id: str, request: ProfileCreateRequest):
    """Create a new enhanced user profile"""
    try:
        # Convert request to dict
        profile_data = request.dict()
        
        # Create profile
        profile = await profile_service.create_profile(user_id, profile_data)
        
        return ProfileResponse(
            success=True,
            data=profile.to_dict(),
            message=f"Profile created successfully for user {user_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to create profile for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    try:
        profile = await profile_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data=profile.to_dict(),
            message=f"Profile retrieved for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.put("/{user_id}", response_model=ProfileResponse)
async def update_user_profile(user_id: str, request: ProfileUpdateRequest):
    """Update user profile"""
    try:
        # Only include non-None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        profile = await profile_service.update_profile(user_id, updates)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data=profile.to_dict(),
            message=f"Profile updated for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.delete("/{user_id}", response_model=ProfileResponse)
async def delete_user_profile(user_id: str):
    """Delete user profile (soft delete - set status to deleted)"""
    try:
        profile = await profile_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Soft delete by setting status
        updated_profile = await profile_service.update_profile(user_id, {'status': 'deleted'})
        
        return ProfileResponse(
            success=True,
            message=f"Profile deleted for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete profile for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.post("/{user_id}/behavior", response_model=ProfileResponse)
async def track_user_behavior(user_id: str, request: BehaviorTrackingRequest):
    """Track user behavior and update metrics"""
    try:
        behavior_data = request.dict()
        
        await profile_service.track_user_behavior(user_id, behavior_data)
        
        return ProfileResponse(
            success=True,
            message=f"Behavior tracking updated for user {user_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to track behavior for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.post("/{user_id}/achievements", response_model=ProfileResponse)
async def add_user_achievement(user_id: str, request: AchievementRequest):
    """Add achievement to user profile"""
    try:
        profile = await profile_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile.add_achievement(request.achievement_type, request.achievement_data)
        
        return ProfileResponse(
            success=True,
            data={'achievements': profile.achievements.to_dict() if hasattr(profile.achievements, 'to_dict') else vars(profile.achievements)},
            message=f"Achievement added for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add achievement for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.post("/{user_id}/social", response_model=ProfileResponse)
async def update_social_connections(user_id: str, request: SocialConnectionRequest):
    """Update user's social connections"""
    try:
        profile = await profile_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile.update_social_connections(
            request.connection_type,
            request.user_ids,
            request.action
        )
        
        return ProfileResponse(
            success=True,
            data={'social_connections': vars(profile.social_connections)},
            message=f"Social connections updated for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update social connections for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}/personalization", response_model=ProfileResponse)
async def get_personalization_settings(user_id: str):
    """Get personalization settings for user"""
    try:
        settings = await profile_service.get_personalization_settings(user_id)
        
        if not settings:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data=settings,
            message=f"Personalization settings retrieved for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get personalization settings for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}/insights", response_model=ProfileResponse)
async def get_user_insights(user_id: str):
    """Generate comprehensive user insights"""
    try:
        insights = await profile_service.generate_user_insights(user_id)
        
        if not insights:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data=insights,
            message=f"Insights generated for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate insights for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}/recommendations", response_model=ProfileResponse)
async def get_user_recommendations(
    user_id: str,
    recommendation_type: str = Query(default="general", regex=r'^(general|content|features|learning)$')
):
    """Get personalized recommendations for user"""
    try:
        recommendations = await profile_service.get_user_recommendations(user_id, recommendation_type)
        
        return ProfileResponse(
            success=True,
            data={
                'recommendations': recommendations,
                'type': recommendation_type,
                'count': len(recommendations)
            },
            message=f"Recommendations generated for user {user_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to get recommendations for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}/completeness", response_model=ProfileResponse)
async def get_profile_completeness(user_id: str):
    """Get profile completion percentage"""
    try:
        profile = await profile_service.get_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        completeness = profile.calculate_profile_completeness()
        
        return ProfileResponse(
            success=True,
            data={
                'completeness_percentage': completeness,
                'status': 'complete' if completeness >= 80 else 'incomplete' if completeness >= 50 else 'basic'
            },
            message=f"Profile completeness calculated for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate completeness for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.post("/search", response_model=ProfileResponse)
async def search_profiles(request: ProfileSearchRequest):
    """Search profiles based on criteria"""
    try:
        search_criteria = {k: v for k, v in request.dict().items() if v is not None}
        
        profiles = await profile_service.search_profiles(search_criteria)
        
        # Convert profiles to dict format
        profile_data = [profile.to_dict() for profile in profiles]
        
        return ProfileResponse(
            success=True,
            data={
                'profiles': profile_data,
                'count': len(profile_data),
                'search_criteria': search_criteria
            },
            message=f"Found {len(profile_data)} matching profiles"
        )
        
    except Exception as e:
        logger.error(f"Profile search failed: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/{user_id}/export", response_model=ProfileResponse)
async def export_profile_data(
    user_id: str,
    format: str = Query(default="json", regex=r'^(json|dict)$')
):
    """Export user profile data"""
    try:
        export_data = await profile_service.export_profile_data(user_id, format)
        
        if not export_data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        if format == "json":
            return StreamingResponse(
                io.StringIO(export_data),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=profile_{user_id}.json"}
            )
        else:
            return ProfileResponse(
                success=True,
                data=export_data,
                message=f"Profile data exported for user {user_id}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export profile data for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.post("/{user_id}/avatar", response_model=ProfileResponse)
async def upload_user_avatar(user_id: str, file: UploadFile = File(...)):
    """Upload user avatar image"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # In production, you would save to cloud storage (S3, etc.)
        # For demo, we'll just generate a placeholder URL
        avatar_url = f"/avatars/{user_id}_{file.filename}"
        
        # Update profile with avatar URL
        profile = await profile_service.update_profile(user_id, {'avatar_url': avatar_url})
        
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data={'avatar_url': avatar_url},
            message=f"Avatar uploaded for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload avatar for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/analytics/system", response_model=ProfileResponse)
async def get_system_analytics():
    """Get system-wide profile analytics"""
    try:
        analytics = await profile_service.get_profile_analytics()
        
        return ProfileResponse(
            success=True,
            data=analytics,
            message="System analytics retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get system analytics: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/analytics/{user_id}", response_model=ProfileResponse)
async def get_user_analytics(user_id: str):
    """Get individual user analytics"""
    try:
        analytics = await profile_service.get_profile_analytics(user_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        return ProfileResponse(
            success=True,
            data=analytics,
            message=f"Analytics retrieved for user {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics for {user_id}: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/roles/available")
async def get_available_roles():
    """Get list of available user roles"""
    try:
        roles = [role.value for role in UserRole]
        
        return ProfileResponse(
            success=True,
            data={
                'roles': roles,
                'descriptions': {
                    'admin': 'Full system access and management capabilities',
                    'moderator': 'Content moderation and user management',
                    'premium': 'Enhanced features and priority support',
                    'standard': 'Regular user with standard features',
                    'guest': 'Limited access for trial users'
                }
            },
            message="Available roles retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get available roles: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/learning-styles/available")
async def get_learning_styles():
    """Get list of available learning styles"""
    try:
        styles = [style.value for style in LearningStyle]
        
        return ProfileResponse(
            success=True,
            data={
                'learning_styles': styles,
                'descriptions': {
                    'visual': 'Learn through images, diagrams, and visual aids',
                    'auditory': 'Learn through listening and verbal instruction',
                    'kinesthetic': 'Learn through hands-on activities and movement',
                    'reading_writing': 'Learn through reading and writing activities',
                    'multimodal': 'Combination of multiple learning styles'
                }
            },
            message="Available learning styles retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get learning styles: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/communication-styles/available")
async def get_communication_styles():
    """Get list of available communication styles"""
    try:
        styles = [style.value for style in CommunicationStyle]
        
        return ProfileResponse(
            success=True,
            data={
                'communication_styles': styles,
                'descriptions': {
                    'formal': 'Professional and structured communication',
                    'casual': 'Relaxed and friendly communication',
                    'technical': 'Precise and detail-oriented communication',
                    'simple': 'Clear and straightforward communication',
                    'detailed': 'Comprehensive and thorough communication'
                }
            },
            message="Available communication styles retrieved"
        )
        
    except Exception as e:
        logger.error(f"Failed to get communication styles: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = await profile_service.health_check()
        
        return ProfileResponse(
            success=True,
            data=health_status,
            message="Service health check completed"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

# Batch operations
@router.post("/batch/create", response_model=ProfileResponse)
async def batch_create_profiles(profiles: List[Dict[str, Any]]):
    """Create multiple user profiles in batch"""
    try:
        created_profiles = []
        errors = []
        
        for profile_data in profiles:
            try:
                user_id = profile_data.get('user_id')
                if not user_id:
                    errors.append(f"Missing user_id in profile data")
                    continue
                
                profile = await profile_service.create_profile(user_id, profile_data)
                created_profiles.append(profile.to_dict())
                
            except Exception as e:
                errors.append(f"Failed to create profile for {profile_data.get('user_id', 'unknown')}: {str(e)}")
        
        return ProfileResponse(
            success=len(errors) == 0,
            data={
                'created_profiles': created_profiles,
                'success_count': len(created_profiles),
                'error_count': len(errors),
                'errors': errors
            },
            message=f"Batch creation completed: {len(created_profiles)} successful, {len(errors)} errors"
        )
        
    except Exception as e:
        logger.error(f"Batch profile creation failed: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

@router.put("/batch/update", response_model=ProfileResponse)
async def batch_update_profiles(updates: List[Dict[str, Any]]):
    """Update multiple user profiles in batch"""
    try:
        updated_profiles = []
        errors = []
        
        for update_data in updates:
            try:
                user_id = update_data.get('user_id')
                if not user_id:
                    errors.append(f"Missing user_id in update data")
                    continue
                
                # Remove user_id from updates
                profile_updates = {k: v for k, v in update_data.items() if k != 'user_id'}
                
                profile = await profile_service.update_profile(user_id, profile_updates)
                if profile:
                    updated_profiles.append(profile.to_dict())
                else:
                    errors.append(f"Profile not found for user {user_id}")
                
            except Exception as e:
                errors.append(f"Failed to update profile for {update_data.get('user_id', 'unknown')}: {str(e)}")
        
        return ProfileResponse(
            success=len(errors) == 0,
            data={
                'updated_profiles': updated_profiles,
                'success_count': len(updated_profiles),
                'error_count': len(errors),
                'errors': errors
            },
            message=f"Batch update completed: {len(updated_profiles)} successful, {len(errors)} errors"
        )
        
    except Exception as e:
        logger.error(f"Batch profile update failed: {e}")
        return ProfileResponse(
            success=False,
            error=str(e)
        )

# WebSocket endpoint for real-time profile updates (placeholder)
# Note: WebSocket implementation would require additional setup
"""
@router.websocket("/{user_id}/live")
async def profile_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Listen for real-time profile updates
            data = await websocket.receive_text()
            update_data = json.loads(data)
            
            # Process update
            profile = await profile_service.update_profile(user_id, update_data)
            
            # Send response
            response = {
                'type': 'profile_update',
                'data': profile.to_dict() if profile else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(response))
            
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        await websocket.close()
"""
