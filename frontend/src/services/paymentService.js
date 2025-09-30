import { apiService } from './apiService';

export const paymentService = {
  // Payment Management
  getPayments: async (params = {}) => {
    try {
      const payments = await apiService.get('/api/payments', params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payments');
    }
  },

  getPayment: async (paymentId) => {
    try {
      const payment = await apiService.get(`/api/payments/${paymentId}`);
      return payment;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment');
    }
  },

  createPayment: async (paymentData) => {
    try {
      const result = await apiService.post('/api/payments', paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create payment');
    }
  },

  updatePayment: async (paymentId, paymentData) => {
    try {
      const result = await apiService.put(`/api/payments/${paymentId}`, paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update payment');
    }
  },

  deletePayment: async (paymentId) => {
    try {
      const result = await apiService.delete(`/api/payments/${paymentId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete payment');
    }
  },

  processPayment: async (paymentId) => {
    try {
      const result = await apiService.post(`/api/payments/${paymentId}/process`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process payment');
    }
  },

  // Payment Reconciliation
  getReconciliations: async (params = {}) => {
    try {
      const reconciliations = await apiService.get('/api/payments/reconciliation', params);
      return reconciliations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reconciliations');
    }
  },

  reconcilePayment: async (reconciliationData) => {
    try {
      const result = await apiService.post('/api/payments/reconciliation', reconciliationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to reconcile payment');
    }
  },

  // Payment Reports
  getPaymentReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/payments/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment reports');
    }
  },

  exportPaymentReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/payments/reports/export/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export payment report');
    }
  },

  // Payment Analytics
  getPaymentAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/payments/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment analytics');
    }
  },

  // Cash Management
  getCashTransactions: async (params = {}) => {
    try {
      const transactions = await apiService.get('/api/payments/cash', params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cash transactions');
    }
  },

  createCashTransaction: async (transactionData) => {
    try {
      const result = await apiService.post('/api/payments/cash', transactionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create cash transaction');
    }
  },

  // Card Payments
  getCardPayments: async (params = {}) => {
    try {
      const payments = await apiService.get('/api/payments/card', params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch card payments');
    }
  },

  processCardPayment: async (paymentData) => {
    try {
      const result = await apiService.post('/api/payments/card/process', paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process card payment');
    }
  },

  // Digital Payments
  getDigitalPayments: async (params = {}) => {
    try {
      const payments = await apiService.get('/api/payments/digital', params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch digital payments');
    }
  },

  processUPIPayment: async (paymentData) => {
    try {
      const result = await apiService.post('/api/payments/digital/upi', paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process UPI payment');
    }
  },

  processWalletPayment: async (paymentData) => {
    try {
      const result = await apiService.post('/api/payments/digital/wallet', paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process wallet payment');
    }
  },

  // Bank Transfers
  getBankTransfers: async (params = {}) => {
    try {
      const transfers = await apiService.get('/api/payments/bank-transfers', params);
      return transfers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank transfers');
    }
  },

  initiateBankTransfer: async (transferData) => {
    try {
      const result = await apiService.post('/api/payments/bank-transfers', transferData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to initiate bank transfer');
    }
  },

  // Financial Transactions
  getTransactions: async (params = {}) => {
    try {
      const transactions = await apiService.get('/api/financial/transactions', params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch transactions');
    }
  },

  createTransaction: async (transactionData) => {
    try {
      const result = await apiService.post('/api/financial/transactions', transactionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create transaction');
    }
  },

  matchTransaction: async (transactionId, matchData) => {
    try {
      const result = await apiService.post(`/api/financial/transactions/${transactionId}/match`, matchData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to match transaction');
    }
  },

  getTransactionReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/financial/transactions/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch transaction reports');
    }
  },

  getTransactionAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/financial/transactions/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch transaction analytics');
    }
  },

  // Banking APIs
  getBankAccounts: async () => {
    try {
      const accounts = await apiService.get('/api/banking/accounts');
      return accounts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bank accounts');
    }
  },

  syncBankAccount: async (accountId) => {
    try {
      const result = await apiService.post(`/api/banking/accounts/${accountId}/sync`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to sync bank account');
    }
  },

  // Payment Gateways
  getPaymentGateways: async () => {
    try {
      const gateways = await apiService.get('/api/payment-gateways');
      return gateways;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment gateways');
    }
  },

  configureGateway: async (gatewayId, config) => {
    try {
      const result = await apiService.put(`/api/payment-gateways/${gatewayId}/configure`, config);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to configure payment gateway');
    }
  },

  // Financial Reporting
  getFinancialReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/financial/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch financial reports');
    }
  },

  generateFinancialReport: async (reportType, params = {}) => {
    try {
      const report = await apiService.post(`/api/financial/reports/generate/${reportType}`, params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate financial report');
    }
  },

  // Compliance Reporting
  getComplianceReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/compliance/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch compliance reports');
    }
  },

  generateComplianceReport: async (reportType, params = {}) => {
    try {
      const report = await apiService.post(`/api/compliance/reports/generate/${reportType}`, params);
      return report;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate compliance report');
    }
  }
};