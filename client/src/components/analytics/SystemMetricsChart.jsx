import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { RefreshCw } from 'lucide-react';

const SystemMetricsChart = () => {
  const [metricsData, setMetricsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('1h'); // 1h, 6h, 24h

  useEffect(() => {
    fetchSystemMetrics();
    const interval = setInterval(fetchSystemMetrics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchSystemMetrics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`/api/analytics/system/performance?timerange=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch system metrics: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform data for chart display
      const transformedData = data.map(metric => ({
        timestamp: new Date(metric.timestamp).toLocaleTimeString(),
        cpu: parseFloat(metric.cpu_usage),
        memory: parseFloat(metric.memory_usage),
        disk: parseFloat(metric.disk_usage),
        load: parseFloat(metric.load_average || 0)
      }));

      setMetricsData(transformedData);
      setError(null);
    } catch (err) {
      console.error('Error fetching system metrics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const timeRangeOptions = [
    { value: '1h', label: '1 Hour' },
    { value: '6h', label: '6 Hours' },
    { value: '24h', label: '24 Hours' }
  ];

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Metrics</CardTitle>
          <CardDescription>Error loading system performance data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchSystemMetrics}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center mx-auto"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Performance Metrics</CardTitle>
              <CardDescription>Real-time system resource utilization</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                {timeRangeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button
                onClick={fetchSystemMetrics}
                className="p-1 text-gray-500 hover:text-gray-700"
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : metricsData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No metrics data available
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    formatter={(value, name) => [`${value.toFixed(1)}%`, name.toUpperCase()]}
                    labelFormatter={(value) => `Time: ${value}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="CPU Usage"
                    dot={{ r: 3 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#82ca9d" 
                    strokeWidth={2}
                    name="Memory Usage"
                    dot={{ r: 3 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="disk" 
                    stroke="#ffc658" 
                    strokeWidth={2}
                    name="Disk Usage"
                    dot={{ r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Load Average Chart */}
      <Card>
        <CardHeader>
          <CardTitle>System Load Average</CardTitle>
          <CardDescription>System load over time</CardDescription>
        </CardHeader>
        <CardContent>
          {metricsData.length > 0 && (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => [value.toFixed(2), 'Load Average']}
                    labelFormatter={(value) => `Time: ${value}`}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="load" 
                    stroke="#ff7c7c" 
                    fill="#ff7c7c"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Current Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metricsData.length > 0 && (
          <>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Current CPU</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {metricsData[metricsData.length - 1]?.cpu.toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Current Memory</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {metricsData[metricsData.length - 1]?.memory.toFixed(1)}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">Current Disk</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {metricsData[metricsData.length - 1]?.disk.toFixed(1)}%
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
};

export default SystemMetricsChart;
