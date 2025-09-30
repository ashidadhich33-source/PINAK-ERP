import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import advancedApiService from '../../services/advancedApiService';
import ChartContainer from '../../components/charts/ChartContainer';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Alert from '../../components/common/Alert';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Database,
  Zap,
  Shield,
  RefreshCw,
  Download,
  Settings,
  Eye,
  EyeOff,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';

const APIMonitoringDashboard = () => {
  const { addNotification } = useApp();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    loadMetrics();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [healthCheck, apiMetrics, performanceData] = await Promise.all([
        advancedApiService.healthCheck(),
        advancedApiService.getMetrics(),
        getPerformanceData()
      ]);
      
      setMetrics({
        health: healthCheck,
        api: apiMetrics,
        performance: performanceData
      });
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceData = async () => {
    // Simulate performance data
    return {
      responseTimes: [
        { time: '00:00', value: 120 },
        { time: '01:00', value: 135 },
        { time: '02:00', value: 110 },
        { time: '03:00', value: 125 },
        { time: '04:00', value: 140 },
        { time: '05:00', value: 115 },
        { time: '06:00', value: 130 },
        { time: '07:00', value: 145 },
        { time: '08:00', value: 120 },
        { time: '09:00', value: 135 },
        { time: '10:00', value: 110 },
        { time: '11:00', value: 125 }
      ],
      errorRates: [
        { time: '00:00', value: 0.5 },
        { time: '01:00', value: 0.8 },
        { time: '02:00', value: 0.3 },
        { time: '03:00', value: 0.6 },
        { time: '04:00', value: 0.9 },
        { time: '05:00', value: 0.4 },
        { time: '06:00', value: 0.7 },
        { time: '07:00', value: 1.0 },
        { time: '08:00', value: 0.5 },
        { time: '09:00', value: 0.8 },
        { time: '10:00', value: 0.3 },
        { time: '11:00', value: 0.6 }
      ],
      throughput: [
        { time: '00:00', value: 150 },
        { time: '01:00', value: 120 },
        { time: '02:00', value: 100 },
        { time: '03:00', value: 80 },
        { time: '04:00', value: 60 },
        { time: '05:00', value: 40 },
        { time: '06:00', value: 80 },
        { time: '07:00', value: 200 },
        { time: '08:00', value: 300 },
        { time: '09:00', value: 400 },
        { time: '10:00', value: 350 },
        { time: '11:00', value: 320 }
      ]
    };
  };

  const handleRefresh = async () => {
    await loadMetrics();
    addNotification({
      type: 'success',
      title: 'Refreshed',
      message: 'API metrics updated successfully',
    });
  };

  const handleClearCache = async () => {
    try {
      advancedApiService.clearCache();
      addNotification({
        type: 'success',
        title: 'Cache Cleared',
        message: 'API cache has been cleared',
      });
      await loadMetrics();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleExportMetrics = async () => {
    try {
      const data = {
        timestamp: new Date().toISOString(),
        metrics: metrics
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `api-metrics-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      addNotification({
        type: 'success',
        title: 'Exported',
        message: 'API metrics exported successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading API metrics..." />
      </div>
    );
  }

  // Chart data
  const responseTimeData = {
    labels: metrics?.performance?.responseTimes?.map(item => item.time) || [],
    datasets: [
      {
        label: 'Response Time (ms)',
        data: metrics?.performance?.responseTimes?.map(item => item.value) || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const errorRateData = {
    labels: metrics?.performance?.errorRates?.map(item => item.time) || [],
    datasets: [
      {
        label: 'Error Rate (%)',
        data: metrics?.performance?.errorRates?.map(item => item.value) || [],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const throughputData = {
    labels: metrics?.performance?.throughput?.map(item => item.time) || [],
    datasets: [
      {
        label: 'Throughput (req/min)',
        data: metrics?.performance?.throughput?.map(item => item.value) || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
            <Activity className="w-6 h-6 text-primary-600" />
            <span>API Monitoring Dashboard</span>
          </h1>
          <p className="text-gray-600">Real-time API performance and health monitoring</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </div>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
            className="form-input"
          >
            <option value="10000">10 seconds</option>
            <option value="30000">30 seconds</option>
            <option value="60000">1 minute</option>
            <option value="300000">5 minutes</option>
          </select>
          <Button
            variant="outline"
            onClick={handleRefresh}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={handleExportMetrics}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* API Health Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className={`w-8 h-8 rounded-md flex items-center justify-center ${
                metrics?.health?.status === 'healthy' ? 'bg-success-100' : 'bg-danger-100'
              }`}>
                {metrics?.health?.status === 'healthy' ? (
                  <CheckCircle className="w-5 h-5 text-success-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-danger-600" />
                )}
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">API Health</p>
              <p className="text-2xl font-semibold text-gray-900">
                {metrics?.health?.status === 'healthy' ? 'Healthy' : 'Unhealthy'}
              </p>
              <p className="text-sm text-gray-600">
                Response: {metrics?.health?.responseTime || 0}ms
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <Activity className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Total Requests</p>
              <p className="text-2xl font-semibold text-gray-900">
                {metrics?.api?.requests || 0}
              </p>
              <p className="text-sm text-primary-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{Math.floor(Math.random() * 100)} today
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-md flex items-center justify-center">
                <Database className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Cache Hit Rate</p>
              <p className="text-2xl font-semibold text-gray-900">
                {metrics?.api?.cacheHits || 0}
              </p>
              <p className="text-sm text-warning-600">
                {Math.round((metrics?.api?.cacheHits / metrics?.api?.requests) * 100) || 0}% hit rate
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-secondary-100 rounded-md flex items-center justify-center">
                <Clock className="w-5 h-5 text-secondary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Avg Response Time</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(metrics?.api?.avgResponseTime || 0)}ms
              </p>
              <p className="text-sm text-secondary-600">
                <TrendingDown className="w-4 h-4 inline mr-1" />
                -{Math.floor(Math.random() * 20)}ms
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartContainer
          type="line"
          data={responseTimeData}
          title="Response Time"
          subtitle="API response times over time"
        />

        <ChartContainer
          type="line"
          data={errorRateData}
          title="Error Rate"
          subtitle="API error rates over time"
        />
      </div>

      <ChartContainer
        type="line"
        data={throughputData}
        title="Throughput"
        subtitle="API requests per minute"
        className="lg:col-span-2"
      />

      {/* API Metrics Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">API Metrics Details</h3>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
            >
              {showDetails ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              <span>{showDetails ? 'Hide' : 'Show'} Details</span>
            </button>
          </div>
        </div>
        
        {showDetails && (
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Request Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Total Requests</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.requests || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Cache Hits</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.cacheHits || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Errors</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.errors || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Success Rate</span>
                    <span className="text-sm font-medium text-gray-900">
                      {Math.round(((metrics?.api?.requests - metrics?.api?.errors) / metrics?.api?.requests) * 100) || 0}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Performance Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Avg Response Time</span>
                    <span className="text-sm font-medium text-gray-900">{Math.round(metrics?.api?.avgResponseTime || 0)}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Cache Size</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.cacheSize || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Queue Size</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.queueSize || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Batch Queue Size</span>
                    <span className="text-sm font-medium text-gray-900">{metrics?.api?.batchQueueSize || 0}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Actions</h4>
                <div className="space-y-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleClearCache}
                    className="w-full flex items-center justify-center space-x-2"
                  >
                    <Database className="w-4 h-4" />
                    <span>Clear Cache</span>
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRefresh}
                    className="w-full flex items-center justify-center space-x-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh Metrics</span>
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleExportMetrics}
                    className="w-full flex items-center justify-center space-x-2"
                  >
                    <Download className="w-4 h-4" />
                    <span>Export Data</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default APIMonitoringDashboard;