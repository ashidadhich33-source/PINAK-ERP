import { apiService } from './apiService';

export const journalEntriesService = {
  // Create journal entry
  createJournalEntry: async (entryData) => {
    try {
      const entry = await apiService.post('/api/accounting/journal-entries', entryData);
      return entry;
    } catch (error) {
      throw new Error(error.message || 'Failed to create journal entry');
    }
  },

  // Add journal entry item
  addJournalEntryItem: async (entryId, itemData) => {
    try {
      const item = await apiService.post(`/api/accounting/journal-entries/${entryId}/items`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to add journal entry item');
    }
  },

  // Post journal entry
  postJournalEntry: async (entryId, postData) => {
    try {
      const result = await apiService.post(`/api/accounting/journal-entries/${entryId}/post`, postData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to post journal entry');
    }
  },

  // Reverse journal entry
  reverseJournalEntry: async (entryId, reverseData) => {
    try {
      const result = await apiService.post(`/api/accounting/journal-entries/${entryId}/reverse`, reverseData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reverse journal entry');
    }
  },

  // Get trial balance
  getTrialBalance: async (params = {}) => {
    try {
      const trialBalance = await apiService.post('/api/accounting/trial-balance', params);
      return trialBalance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trial balance');
    }
  },

  // Get balance sheet
  getBalanceSheet: async (params = {}) => {
    try {
      const balanceSheet = await apiService.post('/api/accounting/balance-sheet', params);
      return balanceSheet;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch balance sheet');
    }
  },

  // Get profit & loss statement
  getProfitLossStatement: async (params = {}) => {
    try {
      const profitLoss = await apiService.post('/api/accounting/profit-loss-statement', params);
      return profitLoss;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch profit & loss statement');
    }
  },

  // Get cash flow statement
  getCashFlowStatement: async (params = {}) => {
    try {
      const cashFlow = await apiService.post('/api/accounting/cash-flow-statement', params);
      return cashFlow;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cash flow statement');
    }
  },

  // Create account reconciliation
  createAccountReconciliation: async (reconciliationData) => {
    try {
      const reconciliation = await apiService.post('/api/accounting/account-reconciliation', reconciliationData);
      return reconciliation;
    } catch (error) {
      throw new Error(error.message || 'Failed to create account reconciliation');
    }
  },

  // Add reconciliation item
  addReconciliationItem: async (reconciliationId, itemData) => {
    try {
      const item = await apiService.post(`/api/accounting/account-reconciliation/${reconciliationId}/items`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to add reconciliation item');
    }
  },

  // Create accounting period
  createAccountingPeriod: async (periodData) => {
    try {
      const period = await apiService.post('/api/accounting/accounting-periods', periodData);
      return period;
    } catch (error) {
      throw new Error(error.message || 'Failed to create accounting period');
    }
  },

  // Close accounting period
  closeAccountingPeriod: async (periodId, closeData) => {
    try {
      const result = await apiService.post(`/api/accounting/accounting-periods/${periodId}/close`, closeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to close accounting period');
    }
  },

  // Get financial summary
  getFinancialSummary: async (params = {}) => {
    try {
      const summary = await apiService.get('/api/accounting/financial-summary', params);
      return summary;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial summary');
    }
  },
};