import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { settingsService } from '../../services/settingsService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Building2, 
  Upload, 
  Save, 
  RefreshCw, 
  Globe, 
  Phone, 
  Mail, 
  MapPin,
  Palette,
  Image,
  Trash2,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react';

const CompanySettings = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [companySettings, setCompanySettings] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  // Form fields
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    legal_name: '',
    email: '',
    phone: '',
    website: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    country: 'India',
    postal_code: '',
    gst_number: '',
    pan_number: '',
    cin_number: '',
    business_type: '',
    financial_year_start: '',
    financial_year_end: '',
    current_financial_year: '',
    currency_code: 'INR',
    currency_symbol: '₹',
    gst_registration_type: '',
    gst_state_code: '',
    theme_color: '#3b82f6',
    description: '',
    notes: ''
  });

  // Fetch company settings
  useEffect(() => {
    const fetchCompanySettings = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const settings = await settingsService.getCompanySettings();
        setCompanySettings(settings);
        setFormData(settings);
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

    fetchCompanySettings();
  }, []);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  };

  // Handle logo upload
  const handleLogoUpload = async (file) => {
    try {
      setSaving(true);
      const result = await settingsService.uploadCompanyLogo(file);
      setFormData(prev => ({
        ...prev,
        logo_path: result.logo_path
      }));
      setHasChanges(true);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Logo uploaded successfully',
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

  // Handle save settings
  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      
      await settingsService.updateCompanySettings(formData);
      setHasChanges(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Company settings saved successfully',
      });
    } catch (err) {
      setError(err.message);
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    } finally {
      setSaving(false);
    }
  };

  // Handle reset settings
  const handleResetSettings = async () => {
    if (!window.confirm('Are you sure you want to reset all company settings to default?')) {
      return;
    }

    try {
      setSaving(true);
      await settingsService.resetSettings('company');
      const settings = await settingsService.getCompanySettings();
      setFormData(settings);
      setHasChanges(false);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Company settings reset to default',
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading company settings..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Company Settings</h1>
          <p className="text-gray-600">Manage your company profile and branding</p>
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
            disabled={saving}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Reset</span>
          </Button>
          <Button
            onClick={handleSaveSettings}
            disabled={!hasChanges || saving}
            loading={saving}
            className="flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Save Changes</span>
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
        {/* Company Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Building2 className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Basic Information</h2>
                <p className="text-gray-600">Company name and contact details</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <Input
                  value={formData.name}
                  onChange={(e) => handleFieldChange('name', e.target.value)}
                  placeholder="Your Company Name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Display Name
                </label>
                <Input
                  value={formData.display_name}
                  onChange={(e) => handleFieldChange('display_name', e.target.value)}
                  placeholder="Display Name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Legal Name
                </label>
                <Input
                  value={formData.legal_name}
                  onChange={(e) => handleFieldChange('legal_name', e.target.value)}
                  placeholder="Legal Company Name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Type
                </label>
                <select
                  value={formData.business_type}
                  onChange={(e) => handleFieldChange('business_type', e.target.value)}
                  className="form-input"
                >
                  <option value="">Select Business Type</option>
                  <option value="sole_proprietorship">Sole Proprietorship</option>
                  <option value="partnership">Partnership</option>
                  <option value="private_limited">Private Limited</option>
                  <option value="public_limited">Public Limited</option>
                  <option value="llp">Limited Liability Partnership</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Phone className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Contact Information</h2>
                <p className="text-gray-600">Phone, email, and website details</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleFieldChange('email', e.target.value)}
                  placeholder="company@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <Input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleFieldChange('phone', e.target.value)}
                  placeholder="+91 1234567890"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Website
                </label>
                <Input
                  type="url"
                  value={formData.website}
                  onChange={(e) => handleFieldChange('website', e.target.value)}
                  placeholder="https://www.example.com"
                />
              </div>
            </div>
          </div>

          {/* Address Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <MapPin className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Address Information</h2>
                <p className="text-gray-600">Company address and location details</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address Line 1
                </label>
                <Input
                  value={formData.address_line1}
                  onChange={(e) => handleFieldChange('address_line1', e.target.value)}
                  placeholder="Street address"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address Line 2
                </label>
                <Input
                  value={formData.address_line2}
                  onChange={(e) => handleFieldChange('address_line2', e.target.value)}
                  placeholder="Apartment, suite, unit, etc."
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City
                  </label>
                  <Input
                    value={formData.city}
                    onChange={(e) => handleFieldChange('city', e.target.value)}
                    placeholder="City"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State
                  </label>
                  <Input
                    value={formData.state}
                    onChange={(e) => handleFieldChange('state', e.target.value)}
                    placeholder="State"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Postal Code
                  </label>
                  <Input
                    value={formData.postal_code}
                    onChange={(e) => handleFieldChange('postal_code', e.target.value)}
                    placeholder="PIN Code"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Tax Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Globe className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Tax Information</h2>
                <p className="text-gray-600">GST, PAN, and other tax details</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GST Number
                </label>
                <Input
                  value={formData.gst_number}
                  onChange={(e) => handleFieldChange('gst_number', e.target.value)}
                  placeholder="22AAAAA0000A1Z5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  PAN Number
                </label>
                <Input
                  value={formData.pan_number}
                  onChange={(e) => handleFieldChange('pan_number', e.target.value)}
                  placeholder="AAAAA0000A"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CIN Number
                </label>
                <Input
                  value={formData.cin_number}
                  onChange={(e) => handleFieldChange('cin_number', e.target.value)}
                  placeholder="U12345AB1234PLC123456"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  GST State Code
                </label>
                <Input
                  value={formData.gst_state_code}
                  onChange={(e) => handleFieldChange('gst_state_code', e.target.value)}
                  placeholder="22"
                />
              </div>
            </div>
          </div>

          {/* Financial Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Globe className="w-6 h-6 text-primary-600" />
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Financial Information</h2>
                <p className="text-gray-600">Financial year and currency settings</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Financial Year Start
                </label>
                <Input
                  type="date"
                  value={formData.financial_year_start}
                  onChange={(e) => handleFieldChange('financial_year_start', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Financial Year End
                </label>
                <Input
                  type="date"
                  value={formData.financial_year_end}
                  onChange={(e) => handleFieldChange('financial_year_end', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Financial Year
                </label>
                <Input
                  value={formData.current_financial_year}
                  onChange={(e) => handleFieldChange('current_financial_year', e.target.value)}
                  placeholder="2024-25"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Currency Code
                </label>
                <select
                  value={formData.currency_code}
                  onChange={(e) => handleFieldChange('currency_code', e.target.value)}
                  className="form-input"
                >
                  <option value="INR">INR - Indian Rupee</option>
                  <option value="USD">USD - US Dollar</option>
                  <option value="EUR">EUR - Euro</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Company Logo */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Image className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Company Logo</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center justify-center w-full h-32 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                {formData.logo_path ? (
                  <img
                    src={formData.logo_path}
                    alt="Company Logo"
                    className="max-w-full max-h-full object-contain rounded-lg"
                  />
                ) : (
                  <div className="text-center">
                    <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No logo uploaded</p>
                  </div>
                )}
              </div>
              
              <div className="space-y-2">
                <Button
                  variant="outline"
                  onClick={() => document.getElementById('logo-upload').click()}
                  className="w-full"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Upload Logo
                </Button>
                <input
                  id="logo-upload"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handleLogoUpload(e.target.files[0])}
                />
                
                {formData.logo_path && (
                  <Button
                    variant="outline"
                    onClick={() => handleFieldChange('logo_path', '')}
                    className="w-full text-danger-600 hover:text-danger-700"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Remove Logo
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Theme Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Palette className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Theme Settings</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme Color
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="color"
                    value={formData.theme_color}
                    onChange={(e) => handleFieldChange('theme_color', e.target.value)}
                    className="w-12 h-8 rounded border border-gray-300"
                  />
                  <Input
                    value={formData.theme_color}
                    onChange={(e) => handleFieldChange('theme_color', e.target.value)}
                    className="flex-1"
                    placeholder="#3b82f6"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Currency Symbol
                </label>
                <Input
                  value={formData.currency_symbol}
                  onChange={(e) => handleFieldChange('currency_symbol', e.target.value)}
                  placeholder="₹"
                />
              </div>
            </div>
          </div>

          {/* Additional Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center space-x-3 mb-4">
              <Info className="w-5 h-5 text-primary-600" />
              <h3 className="text-lg font-medium text-gray-900">Additional Information</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleFieldChange('description', e.target.value)}
                  rows={3}
                  className="form-input"
                  placeholder="Brief description of your company"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleFieldChange('notes', e.target.value)}
                  rows={3}
                  className="form-input"
                  placeholder="Internal notes about the company"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanySettings;