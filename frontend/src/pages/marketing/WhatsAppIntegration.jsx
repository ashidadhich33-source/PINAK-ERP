import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { marketingService } from '../../services/marketingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  MessageSquare, 
  Plus, 
  Edit, 
  Trash2, 
  Search, 
  Filter, 
  Download, 
  RefreshCw, 
  Save, 
  X,
  Eye,
  Send,
  Target,
  Users,
  TrendingUp,
  Calendar,
  Settings,
  CheckCircle,
  AlertTriangle,
  Clock,
  DollarSign,
  Percent,
  Crown,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  CreditCard,
  ShoppingCart,
  User,
  FileText,
  BarChart3,
  Smartphone,
  Wifi,
  Shield,
  Bell,
  Mail,
  Link,
  Copy,
  Play,
  Pause,
  Stop
} from 'lucide-react';

const WhatsAppIntegration = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [filteredTemplates, setFilteredTemplates] = useState([]);
  const [filteredCampaigns, setFilteredCampaigns] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddTemplate, setShowAddTemplate] = useState(false);
  const [showAddCampaign, setShowAddCampaign] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [viewingTemplate, setViewingTemplate] = useState(null);
  const [viewingCampaign, setViewingCampaign] = useState(null);
  const [activeTab, setActiveTab] = useState('templates');

  // Template form data
  const [templateFormData, setTemplateFormData] = useState({
    name: '',
    category: 'UTILITY',
    language: 'en',
    header_type: 'TEXT',
    header_text: '',
    body_text: '',
    footer_text: '',
    status: 'PENDING'
  });

  // Campaign form data
  const [campaignFormData, setCampaignFormData] = useState({
    name: '',
    template_id: '',
    target_audience: 'all',
    scheduled_time: '',
    status: 'draft'
  });

  // Template categories
  const templateCategories = [
    { value: 'UTILITY', label: 'Utility', icon: Settings },
    { value: 'MARKETING', label: 'Marketing', icon: Target },
    { value: 'AUTHENTICATION', label: 'Authentication', icon: Shield }
  ];

  // Template statuses
  const templateStatuses = [
    { value: 'PENDING', label: 'Pending', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'APPROVED', label: 'Approved', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'REJECTED', label: 'Rejected', color: 'text-red-600', bgColor: 'bg-red-100' },
    { value: 'DISABLED', label: 'Disabled', color: 'text-gray-600', bgColor: 'bg-gray-100' }
  ];

  // Campaign statuses
  const campaignStatuses = [
    { value: 'draft', label: 'Draft', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'scheduled', label: 'Scheduled', color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { value: 'running', label: 'Running', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'completed', label: 'Completed', color: 'text-purple-600', bgColor: 'bg-purple-100' },
    { value: 'paused', label: 'Paused', color: 'text-orange-600', bgColor: 'bg-orange-100' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-red-600', bgColor: 'bg-red-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [templatesData, campaignsData] = await Promise.all([
          marketingService.getWhatsAppTemplates(),
          marketingService.getWhatsAppCampaigns()
        ]);
        
        setTemplates(templatesData);
        setCampaigns(campaignsData);
        setFilteredTemplates(templatesData);
        setFilteredCampaigns(campaignsData);
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

  // Filter templates
  useEffect(() => {
    let filtered = templates;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(template =>
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        template.body_text.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(template => template.status === statusFilter);
    }

    setFilteredTemplates(filtered);
  }, [templates, searchTerm, statusFilter]);

  // Filter campaigns
  useEffect(() => {
    let filtered = campaigns;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(campaign =>
        campaign.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(campaign => campaign.status === statusFilter);
    }

    setFilteredCampaigns(filtered);
  }, [campaigns, searchTerm, statusFilter]);

  // Handle template form field changes
  const handleTemplateFieldChange = (field, value) => {
    setTemplateFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle campaign form field changes
  const handleCampaignFieldChange = (field, value) => {
    setCampaignFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add template
  const handleAddTemplate = async () => {
    try {
      setSaving(true);
      await marketingService.createWhatsAppTemplate(templateFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp template created successfully',
      });
      setShowAddTemplate(false);
      resetTemplateForm();
      // Refresh templates
      const templatesData = await marketingService.getWhatsAppTemplates();
      setTemplates(templatesData);
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

  // Handle edit template
  const handleEditTemplate = async () => {
    try {
      setSaving(true);
      await marketingService.updateWhatsAppTemplate(editingTemplate.id, templateFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp template updated successfully',
      });
      setEditingTemplate(null);
      setShowAddTemplate(false);
      resetTemplateForm();
      // Refresh templates
      const templatesData = await marketingService.getWhatsAppTemplates();
      setTemplates(templatesData);
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

  // Handle add campaign
  const handleAddCampaign = async () => {
    try {
      setSaving(true);
      await marketingService.createWhatsAppCampaign(campaignFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp campaign created successfully',
      });
      setShowAddCampaign(false);
      resetCampaignForm();
      // Refresh campaigns
      const campaignsData = await marketingService.getWhatsAppCampaigns();
      setCampaigns(campaignsData);
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

  // Handle edit campaign
  const handleEditCampaign = async () => {
    try {
      setSaving(true);
      await marketingService.updateWhatsAppCampaign(editingCampaign.id, campaignFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp campaign updated successfully',
      });
      setEditingCampaign(null);
      setShowAddCampaign(false);
      resetCampaignForm();
      // Refresh campaigns
      const campaignsData = await marketingService.getWhatsAppCampaigns();
      setCampaigns(campaignsData);
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

  // Handle delete template
  const handleDeleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this WhatsApp template?')) {
      return;
    }

    try {
      await marketingService.deleteWhatsAppTemplate(templateId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp template deleted successfully',
      });
      // Refresh templates
      const templatesData = await marketingService.getWhatsAppTemplates();
      setTemplates(templatesData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete campaign
  const handleDeleteCampaign = async (campaignId) => {
    if (!window.confirm('Are you sure you want to delete this WhatsApp campaign?')) {
      return;
    }

    try {
      await marketingService.deleteWhatsAppCampaign(campaignId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'WhatsApp campaign deleted successfully',
      });
      // Refresh campaigns
      const campaignsData = await marketingService.getWhatsAppCampaigns();
      setCampaigns(campaignsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset template form
  const resetTemplateForm = () => {
    setTemplateFormData({
      name: '',
      category: 'UTILITY',
      language: 'en',
      header_type: 'TEXT',
      header_text: '',
      body_text: '',
      footer_text: '',
      status: 'PENDING'
    });
  };

  // Reset campaign form
  const resetCampaignForm = () => {
    setCampaignFormData({
      name: '',
      template_id: '',
      target_audience: 'all',
      scheduled_time: '',
      status: 'draft'
    });
  };

  // Get template status info
  const getTemplateStatusInfo = (status) => {
    return templateStatuses.find(s => s.value === status) || templateStatuses[0];
  };

  // Get campaign status info
  const getCampaignStatusInfo = (status) => {
    return campaignStatuses.find(s => s.value === status) || campaignStatuses[0];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading WhatsApp integration..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">WhatsApp Integration</h1>
          <p className="text-gray-600">Manage WhatsApp Business API integration and messaging</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
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

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'templates', name: 'Message Templates', icon: FileText },
              { id: 'campaigns', name: 'Message Campaigns', icon: Target },
              { id: 'analytics', name: 'WhatsApp Analytics', icon: BarChart3 },
              { id: 'settings', name: 'Settings', icon: Settings }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Templates Tab */}
          {activeTab === 'templates' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search templates..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Status</option>
                    {templateStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddTemplate(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Template</span>
                </Button>
              </div>

              {/* Templates List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredTemplates.map((template) => {
                  const statusInfo = getTemplateStatusInfo(template.status);
                  
                  return (
                    <div key={template.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <MessageSquare className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                            <p className="text-sm text-gray-500">{template.category}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Language:</span>
                          <span className="text-sm font-medium text-gray-900">{template.language}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Header:</span>
                          <span className="text-sm font-medium text-gray-900">{template.header_type}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Created:</span>
                          <span className="text-sm font-medium text-gray-900">{formatDate(template.created_at)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingTemplate(template)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingTemplate(template);
                            setTemplateFormData(template);
                            setShowAddTemplate(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteTemplate(template.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Campaigns Tab */}
          {activeTab === 'campaigns' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search campaigns..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                </div>
                <div className="w-48">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="form-input"
                  >
                    <option value="all">All Status</option>
                    {campaignStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddCampaign(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Campaign</span>
                </Button>
              </div>

              {/* Campaigns List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCampaigns.map((campaign) => {
                  const statusInfo = getCampaignStatusInfo(campaign.status);
                  
                  return (
                    <div key={campaign.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Target className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{campaign.name}</h3>
                            <p className="text-sm text-gray-500">{campaign.target_audience}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Template:</span>
                          <span className="text-sm font-medium text-gray-900">{campaign.template_name || 'N/A'}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Scheduled:</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.scheduled_time ? formatDate(campaign.scheduled_time) : 'N/A'}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Recipients:</span>
                          <span className="text-sm font-medium text-gray-900">{campaign.recipient_count || 0}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingCampaign(campaign)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingCampaign(campaign);
                            setCampaignFormData(campaign);
                            setShowAddCampaign(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteCampaign(campaign.id)}
                          className="text-danger-600 hover:text-danger-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Analytics Tab */}
          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">WhatsApp Analytics</h3>
                <p className="text-gray-500">Message delivery and engagement analytics will be implemented here</p>
              </div>
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">WhatsApp Settings</h3>
                <p className="text-gray-500">WhatsApp Business API configuration will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Template Modal */}
      {showAddTemplate && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddTemplate(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <MessageSquare className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingTemplate ? 'Edit WhatsApp Template' : 'Add New WhatsApp Template'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update WhatsApp message template</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddTemplate(false);
                      setEditingTemplate(null);
                      resetTemplateForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Template Name *
                      </label>
                      <Input
                        value={templateFormData.name}
                        onChange={(e) => handleTemplateFieldChange('name', e.target.value)}
                        placeholder="Enter template name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category *
                      </label>
                      <select
                        value={templateFormData.category}
                        onChange={(e) => handleTemplateFieldChange('category', e.target.value)}
                        className="form-input"
                        required
                      >
                        {templateCategories.map(category => (
                          <option key={category.value} value={category.value}>
                            {category.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Language *
                      </label>
                      <select
                        value={templateFormData.language}
                        onChange={(e) => handleTemplateFieldChange('language', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="en">English</option>
                        <option value="hi">Hindi</option>
                        <option value="ta">Tamil</option>
                        <option value="te">Telugu</option>
                        <option value="bn">Bengali</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Header Type
                      </label>
                      <select
                        value={templateFormData.header_type}
                        onChange={(e) => handleTemplateFieldChange('header_type', e.target.value)}
                        className="form-input"
                      >
                        <option value="TEXT">Text</option>
                        <option value="IMAGE">Image</option>
                        <option value="VIDEO">Video</option>
                        <option value="DOCUMENT">Document</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Header Text
                    </label>
                    <Input
                      value={templateFormData.header_text}
                      onChange={(e) => handleTemplateFieldChange('header_text', e.target.value)}
                      placeholder="Enter header text"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Body Text *
                    </label>
                    <textarea
                      value={templateFormData.body_text}
                      onChange={(e) => handleTemplateFieldChange('body_text', e.target.value)}
                      rows={4}
                      className="form-input"
                      placeholder="Enter body text"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Footer Text
                    </label>
                    <Input
                      value={templateFormData.footer_text}
                      onChange={(e) => handleTemplateFieldChange('footer_text', e.target.value)}
                      placeholder="Enter footer text"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={templateFormData.status}
                      onChange={(e) => handleTemplateFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {templateStatuses.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingTemplate ? handleEditTemplate : handleAddTemplate}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingTemplate ? 'Update Template' : 'Create Template'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddTemplate(false);
                    setEditingTemplate(null);
                    resetTemplateForm();
                  }}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Campaign Modal */}
      {showAddCampaign && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddCampaign(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Target className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingCampaign ? 'Edit WhatsApp Campaign' : 'Add New WhatsApp Campaign'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update WhatsApp message campaign</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddCampaign(false);
                      setEditingCampaign(null);
                      resetCampaignForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Campaign Name *
                    </label>
                    <Input
                      value={campaignFormData.name}
                      onChange={(e) => handleCampaignFieldChange('name', e.target.value)}
                      placeholder="Enter campaign name"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Template *
                    </label>
                    <select
                      value={campaignFormData.template_id}
                      onChange={(e) => handleCampaignFieldChange('template_id', e.target.value)}
                      className="form-input"
                      required
                    >
                      <option value="">Select Template</option>
                      {templates.map(template => (
                        <option key={template.id} value={template.id}>
                          {template.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Target Audience
                    </label>
                    <select
                      value={campaignFormData.target_audience}
                      onChange={(e) => handleCampaignFieldChange('target_audience', e.target.value)}
                      className="form-input"
                    >
                      <option value="all">All Customers</option>
                      <option value="vip">VIP Customers</option>
                      <option value="new">New Customers</option>
                      <option value="inactive">Inactive Customers</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Scheduled Time
                    </label>
                    <Input
                      type="datetime-local"
                      value={campaignFormData.scheduled_time}
                      onChange={(e) => handleCampaignFieldChange('scheduled_time', e.target.value)}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={campaignFormData.status}
                      onChange={(e) => handleCampaignFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {campaignStatuses.map(status => (
                        <option key={status.value} value={status.value}>
                          {status.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={editingCampaign ? handleEditCampaign : handleAddCampaign}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingCampaign ? 'Update Campaign' : 'Create Campaign'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddCampaign(false);
                    setEditingCampaign(null);
                    resetCampaignForm();
                  }}
                  className="mt-3 w-full sm:mt-0 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatsAppIntegration;