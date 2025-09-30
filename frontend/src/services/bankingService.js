import { apiService } from './apiService';

export const bankingService = {
  // Bank Accounts
  getBankAccounts: async (params = {}) => {
    try {
      const accounts = await apiService.get('/api/banking/bank-accounts', params);
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank accounts');
    }
  },

  getBankAccount: async (accountId) => {
    try {
      const account = await apiService.get(`/api/banking/bank-accounts/${accountId}`);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank account');
    }
  },

  createBankAccount: async (accountData) => {
    try {
      const account = await apiService.post('/api/banking/bank-accounts', accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to create bank account');
    }
  },

  updateBankAccount: async (accountId, accountData) => {
    try {
      const account = await apiService.put(`/api/banking/bank-accounts/${accountId}`, accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to update bank account');
    }
  },

  deleteBankAccount: async (accountId) => {
    try {
      await apiService.delete(`/api/banking/bank-accounts/${accountId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete bank account');
    }
  },

  // Bank Statements
  getBankStatements: async (params = {}) => {
    try {
      const statements = await apiService.get('/api/banking/bank-statements', params);
      return statements;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statements');
    }
  },

  getBankStatement: async (statementId) => {
    try {
      const statement = await apiService.get(`/api/banking/bank-statements/${statementId}`);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statement');
    }
  },

  createBankStatement: async (statementData) => {
    try {
      const statement = await apiService.post('/api/banking/bank-statements', statementData);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to create bank statement');
    }
  },

  updateBankStatement: async (statementId, statementData) => {
    try {
      const statement = await apiService.put(`/api/banking/bank-statements/${statementId}`, statementData);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to update bank statement');
    }
  },

  deleteBankStatement: async (statementId) => {
    try {
      await apiService.delete(`/api/banking/bank-statements/${statementId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete bank statement');
    }
  },

  // Import Bank Statement
  importBankStatement: async (accountId, fileData) => {
    try {
      const formData = new FormData();
      formData.append('file', fileData.file);
      formData.append('account_id', accountId);
      formData.append('statement_date', fileData.statement_date);
      
      const statement = await apiService.post('/api/banking/bank-statements/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to import bank statement');
    }
  },

  // Bank Statement Lines
  getBankStatementLines: async (statementId, params = {}) => {
    try {
      const lines = await apiService.get(`/api/banking/bank-statements/${statementId}/lines`, params);
      return lines;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statement lines');
    }
  },

  getBankStatementLine: async (lineId) => {
    try {
      const line = await apiService.get(`/api/banking/bank-statement-lines/${lineId}`);
      return line;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statement line');
    }
  },

  updateBankStatementLine: async (lineId, lineData) => {
    try {
      const line = await apiService.put(`/api/banking/bank-statement-lines/${lineId}`, lineData);
      return line;
    } catch (error) {
      throw new Error(error.message || 'Failed to update bank statement line');
    }
  },

  // Reconciliation
  getReconciliations: async (params = {}) => {
    try {
      const reconciliations = await apiService.get('/api/banking/reconciliations', params);
      return reconciliations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reconciliations');
    }
  },

  getReconciliation: async (reconciliationId) => {
    try {
      const reconciliation = await apiService.get(`/api/banking/reconciliations/${reconciliationId}`);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reconciliation');
    }
  },

  createReconciliation: async (reconciliationData) => {
    try {
      const reconciliation = await apiService.post('/api/banking/reconciliations', reconciliationData);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to create reconciliation');
    }
  },

  updateReconciliation: async (reconciliationId, reconciliationData) => {
    try {
      const reconciliation = await apiService.put(`/api/banking/reconciliations/${reconciliationId}`, reconciliationData);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to update reconciliation');
    }
  },

  deleteReconciliation: async (reconciliationId) => {
    try {
      await apiService.delete(`/api/banking/reconciliations/${reconciliationId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete reconciliation');
    }
  },

  // Auto Reconcile
  autoReconcile: async (reconciliationId) => {
    try {
      const result = await apiService.post(`/api/banking/reconciliations/${reconciliationId}/auto-reconcile`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to auto reconcile');
    }
  },

  // Manual Reconcile
  manualReconcile: async (reconciliationId, reconcileData) => {
    try {
      const result = await apiService.post(`/api/banking/reconciliations/${reconciliationId}/manual-reconcile`, reconcileData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to manual reconcile');
    }
  },

  // Payment Methods
  getPaymentMethods: async (params = {}) => {
    try {
      const methods = await apiService.get('/api/banking/payment-methods', params);
      return methods;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment methods');
    }
  },

  getPaymentMethod: async (methodId) => {
    try {
      const method = await apiService.get(`/api/banking/payment-methods/${methodId}`);
      return method;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment method');
    }
  },

  createPaymentMethod: async (methodData) => {
    try {
      const method = await apiService.post('/api/banking/payment-methods', methodData);
      return method;
    } catch (error) {
      throw new Error(error.message || 'Failed to create payment method');
    }
  },

  updatePaymentMethod: async (methodId, methodData) => {
    try {
      const method = await apiService.put(`/api/banking/payment-methods/${methodId}`, methodData);
      return method;
    } catch (error) {
      throw new Error(error.message || 'Failed to update payment method');
    }
  },

  deletePaymentMethod: async (methodId) => {
    try {
      await apiService.delete(`/api/banking/payment-methods/${methodId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete payment method');
    }
  },

  // Cash Rounding
  getCashRounding: async (params = {}) => {
    try {
      const rounding = await apiService.get('/api/banking/cash-rounding', params);
      return rounding;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cash rounding');
    }
  },

  createCashRounding: async (roundingData) => {
    try {
      const rounding = await apiService.post('/api/banking/cash-rounding', roundingData);
      return rounding;
    } catch (error) {
      throw new Error(error.message || 'Failed to create cash rounding');
    }
  },

  updateCashRounding: async (roundingId, roundingData) => {
    try {
      const rounding = await apiService.put(`/api/banking/cash-rounding/${roundingId}`, roundingData);
      return rounding;
    } catch (error) {
      throw new Error(error.message || 'Failed to update cash rounding');
    }
  },

  // Import Templates
  getImportTemplates: async (params = {}) => {
    try {
      const templates = await apiService.get('/api/banking/import-templates', params);
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch import templates');
    }
  },

  getImportTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/banking/import-templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch import template');
    }
  },

  createImportTemplate: async (templateData) => {
    try {
      const template = await apiService.post('/api/banking/import-templates', templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to create import template');
    }
  },

  updateImportTemplate: async (templateId, templateData) => {
    try {
      const template = await apiService.put(`/api/banking/import-templates/${templateId}`, templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to update import template');
    }
  },

  deleteImportTemplate: async (templateId) => {
    try {
      await apiService.delete(`/api/banking/import-templates/${templateId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete import template');
    }
  },

  // Banking Analytics
  getBankingAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/banking/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking analytics');
    }
  },

  getBankingDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/banking/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking dashboard');
    }
  },

  getBankingReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/banking/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking reports');
    }
  },

  // Export functionality
  exportBankingData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/banking/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export banking data');
    }
  }
};