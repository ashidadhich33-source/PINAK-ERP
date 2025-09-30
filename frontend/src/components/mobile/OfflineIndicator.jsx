import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import offlineSyncService from '../../services/offlineSyncService';
import Button from '../common/Button';
import { 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  Download, 
  Upload, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  Trash2,
  Settings
} from 'lucide-react';

const OfflineIndicator = () => {
  const { addNotification } = useApp();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [syncStatus, setSyncStatus] = useState('idle');
  const [pendingItems, setPendingItems] = useState(0);
  const [storageInfo, setStorageInfo] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    // Listen for online/offline events
    const handleOnline = () => {
      setIsOnline(true);
      addNotification({
        type: 'success',
        title: 'Connection Restored',
        message: 'You are now online. Syncing data...',
      });
    };

    const handleOffline = () => {
      setIsOnline(false);
      addNotification({
        type: 'warning',
        title: 'Connection Lost',
        message: 'You are now offline. Changes will be synced when connection is restored.',
      });
    };

    // Listen for sync events
    const handleSyncStart = () => {
      setSyncStatus('syncing');
    };

    const handleSyncComplete = (results) => {
      setSyncStatus('success');
      setLastSync(new Date());
      setPendingItems(0);
      
      const successCount = results.filter(r => r.status === 'success').length;
      const errorCount = results.filter(r => r.status === 'error').length;
      
      if (successCount > 0) {
        addNotification({
          type: 'success',
          title: 'Sync Complete',
          message: `${successCount} items synced successfully`,
        });
      }
      
      if (errorCount > 0) {
        addNotification({
          type: 'warning',
          title: 'Sync Issues',
          message: `${errorCount} items failed to sync`,
        });
      }
    };

    const handleSyncError = (error) => {
      setSyncStatus('error');
      addNotification({
        type: 'danger',
        title: 'Sync Failed',
        message: error.message || 'Failed to sync data',
      });
    };

    // Register event listeners
    offlineSyncService.on('online', handleOnline);
    offlineSyncService.on('offline', handleOffline);
    offlineSyncService.on('syncStart', handleSyncStart);
    offlineSyncService.on('syncComplete', handleSyncComplete);
    offlineSyncService.on('syncError', handleSyncError);

    // Load initial data
    loadSyncData();

    return () => {
      offlineSyncService.off('online', handleOnline);
      offlineSyncService.off('offline', handleOffline);
      offlineSyncService.off('syncStart', handleSyncStart);
      offlineSyncService.off('syncComplete', handleSyncComplete);
      offlineSyncService.off('syncError', handleSyncError);
    };
  }, []);

  const loadSyncData = async () => {
    try {
      const syncQueue = await offlineSyncService.getSyncQueue();
      setPendingItems(syncQueue.length);
      
      const storageInfo = await offlineSyncService.getStorageSize();
      setStorageInfo(storageInfo);
    } catch (error) {
      console.error('Failed to load sync data:', error);
    }
  };

  const handleManualSync = async () => {
    if (!isOnline) {
      addNotification({
        type: 'warning',
        title: 'Offline',
        message: 'Cannot sync while offline',
      });
      return;
    }

    try {
      setSyncStatus('syncing');
      await offlineSyncService.syncAll();
    } catch (error) {
      addNotification({
        type: 'danger',
        title: 'Sync Failed',
        message: error.message,
      });
    }
  };

  const handleClearCache = async () => {
    try {
      await offlineSyncService.clearCache();
      addNotification({
        type: 'success',
        title: 'Cache Cleared',
        message: 'Offline cache has been cleared',
      });
      loadSyncData();
    } catch (error) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: 'Failed to clear cache',
      });
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = () => {
    if (!isOnline) return 'text-danger-600 bg-danger-100';
    if (syncStatus === 'syncing') return 'text-warning-600 bg-warning-100';
    if (syncStatus === 'error') return 'text-danger-600 bg-danger-100';
    if (pendingItems > 0) return 'text-warning-600 bg-warning-100';
    return 'text-success-600 bg-success-100';
  };

  const getStatusIcon = () => {
    if (!isOnline) return WifiOff;
    if (syncStatus === 'syncing') return RefreshCw;
    if (syncStatus === 'error') return AlertTriangle;
    if (pendingItems > 0) return Clock;
    return CheckCircle;
  };

  const StatusIcon = getStatusIcon();

  return (
    <>
      {/* Offline Indicator */}
      {!isOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-danger-500 text-white px-4 py-2 text-center text-sm">
          <div className="flex items-center justify-center space-x-2">
            <WifiOff className="w-4 h-4" />
            <span>You're offline. Changes will be synced when connection is restored.</span>
          </div>
        </div>
      )}

      {/* Sync Status Indicator */}
      <div className="fixed bottom-20 left-4 z-40">
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-3">
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${getStatusColor()}`}>
              <StatusIcon className={`w-4 h-4 ${syncStatus === 'syncing' ? 'animate-spin' : ''}`} />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-900">
                  {isOnline ? 'Online' : 'Offline'}
                </span>
                {pendingItems > 0 && (
                  <span className="text-xs text-warning-600">
                    {pendingItems} pending
                  </span>
                )}
              </div>
              
              <div className="text-xs text-gray-500">
                {syncStatus === 'syncing' ? 'Syncing...' :
                 syncStatus === 'success' ? 'Synced' :
                 syncStatus === 'error' ? 'Sync failed' :
                 'Ready'}
              </div>
            </div>
            
            <div className="flex items-center space-x-1">
              <button
                onClick={handleManualSync}
                disabled={!isOnline || syncStatus === 'syncing'}
                className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${syncStatus === 'syncing' ? 'animate-spin' : ''}`} />
              </button>
              
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Sync Details Panel */}
      {showDetails && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Sync Status</h3>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Connection Status */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    {isOnline ? (
                      <Wifi className="w-4 h-4 text-success-500" />
                    ) : (
                      <WifiOff className="w-4 h-4 text-danger-500" />
                    )}
                    <span className="text-sm font-medium">Connection</span>
                  </div>
                  <span className={`text-sm ${
                    isOnline ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {isOnline ? 'Online' : 'Offline'}
                  </span>
                </div>

                {/* Sync Status */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Database className="w-4 h-4 text-primary-500" />
                    <span className="text-sm font-medium">Sync Status</span>
                  </div>
                  <span className={`text-sm ${
                    syncStatus === 'success' ? 'text-success-600' :
                    syncStatus === 'error' ? 'text-danger-600' :
                    syncStatus === 'syncing' ? 'text-warning-600' :
                    'text-gray-600'
                  }`}>
                    {syncStatus === 'syncing' ? 'Syncing...' :
                     syncStatus === 'success' ? 'Synced' :
                     syncStatus === 'error' ? 'Failed' :
                     'Ready'}
                  </span>
                </div>

                {/* Pending Items */}
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-warning-500" />
                    <span className="text-sm font-medium">Pending Items</span>
                  </div>
                  <span className="text-sm text-gray-600">{pendingItems}</span>
                </div>

                {/* Last Sync */}
                {lastSync && (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-success-500" />
                      <span className="text-sm font-medium">Last Sync</span>
                    </div>
                    <span className="text-sm text-gray-600">
                      {lastSync.toLocaleTimeString()}
                    </span>
                  </div>
                )}

                {/* Storage Info */}
                {storageInfo && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Database className="w-4 h-4 text-primary-500" />
                      <span className="text-sm font-medium">Storage</span>
                    </div>
                    <div className="text-sm text-gray-600">
                      <div>Used: {formatBytes(storageInfo.used)}</div>
                      <div>Available: {formatBytes(storageInfo.available)}</div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div 
                          className="bg-primary-600 h-2 rounded-full" 
                          style={{ width: `${storageInfo.percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex items-center space-x-2 pt-4">
                  <Button
                    size="sm"
                    onClick={handleManualSync}
                    disabled={!isOnline || syncStatus === 'syncing'}
                    className="flex items-center space-x-1"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Sync Now</span>
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleClearCache}
                    className="flex items-center space-x-1 text-danger-600 hover:text-danger-900"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Clear Cache</span>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default OfflineIndicator;