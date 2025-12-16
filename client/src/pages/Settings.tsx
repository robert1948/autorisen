import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import ProfileSettings from './profile/ProfileSettings';
import Security from './profile/Security';
import ApiTokens from './profile/ApiTokens';
import { features } from '../config/features';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'api' | 'billing'>('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: 'user' },
    { id: 'security', label: 'Security', icon: 'shield' },
    { id: 'api', label: 'API Tokens', icon: 'key' },
    ...(features.payments ? [{ id: 'billing', label: 'Billing', icon: 'credit-card' }] : [])
  ];

  const getTabIcon = (iconType: string) => {
    const baseClasses = "w-5 h-5";
    switch (iconType) {
      case 'user':
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        );
      case 'shield':
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        );
      case 'key':
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
          </svg>
        );
      case 'credit-card':
        return (
          <svg className={baseClasses} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
          </div>
          <nav className="flex space-x-4">
            <Link 
              to="/dashboard" 
              className="text-gray-600 hover:text-gray-700"
            >
              Dashboard
            </Link>
            {features.agentsShell && (
              <Link 
                to="/agents" 
                className="text-gray-600 hover:text-gray-700"
              >
                My Agents
              </Link>
            )}
          </nav>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
          <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Settings</h2>
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <div className={activeTab === tab.id ? 'text-blue-600' : 'text-gray-400'}>
                    {getTabIcon(tab.icon)}
                  </div>
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>

            {/* Quick Links */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-500 mb-3">Quick Links</h3>
              <div className="space-y-2">
                <Link
                  to="/onboarding/checklist"
                  className="block text-sm text-gray-600 hover:text-gray-900"
                >
                  Onboarding Status
                </Link>
                <Link
                  to="/marketplace"
                  className="block text-sm text-gray-600 hover:text-gray-900"
                >
                  Browse Marketplace
                </Link>
                <Link
                  to="/about"
                  className="block text-sm text-gray-600 hover:text-gray-900"
                >
                  Help & Support
                </Link>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <div className="max-w-4xl">
            {/* Tab Content */}
            {activeTab === 'profile' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Profile Settings</h2>
                  <p className="text-gray-600">
                    Manage your personal information and account preferences.
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow">
                  <div className="p-6">
                    <ProfileSettings />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Security Settings</h2>
                  <p className="text-gray-600">
                    Manage your password, two-factor authentication, and security preferences.
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow">
                  <div className="p-6">
                    <Security />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">API Access</h2>
                  <p className="text-gray-600">
                    Generate and manage API tokens for programmatic access to your agents.
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow">
                  <div className="p-6">
                    <ApiTokens />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'billing' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Billing & Subscription</h2>
                  <p className="text-gray-600">
                    Manage your subscription, payment methods, and billing history.
                  </p>
                </div>

                <div className="space-y-6">
                  {/* Current Plan */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Current Plan</h3>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">You're currently on the</p>
                        <p className="text-xl font-bold text-blue-600">Professional Plan</p>
                        <p className="text-sm text-gray-500">$49/month • Billed monthly</p>
                      </div>
                      <div className="text-right">
                        <Link
                          to="/subscribe"
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Change Plan
                        </Link>
                      </div>
                    </div>
                  </div>

                  {/* Usage */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Current Usage</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Active Agents</span>
                          <span>3 of 50</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full" style={{ width: '6%' }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>API Calls (This Month)</span>
                          <span>1,247 of 100,000</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-600 h-2 rounded-full" style={{ width: '1.2%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Payment Method */}
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Payment Method</h3>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-gray-100 rounded">
                          <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium">•••• •••• •••• 4242</p>
                          <p className="text-sm text-gray-500">Expires 12/25</p>
                        </div>
                      </div>
                      <button className="ml-auto bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                        Update
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Settings;