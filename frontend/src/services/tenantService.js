import { apiService } from './apiService';

export const tenantService = {
  // Get all tenants
  getTenants: async (options = {}) => {
    try {
      const tenants = await apiService.get('/api/tenants', options);
      return tenants;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenants');
    }
  },

  // Get tenant by ID
  getTenantById: async (tenantId) => {
    try {
      const tenant = await apiService.get(`/api/tenants/${tenantId}`);
      return tenant;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant');
    }
  },

  // Create new tenant
  createTenant: async (tenantData) => {
    try {
      const tenant = await apiService.post('/api/tenants', tenantData);
      return tenant;
    } catch (error) {
      throw new Error(error.message || 'Failed to create tenant');
    }
  },

  // Update tenant
  updateTenant: async (tenantId, tenantData) => {
    try {
      const tenant = await apiService.put(`/api/tenants/${tenantId}`, tenantData);
      return tenant;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant');
    }
  },

  // Delete tenant
  deleteTenant: async (tenantId) => {
    try {
      await apiService.delete(`/api/tenants/${tenantId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete tenant');
    }
  },

  // Switch tenant context
  switchTenant: async (tenantId) => {
    try {
      const result = await apiService.post(`/api/tenants/${tenantId}/switch`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to switch tenant');
    }
  },

  // Get current tenant
  getCurrentTenant: async () => {
    try {
      const tenant = await apiService.get('/api/tenants/current');
      return tenant;
    } catch (error) {
      throw new Error(error.message || 'Failed to get current tenant');
    }
  },

  // Get tenant users
  getTenantUsers: async (tenantId, options = {}) => {
    try {
      const users = await apiService.get(`/api/tenants/${tenantId}/users`, options);
      return users;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant users');
    }
  },

  // Add user to tenant
  addUserToTenant: async (tenantId, userId, role) => {
    try {
      const result = await apiService.post(`/api/tenants/${tenantId}/users`, {
        user_id: userId,
        role: role
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add user to tenant');
    }
  },

  // Remove user from tenant
  removeUserFromTenant: async (tenantId, userId) => {
    try {
      await apiService.delete(`/api/tenants/${tenantId}/users/${userId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove user from tenant');
    }
  },

  // Update user role in tenant
  updateUserRole: async (tenantId, userId, role) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/users/${userId}`, {
        role: role
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update user role');
    }
  },

  // Get tenant settings
  getTenantSettings: async (tenantId) => {
    try {
      const settings = await apiService.get(`/api/tenants/${tenantId}/settings`);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant settings');
    }
  },

  // Update tenant settings
  updateTenantSettings: async (tenantId, settings) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/settings`, settings);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant settings');
    }
  },

  // Get tenant permissions
  getTenantPermissions: async (tenantId) => {
    try {
      const permissions = await apiService.get(`/api/tenants/${tenantId}/permissions`);
      return permissions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant permissions');
    }
  },

  // Update tenant permissions
  updateTenantPermissions: async (tenantId, permissions) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/permissions`, permissions);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant permissions');
    }
  },

  // Get tenant analytics
  getTenantAnalytics: async (tenantId, options = {}) => {
    try {
      const analytics = await apiService.get(`/api/tenants/${tenantId}/analytics`, options);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant analytics');
    }
  },

  // Get tenant reports
  getTenantReports: async (tenantId, options = {}) => {
    try {
      const reports = await apiService.get(`/api/tenants/${tenantId}/reports`, options);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant reports');
    }
  },

  // Generate tenant report
  generateTenantReport: async (tenantId, reportType, options = {}) => {
    try {
      const report = await apiService.post(`/api/tenants/${tenantId}/reports`, {
        report_type: reportType,
        ...options
      });
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate tenant report');
    }
  },

  // Get tenant billing
  getTenantBilling: async (tenantId, options = {}) => {
    try {
      const billing = await apiService.get(`/api/tenants/${tenantId}/billing`, options);
      return billing;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant billing');
    }
  },

  // Update tenant billing
  updateTenantBilling: async (tenantId, billingData) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/billing`, billingData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant billing');
    }
  },

  // Get tenant usage
  getTenantUsage: async (tenantId, options = {}) => {
    try {
      const usage = await apiService.get(`/api/tenants/${tenantId}/usage`, options);
      return usage;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant usage');
    }
  },

  // Get tenant limits
  getTenantLimits: async (tenantId) => {
    try {
      const limits = await apiService.get(`/api/tenants/${tenantId}/limits`);
      return limits;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant limits');
    }
  },

  // Update tenant limits
  updateTenantLimits: async (tenantId, limits) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/limits`, limits);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant limits');
    }
  },

  // Get tenant logs
  getTenantLogs: async (tenantId, options = {}) => {
    try {
      const logs = await apiService.get(`/api/tenants/${tenantId}/logs`, options);
      return logs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant logs');
    }
  },

  // Get tenant notifications
  getTenantNotifications: async (tenantId, options = {}) => {
    try {
      const notifications = await apiService.get(`/api/tenants/${tenantId}/notifications`, options);
      return notifications;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant notifications');
    }
  },

  // Send tenant notification
  sendTenantNotification: async (tenantId, notification) => {
    try {
      const result = await apiService.post(`/api/tenants/${tenantId}/notifications`, notification);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send tenant notification');
    }
  },

  // Get tenant statistics
  getTenantStatistics: async (tenantId, options = {}) => {
    try {
      const statistics = await apiService.get(`/api/tenants/${tenantId}/statistics`, options);
      return statistics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant statistics');
    }
  },

  // Get tenant health
  getTenantHealth: async (tenantId) => {
    try {
      const health = await apiService.get(`/api/tenants/${tenantId}/health`);
      return health;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant health');
    }
  },

  // Get tenant backup
  getTenantBackup: async (tenantId) => {
    try {
      const backup = await apiService.get(`/api/tenants/${tenantId}/backup`);
      return backup;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant backup');
    }
  },

  // Create tenant backup
  createTenantBackup: async (tenantId) => {
    try {
      const backup = await apiService.post(`/api/tenants/${tenantId}/backup`);
      return backup;
    } catch (error) {
      throw new Error(error.message || 'Failed to create tenant backup');
    }
  },

  // Restore tenant from backup
  restoreTenantFromBackup: async (tenantId, backupId) => {
    try {
      const result = await apiService.post(`/api/tenants/${tenantId}/restore`, {
        backup_id: backupId
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to restore tenant from backup');
    }
  },

  // Get tenant integrations
  getTenantIntegrations: async (tenantId) => {
    try {
      const integrations = await apiService.get(`/api/tenants/${tenantId}/integrations`);
      return integrations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch tenant integrations');
    }
  },

  // Add tenant integration
  addTenantIntegration: async (tenantId, integrationData) => {
    try {
      const result = await apiService.post(`/api/tenants/${tenantId}/integrations`, integrationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add tenant integration');
    }
  },

  // Update tenant integration
  updateTenantIntegration: async (tenantId, integrationId, integrationData) => {
    try {
      const result = await apiService.put(`/api/tenants/${tenantId}/integrations/${integrationId}`, integrationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tenant integration');
    }
  },

  // Remove tenant integration
  removeTenantIntegration: async (tenantId, integrationId) => {
    try {
      await apiService.delete(`/api/tenants/${tenantId}/integrations/${integrationId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove tenant integration');
    }
  },
};