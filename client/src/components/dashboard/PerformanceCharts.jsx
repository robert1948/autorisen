import React, { useState, useEffect } from 'react';

const PerformanceCharts = ({ timeWindow, loading }) => {
  const [chartsData, setChartsData] = useState(null);
  const [chartsLoading, setChartsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChart, setSelectedChart] = useState('system_resources');

  useEffect(() => {
    const fetchChartsData = async () => {
      try {
        setChartsLoading(true);
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch(`/api/dashboard/charts?hours=${timeWindow}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          setChartsData(data);
          setError(null);
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (err) {
        console.error('Error fetching charts data:', err);
        setError('Failed to load charts data');
      } finally {
        setChartsLoading(false);
      }
    };

    fetchChartsData();
  }, [timeWindow]);

  // Simple chart component (would use a library like Chart.js or Recharts in production)
  const SimpleLineChart = ({ data, label, color = 'blue', unit = '' }) => {
    if (!data || data.length === 0) {
      return (
        <div className="h-32 flex items-center justify-center text-gray-500">
          No data available
        </div>
      );
    }

    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    return (
      <div className="relative">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>{label}</span>
          <span>{max.toFixed(1)}{unit}</span>
        </div>
        
        <div className="h-32 relative border border-gray-200 rounded bg-gray-50">
          <svg className="w-full h-full">
            <polyline
              fill="none"
              stroke={color === 'blue' ? '#3B82F6' : color === 'green' ? '#10B981' : '#EF4444'}
              strokeWidth="2"
              points={data.map((value, index) => {
                const x = (index / (data.length - 1)) * 100;
                const y = 100 - ((value - min) / range) * 100;
                return `${x}%,${y}%`;
              }).join(' ')}
            />
          </svg>
        </div>
        
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{min.toFixed(1)}{unit}</span>
          <span className="text-center">Current: {data[data.length - 1]?.toFixed(1)}{unit}</span>
        </div>
      </div>
    );
  };

  const chartOptions = [
    { id: 'system_resources', label: 'System Resources', icon: '🖥️' },
    { id: 'request_volume', label: 'Request Volume', icon: '🚀' },
    { id: 'error_rate', label: 'Error Rate', icon: '⚠️' },
    { id: 'response_times', label: 'Response Times', icon: '⚡' }
  ];

  const renderSelectedChart = () => {
    if (chartsLoading || !chartsData) {
      return (
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    switch (selectedChart) {
      case 'system_resources':
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <SimpleLineChart
              data={chartsData.system_resources?.cpu || []}
              label="CPU Usage"
              color="blue"
              unit="%"
            />
            <SimpleLineChart
              data={chartsData.system_resources?.memory || []}
              label="Memory Usage"
              color="green"
              unit="%"
            />
          </div>
        );
      
      case 'request_volume':
        return (
          <SimpleLineChart
            data={chartsData.request_volume || []}
            label="Requests per Hour"
            color="blue"
            unit=" req"
          />
        );
      
      case 'error_rate':
        return (
          <SimpleLineChart
            data={chartsData.error_rate || []}
            label="Error Rate"
            color="red"
            unit="%"
          />
        );
      
      case 'response_times':
        return (
          <SimpleLineChart
            data={chartsData.response_times || []}
            label="Average Response Time"
            color="green"
            unit="ms"
          />
        );
      
      default:
        return <div>Unknown chart type</div>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Performance Charts
        </h3>
        
        {chartsData && (
          <div className="text-sm text-gray-500">
            Time range: {timeWindow} hours
          </div>
        )}
      </div>

      {/* Chart Type Selector */}
      <div className="flex flex-wrap gap-2 mb-6">
        {chartOptions.map((option) => (
          <button
            key={option.id}
            onClick={() => setSelectedChart(option.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
              selectedChart === option.id
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

      {/* Chart Content */}
      <div className="min-h-64">
        {renderSelectedChart()}
      </div>

      {/* Time Buckets Info */}
      {chartsData && chartsData.time_buckets && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex justify-between items-center text-xs text-gray-500">
            <span>
              Data points: {chartsData.time_buckets.length}
            </span>
            <span>
              From: {new Date(chartsData.time_buckets[0]).toLocaleString()} 
              {' '} to {' '}
              {new Date(chartsData.time_buckets[chartsData.time_buckets.length - 1]).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* Chart Legend */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-600">
          <p className="mb-2"><strong>Chart Information:</strong></p>
          <ul className="space-y-1">
            <li>• <strong>System Resources:</strong> Real-time CPU and memory usage</li>
            <li>• <strong>Request Volume:</strong> Number of API requests over time</li>
            <li>• <strong>Error Rate:</strong> Percentage of failed requests</li>
            <li>• <strong>Response Times:</strong> Average API response latency</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PerformanceCharts;
