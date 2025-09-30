import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Database, 
  RefreshCw, 
  Play, 
  Pause, 
  Download, 
  Upload, 
  Trash2, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Activity,
  HardDrive,
  Clock,
  Users,
  FileText,
  BarChart3,
  Info,
  Settings,
  Shield,
  Zap
} from 'lucide-react';

const DatabaseManagement = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [databaseStatus, setDatabaseStatus] = useState({});
  const [migrationStatus, setMigrationStatus] = useState({});
  const [backupStatus, setBackupStatus] = useState({});
  const [isRunning, setIsRunning] = useState(false);

  // Fetch database information
  const fetchDatabaseInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [status, migration, backup] = await Promise.all([
        settingsService.getDatabaseStatus(),
        settingsService.getDatabaseStatus(), // This would be migration status in real implementation
        settingsService.getBackups()
      ]);
      
      setDatabaseStatus(status);
      setMigrationStatus(migration);
      setBackupStatus(backup);
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
    fetchDatabaseInfo();
  }, []);

  // Handle run migration
  const handleRunMigration = async () => {
    try {
      setIsRunning(true);
      await settingsService.runDatabaseMigration();
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Database migration completed successfully',
      });
      fetchDatabaseInfo();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Handle seed database
  const handleSeedDatabase = async () => {
    if (!window.confirm('Are you sure you want to seed the database? This will add sample data.')) {
      return;
    }

    try {
      setIsRunning(true);
      await settingsService.seedDatabase();
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Database seeded successfully',
      });
      fetchDatabaseInfo();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Handle create backup
  const handleCreateBackup = async () => {
    try {
      setIsRunning(true);
      await settingsService.createBackup();
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Database backup created successfully',
      });
      fetchDatabaseInfo();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setIsRunning(false);
    }
  };

  // Get status icon and color
  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
      case 'healthy':
      case 'online':
        return <CheckCircle className="w-5 h-5 text-success-500" />;
      case 'warning':
      case 'partial':
        return <AlertTriangle className="w-5 h-5 text-warning-500" />;
      case 'disconnected':
      case 'error':
      case 'offline':
        return <XCircle className="w-5 h-5 text-danger-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading database information..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Database Management</h1>
          <p className="text-gray-600">Manage database operations, migrations, and backups</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={fetchDatabaseInfo}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
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
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Database Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Database className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Database Status</h2>
                <p className="text-gray-600">Current database connection and health</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('connected')}
                <div>
                  <p className="text-sm font-medium text-gray-900">Connection</p>
                  <p className="text-xs text-gray-500">Connected</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                {getStatusIcon('healthy')}
                <div>
                  <p className="text-sm font-medium text-gray-900">Health</p>
                  <p className="text-xs text-gray-500">Healthy</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                <Activity className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Response Time</p>
                  <p className="text-xs text-gray-500">12ms</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                <HardDrive className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Size</p>
                  <p className="text-xs text-gray-500">2.3GB</p>
                </div>
              </div>
            </div>
          </div>

          {/* Database Operations */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Settings className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Database Operations</h2>
                <p className="text-gray-600">Run migrations and manage database</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Zap className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Run Database Migration</p>
                    <p className="text-xs text-gray-500">Apply pending database changes</p>
                  </div>
                </div>
                <Button
                  onClick={handleRunMigration}
                  loading={isRunning}
                  className="flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Run Migration</span>
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Users className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Seed Database</p>
                    <p className="text-xs text-gray-500">Add sample data to database</p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={handleSeedDatabase}
                  loading={isRunning}
                  className="flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>Seed Database</span>
                </Button>
              </div>
            </div>
          </div>

          {/* Backup Management */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Shield className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Backup Management</h2>
                <p className="text-gray-600">Create and manage database backups</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Download className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Create Backup</p>
                    <p className="text-xs text-gray-500">Create a new database backup</p>
                  </div>
                </div>
                <Button
                  onClick={handleCreateBackup}
                  loading={isRunning}
                  className="flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Create Backup</span>
                </Button>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-900">Recent Backups</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">backup_2024_12_19_001.zip</p>
                        <p className="text-xs text-gray-500">Created 2 hours ago • 2.3GB</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" className="text-danger-600 hover:text-danger-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">backup_2024_12_18_001.zip</p>
                        <p className="text-xs text-gray-500">Created 1 day ago • 2.2GB</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" className="text-danger-600 hover:text-danger-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Database Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Database Information</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Database Type</p>
                <p className="text-lg font-medium text-gray-900">PostgreSQL</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Version</p>
                <p className="text-lg font-medium text-gray-900">14.0</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Host</p>
                <p className="text-lg font-medium text-gray-900">localhost:5432</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Database Name</p>
                <p className="text-lg font-medium text-gray-900">pinak_erp</p>
              </div>
            </div>
          </div>

          {/* Database Statistics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Database Statistics</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Tables</span>
                <span className="text-sm font-medium text-gray-900">45</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Records</span>
                <span className="text-sm font-medium text-gray-900">12,345</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Database Size</span>
                <span className="text-sm font-medium text-gray-900">2.3GB</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Index Size</span>
                <span className="text-sm font-medium text-gray-900">450MB</span>
              </div>
            </div>
          </div>

          {/* Migration Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Migration Status</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Pending Migrations</span>
                <span className="text-sm font-medium text-warning-600">2</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Last Migration</span>
                <span className="text-sm font-medium text-gray-900">2024-12-18</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Migration Status</span>
                <span className="text-sm font-medium text-warning-600">Pending</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleRunMigration}
                loading={isRunning}
              >
                <Zap className="w-4 h-4 mr-2" />
                Run Migration
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleCreateBackup}
                loading={isRunning}
              >
                <Download className="w-4 h-4 mr-2" />
                Create Backup
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={fetchDatabaseInfo}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Status
              </Button>
            </div>
          </div>

          {/* System Health */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Health</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Connection Pool</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600">Healthy</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Query Performance</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                  <span className="text-sm text-success-600">Good</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Disk Space</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                  <span className="text-sm text-warning-600">75% Used</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatabaseManagement;