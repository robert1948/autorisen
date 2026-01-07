import React from "react";
import { Link } from "react-router-dom";

import AgentRegistryPanel from "../../features/dev/AgentRegistryPanel";

const Developer: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Developer Agent Builder</h1>
          </div>
          <nav className="flex space-x-4">
            <Link
              to="/marketplace"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Browse Marketplace
            </Link>
            <Link to="/app/agents" className="text-gray-600 hover:text-gray-700">
              My Agents
            </Link>
          </nav>
        </div>
      </header>

      <main className="p-8">
        <section className="mb-6 max-w-4xl">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Create, edit a manifest, and publish
          </h2>
          <p className="text-gray-600">
            Staging MVP: create an agent, edit the JSON manifest, and publish a version.
            To appear in the marketplace, set agent visibility to <strong>Public</strong>
            and publish a version.
          </p>
        </section>

        <section className="bg-white rounded-lg shadow">
          <div className="p-6">
            <AgentRegistryPanel />
          </div>
        </section>
      </main>
    </div>
  );
};

export default Developer;
