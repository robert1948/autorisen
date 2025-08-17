// Enhanced User Profile Components for React Frontend
// Comprehensive profile management with advanced personalization

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  User, Settings, Award, Users, Eye, EyeOff, Edit3, Save, X,
  Camera, Upload, Download, Search, Filter, BarChart3, Target,
  Brain, MessageSquare, Heart, Star, Zap, TrendingUp, Activity,
  BookOpen, Lightbulb, Shield, Globe, Clock, Calendar
} from 'lucide-react';

// Enhanced User Profile Dashboard Component
export const EnhancedProfileDashboard = ({ userId, onProfileUpdate }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  // Fetch profile data
  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/profiles/${userId}`);
      const data = await response.json();
      
      if (data.success) {
        setProfile(data.data);
        if (onProfileUpdate) {
          onProfileUpdate(data.data);
        }
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, onProfileUpdate]);

  // Fetch insights
  const fetchInsights = useCallback(async () => {
    try {
      const response = await fetch(`/api/profiles/${userId}/insights`);
      const data = await response.json();
      
      if (data.success) {
        setInsights(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  }, [userId]);

  // Fetch recommendations
  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await fetch(`/api/profiles/${userId}/recommendations?recommendation_type=general`);
      const data = await response.json();
      
      if (data.success) {
        setRecommendations(data.data.recommendations || []);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  }, [userId]);

  useEffect(() => {
    fetchProfile();
    fetchInsights();
    fetchRecommendations();
  }, [fetchProfile, fetchInsights, fetchRecommendations]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-12">
        <User className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No profile found</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a profile.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Profile Header */}
      <ProfileHeader 
        profile={profile} 
        insights={insights}
        onEdit={() => setEditing(true)}
      />

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'overview', label: 'Overview', icon: User },
            { key: 'analytics', label: 'Analytics', icon: BarChart3 },
            { key: 'personalization', label: 'Personalization', icon: Brain },
            { key: 'achievements', label: 'Achievements', icon: Award },
            { key: 'social', label: 'Social', icon: Users },
            { key: 'settings', label: 'Settings', icon: Settings }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`${
                activeTab === key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <ProfileOverview 
            profile={profile}
            insights={insights}
            recommendations={recommendations}
          />
        )}
        
        {activeTab === 'analytics' && (
          <ProfileAnalytics 
            profile={profile}
            insights={insights}
          />
        )}
        
        {activeTab === 'personalization' && (
          <PersonalizationPanel 
            profile={profile}
            onUpdate={fetchProfile}
          />
        )}
        
        {activeTab === 'achievements' && (
          <AchievementsPanel 
            profile={profile}
            onUpdate={fetchProfile}
          />
        )}
        
        {activeTab === 'social' && (
          <SocialPanel 
            profile={profile}
            onUpdate={fetchProfile}
          />
        )}
        
        {activeTab === 'settings' && (
          <ProfileSettings 
            profile={profile}
            onUpdate={fetchProfile}
          />
        )}
      </div>

      {/* Edit Profile Modal */}
      {editing && (
        <ProfileEditModal
          profile={profile}
          onSave={fetchProfile}
          onClose={() => setEditing(false)}
        />
      )}
    </div>
  );
};

// Profile Header Component
const ProfileHeader = ({ profile, insights, onEdit }) => {
  const completeness = useMemo(() => {
    return insights?.profile_analysis?.completeness || 0;
  }, [insights]);

  const engagementLevel = useMemo(() => {
    const score = insights?.engagement_analysis?.score || 0;
    return score > 0.7 ? 'High' : score > 0.4 ? 'Medium' : 'Low';
  }, [insights]);

  return (
    <div className="bg-white shadow rounded-lg mb-6">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Avatar */}
            <div className="relative">
              <img
                className="h-20 w-20 rounded-full object-cover"
                src={profile.avatar_url || '/api/placeholder/80/80'}
                alt={profile.full_name}
              />
              <button className="absolute bottom-0 right-0 bg-blue-600 text-white rounded-full p-1">
                <Camera className="w-3 h-3" />
              </button>
            </div>

            {/* Profile Info */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{profile.full_name}</h1>
              <p className="text-gray-600">@{profile.username}</p>
              <p className="text-sm text-gray-500 mt-1">{profile.bio}</p>
              
              {/* Status Badges */}
              <div className="flex items-center space-x-2 mt-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  profile.role === 'admin' ? 'bg-red-100 text-red-800' :
                  profile.role === 'premium' ? 'bg-purple-100 text-purple-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {profile.role}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  Level {profile.achievements?.level || 1}
                </span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onEdit}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <Edit3 className="w-4 h-4 mr-2" />
              Edit Profile
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{Math.round(completeness)}%</div>
            <div className="text-sm text-gray-600">Profile Complete</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{engagementLevel}</div>
            <div className="text-sm text-gray-600">Engagement</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{profile.achievements?.points || 0}</div>
            <div className="text-sm text-gray-600">Total Points</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{profile.achievements?.badges?.length || 0}</div>
            <div className="text-sm text-gray-600">Badges Earned</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Overview Component
const ProfileOverview = ({ profile, insights, recommendations }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Personal Information */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium text-gray-500">Location</label>
            <p className="text-gray-900">{profile.location || 'Not specified'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Occupation</label>
            <p className="text-gray-900">{profile.occupation || 'Not specified'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Interests</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {profile.interests?.map((interest, index) => (
                <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {interest}
                </span>
              )) || <span className="text-gray-500">None specified</span>}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Skills</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {profile.skills?.map((skill, index) => (
                <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {skill}
                </span>
              )) || <span className="text-gray-500">None specified</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Personalized Recommendations */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations</h3>
        <div className="space-y-3">
          {recommendations.slice(0, 5).map((rec, index) => (
            <div key={index} className="border-l-4 border-blue-400 pl-4">
              <h4 className="text-sm font-medium text-gray-900">{rec.title}</h4>
              <p className="text-sm text-gray-600">{rec.description}</p>
              <div className="flex items-center mt-1">
                <Star className="w-3 h-3 text-yellow-400 mr-1" />
                <span className="text-xs text-gray-500">Priority: {Math.round(rec.priority * 100)}%</span>
              </div>
            </div>
          ))}
          {recommendations.length === 0 && (
            <p className="text-gray-500">No recommendations available</p>
          )}
        </div>
      </div>

      {/* Learning Preferences */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Learning & Communication</h3>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-500">Learning Style</label>
            <div className="flex items-center mt-1">
              <BookOpen className="w-4 h-4 text-blue-500 mr-2" />
              <span className="text-gray-900 capitalize">{profile.learning_style?.replace('_', ' ')}</span>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Communication Style</label>
            <div className="flex items-center mt-1">
              <MessageSquare className="w-4 h-4 text-green-500 mr-2" />
              <span className="text-gray-900 capitalize">{profile.communication_style}</span>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">AI Preferences</label>
            <div className="text-sm text-gray-600 mt-1">
              <p>Response Length: {profile.preferences?.ai_settings?.response_length}</p>
              <p>Creativity Level: {Math.round((profile.preferences?.ai_settings?.creativity_level || 0.7) * 100)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Summary */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Sessions</span>
            <span className="text-sm font-medium text-gray-900">{profile.behavior_metrics?.session_count || 0}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Total Conversations</span>
            <span className="text-sm font-medium text-gray-900">{profile.ai_interaction_profile?.total_conversations || 0}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Last Activity</span>
            <span className="text-sm font-medium text-gray-900">
              {profile.behavior_metrics?.last_activity ? 
                new Date(profile.behavior_metrics.last_activity).toLocaleDateString() : 
                'Never'
              }
            </span>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-500">Favorite Features</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {profile.behavior_metrics?.favorite_features?.map((feature, index) => (
                <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  {feature.replace('_', ' ')}
                </span>
              )) || <span className="text-gray-500">None yet</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Profile Analytics Component
const ProfileAnalytics = ({ profile, insights }) => {
  if (!insights) {
    return (
      <div className="text-center py-12">
        <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No analytics available</h3>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Engagement Analytics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Engagement Analytics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Activity className="mx-auto h-8 w-8 text-blue-600 mb-2" />
            <div className="text-2xl font-bold text-blue-600">
              {Math.round((insights.engagement_analysis?.score || 0) * 100)}%
            </div>
            <div className="text-sm text-gray-600">Engagement Score</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <Clock className="mx-auto h-8 w-8 text-green-600 mb-2" />
            <div className="text-2xl font-bold text-green-600">
              {Math.round(insights.engagement_analysis?.average_session_duration || 0)}m
            </div>
            <div className="text-sm text-gray-600">Avg Session</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <TrendingUp className="mx-auto h-8 w-8 text-purple-600 mb-2" />
            <div className="text-2xl font-bold text-purple-600">
              {Math.round(insights.engagement_analysis?.session_frequency || 0)}
            </div>
            <div className="text-sm text-gray-600">Sessions/Day</div>
          </div>
        </div>
      </div>

      {/* Learning Analytics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Learning Progress</h3>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Personalization Effectiveness</span>
              <span className="text-sm text-gray-500">
                {Math.round((insights.learning_analysis?.personalization_effectiveness || 0) * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${(insights.learning_analysis?.personalization_effectiveness || 0) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium text-gray-500">Skill Growth Areas</label>
            <div className="mt-2 space-y-2">
              {insights.learning_analysis?.progress_areas?.map((area, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">{area}</span>
                  <span className="text-sm text-green-600">↗ Growing</span>
                </div>
              )) || <p className="text-gray-500">No skill assessments yet</p>}
            </div>
          </div>
        </div>
      </div>

      {/* Social Analytics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Social Engagement</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Network Size</span>
              <span className="text-sm text-gray-500">{insights.social_analysis?.network_size || 0}</span>
            </div>
            <div className="text-xs text-gray-500">Friends + Followers</div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Group Participation</span>
              <span className="text-sm text-gray-500">{insights.social_analysis?.group_participation || 0}</span>
            </div>
            <div className="text-xs text-gray-500">Active Groups</div>
          </div>
        </div>
      </div>

      {/* Achievement Analytics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Achievement Progress</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{insights.achievement_analysis?.total_points || 0}</div>
            <div className="text-sm text-gray-600">Total Points</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{insights.achievement_analysis?.level || 1}</div>
            <div className="text-sm text-gray-600">Current Level</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{insights.achievement_analysis?.badges_earned || 0}</div>
            <div className="text-sm text-gray-600">Badges</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{insights.achievement_analysis?.active_streaks || 0}</div>
            <div className="text-sm text-gray-600">Streaks</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Personalization Panel Component
const PersonalizationPanel = ({ profile, onUpdate }) => {
  const [preferences, setPreferences] = useState(profile.preferences || {});
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/profiles/${profile.user_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences })
      });

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* AI Preferences */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Assistant Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Response Length</label>
            <select 
              value={preferences.ai_settings?.response_length || 'medium'}
              onChange={(e) => setPreferences({
                ...preferences,
                ai_settings: { ...preferences.ai_settings, response_length: e.target.value }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="short">Short & Concise</option>
              <option value="medium">Medium Detail</option>
              <option value="long">Comprehensive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Creativity Level: {Math.round((preferences.ai_settings?.creativity_level || 0.7) * 100)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={preferences.ai_settings?.creativity_level || 0.7}
              onChange={(e) => setPreferences({
                ...preferences,
                ai_settings: { ...preferences.ai_settings, creativity_level: parseFloat(e.target.value) }
              })}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Formality Level</label>
            <select 
              value={preferences.ai_settings?.formality_level || 'balanced'}
              onChange={(e) => setPreferences({
                ...preferences,
                ai_settings: { ...preferences.ai_settings, formality_level: e.target.value }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="casual">Casual</option>
              <option value="balanced">Balanced</option>
              <option value="formal">Formal</option>
              <option value="professional">Professional</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Preferred AI Provider</label>
            <select 
              value={preferences.ai_settings?.preferred_provider || 'auto'}
              onChange={(e) => setPreferences({
                ...preferences,
                ai_settings: { ...preferences.ai_settings, preferred_provider: e.target.value }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="auto">Auto-Select Best</option>
              <option value="openai">OpenAI GPT</option>
              <option value="anthropic">Anthropic Claude</option>
              <option value="google">Google Gemini</option>
            </select>
          </div>
        </div>

        {/* AI Feature Toggles */}
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">AI Features</h4>
          <div className="space-y-3">
            {[
              { key: 'fact_checking', label: 'Fact Checking', description: 'Verify information accuracy' },
              { key: 'citations', label: 'Citations', description: 'Include source references' },
              { key: 'suggestions', label: 'Smart Suggestions', description: 'Proactive recommendations' }
            ].map(({ key, label, description }) => (
              <div key={key} className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-gray-900">{label}</div>
                  <div className="text-sm text-gray-500">{description}</div>
                </div>
                <button
                  onClick={() => setPreferences({
                    ...preferences,
                    ai_settings: { 
                      ...preferences.ai_settings, 
                      [key]: !preferences.ai_settings?.[key] 
                    }
                  })}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    preferences.ai_settings?.[key] ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      preferences.ai_settings?.[key] ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h3>
        <div className="space-y-4">
          {[
            { key: 'email_notifications', label: 'Email Notifications', description: 'Receive updates via email' },
            { key: 'push_notifications', label: 'Push Notifications', description: 'Browser push notifications' },
            { key: 'ai_suggestions', label: 'AI Suggestions', description: 'Personalized recommendations' },
            { key: 'system_updates', label: 'System Updates', description: 'Platform news and updates' },
            { key: 'marketing', label: 'Marketing Communications', description: 'Promotional content' }
          ].map(({ key, label, description }) => (
            <div key={key} className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-900">{label}</div>
                <div className="text-sm text-gray-500">{description}</div>
              </div>
              <button
                onClick={() => setPreferences({
                  ...preferences,
                  notification_settings: { 
                    ...preferences.notification_settings, 
                    [key]: !preferences.notification_settings?.[key] 
                  }
                })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  preferences.notification_settings?.[key] ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    preferences.notification_settings?.[key] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Privacy Settings */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Privacy & Data</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Profile Visibility</label>
            <select 
              value={preferences.privacy_settings?.profile_visibility || 'public'}
              onChange={(e) => setPreferences({
                ...preferences,
                privacy_settings: { ...preferences.privacy_settings, profile_visibility: e.target.value }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="public">Public</option>
              <option value="friends">Friends Only</option>
              <option value="private">Private</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Data Sharing</label>
            <select 
              value={preferences.privacy_settings?.data_sharing || 'minimal'}
              onChange={(e) => setPreferences({
                ...preferences,
                privacy_settings: { ...preferences.privacy_settings, data_sharing: e.target.value }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="none">No Sharing</option>
              <option value="minimal">Minimal (Required Only)</option>
              <option value="selective">Selective Sharing</option>
              <option value="full">Full Sharing</option>
            </select>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};

// Profile Edit Modal Component
const ProfileEditModal = ({ profile, onSave, onClose }) => {
  const [formData, setFormData] = useState({
    full_name: profile.full_name || '',
    bio: profile.bio || '',
    location: profile.location || '',
    occupation: profile.occupation || '',
    interests: profile.interests || [],
    skills: profile.skills || [],
    learning_style: profile.learning_style || 'multimodal',
    communication_style: profile.communication_style || 'balanced'
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch(`/api/profiles/${profile.user_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        onSave();
        onClose();
      }
    } catch (error) {
      console.error('Failed to save profile:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Edit Profile</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
            <textarea
              value={formData.bio}
              onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
              <input
                type="text"
                value={formData.occupation}
                onChange={(e) => setFormData({ ...formData, occupation: e.target.value })}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Learning Style</label>
              <select
                value={formData.learning_style}
                onChange={(e) => setFormData({ ...formData, learning_style: e.target.value })}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="visual">Visual</option>
                <option value="auditory">Auditory</option>
                <option value="kinesthetic">Kinesthetic</option>
                <option value="reading_writing">Reading/Writing</option>
                <option value="multimodal">Multimodal</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Communication Style</label>
              <select
                value={formData.communication_style}
                onChange={(e) => setFormData({ ...formData, communication_style: e.target.value })}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="formal">Formal</option>
                <option value="casual">Casual</option>
                <option value="technical">Technical</option>
                <option value="simple">Simple</option>
                <option value="detailed">Detailed</option>
              </select>
            </div>
          </div>

          {/* Interests and Skills would need more complex editing interfaces */}
          {/* For brevity, showing simplified version */}
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Achievements Panel Component (placeholder)
const AchievementsPanel = ({ profile }) => (
  <div className="bg-white shadow rounded-lg p-6">
    <h3 className="text-lg font-medium text-gray-900 mb-4">Achievements & Badges</h3>
    <p className="text-gray-500">Achievement system coming soon...</p>
  </div>
);

// Social Panel Component (placeholder)
const SocialPanel = ({ profile }) => (
  <div className="bg-white shadow rounded-lg p-6">
    <h3 className="text-lg font-medium text-gray-900 mb-4">Social Connections</h3>
    <p className="text-gray-500">Social features coming soon...</p>
  </div>
);

// Profile Settings Component (placeholder)
const ProfileSettings = ({ profile }) => (
  <div className="bg-white shadow rounded-lg p-6">
    <h3 className="text-lg font-medium text-gray-900 mb-4">Account Settings</h3>
    <p className="text-gray-500">Account management coming soon...</p>
  </div>
);

export default EnhancedProfileDashboard;
