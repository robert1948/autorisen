import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { RefreshCw, Activity, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const APIUsageChart = () => {
  const [apiData, setApiData] = useState([]);
  const [endpointStats, setEndpointStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchAPIUsage();
    const interval = setInterval(fetchAPIUsage, 120000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAPIUsage = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      
      // Fetch API usage data
      const response = await fetch(`/api/analytics/api/usage?timerange=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch API usage: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Process hourly API usage
      const hourlyUsage = {};
      const endpointCounts = {};
      const statusCodes = {};

      data.forEach(usage => {
        const hour = new Date(usage.timestamp).getHours();
        const hourKey = `${hour}:00`;
        
        if (!hourlyUsage[hourKey]) {
          hourlyUsage[hourKey] = {
            hour: hourKey,
            requests: 0,
            errors: 0,
            avgResponseTime: 0,
            responseTimeSum: 0,
            responseTimeCount: 0
          };
        }
        
        hourlyUsage[hourKey].requests += 1;
        
        if (usage.status_code >= 400) {
          hourlyUsage[hourKey].errors += 1;
        }
        
        if (usage.response_time) {
          hourlyUsage[hourKey].responseTimeSum += parseFloat(usage.response_time);
          hourlyUsage[hourKey].responseTimeCount += 1;
        }
        
        // Endpoint statistics
        const endpoint = usage.endpoint || 'Unknown';
        endpointCounts[endpoint] = (endpointCounts[endpoint] || 0) + 1;
        
        // Status code statistics
        const statusCode = usage.status_code || 'Unknown';
        statusCodes[statusCode] = (statusCodes[statusCode] || 0) + 1;
      });

      // Calculate average response times
      Object.values(hourlyUsage).forEach(hour => {
        if (hour.responseTimeCount > 0) {
          hour.avgResponseTime = (hour.responseTimeSum / hour.responseTimeCount).toFixed(2);
        }
      });

      // Convert to arrays for charts
      const apiArray = Object.values(hourlyUsage).sort((a, b) => parseInt(a.hour) - parseInt(b.hour));
      
      const endpointArray = Object.entries(endpointCounts)
        .map(([endpoint, count]) => ({
          endpoint: endpoint.length > 20 ? endpoint.substring(0, 20) + '...' : endpoint,
          fullEndpoint: endpoint,
          count,
          percentage: ((count / data.length) * 100).toFixed(1)
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10); // Top 10 endpoints

      setApiData(apiArray);
      setEndpointStats(endpointArray);
      setError(null);
    } catch (err) {
      console.error('Error fetching API usage:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const timeRangeOptions = [
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' }
  ];

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>API Usage</CardTitle>
          <CardDescription>Error loading API usage data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchAPIUsage}
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

  const totalRequests = apiData.reduce((sum, item) => sum + item.requests, 0);
  const totalErrors = apiData.reduce((sum, item) => sum + item.errors, 0);
  const errorRate = totalRequests > 0 ? ((totalErrors / totalRequests) * 100).toFixed(2) : 0;
  const avgResponseTime = apiData.length > 0 
    ? (apiData.reduce((sum, item) => sum + parseFloat(item.avgResponseTime || 0), 0) / apiData.length).toFixed(2)
    : 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalRequests.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Last {timeRange}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{errorRate}%</div>
            <p className="text-xs text-muted-foreground">
              {totalErrors} errors
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgResponseTime}ms</div>
            <p className="text-xs text-muted-foreground">
              Response time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{(100 - parseFloat(errorRate)).toFixed(2)}%</div>
            <p className="text-xs text-muted-foreground">
              Successful requests
            </p>
          </CardContent>
        </Card>
      </div>

      {/* API Usage Over Time */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>API Requests Over Time</CardTitle>
              <CardDescription>Hourly API usage and error tracking</CardDescription>
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
                onClick={fetchAPIUsage}
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
          ) : apiData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No API usage data available
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={apiData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'avgResponseTime') return [`${value}ms`, 'Avg Response Time'];
                      return [value, name === 'requests' ? 'Requests' : 'Errors'];
                    }}
                    labelFormatter={(value) => `Hour: ${value}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="requests" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    name="Requests"
                    yAxisId="left"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="errors" 
                    stroke="#ff4444" 
                    strokeWidth={2}
                    name="Errors"
                    yAxisId="left"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Response Time Chart */}
      {apiData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Response Time Trends</CardTitle>
            <CardDescription>Average response time by hour</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={apiData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => [`${value}ms`, 'Response Time']}
                    labelFormatter={(value) => `Hour: ${value}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="avgResponseTime" 
                    stroke="#82ca9d" 
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Top Endpoints */}
      {endpointStats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top API Endpoints</CardTitle>
            <CardDescription>Most frequently used endpoints</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={endpointStats} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="endpoint" type="category" width={150} />
                  <Tooltip 
                    formatter={(value) => [value, 'Requests']}
                    labelFormatter={(value) => `Endpoint: ${value}`}
                  />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default APIUsageChart;
