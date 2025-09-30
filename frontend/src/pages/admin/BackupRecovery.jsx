import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Shield, 
  Download, 
  Upload, 
  Trash2, 
  RefreshCw, 
  Play, 
  Pause, 
  Clock, 
  HardDrive, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  FileText,
  Settings,
  Calendar,
  Activity,
  Info
} from 'lucide-react';

const BackupRecovery = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backups, setBackups] = useState([]);
  const [backupStatus, setBackupStatus] = useState({});
  const [isCreating, setIsCreating] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);

  // Fetch backups and status
  const fetchBackupData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [backupsData, statusData] = await Promise.all([
        settingsService.getBackups(),
        settingsService.getBackups() // This would be backup status in real implementation
      ]);
      
      setBackups(backupsData);
      setBackupStatus(statusData);
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
    fetchBackupData();
  }, []);

  // Handle create backup
  const handleCreateBackup = async () => {
    try {
      setIsCreating(true);
      await settingsService.createBackup();
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Backup created successfully',
      });
      fetchBackupData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setIsCreating(false);
    }
  };

  // Handle download backup
  const handleDownloadBackup = async (backupId) => {
    try {
      await settingsService.downloadBackup(backupId);
      addNotification({
        type: 'success',
        title: 'Download Started',
        message: 'Backup download will begin shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle restore backup
  const handleRestoreBackup = async (backupId) => {
    if (!window.confirm('Are you sure you want to restore this backup? This will overwrite all current data.')) {
      return;
    }

    try {
      setIsRestoring(true);
      await settingsService.restoreBackup(backupId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Backup restored successfully',
      });
      fetchBackupData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setIsRestoring(false);
    }
  };

  // Handle delete backup
  const handleDeleteBackup = async (backupId) => {
    if (!window.confirm('Are you sure you want to delete this backup?')) {
      return;
    }

    try {
      await settingsService.deleteBackup(backupId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Backup deleted successfully',
      });
      fetchBackupData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading backup information..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Backup & Recovery</h1>
          <p className="text-gray-600">Manage database backups and recovery operations</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={fetchBackupData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={handleCreateBackup}
            loading={isCreating}
            className="flex items-center space-x-2"
          >
            <Shield className="w-4 h-4" />
            <span>Create Backup</span>
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
          {/* Backup Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Activity className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Backup Status</h2>
                <p className="text-gray-600">Current backup system status and health</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                <CheckCircle className="w-5 h-5 text-success-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Backup System</p>
                  <p className="text-xs text-gray-500">Active</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                <Clock className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Last Backup</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg">
                <HardDrive className="w-5 h-5 text-primary-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Storage Used</p>
                  <p className="text-xs text-gray-500">2.3GB / 10GB</p>
                </div>
              </div>
            </div>
          </div>

          {/* Backup List */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <FileText className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Available Backups</h2>
                <p className="text-gray-600">List of all available database backups</p>
              </div>
            </div>

            <div className="space-y-4">
              {backups.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No backups available</p>
                  <p className="text-sm text-gray-400">Create your first backup to get started</p>
                </div>
              ) : (
                backups.map((backup) => (
                  <div key={backup.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-primary-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">{backup.filename}</p>
                        <p className="text-xs text-gray-500">
                          Created {formatDate(backup.created_at)} • {formatFileSize(backup.size)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadBackup(backup.id)}
                        className="flex items-center space-x-1"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRestoreBackup(backup.id)}
                        loading={isRestoring}
                        className="flex items-center space-x-1"
                      >
                        <Upload className="w-4 h-4" />
                        <span>Restore</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteBackup(backup.id)}
                        className="flex items-center space-x-1 text-danger-600 hover:text-danger-700"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Delete</span>
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Backup Schedule */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Calendar className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Backup Schedule</h2>
                <p className="text-gray-600">Automated backup configuration</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Settings className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Daily Backup</p>
                    <p className="text-xs text-gray-500">Automated backup at 2:00 AM</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-success-600">Enabled</span>
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Settings className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Weekly Backup</p>
                    <p className="text-xs text-gray-500">Full backup every Sunday</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-success-600">Enabled</span>
                  <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Settings className="w-5 h-5 text-primary-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Monthly Backup</p>
                    <p className="text-xs text-gray-500">Archive backup on 1st of month</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-warning-600">Disabled</span>
                  <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Button
                onClick={handleCreateBackup}
                loading={isCreating}
                className="w-full justify-start"
              >
                <Shield className="w-4 h-4 mr-2" />
                Create Backup
              </Button>
              
              <Button
                variant="outline"
                onClick={fetchBackupData}
                className="w-full justify-start"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh List
              </Button>
            </div>
          </div>

          {/* Backup Statistics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Backup Statistics</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Backups</span>
                <span className="text-sm font-medium text-gray-900">{backups.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Size</span>
                <span className="text-sm font-medium text-gray-900">2.3GB</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Last Backup</span>
                <span className="text-sm font-medium text-gray-900">2 hours ago</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Next Backup</span>
                <span className="text-sm font-medium text-gray-900">22 hours</span>
              </div>
            </div>
          </div>

          {/* Storage Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Storage Information</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Used Space</span>
                  <span className="text-sm font-medium text-gray-900">2.3GB</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full" style={{ width: '23%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Available Space</span>
                  <span className="text-sm font-medium text-gray-900">7.7GB</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-400 h-2 rounded-full" style={{ width: '77%' }}></div>
                </div>
              </div>
              
              <div className="pt-2">
                <p className="text-xs text-gray-500">Total Storage: 10GB</p>
              </div>
            </div>
          </div>

          {/* Recovery Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Info className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Recovery Information</h3>
            </div>
            <div className="space-y-3">
              <div className="p-3 bg-warning-50 border border-warning-200 rounded-lg">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 text-warning-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-warning-800">Important Notice</p>
                    <p className="text-xs text-warning-700 mt-1">
                      Restoring a backup will overwrite all current data. Make sure to create a backup before restoring.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-3 bg-info-50 border border-info-200 rounded-lg">
                <div className="flex items-start space-x-2">
                  <Info className="w-4 h-4 text-info-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-info-800">Recovery Time</p>
                    <p className="text-xs text-info-700 mt-1">
                      Recovery process typically takes 5-10 minutes depending on backup size.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BackupRecovery;