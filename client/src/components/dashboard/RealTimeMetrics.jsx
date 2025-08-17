import React from 'react';

const RealTimeMetrics = ({ realTimeData, loading }) => {
  if (!realTimeData && !loading) {
    return null;
  }

  const metrics = [
    {
      id: 'requests_per_minute',
      title: 'Requests/Minute',
      value: realTimeData?.quick_stats?.requests_per_minute || 0,
      unit: 'req/min',
      icon: '🚀',
      color: 'blue',
      format: (val) => Math.round(val)
    },
    {
      id: 'avg_response_time',
      title: 'Avg Response Time',
      value: realTimeData?.quick_stats?.avg_response_time || 0,
      unit: 'ms',
      icon: '⚡',
      color: realTimeData?.quick_stats?.avg_response_time > 1000 ? 'yellow' : 'green',
      format: (val) => Math.round(val)
    },
    {
      id: 'error_rate',
      title: 'Error Rate',
      value: realTimeData?.quick_stats?.error_rate || 0,
      unit: '%',
      icon: '⚠️',
      color: realTimeData?.quick_stats?.error_rate > 5 ? 'red' : realTimeData?.quick_stats?.error_rate > 2 ? 'yellow' : 'green',
      format: (val) => val.toFixed(2)
    },
    {
      id: 'active_errors',
      title: 'Active Errors',
      value: realTimeData?.quick_stats?.active_errors || 0,
      unit: 'errors',
      icon: '🔥',
      color: realTimeData?.quick_stats?.active_errors > 10 ? 'red' : realTimeData?.quick_stats?.active_errors > 0 ? 'yellow' : 'green',
      format: (val) => Math.round(val)
    },
    {
      id: 'cpu_percent',
      title: 'CPU Usage',
      value: realTimeData?.system_health?.cpu_percent || 0,
      unit: '%',
      icon: '💻',
      color: realTimeData?.system_health?.cpu_percent > 80 ? 'red' : realTimeData?.system_health?.cpu_percent > 70 ? 'yellow' : 'green',
      format: (val) => Math.round(val)
    },
    {
      id: 'memory_percent',
      title: 'Memory Usage',
      value: realTimeData?.system_health?.memory_percent || 0,
      unit: '%',
      icon: '🧠',
      color: realTimeData?.system_health?.memory_percent > 85 ? 'red' : realTimeData?.system_health?.memory_percent > 75 ? 'yellow' : 'green',
      format: (val) => Math.round(val)
    }
  ];

  const getColorClasses = (color, isBackground = false) => {
    const colorMap = {
      blue: isBackground ? 'bg-blue-50 border-blue-200' : 'text-blue-600',
      green: isBackground ? 'bg-green-50 border-green-200' : 'text-green-600',
      yellow: isBackground ? 'bg-yellow-50 border-yellow-200' : 'text-yellow-600',
      red: isBackground ? 'bg-red-50 border-red-200' : 'text-red-600',
      gray: isBackground ? 'bg-gray-50 border-gray-200' : 'text-gray-600'
    };
    return colorMap[color] || colorMap.gray;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Real-time Metrics
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {metrics.map((metric) => (
          <div
            key={metric.id}
            className={`p-4 rounded-lg border ${getColorClasses(metric.color, true)} transition-all duration-300 hover:shadow-md`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{metric.icon}</span>
              {loading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
              )}
            </div>
            
            <div className={`text-2xl font-bold ${getColorClasses(metric.color)} mb-1`}>
              {loading ? (
                <div className="animate-pulse bg-gray-200 h-6 w-12 rounded"></div>
              ) : (
                <>
                  {metric.format(metric.value)}
                  <span className="text-sm font-normal text-gray-500 ml-1">
                    {metric.unit}
                  </span>
                </>
              )}
            </div>
            
            <div className="text-xs text-gray-600">
              {metric.title}
            </div>
          </div>
        ))}
      </div>

      {/* Additional Real-time Info */}
      {realTimeData && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>
                System Status: 
                <span className={`ml-1 font-medium ${
                  realTimeData.system_status === 'healthy' ? 'text-green-600' :
                  realTimeData.system_status === 'degraded' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  {realTimeData.system_status?.charAt(0).toUpperCase() + realTimeData.system_status?.slice(1)}
                </span>
              </span>
              
              {realTimeData.alerts_count > 0 && (
                <span className="text-red-600">
                  🚨 {realTimeData.alerts_count} active alert{realTimeData.alerts_count !== 1 ? 's' : ''}
                </span>
              )}
            </div>
            
            <div className="text-xs text-gray-500">
              Updated: {new Date(realTimeData.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealTimeMetrics;
