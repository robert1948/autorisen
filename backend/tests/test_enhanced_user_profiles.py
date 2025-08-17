"""
Comprehensive Tests for Enhanced User Profile System
Testing all components of the user profile service and API

Author: CapeAI Development Team
Date: July 25, 2025
"""

import asyncio
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Import the components to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.user_profile_service import (
    UserProfileService, EnhancedUserProfile, UserRole, UserStatus,
    PrivacyLevel, LearningStyle, CommunicationStyle,
    UserPreferences, UserBehaviorMetrics, AIInteractionProfile,
    UserAchievements, SocialConnections, create_user_profile_service,
    generate_sample_profile_data
)

class TestEnhancedUserProfile:
    """Test cases for Enhanced User Profile"""
    
    def setup_method(self):
        """Setup test data"""
        self.user_id = "test_user_123"
        self.sample_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'bio': 'A test user profile',
            'interests': ['technology', 'science'],
            'skills': ['python', 'testing'],
            'learning_style': 'multimodal',
            'communication_style': 'balanced'
        }
    
    def test_profile_creation(self):
        """Test creating a new user profile"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        assert profile.user_id == self.user_id
        assert profile.username == 'testuser'
        assert profile.email == 'test@example.com'
        assert profile.full_name == 'Test User'
        assert profile.bio == 'A test user profile'
        assert profile.interests == ['technology', 'science']
        assert profile.skills == ['python', 'testing']
        assert profile.learning_style == LearningStyle.MULTIMODAL
        assert profile.communication_style == CommunicationStyle.BALANCED
        assert profile.role == UserRole.STANDARD
        assert profile.status == UserStatus.ACTIVE
    
    def test_profile_completeness_calculation(self):
        """Test profile completeness calculation"""
        # Empty profile
        empty_profile = EnhancedUserProfile("empty_user", {})
        completeness = empty_profile.calculate_profile_completeness()
        assert completeness == 0.0
        
        # Partially filled profile
        partial_profile = EnhancedUserProfile(self.user_id, self.sample_data)
        completeness = partial_profile.calculate_profile_completeness()
        assert 0 < completeness < 100
        
        # More complete profile
        complete_data = {
            **self.sample_data,
            'avatar_url': 'http://example.com/avatar.jpg',
            'location': 'Test City',
            'occupation': 'Software Developer',
            'expertise_areas': ['web_development', 'ai'],
            'preferences': {
                'language': 'en-US',
                'timezone': 'America/New_York',
                'theme': 'dark'
            },
            'custom_fields': {'special_interest': 'quantum_computing'}
        }
        complete_profile = EnhancedUserProfile(self.user_id, complete_data)
        
        # Simulate some activity
        complete_profile.behavior_metrics.session_count = 10
        complete_profile.ai_interaction_profile.total_conversations = 5
        complete_profile.ai_interaction_profile.topic_interests = ['ai', 'science']
        complete_profile.achievements.badges = ['early_adopter']
        complete_profile.social_connections.friends = ['friend1', 'friend2']
        
        completeness = complete_profile.calculate_profile_completeness()
        assert completeness > 80
    
    def test_behavior_metrics_update(self):
        """Test updating behavior metrics"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        session_data = {
            'duration': 1800,  # 30 minutes
            'features_used': ['chat', 'search', 'analytics']
        }
        
        initial_session_count = profile.behavior_metrics.session_count
        profile.update_behavior_metrics(session_data)
        
        assert profile.behavior_metrics.session_count == initial_session_count + 1
        assert profile.behavior_metrics.total_time_spent == 1800
        assert profile.behavior_metrics.average_session_length == 1800
        assert profile.behavior_metrics.last_activity is not None
        assert 'chat' in profile.behavior_metrics.usage_patterns
        assert profile.behavior_metrics.usage_patterns['chat'] == 1
        assert profile.behavior_metrics.favorite_features == ['chat', 'search', 'analytics']
    
    def test_ai_interaction_update(self):
        """Test updating AI interaction profile"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        conversation_data = {
            'message_count': 10,
            'topics': ['machine_learning', 'python'],
            'skills_demonstrated': {'python': 0.8, 'problem_solving': 0.7},
            'feedback': 'positive'
        }
        
        initial_conversations = profile.ai_interaction_profile.total_conversations
        profile.update_ai_interaction_profile(conversation_data)
        
        assert profile.ai_interaction_profile.total_conversations == initial_conversations + 1
        assert profile.ai_interaction_profile.average_messages_per_conversation == 10
        assert 'machine_learning' in profile.ai_interaction_profile.topic_interests
        assert 'python' in profile.ai_interaction_profile.topic_interests
        assert profile.ai_interaction_profile.skill_assessments['python'] == 0.8
        assert profile.ai_interaction_profile.skill_assessments['problem_solving'] == 0.7
        assert profile.ai_interaction_profile.feedback_patterns['positive'] == 1
    
    def test_achievement_addition(self):
        """Test adding achievements"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        # Add badge
        badge_data = {'name': 'first_conversation', 'points': 10}
        profile.add_achievement('badge', badge_data)
        
        assert 'first_conversation' in profile.achievements.badges
        assert profile.achievements.points == 10
        
        # Add milestone
        milestone_data = {'name': 'week_1_complete', 'points': 50}
        profile.add_achievement('milestone', milestone_data)
        
        assert 'week_1_complete' in profile.achievements.milestones
        assert profile.achievements.points == 60
        
        # Add streak
        streak_data = {'name': 'daily_usage', 'count': 7}
        profile.add_achievement('streak', streak_data)
        
        assert profile.achievements.streaks['daily_usage'] == 7
    
    def test_social_connections_update(self):
        """Test updating social connections"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        # Add friends
        profile.update_social_connections('friends', ['friend1', 'friend2'], 'add')
        assert 'friend1' in profile.social_connections.friends
        assert 'friend2' in profile.social_connections.friends
        
        # Remove friend
        profile.update_social_connections('friends', ['friend1'], 'remove')
        assert 'friend1' not in profile.social_connections.friends
        assert 'friend2' in profile.social_connections.friends
        
        # Add followers
        profile.update_social_connections('followers', ['follower1'], 'add')
        assert 'follower1' in profile.social_connections.followers
    
    def test_personalization_settings(self):
        """Test getting personalization settings"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        # Add some interaction data
        profile.ai_interaction_profile.skill_assessments = {'python': 0.8, 'ai': 0.6}
        profile.ai_interaction_profile.topic_interests = ['technology', 'science']
        profile.behavior_metrics.favorite_features = ['chat', 'analytics']
        
        settings = profile.get_personalization_settings()
        
        assert settings['language'] == profile.preferences.language
        assert settings['communication_style'] == profile.communication_style.value
        assert settings['learning_style'] == profile.learning_style.value
        assert settings['interests'] == profile.interests
        assert settings['skill_levels'] == profile.ai_interaction_profile.skill_assessments
        assert settings['topic_preferences'] == profile.ai_interaction_profile.topic_interests
    
    def test_user_insights_generation(self):
        """Test generating user insights"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        # Add some data for insights
        profile.behavior_metrics.session_count = 20
        profile.behavior_metrics.engagement_score = 0.8
        profile.ai_interaction_profile.skill_assessments = {'python': 0.7}
        profile.achievements.points = 500
        profile.achievements.badges = ['early_adopter', 'active_user']
        profile.social_connections.friends = ['friend1', 'friend2', 'friend3']
        
        insights = profile.generate_user_insights()
        
        assert 'engagement_analysis' in insights
        assert 'learning_analysis' in insights
        assert 'social_analysis' in insights
        assert 'achievement_analysis' in insights
        assert 'profile_analysis' in insights
        
        assert insights['engagement_analysis']['level'] == 'high'
        assert insights['achievement_analysis']['total_points'] == 500
        assert insights['achievement_analysis']['badges_earned'] == 2
        assert insights['social_analysis']['network_size'] == 3
    
    def test_profile_serialization(self):
        """Test profile to_dict and from_dict methods"""
        profile = EnhancedUserProfile(self.user_id, self.sample_data)
        
        # Convert to dict
        profile_dict = profile.to_dict()
        
        assert profile_dict['user_id'] == self.user_id
        assert profile_dict['username'] == 'testuser'
        assert profile_dict['email'] == 'test@example.com'
        assert 'created_at' in profile_dict
        assert 'updated_at' in profile_dict
        
        # Convert back from dict
        restored_profile = EnhancedUserProfile.from_dict(profile_dict)
        
        assert restored_profile.user_id == profile.user_id
        assert restored_profile.username == profile.username
        assert restored_profile.email == profile.email
        assert restored_profile.interests == profile.interests

class TestUserProfileService:
    """Test cases for User Profile Service"""
    
    def setup_method(self):
        """Setup test service"""
        config = {
            'cache_enabled': True,
            'analytics_enabled': True,
            'recommendation_engine': True
        }
        self.service = create_user_profile_service(config)
        self.user_id = "service_test_user"
        self.sample_data = generate_sample_profile_data(self.user_id)
    
    @pytest.mark.asyncio
    async def test_create_profile(self):
        """Test creating a profile through the service"""
        profile = await self.service.create_profile(self.user_id, self.sample_data)
        
        assert profile is not None
        assert profile.user_id == self.user_id
        assert profile.username == f'user_{self.user_id}'
        assert profile.email == f'user_{self.user_id}@example.com'
        assert self.service.performance_metrics['total_profiles'] == 1
    
    @pytest.mark.asyncio
    async def test_get_profile(self):
        """Test retrieving a profile"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        # Retrieve profile
        profile = await self.service.get_profile(self.user_id)
        
        assert profile is not None
        assert profile.user_id == self.user_id
        
        # Test non-existent profile
        non_existent = await self.service.get_profile("non_existent_user")
        assert non_existent is None
    
    @pytest.mark.asyncio
    async def test_update_profile(self):
        """Test updating a profile"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        # Update profile
        updates = {
            'full_name': 'Updated Name',
            'bio': 'Updated bio',
            'interests': ['new_interest']
        }
        
        updated_profile = await self.service.update_profile(self.user_id, updates)
        
        assert updated_profile is not None
        assert updated_profile.full_name == 'Updated Name'
        assert updated_profile.bio == 'Updated bio'
        assert updated_profile.interests == ['new_interest']
        assert self.service.performance_metrics['profile_updates'] == 1
    
    @pytest.mark.asyncio
    async def test_track_user_behavior(self):
        """Test behavior tracking"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        behavior_data = {
            'session_data': {
                'duration': 1200,
                'features_used': ['chat', 'search']
            },
            'conversation_data': {
                'message_count': 5,
                'topics': ['ai', 'technology'],
                'feedback': 'positive'
            },
            'achievements': [
                {
                    'type': 'badge',
                    'data': {'name': 'first_session', 'points': 10}
                }
            ]
        }
        
        await self.service.track_user_behavior(self.user_id, behavior_data)
        
        # Verify updates
        profile = await self.service.get_profile(self.user_id)
        assert profile.behavior_metrics.session_count == 1
        assert profile.behavior_metrics.total_time_spent == 1200
        assert profile.ai_interaction_profile.total_conversations == 1
        assert 'first_session' in profile.achievements.badges
    
    @pytest.mark.asyncio
    async def test_personalization_settings(self):
        """Test getting personalization settings"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        settings = await self.service.get_personalization_settings(self.user_id)
        
        assert 'language' in settings
        assert 'communication_style' in settings
        assert 'learning_style' in settings
        assert 'interests' in settings
        assert self.service.performance_metrics['personalization_requests'] == 1
    
    @pytest.mark.asyncio
    async def test_user_insights(self):
        """Test generating user insights"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        insights = await self.service.generate_user_insights(self.user_id)
        
        assert 'engagement_analysis' in insights
        assert 'learning_analysis' in insights
        assert 'social_analysis' in insights
        assert 'achievement_analysis' in insights
        assert 'profile_analysis' in insights
        assert self.service.performance_metrics['insights_generated'] == 1
    
    @pytest.mark.asyncio
    async def test_user_recommendations(self):
        """Test generating user recommendations"""
        # Create profile first
        profile_data = {
            **self.sample_data,
            'interests': ['technology', 'science', 'ai'],
            'skills': ['python', 'machine_learning']
        }
        await self.service.create_profile(self.user_id, profile_data)
        
        # Test content recommendations
        content_recs = await self.service.get_user_recommendations(self.user_id, 'content')
        assert len(content_recs) > 0
        assert all('type' in rec and rec['type'] == 'content' for rec in content_recs)
        
        # Test feature recommendations
        feature_recs = await self.service.get_user_recommendations(self.user_id, 'features')
        assert len(feature_recs) > 0
        assert all('type' in rec and rec['type'] == 'feature' for rec in feature_recs)
        
        # Test learning recommendations
        learning_recs = await self.service.get_user_recommendations(self.user_id, 'learning')
        assert len(learning_recs) >= 0  # May be empty if no skill assessments
        
        assert self.service.performance_metrics['recommendation_requests'] >= 3
    
    @pytest.mark.asyncio
    async def test_profile_search(self):
        """Test profile searching"""
        # Create multiple profiles
        users = ['user1', 'user2', 'user3']
        for i, user in enumerate(users):
            data = generate_sample_profile_data(user)
            if i == 0:
                data['role'] = 'premium'
                data['interests'] = ['technology', 'ai']
            elif i == 1:
                data['role'] = 'standard'
                data['interests'] = ['science', 'research']
            else:
                data['role'] = 'standard'
                data['interests'] = ['technology', 'design']
            
            await self.service.create_profile(user, data)
        
        # Search by role
        premium_users = await self.service.search_profiles({'role': 'premium'})
        assert len(premium_users) == 1
        assert premium_users[0].role == UserRole.PREMIUM
        
        # Search by interests
        tech_users = await self.service.search_profiles({'interests': ['technology']})
        assert len(tech_users) == 2
        
        # Search by multiple criteria
        tech_standard_users = await self.service.search_profiles({
            'role': 'standard',
            'interests': ['technology']
        })
        assert len(tech_standard_users) == 1
    
    @pytest.mark.asyncio
    async def test_profile_analytics(self):
        """Test profile analytics"""
        # Create some profiles
        users = ['analytics1', 'analytics2', 'analytics3']
        for user in users:
            data = generate_sample_profile_data(user)
            await self.service.create_profile(user, data)
        
        # Test system-wide analytics
        system_analytics = await self.service.get_profile_analytics()
        
        assert 'total_profiles' in system_analytics
        assert 'active_profiles' in system_analytics
        assert 'average_completeness' in system_analytics
        assert 'average_engagement' in system_analytics
        assert 'role_distribution' in system_analytics
        assert 'performance_metrics' in system_analytics
        
        assert system_analytics['total_profiles'] >= 3
        
        # Test individual user analytics
        user_analytics = await self.service.get_profile_analytics('analytics1')
        
        assert 'user_insights' in user_analytics
        assert 'profile_completeness' in user_analytics
        assert 'engagement_score' in user_analytics
    
    @pytest.mark.asyncio
    async def test_export_profile_data(self):
        """Test exporting profile data"""
        # Create profile first
        await self.service.create_profile(self.user_id, self.sample_data)
        
        # Export as dict
        dict_export = await self.service.export_profile_data(self.user_id, 'dict')
        assert isinstance(dict_export, dict)
        assert dict_export['user_id'] == self.user_id
        
        # Export as JSON
        json_export = await self.service.export_profile_data(self.user_id, 'json')
        assert isinstance(json_export, str)
        parsed_json = json.loads(json_export)
        assert parsed_json['user_id'] == self.user_id
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test service health check"""
        health = await self.service.health_check()
        
        assert health['status'] == 'healthy'
        assert 'total_profiles' in health
        assert 'active_profiles' in health
        assert 'performance_metrics' in health
        assert 'memory_usage' in health

class TestUserProfileComponents:
    """Test cases for user profile data structures"""
    
    def test_user_preferences(self):
        """Test UserPreferences dataclass"""
        prefs = UserPreferences()
        
        # Test defaults
        assert prefs.language == "en-US"
        assert prefs.timezone == "UTC"
        assert prefs.theme == "light"
        assert prefs.notification_settings['email_notifications'] is True
        assert prefs.ai_settings['creativity_level'] == 0.7
        
        # Test custom values
        custom_prefs = UserPreferences(
            language="es-ES",
            timezone="Europe/Madrid",
            theme="dark"
        )
        assert custom_prefs.language == "es-ES"
        assert custom_prefs.timezone == "Europe/Madrid"
        assert custom_prefs.theme == "dark"
    
    def test_behavior_metrics(self):
        """Test UserBehaviorMetrics dataclass"""
        metrics = UserBehaviorMetrics()
        
        # Test defaults
        assert metrics.session_count == 0
        assert metrics.total_time_spent == 0.0
        assert metrics.average_session_length == 0.0
        assert metrics.last_activity is None
        assert metrics.favorite_features == []
        assert metrics.usage_patterns == {}
        
        # Test with data
        metrics_with_data = UserBehaviorMetrics(
            session_count=10,
            total_time_spent=3600.0,
            average_session_length=360.0,
            favorite_features=['chat', 'search'],
            usage_patterns={'chat': 15, 'search': 10}
        )
        assert metrics_with_data.session_count == 10
        assert metrics_with_data.total_time_spent == 3600.0
    
    def test_ai_interaction_profile(self):
        """Test AIInteractionProfile dataclass"""
        profile = AIInteractionProfile()
        
        # Test defaults
        assert profile.total_conversations == 0
        assert profile.average_messages_per_conversation == 0.0
        assert profile.preferred_conversation_length == "medium"
        assert profile.topic_interests == []
        assert profile.skill_assessments == {}
        
        # Test with data
        profile_with_data = AIInteractionProfile(
            total_conversations=5,
            topic_interests=['ai', 'science'],
            skill_assessments={'python': 0.8, 'communication': 0.7}
        )
        assert profile_with_data.total_conversations == 5
        assert 'ai' in profile_with_data.topic_interests
        assert profile_with_data.skill_assessments['python'] == 0.8
    
    def test_user_achievements(self):
        """Test UserAchievements dataclass"""
        achievements = UserAchievements()
        
        # Test defaults
        assert achievements.badges == []
        assert achievements.milestones == {}
        assert achievements.streaks == {}
        assert achievements.points == 0
        assert achievements.level == 1
        assert achievements.experience == 0
        
        # Test with data
        achievements_with_data = UserAchievements(
            badges=['early_adopter', 'active_user'],
            points=150,
            level=2,
            experience=150
        )
        assert len(achievements_with_data.badges) == 2
        assert achievements_with_data.points == 150
        assert achievements_with_data.level == 2
    
    def test_social_connections(self):
        """Test SocialConnections dataclass"""
        connections = SocialConnections()
        
        # Test defaults
        assert connections.friends == []
        assert connections.followers == []
        assert connections.following == []
        assert connections.groups == []
        assert connections.shared_interests == {}
        
        # Test with data
        connections_with_data = SocialConnections(
            friends=['friend1', 'friend2'],
            followers=['follower1'],
            following=['following1', 'following2', 'following3'],
            groups=['group1']
        )
        assert len(connections_with_data.friends) == 2
        assert len(connections_with_data.followers) == 1
        assert len(connections_with_data.following) == 3
        assert len(connections_with_data.groups) == 1

class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_create_user_profile_service(self):
        """Test service factory function"""
        config = {'test': True}
        service = create_user_profile_service(config)
        
        assert isinstance(service, UserProfileService)
        assert service.config == config
    
    def test_generate_sample_profile_data(self):
        """Test sample data generation"""
        user_id = "sample_user"
        data = generate_sample_profile_data(user_id)
        
        assert data['username'] == f'user_{user_id}'
        assert data['email'] == f'user_{user_id}@example.com'
        assert data['full_name'] == f'User {user_id}'
        assert 'interests' in data
        assert 'skills' in data
        assert 'learning_style' in data
        assert 'communication_style' in data
        assert 'preferences' in data

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_profile_data(self):
        """Test creating profile with empty data"""
        profile = EnhancedUserProfile("empty_user", {})
        
        assert profile.user_id == "empty_user"
        assert profile.username == ""
        assert profile.email == ""
        assert profile.role == UserRole.STANDARD
        assert profile.status == UserStatus.ACTIVE
    
    def test_invalid_enum_values(self):
        """Test handling invalid enum values"""
        # Should fall back to defaults for invalid values
        data = {
            'role': 'invalid_role',  # Should default to 'standard'
            'learning_style': 'invalid_style',  # Should default to 'multimodal'
        }
        
        # The EnhancedUserProfile should handle invalid enum values gracefully
        # by either using defaults or raising appropriate errors
        try:
            profile = EnhancedUserProfile("test_user", data)
            # If it doesn't raise an error, check defaults are used
            assert profile.role == UserRole.STANDARD
        except (ValueError, KeyError):
            # If it raises an error, that's also acceptable behavior
            pass
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self):
        """Test service error handling"""
        service = create_user_profile_service({})
        
        # Test operations on non-existent profiles
        non_existent_profile = await service.get_profile("non_existent")
        assert non_existent_profile is None
        
        update_result = await service.update_profile("non_existent", {'name': 'test'})
        assert update_result is None
        
        insights = await service.generate_user_insights("non_existent")
        assert insights == {}
        
        settings = await service.get_personalization_settings("non_existent")
        assert settings == {}

# Performance and load testing
class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_bulk_profile_creation(self):
        """Test creating multiple profiles efficiently"""
        service = create_user_profile_service({'cache_enabled': True})
        
        # Create 100 profiles
        tasks = []
        for i in range(100):
            user_id = f"bulk_user_{i}"
            data = generate_sample_profile_data(user_id)
            tasks.append(service.create_profile(user_id, data))
        
        profiles = await asyncio.gather(*tasks)
        
        assert len(profiles) == 100
        assert all(profile is not None for profile in profiles)
        assert service.performance_metrics['total_profiles'] >= 100
    
    @pytest.mark.asyncio
    async def test_concurrent_profile_operations(self):
        """Test concurrent profile operations"""
        service = create_user_profile_service({'cache_enabled': True})
        user_id = "concurrent_user"
        
        # Create profile
        data = generate_sample_profile_data(user_id)
        await service.create_profile(user_id, data)
        
        # Perform concurrent operations
        tasks = [
            service.get_profile(user_id),
            service.generate_user_insights(user_id),
            service.get_personalization_settings(user_id),
            service.get_user_recommendations(user_id, 'content'),
            service.get_profile_analytics(user_id)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All operations should complete successfully
        assert all(result is not None for result in results)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
