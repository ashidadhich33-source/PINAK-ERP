import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../common/Button';
import Input from '../common/Input';
import Alert from '../common/Alert';
import LoadingSpinner from '../common/LoadingSpinner';
import { 
  Shield, 
  Lock, 
  Eye, 
  EyeOff, 
  Key, 
  UserCheck, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Settings,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Edit,
  Plus
} from 'lucide-react';

const SecurityDashboard = () => {
  const { addNotification } = useApp();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [securitySettings, setSecuritySettings] = useState({
    password_policy: {
      min_length: 8,
      require_uppercase: true,
      require_lowercase: true,
      require_numbers: true,
      require_symbols: true,
      max_age_days: 90,
      prevent_reuse: 5
    },
    session_management: {
      session_timeout: 30,
      max_concurrent_sessions: 5,
      require_reauth_for_sensitive: true
    },
    two_factor_auth: {
      enabled: false,
      required_for_admin: true,
      backup_codes_count: 10
    },
    ip_restrictions: {
      enabled: false,
      allowed_ips: [],
      blocked_ips: []
    },
    audit_logging: {
      enabled: true,
      retention_days: 365,
      log_level: 'info'
    }
  });
  const [auditLogs, setAuditLogs] = useState([]);
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [activeSessions, setActiveSessions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      setLoading(true);
      // Load security settings, audit logs, alerts, and active sessions
      // This would typically make API calls to fetch this data
      setLoading(false);
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleSettingChange = (category, setting, value) => {
    setSecuritySettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const handleSaveSettings = async () => {
    try {
      // Save security settings
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Security settings updated successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleTerminateSession = async (sessionId) => {
    try {
      // Terminate session
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Session terminated successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleExportAuditLogs = async () => {
    try {
      // Export audit logs
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Audit logs exported successfully',
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
        <LoadingSpinner size="lg" text="Loading security data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="text-gray-600">Manage security settings and monitor system security</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={loadSecurityData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={handleSaveSettings}
            className="flex items-center space-x-2"
          >
            <Shield className="w-4 h-4" />
            <span>Save Settings</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Security Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-md flex items-center justify-center">
                <Shield className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Security Score</p>
              <p className="text-2xl font-semibold text-gray-900">85%</p>
              <p className="text-sm text-success-600">Good</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-md flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Active Alerts</p>
              <p className="text-2xl font-semibold text-gray-900">3</p>
              <p className="text-sm text-warning-600">Requires attention</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <UserCheck className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Active Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">12</p>
              <p className="text-sm text-primary-600">Current users</p>
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
              <p className="text-sm font-medium text-gray-500">Last Login</p>
              <p className="text-2xl font-semibold text-gray-900">2h ago</p>
              <p className="text-sm text-secondary-600">From IP: 192.168.1.1</p>
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Password Policy */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Password Policy</h3>
          <div className="space-y-4">
            <div>
              <label className="form-label">Minimum Length</label>
              <Input
                type="number"
                value={securitySettings.password_policy.min_length}
                onChange={(e) => handleSettingChange('password_policy', 'min_length', parseInt(e.target.value))}
                min="6"
                max="32"
              />
            </div>
            
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={securitySettings.password_policy.require_uppercase}
                  onChange={(e) => handleSettingChange('password_policy', 'require_uppercase', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Require uppercase letters</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={securitySettings.password_policy.require_lowercase}
                  onChange={(e) => handleSettingChange('password_policy', 'require_lowercase', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Require lowercase letters</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={securitySettings.password_policy.require_numbers}
                  onChange={(e) => handleSettingChange('password_policy', 'require_numbers', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Require numbers</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={securitySettings.password_policy.require_symbols}
                  onChange={(e) => handleSettingChange('password_policy', 'require_symbols', e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Require symbols</span>
              </label>
            </div>
            
            <div>
              <label className="form-label">Maximum Age (days)</label>
              <Input
                type="number"
                value={securitySettings.password_policy.max_age_days}
                onChange={(e) => handleSettingChange('password_policy', 'max_age_days', parseInt(e.target.value))}
                min="30"
                max="365"
              />
            </div>
          </div>
        </div>

        {/* Session Management */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Session Management</h3>
          <div className="space-y-4">
            <div>
              <label className="form-label">Session Timeout (minutes)</label>
              <Input
                type="number"
                value={securitySettings.session_management.session_timeout}
                onChange={(e) => handleSettingChange('session_management', 'session_timeout', parseInt(e.target.value))}
                min="5"
                max="480"
              />
            </div>
            
            <div>
              <label className="form-label">Max Concurrent Sessions</label>
              <Input
                type="number"
                value={securitySettings.session_management.max_concurrent_sessions}
                onChange={(e) => handleSettingChange('session_management', 'max_concurrent_sessions', parseInt(e.target.value))}
                min="1"
                max="20"
              />
            </div>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={securitySettings.session_management.require_reauth_for_sensitive}
                onChange={(e) => handleSettingChange('session_management', 'require_reauth_for_sensitive', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Require re-authentication for sensitive operations</span>
            </label>
          </div>
        </div>
      </div>

      {/* Two-Factor Authentication */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Two-Factor Authentication</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={securitySettings.two_factor_auth.enabled}
                onChange={(e) => handleSettingChange('two_factor_auth', 'enabled', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Enable 2FA</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={securitySettings.two_factor_auth.required_for_admin}
                onChange={(e) => handleSettingChange('two_factor_auth', 'required_for_admin', e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Required for admin users</span>
            </label>
            
            <div>
              <label className="form-label">Backup Codes Count</label>
              <Input
                type="number"
                value={securitySettings.two_factor_auth.backup_codes_count}
                onChange={(e) => handleSettingChange('two_factor_auth', 'backup_codes_count', parseInt(e.target.value))}
                min="5"
                max="20"
              />
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">2FA Status</h4>
              <div className="flex items-center space-x-2">
                {securitySettings.two_factor_auth.enabled ? (
                  <CheckCircle className="w-5 h-5 text-success-500" />
                ) : (
                  <XCircle className="w-5 h-5 text-danger-500" />
                )}
                <span className="text-sm text-gray-700">
                  {securitySettings.two_factor_auth.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
            </div>
            
            <Button
              variant="outline"
              className="w-full"
              onClick={() => {/* Setup 2FA */}}
            >
              Setup 2FA
            </Button>
          </div>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Active Sessions</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {/* Refresh sessions */}}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
        
        <div className="space-y-3">
          {activeSessions.map((session, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <UserCheck className="w-4 h-4 text-primary-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{session.user_name}</p>
                  <p className="text-xs text-gray-500">{session.ip_address} • {session.location}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">{session.last_activity}</span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleTerminateSession(session.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  Terminate
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Audit Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Audit Logs</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportAuditLogs}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
        </div>
        
        <div className="space-y-3">
          {auditLogs.map((log, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  log.level === 'info' ? 'bg-primary-500' :
                  log.level === 'warning' ? 'bg-warning-500' :
                  log.level === 'error' ? 'bg-danger-500' :
                  'bg-gray-500'
                }`} />
                <div>
                  <p className="text-sm font-medium text-gray-900">{log.action}</p>
                  <p className="text-xs text-gray-500">{log.user_name} • {log.timestamp}</p>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-sm text-gray-500">{log.ip_address}</p>
                <p className="text-xs text-gray-400">{log.user_agent}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;