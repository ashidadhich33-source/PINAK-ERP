import { apiService } from './apiService';

export const accountingService = {
  // Chart of Accounts
  getChartOfAccounts: async (params = {}) => {
    try {
      const accounts = await apiService.get('/api/chart-of-accounts', params);
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch chart of accounts');
    }
  },

  getChartOfAccount: async (accountId) => {
    try {
      const account = await apiService.get(`/api/chart-of-accounts/${accountId}`);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch chart of account');
    }
  },

  createChartOfAccount: async (accountData) => {
    try {
      const account = await apiService.post('/api/chart-of-accounts', accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to create chart of account');
    }
  },

  updateChartOfAccount: async (accountId, accountData) => {
    try {
      const account = await apiService.put(`/api/chart-of-accounts/${accountId}`, accountData);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to update chart of account');
    }
  },

  deleteChartOfAccount: async (accountId) => {
    try {
      await apiService.delete(`/api/chart-of-accounts/${accountId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete chart of account');
    }
  },

  // Journal Entries
  getJournalEntries: async (params = {}) => {
    try {
      const entries = await apiService.get('/api/double-entry-accounting/journal-entries', params);
      return entries;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch journal entries');
    }
  },

  getJournalEntry: async (entryId) => {
    try {
      const entry = await apiService.get(`/api/double-entry-accounting/journal-entries/${entryId}`);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch journal entry');
    }
  },

  createJournalEntry: async (entryData) => {
    try {
      const entry = await apiService.post('/api/double-entry-accounting/journal-entries', entryData);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to create journal entry');
    }
  },

  updateJournalEntry: async (entryId, entryData) => {
    try {
      const entry = await apiService.put(`/api/double-entry-accounting/journal-entries/${entryId}`, entryData);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to update journal entry');
    }
  },

  deleteJournalEntry: async (entryId) => {
    try {
      await apiService.delete(`/api/double-entry-accounting/journal-entries/${entryId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete journal entry');
    }
  },

  postJournalEntry: async (entryId) => {
    try {
      const entry = await apiService.post(`/api/double-entry-accounting/journal-entries/${entryId}/post`);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to post journal entry');
    }
  },

  reverseJournalEntry: async (entryId) => {
    try {
      const entry = await apiService.post(`/api/double-entry-accounting/journal-entries/${entryId}/reverse`);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to reverse journal entry');
    }
  },

  // Trial Balance
  getTrialBalance: async (params = {}) => {
    try {
      const trialBalance = await apiService.get('/api/double-entry-accounting/trial-balance', params);
      return trialBalance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trial balance');
    }
  },

  generateTrialBalance: async (balanceData) => {
    try {
      const trialBalance = await apiService.post('/api/double-entry-accounting/trial-balance', balanceData);
      return trialBalance;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate trial balance');
    }
  },

  // Balance Sheet
  getBalanceSheet: async (params = {}) => {
    try {
      const balanceSheet = await apiService.get('/api/double-entry-accounting/balance-sheet', params);
      return balanceSheet;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch balance sheet');
    }
  },

  generateBalanceSheet: async (sheetData) => {
    try {
      const balanceSheet = await apiService.post('/api/double-entry-accounting/balance-sheet', sheetData);
      return balanceSheet;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate balance sheet');
    }
  },

  // Profit & Loss Statement
  getProfitLossStatement: async (params = {}) => {
    try {
      const statement = await apiService.get('/api/double-entry-accounting/profit-loss-statement', params);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit & loss statement');
    }
  },

  generateProfitLossStatement: async (statementData) => {
    try {
      const statement = await apiService.post('/api/double-entry-accounting/profit-loss-statement', statementData);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate profit & loss statement');
    }
  },

  // General Ledger
  getGeneralLedger: async (params = {}) => {
    try {
      const ledger = await apiService.get('/api/double-entry-accounting/general-ledger', params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch general ledger');
    }
  },

  // Account Balances
  getAccountBalances: async (params = {}) => {
    try {
      const balances = await apiService.get('/api/double-entry-accounting/account-balances', params);
      return balances;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account balances');
    }
  },

  // Financial Year Management
  getFinancialYears: async (params = {}) => {
    try {
      const years = await apiService.get('/api/financial-years', params);
      return years;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial years');
    }
  },

  getFinancialYear: async (yearId) => {
    try {
      const year = await apiService.get(`/api/financial-years/${yearId}`);
      return year;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial year');
    }
  },

  createFinancialYear: async (yearData) => {
    try {
      const year = await apiService.post('/api/financial-years', yearData);
      return year;
    } catch (error) {
      throw new Error(error.message || 'Failed to create financial year');
    }
  },

  updateFinancialYear: async (yearId, yearData) => {
    try {
      const year = await apiService.put(`/api/financial-years/${yearId}`, yearData);
      return year;
    } catch (error) {
      throw new Error(error.message || 'Failed to update financial year');
    }
  },

  // Banking
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

  // Bank Statements
  getBankStatements: async (params = {}) => {
    try {
      const statements = await apiService.get('/api/banking/bank-statements', params);
      return statements;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statements');
    }
  },

  importBankStatement: async (statementData) => {
    try {
      const statement = await apiService.post('/api/banking/bank-statements/import', statementData);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to import bank statement');
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

  createReconciliation: async (reconciliationData) => {
    try {
      const reconciliation = await apiService.post('/api/banking/reconciliations', reconciliationData);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to create reconciliation');
    }
  },

  // Advanced Reporting
  getAdvancedReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/advanced-reporting', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch advanced reports');
    }
  },

  generateAdvancedReport: async (reportData) => {
    try {
      const report = await apiService.post('/api/advanced-reporting/generate', reportData);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate advanced report');
    }
  },

  // Export functionality
  exportAccountingData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/accounting/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export accounting data');
    }
  }
};