import React, { useState } from 'react';

const AlertPanel = ({ alerts, loading }) => {
  const [filter, setFilter] = useState('all');
  const [expandedAlert, setExpandedAlert] = useState(null);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return '🚨';
      case 'high':
        return '⚠️';
      case 'medium':
        return '⚡';
      case 'low':
        return 'ℹ️';
      default:
        return '📋';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'system':
        return '🖥️';
      case 'performance':
        return '📊';
      case 'security':
        return '🔒';
      case 'network':
        return '🌐';
      default:
        return '📋';
    }
  };

  const filteredAlerts = alerts?.filter(alert => {
    if (filter === 'all') return true;
    return alert.severity === filter;
  }) || [];

  const alertCounts = {
    all: alerts?.length || 0,
    critical: alerts?.filter(a => a.severity === 'critical').length || 0,
    high: alerts?.filter(a => a.severity === 'high').length || 0,
    medium: alerts?.filter(a => a.severity === 'medium').length || 0,
    low: alerts?.filter(a => a.severity === 'low').length || 0
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/dashboard/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // In a real app, this would update the alerts state
        console.log(`Alert ${alertId} acknowledged`);
      }
    } catch (err) {
      console.error('Error acknowledging alert:', err);
    }
  };

  const AlertCard = ({ alert }) => (
    <div className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)} transition-all duration-300 hover:shadow-md`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="flex items-center space-x-2">
            <span className="text-xl">{getSeverityIcon(alert.severity)}</span>
            <span className="text-sm">{getTypeIcon(alert.type)}</span>
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h4 className="font-medium text-gray-900 truncate">
                {alert.title}
              </h4>
              <span className={`px-2 py-1 text-xs rounded-full ${getSeverityColor(alert.severity)}`}>
                {alert.severity}
              </span>
            </div>
            
            <p className="text-sm text-gray-600 mb-2">
              {alert.message}
            </p>
            
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span>
                Type: {alert.type}
              </span>
              <span>
                {new Date(alert.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => setExpandedAlert(expandedAlert === alert.id ? null : alert.id)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="View details"
          >
            {expandedAlert === alert.id ? '📖' : '📄'}
          </button>
          
          <button
            onClick={() => handleAcknowledgeAlert(alert.id)}
            className="text-blue-600 hover:text-blue-800 transition-colors text-sm"
            title="Acknowledge alert"
          >
            ✓
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {expandedAlert === alert.id && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-sm space-y-2">
            <div>
              <strong>Alert ID:</strong> {alert.id}
            </div>
            <div>
              <strong>Timestamp:</strong> {new Date(alert.timestamp).toLocaleString()}
            </div>
            <div>
              <strong>Type:</strong> {alert.type}
            </div>
            <div>
              <strong>Severity:</strong> {alert.severity}
            </div>
            {alert.metadata && (
              <div>
                <strong>Additional Info:</strong>
                <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                  {JSON.stringify(alert.metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const LoadingCard = () => (
    <div className="p-4 rounded-lg border border-gray-200 bg-gray-50">
      <div className="animate-pulse">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-gray-300 rounded"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <span className="mr-2">🚨</span>
          System Alerts
          {alertCounts.all > 0 && (
            <span className="ml-2 bg-red-100 text-red-800 text-sm px-2 py-1 rounded-full">
              {alertCounts.all}
            </span>
          )}
        </h3>

        {!loading && alerts && alerts.length > 0 && (
          <div className="text-sm text-gray-500">
            {filteredAlerts.length} of {alerts.length} alerts
          </div>
        )}
      </div>

      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-2 mb-6">
        {[
          { key: 'all', label: 'All', count: alertCounts.all },
          { key: 'critical', label: 'Critical', count: alertCounts.critical },
          { key: 'high', label: 'High', count: alertCounts.high },
          { key: 'medium', label: 'Medium', count: alertCounts.medium },
          { key: 'low', label: 'Low', count: alertCounts.low }
        ].map(({ key, label, count }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
              filter === key
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            disabled={count === 0 && key !== 'all'}
          >
            <span>{label}</span>
            {count > 0 && (
              <span className={`px-2 py-1 text-xs rounded-full ${
                filter === key ? 'bg-white text-blue-600' : 'bg-gray-200 text-gray-700'
              }`}>
                {count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {loading ? (
          <>
            <LoadingCard />
            <LoadingCard />
            <LoadingCard />
          </>
        ) : filteredAlerts.length > 0 ? (
          filteredAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))
        ) : alerts && alerts.length > 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔍</div>
            <p>No alerts matching current filter</p>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">✅</div>
            <p className="text-lg font-medium">No Active Alerts</p>
            <p className="text-sm">Your system is running smoothly</p>
          </div>
        )}
      </div>

      {/* Alert Summary */}
      {alerts && alerts.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="text-red-600">
              <div className="text-2xl font-bold">{alertCounts.critical + alertCounts.high}</div>
              <div className="text-xs text-gray-600">High Priority</div>
            </div>
            <div className="text-yellow-600">
              <div className="text-2xl font-bold">{alertCounts.medium}</div>
              <div className="text-xs text-gray-600">Medium Priority</div>
            </div>
            <div className="text-blue-600">
              <div className="text-2xl font-bold">{alertCounts.low}</div>
              <div className="text-xs text-gray-600">Low Priority</div>
            </div>
            <div className="text-gray-600">
              <div className="text-2xl font-bold">{alertCounts.all}</div>
              <div className="text-xs text-gray-600">Total Active</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertPanel;
