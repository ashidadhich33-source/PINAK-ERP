import { apiService } from './apiService';

export const aiService = {
  // Predictive Analytics
  getPredictiveAnalytics: async (options = {}) => {
    try {
      const analytics = await apiService.get('/api/ai/predictive-analytics', options);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch predictive analytics');
    }
  },

  // Sales Forecasting
  getSalesForecast: async (period = '30d', options = {}) => {
    try {
      const forecast = await apiService.get('/api/ai/sales-forecast', {
        period,
        ...options
      });
      return forecast;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales forecast');
    }
  },

  // Inventory Predictions
  getInventoryPredictions: async (options = {}) => {
    try {
      const predictions = await apiService.get('/api/ai/inventory-predictions', options);
      return predictions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch inventory predictions');
    }
  },

  // Customer Behavior Analysis
  getCustomerBehaviorAnalysis: async (customerId = null, options = {}) => {
    try {
      const analysis = await apiService.get('/api/ai/customer-behavior', {
        customer_id: customerId,
        ...options
      });
      return analysis;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer behavior analysis');
    }
  },

  // Demand Forecasting
  getDemandForecast: async (productId = null, options = {}) => {
    try {
      const forecast = await apiService.get('/api/ai/demand-forecast', {
        product_id: productId,
        ...options
      });
      return forecast;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch demand forecast');
    }
  },

  // Price Optimization
  getPriceOptimization: async (productId, options = {}) => {
    try {
      const optimization = await apiService.get(`/api/ai/price-optimization/${productId}`, options);
      return optimization;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch price optimization');
    }
  },

  // Anomaly Detection
  getAnomalyDetection: async (module, options = {}) => {
    try {
      const anomalies = await apiService.get('/api/ai/anomaly-detection', {
        module,
        ...options
      });
      return anomalies;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch anomaly detection');
    }
  },

  // Smart Recommendations
  getSmartRecommendations: async (type, options = {}) => {
    try {
      const recommendations = await apiService.get('/api/ai/recommendations', {
        type,
        ...options
      });
      return recommendations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch smart recommendations');
    }
  },

  // Product Recommendations
  getProductRecommendations: async (customerId = null, options = {}) => {
    try {
      const recommendations = await apiService.get('/api/ai/product-recommendations', {
        customer_id: customerId,
        ...options
      });
      return recommendations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch product recommendations');
    }
  },

  // Customer Recommendations
  getCustomerRecommendations: async (options = {}) => {
    try {
      const recommendations = await apiService.get('/api/ai/customer-recommendations', options);
      return recommendations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer recommendations');
    }
  },

  // Business Insights
  getBusinessInsights: async (options = {}) => {
    try {
      const insights = await apiService.get('/api/ai/business-insights', options);
      return insights;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch business insights');
    }
  },

  // Automated Insights
  getAutomatedInsights: async (options = {}) => {
    try {
      const insights = await apiService.get('/api/ai/automated-insights', options);
      return insights;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automated insights');
    }
  },

  // AI Chatbot
  sendChatMessage: async (message, context = {}) => {
    try {
      const response = await apiService.post('/api/ai/chat', {
        message,
        context
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to send chat message');
    }
  },

  // Get Chat History
  getChatHistory: async (options = {}) => {
    try {
      const history = await apiService.get('/api/ai/chat/history', options);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch chat history');
    }
  },

  // Clear Chat History
  clearChatHistory: async () => {
    try {
      await apiService.delete('/api/ai/chat/history');
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to clear chat history');
    }
  },

  // AI Model Training
  trainModel: async (modelType, data, options = {}) => {
    try {
      const result = await apiService.post('/api/ai/train-model', {
        model_type: modelType,
        data,
        ...options
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to train AI model');
    }
  },

  // Get Model Performance
  getModelPerformance: async (modelId) => {
    try {
      const performance = await apiService.get(`/api/ai/models/${modelId}/performance`);
      return performance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch model performance');
    }
  },

  // Update Model
  updateModel: async (modelId, data) => {
    try {
      const result = await apiService.put(`/api/ai/models/${modelId}`, data);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update AI model');
    }
  },

  // Delete Model
  deleteModel: async (modelId) => {
    try {
      await apiService.delete(`/api/ai/models/${modelId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete AI model');
    }
  },

  // Get AI Models
  getAIModels: async (options = {}) => {
    try {
      const models = await apiService.get('/api/ai/models', options);
      return models;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI models');
    }
  },

  // Get AI Analytics
  getAIAnalytics: async (options = {}) => {
    try {
      const analytics = await apiService.get('/api/ai/analytics', options);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI analytics');
    }
  },

  // Get AI Performance Metrics
  getAIPerformanceMetrics: async (options = {}) => {
    try {
      const metrics = await apiService.get('/api/ai/performance-metrics', options);
      return metrics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI performance metrics');
    }
  },

  // Export AI Data
  exportAIData: async (dataType, format = 'csv', options = {}) => {
    try {
      const data = await apiService.get('/api/ai/export', {
        data_type: dataType,
        format,
        ...options
      });
      return data;
    } catch (error) {
      throw new Error(error.message || 'Failed to export AI data');
    }
  },

  // Get AI Insights
  getAIInsights: async (options = {}) => {
    try {
      const insights = await apiService.get('/api/ai/insights', options);
      return insights;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI insights');
    }
  },

  // Generate AI Report
  generateAIReport: async (reportType, options = {}) => {
    try {
      const report = await apiService.post('/api/ai/reports', {
        report_type: reportType,
        ...options
      });
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate AI report');
    }
  },

  // Get AI Recommendations
  getAIRecommendations: async (options = {}) => {
    try {
      const recommendations = await apiService.get('/api/ai/recommendations', options);
      return recommendations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI recommendations');
    }
  },

  // Update AI Recommendations
  updateAIRecommendations: async (recommendationId, feedback) => {
    try {
      const result = await apiService.put(`/api/ai/recommendations/${recommendationId}`, {
        feedback
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update AI recommendations');
    }
  },

  // Get AI Alerts
  getAIAlerts: async (options = {}) => {
    try {
      const alerts = await apiService.get('/api/ai/alerts', options);
      return alerts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI alerts');
    }
  },

  // Mark AI Alert as Read
  markAIAlertAsRead: async (alertId) => {
    try {
      await apiService.patch(`/api/ai/alerts/${alertId}/read`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to mark AI alert as read');
    }
  },

  // Get AI Statistics
  getAIStatistics: async (options = {}) => {
    try {
      const statistics = await apiService.get('/api/ai/statistics', options);
      return statistics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI statistics');
    }
  },

  // Get AI Health
  getAIHealth: async () => {
    try {
      const health = await apiService.get('/api/ai/health');
      return health;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI health');
    }
  },

  // Get AI Configuration
  getAIConfiguration: async () => {
    try {
      const configuration = await apiService.get('/api/ai/configuration');
      return configuration;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch AI configuration');
    }
  },

  // Update AI Configuration
  updateAIConfiguration: async (configuration) => {
    try {
      const result = await apiService.put('/api/ai/configuration', configuration);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update AI configuration');
    }
  },
};