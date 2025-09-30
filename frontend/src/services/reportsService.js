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

  // Custom Reports
  getCustomReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/reports/custom', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch custom reports');
    }
  },

  getCustomReport: async (reportId) => {
    try {
      const report = await apiService.get(`/api/reports/custom/${reportId}`);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch custom report');
    }
  },

  createCustomReport: async (reportData) => {
    try {
      const report = await apiService.post('/api/reports/custom', reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to create custom report');
    }
  },

  updateCustomReport: async (reportId, reportData) => {
    try {
      const report = await apiService.put(`/api/reports/custom/${reportId}`, reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to update custom report');
    }
  },

  deleteCustomReport: async (reportId) => {
    try {
      await apiService.delete(`/api/reports/custom/${reportId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete custom report');
    }
  },

  // Report Templates
  getReportTemplates: async (params = {}) => {
    try {
      const templates = await apiService.get('/api/reports/templates', params);
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report templates');
    }
  },

  getReportTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/reports/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report template');
    }
  },

  createReportTemplate: async (templateData) => {
    try {
      const template = await apiService.post('/api/reports/templates', templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report template');
    }
  },

  updateReportTemplate: async (templateId, templateData) => {
    try {
      const template = await apiService.put(`/api/reports/templates/${templateId}`, templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report template');
    }
  },

  deleteReportTemplate: async (templateId) => {
    try {
      await apiService.delete(`/api/reports/templates/${templateId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report template');
    }
  },

  // Report Schedules
  getReportSchedules: async (params = {}) => {
    try {
      const schedules = await apiService.get('/api/reports/schedules', params);
      return schedules;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report schedules');
    }
  },

  getReportSchedule: async (scheduleId) => {
    try {
      const schedule = await apiService.get(`/api/reports/schedules/${scheduleId}`);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report schedule');
    }
  },

  createReportSchedule: async (scheduleData) => {
    try {
      const schedule = await apiService.post('/api/reports/schedules', scheduleData);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report schedule');
    }
  },

  updateReportSchedule: async (scheduleId, scheduleData) => {
    try {
      const schedule = await apiService.put(`/api/reports/schedules/${scheduleId}`, scheduleData);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report schedule');
    }
  },

  deleteReportSchedule: async (scheduleId) => {
    try {
      await apiService.delete(`/api/reports/schedules/${scheduleId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report schedule');
    }
  },

  // Report Categories
  getReportCategories: async (params = {}) => {
    try {
      const categories = await apiService.get('/api/reports/categories', params);
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report categories');
    }
  },

  getReportCategory: async (categoryId) => {
    try {
      const category = await apiService.get(`/api/reports/categories/${categoryId}`);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report category');
    }
  },

  createReportCategory: async (categoryData) => {
    try {
      const category = await apiService.post('/api/reports/categories', categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report category');
    }
  },

  updateReportCategory: async (categoryId, categoryData) => {
    try {
      const category = await apiService.put(`/api/reports/categories/${categoryId}`, categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report category');
    }
  },

  deleteReportCategory: async (categoryId) => {
    try {
      await apiService.delete(`/api/reports/categories/${categoryId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report category');
    }
  },

  // Report Generation
  generateReport: async (reportId, parameters = {}) => {
    try {
      const report = await apiService.post(`/api/reports/custom/${reportId}/generate`, parameters);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate report');
    }
  },

  // Report Export
  exportReport: async (reportId, format, parameters = {}) => {
    try {
      const response = await apiService.post(`/api/reports/custom/${reportId}/export`, {
        format,
        parameters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export report');
    }
  },

  // Report Favorites
  addReportFavorite: async (reportId) => {
    try {
      const response = await apiService.post(`/api/reports/custom/${reportId}/favorite`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to add report to favorites');
    }
  },

  removeReportFavorite: async (reportId) => {
    try {
      await apiService.delete(`/api/reports/custom/${reportId}/favorite`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove report from favorites');
    }
  }
};