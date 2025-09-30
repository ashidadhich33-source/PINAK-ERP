import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { reportService } from '../../services/reportService';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Alert from '../../components/common/Alert';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Calendar, 
  Download, 
  RefreshCw, 
  FileText, 
  PieChart, 
  Activity,
  Calculator,
  Eye,
  Print,
  Share2,
  Clock,
  Target,
  Award,
  CheckCircle,
  AlertTriangle,
  Users,
  ShoppingCart,
  Package,
  Building2,
  CreditCard,
  Settings,
  Plus,
  Edit,
  Trash2,
  Save,
  X,
  Bell,
  Mail,
  Link,
  Copy
} from 'lucide-react';

const AdvancedReporting = () => {
  const { addNotification } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('custom');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingReport, setEditingReport] = useState(null);
  const [customReports, setCustomReports] = useState([]);
  const [scheduledReports, setScheduledReports] = useState([]);
  const [sharedReports, setSharedReports] = useState([]);

  // Form data for custom reports
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    data_source: '',
    filters: [],
    columns: [],
    chart_type: '',
    schedule: '',
    recipients: []
  });

  // Report data sources
  const dataSources = [
    { value: 'sales', label: 'Sales Data', icon: ShoppingCart },
    { value: 'inventory', label: 'Inventory Data', icon: Package },
    { value: 'financial', label: 'Financial Data', icon: DollarSign },
    { value: 'customers', label: 'Customer Data', icon: Users },
    { value: 'purchases', label: 'Purchase Data', icon: Building2 }
  ];

  // Chart types
  const chartTypes = [
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
    { value: 'line', label: 'Line Chart', icon: TrendingUp },
    { value: 'pie', label: 'Pie Chart', icon: PieChart },
    { value: 'table', label: 'Table', icon: FileText }
  ];

  // Schedule options
  const scheduleOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'quarterly', label: 'Quarterly' }
  ];

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const [custom, scheduled, shared] = await Promise.all([
          reportService.getCustomReports(),
          reportService.getScheduledReports(),
          reportService.getSharedReports()
        ]);
        
        setCustomReports(custom);
        setScheduledReports(scheduled);
        setSharedReports(shared);
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

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle add filter
  const handleAddFilter = () => {
    setFormData(prev => ({
      ...prev,
      filters: [...prev.filters, { field: '', operator: '', value: '' }]
    }));
  };

  // Handle remove filter
  const handleRemoveFilter = (index) => {
    setFormData(prev => ({
      ...prev,
      filters: prev.filters.filter((_, i) => i !== index)
    }));
  };

  // Handle add column
  const handleAddColumn = () => {
    setFormData(prev => ({
      ...prev,
      columns: [...prev.columns, { field: '', label: '', type: '' }]
    }));
  };

  // Handle remove column
  const handleRemoveColumn = (index) => {
    setFormData(prev => ({
      ...prev,
      columns: prev.columns.filter((_, i) => i !== index)
    }));
  };

  // Handle add recipient
  const handleAddRecipient = () => {
    setFormData(prev => ({
      ...prev,
      recipients: [...prev.recipients, { email: '', name: '' }]
    }));
  };

  // Handle remove recipient
  const handleRemoveRecipient = (index) => {
    setFormData(prev => ({
      ...prev,
      recipients: prev.recipients.filter((_, i) => i !== index)
    }));
  };

  // Handle save custom report
  const handleSaveCustomReport = async () => {
    try {
      setLoading(true);
      if (editingReport) {
        await reportService.updateCustomReport(editingReport.id, formData);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Custom report updated successfully',
        });
      } else {
        await reportService.createCustomReport(formData);
        addNotification({
          type: 'success',
          title: 'Success',
          message: 'Custom report created successfully',
        });
      }
      setShowAddForm(false);
      setEditingReport(null);
      resetForm();
      // Refresh reports
      const custom = await reportService.getCustomReports();
      setCustomReports(custom);
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

  // Handle delete custom report
  const handleDeleteCustomReport = async (reportId) => {
    if (!window.confirm('Are you sure you want to delete this custom report?')) {
      return;
    }

    try {
      await reportService.deleteCustomReport(reportId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Custom report deleted successfully',
      });
      // Refresh reports
      const custom = await reportService.getCustomReports();
      setCustomReports(custom);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle schedule report
  const handleScheduleReport = async (reportId) => {
    try {
      await reportService.scheduleReport(reportId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Report scheduled successfully',
      });
      // Refresh scheduled reports
      const scheduled = await reportService.getScheduledReports();
      setScheduledReports(scheduled);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle share report
  const handleShareReport = async (reportId) => {
    try {
      await reportService.shareReport(reportId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Report shared successfully',
      });
      // Refresh shared reports
      const shared = await reportService.getSharedReports();
      setSharedReports(shared);
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      data_source: '',
      filters: [],
      columns: [],
      chart_type: '',
      schedule: '',
      recipients: []
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading advanced reporting..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Reporting</h1>
          <p className="text-gray-600">Create custom reports, schedule automated reports, and share insights</p>
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
          <Button
            onClick={() => setShowAddForm(true)}
            className="flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Create Report</span>
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
              { id: 'custom', name: 'Custom Reports', icon: FileText },
              { id: 'scheduled', name: 'Scheduled Reports', icon: Clock },
              { id: 'shared', name: 'Shared Reports', icon: Share2 }
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
          {/* Custom Reports Tab */}
          {activeTab === 'custom' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {customReports.map((report) => (
                  <div key={report.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                          <FileText className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{report.name}</h3>
                          <p className="text-sm text-gray-500">{report.description}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Data Source:</span>
                        <span className="text-sm font-medium text-gray-900">{report.data_source}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Chart Type:</span>
                        <span className="text-sm font-medium text-gray-900">{report.chart_type}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Created:</span>
                        <span className="text-sm font-medium text-gray-900">{new Date(report.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setEditingReport(report);
                          setFormData(report);
                          setShowAddForm(true);
                        }}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleScheduleReport(report.id)}
                      >
                        <Clock className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleShareReport(report.id)}
                      >
                        <Share2 className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleDeleteCustomReport(report.id)}
                        className="text-danger-600 hover:text-danger-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Scheduled Reports Tab */}
          {activeTab === 'scheduled' && (
            <div className="space-y-6">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Report Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Schedule
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Next Run
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {scheduledReports.map((report) => (
                      <tr key={report.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {report.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {report.schedule}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(report.next_run).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            report.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {report.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleShareReport(report.id)}
                            >
                              <Share2 className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDeleteCustomReport(report.id)}
                              className="text-danger-600 hover:text-danger-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Shared Reports Tab */}
          {activeTab === 'shared' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sharedReports.map((report) => (
                  <div key={report.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                          <Share2 className="w-5 h-5 text-green-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-medium text-gray-900">{report.name}</h3>
                          <p className="text-sm text-gray-500">Shared by {report.shared_by}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Shared:</span>
                        <span className="text-sm font-medium text-gray-900">{new Date(report.shared_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Access:</span>
                        <span className="text-sm font-medium text-gray-900">{report.access_level}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => window.open(report.link, '_blank')}
                      >
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => navigator.clipboard.writeText(report.link)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add/Edit Custom Report Modal */}
      {showAddForm && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddForm(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-primary-600" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {editingReport ? 'Edit Custom Report' : 'Create Custom Report'}
                      </h3>
                      <p className="text-sm text-gray-500">Build your custom report</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingReport(null);
                      resetForm();
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
                        Report Name *
                      </label>
                      <Input
                        value={formData.name}
                        onChange={(e) => handleFieldChange('name', e.target.value)}
                        placeholder="Enter report name"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Data Source *
                      </label>
                      <select
                        value={formData.data_source}
                        onChange={(e) => handleFieldChange('data_source', e.target.value)}
                        className="form-input"
                        required
                      >
                        <option value="">Select Data Source</option>
                        {dataSources.map(source => (
                          <option key={source.value} value={source.value}>
                            {source.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleFieldChange('description', e.target.value)}
                      rows={3}
                      className="form-input"
                      placeholder="Enter report description"
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Chart Type
                      </label>
                      <select
                        value={formData.chart_type}
                        onChange={(e) => handleFieldChange('chart_type', e.target.value)}
                        className="form-input"
                      >
                        <option value="">Select Chart Type</option>
                        {chartTypes.map(chart => (
                          <option key={chart.value} value={chart.value}>
                            {chart.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Schedule
                      </label>
                      <select
                        value={formData.schedule}
                        onChange={(e) => handleFieldChange('schedule', e.target.value)}
                        className="form-input"
                      >
                        <option value="">No Schedule</option>
                        {scheduleOptions.map(schedule => (
                          <option key={schedule.value} value={schedule.value}>
                            {schedule.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  {/* Filters */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Filters</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleAddFilter}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Filter
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.filters.map((filter, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <Input
                            value={filter.field}
                            onChange={(e) => {
                              const newFilters = [...formData.filters];
                              newFilters[index].field = e.target.value;
                              setFormData(prev => ({ ...prev, filters: newFilters }));
                            }}
                            placeholder="Field"
                            className="flex-1"
                          />
                          <select
                            value={filter.operator}
                            onChange={(e) => {
                              const newFilters = [...formData.filters];
                              newFilters[index].operator = e.target.value;
                              setFormData(prev => ({ ...prev, filters: newFilters }));
                            }}
                            className="form-input w-32"
                          >
                            <option value="">Operator</option>
                            <option value="equals">Equals</option>
                            <option value="contains">Contains</option>
                            <option value="greater_than">Greater Than</option>
                            <option value="less_than">Less Than</option>
                          </select>
                          <Input
                            value={filter.value}
                            onChange={(e) => {
                              const newFilters = [...formData.filters];
                              newFilters[index].value = e.target.value;
                              setFormData(prev => ({ ...prev, filters: newFilters }));
                            }}
                            placeholder="Value"
                            className="flex-1"
                          />
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRemoveFilter(index)}
                            className="text-danger-600 hover:text-danger-700"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Columns */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Columns</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleAddColumn}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Column
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.columns.map((column, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <Input
                            value={column.field}
                            onChange={(e) => {
                              const newColumns = [...formData.columns];
                              newColumns[index].field = e.target.value;
                              setFormData(prev => ({ ...prev, columns: newColumns }));
                            }}
                            placeholder="Field"
                            className="flex-1"
                          />
                          <Input
                            value={column.label}
                            onChange={(e) => {
                              const newColumns = [...formData.columns];
                              newColumns[index].label = e.target.value;
                              setFormData(prev => ({ ...prev, columns: newColumns }));
                            }}
                            placeholder="Label"
                            className="flex-1"
                          />
                          <select
                            value={column.type}
                            onChange={(e) => {
                              const newColumns = [...formData.columns];
                              newColumns[index].type = e.target.value;
                              setFormData(prev => ({ ...prev, columns: newColumns }));
                            }}
                            className="form-input w-32"
                          >
                            <option value="">Type</option>
                            <option value="text">Text</option>
                            <option value="number">Number</option>
                            <option value="date">Date</option>
                            <option value="currency">Currency</option>
                          </select>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRemoveColumn(index)}
                            className="text-danger-600 hover:text-danger-700"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Recipients */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-gray-900">Recipients</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={handleAddRecipient}
                      >
                        <Plus className="w-4 h-4 mr-1" />
                        Add Recipient
                      </Button>
                    </div>
                    
                    <div className="space-y-3">
                      {formData.recipients.map((recipient, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                          <Input
                            value={recipient.email}
                            onChange={(e) => {
                              const newRecipients = [...formData.recipients];
                              newRecipients[index].email = e.target.value;
                              setFormData(prev => ({ ...prev, recipients: newRecipients }));
                            }}
                            placeholder="Email"
                            type="email"
                            className="flex-1"
                          />
                          <Input
                            value={recipient.name}
                            onChange={(e) => {
                              const newRecipients = [...formData.recipients];
                              newRecipients[index].name = e.target.value;
                              setFormData(prev => ({ ...prev, recipients: newRecipients }));
                            }}
                            placeholder="Name"
                            className="flex-1"
                          />
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRemoveRecipient(index)}
                            className="text-danger-600 hover:text-danger-700"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  onClick={handleSaveCustomReport}
                  loading={loading}
                  className="w-full sm:w-auto sm:ml-3"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {editingReport ? 'Update Report' : 'Create Report'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAddForm(false);
                    setEditingReport(null);
                    resetForm();
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

export default AdvancedReporting;