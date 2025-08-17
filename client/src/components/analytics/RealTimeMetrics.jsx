import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Activity, Cpu, HardDrive, MemoryStick, Wifi, AlertCircle } from 'lucide-react';

const RealTimeMetrics = () => {
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    fetchRealTimeMetrics();
    const interval = setInterval(fetchRealTimeMetrics, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRealTimeMetrics = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch('/api/analytics/metrics/realtime', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch real-time metrics: ${response.statusText}`);
      }

      const data = await response.json();
      setRealTimeData(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching real-time metrics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (value, thresholds) => {
    if (value >= thresholds.critical) return 'bg-red-500';
    if (value >= thresholds.warning) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getStatusBadge = (value, thresholds) => {
    if (value >= thresholds.critical) return <Badge variant="destructive">Critical</Badge>;
    if (value >= thresholds.warning) return <Badge variant="secondary">Warning</Badge>;
    return <Badge variant="default" className="bg-green-600">Good</Badge>;
  };

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Real-time Metrics</CardTitle>
          <CardDescription>Error loading real-time data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchRealTimeMetrics}
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

  const thresholds = {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 },
    disk: { warning: 85, critical: 95 }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Real-time System Metrics</h2>
          <p className="text-gray-600">Live system performance monitoring</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Live</span>
          </div>
          <button
            onClick={fetchRealTimeMetrics}
            className="p-2 text-gray-500 hover:text-gray-700"
            disabled={loading}
          >
            <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading && !realTimeData ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading real-time metrics...</p>
          </div>
        </div>
      ) : realTimeData ? (
        <>
          {/* System Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-2xl font-bold">{realTimeData.system?.cpu_usage?.toFixed(1) || 0}%</div>
                  {getStatusBadge(realTimeData.system?.cpu_usage || 0, thresholds.cpu)}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getStatusColor(realTimeData.system?.cpu_usage || 0, thresholds.cpu)}`}
                    style={{ width: `${realTimeData.system?.cpu_usage || 0}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                <MemoryStick className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-2xl font-bold">{realTimeData.system?.memory_usage?.toFixed(1) || 0}%</div>
                  {getStatusBadge(realTimeData.system?.memory_usage || 0, thresholds.memory)}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getStatusColor(realTimeData.system?.memory_usage || 0, thresholds.memory)}`}
                    style={{ width: `${realTimeData.system?.memory_usage || 0}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-2xl font-bold">{realTimeData.system?.disk_usage?.toFixed(1) || 0}%</div>
                  {getStatusBadge(realTimeData.system?.disk_usage || 0, thresholds.disk)}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${getStatusColor(realTimeData.system?.disk_usage || 0, thresholds.disk)}`}
                    style={{ width: `${realTimeData.system?.disk_usage || 0}%` }}
                  ></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{realTimeData.users?.active_sessions || 0}</div>
                <p className="text-xs text-muted-foreground">
                  {realTimeData.users?.online_users || 0} users online
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Detailed System Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>System Details</CardTitle>
                <CardDescription>Current system status and load</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Load Average:</span>
                    <span className="text-lg">{realTimeData.system?.load_average?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Memory Available:</span>
                    <span className="text-lg">{realTimeData.system?.memory_available_gb?.toFixed(1) || 'N/A'} GB</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Disk Free:</span>
                    <span className="text-lg">{realTimeData.system?.disk_free_gb?.toFixed(1) || 'N/A'} GB</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Network I/O:</span>
                    <span className="text-lg">{realTimeData.system?.network_io_mb?.toFixed(1) || 'N/A'} MB/s</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Application Metrics</CardTitle>
                <CardDescription>Real-time application performance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Requests/min:</span>
                    <span className="text-lg">{realTimeData.api?.requests_per_minute || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Error Rate:</span>
                    <span className="text-lg">{realTimeData.api?.error_rate?.toFixed(2) || 0}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Avg Response:</span>
                    <span className="text-lg">{realTimeData.api?.avg_response_time?.toFixed(0) || 0}ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium">Queue Size:</span>
                    <span className="text-lg">{realTimeData.api?.queue_size || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Events */}
          <Card>
            <CardHeader>
              <CardTitle>Live Event Stream</CardTitle>
              <CardDescription>Real-time system and user events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {realTimeData.recent_events?.length > 0 ? (
                  realTimeData.recent_events.map((event, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded border-l-4 border-blue-500">
                      <div className="flex items-center space-x-3">
                        <Activity className="h-4 w-4 text-blue-500" />
                        <div>
                          <p className="text-sm font-medium">{event.event_type}</p>
                          <p className="text-xs text-gray-500">{event.event_data?.description || 'System event'}</p>
                        </div>
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-sm text-center py-4">No recent events</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Last Update Info */}
          {lastUpdate && (
            <div className="text-center text-sm text-gray-500">
              Last updated: {lastUpdate.toLocaleTimeString()} • Auto-refresh every 5 seconds
            </div>
          )}
        </>
      ) : null}
    </div>
  );
};

export default RealTimeMetrics;
