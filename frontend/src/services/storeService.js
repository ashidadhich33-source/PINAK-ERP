import { apiService } from './apiService';

export const storeService = {
  // Store Management
  getStores: async () => {
    try {
      const stores = await apiService.get('/api/store/stores');
      return stores;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stores');
    }
  },

  getStore: async (storeId) => {
    try {
      const store = await apiService.get(`/api/store/stores/${storeId}`);
      return store;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store');
    }
  },

  createStore: async (storeData) => {
    try {
      const result = await apiService.post('/api/store/stores', storeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create store');
    }
  },

  updateStore: async (storeId, storeData) => {
    try {
      const result = await apiService.put(`/api/store/stores/${storeId}`, storeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update store');
    }
  },

  deleteStore: async (storeId) => {
    try {
      const result = await apiService.delete(`/api/store/stores/${storeId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete store');
    }
  },

  // Store Hierarchy
  getStoreHierarchy: async () => {
    try {
      const hierarchy = await apiService.get('/api/store/hierarchy');
      return hierarchy;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store hierarchy');
    }
  },

  updateStoreHierarchy: async (hierarchyData) => {
    try {
      const result = await apiService.put('/api/store/hierarchy', hierarchyData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update store hierarchy');
    }
  },

  // Store Settings
  getStoreSettings: async (storeId) => {
    try {
      const settings = await apiService.get(`/api/store/stores/${storeId}/settings`);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store settings');
    }
  },

  updateStoreSettings: async (storeId, settingsData) => {
    try {
      const result = await apiService.put(`/api/store/stores/${storeId}/settings`, settingsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update store settings');
    }
  },

  // Store Analytics
  getStoreAnalytics: async (storeId, params = {}) => {
    try {
      const analytics = await apiService.get(`/api/store/stores/${storeId}/analytics`, params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store analytics');
    }
  },

  getStorePerformance: async (storeId, params = {}) => {
    try {
      const performance = await apiService.get(`/api/store/stores/${storeId}/performance`, params);
      return performance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store performance');
    }
  },

  // POS Sessions
  getPOSSessions: async () => {
    try {
      const sessions = await apiService.get('/api/store/pos/sessions');
      return sessions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS sessions');
    }
  },

  getPOSSession: async (sessionId) => {
    try {
      const session = await apiService.get(`/api/store/pos/sessions/${sessionId}`);
      return session;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS session');
    }
  },

  createPOSSession: async (sessionData) => {
    try {
      const result = await apiService.post('/api/store/pos/sessions', sessionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create POS session');
    }
  },

  updatePOSSession: async (sessionId, sessionData) => {
    try {
      const result = await apiService.put(`/api/store/pos/sessions/${sessionId}`, sessionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update POS session');
    }
  },

  deletePOSSession: async (sessionId) => {
    try {
      const result = await apiService.delete(`/api/store/pos/sessions/${sessionId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete POS session');
    }
  },

  closePOSSession: async (sessionId) => {
    try {
      const result = await apiService.post(`/api/store/pos/sessions/${sessionId}/close`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to close POS session');
    }
  },

  // Session Reports
  getSessionReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/store/pos/sessions/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch session reports');
    }
  },

  getSessionAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/store/pos/sessions/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch session analytics');
    }
  },

  // Session Security
  getSessionSecurity: async () => {
    try {
      const security = await apiService.get('/api/store/pos/sessions/security');
      return security;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch session security');
    }
  },

  updateSessionSecurity: async (securityData) => {
    try {
      const result = await apiService.put('/api/store/pos/sessions/security', securityData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update session security');
    }
  },

  // Receipt Templates
  getReceiptTemplates: async () => {
    try {
      const templates = await apiService.get('/api/store/pos/receipts/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch receipt templates');
    }
  },

  getReceiptTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/store/pos/receipts/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch receipt template');
    }
  },

  createReceiptTemplate: async (templateData) => {
    try {
      const result = await apiService.post('/api/store/pos/receipts/templates', templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create receipt template');
    }
  },

  updateReceiptTemplate: async (templateId, templateData) => {
    try {
      const result = await apiService.put(`/api/store/pos/receipts/templates/${templateId}`, templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update receipt template');
    }
  },

  deleteReceiptTemplate: async (templateId) => {
    try {
      const result = await apiService.delete(`/api/store/pos/receipts/templates/${templateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete receipt template');
    }
  },

  // Receipts
  getReceipts: async () => {
    try {
      const receipts = await apiService.get('/api/store/pos/receipts');
      return receipts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch receipts');
    }
  },

  getReceipt: async (receiptId) => {
    try {
      const receipt = await apiService.get(`/api/store/pos/receipts/${receiptId}`);
      return receipt;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch receipt');
    }
  },

  createReceipt: async (receiptData) => {
    try {
      const result = await apiService.post('/api/store/pos/receipts', receiptData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create receipt');
    }
  },

  updateReceipt: async (receiptId, receiptData) => {
    try {
      const result = await apiService.put(`/api/store/pos/receipts/${receiptId}`, receiptData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update receipt');
    }
  },

  deleteReceipt: async (receiptId) => {
    try {
      const result = await apiService.delete(`/api/store/pos/receipts/${receiptId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete receipt');
    }
  },

  // Receipt Printing
  printReceipt: async (receiptId) => {
    try {
      const result = await apiService.post(`/api/store/pos/receipts/${receiptId}/print`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to print receipt');
    }
  },

  sendReceipt: async (receiptId) => {
    try {
      const result = await apiService.post(`/api/store/pos/receipts/${receiptId}/send`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send receipt');
    }
  },

  // Receipt Analytics
  getReceiptAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/store/pos/receipts/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch receipt analytics');
    }
  },

  // POS Analytics
  getPOSAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/store/pos/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS analytics');
    }
  },

  getSalesAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/store/pos/analytics/sales', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales analytics');
    }
  },

  getPerformanceMetrics: async (params = {}) => {
    try {
      const metrics = await apiService.get('/api/store/pos/analytics/performance', params);
      return metrics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch performance metrics');
    }
  },

  getTrendAnalysis: async (params = {}) => {
    try {
      const trends = await apiService.get('/api/store/pos/analytics/trends', params);
      return trends;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trend analysis');
    }
  },

  getComparativeAnalysis: async (params = {}) => {
    try {
      const comparison = await apiService.get('/api/store/pos/analytics/comparison', params);
      return comparison;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch comparative analysis');
    }
  },

  // Store Reports
  getStoreReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/store/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch store reports');
    }
  },

  exportStoreReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/store/reports/export/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export store report');
    }
  },

  // Store Validation
  validateStore: async (storeData) => {
    try {
      const result = await apiService.post('/api/store/validate', storeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate store');
    }
  },

  validatePOSSession: async (sessionData) => {
    try {
      const result = await apiService.post('/api/store/pos/sessions/validate', sessionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate POS session');
    }
  }
};