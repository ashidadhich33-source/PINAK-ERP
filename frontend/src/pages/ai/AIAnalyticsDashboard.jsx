import React, { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { aiService } from '../../services/aiService';
import ChartContainer from '../../components/charts/ChartContainer';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Alert from '../../components/common/Alert';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown,
  Target,
  Zap,
  BarChart3,
  PieChart,
  Activity,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Download,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react';

const AIAnalyticsDashboard = () => {
  const { addNotification } = useApp();
  const [aiData, setAiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [showInsights, setShowInsights] = useState(true);

  useEffect(() => {
    loadAIData();
  }, [selectedPeriod]);

  const loadAIData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [predictiveAnalytics, salesForecast, inventoryPredictions, businessInsights] = await Promise.all([
        aiService.getPredictiveAnalytics({ period: selectedPeriod }),
        aiService.getSalesForecast(selectedPeriod),
        aiService.getInventoryPredictions({ period: selectedPeriod }),
        aiService.getBusinessInsights({ period: selectedPeriod })
      ]);
      
      setAiData({
        predictiveAnalytics,
        salesForecast,
        inventoryPredictions,
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

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAIData();
    setRefreshing(false);
  };

  const handleExportReport = async (reportType) => {
    try {
      await aiService.generateAIReport(reportType, { period: selectedPeriod });
      addNotification({
        type: 'success',
        title: 'Report Generated',
        message: `${reportType} report will be downloaded shortly`,
      });
    } catch (err) {
      addNotification({
        type: 'danger',
        title: 'Error',
        message: err.message,
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading AI analytics..." />
      </div>
    );
  }

  // Sales forecast chart data
  const salesForecastData = {
    labels: aiData?.salesForecast?.labels || [],
    datasets: [
      {
        label: 'Historical Sales',
        data: aiData?.salesForecast?.historical || [],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'AI Forecast',
        data: aiData?.salesForecast?.forecast || [],
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.4,
        borderDash: [5, 5],
        fill: false,
      },
    ],
  };

  // Inventory predictions chart data
  const inventoryPredictionsData = {
    labels: aiData?.inventoryPredictions?.labels || [],
    datasets: [
      {
        label: 'Current Stock',
        data: aiData?.inventoryPredictions?.current_stock || [],
        backgroundColor: '#3b82f6',
        borderColor: '#3b82f6',
        borderWidth: 1,
      },
      {
        label: 'Predicted Demand',
        data: aiData?.inventoryPredictions?.predicted_demand || [],
        backgroundColor: '#f59e0b',
        borderColor: '#f59e0b',
        borderWidth: 1,
      },
    ],
  };

  // Business insights chart data
  const businessInsightsData = {
    labels: aiData?.businessInsights?.labels || [],
    datasets: [
      {
        label: 'Performance Score',
        data: aiData?.businessInsights?.performance_scores || [],
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
            <Brain className="w-6 h-6 text-primary-600" />
            <span>AI Analytics Dashboard</span>
          </h1>
          <p className="text-gray-600">Intelligent insights powered by artificial intelligence</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="form-input"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button
            variant="outline"
            onClick={handleRefresh}
            loading={refreshing}
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

      {/* AI Insights Toggle */}
      <div className="flex items-center justify-between bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-3">
          <Brain className="w-5 h-5 text-primary-600" />
          <span className="font-medium text-gray-900">AI Insights</span>
        </div>
        <button
          onClick={() => setShowInsights(!showInsights)}
          className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900"
        >
          {showInsights ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          <span>{showInsights ? 'Hide' : 'Show'} Insights</span>
        </button>
      </div>

      {/* AI Insights */}
      {showInsights && aiData?.businessInsights?.insights && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {aiData.businessInsights.insights.map((insight, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-4">
              <div className="flex items-start space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  insight.type === 'positive' ? 'bg-success-100' :
                  insight.type === 'warning' ? 'bg-warning-100' :
                  'bg-danger-100'
                }`}>
                  {insight.type === 'positive' ? (
                    <CheckCircle className="w-4 h-4 text-success-600" />
                  ) : insight.type === 'warning' ? (
                    <AlertTriangle className="w-4 h-4 text-warning-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-danger-600" />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{insight.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      insight.type === 'positive' ? 'bg-success-100 text-success-800' :
                      insight.type === 'warning' ? 'bg-warning-100 text-warning-800' :
                      'bg-danger-100 text-danger-800'
                    }`}>
                      {insight.type === 'positive' ? 'Positive' :
                       insight.type === 'warning' ? 'Warning' : 'Critical'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Key AI Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-md flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">AI Accuracy</p>
              <p className="text-2xl font-semibold text-gray-900">
                {aiData?.predictiveAnalytics?.accuracy || 0}%
              </p>
              <p className="text-sm text-success-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                +{aiData?.predictiveAnalytics?.accuracy_improvement || 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-success-100 rounded-md flex items-center justify-center">
                <Target className="w-5 h-5 text-success-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Prediction Confidence</p>
              <p className="text-2xl font-semibold text-gray-900">
                {aiData?.predictiveAnalytics?.confidence || 0}%
              </p>
              <p className="text-sm text-success-600">
                <CheckCircle className="w-4 h-4 inline mr-1" />
                High confidence
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-warning-100 rounded-md flex items-center justify-center">
                <Zap className="w-5 h-5 text-warning-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">AI Recommendations</p>
              <p className="text-2xl font-semibold text-gray-900">
                {aiData?.businessInsights?.recommendations_count || 0}
              </p>
              <p className="text-sm text-warning-600">
                <Activity className="w-4 h-4 inline mr-1" />
                Active insights
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-secondary-100 rounded-md flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-secondary-600" />
              </div>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-500">Model Performance</p>
              <p className="text-2xl font-semibold text-gray-900">
                {aiData?.predictiveAnalytics?.model_performance || 0}%
              </p>
              <p className="text-sm text-secondary-600">
                <TrendingUp className="w-4 h-4 inline mr-1" />
                Optimized
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Forecast */}
        <ChartContainer
          type="line"
          data={salesForecastData}
          title="AI Sales Forecast"
          subtitle="Historical data vs AI predictions"
          className="lg:col-span-2"
        />

        {/* Inventory Predictions */}
        <ChartContainer
          type="bar"
          data={inventoryPredictionsData}
          title="Inventory Predictions"
          subtitle="AI-powered demand forecasting"
        />

        {/* Business Insights */}
        <ChartContainer
          type="line"
          data={businessInsightsData}
          title="Business Performance"
          subtitle="AI-analyzed performance metrics"
        />
      </div>

      {/* AI Recommendations */}
      {aiData?.businessInsights?.recommendations && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">AI Recommendations</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleExportReport('recommendations')}
              className="flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </Button>
          </div>
          
          <div className="space-y-4">
            {aiData.businessInsights.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <Brain className="w-4 h-4 text-primary-600" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{recommendation.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
                  <div className="mt-2 flex items-center space-x-4">
                    <span className="text-sm text-gray-500">
                      Confidence: {recommendation.confidence}%
                    </span>
                    <span className="text-sm text-gray-500">
                      Impact: {recommendation.impact}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="outline">
                    Apply
                  </Button>
                  <Button size="sm" variant="outline">
                    Dismiss
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Model Performance */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Model Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Target className="w-8 h-8 text-primary-600" />
            </div>
            <h4 className="font-medium text-gray-900">Accuracy</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {aiData?.predictiveAnalytics?.accuracy || 0}%
            </p>
            <p className="text-sm text-gray-500">Prediction accuracy</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Zap className="w-8 h-8 text-success-600" />
            </div>
            <h4 className="font-medium text-gray-900">Speed</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {aiData?.predictiveAnalytics?.processing_time || 0}ms
            </p>
            <p className="text-sm text-gray-500">Average processing time</p>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Activity className="w-8 h-8 text-warning-600" />
            </div>
            <h4 className="font-medium text-gray-900">Uptime</h4>
            <p className="text-2xl font-semibold text-gray-900">
              {aiData?.predictiveAnalytics?.uptime || 0}%
            </p>
            <p className="text-sm text-gray-500">Service availability</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAnalyticsDashboard;