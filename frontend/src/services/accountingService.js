import { apiService } from './apiService';

export const accountingService = {
  // Chart of Accounts
  getChartOfAccounts: async () => {
    try {
      const accounts = await apiService.get('/api/accounting/chart-of-accounts');
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch chart of accounts');
    }
  },

  getAccount: async (accountId) => {
    try {
      const account = await apiService.get(`/api/accounting/accounts/${accountId}`);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account');
    }
  },

  createAccount: async (accountData) => {
    try {
      const result = await apiService.post('/api/accounting/accounts', accountData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create account');
    }
  },

  updateAccount: async (accountId, accountData) => {
    try {
      const result = await apiService.put(`/api/accounting/accounts/${accountId}`, accountData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update account');
    }
  },

  deleteAccount: async (accountId) => {
    try {
      const result = await apiService.delete(`/api/accounting/accounts/${accountId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete account');
    }
  },

  getAccountCategories: async () => {
    try {
      const categories = await apiService.get('/api/accounting/account-categories');
      return categories;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account categories');
    }
  },

  getAccountTypes: async () => {
    try {
      const types = await apiService.get('/api/accounting/account-types');
      return types;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account types');
    }
  },

  // Journal Entries
  getJournalEntries: async (params = {}) => {
    try {
      const entries = await apiService.get('/api/accounting/journal-entries', params);
      return entries;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch journal entries');
    }
  },

  getJournalEntry: async (entryId) => {
    try {
      const entry = await apiService.get(`/api/accounting/journal-entries/${entryId}`);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch journal entry');
    }
  },

  createJournalEntry: async (entryData) => {
    try {
      const result = await apiService.post('/api/accounting/journal-entries', entryData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create journal entry');
    }
  },

  updateJournalEntry: async (entryId, entryData) => {
    try {
      const result = await apiService.put(`/api/accounting/journal-entries/${entryId}`, entryData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update journal entry');
    }
  },

  deleteJournalEntry: async (entryId) => {
    try {
      const result = await apiService.delete(`/api/accounting/journal-entries/${entryId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete journal entry');
    }
  },

  reverseJournalEntry: async (entryId) => {
    try {
      const result = await apiService.post(`/api/accounting/journal-entries/${entryId}/reverse`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reverse journal entry');
    }
  },

  approveJournalEntry: async (entryId) => {
    try {
      const result = await apiService.post(`/api/accounting/journal-entries/${entryId}/approve`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to approve journal entry');
    }
  },

  // Ledger Management
  getGeneralLedger: async (params = {}) => {
    try {
      const ledger = await apiService.get('/api/accounting/general-ledger', params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch general ledger');
    }
  },

  getAccountLedger: async (accountId, params = {}) => {
    try {
      const ledger = await apiService.get(`/api/accounting/accounts/${accountId}/ledger`, params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch account ledger');
    }
  },

  getSubLedgers: async (params = {}) => {
    try {
      const ledgers = await apiService.get('/api/accounting/sub-ledgers', params);
      return ledgers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sub ledgers');
    }
  },

  getCustomerLedger: async (customerId, params = {}) => {
    try {
      const ledger = await apiService.get(`/api/accounting/customers/${customerId}/ledger`, params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer ledger');
    }
  },

  getVendorLedger: async (vendorId, params = {}) => {
    try {
      const ledger = await apiService.get(`/api/accounting/vendors/${vendorId}/ledger`, params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor ledger');
    }
  },

  getInventoryLedger: async (itemId, params = {}) => {
    try {
      const ledger = await apiService.get(`/api/accounting/inventory/${itemId}/ledger`, params);
      return ledger;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch inventory ledger');
    }
  },

  // Ledger Reconciliation
  reconcileAccount: async (accountId, reconciliationData) => {
    try {
      const result = await apiService.post(`/api/accounting/accounts/${accountId}/reconcile`, reconciliationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reconcile account');
    }
  },

  getReconciliationHistory: async (accountId) => {
    try {
      const history = await apiService.get(`/api/accounting/accounts/${accountId}/reconciliation-history`);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reconciliation history');
    }
  },

  // Financial Year Management
  getFinancialYears: async () => {
    try {
      const years = await apiService.get('/api/accounting/financial-years');
      return years;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial years');
    }
  },

  getCurrentFinancialYear: async () => {
    try {
      const year = await apiService.get('/api/accounting/financial-years/current');
      return year;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch current financial year');
    }
  },

  createFinancialYear: async (yearData) => {
    try {
      const result = await apiService.post('/api/accounting/financial-years', yearData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create financial year');
    }
  },

  updateFinancialYear: async (yearId, yearData) => {
    try {
      const result = await apiService.put(`/api/accounting/financial-years/${yearId}`, yearData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update financial year');
    }
  },

  closeFinancialYear: async (yearId) => {
    try {
      const result = await apiService.post(`/api/accounting/financial-years/${yearId}/close`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to close financial year');
    }
  },

  // Opening Balances
  getOpeningBalances: async (financialYearId) => {
    try {
      const balances = await apiService.get(`/api/accounting/financial-years/${financialYearId}/opening-balances`);
      return balances;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch opening balances');
    }
  },

  updateOpeningBalances: async (financialYearId, balances) => {
    try {
      const result = await apiService.post(`/api/accounting/financial-years/${financialYearId}/opening-balances`, balances);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update opening balances');
    }
  },

  // Banking Integration
  getBankAccounts: async () => {
    try {
      const accounts = await apiService.get('/api/accounting/bank-accounts');
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank accounts');
    }
  },

  getBankAccount: async (accountId) => {
    try {
      const account = await apiService.get(`/api/accounting/bank-accounts/${accountId}`);
      return account;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank account');
    }
  },

  createBankAccount: async (accountData) => {
    try {
      const result = await apiService.post('/api/accounting/bank-accounts', accountData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create bank account');
    }
  },

  updateBankAccount: async (accountId, accountData) => {
    try {
      const result = await apiService.put(`/api/accounting/bank-accounts/${accountId}`, accountData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update bank account');
    }
  },

  deleteBankAccount: async (accountId) => {
    try {
      const result = await apiService.delete(`/api/accounting/bank-accounts/${accountId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete bank account');
    }
  },

  // Bank Reconciliation
  getBankReconciliation: async (accountId, params = {}) => {
    try {
      const reconciliation = await apiService.get(`/api/accounting/bank-accounts/${accountId}/reconciliation`, params);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank reconciliation');
    }
  },

  reconcileBankAccount: async (accountId, reconciliationData) => {
    try {
      const result = await apiService.post(`/api/accounting/bank-accounts/${accountId}/reconcile`, reconciliationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reconcile bank account');
    }
  },

  getBankTransactions: async (accountId, params = {}) => {
    try {
      const transactions = await apiService.get(`/api/accounting/bank-accounts/${accountId}/transactions`, params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank transactions');
    }
  },

  // Payment Processing
  processPayment: async (paymentData) => {
    try {
      const result = await apiService.post('/api/accounting/payments', paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process payment');
    }
  },

  getPayments: async (params = {}) => {
    try {
      const payments = await apiService.get('/api/accounting/payments', params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payments');
    }
  },

  getPayment: async (paymentId) => {
    try {
      const payment = await apiService.get(`/api/accounting/payments/${paymentId}`);
      return payment;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment');
    }
  },

  // Banking Reports
  getBankingReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/accounting/banking-reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking reports');
    }
  },

  getBankStatement: async (accountId, params = {}) => {
    try {
      const statement = await apiService.get(`/api/accounting/bank-accounts/${accountId}/statement`, params);
      return statement;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank statement');
    }
  },

  // Financial Reports
  getTrialBalance: async (params = {}) => {
    try {
      const trialBalance = await apiService.get('/api/accounting/trial-balance', params);
      return trialBalance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trial balance');
    }
  },

  getProfitAndLoss: async (params = {}) => {
    try {
      const pnl = await apiService.get('/api/accounting/profit-loss', params);
      return pnl;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit and loss statement');
    }
  },

  getBalanceSheet: async (params = {}) => {
    try {
      const balanceSheet = await apiService.get('/api/accounting/balance-sheet', params);
      return balanceSheet;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch balance sheet');
    }
  },

  getCashFlow: async (params = {}) => {
    try {
      const cashFlow = await apiService.get('/api/accounting/cash-flow', params);
      return cashFlow;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cash flow statement');
    }
  },

  // Account Validation
  validateAccount: async (accountData) => {
    try {
      const result = await apiService.post('/api/accounting/validate-account', accountData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate account');
    }
  },

  validateJournalEntry: async (entryData) => {
    try {
      const result = await apiService.post('/api/accounting/validate-journal-entry', entryData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate journal entry');
    }
  },

  // Export Functions
  exportChartOfAccounts: async (format = 'excel') => {
    try {
      const result = await apiService.post('/api/accounting/export/chart-of-accounts', { format });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export chart of accounts');
    }
  },

  exportJournalEntries: async (params = {}) => {
    try {
      const result = await apiService.post('/api/accounting/export/journal-entries', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export journal entries');
    }
  },

  exportGeneralLedger: async (params = {}) => {
    try {
      const result = await apiService.post('/api/accounting/export/general-ledger', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export general ledger');
    }
  },

  exportTrialBalance: async (params = {}) => {
    try {
      const result = await apiService.post('/api/accounting/export/trial-balance', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export trial balance');
    }
  }
};