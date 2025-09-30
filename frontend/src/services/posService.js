import { apiService } from './apiService';

export const posService = {
  // Get POS session
  getPosSession: async (sessionId) => {
    try {
      const session = await apiService.get(`/api/pos/sessions/${sessionId}`);
      return session;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS session');
    }
  },

  // Create new POS session
  createPosSession: async (sessionData) => {
    try {
      const session = await apiService.post('/api/pos/sessions', sessionData);
      return session;
    } catch (error) {
      throw new Error(error.message || 'Failed to create POS session');
    }
  },

  // Update POS session
  updatePosSession: async (sessionId, sessionData) => {
    try {
      const session = await apiService.put(`/api/pos/sessions/${sessionId}`, sessionData);
      return session;
    } catch (error) {
      throw new Error(error.message || 'Failed to update POS session');
    }
  },

  // Close POS session
  closePosSession: async (sessionId) => {
    try {
      const session = await apiService.post(`/api/pos/sessions/${sessionId}/close`);
      return session;
    } catch (error) {
      throw new Error(error.message || 'Failed to close POS session');
    }
  },

  // Get POS transactions
  getPosTransactions: async (params = {}) => {
    try {
      const transactions = await apiService.get('/api/pos/transactions', params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS transactions');
    }
  },

  // Get POS transaction by ID
  getPosTransaction: async (transactionId) => {
    try {
      const transaction = await apiService.get(`/api/pos/transactions/${transactionId}`);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS transaction');
    }
  },

  // Create POS transaction
  createPosTransaction: async (transactionData) => {
    try {
      const transaction = await apiService.post('/api/pos/transactions', transactionData);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to create POS transaction');
    }
  },

  // Update POS transaction
  updatePosTransaction: async (transactionId, transactionData) => {
    try {
      const transaction = await apiService.put(`/api/pos/transactions/${transactionId}`, transactionData);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to update POS transaction');
    }
  },

  // Cancel POS transaction
  cancelPosTransaction: async (transactionId) => {
    try {
      const transaction = await apiService.post(`/api/pos/transactions/${transactionId}/cancel`);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to cancel POS transaction');
    }
  },

  // Process payment
  processPayment: async (transactionId, paymentData) => {
    try {
      const payment = await apiService.post(`/api/pos/transactions/${transactionId}/payment`, paymentData);
      return payment;
    } catch (error) {
      throw new Error(error.message || 'Failed to process payment');
    }
  },

  // Get payment methods
  getPaymentMethods: async () => {
    try {
      const methods = await apiService.get('/api/pos/payment-methods');
      return methods;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment methods');
    }
  },

  // Get POS dashboard data
  getPosDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/pos/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS dashboard data');
    }
  },

  // Get POS reports
  getPosReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/pos/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS reports');
    }
  },

  // Print receipt
  printReceipt: async (transactionId) => {
    try {
      const receipt = await apiService.get(`/api/pos/transactions/${transactionId}/receipt`);
      return receipt;
    } catch (error) {
      throw new Error(error.message || 'Failed to print receipt');
    }
  },

  // Get POS settings
  getPosSettings: async () => {
    try {
      const settings = await apiService.get('/api/pos/settings');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS settings');
    }
  },

  // Update POS settings
  updatePosSettings: async (settingsData) => {
    try {
      const settings = await apiService.put('/api/pos/settings', settingsData);
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to update POS settings');
    }
  },

  // Get POS statistics
  getPosStatistics: async (params = {}) => {
    try {
      const statistics = await apiService.get('/api/pos/statistics', params);
      return statistics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS statistics');
    }
  },

  // Get POS inventory
  getPosInventory: async (params = {}) => {
    try {
      const inventory = await apiService.get('/api/pos/inventory', params);
      return inventory;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS inventory');
    }
  },

  // Search POS inventory
  searchPosInventory: async (query, params = {}) => {
    try {
      const inventory = await apiService.get('/api/pos/inventory/search', {
        q: query,
        ...params,
      });
      return inventory;
    } catch (error) {
      throw new Error(error.message || 'Failed to search POS inventory');
    }
  },

  // Get POS customers
  getPosCustomers: async (params = {}) => {
    try {
      const customers = await apiService.get('/api/pos/customers', params);
      return customers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS customers');
    }
  },

  // Search POS customers
  searchPosCustomers: async (query, params = {}) => {
    try {
      const customers = await apiService.get('/api/pos/customers/search', {
        q: query,
        ...params,
      });
      return customers;
    } catch (error) {
      throw new Error(error.message || 'Failed to search POS customers');
    }
  },

  // Get all POS sessions
  getPosSessions: async (params = {}) => {
    try {
      const sessions = await apiService.get('/api/pos/pos-sessions', params);
      return sessions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS sessions');
    }
  },

  // Complete POS transaction
  completePosTransaction: async (transactionId, completionData) => {
    try {
      const result = await apiService.post(`/api/pos/pos-transactions/${transactionId}/complete`, completionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to complete POS transaction');
    }
  },

  // Add POS transaction item
  addPosTransactionItem: async (transactionId, itemData) => {
    try {
      const item = await apiService.post(`/api/pos/pos-transactions/${transactionId}/items`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to add POS transaction item');
    }
  },

  // Add POS transaction payment
  addPosTransactionPayment: async (transactionId, paymentData) => {
    try {
      const payment = await apiService.post(`/api/pos/pos-transactions/${transactionId}/payments`, paymentData);
      return payment;
    } catch (error) {
      throw new Error(error.message || 'Failed to add POS transaction payment');
    }
  },

  // Void POS transaction
  voidPosTransaction: async (transactionId, voidData) => {
    try {
      const result = await apiService.post(`/api/pos/pos-transactions/${transactionId}/void`, voidData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to void POS transaction');
    }
  },

  // Create store
  createStore: async (storeData) => {
    try {
      const store = await apiService.post('/api/pos/stores', storeData);
      return store;
    } catch (error) {
      throw new Error(error.message || 'Failed to create store');
    }
  },

  // Get stores
  getStores: async (params = {}) => {
    try {
      const stores = await apiService.get('/api/pos/stores', params);
      return stores;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch stores');
    }
  },

  // Generate POS receipt
  generatePosReceipt: async (transactionId, receiptData) => {
    try {
      const receipt = await apiService.post(`/api/pos/pos-transactions/${transactionId}/receipt`, receiptData);
      return receipt;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate POS receipt');
    }
  },

  // Print POS receipt
  printPosReceipt: async (transactionId, printData) => {
    try {
      const result = await apiService.post(`/api/pos/pos-transactions/${transactionId}/print-receipt`, printData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to print POS receipt');
    }
  },

  // Get POS sales report
  getPosSalesReport: async (params = {}) => {
    try {
      const report = await apiService.get('/api/pos/pos-analytics/sales-report', params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch POS sales report');
    }
  },

  // Link POS exchange
  linkPosExchange: async (transactionId, exchangeData) => {
    try {
      const result = await apiService.post(`/api/pos/pos-transactions/${transactionId}/link-exchange`, exchangeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to link POS exchange');
    }
  },

  // Link POS return
  linkPosReturn: async (transactionId, returnData) => {
    try {
      const result = await apiService.post(`/api/pos/pos-transactions/${transactionId}/link-return`, returnData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to link POS return');
    }
  },
};