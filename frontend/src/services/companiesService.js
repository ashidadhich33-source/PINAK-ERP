import { apiService } from './apiService';

export const companiesService = {
  // Get all companies
  getCompanies: async (params = {}) => {
    try {
      const companies = await apiService.get('/api/companies/', params);
      return companies;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch companies');
    }
  },

  // Get company by ID
  getCompany: async (companyId) => {
    try {
      const company = await apiService.get(`/api/companies/${companyId}`);
      return company;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch company');
    }
  },

  // Create new company
  createCompany: async (companyData) => {
    try {
      const company = await apiService.post('/api/companies/', companyData);
      return company;
    } catch (error) {
      throw new Error(error.message || 'Failed to create company');
    }
  },

  // Update company
  updateCompany: async (companyId, companyData) => {
    try {
      const company = await apiService.put(`/api/companies/${companyId}`, companyData);
      return company;
    } catch (error) {
      throw new Error(error.message || 'Failed to update company');
    }
  },

  // Delete company
  deleteCompany: async (companyId) => {
    try {
      await apiService.delete(`/api/companies/${companyId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete company');
    }
  },

  // Toggle company status
  toggleCompanyStatus: async (companyId) => {
    try {
      const response = await apiService.put(`/api/companies/${companyId}/toggle-status`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle company status');
    }
  },

  // Get company settings
  getCompanySettings: async (companyId) => {
    try {
      const settings = await apiService.get(`/api/companies/${companyId}/settings`);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch company settings');
    }
  },

  // Update company settings
  updateCompanySettings: async (companyId, settingsData) => {
    try {
      const settings = await apiService.put(`/api/companies/${companyId}/settings`, settingsData);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to update company settings');
    }
  },

  // Get company statistics
  getCompanyStats: async (companyId) => {
    try {
      const stats = await apiService.get(`/api/companies/${companyId}/stats`);
      return stats;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch company statistics');
    }
  },

  // Search companies
  searchCompanies: async (query, params = {}) => {
    try {
      const companies = await apiService.get('/api/companies/search', {
        q: query,
        ...params,
      });
      return companies;
    } catch (error) {
      throw new Error(error.message || 'Failed to search companies');
    }
  },

  // Export companies
  exportCompanies: async (format = 'csv', filters = {}) => {
    try {
      const response = await apiService.get('/api/companies/export', {
        format,
        ...filters,
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export companies');
    }
  },

  // Import companies
  importCompanies: async (file, onProgress = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.upload('/api/companies/import', formData, onProgress);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to import companies');
    }
  },
};