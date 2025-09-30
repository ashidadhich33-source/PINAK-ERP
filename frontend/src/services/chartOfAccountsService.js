import { apiService } from './apiService';

export const chartOfAccountsService = {
  // Get all chart of accounts
  getChartOfAccounts: async (params = {}) => {
    try {
      const accounts = await apiService.get('/api/accounting/chart-of-accounts/', params);
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch chart of accounts');
    }
  },

  // Get chart of accounts hierarchy
  getAccountHierarchy: async () => {
    try {
      const hierarchy = await apiService.get('/api/accounting/chart-of-accounts/hierarchy');
      return hierarchy;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account hierarchy');
    }
  },

  // Get account by ID
  getAccount: async (accountId) => {
    try {
      const account = await apiService.get(`/api/accounting/chart-of-accounts/${accountId}`);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account');
    }
  },

  // Create new account
  createAccount: async (accountData) => {
    try {
      const account = await apiService.post('/api/accounting/chart-of-accounts/', accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to create account');
    }
  },

  // Update account
  updateAccount: async (accountId, accountData) => {
    try {
      const account = await apiService.put(`/api/accounting/chart-of-accounts/${accountId}`, accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to update account');
    }
  },

  // Delete account
  deleteAccount: async (accountId) => {
    try {
      await apiService.delete(`/api/accounting/chart-of-accounts/${accountId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete account');
    }
  },

  // Initialize Indian chart of accounts
  initializeIndianAccounts: async () => {
    try {
      const result = await apiService.post('/api/accounting/chart-of-accounts/initialize-indian');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to initialize Indian chart of accounts');
    }
  },

  // Get account balance
  getAccountBalance: async (accountId, params = {}) => {
    try {
      const balance = await apiService.get(`/api/accounting/chart-of-accounts/${accountId}/balance`, params);
      return balance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account balance');
    }
  },

  // Get trial balance
  getTrialBalance: async (params = {}) => {
    try {
      const trialBalance = await apiService.get('/api/accounting/chart-of-accounts/trial-balance', params);
      return trialBalance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trial balance');
    }
  },

  // Get balance sheet
  getBalanceSheet: async (params = {}) => {
    try {
      const balanceSheet = await apiService.get('/api/accounting/chart-of-accounts/balance-sheet', params);
      return balanceSheet;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch balance sheet');
    }
  },

  // Get profit & loss
  getProfitLoss: async (params = {}) => {
    try {
      const profitLoss = await apiService.get('/api/accounting/chart-of-accounts/profit-loss', params);
      return profitLoss;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit & loss');
    }
  },

  // Export chart of accounts
  exportChartOfAccounts: async (format = 'excel', params = {}) => {
    try {
      const response = await apiService.get('/api/accounting/chart-of-accounts/export/excel', params);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export chart of accounts');
    }
  },

  // Get account types
  getAccountTypes: async () => {
    try {
      const types = await apiService.get('/api/accounting/chart-of-accounts/types');
      return types;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account types');
    }
  },

  // Validate account code
  validateAccountCode: async (accountCode, accountId = null) => {
    try {
      const result = await apiService.post('/api/accounting/chart-of-accounts/validate-code', {
        account_code: accountCode,
        account_id: accountId
      });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate account code');
    }
  },
};