import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, UserProfile, UserProfileUpdate } from '../../services/api';

interface FormData {
  firstName: string;
  lastName: string;
  company: string;
  role: string;
  experience: string;
  interests: string[];
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
}

const OnboardingProfile: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    company: '',
    role: '',
    experience: '',
    interests: [],
    notifications: {
      email: true,
      push: false,
      sms: false
    }
  });

  const interestOptions = [
    'Task Automation',
    'Data Analysis',
    'Content Creation',
    'Customer Support',
    'Development Tools',
    'Marketing',
    'Finance',
    'HR & Recruiting'
  ];

  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // Prepare data for backend
      const updateData: UserProfileUpdate = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        company: formData.company,
        role: formData.role,
        experience_level: formData.experience,
        interests: formData.interests,
        notifications_email: formData.notifications.email,
        notifications_push: formData.notifications.push,
        notifications_sms: formData.notifications.sms,
      };

      // Save profile to backend
      await api.userProfile.updateProfile(updateData);
      
      // Mark profile completion in onboarding
      try {
        await api.onboarding.completeItem('complete_profile');
      } catch (error) {
        console.warn('Failed to mark profile complete:', error);
      }

      console.log('Profile saved successfully:', formData);
      
      // Navigate to next step
      navigate('/onboarding/checklist');
    } catch (error) {
      console.error('Failed to save profile:', error);
      alert('Failed to save profile. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Complete Your Profile</h1>
          <p className="mt-2 text-gray-600">
            Help us personalize your CapeControl experience
          </p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Basic Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  id="firstName"
                  required
                  value={formData.firstName}
                  onChange={(e) => setFormData(prev => ({ ...prev, firstName: e.target.value }))}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  id="lastName"
                  required
                  value={formData.lastName}
                  onChange={(e) => setFormData(prev => ({ ...prev, lastName: e.target.value }))}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                  Company
                </label>
                <input
                  type="text"
                  id="company"
                  value={formData.company}
                  onChange={(e) => setFormData(prev => ({ ...prev, company: e.target.value }))}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                  Role
                </label>
                <select
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="">Select your role</option>
                  <option value="developer">Developer</option>
                  <option value="manager">Manager</option>
                  <option value="analyst">Data Analyst</option>
                  <option value="marketer">Marketer</option>
                  <option value="entrepreneur">Entrepreneur</option>
                  <option value="student">Student</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Experience Level */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Experience with AI Tools</h2>
            
            <div className="space-y-4">
              {[
                { value: 'beginner', label: 'Beginner', desc: 'New to AI automation tools' },
                { value: 'intermediate', label: 'Intermediate', desc: 'Some experience with AI tools' },
                { value: 'advanced', label: 'Advanced', desc: 'Experienced with multiple AI platforms' }
              ].map((level) => (
                <div key={level.value} className="flex items-start">
                  <input
                    type="radio"
                    id={level.value}
                    name="experience"
                    value={level.value}
                    checked={formData.experience === level.value}
                    onChange={(e) => setFormData(prev => ({ ...prev, experience: e.target.value }))}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div className="ml-3">
                    <label htmlFor={level.value} className="block text-sm font-medium text-gray-900">
                      {level.label}
                    </label>
                    <p className="text-sm text-gray-600">{level.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Interests */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Areas of Interest</h2>
            <p className="text-sm text-gray-600 mb-4">Select areas where you'd like to use AI agents (choose all that apply)</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {interestOptions.map((interest) => (
                <div key={interest} className="relative">
                  <input
                    type="checkbox"
                    id={`interest-${interest}`}
                    checked={formData.interests.includes(interest)}
                    onChange={() => handleInterestToggle(interest)}
                    className="sr-only"
                  />
                  <label
                    htmlFor={`interest-${interest}`}
                    className={`block p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      formData.interests.includes(interest)
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <span className="text-sm font-medium">{interest}</span>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Notification Preferences</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                  <p className="text-sm text-gray-600">Get updates about your agents and tasks</p>
                </div>
                <input
                  type="checkbox"
                  checked={formData.notifications.email}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, email: e.target.checked }
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">Push Notifications</h3>
                  <p className="text-sm text-gray-600">Real-time alerts in your browser</p>
                </div>
                <input
                  type="checkbox"
                  checked={formData.notifications.push}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, push: e.target.checked }
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">SMS Notifications</h3>
                  <p className="text-sm text-gray-600">Critical updates via text message</p>
                </div>
                <input
                  type="checkbox"
                  checked={formData.notifications.sms}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    notifications: { ...prev.notifications, sms: e.target.checked }
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-between">
            <button
              type="button"
              onClick={() => navigate('/onboarding/guide')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Back
            </button>
            
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Save Profile
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OnboardingProfile;