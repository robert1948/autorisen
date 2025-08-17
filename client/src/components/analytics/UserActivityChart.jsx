import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { RefreshCw, Users, Clock, MousePointer } from 'lucide-react';

const UserActivityChart = () => {
  const [activityData, setActivityData] = useState([]);
  const [sessionData, setSessionData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchUserActivity();
    const interval = setInterval(fetchUserActivity, 120000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchUserActivity = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await fetch(`/api/analytics/users/activity?timerange=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch user activity: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform activity data for charts
      const hourlyActivity = {};
      const sessionsByDevice = {};
      
      data.forEach(activity => {
        const hour = new Date(activity.timestamp).getHours();
        const hourKey = `${hour}:00`;
        
        if (!hourlyActivity[hourKey]) {
          hourlyActivity[hourKey] = {
            hour: hourKey,
            sessions: 0,
            users: new Set()
          };
        }
        
        hourlyActivity[hourKey].sessions += 1;
        hourlyActivity[hourKey].users.add(activity.user_id);
        
        // Device type analysis (if available)
        const deviceType = activity.session_data?.device_type || 'Unknown';
        sessionsByDevice[deviceType] = (sessionsByDevice[deviceType] || 0) + 1;
      });

      // Convert to array format for charts
      const activityArray = Object.values(hourlyActivity).map(item => ({
        ...item,
        users: item.users.size
      })).sort((a, b) => parseInt(a.hour) - parseInt(b.hour));

      const deviceArray = Object.entries(sessionsByDevice).map(([device, count]) => ({
        device,
        count,
        percentage: ((count / data.length) * 100).toFixed(1)
      }));

      setActivityData(activityArray);
      setSessionData(deviceArray);
      setError(null);
    } catch (err) {
      console.error('Error fetching user activity:', err);
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

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>User Activity</CardTitle>
          <CardDescription>Error loading user activity data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchUserActivity}
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

  const totalSessions = activityData.reduce((sum, item) => sum + item.sessions, 0);
  const totalUsers = activityData.reduce((sum, item) => sum + item.users, 0);
  const peakHour = activityData.reduce((max, item) => 
    item.sessions > (max?.sessions || 0) ? item : max, null
  );

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalSessions}</div>
            <p className="text-xs text-muted-foreground">
              Last {timeRange}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <MousePointer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUsers}</div>
            <p className="text-xs text-muted-foreground">
              Unique users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Peak Hour</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{peakHour?.hour || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">
              {peakHour?.sessions || 0} sessions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Hourly Activity Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Hourly User Activity</CardTitle>
              <CardDescription>Sessions and unique users by hour</CardDescription>
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
                onClick={fetchUserActivity}
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
          ) : activityData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No activity data available
            </div>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value, name) => [value, name === 'sessions' ? 'Sessions' : 'Users']}
                    labelFormatter={(value) => `Hour: ${value}`}
                  />
                  <Legend />
                  <Bar dataKey="sessions" fill="#8884d8" name="Sessions" />
                  <Bar dataKey="users" fill="#82ca9d" name="Unique Users" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Device/Session Type Distribution */}
      {sessionData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Session Distribution</CardTitle>
              <CardDescription>Sessions by device type</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sessionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ device, percentage }) => `${device}: ${percentage}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {sessionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [value, 'Sessions']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Session Details</CardTitle>
              <CardDescription>Breakdown by category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {sessionData.map((item, index) => (
                  <div key={item.device} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="font-medium">{item.device}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold">{item.count}</div>
                      <div className="text-xs text-gray-500">{item.percentage}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default UserActivityChart;
