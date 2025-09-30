import { apiService } from './apiService';

export const reportsService = {
  // Get sales reports
  getSalesReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/sales', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales reports');
    }
  },

  // Get inventory reports
  getInventoryReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/inventory', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch inventory reports');
    }
  },

  // Get customer reports
  getCustomerReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/customers', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer reports');
    }
  },

  // Get financial reports
  getFinancialReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/financial', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial reports');
    }
  },

  // Get POS reports
  getPosReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/pos', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS reports');
    }
  },

  // Get dashboard analytics
  getDashboardAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/reports/dashboard', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch dashboard analytics');
    }
  },

  // Get sales trends
  getSalesTrends: async (params = {}) => {
    try {
      const trends = await apiService.get('/api/reports/sales/trends', params);
      return trends;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales trends');
    }
  },

  // Get top products
  getTopProducts: async (params = {}) => {
    try {
      const products = await apiService.get('/api/reports/products/top', params);
      return products;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch top products');
    }
  },

  // Get low stock alerts
  getLowStockAlerts: async (params = {}) => {
    try {
      const alerts = await apiService.get('/api/reports/inventory/low-stock', params);
      return alerts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch low stock alerts');
    }
  },

  // Get customer analytics
  getCustomerAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/reports/customers/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer analytics');
    }
  },

  // Get revenue reports
  getRevenueReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/revenue', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch revenue reports');
    }
  },

  // Get profit reports
  getProfitReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/profit', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit reports');
    }
  },

  // Get tax reports
  getTaxReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/tax', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tax reports');
    }
  },

  // Get GST reports
  getGstReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/gst', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST reports');
    }
  },

  // Get commission reports
  getCommissionReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/commission', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch commission reports');
    }
  },

  // Get loyalty reports
  getLoyaltyReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/loyalty', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty reports');
    }
  },

  // Get WhatsApp reports
  getWhatsappReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/whatsapp', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp reports');
    }
  },

  // Get automation reports
  getAutomationReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/automation', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation reports');
    }
  },

  // Get optimization reports
  getOptimizationReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/optimization', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch optimization reports');
    }
  },

  // Get compliance reports
  getComplianceReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/compliance', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch compliance reports');
    }
  },

  // Get banking reports
  getBankingReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/banking', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking reports');
    }
  },

  // Get purchase reports
  getPurchaseReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/purchase', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase reports');
    }
  },

  // Get testing reports
  getTestingReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/testing', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch testing reports');
    }
  },

  // Export reports
  exportReports: async (reportType, format = 'csv', filters = {}) => {
    try {
      const response = await apiService.get(`/api/reports/${reportType}/export`, {
        format,
        ...filters,
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export reports');
    }
  },

  // Get report templates
  getReportTemplates: async () => {
    try {
      const templates = await apiService.get('/api/reports/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report templates');
    }
  },

  // Create custom report
  createCustomReport: async (reportData) => {
    try {
      const report = await apiService.post('/api/reports/custom', reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to create custom report');
    }
  },

  // Get report by ID
  getReport: async (reportId) => {
    try {
      const report = await apiService.get(`/api/reports/${reportId}`);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report');
    }
  },

  // Update report
  updateReport: async (reportId, reportData) => {
    try {
      const report = await apiService.put(`/api/reports/${reportId}`, reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report');
    }
  },

  // Delete report
  deleteReport: async (reportId) => {
    try {
      await apiService.delete(`/api/reports/${reportId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report');
    }
  },

  // Schedule report
  scheduleReport: async (reportId, scheduleData) => {
    try {
      const schedule = await apiService.post(`/api/reports/${reportId}/schedule`, scheduleData);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to schedule report');
    }
  },

  // Get scheduled reports
  getScheduledReports: async () => {
    try {
      const reports = await apiService.get('/api/reports/scheduled');
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch scheduled reports');
    }
  },
};