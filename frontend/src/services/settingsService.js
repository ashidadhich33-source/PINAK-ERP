import { apiService } from './apiService';

export const settingsService = {
  // Get all settings
  getSettings: async () => {
    try {
      const settings = await apiService.get('/api/settings/settings');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch settings');
    }
  },

  // Get settings by section
  getSettingsBySection: async (section) => {
    try {
      const settings = await apiService.get(`/api/settings/settings/${section}`);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch section settings');
    }
  },

  // Update single setting
  updateSetting: async (key, value) => {
    try {
      const result = await apiService.post('/api/settings/update', {
        key,
        value
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update setting');
    }
  },

  // Update multiple settings
  updateSettings: async (settings) => {
    try {
      const result = await apiService.post('/api/settings/update-section', settings);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update settings');
    }
  },

  // Reset settings to defaults
  resetSettings: async (section = null) => {
    try {
      const endpoint = section 
        ? `/api/settings/reset/${section}`
        : '/api/settings/reset';
      const result = await apiService.post(endpoint);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reset settings');
    }
  },

  // Validate settings
  validateSettings: async () => {
    try {
      const result = await apiService.get('/api/settings/validate');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate settings');
    }
  },

  // Export settings
  exportSettings: async (format = 'json') => {
    try {
      const result = await apiService.post('/api/settings/export', { format });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export settings');
    }
  },

  // Import settings
  importSettings: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const result = await apiService.upload('/api/settings/import', formData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to import settings');
    }
  },

  // Company Settings
  getCompanySettings: async () => {
    try {
      const settings = await apiService.get('/api/settings/company');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch company settings');
    }
  },

  updateCompanySettings: async (settings) => {
    try {
      const result = await apiService.post('/api/settings/company', settings);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update company settings');
    }
  },

  uploadCompanyLogo: async (logoFile) => {
    try {
      const formData = new FormData();
      formData.append('logo', logoFile);
      
      const result = await apiService.upload('/api/settings/company/logo', formData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to upload company logo');
    }
  },

  // Print Templates
  getPrintTemplates: async () => {
    try {
      const templates = await apiService.get('/api/settings/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch print templates');
    }
  },

  getPrintTemplate: async (templateType) => {
    try {
      const template = await apiService.get(`/api/settings/templates/${templateType}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch print template');
    }
  },

  updatePrintTemplate: async (templateType, template) => {
    try {
      const result = await apiService.post('/api/settings/templates', {
        template_type: templateType,
        template
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update print template');
    }
  },

  resetPrintTemplate: async (templateType) => {
    try {
      const result = await apiService.post(`/api/settings/templates/${templateType}/reset`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reset print template');
    }
  },

  // Quick Settings
  toggleGST: async () => {
    try {
      const result = await apiService.post('/api/settings/quick-settings/toggle-gst');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle GST');
    }
  },

  toggleLoyalty: async () => {
    try {
      const result = await apiService.post('/api/settings/quick-settings/toggle-loyalty');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle loyalty');
    }
  },

  toggleWhatsApp: async () => {
    try {
      const result = await apiService.post('/api/settings/quick-settings/toggle-whatsapp');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle WhatsApp');
    }
  },

  updateFinancialYear: async (yearData) => {
    try {
      const result = await apiService.post('/api/settings/quick-settings/update-financial-year', yearData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update financial year');
    }
  },

  updateTaxRates: async (taxRates) => {
    try {
      const result = await apiService.post('/api/settings/quick-settings/update-tax-rates', taxRates);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update tax rates');
    }
  },

  // System Information
  getSystemInfo: async () => {
    try {
      const info = await apiService.get('/api/settings/system-info');
      return info;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch system information');
    }
  },

  // Database Management
  getDatabaseStatus: async () => {
    try {
      const status = await apiService.get('/api/database/status');
      return status;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch database status');
    }
  },

  runDatabaseMigration: async () => {
    try {
      const result = await apiService.post('/api/database/migrate');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to run database migration');
    }
  },

  seedDatabase: async () => {
    try {
      const result = await apiService.post('/api/database/seed');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to seed database');
    }
  },

  // System Setup
  getSetupStatus: async () => {
    try {
      const status = await apiService.get('/api/setup/status');
      return status;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch setup status');
    }
  },

  initializeSystem: async (setupData) => {
    try {
      const result = await apiService.post('/api/setup/initialize', setupData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to initialize system');
    }
  },

  completeSetup: async () => {
    try {
      const result = await apiService.post('/api/setup/complete');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to complete setup');
    }
  },

  // Backup Management
  createBackup: async (backupData = {}) => {
    try {
      const result = await apiService.post('/api/backup/create', backupData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create backup');
    }
  },

  getBackups: async () => {
    try {
      const backups = await apiService.get('/api/backup/list');
      return backups;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch backups');
    }
  },

  restoreBackup: async (backupId) => {
    try {
      const result = await apiService.post('/api/backup/restore', { backup_id: backupId });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to restore backup');
    }
  },

  deleteBackup: async (backupId) => {
    try {
      const result = await apiService.delete(`/api/backup/${backupId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete backup');
    }
  },

  downloadBackup: async (backupId) => {
    try {
      const result = await apiService.download(`/api/backup/${backupId}/download`, `backup-${backupId}.zip`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to download backup');
    }
  },

  // Automation Control
  getAutomationWorkflows: async () => {
    try {
      const workflows = await apiService.get('/api/automation/workflows');
      return workflows;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation workflows');
    }
  },

  createAutomationWorkflow: async (workflowData) => {
    try {
      const result = await apiService.post('/api/automation/workflows', workflowData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create automation workflow');
    }
  },

  getAutomationRules: async () => {
    try {
      const rules = await apiService.get('/api/automation/rules');
      return rules;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation rules');
    }
  },

  createAutomationRule: async (ruleData) => {
    try {
      const result = await apiService.post('/api/automation/rules', ruleData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create automation rule');
    }
  },

  getAutomationTriggers: async () => {
    try {
      const triggers = await apiService.get('/api/automation/triggers');
      return triggers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation triggers');
    }
  },

  createAutomationTrigger: async (triggerData) => {
    try {
      const result = await apiService.post('/api/automation/triggers', triggerData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create automation trigger');
    }
  },

  getAutomationActions: async () => {
    try {
      const actions = await apiService.get('/api/automation/actions');
      return actions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation actions');
    }
  },

  createAutomationAction: async (actionData) => {
    try {
      const result = await apiService.post('/api/automation/actions', actionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create automation action');
    }
  },

  getAutomationLogs: async (params = {}) => {
    try {
      const logs = await apiService.get('/api/automation/logs', params);
      return logs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch automation logs');
    }
  },

  executeAutomation: async (automationId) => {
    try {
      const result = await apiService.post('/api/automation/execute', { automation_id: automationId });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to execute automation');
    }
  },

  approveAutomation: async (automationId) => {
    try {
      const result = await apiService.post('/api/automation/approve', { automation_id: automationId });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to approve automation');
    }
  },

  rollbackAutomation: async (automationId) => {
    try {
      const result = await apiService.post('/api/automation/rollback', { automation_id: automationId });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to rollback automation');
    }
  }
};