import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Settings, 
  Building2, 
  FileText, 
  ToggleLeft, 
  ToggleRight,
  Monitor,
  Database,
  Shield,
  Bell,
  Globe,
  Palette,
  Save,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Edit,
  Plus,
  Search,
  Filter,
  ChevronRight,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const SettingsDashboard = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({});
  const [systemInfo, setSystemInfo] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  // Settings categories
  const settingsCategories = [
    {
      id: 'general',
      name: 'General Settings',
      icon: Settings,
      description: 'Basic system configuration'
    },
    {
      id: 'company',
      name: 'Company Settings',
      icon: Building2,
      description: 'Company profile and branding'
    },
    {
      id: 'templates',
      name: 'Print Templates',
      icon: FileText,
      description: 'Invoice and receipt templates'
    },
    {
      id: 'features',
      name: 'Feature Toggles',
      icon: ToggleLeft,
      description: 'Enable/disable system features'
    },
    {
      id: 'system',
      name: 'System Information',
      icon: Monitor,
      description: 'System status and health'
    },
    {
      id: 'database',
      name: 'Database',
      icon: Database,
      description: 'Database management'
    },
    {
      id: 'backup',
      name: 'Backup & Recovery',
      icon: Shield,
      description: 'Data backup and restore'
    },
    {
      id: 'automation',
      name: 'Automation',
      icon: Bell,
      description: 'Automated workflows'
    }
  ];

  // Fetch settings and system info
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [settingsData, systemInfoData] = await Promise.all([
          settingsService.getSettings(),
          settingsService.getSystemInfo()
        ]);
        
        setSettings(settingsData);
        setSystemInfo(systemInfoData);
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

    fetchData();
  }, []);

  // Handle setting change
  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setHasChanges(true);
  };

  // Handle save settings
  const handleSaveSettings = async () => {
    try {
      setLoading(true);
      await settingsService.updateSettings(settings);
      setHasChanges(false);
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
      setLoading(false);
    }
  };

  // Handle reset settings
  const handleResetSettings = async () => {
    if (!window.confirm('Are you sure you want to reset all settings to default?')) {
      return;
    }

    try {
      setLoading(true);
      await settingsService.resetSettings();
      const settingsData = await settingsService.getSettings();
      setSettings(settingsData);
      setHasChanges(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Settings reset to default',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle export settings
  const handleExportSettings = async () => {
    try {
      await settingsService.exportSettings();
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Settings export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle import settings
  const handleImportSettings = async (file) => {
    try {
      setLoading(true);
      await settingsService.importSettings(file);
      const settingsData = await settingsService.getSettings();
      setSettings(settingsData);
      setHasChanges(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Settings imported successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading settings..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-600">Manage system configuration and preferences</p>
        </div>
        <div className="flex items-center space-x-3">
          {hasChanges && (
            <div className="flex items-center space-x-2 text-warning-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">Unsaved changes</span>
            </div>
          )}
          <Button
            variant="outline"
            onClick={handleResetSettings}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reset</span>
          </Button>
          <Button
            variant="outline"
            onClick={handleExportSettings}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
          <Button
            variant="outline"
            onClick={() => document.getElementById('import-settings').click()}
            className="flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </Button>
          <Button
            onClick={handleSaveSettings}
            disabled={!hasChanges}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
          </Button>
        </div>
      </div>

      {/* Hidden file input for import */}
      <input
        id="import-settings"
        type="file"
        accept=".json"
        onChange={(e) => handleImportSettings(e.target.files[0])}
        className="hidden"
      />

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Settings Categories</h3>
            </div>
            <nav className="p-4 space-y-2">
              {settingsCategories.map((category) => {
                const Icon = category.icon;
                return (
                  <button
                    key={category.id}
                    onClick={() => setActiveTab(category.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === category.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <div className="flex-1 text-left">
                      <div className="font-medium">{category.name}</div>
                      <div className="text-xs text-gray-500">{category.description}</div>
                    </div>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Settings className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">General Settings</h2>
                    <p className="text-gray-600">Basic system configuration and preferences</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Application Settings */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Application Settings</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Application Name
                        </label>
                        <input
                          type="text"
                          value={settings.app_name || ''}
                          onChange={(e) => handleSettingChange('app_name', e.target.value)}
                          className="form-input"
                          placeholder="PINAK-ERP"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Default Language
                        </label>
                        <select
                          value={settings.default_language || 'en'}
                          onChange={(e) => handleSettingChange('default_language', e.target.value)}
                          className="form-input"
                        >
                          <option value="en">English</option>
                          <option value="hi">Hindi</option>
                          <option value="ta">Tamil</option>
                          <option value="te">Telugu</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Default Currency
                        </label>
                        <select
                          value={settings.default_currency || 'INR'}
                          onChange={(e) => handleSettingChange('default_currency', e.target.value)}
                          className="form-input"
                        >
                          <option value="INR">Indian Rupee (₹)</option>
                          <option value="USD">US Dollar ($)</option>
                          <option value="EUR">Euro (€)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Time Zone
                        </label>
                        <select
                          value={settings.timezone || 'Asia/Kolkata'}
                          onChange={(e) => handleSettingChange('timezone', e.target.value)}
                          className="form-input"
                        >
                          <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                          <option value="UTC">UTC</option>
                          <option value="America/New_York">America/New_York (EST)</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Security Settings */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Enable Two-Factor Authentication</h4>
                          <p className="text-sm text-gray-500">Require 2FA for all users</p>
                        </div>
                        <button
                          onClick={() => handleSettingChange('enable_2fa', !settings.enable_2fa)}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            settings.enable_2fa ? 'bg-primary-600' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              settings.enable_2fa ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">Session Timeout</h4>
                          <p className="text-sm text-gray-500">Auto-logout after inactivity</p>
                        </div>
                        <select
                          value={settings.session_timeout || '30'}
                          onChange={(e) => handleSettingChange('session_timeout', e.target.value)}
                          className="form-input w-32"
                        >
                          <option value="15">15 minutes</option>
                          <option value="30">30 minutes</option>
                          <option value="60">1 hour</option>
                          <option value="120">2 hours</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Company Settings */}
            {activeTab === 'company' && (
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Building2 className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Company Settings</h2>
                    <p className="text-gray-600">Company profile and branding configuration</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Company Information */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Company Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Company Name
                        </label>
                        <input
                          type="text"
                          value={settings.company_name || ''}
                          onChange={(e) => handleSettingChange('company_name', e.target.value)}
                          className="form-input"
                          placeholder="Your Company Name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Legal Name
                        </label>
                        <input
                          type="text"
                          value={settings.legal_name || ''}
                          onChange={(e) => handleSettingChange('legal_name', e.target.value)}
                          className="form-input"
                          placeholder="Legal Company Name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email
                        </label>
                        <input
                          type="email"
                          value={settings.company_email || ''}
                          onChange={(e) => handleSettingChange('company_email', e.target.value)}
                          className="form-input"
                          placeholder="company@example.com"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Phone
                        </label>
                        <input
                          type="tel"
                          value={settings.company_phone || ''}
                          onChange={(e) => handleSettingChange('company_phone', e.target.value)}
                          className="form-input"
                          placeholder="+91 1234567890"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Branding */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Branding</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Company Logo
                        </label>
                        <div className="flex items-center space-x-4">
                          <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
                            {settings.company_logo ? (
                              <img
                                src={settings.company_logo}
                                alt="Company Logo"
                                className="w-full h-full object-contain rounded-lg"
                              />
                            ) : (
                              <Building2 className="w-8 h-8 text-gray-400" />
                            )}
                          </div>
                          <div>
                            <Button
                              variant="outline"
                              onClick={() => document.getElementById('logo-upload').click()}
                            >
                              <Upload className="w-4 h-4 mr-2" />
                              Upload Logo
                            </Button>
                            <input
                              id="logo-upload"
                              type="file"
                              accept="image/*"
                              className="hidden"
                              onChange={(e) => handleSettingChange('company_logo', e.target.files[0])}
                            />
                          </div>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Theme Color
                        </label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="color"
                            value={settings.theme_color || '#3b82f6'}
                            onChange={(e) => handleSettingChange('theme_color', e.target.value)}
                            className="w-12 h-8 rounded border border-gray-300"
                          />
                          <input
                            type="text"
                            value={settings.theme_color || '#3b82f6'}
                            onChange={(e) => handleSettingChange('theme_color', e.target.value)}
                            className="form-input w-32"
                            placeholder="#3b82f6"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* System Information */}
            {activeTab === 'system' && (
              <div className="p-6">
                <div className="flex items-center space-x-3 mb-6">
                  <Monitor className="w-6 h-6 text-primary-600" />
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">System Information</h2>
                    <p className="text-gray-600">System status, version, and health monitoring</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* System Status */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">Database</p>
                          <p className="text-xs text-gray-500">Connected</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">API</p>
                          <p className="text-xs text-gray-500">Online</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">Cache</p>
                          <p className="text-xs text-gray-500">Partial</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Version Information */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Version Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                      <div>
                        <p className="text-sm text-gray-500">Last Updated</p>
                        <p className="text-lg font-medium text-gray-900">December 19, 2024</p>
                      </div>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Response Time</p>
                        <p className="text-lg font-medium text-gray-900">45ms</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Memory Usage</p>
                        <p className="text-lg font-medium text-gray-900">2.1GB</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">CPU Usage</p>
                        <p className="text-lg font-medium text-gray-900">15%</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsDashboard;