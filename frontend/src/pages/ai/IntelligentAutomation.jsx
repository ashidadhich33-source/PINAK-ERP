import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { aiService } from '../../services/aiService';
import { workflowService } from '../../services/workflowService';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Alert from '../../components/common/Alert';
import ChartContainer from '../../components/charts/ChartContainer';
import { 
  Brain, 
  Zap, 
  Settings,
  Play,
  Pause,
  Stop,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  Edit,
  Eye,
  EyeOff,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Activity,
  Target,
  TrendingUp,
  Clock,
  BarChart3,
  PieChart,
  Users,
  Package,
  ShoppingCart
} from 'lucide-react';

const IntelligentAutomation = () => {
  const { addNotification } = useApp();
  const [automation, setAutomation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [showSettings, setShowSettings] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000);

  useEffect(() => {
    loadAutomationData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadAutomationData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadAutomationData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [workflows, aiModels, automationMetrics, performanceData] = await Promise.all([
        workflowService.getWorkflows({ category: selectedCategory, status: selectedStatus }),
        aiService.getAIModels({ category: selectedCategory }),
        aiService.getAIPerformanceMetrics({ category: selectedCategory }),
        aiService.getAIAnalytics({ category: selectedCategory })
      ]);
      
      setAutomation({
        workflows,
        aiModels,
        automationMetrics,
        performanceData
      });
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

  const handleWorkflowAction = async (workflowId, action) => {
    try {
      if (action === 'start') {
        await workflowService.startWorkflowInstance(workflowId, {});
      } else if (action === 'pause') {
        await workflowService.toggleWorkflowStatus(workflowId, false);
      } else if (action === 'resume') {
        await workflowService.toggleWorkflowStatus(workflowId, true);
      } else if (action === 'stop') {
        await workflowService.toggleWorkflowStatus(workflowId, false);
      }
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Workflow ${action} successfully`,
      });
      
      loadAutomationData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleModelAction = async (modelId, action) => {
    try {
      if (action === 'train') {
        await aiService.trainModel('automation', {}, { model_id: modelId });
      } else if (action === 'update') {
        await aiService.updateModel(modelId, {});
      } else if (action === 'delete') {
        await aiService.deleteModel(modelId);
      }
      
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Model ${action} successfully`,
      });
      
      loadAutomationData();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleExportData = async (dataType, format = 'csv') => {
    try {
      await aiService.exportAIData(dataType, format, {
        category: selectedCategory,
        status: selectedStatus
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: `${dataType} data will be downloaded shortly`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return Play;
      case 'paused':
        return Pause;
      case 'stopped':
        return Stop;
      case 'error':
        return XCircle;
      default:
        return Activity;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'text-success-600 bg-success-100';
      case 'paused':
        return 'text-warning-600 bg-warning-100';
      case 'stopped':
        return 'text-gray-600 bg-gray-100';
      case 'error':
        return 'text-danger-600 bg-danger-100';
      default:
        return 'text-primary-600 bg-primary-100';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'sales':
        return ShoppingCart;
      case 'inventory':
        return Package;
      case 'customers':
        return Users;
      case 'finance':
        return BarChart3;
      case 'operations':
        return Settings;
      default:
        return Brain;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading automation data..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
            <Brain className="w-6 h-6 text-primary-600" />
            <span>Intelligent Automation</span>
          </h1>
          <p className="text-gray-600">AI-driven workflows and intelligent automation</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </div>
          <Button
            variant="outline"
            onClick={loadAutomationData}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={() => handleExportData('automation')}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export</span>
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert type="danger" title="Error">
          {error}
        </Alert>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Filters</h3>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <Settings className="w-4 h-4" />
            <span>{showSettings ? 'Hide' : 'Show'} Settings</span>
          </button>
        </div>
        
        {showSettings && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="form-label">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-input"
              >
                <option value="all">All Categories</option>
                <option value="sales">Sales</option>
                <option value="inventory">Inventory</option>
                <option value="customers">Customers</option>
                <option value="finance">Finance</option>
                <option value="operations">Operations</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="form-input"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="stopped">Stopped</option>
                <option value="error">Error</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Refresh Interval</label>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                className="form-input"
              >
                <option value="10000">10 seconds</option>
                <option value="30000">30 seconds</option>
                <option value="60000">1 minute</option>
                <option value="300000">5 minutes</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Automation Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Active Workflows</p>
              <p className="text-2xl font-semibold text-gray-900">
                {automation?.workflows?.active_count || 0}
              </p>
              <p className="text-sm text-primary-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{automation?.workflows?.new_today || 0} today
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-md flex items-center justify-center">
                <Zap className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">AI Models</p>
              <p className="text-2xl font-semibold text-gray-900">
                {automation?.aiModels?.total || 0}
              </p>
              <p className="text-sm text-success-600">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                {automation?.aiModels?.active_count || 0} active
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-md flex items-center justify-center">
                <Activity className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Automation Rate</p>
              <p className="text-2xl font-semibold text-gray-900">
                {automation?.automationMetrics?.automation_rate || 0}%
              </p>
              <p className="text-sm text-warning-600">
                <Target className="w-4 h-4 inline mr-1" />
                Efficiency
              </p>
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
              <p className="text-sm font-medium text-gray-500">Avg. Processing</p>
              <p className="text-2xl font-semibold text-gray-900">
                {automation?.automationMetrics?.avg_processing_time || 0}ms
              </p>
              <p className="text-sm text-secondary-600">
                <TrendingDown className="w-4 h-4 inline mr-1" />
                Fast processing
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Active Workflows</h3>
          <p className="text-sm text-gray-500">AI-driven automation workflows</p>
        </div>
        
        <div className="p-6">
          {automation?.workflows?.workflows?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No workflows found</p>
              <p className="text-sm">Create your first intelligent workflow</p>
            </div>
          ) : (
            <div className="space-y-4">
              {automation?.workflows?.workflows?.map((workflow, index) => {
                const StatusIcon = getStatusIcon(workflow.status);
                const CategoryIcon = getCategoryIcon(workflow.category);
                
                return (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        getStatusColor(workflow.status)
                      }`}>
                        <StatusIcon className="w-5 h-5" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{workflow.name}</h4>
                            <p className="text-sm text-gray-600 mt-1">{workflow.description}</p>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              getStatusColor(workflow.status)
                            }`}>
                              {workflow.status}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(workflow.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        
                        <div className="mt-3 flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <div className="flex items-center space-x-1">
                              <CategoryIcon className="w-4 h-4" />
                              <span>{workflow.category}</span>
                            </div>
                            <span>Steps: {workflow.steps_count}</span>
                            <span>Success Rate: {workflow.success_rate}%</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            {workflow.status === 'active' ? (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleWorkflowAction(workflow.id, 'pause')}
                                className="text-warning-600 hover:text-warning-900"
                              >
                                <Pause className="w-4 h-4 mr-1" />
                                Pause
                              </Button>
                            ) : (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleWorkflowAction(workflow.id, 'resume')}
                                className="text-success-600 hover:text-success-900"
                              >
                                <Play className="w-4 h-4 mr-1" />
                                Resume
                              </Button>
                            )}
                            
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleWorkflowAction(workflow.id, 'stop')}
                              className="text-danger-600 hover:text-danger-900"
                            >
                              <Stop className="w-4 h-4 mr-1" />
                              Stop
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* AI Models */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">AI Models</h3>
          <p className="text-sm text-gray-500">Machine learning models for automation</p>
        </div>
        
        <div className="p-6">
          {automation?.aiModels?.models?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No AI models found</p>
              <p className="text-sm">Train your first AI model</p>
            </div>
          ) : (
            <div className="space-y-4">
              {automation?.aiModels?.models?.map((model, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                      <Brain className="w-5 h-5 text-primary-600" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{model.name}</h4>
                          <p className="text-sm text-gray-600 mt-1">{model.description}</p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            model.status === 'active' ? 'bg-success-100 text-success-800' :
                            model.status === 'training' ? 'bg-warning-100 text-warning-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {model.status}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(model.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Type: {model.type}</span>
                          <span>Accuracy: {model.accuracy}%</span>
                          <span>Version: {model.version}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleModelAction(model.id, 'train')}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            Train
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleModelAction(model.id, 'update')}
                            className="text-warning-600 hover:text-warning-900"
                          >
                            <Edit className="w-4 h-4 mr-1" />
                            Update
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleModelAction(model.id, 'delete')}
                            className="text-danger-600 hover:text-danger-900"
                          >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Target className="w-8 h-8 text-primary-600" />
            </div>
            <h4 className="font-medium text-gray-900">Automation Rate</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {automation?.automationMetrics?.automation_rate || 0}%
            </p>
            <p className="text-sm text-gray-500">Tasks automated</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Zap className="w-8 h-8 text-success-600" />
            </div>
            <h4 className="font-medium text-gray-900">Processing Speed</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {automation?.automationMetrics?.avg_processing_time || 0}ms
            </p>
            <p className="text-sm text-gray-500">Average processing time</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Activity className="w-8 h-8 text-warning-600" />
            </div>
            <h4 className="font-medium text-gray-900">Success Rate</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {automation?.automationMetrics?.success_rate || 0}%
            </p>
            <p className="text-sm text-gray-500">Successful executions</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligentAutomation;