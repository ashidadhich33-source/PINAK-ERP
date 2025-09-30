import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { marketingService } from '../../services/marketingService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import DataTable from '../../components/common/DataTable';
import { 
  Plus, 
  Search, 
  Download, 
  Upload,
  MessageSquare,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  Calendar,
  Send,
  Users,
  Target,
  Settings,
  Play,
  Pause,
  RefreshCw,
  FileText,
  BarChart3,
  TrendingUp,
  Bell,
  Share
} from 'lucide-react';

const WhatsAppIntegration = () => {
  const { addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('templates');
  const [templates, setTemplates] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [messageHistory, setMessageHistory] = useState([]);
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  // Fetch data based on active tab
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        search: searchTerm,
        status: filters.status !== 'all' ? filters.status : undefined,
        date_range: filters.dateRange !== 'all' ? filters.dateRange : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      let data;
      switch (activeTab) {
        case 'templates':
          data = await marketingService.getWhatsAppTemplates(params);
          setTemplates(data);
          break;
        case 'campaigns':
          data = await marketingService.getWhatsAppCampaigns(params);
          setCampaigns(data);
          break;
        case 'message-history':
          data = await marketingService.getWhatsAppMessages(params);
          setMessageHistory(data);
          break;
        case 'webhooks':
          data = await marketingService.getWhatsAppWebhooks(params);
          setWebhooks(data);
          break;
        default:
          break;
      }
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
    fetchData();
  }, [activeTab, searchTerm, filters]);

  // Handle search
  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      switch (activeTab) {
        case 'templates':
          await marketingService.deleteWhatsAppTemplate(id);
          setTemplates(prev => prev.filter(item => item.id !== id));
          break;
        case 'campaigns':
          await marketingService.deleteWhatsAppCampaign(id);
          setCampaigns(prev => prev.filter(item => item.id !== id));
          break;
        case 'webhooks':
          await marketingService.deleteWhatsAppWebhook(id);
          setWebhooks(prev => prev.filter(item => item.id !== id));
          break;
        default:
          break;
      }
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Item deleted successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle start campaign
  const handleStartCampaign = async (campaignId) => {
    try {
      await marketingService.startWhatsAppCampaign(campaignId);
      setCampaigns(prev => prev.map(campaign => 
        campaign.id === campaignId 
          ? { ...campaign, status: 'running' }
          : campaign
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Campaign started successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle stop campaign
  const handleStopCampaign = async (campaignId) => {
    try {
      await marketingService.stopWhatsAppCampaign(campaignId);
      setCampaigns(prev => prev.map(campaign => 
        campaign.id === campaignId 
          ? { ...campaign, status: 'stopped' }
          : campaign
      ));
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Campaign stopped successfully',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      await marketingService.exportWhatsAppData('csv', activeTab, filters);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Data export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Get current data based on active tab
  const getCurrentData = () => {
    switch (activeTab) {
      case 'templates':
        return templates;
      case 'campaigns':
        return campaigns;
      case 'message-history':
        return messageHistory;
      case 'webhooks':
        return webhooks;
      default:
        return [];
    }
  };

  // Get columns based on active tab
  const getColumns = () => {
    switch (activeTab) {
      case 'templates':
        return [
          {
            key: 'template_name',
            label: 'Template Name',
            render: (template) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{template.template_name}</p>
                  <p className="text-sm text-gray-500">{template.template_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'template_type',
            label: 'Type',
            render: (template) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {template.template_type}
              </span>
            ),
          },
          {
            key: 'content',
            label: 'Content',
            render: (template) => (
              <div className="max-w-xs">
                <p className="text-sm text-gray-900 truncate">{template.content || '-'}</p>
              </div>
            ),
          },
          {
            key: 'language',
            label: 'Language',
            render: (template) => (
              <span className="text-sm text-gray-900">{template.language || 'English'}</span>
            ),
          },
          {
            key: 'status',
            label: 'Status',
            render: (template) => {
              const statusInfo = {
                approved: { icon: CheckCircle, color: 'text-success-600', bgColor: 'bg-success-100' },
                pending: { icon: Clock, color: 'text-warning-600', bgColor: 'bg-warning-100' },
                rejected: { icon: XCircle, color: 'text-danger-600', bgColor: 'bg-danger-100' },
              }[template.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {template.status}
                </span>
              );
            },
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (template) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/whatsapp/templates/${template.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/whatsapp/templates/${template.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(template.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'campaigns':
        return [
          {
            key: 'campaign_name',
            label: 'Campaign',
            render: (campaign) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{campaign.campaign_name}</p>
                  <p className="text-sm text-gray-500">{campaign.campaign_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'template',
            label: 'Template',
            render: (campaign) => (
              <div>
                <p className="font-medium text-gray-900">{campaign.template?.template_name || '-'}</p>
                <p className="text-sm text-gray-500">{campaign.template?.template_type || ''}</p>
              </div>
            ),
          },
          {
            key: 'recipients',
            label: 'Recipients',
            render: (campaign) => (
              <div className="text-center">
                <p className="font-medium text-gray-900">{campaign.recipient_count || 0}</p>
                <p className="text-sm text-gray-500">recipients</p>
              </div>
            ),
          },
          {
            key: 'status',
            label: 'Status',
            render: (campaign) => {
              const statusInfo = {
                running: { icon: Play, color: 'text-success-600', bgColor: 'bg-success-100' },
                stopped: { icon: Pause, color: 'text-warning-600', bgColor: 'bg-warning-100' },
                completed: { icon: CheckCircle, color: 'text-blue-600', bgColor: 'bg-blue-100' },
                draft: { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' },
              }[campaign.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {campaign.status}
                </span>
              );
            },
          },
          {
            key: 'progress',
            label: 'Progress',
            render: (campaign) => (
              <div className="w-full">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>{campaign.sent_count || 0} sent</span>
                  <span>{Math.round(((campaign.sent_count || 0) / (campaign.recipient_count || 1)) * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full" 
                    style={{ width: `${Math.round(((campaign.sent_count || 0) / (campaign.recipient_count || 1)) * 100)}%` }}
                  ></div>
                </div>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (campaign) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/whatsapp/campaigns/${campaign.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/whatsapp/campaigns/${campaign.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                {campaign.status === 'draft' && (
                  <button
                    onClick={() => handleStartCampaign(campaign.id)}
                    className="text-success-600 hover:text-success-900"
                    title="Start Campaign"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                )}
                {campaign.status === 'running' && (
                  <button
                    onClick={() => handleStopCampaign(campaign.id)}
                    className="text-warning-600 hover:text-warning-900"
                    title="Stop Campaign"
                  >
                    <Pause className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(campaign.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'message-history':
        return [
          {
            key: 'message_info',
            label: 'Message',
            render: (message) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{message.recipient_name || 'Unknown'}</p>
                  <p className="text-sm text-gray-500">{message.recipient_phone}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'content',
            label: 'Content',
            render: (message) => (
              <div className="max-w-xs">
                <p className="text-sm text-gray-900 truncate">{message.content || '-'}</p>
              </div>
            ),
          },
          {
            key: 'message_type',
            label: 'Type',
            render: (message) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {message.message_type}
              </span>
            ),
          },
          {
            key: 'status',
            label: 'Status',
            render: (message) => {
              const statusInfo = {
                sent: { icon: CheckCircle, color: 'text-success-600', bgColor: 'bg-success-100' },
                delivered: { icon: CheckCircle, color: 'text-blue-600', bgColor: 'bg-blue-100' },
                read: { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' },
                failed: { icon: XCircle, color: 'text-danger-600', bgColor: 'bg-danger-100' },
                pending: { icon: Clock, color: 'text-warning-600', bgColor: 'bg-warning-100' },
              }[message.status] || { icon: Clock, color: 'text-gray-600', bgColor: 'bg-gray-100' };
              
              const Icon = statusInfo.icon;
              return (
                <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${statusInfo.bgColor} ${statusInfo.color}`}>
                  <Icon className="w-3 h-3 mr-1" />
                  {message.status}
                </span>
              );
            },
          },
          {
            key: 'sent_at',
            label: 'Sent At',
            render: (message) => (
              <div>
                <p className="font-medium text-gray-900">
                  {new Date(message.sent_at).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-500">
                  {new Date(message.sent_at).toLocaleTimeString()}
                </p>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (message) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/whatsapp/messages/${message.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                {message.status === 'failed' && (
                  <button
                    onClick={() => {/* Handle resend */}}
                    className="text-blue-600 hover:text-blue-900"
                    title="Resend Message"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                )}
              </div>
            ),
          },
        ];
      case 'webhooks':
        return [
          {
            key: 'webhook_name',
            label: 'Webhook',
            render: (webhook) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Bell className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{webhook.webhook_name}</p>
                  <p className="text-sm text-gray-500">{webhook.url}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'events',
            label: 'Events',
            render: (webhook) => (
              <div className="flex flex-wrap gap-1">
                {webhook.events?.map((event, index) => (
                  <span key={index} className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded">
                    {event}
                  </span>
                ))}
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (webhook) => (
              <div className="flex items-center space-x-2">
                {webhook.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {webhook.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'last_triggered',
            label: 'Last Triggered',
            render: (webhook) => (
              <div>
                <p className="font-medium text-gray-900">
                  {webhook.last_triggered ? new Date(webhook.last_triggered).toLocaleDateString() : 'Never'}
                </p>
                <p className="text-sm text-gray-500">
                  {webhook.trigger_count || 0} times
                </p>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (webhook) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/whatsapp/webhooks/${webhook.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/whatsapp/webhooks/${webhook.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(webhook.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      default:
        return [];
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading WhatsApp data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">WhatsApp Integration</h1>
          <p className="text-gray-600">Manage WhatsApp messaging, campaigns, and templates</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            onClick={handleExport}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'templates', name: 'Message Templates', icon: FileText },
              { id: 'campaigns', name: 'Campaigns', icon: Target },
              { id: 'message-history', name: 'Message History', icon: MessageSquare },
              { id: 'webhooks', name: 'Webhooks', icon: Bell },
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
          {/* Filters and Search */}
          <div className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  <Input
                    placeholder="Search..."
                    value={searchTerm}
                    onChange={handleSearch}
                    className="pl-10"
                  />
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>
              
              <div>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="running">Running</option>
                  <option value="stopped">Stopped</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.dateRange}
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Dates</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
              
              <div>
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                  className="form-input"
                >
                  <option value="created_at">Sort by Date</option>
                  <option value="name">Sort by Name</option>
                  <option value="status">Sort by Status</option>
                </select>
              </div>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert type="danger" title="Error">
              {error}
            </Alert>
          )}

          {/* Data Table */}
          <DataTable
            data={getCurrentData()}
            columns={getColumns()}
            loading={loading}
            emptyMessage="No data found"
          />
        </div>
      </div>
    </div>
  );
};

export default WhatsAppIntegration;