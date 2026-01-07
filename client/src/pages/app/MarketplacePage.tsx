import React from 'react';
import { Link } from 'react-router-dom';
import MarketplaceShowcase from '../../features/marketplace/MarketplaceShowcase';

const Marketplace: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Agent Marketplace</h1>
          </div>
          <nav className="flex space-x-4">
            <Link 
              to="/agents" 
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              My Agents
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
              Discover & Deploy AI Agents
            </h2>
            <p className="text-gray-600 mb-6">
              Browse curated agents from the community. Launch them in your workspace, 
              review their manifests, or get inspiration for your own agent creations.
            </p>
            
            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-6 bg-white rounded-lg shadow p-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">25+</p>
                <p className="text-sm text-gray-500">Published Agents</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">1.2k</p>
                <p className="text-sm text-gray-500">Agent Deployments</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">4.8★</p>
                <p className="text-sm text-gray-500">Average Rating</p>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Categories */}
        <section className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Popular Categories</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Support</p>
                  <p className="text-sm text-gray-500">8 agents</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Onboarding</p>
                  <p className="text-sm text-gray-500">5 agents</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Energy</p>
                  <p className="text-sm text-gray-500">7 agents</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Finance</p>
                  <p className="text-sm text-gray-500">5 agents</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Main Marketplace Component */}
        <section className="bg-white rounded-lg shadow">
          <div className="p-6">
            <MarketplaceShowcase />
          </div>
        </section>
      </main>
    </div>
  );
};

export default Marketplace;