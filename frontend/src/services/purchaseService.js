import { apiService } from './apiService';

export const purchaseService = {
  // Purchase Orders
  getPurchaseOrders: async (params = {}) => {
    try {
      const orders = await apiService.get('/api/purchases/orders', params);
      return orders;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase orders');
    }
  },

  getPurchaseOrder: async (orderId) => {
    try {
      const order = await apiService.get(`/api/purchases/orders/${orderId}`);
      return order;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase order');
    }
  },

  createPurchaseOrder: async (orderData) => {
    try {
      const result = await apiService.post('/api/purchases/orders', orderData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create purchase order');
    }
  },

  updatePurchaseOrder: async (orderId, orderData) => {
    try {
      const result = await apiService.put(`/api/purchases/orders/${orderId}`, orderData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update purchase order');
    }
  },

  deletePurchaseOrder: async (orderId) => {
    try {
      const result = await apiService.delete(`/api/purchases/orders/${orderId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete purchase order');
    }
  },

  approvePurchaseOrder: async (orderId) => {
    try {
      const result = await apiService.post(`/api/purchases/orders/${orderId}/approve`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to approve purchase order');
    }
  },

  sendPurchaseOrder: async (orderId) => {
    try {
      const result = await apiService.post(`/api/purchases/orders/${orderId}/send`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send purchase order');
    }
  },

  cancelPurchaseOrder: async (orderId) => {
    try {
      const result = await apiService.post(`/api/purchases/orders/${orderId}/cancel`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to cancel purchase order');
    }
  },

  receivePurchaseOrder: async (orderId, receiveData) => {
    try {
      const result = await apiService.post(`/api/purchases/orders/${orderId}/receive`, receiveData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to receive purchase order');
    }
  },

  // Purchase Invoices
  getPurchaseInvoices: async (params = {}) => {
    try {
      const invoices = await apiService.get('/api/purchases/invoices', params);
      return invoices;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase invoices');
    }
  },

  getPurchaseInvoice: async (invoiceId) => {
    try {
      const invoice = await apiService.get(`/api/purchases/invoices/${invoiceId}`);
      return invoice;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase invoice');
    }
  },

  createPurchaseInvoice: async (invoiceData) => {
    try {
      const result = await apiService.post('/api/purchases/invoices', invoiceData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create purchase invoice');
    }
  },

  updatePurchaseInvoice: async (invoiceId, invoiceData) => {
    try {
      const result = await apiService.put(`/api/purchases/invoices/${invoiceId}`, invoiceData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update purchase invoice');
    }
  },

  deletePurchaseInvoice: async (invoiceId) => {
    try {
      const result = await apiService.delete(`/api/purchases/invoices/${invoiceId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete purchase invoice');
    }
  },

  approvePurchaseInvoice: async (invoiceId) => {
    try {
      const result = await apiService.post(`/api/purchases/invoices/${invoiceId}/approve`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to approve purchase invoice');
    }
  },

  matchPurchaseInvoice: async (invoiceId, matchData) => {
    try {
      const result = await apiService.post(`/api/purchases/invoices/${invoiceId}/match`, matchData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to match purchase invoice');
    }
  },

  // Purchase Invoice Payments
  getPurchaseInvoicePayments: async (invoiceId) => {
    try {
      const payments = await apiService.get(`/api/purchases/invoices/${invoiceId}/payments`);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch invoice payments');
    }
  },

  createPurchaseInvoicePayment: async (invoiceId, paymentData) => {
    try {
      const result = await apiService.post(`/api/purchases/invoices/${invoiceId}/payments`, paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create invoice payment');
    }
  },

  updatePurchaseInvoicePayment: async (paymentId, paymentData) => {
    try {
      const result = await apiService.put(`/api/purchases/payments/${paymentId}`, paymentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update invoice payment');
    }
  },

  deletePurchaseInvoicePayment: async (paymentId) => {
    try {
      const result = await apiService.delete(`/api/purchases/payments/${paymentId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete invoice payment');
    }
  },

  // Vendors
  getVendors: async (params = {}) => {
    try {
      const vendors = await apiService.get('/api/purchases/vendors', params);
      return vendors;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendors');
    }
  },

  getVendor: async (vendorId) => {
    try {
      const vendor = await apiService.get(`/api/purchases/vendors/${vendorId}`);
      return vendor;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor');
    }
  },

  createVendor: async (vendorData) => {
    try {
      const result = await apiService.post('/api/purchases/vendors', vendorData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create vendor');
    }
  },

  updateVendor: async (vendorId, vendorData) => {
    try {
      const result = await apiService.put(`/api/purchases/vendors/${vendorId}`, vendorData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update vendor');
    }
  },

  deleteVendor: async (vendorId) => {
    try {
      const result = await apiService.delete(`/api/purchases/vendors/${vendorId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete vendor');
    }
  },

  // Vendor Performance
  getVendorPerformance: async (vendorId, params = {}) => {
    try {
      const performance = await apiService.get(`/api/purchases/vendors/${vendorId}/performance`, params);
      return performance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor performance');
    }
  },

  updateVendorRating: async (vendorId, ratingData) => {
    try {
      const result = await apiService.post(`/api/purchases/vendors/${vendorId}/rating`, ratingData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update vendor rating');
    }
  },

  // Vendor Payments
  getVendorPayments: async (vendorId, params = {}) => {
    try {
      const payments = await apiService.get(`/api/purchases/vendors/${vendorId}/payments`, params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor payments');
    }
  },

  getVendorPaymentHistory: async (vendorId, params = {}) => {
    try {
      const history = await apiService.get(`/api/purchases/vendors/${vendorId}/payment-history`, params);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor payment history');
    }
  },

  // Items
  getItems: async (params = {}) => {
    try {
      const items = await apiService.get('/api/inventory/items', params);
      return items;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch items');
    }
  },

  getItem: async (itemId) => {
    try {
      const item = await apiService.get(`/api/inventory/items/${itemId}`);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch item');
    }
  },

  // Purchase Analytics
  getPurchaseReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/purchases/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase reports');
    }
  },

  getPurchaseAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/purchases/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase analytics');
    }
  },

  getVendorAnalysis: async (params = {}) => {
    try {
      const analysis = await apiService.get('/api/purchases/vendor-analysis', params);
      return analysis;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch vendor analysis');
    }
  },

  getCostAnalysis: async (params = {}) => {
    try {
      const analysis = await apiService.get('/api/purchases/cost-analysis', params);
      return analysis;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cost analysis');
    }
  },

  getTrendAnalysis: async (params = {}) => {
    try {
      const analysis = await apiService.get('/api/purchases/trend-analysis', params);
      return analysis;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch trend analysis');
    }
  },

  // Purchase Order Reports
  getPurchaseOrderReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/purchases/order-reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase order reports');
    }
  },

  getPurchaseOrderSummary: async (params = {}) => {
    try {
      const summary = await apiService.get('/api/purchases/order-summary', params);
      return summary;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase order summary');
    }
  },

  getPurchaseOrderStatus: async (params = {}) => {
    try {
      const status = await apiService.get('/api/purchases/order-status', params);
      return status;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch purchase order status');
    }
  },

  // Export Functions
  exportPurchaseOrders: async (params = {}) => {
    try {
      const result = await apiService.post('/api/purchases/export/orders', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export purchase orders');
    }
  },

  exportPurchaseInvoices: async (params = {}) => {
    try {
      const result = await apiService.post('/api/purchases/export/invoices', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export purchase invoices');
    }
  },

  exportVendorList: async (params = {}) => {
    try {
      const result = await apiService.post('/api/purchases/export/vendors', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export vendor list');
    }
  },

  exportPurchaseReports: async (params = {}) => {
    try {
      const result = await apiService.post('/api/purchases/export/reports', params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export purchase reports');
    }
  },

  // Validation
  validatePurchaseOrder: async (orderData) => {
    try {
      const result = await apiService.post('/api/purchases/validate/order', orderData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate purchase order');
    }
  },

  validatePurchaseInvoice: async (invoiceData) => {
    try {
      const result = await apiService.post('/api/purchases/validate/invoice', invoiceData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate purchase invoice');
    }
  },

  validateVendor: async (vendorData) => {
    try {
      const result = await apiService.post('/api/purchases/validate/vendor', vendorData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate vendor');
    }
  }
};