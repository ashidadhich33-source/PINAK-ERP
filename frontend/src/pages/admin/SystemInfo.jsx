import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Monitor, 
  Database, 
  Server, 
  Cpu, 
  HardDrive, 
  Wifi, 
  WifiOff,
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  RefreshCw,
  Download,
  Activity,
  Shield,
  Clock,
  Users,
  FileText,
  BarChart3,
  Info
} from 'lucide-react';

const SystemInfo = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [systemInfo, setSystemInfo] = useState({});
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [healthStatus, setHealthStatus] = useState({});
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Fetch system information
  const fetchSystemInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [systemData, performanceData, healthData] = await Promise.all([
        settingsService.getSystemInfo(),
        settingsService.getSystemInfo(), // This would be a different endpoint in real implementation
        settingsService.getSystemInfo()  // This would be a different endpoint in real implementation
      ]);
      
      setSystemInfo(systemData);
      setPerformanceMetrics(performanceData);
      setHealthStatus(healthData);
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

  useEffect(() => {
    fetchSystemInfo();
  }, []);

  // Auto refresh effect
  useEffect(() => {
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchSystemInfo, 30000); // Refresh every 30 seconds
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Handle export system info
  const handleExportSystemInfo = async () => {
    try {
      await settingsService.exportSettings('json');
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'System information export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get status icon and color
  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
      case 'healthy':
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'warning':
      case 'partial':
        return <AlertTriangle className="w-5 h-5 text-warning-500" />;
      case 'offline':
      case 'error':
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-danger-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading system information..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Information</h1>
          <p className="text-gray-600">Monitor system status, performance, and health</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-2 ${autoRefresh ? 'bg-primary-100 text-primary-700' : ''}`}
          >
            <Activity className="w-4 h-4" />
            <span>{autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}</span>
          </Button>
          <Button
            variant="outline"
            onClick={fetchSystemInfo}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            variant="outline"
            onClick={handleExportSystemInfo}
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* System Status */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overall Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Monitor className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
                <p className="text-gray-600">Current system health and connectivity</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('online')}
                <div>
                  <p className="text-sm font-medium text-gray-900">Database</p>
                  <p className="text-xs text-gray-500">Connected</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('online')}
                <div>
                  <p className="text-sm font-medium text-gray-900">API Server</p>
                  <p className="text-xs text-gray-500">Online</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('warning')}
                <div>
                  <p className="text-sm font-medium text-gray-900">Cache</p>
                  <p className="text-xs text-gray-500">Partial</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('online')}
                <div>
                  <p className="text-sm font-medium text-gray-900">File Storage</p>
                  <p className="text-xs text-gray-500">Available</p>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <BarChart3 className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Performance Metrics</h2>
                <p className="text-gray-600">System performance and resource usage</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mx-auto mb-3">
                  <Cpu className="w-8 h-8 text-primary-600" />
                </div>
                <p className="text-sm text-gray-500">CPU Usage</p>
                <p className="text-2xl font-bold text-gray-900">15%</p>
                <p className="text-xs text-success-600">Normal</p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center w-16 h-16 bg-warning-100 rounded-full mx-auto mb-3">
                  <HardDrive className="w-8 h-8 text-warning-600" />
                </div>
                <p className="text-sm text-gray-500">Memory Usage</p>
                <p className="text-2xl font-bold text-gray-900">2.1GB</p>
                <p className="text-xs text-warning-600">High</p>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center w-16 h-16 bg-success-100 rounded-full mx-auto mb-3">
                  <Activity className="w-8 h-8 text-success-600" />
                </div>
                <p className="text-sm text-gray-500">Response Time</p>
                <p className="text-2xl font-bold text-gray-900">45ms</p>
                <p className="text-xs text-success-600">Fast</p>
              </div>
            </div>
          </div>

          {/* System Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Server className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">System Information</h2>
                <p className="text-gray-600">Version and configuration details</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Frontend Version</p>
                  <p className="text-lg font-medium text-gray-900">1.0.0</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Backend Version</p>
                  <p className="text-lg font-medium text-gray-900">1.0.0</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Database Version</p>
                  <p className="text-lg font-medium text-gray-900">PostgreSQL 14.0</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500">Last Updated</p>
                  <p className="text-lg font-medium text-gray-900">December 19, 2024</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Uptime</p>
                  <p className="text-lg font-medium text-gray-900">15 days, 3 hours</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Environment</p>
                  <p className="text-lg font-medium text-gray-900">Production</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <Users className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Active Users</p>
                  <p className="text-lg font-bold text-gray-900">24</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Total Records</p>
                  <p className="text-lg font-bold text-gray-900">1,234</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Database className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Database Size</p>
                  <p className="text-lg font-bold text-gray-900">2.3GB</p>
                </div>
              </div>
            </div>
          </div>

          {/* System Health */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600">Healthy</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Server</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600">Healthy</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Cache</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                  <span className="text-sm text-warning-600">Warning</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Storage</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600">Healthy</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-success-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">System backup completed</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">New user registered</p>
                  <p className="text-xs text-gray-500">5 minutes ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-warning-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">High memory usage detected</p>
                  <p className="text-xs text-gray-500">10 minutes ago</p>
                </div>
              </div>
            </div>
          </div>

          {/* Security Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Security Status</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">SSL Certificate</span>
                <span className="text-sm text-success-600">Valid</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Firewall</span>
                <span className="text-sm text-success-600">Active</span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Updates</span>
                <span className="text-sm text-warning-600">Pending</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemInfo;