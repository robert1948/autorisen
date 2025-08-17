import React from 'react';

const SystemMetrics = ({ widgets, loading }) => {
  if (!widgets && !loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h3>
        <p className="text-gray-500">No system metrics available</p>
      </div>
    );
  }

  // Filter system-related widgets
  const systemWidgets = widgets.filter(widget => 
    widget.id.includes('cpu') || 
    widget.id.includes('memory') || 
    widget.id.includes('disk') ||
    widget.id.includes('system')
  );

  const performanceWidgets = widgets.filter(widget =>
    widget.id.includes('request') ||
    widget.id.includes('response') ||
    widget.id.includes('error')
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return '📈';
      case 'down':
        return '📉';
      case 'stable':
        return '➡️';
      default:
        return '─';
    }
  };

  const getWidgetIcon = (id) => {
    if (id.includes('cpu')) return '💻';
    if (id.includes('memory')) return '🧠';
    if (id.includes('disk')) return '💾';
    if (id.includes('request')) return '🚀';
    if (id.includes('response')) return '⚡';
    if (id.includes('error')) return '⚠️';
    if (id.includes('system')) return '🖥️';
    return '📊';
  };

  const formatValue = (value, unit) => {
    if (typeof value === 'number') {
      if (value > 1000 && unit !== '%') {
        return (value / 1000).toFixed(1) + 'K';
      }
      return value.toFixed(1);
    }
    return value;
  };

  const WidgetCard = ({ widget }) => (
    <div className={`p-4 rounded-lg border ${getStatusColor(widget.status)} transition-all duration-300 hover:shadow-md`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getWidgetIcon(widget.id)}</span>
          <h4 className="font-medium text-gray-900">{widget.title}</h4>
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-sm">{getTrendIcon(widget.trend)}</span>
          <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(widget.status)}`}>
            {widget.status}
          </span>
        </div>
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-bold text-gray-900">
          {formatValue(widget.value, widget.unit)}
        </span>
        {widget.unit && (
          <span className="text-sm text-gray-500">{widget.unit}</span>
        )}
      </div>

      {/* Progress bar for percentage values */}
      {widget.unit === '%' && typeof widget.value === 'number' && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                widget.status === 'healthy' ? 'bg-green-500' :
                widget.status === 'warning' ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${Math.min(widget.value, 100)}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Thresholds info */}
      {widget.metadata?.threshold_warning && (
        <div className="mt-2 text-xs text-gray-500">
          Warning: {widget.metadata.threshold_warning}{widget.unit}
          {widget.metadata?.threshold_critical && (
            <span className="ml-2">
              Critical: {widget.metadata.threshold_critical}{widget.unit}
            </span>
          )}
        </div>
      )}
    </div>
  );

  const LoadingCard = () => (
    <div className="p-4 rounded-lg border border-gray-200 bg-gray-50">
      <div className="animate-pulse">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gray-300 rounded"></div>
            <div className="h-4 bg-gray-300 rounded w-24"></div>
          </div>
          <div className="h-6 bg-gray-300 rounded w-16"></div>
        </div>
        <div className="h-8 bg-gray-300 rounded w-20 mb-3"></div>
        <div className="w-full bg-gray-300 rounded-full h-2"></div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* System Resources */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">🖥️</span>
          System Resources
        </h3>
        
        <div className="space-y-4">
          {loading ? (
            <>
              <LoadingCard />
              <LoadingCard />
              <LoadingCard />
            </>
          ) : systemWidgets.length > 0 ? (
            systemWidgets.map((widget) => (
              <WidgetCard key={widget.id} widget={widget} />
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No system metrics available</p>
          )}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">📊</span>
          Performance Metrics
        </h3>
        
        <div className="space-y-4">
          {loading ? (
            <>
              <LoadingCard />
              <LoadingCard />
            </>
          ) : performanceWidgets.length > 0 ? (
            performanceWidgets.map((widget) => (
              <WidgetCard key={widget.id} widget={widget} />
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No performance metrics available</p>
          )}
        </div>
      </div>

      {/* System Status Summary */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">🎯</span>
          Status Summary
        </h3>
        
        <div className="space-y-3">
          {loading ? (
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-300 rounded w-full"></div>
              <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              <div className="h-4 bg-gray-300 rounded w-1/2"></div>
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Overall Health</span>
                <span className={`text-sm font-medium ${
                  systemWidgets.every(w => w.status === 'healthy') ? 'text-green-600' :
                  systemWidgets.some(w => w.status === 'critical') ? 'text-red-600' :
                  'text-yellow-600'
                }`}>
                  {systemWidgets.every(w => w.status === 'healthy') ? 'Excellent' :
                   systemWidgets.some(w => w.status === 'critical') ? 'Needs Attention' :
                   'Good'}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Widgets</span>
                <span className="text-sm font-medium text-gray-900">
                  {systemWidgets.length + performanceWidgets.length}
                </span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Last Update</span>
                <span className="text-sm font-medium text-gray-900">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default SystemMetrics;
