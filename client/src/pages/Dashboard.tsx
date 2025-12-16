import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, DashboardStats, ActivityItem } from '../services/api';
import { PaymentDashboardSummary, RecentPaymentsWidget, QuickPaymentButton } from '../components/payments/PaymentIntegration';
import { PaymentStateProvider } from '../context/PaymentStateContext';
import { PaymentErrorBoundary } from '../components/payments/PaymentErrorBoundary';
import { features } from '../config/features';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const [statsData, activityData] = await Promise.all([
          api.dashboard.getStats(),
          api.dashboard.getRecentActivity(5),
        ]);
        setStats(statsData);
        setActivity(activityData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setError('Failed to load dashboard data. Please try again.');
        // Set fallback data for development
        setStats({
          active_agents: 3,
          tasks_complete: 42,
          system_status: 'operational',
          agents_deployed: 5,
          total_runs: 127,
          success_rate: 94.2,
        });
        setActivity([
          {
            id: '1',
            type: 'agent_deploy',
            title: 'Agent Deployed',
            description: 'Email automation agent deployed successfully',
            timestamp: new Date().toISOString(),
            status: 'success',
          },
          {
            id: '2',
            type: 'task_complete',
            title: 'Task Completed',
            description: 'Data analysis workflow completed',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            status: 'success',
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} days ago`;
    if (diffHours > 0) return `${diffHours} hours ago`;
    return 'Just now';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <span className="text-sm text-gray-500">Welcome back!</span>
          </div>
          <nav className="flex space-x-4">
            {features.onboarding && (
              <Link 
                to="/onboarding/guide" 
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Getting Started
              </Link>
            )}
            {features.payments && (
              <Link 
                to="/billing" 
                className="text-gray-600 hover:text-gray-700"
              >
                Billing
              </Link>
            )}
            <Link 
              to="/onboarding/profile" 
              className="text-gray-600 hover:text-gray-700"
            >
              Profile
            </Link>
            <Link 
              to="/about" 
              className="text-gray-600 hover:text-gray-700"
            >
              Help
            </Link>
          </nav>
        </div>
      </header>

      <main className="p-8">
        {error && (
          <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Notice</h3>
                <p className="mt-1 text-sm text-yellow-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Stats Overview */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Active Agents</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.active_agents || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Tasks Complete</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.tasks_complete || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">System Status</p>
                  <p className="text-lg font-bold text-green-600 capitalize">{stats?.system_status || 'Loading'}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Success Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{stats?.success_rate?.toFixed(1) || 0}%</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Recent Activity */}
          <section className="xl:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                {activity.length > 0 ? (
                  <div className="space-y-4">
                    {activity.map((item) => (
                      <div key={item.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50">
                        <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-2 ${
                          item.status === 'success' ? 'bg-green-400' : 
                          item.status === 'error' ? 'bg-red-400' : 'bg-yellow-400'
                        }`} />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900">{item.title}</p>
                          <p className="text-sm text-gray-500">{item.description}</p>
                          <p className="text-xs text-gray-400 mt-1">{formatTimestamp(item.timestamp)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-500">No recent activity</p>
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Quick Actions */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-4">
              {features.payments && (
                <PaymentErrorBoundary>
                  <div className="bg-white rounded-lg shadow p-4">
                    <QuickPaymentButton 
                      className="w-full"
                      onClick={() => window.location.href = '/checkout'}
                    />
                  </div>
                </PaymentErrorBoundary>
              )}

              {features.agentsShell && (
                <>
                  <Link
                    to="/agents"
                    className="block bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Manage Agents</p>
                        <p className="text-xs text-gray-500">Create, test, and deploy agents</p>
                      </div>
                    </div>
                  </Link>

                  <Link
                    to="/marketplace"
                    className="block bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Browse Marketplace</p>
                        <p className="text-xs text-gray-500">Find new tools and agents</p>
                      </div>
                    </div>
                  </Link>
                </>
              )}

              <Link
                to="/settings"
                className="block bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">System Settings</p>
                    <p className="text-xs text-gray-500">Configure your account</p>
                  </div>
                </div>
              </Link>
            </div>
          </section>

          {/* Payment Summary */}
          {features.payments && (
            <PaymentErrorBoundary>
              <PaymentStateProvider>
                <section>
                  <PaymentDashboardSummary />
                </section>
              </PaymentStateProvider>
            </PaymentErrorBoundary>
          )}
        </div>

        {/* Full-width Payment Widgets */}
        {features.payments && (
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Recent Payments */}
            <PaymentErrorBoundary>
              <PaymentStateProvider>
                <RecentPaymentsWidget 
                  className="lg:col-span-1"
                  limit={5}
                />
              </PaymentStateProvider>
            </PaymentErrorBoundary>

            {/* Payment Actions */}
            <section className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Actions</h3>
                <div className="space-y-4">
                  <Link
                    to="/checkout"
                    className="block bg-blue-50 rounded-lg p-4 hover:bg-blue-100 transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Make Payment</p>
                        <p className="text-xs text-gray-500">Process a new payment</p>
                      </div>
                    </div>
                  </Link>

                  <Link
                    to="/billing/methods"
                    className="block bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="p-2 bg-gray-100 rounded-lg">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Payment Methods</p>
                        <p className="text-xs text-gray-500">Manage your payment methods</p>
                      </div>
                    </div>
                  </Link>

                  <Link
                    to="/billing/invoices"
                    className="block bg-green-50 rounded-lg p-4 hover:bg-green-100 transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-900">Invoice History</p>
                        <p className="text-xs text-gray-500">View past invoices and payments</p>
                      </div>
                    </div>
                  </Link>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;