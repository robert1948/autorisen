import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// Individual dashboard components
import DashboardHeader from './DashboardHeader';
import SystemMetrics from './SystemMetrics';
import PerformanceCharts from './PerformanceCharts';
import AlertPanel from './AlertPanel';
import EndpointAnalytics from './EndpointAnalytics';
import RealTimeMetrics from './RealTimeMetrics';

const PerformanceDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeWindow, setTimeWindow] = useState(24);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const navigate = useNavigate();

  // Fetch complete dashboard data
  const fetchDashboardData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await fetch(`/api/dashboard/?time_window=${timeWindow}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setLastUpdate(new Date().toLocaleTimeString());
        setError(null);
      } else if (response.status === 401) {
        navigate('/login');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    }
  }, [timeWindow, navigate]);

  // Fetch real-time data
  const fetchRealTimeData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('/api/dashboard/real-time', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRealTimeData(data);
      }
    } catch (err) {
      console.error('Error fetching real-time data:', err);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchDashboardData(),
        fetchRealTimeData()
      ]);
      setLoading(false);
    };

    loadData();
  }, [fetchDashboardData, fetchRealTimeData]);

  // Auto-refresh setup
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchRealTimeData();
      
      // Refresh full dashboard data every 2 minutes
      const now = new Date();
      if (!lastUpdate || (now - new Date(lastUpdate)) > 120000) {
        fetchDashboardData();
      }
    }, 10000); // 10 second intervals

    return () => clearInterval(interval);
  }, [autoRefresh, fetchDashboardData, fetchRealTimeData, lastUpdate]);

  // Handle time window change
  const handleTimeWindowChange = (newTimeWindow) => {
    setTimeWindow(newTimeWindow);
  };

  // Handle manual refresh
  const handleRefresh = async () => {
    setLoading(true);
    await Promise.all([
      fetchDashboardData(),
      fetchRealTimeData()
    ]);
    setLoading(false);
  };

  // Handle auto-refresh toggle
  const handleAutoRefreshToggle = () => {
    setAutoRefresh(!autoRefresh);
  };

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Loading Performance Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Dashboard Header */}
      <DashboardHeader
        systemStatus={dashboardData?.system_status}
        realTimeData={realTimeData}
        timeWindow={timeWindow}
        onTimeWindowChange={handleTimeWindowChange}
        autoRefresh={autoRefresh}
        onAutoRefreshToggle={handleAutoRefreshToggle}
        onRefresh={handleRefresh}
        lastUpdate={lastUpdate}
        loading={loading}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="text-red-400 text-xl mr-3">⚠️</div>
              <div className="flex-1">
                <h3 className="text-red-800 font-medium">Dashboard Warning</h3>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Real-time Metrics Row */}
        <div className="mb-8">
          <RealTimeMetrics 
            realTimeData={realTimeData}
            loading={loading}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - System Metrics */}
          <div className="lg:col-span-1">
            <SystemMetrics 
              widgets={dashboardData?.widgets || []}
              loading={loading}
            />
          </div>

          {/* Right Column - Charts and Analytics */}
          <div className="lg:col-span-2 space-y-8">
            {/* Performance Charts */}
            <PerformanceCharts 
              timeWindow={timeWindow}
              loading={loading}
            />

            {/* Endpoint Analytics */}
            <EndpointAnalytics 
              loading={loading}
            />
          </div>
        </div>

        {/* Alert Panel */}
        <div className="mt-8">
          <AlertPanel 
            alerts={dashboardData?.alerts || []}
            loading={loading}
          />
        </div>

        {/* Performance Summary */}
        {dashboardData?.performance_summary && (
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Performance Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {Object.entries(dashboardData.performance_summary.key_metrics || {}).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{value}</div>
                    <div className="text-sm text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}
                    </div>
                  </div>
                ))}
              </div>
              
              {dashboardData.performance_summary.recommendations && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
                  <ul className="space-y-1">
                    {dashboardData.performance_summary.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>CapeControl Performance Dashboard v3.0.0</p>
          {lastUpdate && (
            <p>Last updated: {lastUpdate}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
