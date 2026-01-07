import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AgentWorkbench from '../../features/dev/AgentWorkbench';
import AgentRegistryPanel from '../../features/dev/AgentRegistryPanel';

const Agents: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'manage' | 'workbench'>('manage');
  const [chatLaunched, setChatLaunched] = useState(false);
  const navigate = useNavigate();

  const handleLaunchChat = () => {
    setChatLaunched(true);
    setActiveTab('workbench');
    navigate('/chat?placement=developer');
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
            <h1 className="text-2xl font-bold text-gray-900">My Agents</h1>
          </div>
          <nav className="flex space-x-4">
            <Link 
              to="/marketplace" 
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Browse Marketplace
            </Link>
            <Link 
              to="/dashboard" 
              className="text-gray-600 hover:text-gray-700"
            >
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      <main className="p-8">
        {/* Page Introduction */}
        <section className="mb-8">
          <div className="max-w-4xl">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Create, Test & Deploy Your AI Agents
            </h2>
            <p className="text-gray-600 mb-6">
              Develop custom agents with the integrated workbench, manage your agent registry, 
              and deploy to production when ready.
            </p>
            
            {/* Agent Development Flow */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 7.172V5L8 4z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">1. Prototype</h3>
                    <p className="text-sm text-gray-500">Test prompts & tools</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  Use the workbench to iterate on prompts, inspect tool calls, and validate behavior with live logs.
                </p>
              </div>

              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">2. Register</h3>
                    <p className="text-sm text-gray-500">Create agent versions</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  Register successful prototypes as versioned agents with proper manifests and documentation.
                </p>
              </div>

              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">3. Deploy</h3>
                    <p className="text-sm text-gray-500">Publish & share</p>
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  Deploy to production and optionally publish to the marketplace for community use.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Tab Navigation */}
        <section className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('manage')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'manage'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Agent Registry
              </button>
              <button
                onClick={() => setActiveTab('workbench')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'workbench'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Development Workbench
                {chatLaunched && (
                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Active
                  </span>
                )}
              </button>
            </nav>
          </div>
        </section>

        {/* Tab Content */}
        <section className="bg-white rounded-lg shadow">
          <div className="p-6">
            {activeTab === 'manage' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Agent Registry</h3>
                  <p className="text-gray-600">
                    Manage your private agents, create new versions, and publish to the marketplace.
                  </p>
                </div>
                <AgentRegistryPanel />
              </div>
            )}

            {activeTab === 'workbench' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Development Workbench</h3>
                  <p className="text-gray-600">
                    Test agent behavior, inspect tool calls, and iterate on prompts with live feedback.
                  </p>
                </div>
                
                {/* Workbench Component */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div>
                    <AgentWorkbench onLaunchChat={handleLaunchChat} />
                  </div>
                  
                  <div className="space-y-6">
                    {/* Live Session Status */}
                    <div className={`p-4 rounded-lg border ${
                      chatLaunched 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          chatLaunched ? 'bg-green-500' : 'bg-gray-400'
                        }`} />
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {chatLaunched ? 'Workbench Active' : 'Ready to Test'}
                          </h4>
                          <p className="text-sm text-gray-600">
                            {chatLaunched 
                              ? 'Agent testing session in progress'
                              : 'Click "Open Agent Workbench" to start testing'
                            }
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-900">Quick Actions</h4>
                      <div className="space-y-2">
                        <Link
                          to="/marketplace"
                          className="block p-3 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <div>
                              <p className="font-medium text-gray-900">Browse Examples</p>
                              <p className="text-sm text-gray-500">Find inspiration in the marketplace</p>
                            </div>
                          </div>
                        </Link>
                        
                        <div className="block p-3 border border-gray-200 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <div>
                              <p className="font-medium text-gray-900">View Documentation</p>
                              <p className="text-sm text-gray-500">Learn agent development best practices</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Agents;
