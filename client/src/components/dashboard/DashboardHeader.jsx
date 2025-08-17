import React from 'react';

const DashboardHeader = ({
  systemStatus,
  realTimeData,
  timeWindow,
  onTimeWindowChange,
  autoRefresh,
  onAutoRefreshToggle,
  onRefresh,
  lastUpdate,
  loading
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'unhealthy':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return '✅';
      case 'degraded':
        return '⚠️';
      case 'unhealthy':
        return '❌';
      default:
        return '❓';
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Left Side - Title and Status */}
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Performance Dashboard
            </h1>
            
            {/* System Status Badge */}
            <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(systemStatus)}`}>
              <span className="mr-1">{getStatusIcon(systemStatus)}</span>
              {systemStatus ? systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1) : 'Unknown'}
            </div>

            {/* Loading Indicator */}
            {loading && (
              <div className="flex items-center text-sm text-blue-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                Updating...
              </div>
            )}
          </div>

          {/* Right Side - Controls */}
          <div className="flex items-center space-x-4">
            {/* Quick Stats */}
            {realTimeData && (
              <div className="hidden md:flex items-center space-x-6 text-sm">
                <div className="text-center">
                  <div className="font-semibold text-blue-600">
                    {Math.round(realTimeData.quick_stats?.requests_per_minute || 0)}
                  </div>
                  <div className="text-gray-500">req/min</div>
                </div>
                <div className="text-center">
                  <div className="font-semibold text-green-600">
                    {Math.round(realTimeData.quick_stats?.avg_response_time || 0)}ms
                  </div>
                  <div className="text-gray-500">response</div>
                </div>
                <div className="text-center">
                  <div className={`font-semibold ${
                    (realTimeData.quick_stats?.error_rate || 0) > 5 
                      ? 'text-red-600' 
                      : 'text-green-600'
                  }`}>
                    {(realTimeData.quick_stats?.error_rate || 0).toFixed(1)}%
                  </div>
                  <div className="text-gray-500">errors</div>
                </div>
              </div>
            )}

            {/* Time Window Selector */}
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Time:</label>
              <select
                value={timeWindow}
                onChange={(e) => onTimeWindowChange(parseInt(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>1 Hour</option>
                <option value={6}>6 Hours</option>
                <option value={24}>24 Hours</option>
                <option value={72}>3 Days</option>
                <option value={168}>1 Week</option>
              </select>
            </div>

            {/* Auto Refresh Toggle */}
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Auto:</label>
              <button
                onClick={onAutoRefreshToggle}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    autoRefresh ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            {/* Manual Refresh Button */}
            <button
              onClick={onRefresh}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <span className={`${loading ? 'animate-spin' : ''}`}>
                {loading ? '⟳' : '🔄'}
              </span>
              <span>Refresh</span>
            </button>

            {/* Export Button */}
            <div className="relative">
              <button
                className="bg-gray-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-700 transition-colors"
                onClick={() => {
                  // This would trigger an export modal or dropdown
                  alert('Export functionality coming soon');
                }}
              >
                📊 Export
              </button>
            </div>
          </div>
        </div>

        {/* Last Update Info */}
        {lastUpdate && (
          <div className="pb-2">
            <div className="text-xs text-gray-500">
              Last updated: {lastUpdate}
              {autoRefresh && (
                <span className="ml-2 text-green-600">
                  • Auto-refresh enabled
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardHeader;
