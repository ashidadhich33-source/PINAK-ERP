import { apiService } from './apiService';

export const reportService = {
  // Financial Reports
  getProfitLossReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/financial/profit-loss', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit & loss report');
    }
  },

  getBalanceSheetReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/financial/balance-sheet', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch balance sheet report');
    }
  },

  getCashFlowReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/financial/cash-flow', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cash flow report');
    }
  },

  getTrialBalanceReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/financial/trial-balance', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trial balance report');
    }
  },

  // Stock Reports
  getStockSummaryReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/stock/summary', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock summary report');
    }
  },

  getStockMovementReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/stock/movement', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock movement report');
    }
  },

  getStockValuationReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/stock/valuation', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock valuation report');
    }
  },

  getStockAgingReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/reports/stock/aging', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stock aging report');
    }
  },

  // Dashboard Reports
  getExecutiveDashboard: async (params = {}) => {
    try {
      const dashboard = await apiService.get('/api/reports/dashboards/executive', params);
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch executive dashboard');
    }
  },

  getOperationalDashboard: async (params = {}) => {
    try {
      const dashboard = await apiService.get('/api/reports/dashboards/operational', params);
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch operational dashboard');
    }
  },

  getFinancialDashboard: async (params = {}) => {
    try {
      const dashboard = await apiService.get('/api/reports/dashboards/financial', params);
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial dashboard');
    }
  },

  getSalesDashboard: async (params = {}) => {
    try {
      const dashboard = await apiService.get('/api/reports/dashboards/sales', params);
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales dashboard');
    }
  },

  // Custom Reports
  getCustomReports: async () => {
    try {
      const reports = await apiService.get('/api/reports/custom');
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
      const result = await apiService.post('/api/reports/custom', reportData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create custom report');
    }
  },

  updateCustomReport: async (reportId, reportData) => {
    try {
      const result = await apiService.put(`/api/reports/custom/${reportId}`, reportData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update custom report');
    }
  },

  deleteCustomReport: async (reportId) => {
    try {
      const result = await apiService.delete(`/api/reports/custom/${reportId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete custom report');
    }
  },

  // Scheduled Reports
  getScheduledReports: async () => {
    try {
      const reports = await apiService.get('/api/reports/scheduled');
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch scheduled reports');
    }
  },

  getScheduledReport: async (reportId) => {
    try {
      const report = await apiService.get(`/api/reports/scheduled/${reportId}`);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch scheduled report');
    }
  },

  scheduleReport: async (reportId, scheduleData = {}) => {
    try {
      const result = await apiService.post(`/api/reports/custom/${reportId}/schedule`, scheduleData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to schedule report');
    }
  },

  updateScheduledReport: async (reportId, scheduleData) => {
    try {
      const result = await apiService.put(`/api/reports/scheduled/${reportId}`, scheduleData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update scheduled report');
    }
  },

  deleteScheduledReport: async (reportId) => {
    try {
      const result = await apiService.delete(`/api/reports/scheduled/${reportId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete scheduled report');
    }
  },

  // Shared Reports
  getSharedReports: async () => {
    try {
      const reports = await apiService.get('/api/reports/shared');
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch shared reports');
    }
  },

  getSharedReport: async (reportId) => {
    try {
      const report = await apiService.get(`/api/reports/shared/${reportId}`);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch shared report');
    }
  },

  shareReport: async (reportId, shareData = {}) => {
    try {
      const result = await apiService.post(`/api/reports/custom/${reportId}/share`, shareData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to share report');
    }
  },

  updateSharedReport: async (reportId, shareData) => {
    try {
      const result = await apiService.put(`/api/reports/shared/${reportId}`, shareData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update shared report');
    }
  },

  deleteSharedReport: async (reportId) => {
    try {
      const result = await apiService.delete(`/api/reports/shared/${reportId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete shared report');
    }
  },

  // Export Functions
  exportFinancialReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/reports/export/financial/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export financial report');
    }
  },

  exportStockReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/reports/export/stock/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export stock report');
    }
  },

  exportDashboard: async (dashboardType, params = {}) => {
    try {
      const result = await apiService.post(`/api/reports/export/dashboard/${dashboardType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export dashboard');
    }
  },

  exportCustomReport: async (reportId, format = 'pdf') => {
    try {
      const result = await apiService.post(`/api/reports/export/custom/${reportId}`, { format });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export custom report');
    }
  },

  // Report Generation
  generateReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/reports/generate/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate report');
    }
  },

  // Report Templates
  getReportTemplates: async () => {
    try {
      const templates = await apiService.get('/api/reports/templates');
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
      const result = await apiService.post('/api/reports/templates', templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report template');
    }
  },

  updateReportTemplate: async (templateId, templateData) => {
    try {
      const result = await apiService.put(`/api/reports/templates/${templateId}`, templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report template');
    }
  },

  deleteReportTemplate: async (templateId) => {
    try {
      const result = await apiService.delete(`/api/reports/templates/${templateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report template');
    }
  },

  // Report Analytics
  getReportAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/reports/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report analytics');
    }
  },

  getReportUsage: async (reportId) => {
    try {
      const usage = await apiService.get(`/api/reports/custom/${reportId}/usage`);
      return usage;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report usage');
    }
  },

  // Report Validation
  validateReport: async (reportData) => {
    try {
      const result = await apiService.post('/api/reports/validate', reportData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate report');
    }
  },

  // Report Permissions
  getReportPermissions: async (reportId) => {
    try {
      const permissions = await apiService.get(`/api/reports/custom/${reportId}/permissions`);
      return permissions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report permissions');
    }
  },

  updateReportPermissions: async (reportId, permissions) => {
    try {
      const result = await apiService.put(`/api/reports/custom/${reportId}/permissions`, permissions);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report permissions');
    }
  },

  // Report Categories
  getReportCategories: async () => {
    try {
      const categories = await apiService.get('/api/reports/categories');
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report categories');
    }
  },

  getReportsByCategory: async (categoryId) => {
    try {
      const reports = await apiService.get(`/api/reports/categories/${categoryId}/reports`);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reports by category');
    }
  }
};