import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, type OnboardingChecklist, type OnboardingChecklistItem } from '../../services/api';

const OnboardingChecklistPage: React.FC = () => {
  const navigate = useNavigate();
  const [checklistData, setChecklistData] = useState<OnboardingChecklist | null>(null);
  const [loading, setLoading] = useState(true);
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());

  // Load checklist data from API
  useEffect(() => {
    const loadChecklist = async () => {
      try {
        setLoading(true);
        const data = await api.onboarding.getChecklist();
        setChecklistData(data);
      } catch (error) {
        console.error('Failed to load checklist:', error);
        // Fallback data if API fails
        setChecklistData({
          items: [
            {
              id: 'complete_profile',
              title: 'Complete Your Profile',
              description: 'Add your basic information and preferences',
              completed: false,
              required: true,
              order: 1
            },
            {
              id: 'verify_email',
              title: 'Verify Email Address',
              description: 'Check your inbox and click the verification link',
              completed: false,
              required: true,
              order: 2
            },
            {
              id: 'watch_guide',
              title: 'Watch Welcome Guide',
              description: 'Learn the basics of using CapeControl',
              completed: false,
              required: false,
              order: 3
            },
            {
              id: 'try_agent',
              title: 'Try Your First Agent',
              description: 'Run a sample agent to see how it works',
              completed: false,
              required: false,
              order: 4
            },
            {
              id: 'explore_marketplace',
              title: 'Explore Marketplace',
              description: 'Browse available agents and tools',
              completed: false,
              required: false,
              order: 5
            },
            {
              id: 'setup_notifications',
              title: 'Set Up Notifications',
              description: 'Configure how you want to be notified',
              completed: false,
              required: false,
              order: 6
            }
          ],
          completion_percentage: 0,
          required_completed: 0,
          required_total: 2,
          optional_completed: 0,
          optional_total: 4
        });
      } finally {
        setLoading(false);
      }
    };

    loadChecklist();
  }, []);

  const toggleItem = async (id: string) => {
    if (updatingItems.has(id)) return; // Prevent double-clicks

    setUpdatingItems(prev => new Set(prev).add(id));

    try {
      await api.onboarding.completeItem(id);
      // Reload checklist to get updated state
      const updatedData = await api.onboarding.getChecklist();
      setChecklistData(updatedData);
    } catch (error) {
      console.error('Failed to update checklist item:', error);
      // Optionally show error message to user
    } finally {
      setUpdatingItems(prev => {
        const newSet = new Set(prev);
        newSet.delete(id);
        return newSet;
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!checklistData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Failed to load checklist</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-2 text-blue-600 hover:text-blue-700"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  const canContinue = checklistData.required_completed === checklistData.required_total;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Getting Started Checklist</h1>
          <p className="mt-2 text-gray-600">
            Complete these steps to get the most out of CapeControl
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Progress</h2>
            <span className="text-2xl font-bold text-blue-600">
              {checklistData.completion_percentage}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${checklistData.completion_percentage}%` }}
            />
          </div>
          
          <div className="flex justify-between text-sm text-gray-600">
            <span>{checklistData.completion_percentage}% Complete</span>
            <span>Required: {checklistData.required_completed}/{checklistData.required_total}</span>
          </div>
        </div>

        {/* Required Items */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
              Required Items
            </h3>
            <div className="space-y-4">
              {checklistData.items
                .filter(item => item.required)
                .sort((a, b) => a.order - b.order)
                .map((item) => (
                <ChecklistItem 
                  key={item.id} 
                  item={item} 
                  onToggle={toggleItem}
                  updating={updatingItems.has(item.id)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Optional Items */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
              Optional Items
            </h3>
            <div className="space-y-4">
              {checklistData.items
                .filter(item => !item.required)
                .sort((a, b) => a.order - b.order)
                .map((item) => (
                <ChecklistItem 
                  key={item.id} 
                  item={item} 
                  onToggle={toggleItem}
                  updating={updatingItems.has(item.id)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between">
          <Link
            to="/onboarding/guide"
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            ← Back to Guide
          </Link>

          <div className="flex space-x-3">
            {!canContinue && (
              <div className="flex items-center text-sm text-amber-600">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Complete required items first
              </div>
            )}
            
            <button
              onClick={() => navigate('/dashboard')}
              disabled={!canContinue}
              className={`inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                canContinue 
                  ? 'bg-blue-600 hover:bg-blue-700' 
                  : 'bg-gray-400 cursor-not-allowed'
              }`}
            >
              Continue to Dashboard →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

interface ChecklistItemProps {
  item: OnboardingChecklistItem;
  onToggle: (id: string) => void;
  updating: boolean;
}

const ChecklistItem: React.FC<ChecklistItemProps> = ({ item, onToggle, updating }) => {
  const getActionLink = (itemId: string) => {
    switch (itemId) {
      case 'complete_profile':
        return '/onboarding/profile';
      case 'watch_guide':
        return '/onboarding/guide';
      case 'explore_marketplace':
        return '/marketplace';
      default:
        return null;
    }
  };

  const actionLink = getActionLink(item.id);

  return (
    <div className="flex items-start space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
      <button
        onClick={() => onToggle(item.id)}
        disabled={updating}
        className={`flex-shrink-0 w-5 h-5 rounded border-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          item.completed
            ? 'bg-green-600 border-green-600 text-white'
            : 'border-gray-300 hover:border-gray-400'
        } ${updating ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {updating ? (
          <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto" />
        ) : item.completed ? (
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        ) : null}
      </button>

      <div className="flex-1 min-w-0">
        <h4 className={`text-sm font-medium ${item.completed ? 'text-gray-600 line-through' : 'text-gray-900'}`}>
          {item.title}
        </h4>
        <p className="text-sm text-gray-500 mt-1">
          {item.description}
        </p>
      </div>

      {!item.completed && actionLink && (
        <Link
          to={actionLink}
          className="flex-shrink-0 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          Go →
        </Link>
      )}
    </div>
  );
};

export default OnboardingChecklistPage;