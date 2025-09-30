import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useApp } from '../../contexts/AppContext';
import { advancedReportingService } from '../../services/advancedReportingService';
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
  BarChart3,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  Filter,
  Calendar,
  FileText,
  TrendingUp,
  Settings,
  Star,
  Share,
  Play,
  Pause,
  RefreshCw,
  Target,
  PieChart,
  LineChart,
  Activity
} from 'lucide-react';

const AdvancedReporting = () => {
  const { addNotification } = useApp();
  const [activeTab, setActiveTab] = useState('custom-reports');
  const [customReports, setCustomReports] = useState([]);
  const [reportTemplates, setReportTemplates] = useState([]);
  const [reportSchedules, setReportSchedules] = useState([]);
  const [reportCategories, setReportCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
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
        category: filters.category !== 'all' ? filters.category : undefined,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder,
      };
      
      let data;
      switch (activeTab) {
        case 'custom-reports':
          data = await advancedReportingService.getCustomReports(params);
          setCustomReports(data);
          break;
        case 'templates':
          data = await advancedReportingService.getReportTemplates(params);
          setReportTemplates(data);
          break;
        case 'schedules':
          data = await advancedReportingService.getReportSchedules(params);
          setReportSchedules(data);
          break;
        case 'categories':
          data = await advancedReportingService.getReportCategories(params);
          setReportCategories(data);
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
        case 'custom-reports':
          await advancedReportingService.deleteCustomReport(id);
          setCustomReports(prev => prev.filter(item => item.id !== id));
          break;
        case 'templates':
          await advancedReportingService.deleteReportTemplate(id);
          setReportTemplates(prev => prev.filter(item => item.id !== id));
          break;
        case 'schedules':
          await advancedReportingService.deleteReportSchedule(id);
          setReportSchedules(prev => prev.filter(item => item.id !== id));
          break;
        case 'categories':
          await advancedReportingService.deleteReportCategory(id);
          setReportCategories(prev => prev.filter(item => item.id !== id));
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

  // Handle generate report
  const handleGenerateReport = async (reportId) => {
    try {
      await advancedReportingService.generateReport(reportId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Report generation started',
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
  const handleExport = async (reportId, format = 'pdf') => {
    try {
      await advancedReportingService.exportReport(reportId, format);
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Report export will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  // Handle add to favorites
  const handleAddToFavorites = async (reportId) => {
    try {
      await advancedReportingService.addReportFavorite(reportId);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Report added to favorites',
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
      case 'custom-reports':
        return customReports;
      case 'templates':
        return reportTemplates;
      case 'schedules':
        return reportSchedules;
      case 'categories':
        return reportCategories;
      default:
        return [];
    }
  };

  // Get columns based on active tab
  const getColumns = () => {
    switch (activeTab) {
      case 'custom-reports':
        return [
          {
            key: 'report_name',
            label: 'Report Name',
            render: (report) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{report.report_name}</p>
                  <p className="text-sm text-gray-500">{report.report_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'category',
            label: 'Category',
            render: (report) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {report.category?.category_name || 'Uncategorized'}
              </span>
            ),
          },
          {
            key: 'report_type',
            label: 'Type',
            render: (report) => (
              <div className="flex items-center space-x-2">
                {report.report_type === 'financial' && <PieChart className="w-4 h-4 text-green-600" />}
                {report.report_type === 'operational' && <BarChart3 className="w-4 h-4 text-blue-600" />}
                {report.report_type === 'analytical' && <LineChart className="w-4 h-4 text-purple-600" />}
                <span className="text-sm text-gray-900">{report.report_type}</span>
              </div>
            ),
          },
          {
            key: 'last_generated',
            label: 'Last Generated',
            render: (report) => (
              <div>
                <p className="font-medium text-gray-900">
                  {report.last_generated ? new Date(report.last_generated).toLocaleDateString() : 'Never'}
                </p>
                <p className="text-sm text-gray-500">
                  {report.generation_count || 0} times
                </p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (report) => (
              <div className="flex items-center space-x-2">
                {report.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {report.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (report) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/reporting/custom-reports/${report.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/reporting/custom-reports/${report.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleGenerateReport(report.id)}
                  className="text-blue-600 hover:text-blue-900"
                  title="Generate Report"
                >
                  <Play className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleExport(report.id, 'pdf')}
                  className="text-green-600 hover:text-green-900"
                  title="Export PDF"
                >
                  <Download className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleAddToFavorites(report.id)}
                  className="text-yellow-600 hover:text-yellow-900"
                  title="Add to Favorites"
                >
                  <Star className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(report.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'templates':
        return [
          {
            key: 'template_name',
            label: 'Template Name',
            render: (template) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-5 h-5 text-primary-600" />
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
            key: 'description',
            label: 'Description',
            render: (template) => (
              <div className="max-w-xs">
                <p className="text-sm text-gray-900 truncate">{template.description || '-'}</p>
              </div>
            ),
          },
          {
            key: 'usage_count',
            label: 'Usage',
            render: (template) => (
              <div className="text-center">
                <p className="font-medium text-gray-900">{template.usage_count || 0}</p>
                <p className="text-sm text-gray-500">times used</p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (template) => (
              <div className="flex items-center space-x-2">
                {template.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {template.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (template) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/reporting/templates/${template.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/reporting/templates/${template.id}/edit`}
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
      case 'schedules':
        return [
          {
            key: 'schedule_name',
            label: 'Schedule',
            render: (schedule) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{schedule.schedule_name}</p>
                  <p className="text-sm text-gray-500">{schedule.report?.report_name}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'frequency',
            label: 'Frequency',
            render: (schedule) => (
              <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                {schedule.frequency}
              </span>
            ),
          },
          {
            key: 'next_run',
            label: 'Next Run',
            render: (schedule) => (
              <div>
                <p className="font-medium text-gray-900">
                  {schedule.next_run ? new Date(schedule.next_run).toLocaleDateString() : '-'}
                </p>
                <p className="text-sm text-gray-500">
                  {schedule.last_run ? `Last: ${new Date(schedule.last_run).toLocaleDateString()}` : 'Never run'}
                </p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (schedule) => (
              <div className="flex items-center space-x-2">
                {schedule.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {schedule.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (schedule) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/reporting/schedules/${schedule.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/reporting/schedules/${schedule.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                {schedule.is_active ? (
                  <button
                    onClick={() => {/* Handle pause */}}
                    className="text-warning-600 hover:text-warning-900"
                    title="Pause Schedule"
                  >
                    <Pause className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => {/* Handle resume */}}
                    className="text-success-600 hover:text-success-900"
                    title="Resume Schedule"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="text-danger-600 hover:text-danger-900"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ];
      case 'categories':
        return [
          {
            key: 'category_name',
            label: 'Category',
            render: (category) => (
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{category.category_name}</p>
                  <p className="text-sm text-gray-500">{category.category_code}</p>
                </div>
              </div>
            ),
          },
          {
            key: 'description',
            label: 'Description',
            render: (category) => (
              <div className="max-w-xs">
                <p className="text-sm text-gray-900 truncate">{category.description || '-'}</p>
              </div>
            ),
          },
          {
            key: 'report_count',
            label: 'Reports',
            render: (category) => (
              <div className="text-center">
                <p className="font-medium text-gray-900">{category.report_count || 0}</p>
                <p className="text-sm text-gray-500">reports</p>
              </div>
            ),
          },
          {
            key: 'is_active',
            label: 'Status',
            render: (category) => (
              <div className="flex items-center space-x-2">
                {category.is_active ? (
                  <CheckCircle className="w-4 h-4 text-success-500" />
                ) : (
                  <XCircle className="w-4 h-4 text-danger-500" />
                )}
                <span className="text-sm text-gray-900">
                  {category.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ),
          },
          {
            key: 'actions',
            label: 'Actions',
            render: (category) => (
              <div className="flex items-center space-x-2">
                <Link
                  to={`/reporting/categories/${category.id}`}
                  className="text-primary-600 hover:text-primary-900"
                >
                  <Eye className="w-4 h-4" />
                </Link>
                <Link
                  to={`/reporting/categories/${category.id}/edit`}
                  className="text-secondary-600 hover:text-secondary-900"
                >
                  <Edit className="w-4 h-4" />
                </Link>
                <button
                  onClick={() => handleDelete(category.id)}
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
        <LoadingSpinner size="lg" text="Loading reporting data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Reporting</h1>
          <p className="text-gray-600">Create, manage, and schedule custom reports</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Upload className="w-4 h-4" />
            <span>Import</span>
          </Button>
          <Link to="/reporting/custom-reports/new">
            <Button className="flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>New Report</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'custom-reports', name: 'Custom Reports', icon: BarChart3 },
              { id: 'templates', name: 'Templates', icon: FileText },
              { id: 'schedules', name: 'Schedules', icon: Clock },
              { id: 'categories', name: 'Categories', icon: Target },
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
                </select>
              </div>
              
              <div>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Categories</option>
                  <option value="financial">Financial</option>
                  <option value="operational">Operational</option>
                  <option value="analytical">Analytical</option>
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

export default AdvancedReporting;