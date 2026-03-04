import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiFetch } from '../../lib/apiFetch';
import { fetchMarketplaceCategories } from '../../lib/api';
import MarketplaceShowcase from '../../features/marketplace/MarketplaceShowcase';

interface MarketplaceStats {
  total_agents: number;
  total_downloads: number;
  active_users: number;
  popular_categories: { category: string; count: number }[];
}

/** Human-friendly labels and colour classes for each AgentCategory. */
const CATEGORY_META: Record<string, { label: string; color: string }> = {
  automation: { label: 'Automation', color: 'yellow' },
  analytics: { label: 'Analytics', color: 'blue' },
  integration: { label: 'Integration', color: 'indigo' },
  security: { label: 'Security', color: 'red' },
  productivity: { label: 'Productivity', color: 'green' },
  ai_assistant: { label: 'AI Assistant', color: 'purple' },
  workflow: { label: 'Workflow', color: 'orange' },
  monitoring: { label: 'Monitoring', color: 'cyan' },
  communication: { label: 'Communication', color: 'pink' },
  development: { label: 'Development', color: 'slate' },
};

const Marketplace: React.FC = () => {
  const [stats, setStats] = useState<MarketplaceStats | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  useEffect(() => {
    apiFetch('/marketplace/analytics')
      .then((data) => setStats(data as MarketplaceStats))
      .catch(() => setStats(null));
    fetchMarketplaceCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);
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
            
            {/* Quick Stats — fetched from /api/marketplace/analytics */}
            {stats && stats.total_agents > 0 && (
            <div className="grid grid-cols-3 gap-6 bg-white rounded-lg shadow p-6">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">{stats.total_agents}</p>
                <p className="text-sm text-gray-500">Published Agents</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">{stats.total_downloads || '—'}</p>
                <p className="text-sm text-gray-500">Agent Deployments</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">{stats.active_users || '—'}</p>
                <p className="text-sm text-gray-500">Active Users</p>
              </div>
            </div>
            )}
          </div>
        </section>

        {/* Categories — fetched from /api/marketplace/categories */}
        {categories.length > 0 && (
        <section className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Browse Categories</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {categories.map((cat) => {
              const meta = CATEGORY_META[cat] ?? { label: cat, color: 'gray' };
              const isActive = selectedCategory === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(isActive ? null : cat)}
                  className={`rounded-lg border p-3 text-left transition-shadow hover:shadow-md ${
                    isActive
                      ? `bg-${meta.color}-100 border-${meta.color}-400 ring-2 ring-${meta.color}-300`
                      : 'bg-white border-gray-200'
                  }`}
                >
                  <p className={`font-medium ${isActive ? `text-${meta.color}-700` : 'text-gray-900'}`}>
                    {meta.label}
                  </p>
                  {stats?.popular_categories && (() => {
                    const found = stats.popular_categories.find((c) => c.category === cat);
                    return found ? (
                      <p className="text-xs text-gray-500 mt-1">{found.count} agent{found.count !== 1 ? 's' : ''}</p>
                    ) : null;
                  })()}
                </button>
              );
            })}
          </div>
        </section>
        )}

        {/* Main Marketplace Component */}
        <section className="bg-white rounded-lg shadow">
          <div className="p-6">
            <MarketplaceShowcase categoryFilter={selectedCategory} />
          </div>
        </section>
      </main>
    </div>
  );
};

export default Marketplace;