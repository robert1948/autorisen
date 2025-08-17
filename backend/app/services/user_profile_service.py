"""
Enhanced User Profile Service
Comprehensive user profile management with advanced personalization and analytics

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import uuid

# Database imports
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Pydantic models for validation
from pydantic import BaseModel, Field, validator
import bcrypt

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role types"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    PREMIUM = "premium"
    STANDARD = "standard"
    GUEST = "guest"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"

class PrivacyLevel(Enum):
    """Privacy level settings"""
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"

class LearningStyle(Enum):
    """User learning style preferences"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"

class CommunicationStyle(Enum):
    """User communication preferences"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    SIMPLE = "simple"
    DETAILED = "detailed"
    BALANCED = "balanced"  # Added balanced as a common option

@dataclass
class UserPreferences:
    """User preference settings"""
    language: str = "en-US"
    timezone: str = "UTC"
    theme: str = "light"
    notification_settings: Dict[str, bool] = field(default_factory=lambda: {
        "email_notifications": True,
        "push_notifications": True,
        "ai_suggestions": True,
        "system_updates": True,
        "marketing": False
    })
    ai_settings: Dict[str, Any] = field(default_factory=lambda: {
        "preferred_provider": "auto",
        "response_length": "medium",
        "formality_level": "balanced",
        "creativity_level": 0.7,
        "fact_checking": True,
        "citations": True
    })
    privacy_settings: Dict[str, str] = field(default_factory=lambda: {
        "profile_visibility": "public",
        "activity_tracking": "enabled",
        "data_sharing": "minimal",
        "analytics": "enabled"
    })

@dataclass
class UserBehaviorMetrics:
    """User behavior tracking metrics"""
    session_count: int = 0
    total_time_spent: float = 0.0
    average_session_length: float = 0.0
    last_activity: Optional[datetime] = None
    favorite_features: List[str] = field(default_factory=list)
    usage_patterns: Dict[str, int] = field(default_factory=dict)
    interaction_quality: float = 0.0
    engagement_score: float = 0.0
    retention_score: float = 0.0

@dataclass
class AIInteractionProfile:
    """AI interaction behavior and preferences"""
    total_conversations: int = 0
    average_messages_per_conversation: float = 0.0
    preferred_conversation_length: str = "medium"
    topic_interests: List[str] = field(default_factory=list)
    skill_assessments: Dict[str, float] = field(default_factory=dict)
    learning_progress: Dict[str, float] = field(default_factory=dict)
    feedback_patterns: Dict[str, int] = field(default_factory=dict)
    personalization_effectiveness: float = 0.0

@dataclass
class UserAchievements:
    """User achievements and milestones"""
    badges: List[str] = field(default_factory=list)
    milestones: Dict[str, datetime] = field(default_factory=dict)
    streaks: Dict[str, int] = field(default_factory=dict)
    points: int = 0
    level: int = 1
    experience: int = 0

@dataclass
class SocialConnections:
    """User social connections and network"""
    friends: List[str] = field(default_factory=list)
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    shared_interests: Dict[str, List[str]] = field(default_factory=dict)

class EnhancedUserProfile:
    """
    Comprehensive user profile with advanced personalization and analytics
    """
    
    def __init__(self, user_id: str, profile_data: Dict[str, Any] = None):
        """Initialize enhanced user profile"""
        self.user_id = user_id
        self.profile_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Core profile information
        self.username = profile_data.get('username', '')
        self.email = profile_data.get('email', '')
        self.full_name = profile_data.get('full_name', '')
        self.bio = profile_data.get('bio', '')
        self.avatar_url = profile_data.get('avatar_url', '')
        self.role = UserRole(profile_data.get('role', 'standard'))
        self.status = UserStatus(profile_data.get('status', 'active'))
        
        # Personal information
        self.date_of_birth = profile_data.get('date_of_birth')
        self.location = profile_data.get('location', '')
        self.occupation = profile_data.get('occupation', '')
        self.interests = profile_data.get('interests', [])
        self.skills = profile_data.get('skills', [])
        self.expertise_areas = profile_data.get('expertise_areas', [])
        
        # Learning and communication preferences
        self.learning_style = LearningStyle(profile_data.get('learning_style', 'multimodal'))
        self.communication_style = CommunicationStyle(profile_data.get('communication_style', 'balanced'))
        
        # Preferences and settings
        self.preferences = UserPreferences(**profile_data.get('preferences', {}))
        
        # Behavioral analytics
        self.behavior_metrics = UserBehaviorMetrics(**profile_data.get('behavior_metrics', {}))
        self.ai_interaction_profile = AIInteractionProfile(**profile_data.get('ai_interaction_profile', {}))
        
        # Achievements and social
        self.achievements = UserAchievements(**profile_data.get('achievements', {}))
        self.social_connections = SocialConnections(**profile_data.get('social_connections', {}))
        
        # Dynamic attributes
        self.dynamic_attributes = profile_data.get('dynamic_attributes', {})
        self.custom_fields = profile_data.get('custom_fields', {})
        
        # Analytics tracking
        self.analytics_data = {
            'profile_completeness': 0.0,
            'engagement_trends': [],
            'personalization_score': 0.0,
            'satisfaction_rating': 0.0,
            'feature_adoption': {},
            'usage_heatmap': {},
            'interaction_quality': 0.0
        }
    
    def calculate_profile_completeness(self) -> float:
        """Calculate profile completion percentage"""
        total_fields = 20
        completed_fields = 0
        
        # Check core fields
        if self.username: completed_fields += 1
        if self.email: completed_fields += 1
        if self.full_name: completed_fields += 1
        if self.bio: completed_fields += 1
        if self.avatar_url: completed_fields += 1
        if self.location: completed_fields += 1
        if self.occupation: completed_fields += 1
        if self.interests: completed_fields += 1
        if self.skills: completed_fields += 1
        if self.expertise_areas: completed_fields += 1
        
        # Check preferences
        if self.preferences.language != "en-US": completed_fields += 1
        if self.preferences.timezone != "UTC": completed_fields += 1
        if self.preferences.theme != "light": completed_fields += 1
        
        # Check behavioral data
        if self.behavior_metrics.session_count > 0: completed_fields += 1
        if self.ai_interaction_profile.total_conversations > 0: completed_fields += 1
        if self.ai_interaction_profile.topic_interests: completed_fields += 1
        if self.achievements.badges: completed_fields += 1
        if self.social_connections.friends: completed_fields += 1
        if self.dynamic_attributes: completed_fields += 1
        if self.custom_fields: completed_fields += 1
        
        completeness = (completed_fields / total_fields) * 100
        self.analytics_data['profile_completeness'] = completeness
        return completeness
    
    def update_behavior_metrics(self, session_data: Dict[str, Any]):
        """Update user behavior metrics"""
        metrics = self.behavior_metrics
        
        # Update session data
        metrics.session_count += 1
        session_duration = session_data.get('duration', 0)
        metrics.total_time_spent += session_duration
        metrics.average_session_length = metrics.total_time_spent / metrics.session_count
        metrics.last_activity = datetime.utcnow()
        
        # Update usage patterns
        features_used = session_data.get('features_used', [])
        for feature in features_used:
            metrics.usage_patterns[feature] = metrics.usage_patterns.get(feature, 0) + 1
        
        # Update favorite features
        if features_used:
            feature_counts = [(feature, count) for feature, count in metrics.usage_patterns.items()]
            feature_counts.sort(key=lambda x: x[1], reverse=True)
            metrics.favorite_features = [feature for feature, _ in feature_counts[:5]]
        
        # Calculate engagement score
        metrics.engagement_score = self._calculate_engagement_score()
        
        self.updated_at = datetime.utcnow()
    
    def update_ai_interaction_profile(self, conversation_data: Dict[str, Any]):
        """Update AI interaction profile"""
        profile = self.ai_interaction_profile
        
        # Update conversation stats
        profile.total_conversations += 1
        message_count = conversation_data.get('message_count', 0)
        
        total_messages = profile.average_messages_per_conversation * (profile.total_conversations - 1)
        profile.average_messages_per_conversation = (total_messages + message_count) / profile.total_conversations
        
        # Update topic interests
        topics = conversation_data.get('topics', [])
        for topic in topics:
            if topic not in profile.topic_interests:
                profile.topic_interests.append(topic)
        
        # Update skill assessments
        skills_demonstrated = conversation_data.get('skills_demonstrated', {})
        for skill, level in skills_demonstrated.items():
            current_level = profile.skill_assessments.get(skill, 0.0)
            profile.skill_assessments[skill] = (current_level + level) / 2
        
        # Update feedback patterns
        feedback = conversation_data.get('feedback')
        if feedback:
            profile.feedback_patterns[feedback] = profile.feedback_patterns.get(feedback, 0) + 1
        
        # Calculate personalization effectiveness
        profile.personalization_effectiveness = self._calculate_personalization_effectiveness()
        
        self.updated_at = datetime.utcnow()
    
    def add_achievement(self, achievement_type: str, achievement_data: Dict[str, Any]):
        """Add user achievement"""
        achievements = self.achievements
        
        if achievement_type == "badge":
            badge_name = achievement_data.get('name')
            if badge_name and badge_name not in achievements.badges:
                achievements.badges.append(badge_name)
                achievements.points += achievement_data.get('points', 0)
        
        elif achievement_type == "milestone":
            milestone_name = achievement_data.get('name')
            if milestone_name:
                achievements.milestones[milestone_name] = datetime.utcnow()
                achievements.points += achievement_data.get('points', 0)
        
        elif achievement_type == "streak":
            streak_name = achievement_data.get('name')
            streak_count = achievement_data.get('count', 1)
            if streak_name:
                achievements.streaks[streak_name] = streak_count
        
        # Update level based on points
        new_level = min(100, max(1, achievements.points // 1000 + 1))
        if new_level > achievements.level:
            achievements.level = new_level
            achievements.experience = achievements.points % 1000
        
        self.updated_at = datetime.utcnow()
    
    def update_social_connections(self, connection_type: str, user_ids: List[str], action: str = "add"):
        """Update social connections"""
        connections = self.social_connections
        
        if connection_type == "friends":
            target_list = connections.friends
        elif connection_type == "followers":
            target_list = connections.followers
        elif connection_type == "following":
            target_list = connections.following
        elif connection_type == "groups":
            target_list = connections.groups
        else:
            return
        
        for user_id in user_ids:
            if action == "add" and user_id not in target_list:
                target_list.append(user_id)
            elif action == "remove" and user_id in target_list:
                target_list.remove(user_id)
        
        self.updated_at = datetime.utcnow()
    
    def get_personalization_settings(self) -> Dict[str, Any]:
        """Get personalization settings for AI interactions"""
        return {
            'language': self.preferences.language,
            'communication_style': self.communication_style.value,
            'learning_style': self.learning_style.value,
            'formality_level': self.preferences.ai_settings.get('formality_level', 'balanced'),
            'response_length': self.preferences.ai_settings.get('response_length', 'medium'),
            'creativity_level': self.preferences.ai_settings.get('creativity_level', 0.7),
            'interests': self.interests,
            'expertise_areas': self.expertise_areas,
            'skill_levels': self.ai_interaction_profile.skill_assessments,
            'topic_preferences': self.ai_interaction_profile.topic_interests,
            'interaction_history': {
                'total_conversations': self.ai_interaction_profile.total_conversations,
                'average_length': self.ai_interaction_profile.average_messages_per_conversation,
                'favorite_features': self.behavior_metrics.favorite_features
            }
        }
    
    def generate_user_insights(self) -> Dict[str, Any]:
        """Generate insights about user behavior and preferences"""
        insights = {
            'engagement_analysis': {
                'level': 'high' if self.behavior_metrics.engagement_score > 0.7 else 'medium' if self.behavior_metrics.engagement_score > 0.4 else 'low',
                'score': self.behavior_metrics.engagement_score,
                'session_frequency': self.behavior_metrics.session_count / max(1, (datetime.utcnow() - self.created_at).days),
                'average_session_duration': self.behavior_metrics.average_session_length
            },
            'learning_analysis': {
                'style': self.learning_style.value,
                'progress_areas': list(self.ai_interaction_profile.learning_progress.keys()),
                'skill_growth': len(self.ai_interaction_profile.skill_assessments),
                'personalization_effectiveness': self.ai_interaction_profile.personalization_effectiveness
            },
            'social_analysis': {
                'network_size': len(self.social_connections.friends) + len(self.social_connections.followers),
                'group_participation': len(self.social_connections.groups),
                'social_engagement': 'high' if len(self.social_connections.friends) > 10 else 'medium' if len(self.social_connections.friends) > 3 else 'low'
            },
            'achievement_analysis': {
                'total_points': self.achievements.points,
                'level': self.achievements.level,
                'badges_earned': len(self.achievements.badges),
                'active_streaks': len([s for s in self.achievements.streaks.values() if s > 0])
            },
            'profile_analysis': {
                'completeness': self.calculate_profile_completeness(),
                'last_updated': (datetime.utcnow() - self.updated_at).days,
                'account_age': (datetime.utcnow() - self.created_at).days,
                'role': self.role.value,
                'status': self.status.value
            }
        }
        
        return insights
    
    def _calculate_engagement_score(self) -> float:
        """Calculate user engagement score"""
        metrics = self.behavior_metrics
        
        # Base engagement from session frequency
        days_since_creation = max(1, (datetime.utcnow() - self.created_at).days)
        session_frequency = metrics.session_count / days_since_creation
        
        # Average session length factor
        avg_session_factor = min(1.0, metrics.average_session_length / 1800)  # 30 minutes as baseline
        
        # Feature diversity factor
        feature_diversity = len(metrics.usage_patterns) / 10  # Assuming 10 main features
        
        # Recent activity factor
        if metrics.last_activity:
            days_since_activity = (datetime.utcnow() - metrics.last_activity).days
            recency_factor = max(0.1, 1.0 - (days_since_activity / 30))
        else:
            recency_factor = 0.1
        
        # Combined engagement score
        engagement_score = (
            session_frequency * 0.3 +
            avg_session_factor * 0.2 +
            feature_diversity * 0.2 +
            recency_factor * 0.3
        )
        
        return min(1.0, engagement_score)
    
    def _calculate_personalization_effectiveness(self) -> float:
        """Calculate how effective personalization is for this user"""
        profile = self.ai_interaction_profile
        
        # Conversation satisfaction (from feedback)
        positive_feedback = profile.feedback_patterns.get('positive', 0) + profile.feedback_patterns.get('helpful', 0)
        total_feedback = sum(profile.feedback_patterns.values())
        satisfaction_score = positive_feedback / max(1, total_feedback)
        
        # Engagement with personalized features
        personalized_features = ['ai_suggestions', 'customized_responses', 'topic_recommendations']
        personalized_usage = sum(self.behavior_metrics.usage_patterns.get(f, 0) for f in personalized_features)
        total_usage = sum(self.behavior_metrics.usage_patterns.values())
        personalization_usage = personalized_usage / max(1, total_usage)
        
        # Learning progress indicator
        learning_progress = len(profile.learning_progress) * 0.1  # Each area of progress adds 0.1
        
        # Combined effectiveness
        effectiveness = (satisfaction_score * 0.5 + personalization_usage * 0.3 + learning_progress * 0.2)
        
        return min(1.0, effectiveness)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            'user_id': self.user_id,
            'profile_id': self.profile_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'role': self.role.value,
            'status': self.status.value,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'location': self.location,
            'occupation': self.occupation,
            'interests': self.interests,
            'skills': self.skills,
            'expertise_areas': self.expertise_areas,
            'learning_style': self.learning_style.value,
            'communication_style': self.communication_style.value,
            'preferences': asdict(self.preferences),
            'behavior_metrics': asdict(self.behavior_metrics),
            'ai_interaction_profile': asdict(self.ai_interaction_profile),
            'achievements': asdict(self.achievements),
            'social_connections': asdict(self.social_connections),
            'dynamic_attributes': self.dynamic_attributes,
            'custom_fields': self.custom_fields,
            'analytics_data': self.analytics_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedUserProfile':
        """Create profile from dictionary"""
        profile = cls(data['user_id'], data)
        
        # Set datetime fields
        if data.get('created_at'):
            profile.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            profile.updated_at = datetime.fromisoformat(data['updated_at'])
        if data.get('date_of_birth'):
            profile.date_of_birth = datetime.fromisoformat(data['date_of_birth'])
        
        return profile

class UserProfileService:
    """
    Service for managing enhanced user profiles with advanced features
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize user profile service"""
        self.config = config
        self.profiles = {}  # In-memory storage for demo
        self.profile_analytics = {}
        self.recommendation_engine = None
        
        # Performance tracking
        self.performance_metrics = {
            'total_profiles': 0,
            'active_profiles': 0,
            'profile_updates': 0,
            'personalization_requests': 0,
            'insights_generated': 0,
            'recommendation_requests': 0
        }
        
        logger.info("Enhanced user profile service initialized")
    
    async def create_profile(self, user_id: str, profile_data: Dict[str, Any]) -> EnhancedUserProfile:
        """Create new enhanced user profile"""
        try:
            profile = EnhancedUserProfile(user_id, profile_data)
            self.profiles[user_id] = profile
            
            # Update analytics
            self.performance_metrics['total_profiles'] += 1
            if profile.status == UserStatus.ACTIVE:
                self.performance_metrics['active_profiles'] += 1
            
            logger.info(f"Created enhanced profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create profile for user {user_id}: {e}")
            raise
    
    async def get_profile(self, user_id: str) -> Optional[EnhancedUserProfile]:
        """Get user profile"""
        return self.profiles.get(user_id)
    
    async def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[EnhancedUserProfile]:
        """Update user profile"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return None
            
            # Update basic fields
            for field, value in updates.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            # Update preferences if provided
            if 'preferences' in updates:
                profile.preferences = UserPreferences(**updates['preferences'])
            
            # Update custom fields
            if 'custom_fields' in updates:
                profile.custom_fields.update(updates['custom_fields'])
            
            profile.updated_at = datetime.utcnow()
            self.performance_metrics['profile_updates'] += 1
            
            logger.info(f"Updated profile for user {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update profile for user {user_id}: {e}")
            raise
    
    async def track_user_behavior(self, user_id: str, behavior_data: Dict[str, Any]):
        """Track user behavior and update metrics"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return
            
            # Update behavior metrics
            if 'session_data' in behavior_data:
                profile.update_behavior_metrics(behavior_data['session_data'])
            
            # Update AI interaction profile
            if 'conversation_data' in behavior_data:
                profile.update_ai_interaction_profile(behavior_data['conversation_data'])
            
            # Add achievements
            if 'achievements' in behavior_data:
                for achievement in behavior_data['achievements']:
                    profile.add_achievement(achievement['type'], achievement['data'])
            
            logger.info(f"Updated behavior tracking for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to track behavior for user {user_id}: {e}")
            raise
    
    async def get_personalization_settings(self, user_id: str) -> Dict[str, Any]:
        """Get personalization settings for user"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return {}
            
            settings = profile.get_personalization_settings()
            self.performance_metrics['personalization_requests'] += 1
            
            return settings
            
        except Exception as e:
            logger.error(f"Failed to get personalization settings for user {user_id}: {e}")
            return {}
    
    async def generate_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive user insights"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return {}
            
            insights = profile.generate_user_insights()
            self.performance_metrics['insights_generated'] += 1
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights for user {user_id}: {e}")
            return {}
    
    async def get_user_recommendations(self, user_id: str, recommendation_type: str = "general") -> List[Dict[str, Any]]:
        """Generate personalized recommendations for user"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return []
            
            recommendations = []
            
            if recommendation_type == "content":
                # Content recommendations based on interests and behavior
                interests = profile.interests
                topic_interests = profile.ai_interaction_profile.topic_interests
                
                for interest in interests[:5]:
                    recommendations.append({
                        'type': 'content',
                        'title': f"Explore {interest}",
                        'description': f"Discover more about {interest} with AI assistance",
                        'priority': 0.8,
                        'category': interest
                    })
                
                for topic in topic_interests[:3]:
                    if topic not in interests:
                        recommendations.append({
                            'type': 'content',
                            'title': f"Deep dive into {topic}",
                            'description': f"Based on your recent conversations about {topic}",
                            'priority': 0.6,
                            'category': topic
                        })
            
            elif recommendation_type == "features":
                # Feature recommendations based on usage patterns
                unused_features = ['voice_interaction', 'advanced_templates', 'analytics_dashboard']
                used_features = list(profile.behavior_metrics.usage_patterns.keys())
                
                for feature in unused_features:
                    if feature not in used_features:
                        recommendations.append({
                            'type': 'feature',
                            'title': f"Try {feature.replace('_', ' ').title()}",
                            'description': f"Enhance your experience with {feature.replace('_', ' ')}",
                            'priority': 0.7,
                            'category': 'feature_discovery'
                        })
            
            elif recommendation_type == "learning":
                # Learning recommendations based on skill assessments
                skill_levels = profile.ai_interaction_profile.skill_assessments
                
                for skill, level in skill_levels.items():
                    if level < 0.7:  # Room for improvement
                        recommendations.append({
                            'type': 'learning',
                            'title': f"Improve {skill} skills",
                            'description': f"Personalized learning path for {skill}",
                            'priority': 0.9 - level,
                            'category': skill
                        })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x['priority'], reverse=True)
            
            self.performance_metrics['recommendation_requests'] += 1
            
            return recommendations[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for user {user_id}: {e}")
            return []
    
    async def get_profile_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Get profile analytics"""
        try:
            if user_id:
                # Individual user analytics
                profile = self.profiles.get(user_id)
                if not profile:
                    return {}
                
                return {
                    'user_insights': profile.generate_user_insights(),
                    'profile_completeness': profile.calculate_profile_completeness(),
                    'personalization_effectiveness': profile.ai_interaction_profile.personalization_effectiveness,
                    'engagement_score': profile.behavior_metrics.engagement_score,
                    'analytics_data': profile.analytics_data
                }
            else:
                # System-wide analytics
                total_profiles = len(self.profiles)
                if total_profiles == 0:
                    return {'message': 'No profiles available'}
                
                active_profiles = sum(1 for p in self.profiles.values() if p.status == UserStatus.ACTIVE)
                avg_completeness = sum(p.calculate_profile_completeness() for p in self.profiles.values()) / total_profiles
                avg_engagement = sum(p.behavior_metrics.engagement_score for p in self.profiles.values()) / total_profiles
                
                role_distribution = {}
                for profile in self.profiles.values():
                    role = profile.role.value
                    role_distribution[role] = role_distribution.get(role, 0) + 1
                
                return {
                    'total_profiles': total_profiles,
                    'active_profiles': active_profiles,
                    'average_completeness': avg_completeness,
                    'average_engagement': avg_engagement,
                    'role_distribution': role_distribution,
                    'performance_metrics': self.performance_metrics
                }
                
        except Exception as e:
            logger.error(f"Failed to get profile analytics: {e}")
            return {}
    
    async def search_profiles(self, query: Dict[str, Any]) -> List[EnhancedUserProfile]:
        """Search profiles based on criteria"""
        try:
            results = []
            
            for profile in self.profiles.values():
                match = True
                
                # Filter by role
                if 'role' in query and profile.role.value != query['role']:
                    match = False
                
                # Filter by status
                if 'status' in query and profile.status.value != query['status']:
                    match = False
                
                # Filter by interests
                if 'interests' in query:
                    required_interests = query['interests']
                    if not any(interest in profile.interests for interest in required_interests):
                        match = False
                
                # Filter by skills
                if 'skills' in query:
                    required_skills = query['skills']
                    if not any(skill in profile.skills for skill in required_skills):
                        match = False
                
                # Filter by engagement level
                if 'min_engagement' in query:
                    if profile.behavior_metrics.engagement_score < query['min_engagement']:
                        match = False
                
                # Filter by profile completeness
                if 'min_completeness' in query:
                    if profile.calculate_profile_completeness() < query['min_completeness']:
                        match = False
                
                if match:
                    results.append(profile)
            
            # Sort results by relevance (engagement score)
            results.sort(key=lambda p: p.behavior_metrics.engagement_score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Profile search failed: {e}")
            return []
    
    async def export_profile_data(self, user_id: str, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export user profile data"""
        try:
            profile = self.profiles.get(user_id)
            if not profile:
                return {}
            
            profile_data = profile.to_dict()
            
            if format == "json":
                return json.dumps(profile_data, indent=2, default=str)
            else:
                return profile_data
                
        except Exception as e:
            logger.error(f"Failed to export profile data for user {user_id}: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            return {
                'status': 'healthy',
                'total_profiles': len(self.profiles),
                'active_profiles': sum(1 for p in self.profiles.values() if p.status == UserStatus.ACTIVE),
                'performance_metrics': self.performance_metrics,
                'memory_usage': {
                    'profiles_stored': len(self.profiles),
                    'analytics_tracked': len(self.profile_analytics)
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}

# Utility functions
def create_user_profile_service(config: Dict[str, Any]) -> UserProfileService:
    """Factory function to create user profile service"""
    return UserProfileService(config)

def generate_sample_profile_data(user_id: str) -> Dict[str, Any]:
    """Generate sample profile data for testing"""
    return {
        'username': f'user_{user_id}',
        'email': f'user_{user_id}@example.com',
        'full_name': f'User {user_id}',
        'bio': 'Sample user profile for testing',
        'interests': ['technology', 'science', 'learning'],
        'skills': ['python', 'data_analysis', 'communication'],
        'expertise_areas': ['software_development', 'problem_solving'],
        'learning_style': 'multimodal',
        'communication_style': 'casual',  # Fixed: use valid enum value
        'preferences': {
            'language': 'en-US',
            'ai_settings': {
                'creativity_level': 0.7,
                'response_length': 'medium'
            }
        }
    }
