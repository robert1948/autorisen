import React, { useState, useEffect } from 'react';

const EndpointAnalytics = ({ loading }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedView, setSelectedView] = useState('volume');

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setAnalyticsLoading(true);
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch('/api/dashboard/analytics/endpoints', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setAnalyticsData(data);
          setError(null);
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (err) {
        console.error('Error fetching analytics data:', err);
        setError('Failed to load endpoint analytics');
      } finally {
        setAnalyticsLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  const viewOptions = [
    { id: 'volume', label: 'Top by Volume', icon: '📊' },
    { id: 'errors', label: 'Top by Errors', icon: '⚠️' },
    { id: 'slowest', label: 'Slowest Endpoints', icon: '🐌' }
  ];

  const getEndpointColor = (endpoint) => {
    if (endpoint.includes('/api/auth')) return 'text-blue-600 bg-blue-50';
    if (endpoint.includes('/api/cape')) return 'text-green-600 bg-green-50';
    if (endpoint.includes('/api/monitoring')) return 'text-purple-600 bg-purple-50';
    if (endpoint.includes('/api/dashboard')) return 'text-orange-600 bg-orange-50';
    if (endpoint.includes('/api/health')) return 'text-teal-600 bg-teal-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getMethodColor = (endpoint) => {
    if (endpoint.includes('GET')) return 'text-green-600 bg-green-100';
    if (endpoint.includes('POST')) return 'text-blue-600 bg-blue-100';
    if (endpoint.includes('PUT')) return 'text-yellow-600 bg-yellow-100';
    if (endpoint.includes('DELETE')) return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  const formatEndpoint = (endpoint) => {
    // Extract method and path
    const parts = endpoint.split(' ');
    const method = parts[0] || 'GET';
    const path = parts.slice(1).join(' ') || endpoint;
    
    return { method, path: path.length > 40 ? path.substring(0, 40) + '...' : path };
  };

  const EndpointRow = ({ endpoint, data, index, type }) => {
    const { method, path } = formatEndpoint(endpoint);
    
    return (
      <div className={`p-4 rounded-lg border ${getEndpointColor(endpoint)} transition-all duration-300 hover:shadow-md`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-sm font-bold text-gray-600">
              {index + 1}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-1">
                <span className={`px-2 py-1 text-xs font-mono rounded ${getMethodColor(endpoint)}`}>
                  {method}
                </span>
                <span className="font-medium text-gray-900 truncate">
                  {path}
                </span>
              </div>
              
              <div className="text-sm text-gray-600">
                {type === 'volume' && (
                  <>
                    {data.requests?.toLocaleString()} requests • Avg: {data.avg_response_time}ms
                  </>
                )}
                {type === 'errors' && (
                  <>
                    {data.errors} errors • Rate: {data.error_rate}%
                  </>
                )}
                {type === 'slowest' && (
                  <>
                    Avg: {data.avg_response_time}ms • Max: {data.max_response_time}ms
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex-shrink-0">
            {type === 'volume' && (
              <div className="text-right">
                <div className="text-lg font-semibold text-blue-600">
                  {data.requests?.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">requests</div>
              </div>
            )}
            {type === 'errors' && (
              <div className="text-right">
                <div className="text-lg font-semibold text-red-600">
                  {data.error_rate}%
                </div>
                <div className="text-xs text-gray-500">{data.errors} errors</div>
              </div>
            )}
            {type === 'slowest' && (
              <div className="text-right">
                <div className="text-lg font-semibold text-yellow-600">
                  {data.avg_response_time}ms
                </div>
                <div className="text-xs text-gray-500">avg time</div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const LoadingRow = () => (
    <div className="p-4 rounded-lg border border-gray-200 bg-gray-50">
      <div className="animate-pulse">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-1/2"></div>
          </div>
          <div className="w-16 h-8 bg-gray-300 rounded"></div>
        </div>
      </div>
    </div>
  );

  const renderAnalyticsData = () => {
    if (analyticsLoading || !analyticsData) {
      return (
        <div className="space-y-4">
          <LoadingRow />
          <LoadingRow />
          <LoadingRow />
          <LoadingRow />
          <LoadingRow />
        </div>
      );
    }

    let data = [];
    let type = selectedView;

    switch (selectedView) {
      case 'volume':
        data = analyticsData.top_by_volume || [];
        break;
      case 'errors':
        data = analyticsData.top_by_errors || [];
        break;
      case 'slowest':
        data = analyticsData.slowest_endpoints || [];
        break;
    }

    if (data.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">📊</div>
          <p>No endpoint data available</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {data.slice(0, 10).map((item, index) => (
          <EndpointRow
            key={`${item.endpoint}-${index}`}
            endpoint={item.endpoint}
            data={item}
            index={index}
            type={type}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Endpoint Analytics
        </h3>
        
        {analyticsData && (
          <div className="text-sm text-gray-500">
            {analyticsData.total_endpoints} total endpoints
          </div>
        )}
      </div>

      {/* View Selector */}
      <div className="flex flex-wrap gap-2 mb-6">
        {viewOptions.map((option) => (
          <button
            key={option.id}
            onClick={() => setSelectedView(option.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
              selectedView === option.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <span>{option.icon}</span>
            <span>{option.label}</span>
          </button>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <span className="text-red-400 text-xl mr-2">⚠️</span>
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* Analytics Data */}
      {renderAnalyticsData()}

      {/* Summary Stats */}
      {analyticsData && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData.total_endpoints}
              </div>
              <div className="text-sm text-gray-600">Total Endpoints</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {analyticsData.top_by_volume?.reduce((sum, item) => sum + (item.requests || 0), 0)?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600">Total Requests</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {analyticsData.top_by_errors?.reduce((sum, item) => sum + (item.errors || 0), 0) || 0}
              </div>
              <div className="text-sm text-gray-600">Total Errors</div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-600">
          <p className="mb-2"><strong>Endpoint Categories:</strong></p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-50 border border-blue-200 rounded"></div>
              <span>Authentication</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-50 border border-green-200 rounded"></div>
              <span>AI Services</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-purple-50 border border-purple-200 rounded"></div>
              <span>Monitoring</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-orange-50 border border-orange-200 rounded"></div>
              <span>Dashboard</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-teal-50 border border-teal-200 rounded"></div>
              <span>Health</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EndpointAnalytics;
