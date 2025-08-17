import { useState, useEffect, useCallback } from 'react';
import { Activity, Database, Server, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://www.cape-control.com/api' 
  : 'http://localhost:8001/api';

export default function HealthDashboard() {
  const [healthData, setHealthData] = useState({
    api: { status: 'checking', responseTime: null, lastCheck: null },
    database: { status: 'checking', responseTime: null, lastCheck: null },
    auth: { status: 'checking', responseTime: null, lastCheck: null },
    overall: 'checking'
  });
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const checkHealth = useCallback(async () => {
    setIsRefreshing(true);
    const results = {};
    
    // Check API Health
    try {
      const start = performance.now();
      const response = await fetch(`${API_BASE}/health/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const responseTime = Math.round(performance.now() - start);
      
      results.api = {
        status: response.ok ? 'healthy' : 'unhealthy',
        responseTime,
        lastCheck: new Date().toISOString(),
        details: response.ok ? await response.json() : null
      };
    } catch (error) {
      results.api = {
        status: 'error',
        responseTime: null,
        lastCheck: new Date().toISOString(),
        error: error.message
      };
    }

    // Check Database Health
    try {
      const start = performance.now();
      const response = await fetch(`${API_BASE}/health/database`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const responseTime = Math.round(performance.now() - start);
      
      results.database = {
        status: response.ok ? 'healthy' : 'unhealthy',
        responseTime,
        lastCheck: new Date().toISOString(),
        details: response.ok ? await response.json() : null
      };
    } catch (error) {
      results.database = {
        status: 'error',
        responseTime: null,
        lastCheck: new Date().toISOString(),
        error: error.message
      };
    }

    // Check Auth Health
    try {
      const start = performance.now();
      const response = await fetch(`${API_BASE}/auth/v2/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const responseTime = Math.round(performance.now() - start);
      
      results.auth = {
        status: response.ok ? 'healthy' : 'unhealthy',
        responseTime,
        lastCheck: new Date().toISOString(),
        details: response.ok ? await response.json() : null
      };
    } catch (error) {
      results.auth = {
        status: 'error',
        responseTime: null,
        lastCheck: new Date().toISOString(),
        error: error.message
      };
    }

    // Determine overall health
    const statuses = Object.values(results).map(r => r.status);
    let overall = 'healthy';
    if (statuses.includes('error')) overall = 'error';
    else if (statuses.includes('unhealthy')) overall = 'unhealthy';

    setHealthData({ ...results, overall });
    setIsRefreshing(false);
  }, []);

  useEffect(() => {
    checkHealth();
    
    if (autoRefresh) {
      const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
      return () => clearInterval(interval);
    }
  }, [checkHealth, autoRefresh]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'unhealthy': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <div className="w-5 h-5 animate-pulse bg-gray-300 rounded-full" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'border-green-200 bg-green-50';
      case 'unhealthy': return 'border-yellow-200 bg-yellow-50';
      case 'error': return 'border-red-200 bg-red-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const formatResponseTime = (time) => {
    if (time === null) return 'N/A';
    if (time < 1000) return `${time}ms`;
    return `${(time / 1000).toFixed(2)}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white p-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">System Health Dashboard</h1>
              <p className="text-gray-600">Real-time monitoring of CapeControl system components</p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="mr-2"
                />
                Auto-refresh (30s)
              </label>
              <button
                onClick={checkHealth}
                disabled={isRefreshing}
                className="btn-mobile bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {isRefreshing ? (
                  <div className="flex items-center">
                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                    Checking...
                  </div>
                ) : (
                  'Refresh Now'
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Overall Status */}
        <div className={`p-6 rounded-lg border-2 mb-6 ${getStatusColor(healthData.overall)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              {getStatusIcon(healthData.overall)}
              <span className="ml-3 text-lg font-semibold">
                Overall System Status: {healthData.overall.charAt(0).toUpperCase() + healthData.overall.slice(1)}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              Last updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>

        {/* Individual Component Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* API Health */}
          <div className={`p-6 rounded-lg border ${getStatusColor(healthData.api.status)}`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Server className="w-6 h-6 text-blue-600 mr-3" />
                <h3 className="text-lg font-semibold">API Server</h3>
              </div>
              {getStatusIcon(healthData.api.status)}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Response Time:</span>
                <span className="font-mono">{formatResponseTime(healthData.api.responseTime)}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Check:</span>
                <span className="font-mono">
                  {healthData.api.lastCheck ? new Date(healthData.api.lastCheck).toLocaleTimeString() : 'N/A'}
                </span>
              </div>
              {healthData.api.error && (
                <div className="text-red-600 text-xs mt-2">
                  Error: {healthData.api.error}
                </div>
              )}
            </div>
          </div>

          {/* Database Health */}
          <div className={`p-6 rounded-lg border ${getStatusColor(healthData.database.status)}`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Database className="w-6 h-6 text-green-600 mr-3" />
                <h3 className="text-lg font-semibold">Database</h3>
              </div>
              {getStatusIcon(healthData.database.status)}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Response Time:</span>
                <span className="font-mono">{formatResponseTime(healthData.database.responseTime)}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Check:</span>
                <span className="font-mono">
                  {healthData.database.lastCheck ? new Date(healthData.database.lastCheck).toLocaleTimeString() : 'N/A'}
                </span>
              </div>
              {healthData.database.error && (
                <div className="text-red-600 text-xs mt-2">
                  Error: {healthData.database.error}
                </div>
              )}
            </div>
          </div>

          {/* Auth Health */}
          <div className={`p-6 rounded-lg border ${getStatusColor(healthData.auth.status)}`}>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <Activity className="w-6 h-6 text-purple-600 mr-3" />
                <h3 className="text-lg font-semibold">Authentication</h3>
              </div>
              {getStatusIcon(healthData.auth.status)}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Response Time:</span>
                <span className="font-mono">{formatResponseTime(healthData.auth.responseTime)}</span>
              </div>
              <div className="flex justify-between">
                <span>Last Check:</span>
                <span className="font-mono">
                  {healthData.auth.lastCheck ? new Date(healthData.auth.lastCheck).toLocaleTimeString() : 'N/A'}
                </span>
              </div>
              {healthData.auth.error && (
                <div className="text-red-600 text-xs mt-2">
                  Error: {healthData.auth.error}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-8 p-6 bg-white rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Performance Summary
          </h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {formatResponseTime(healthData.api.responseTime)}
              </div>
              <div className="text-sm text-gray-600">API Response</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {formatResponseTime(healthData.database.responseTime)}
              </div>
              <div className="text-sm text-gray-600">Database Query</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {formatResponseTime(healthData.auth.responseTime)}
              </div>
              <div className="text-sm text-gray-600">Auth Service</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
