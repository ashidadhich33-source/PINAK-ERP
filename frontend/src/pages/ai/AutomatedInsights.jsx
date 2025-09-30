import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { aiService } from '../../services/aiService';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Alert from '../../components/common/Alert';
import ChartContainer from '../../components/charts/ChartContainer';
import { 
  Brain, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  TrendingUp, 
  TrendingDown,
  Activity,
  Zap,
  Target,
  BarChart3,
  PieChart,
  RefreshCw,
  Download,
  Filter,
  Eye,
  EyeOff,
  Settings,
  Bell,
  Clock,
  Star
} from 'lucide-react';

const AutomatedInsights = () => {
  const { addNotification } = useApp();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  useEffect(() => {
    loadInsights();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadInsights, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [automatedInsights, anomalyDetection, businessInsights] = await Promise.all([
        aiService.getAutomatedInsights({ category: selectedCategory, severity: selectedSeverity }),
        aiService.getAnomalyDetection('all', { category: selectedCategory }),
        aiService.getBusinessInsights({ category: selectedCategory })
      ]);
      
      setInsights({
        automatedInsights,
        anomalyDetection,
        businessInsights
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

  const handleInsightAction = async (insightId, action) => {
    try {
      // Handle insight action (acknowledge, dismiss, etc.)
      addNotification({
        type: 'success',
        title: 'Success',
        message: `Insight ${action} successfully`,
      });
      
      // Reload insights
      loadInsights();
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const handleExportInsights = async (format = 'csv') => {
    try {
      await aiService.exportAIData('insights', format, {
        category: selectedCategory,
        severity: selectedSeverity
      });
      addNotification({
        type: 'success',
        title: 'Export Started',
        message: 'Insights will be downloaded shortly',
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return XCircle;
      case 'high':
        return AlertTriangle;
      case 'medium':
        return Activity;
      case 'low':
        return CheckCircle;
      default:
        return Bell;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'text-danger-600 bg-danger-100';
      case 'high':
        return 'text-warning-600 bg-warning-100';
      case 'medium':
        return 'text-info-600 bg-info-100';
      case 'low':
        return 'text-success-600 bg-success-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'sales':
        return TrendingUp;
      case 'inventory':
        return BarChart3;
      case 'customers':
        return Target;
      case 'finance':
        return PieChart;
      default:
        return Brain;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading automated insights..." />
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
            <span>Automated Insights</span>
          </h1>
          <p className="text-gray-600">AI-powered insights and anomaly detection</p>
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
            onClick={loadInsights}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </Button>
          <Button
            onClick={() => handleExportInsights()}
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
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
          >
            <Filter className="w-4 h-4" />
            <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
          </button>
        </div>
        
        {showFilters && (
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
              <label className="form-label">Severity</label>
              <select
                value={selectedSeverity}
                onChange={(e) => setSelectedSeverity(e.target.value)}
                className="form-input"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
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

      {/* Insights Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <Brain className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Total Insights</p>
              <p className="text-2xl font-semibold text-gray-900">
                {insights?.automatedInsights?.total || 0}
              </p>
              <p className="text-sm text-primary-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{insights?.automatedInsights?.new_today || 0} today
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-danger-100 rounded-md flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-danger-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Critical Alerts</p>
              <p className="text-2xl font-semibold text-gray-900">
                {insights?.anomalyDetection?.critical_count || 0}
              </p>
              <p className="text-sm text-danger-600">
                <AlertTriangle className="w-4 h-4 inline mr-1" />
                Requires attention
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-md flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Resolved</p>
              <p className="text-2xl font-semibold text-gray-900">
                {insights?.automatedInsights?.resolved || 0}
              </p>
              <p className="text-sm text-success-600">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                This week
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
              <p className="text-sm font-medium text-gray-500">Accuracy</p>
              <p className="text-2xl font-semibold text-gray-900">
                {insights?.automatedInsights?.accuracy || 0}%
              </p>
              <p className="text-sm text-warning-600">
                <Target className="w-4 h-4 inline mr-1" />
                AI confidence
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Automated Insights */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Automated Insights</h3>
          <p className="text-sm text-gray-500">AI-generated insights and recommendations</p>
        </div>
        
        <div className="p-6">
          {insights?.automatedInsights?.insights?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No insights available</p>
              <p className="text-sm">AI is analyzing your data...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {insights?.automatedInsights?.insights?.map((insight, index) => {
                const SeverityIcon = getSeverityIcon(insight.severity);
                const CategoryIcon = getCategoryIcon(insight.category);
                
                return (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        getSeverityColor(insight.severity)
                      }`}>
                        <SeverityIcon className="w-5 h-5" />
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{insight.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              getSeverityColor(insight.severity)
                            }`}>
                              {insight.severity}
                            </span>
                            <span className="text-xs text-gray-500">
                              {new Date(insight.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        
                        <div className="mt-3 flex items-center justify-between">
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <div className="flex items-center space-x-1">
                              <CategoryIcon className="w-4 h-4" />
                              <span>{insight.category}</span>
                            </div>
                            <span>Confidence: {insight.confidence}%</span>
                            <span>Impact: {insight.impact}</span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleInsightAction(insight.id, 'acknowledge')}
                              className="text-success-600 hover:text-success-900"
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Acknowledge
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleInsightAction(insight.id, 'dismiss')}
                              className="text-danger-600 hover:text-danger-900"
                            >
                              <XCircle className="w-4 h-4 mr-1" />
                              Dismiss
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

      {/* Anomaly Detection */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Anomaly Detection</h3>
          <p className="text-sm text-gray-500">Unusual patterns detected by AI</p>
        </div>
        
        <div className="p-6">
          {insights?.anomalyDetection?.anomalies?.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-success-500" />
              <p>No anomalies detected</p>
              <p className="text-sm">Your data looks normal</p>
            </div>
          ) : (
            <div className="space-y-4">
              {insights?.anomalyDetection?.anomalies?.map((anomaly, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 bg-warning-100 rounded-full flex items-center justify-center">
                      <AlertTriangle className="w-5 h-5 text-warning-600" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{anomaly.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{anomaly.description}</p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-gray-500">
                            {new Date(anomaly.detected_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                      
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Type: {anomaly.type}</span>
                          <span>Severity: {anomaly.severity}</span>
                          <span>Confidence: {anomaly.confidence}%</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleInsightAction(anomaly.id, 'investigate')}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <Eye className="w-4 h-4 mr-1" />
                            Investigate
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleInsightAction(anomaly.id, 'dismiss')}
                            className="text-danger-600 hover:text-danger-900"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Dismiss
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

      {/* AI Performance Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Target className="w-8 h-8 text-primary-600" />
            </div>
            <h4 className="font-medium text-gray-900">Accuracy</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {insights?.automatedInsights?.accuracy || 0}%
            </p>
            <p className="text-sm text-gray-500">Prediction accuracy</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Zap className="w-8 h-8 text-success-600" />
            </div>
            <h4 className="font-medium text-gray-900">Response Time</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {insights?.automatedInsights?.response_time || 0}ms
            </p>
            <p className="text-sm text-gray-500">Average processing time</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Activity className="w-8 h-8 text-warning-600" />
            </div>
            <h4 className="font-medium text-gray-900">Uptime</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {insights?.automatedInsights?.uptime || 0}%
            </p>
            <p className="text-sm text-gray-500">Service availability</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomatedInsights;