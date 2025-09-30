import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Save,
  RefreshCw,
  Settings,
  Database,
  Shield,
  Mail,
  MessageSquare,
  Globe,
  CreditCard,
  Bell,
  Monitor,
  HardDrive,
  Key,
  Lock,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const SystemSettings = () => {
  const { addNotification } = useApp();
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('general');

  // Fetch settings
  const fetchSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await settingsService.getSystemSettings();
      setSettings(data);
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
    fetchSettings();
  }, []);

  // Handle setting change
  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  // Handle save settings
  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      await settingsService.updateSystemSettings(settings);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Settings saved successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle test connection
  const handleTestConnection = async (type) => {
    try {
      await settingsService.testConnection(type);
      addNotification({
        type: 'success',
        title: 'Success',
        message: `${type} connection test successful`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: `${type} connection test failed: ${err.message}`,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading system settings..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600">Configure system-wide settings and preferences</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={fetchSettings}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={handleSaveSettings}
            disabled={saving}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Settings Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'general', name: 'General', icon: Settings },
              { id: 'database', name: 'Database', icon: Database },
              { id: 'security', name: 'Security', icon: Shield },
              { id: 'email', name: 'Email', icon: Mail },
              { id: 'whatsapp', name: 'WhatsApp', icon: MessageSquare },
              { id: 'localization', name: 'Localization', icon: Globe },
              { id: 'payments', name: 'Payments', icon: CreditCard },
              { id: 'notifications', name: 'Notifications', icon: Bell },
              { id: 'monitoring', name: 'Monitoring', icon: Monitor },
              { id: 'backup', name: 'Backup', icon: HardDrive },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Application Name
                  </label>
                  <Input
                    value={settings.general?.app_name || ''}
                    onChange={(e) => handleSettingChange('general', 'app_name', e.target.value)}
                    placeholder="Enter application name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Application Version
                  </label>
                  <Input
                    value={settings.general?.app_version || ''}
                    onChange={(e) => handleSettingChange('general', 'app_version', e.target.value)}
                    placeholder="Enter application version"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <Input
                    value={settings.general?.company_name || ''}
                    onChange={(e) => handleSettingChange('general', 'company_name', e.target.value)}
                    placeholder="Enter company name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Timezone
                  </label>
                  <select
                    value={settings.general?.timezone || 'UTC'}
                    onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
                    className="form-input"
                  >
                    <option value="UTC">UTC</option>
                    <option value="Asia/Kolkata">Asia/Kolkata</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="Europe/London">Europe/London</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Currency
                  </label>
                  <select
                    value={settings.general?.currency || 'INR'}
                    onChange={(e) => handleSettingChange('general', 'currency', e.target.value)}
                    className="form-input"
                  >
                    <option value="INR">INR (₹)</option>
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date Format
                  </label>
                  <select
                    value={settings.general?.date_format || 'DD/MM/YYYY'}
                    onChange={(e) => handleSettingChange('general', 'date_format', e.target.value)}
                    className="form-input"
                  >
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Database Settings */}
          {activeTab === 'database' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Type
                  </label>
                  <select
                    value={settings.database?.type || 'sqlite'}
                    onChange={(e) => handleSettingChange('database', 'type', e.target.value)}
                    className="form-input"
                  >
                    <option value="sqlite">SQLite</option>
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mysql">MySQL</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Host
                  </label>
                  <Input
                    value={settings.database?.host || ''}
                    onChange={(e) => handleSettingChange('database', 'host', e.target.value)}
                    placeholder="Enter database host"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Port
                  </label>
                  <Input
                    type="number"
                    value={settings.database?.port || ''}
                    onChange={(e) => handleSettingChange('database', 'port', e.target.value)}
                    placeholder="Enter database port"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Name
                  </label>
                  <Input
                    value={settings.database?.name || ''}
                    onChange={(e) => handleSettingChange('database', 'name', e.target.value)}
                    placeholder="Enter database name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Username
                  </label>
                  <Input
                    value={settings.database?.username || ''}
                    onChange={(e) => handleSettingChange('database', 'username', e.target.value)}
                    placeholder="Enter database username"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Database Password
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={settings.database?.password || ''}
                      onChange={(e) => handleSettingChange('database', 'password', e.target.value)}
                      placeholder="Enter database password"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => handleTestConnection('database')}
                  className="flex items-center space-x-2"
                >
                  <Database className="w-4 h-4" />
                  <span>Test Connection</span>
                </Button>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    JWT Secret Key
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={settings.security?.jwt_secret || ''}
                      onChange={(e) => handleSettingChange('security', 'jwt_secret', e.target.value)}
                      placeholder="Enter JWT secret key"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    JWT Expiry (hours)
                  </label>
                  <Input
                    type="number"
                    value={settings.security?.jwt_expiry || 24}
                    onChange={(e) => handleSettingChange('security', 'jwt_expiry', e.target.value)}
                    placeholder="Enter JWT expiry in hours"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password Min Length
                  </label>
                  <Input
                    type="number"
                    value={settings.security?.password_min_length || 8}
                    onChange={(e) => handleSettingChange('security', 'password_min_length', e.target.value)}
                    placeholder="Enter minimum password length"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Login Attempts
                  </label>
                  <Input
                    type="number"
                    value={settings.security?.max_login_attempts || 5}
                    onChange={(e) => handleSettingChange('security', 'max_login_attempts', e.target.value)}
                    placeholder="Enter max login attempts"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Account Lockout Duration (minutes)
                  </label>
                  <Input
                    type="number"
                    value={settings.security?.lockout_duration || 30}
                    onChange={(e) => handleSettingChange('security', 'lockout_duration', e.target.value)}
                    placeholder="Enter lockout duration"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enable 2FA
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={settings.security?.enable_2fa || false}
                      onChange={(e) => handleSettingChange('security', 'enable_2fa', e.target.checked)}
                      className="form-checkbox"
                    />
                    <span className="text-sm text-gray-700">Enable Two-Factor Authentication</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Email Settings */}
          {activeTab === 'email' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP Host
                  </label>
                  <Input
                    value={settings.email?.smtp_host || ''}
                    onChange={(e) => handleSettingChange('email', 'smtp_host', e.target.value)}
                    placeholder="Enter SMTP host"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP Port
                  </label>
                  <Input
                    type="number"
                    value={settings.email?.smtp_port || 587}
                    onChange={(e) => handleSettingChange('email', 'smtp_port', e.target.value)}
                    placeholder="Enter SMTP port"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP Username
                  </label>
                  <Input
                    value={settings.email?.smtp_username || ''}
                    onChange={(e) => handleSettingChange('email', 'smtp_username', e.target.value)}
                    placeholder="Enter SMTP username"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP Password
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={settings.email?.smtp_password || ''}
                      onChange={(e) => handleSettingChange('email', 'smtp_password', e.target.value)}
                      placeholder="Enter SMTP password"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Email
                  </label>
                  <Input
                    type="email"
                    value={settings.email?.from_email || ''}
                    onChange={(e) => handleSettingChange('email', 'from_email', e.target.value)}
                    placeholder="Enter from email"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Name
                  </label>
                  <Input
                    value={settings.email?.from_name || ''}
                    onChange={(e) => handleSettingChange('email', 'from_name', e.target.value)}
                    placeholder="Enter from name"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => handleTestConnection('email')}
                  className="flex items-center space-x-2"
                >
                  <Mail className="w-4 h-4" />
                  <span>Test Email</span>
                </Button>
              </div>
            </div>
          )}

          {/* WhatsApp Settings */}
          {activeTab === 'whatsapp' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    WhatsApp Business API URL
                  </label>
                  <Input
                    value={settings.whatsapp?.api_url || ''}
                    onChange={(e) => handleSettingChange('whatsapp', 'api_url', e.target.value)}
                    placeholder="Enter WhatsApp API URL"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Token
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={settings.whatsapp?.access_token || ''}
                      onChange={(e) => handleSettingChange('whatsapp', 'access_token', e.target.value)}
                      placeholder="Enter access token"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number ID
                  </label>
                  <Input
                    value={settings.whatsapp?.phone_number_id || ''}
                    onChange={(e) => handleSettingChange('whatsapp', 'phone_number_id', e.target.value)}
                    placeholder="Enter phone number ID"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Webhook Verify Token
                  </label>
                  <div className="relative">
                    <Input
                      type="password"
                      value={settings.whatsapp?.webhook_verify_token || ''}
                      onChange={(e) => handleSettingChange('whatsapp', 'webhook_verify_token', e.target.value)}
                      placeholder="Enter webhook verify token"
                    />
                  </div>
                </div>
              </div>
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  onClick={() => handleTestConnection('whatsapp')}
                  className="flex items-center space-x-2"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Test WhatsApp</span>
                </Button>
              </div>
            </div>
          )}

          {/* Other tabs would follow similar patterns... */}
        </div>
      </div>
    </div>
  );
};

export default SystemSettings;