import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { marketingService } from '../../services/marketingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  Target, 
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
  Star,
  Gift,
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
  Stop,
  Send,
  MessageSquare,
  Database,
  Filter as FilterIcon,
  Layers,
  Activity
} from 'lucide-react';

const MarketingAutomation = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [segments, setSegments] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [automations, setAutomations] = useState([]);
  const [filteredSegments, setFilteredSegments] = useState([]);
  const [filteredCampaigns, setFilteredCampaigns] = useState([]);
  const [filteredAutomations, setFilteredAutomations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showAddSegment, setShowAddSegment] = useState(false);
  const [showAddCampaign, setShowAddCampaign] = useState(false);
  const [showAddAutomation, setShowAddAutomation] = useState(false);
  const [editingSegment, setEditingSegment] = useState(null);
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [editingAutomation, setEditingAutomation] = useState(null);
  const [viewingSegment, setViewingSegment] = useState(null);
  const [viewingCampaign, setViewingCampaign] = useState(null);
  const [viewingAutomation, setViewingAutomation] = useState(null);
  const [activeTab, setActiveTab] = useState('segments');

  // Segment form data
  const [segmentFormData, setSegmentFormData] = useState({
    name: '',
    description: '',
    criteria: [],
    status: 'active'
  });

  // Campaign form data
  const [campaignFormData, setCampaignFormData] = useState({
    name: '',
    description: '',
    type: 'email',
    segment_id: '',
    template_id: '',
    scheduled_time: '',
    status: 'draft'
  });

  // Automation form data
  const [automationFormData, setAutomationFormData] = useState({
    name: '',
    description: '',
    trigger: 'purchase',
    conditions: [],
    actions: [],
    status: 'active'
  });

  // Campaign types
  const campaignTypes = [
    { value: 'email', label: 'Email Campaign', icon: Mail },
    { value: 'sms', label: 'SMS Campaign', icon: MessageSquare },
    { value: 'whatsapp', label: 'WhatsApp Campaign', icon: Smartphone },
    { value: 'push', label: 'Push Notification', icon: Bell }
  ];

  // Automation triggers
  const automationTriggers = [
    { value: 'purchase', label: 'Purchase Made', icon: ShoppingCart },
    { value: 'signup', label: 'Customer Signup', icon: User },
    { value: 'abandoned_cart', label: 'Abandoned Cart', icon: ShoppingCart },
    { value: 'birthday', label: 'Birthday', icon: Gift },
    { value: 'anniversary', label: 'Anniversary', icon: Calendar },
    { value: 'inactive', label: 'Inactive Customer', icon: Clock }
  ];

  // Status options
  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600', bgColor: 'bg-green-100' },
    { value: 'inactive', label: 'Inactive', color: 'text-gray-600', bgColor: 'bg-gray-100' },
    { value: 'draft', label: 'Draft', color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
    { value: 'paused', label: 'Paused', color: 'text-orange-600', bgColor: 'bg-orange-100' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [segmentsData, campaignsData, automationsData] = await Promise.all([
          marketingService.getCustomerSegments(),
          marketingService.getMarketingCampaigns(),
          marketingService.getMarketingAutomations()
        ]);
        
        setSegments(segmentsData);
        setCampaigns(campaignsData);
        setAutomations(automationsData);
        setFilteredSegments(segmentsData);
        setFilteredCampaigns(campaignsData);
        setFilteredAutomations(automationsData);
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

  // Filter data
  useEffect(() => {
    let filtered = [];

    switch (activeTab) {
      case 'segments':
        filtered = segments;
        break;
      case 'campaigns':
        filtered = campaigns;
        break;
      case 'automations':
        filtered = automations;
        break;
      default:
        filtered = [];
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(item => item.status === statusFilter);
    }

    switch (activeTab) {
      case 'segments':
        setFilteredSegments(filtered);
        break;
      case 'campaigns':
        setFilteredCampaigns(filtered);
        break;
      case 'automations':
        setFilteredAutomations(filtered);
        break;
    }
  }, [segments, campaigns, automations, searchTerm, statusFilter, activeTab]);

  // Handle segment form field changes
  const handleSegmentFieldChange = (field, value) => {
    setSegmentFormData(prev => ({
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

  // Handle automation form field changes
  const handleAutomationFieldChange = (field, value) => {
    setAutomationFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add segment
  const handleAddSegment = async () => {
    try {
      setSaving(true);
      await marketingService.createCustomerSegment(segmentFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Customer segment created successfully',
      });
      setShowAddSegment(false);
      resetSegmentForm();
      // Refresh segments
      const segmentsData = await marketingService.getCustomerSegments();
      setSegments(segmentsData);
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
      await marketingService.createMarketingCampaign(campaignFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Marketing campaign created successfully',
      });
      setShowAddCampaign(false);
      resetCampaignForm();
      // Refresh campaigns
      const campaignsData = await marketingService.getMarketingCampaigns();
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

  // Handle add automation
  const handleAddAutomation = async () => {
    try {
      setSaving(true);
      await marketingService.createMarketingAutomation(automationFormData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Marketing automation created successfully',
      });
      setShowAddAutomation(false);
      resetAutomationForm();
      // Refresh automations
      const automationsData = await marketingService.getMarketingAutomations();
      setAutomations(automationsData);
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

  // Handle delete segment
  const handleDeleteSegment = async (segmentId) => {
    if (!window.confirm('Are you sure you want to delete this customer segment?')) {
      return;
    }

    try {
      await marketingService.deleteCustomerSegment(segmentId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Customer segment deleted successfully',
      });
      // Refresh segments
      const segmentsData = await marketingService.getCustomerSegments();
      setSegments(segmentsData);
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
    if (!window.confirm('Are you sure you want to delete this marketing campaign?')) {
      return;
    }

    try {
      await marketingService.deleteMarketingCampaign(campaignId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Marketing campaign deleted successfully',
      });
      // Refresh campaigns
      const campaignsData = await marketingService.getMarketingCampaigns();
      setCampaigns(campaignsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle delete automation
  const handleDeleteAutomation = async (automationId) => {
    if (!window.confirm('Are you sure you want to delete this marketing automation?')) {
      return;
    }

    try {
      await marketingService.deleteMarketingAutomation(automationId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Marketing automation deleted successfully',
      });
      // Refresh automations
      const automationsData = await marketingService.getMarketingAutomations();
      setAutomations(automationsData);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset forms
  const resetSegmentForm = () => {
    setSegmentFormData({
      name: '',
      description: '',
      criteria: [],
      status: 'active'
    });
  };

  const resetCampaignForm = () => {
    setCampaignFormData({
      name: '',
      description: '',
      type: 'email',
      segment_id: '',
      template_id: '',
      scheduled_time: '',
      status: 'draft'
    });
  };

  const resetAutomationForm = () => {
    setAutomationFormData({
      name: '',
      description: '',
      trigger: 'purchase',
      conditions: [],
      actions: [],
      status: 'active'
    });
  };

  // Get status info
  const getStatusInfo = (status) => {
    return statusOptions.find(s => s.value === status) || statusOptions[0];
  };

  // Get campaign type info
  const getCampaignTypeInfo = (type) => {
    return campaignTypes.find(t => t.value === type) || campaignTypes[0];
  };

  // Get automation trigger info
  const getAutomationTriggerInfo = (trigger) => {
    return automationTriggers.find(t => t.value === trigger) || automationTriggers[0];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading marketing automation..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Marketing Automation</h1>
          <p className="text-gray-600">Manage customer segmentation, campaigns, and automated messaging</p>
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
              { id: 'segments', name: 'Customer Segmentation', icon: Users },
              { id: 'campaigns', name: 'Campaign Management', icon: Target },
              { id: 'automations', name: 'Automated Messaging', icon: Zap },
              { id: 'analytics', name: 'Marketing Analytics', icon: BarChart3 }
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
          {/* Segments Tab */}
          {activeTab === 'segments' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search segments..."
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
                    {statusOptions.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddSegment(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Segment</span>
                </Button>
              </div>

              {/* Segments List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredSegments.map((segment) => {
                  const statusInfo = getStatusInfo(segment.status);
                  
                  return (
                    <div key={segment.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <Users className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{segment.name}</h3>
                            <p className="text-sm text-gray-500">{segment.description}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Customers:</span>
                          <span className="text-sm font-medium text-gray-900">{segment.customer_count || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Criteria:</span>
                          <span className="text-sm font-medium text-gray-900">{segment.criteria?.length || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Created:</span>
                          <span className="text-sm font-medium text-gray-900">{formatDate(segment.created_at)}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingSegment(segment)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingSegment(segment);
                            setSegmentFormData(segment);
                            setShowAddSegment(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteSegment(segment.id)}
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
                    {statusOptions.map(status => (
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
                  const statusInfo = getStatusInfo(campaign.status);
                  const typeInfo = getCampaignTypeInfo(campaign.type);
                  const TypeIcon = typeInfo.icon;
                  
                  return (
                    <div key={campaign.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <TypeIcon className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{campaign.name}</h3>
                            <p className="text-sm text-gray-500">{campaign.description}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Type:</span>
                          <span className="text-sm font-medium text-gray-900">{typeInfo.label}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Recipients:</span>
                          <span className="text-sm font-medium text-gray-900">{campaign.recipient_count || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Scheduled:</span>
                          <span className="text-sm font-medium text-gray-900">
                            {campaign.scheduled_time ? formatDate(campaign.scheduled_time) : 'N/A'}
                          </span>
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

          {/* Automations Tab */}
          {activeTab === 'automations' && (
            <div className="space-y-6">
              {/* Filters */}
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Search automations..."
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
                    {statusOptions.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowAddAutomation(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Automation</span>
                </Button>
              </div>

              {/* Automations List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredAutomations.map((automation) => {
                  const statusInfo = getStatusInfo(automation.status);
                  const triggerInfo = getAutomationTriggerInfo(automation.trigger);
                  const TriggerIcon = triggerInfo.icon;
                  
                  return (
                    <div key={automation.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                            <TriggerIcon className="w-5 h-5 text-purple-600" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{automation.name}</h3>
                            <p className="text-sm text-gray-500">{automation.description}</p>
                          </div>
                        </div>
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                          {statusInfo.label}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Trigger:</span>
                          <span className="text-sm font-medium text-gray-900">{triggerInfo.label}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Actions:</span>
                          <span className="text-sm font-medium text-gray-900">{automation.actions?.length || 0}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">Executions:</span>
                          <span className="text-sm font-medium text-gray-900">{automation.execution_count || 0}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setViewingAutomation(automation)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingAutomation(automation);
                            setAutomationFormData(automation);
                            setShowAddAutomation(true);
                          }}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteAutomation(automation.id)}
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
                <h3 className="text-lg font-medium text-gray-900 mb-2">Marketing Analytics</h3>
                <p className="text-gray-500">Campaign performance tracking will be implemented here</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Segment Modal */}
      {showAddSegment && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddSegment(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Users className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingSegment ? 'Edit Customer Segment' : 'Add New Customer Segment'}
                      </h3>
                      <p className="text-sm text-gray-500">Create or update customer segment</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddSegment(false);
                      setEditingSegment(null);
                      resetSegmentForm();
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Segment Name *
                    </label>
                    <Input
                      value={segmentFormData.name}
                      onChange={(e) => handleSegmentFieldChange('name', e.target.value)}
                      placeholder="Enter segment name"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={segmentFormData.description}
                      onChange={(e) => handleSegmentFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter segment description"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={segmentFormData.status}
                      onChange={(e) => handleSegmentFieldChange('status', e.target.value)}
                      className="form-input"
                    >
                      {statusOptions.map(status => (
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
                  onClick={editingSegment ? handleEditSegment : handleAddSegment}
                  loading={saving}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingSegment ? 'Update Segment' : 'Create Segment'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddSegment(false);
                    setEditingSegment(null);
                    resetSegmentForm();
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

export default MarketingAutomation;