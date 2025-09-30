import { apiService } from './apiService';

export const advancedReportingService = {
  // Report Builder
  getReportTemplates: async (params = {}) => {
    try {
      const templates = await apiService.get('/api/advanced-reporting/templates', params);
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report templates');
    }
  },

  getReportTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/advanced-reporting/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report template');
    }
  },

  createReportTemplate: async (templateData) => {
    try {
      const template = await apiService.post('/api/advanced-reporting/templates', templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report template');
    }
  },

  updateReportTemplate: async (templateId, templateData) => {
    try {
      const template = await apiService.put(`/api/advanced-reporting/templates/${templateId}`, templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report template');
    }
  },

  deleteReportTemplate: async (templateId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/templates/${templateId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report template');
    }
  },

  // Custom Reports
  getCustomReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/advanced-reporting/custom-reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch custom reports');
    }
  },

  getCustomReport: async (reportId) => {
    try {
      const report = await apiService.get(`/api/advanced-reporting/custom-reports/${reportId}`);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch custom report');
    }
  },

  createCustomReport: async (reportData) => {
    try {
      const report = await apiService.post('/api/advanced-reporting/custom-reports', reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to create custom report');
    }
  },

  updateCustomReport: async (reportId, reportData) => {
    try {
      const report = await apiService.put(`/api/advanced-reporting/custom-reports/${reportId}`, reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to update custom report');
    }
  },

  deleteCustomReport: async (reportId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/custom-reports/${reportId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete custom report');
    }
  },

  // Report Generation
  generateReport: async (reportId, parameters = {}) => {
    try {
      const report = await apiService.post(`/api/advanced-reporting/custom-reports/${reportId}/generate`, parameters);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate report');
    }
  },

  // Report Scheduling
  getReportSchedules: async (params = {}) => {
    try {
      const schedules = await apiService.get('/api/advanced-reporting/schedules', params);
      return schedules;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report schedules');
    }
  },

  getReportSchedule: async (scheduleId) => {
    try {
      const schedule = await apiService.get(`/api/advanced-reporting/schedules/${scheduleId}`);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report schedule');
    }
  },

  createReportSchedule: async (scheduleData) => {
    try {
      const schedule = await apiService.post('/api/advanced-reporting/schedules', scheduleData);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report schedule');
    }
  },

  updateReportSchedule: async (scheduleId, scheduleData) => {
    try {
      const schedule = await apiService.put(`/api/advanced-reporting/schedules/${scheduleId}`, scheduleData);
      return schedule;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report schedule');
    }
  },

  deleteReportSchedule: async (scheduleId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/schedules/${scheduleId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report schedule');
    }
  },

  // Report Categories
  getReportCategories: async (params = {}) => {
    try {
      const categories = await apiService.get('/api/advanced-reporting/categories', params);
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report categories');
    }
  },

  getReportCategory: async (categoryId) => {
    try {
      const category = await apiService.get(`/api/advanced-reporting/categories/${categoryId}`);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report category');
    }
  },

  createReportCategory: async (categoryData) => {
    try {
      const category = await apiService.post('/api/advanced-reporting/categories', categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report category');
    }
  },

  updateReportCategory: async (categoryId, categoryData) => {
    try {
      const category = await apiService.put(`/api/advanced-reporting/categories/${categoryId}`, categoryData);
      return category;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report category');
    }
  },

  deleteReportCategory: async (categoryId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/categories/${categoryId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report category');
    }
  },

  // Report Fields
  getReportFields: async (params = {}) => {
    try {
      const fields = await apiService.get('/api/advanced-reporting/fields', params);
      return fields;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report fields');
    }
  },

  getReportField: async (fieldId) => {
    try {
      const field = await apiService.get(`/api/advanced-reporting/fields/${fieldId}`);
      return field;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report field');
    }
  },

  createReportField: async (fieldData) => {
    try {
      const field = await apiService.post('/api/advanced-reporting/fields', fieldData);
      return field;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report field');
    }
  },

  updateReportField: async (fieldId, fieldData) => {
    try {
      const field = await apiService.put(`/api/advanced-reporting/fields/${fieldId}`, fieldData);
      return field;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report field');
    }
  },

  deleteReportField: async (fieldId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/fields/${fieldId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report field');
    }
  },

  // Report Filters
  getReportFilters: async (params = {}) => {
    try {
      const filters = await apiService.get('/api/advanced-reporting/filters', params);
      return filters;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report filters');
    }
  },

  getReportFilter: async (filterId) => {
    try {
      const filter = await apiService.get(`/api/advanced-reporting/filters/${filterId}`);
      return filter;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report filter');
    }
  },

  createReportFilter: async (filterData) => {
    try {
      const filter = await apiService.post('/api/advanced-reporting/filters', filterData);
      return filter;
    } catch (error) {
      throw new Error(error.message || 'Failed to create report filter');
    }
  },

  updateReportFilter: async (filterId, filterData) => {
    try {
      const filter = await apiService.put(`/api/advanced-reporting/filters/${filterId}`, filterData);
      return filter;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report filter');
    }
  },

  deleteReportFilter: async (filterId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/filters/${filterId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete report filter');
    }
  },

  // Report Analytics
  getReportAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/advanced-reporting/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report analytics');
    }
  },

  getReportDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/advanced-reporting/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report dashboard');
    }
  },

  // Report Export
  exportReport: async (reportId, format, parameters = {}) => {
    try {
      const response = await apiService.post(`/api/advanced-reporting/custom-reports/${reportId}/export`, {
        format,
        parameters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export report');
    }
  },

  // Report Sharing
  shareReport: async (reportId, shareData) => {
    try {
      const response = await apiService.post(`/api/advanced-reporting/custom-reports/${reportId}/share`, shareData);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to share report');
    }
  },

  // Report Permissions
  getReportPermissions: async (reportId) => {
    try {
      const permissions = await apiService.get(`/api/advanced-reporting/custom-reports/${reportId}/permissions`);
      return permissions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report permissions');
    }
  },

  updateReportPermissions: async (reportId, permissions) => {
    try {
      const response = await apiService.put(`/api/advanced-reporting/custom-reports/${reportId}/permissions`, permissions);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to update report permissions');
    }
  },

  // Report History
  getReportHistory: async (reportId, params = {}) => {
    try {
      const history = await apiService.get(`/api/advanced-reporting/custom-reports/${reportId}/history`, params);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report history');
    }
  },

  // Report Favorites
  getReportFavorites: async (params = {}) => {
    try {
      const favorites = await apiService.get('/api/advanced-reporting/favorites', params);
      return favorites;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch report favorites');
    }
  },

  addReportFavorite: async (reportId) => {
    try {
      const response = await apiService.post(`/api/advanced-reporting/custom-reports/${reportId}/favorite`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to add report to favorites');
    }
  },

  removeReportFavorite: async (reportId) => {
    try {
      await apiService.delete(`/api/advanced-reporting/custom-reports/${reportId}/favorite`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove report from favorites');
    }
  }
};