import { apiService } from './apiService';

export const salesService = {
  // Get all sales
  getSales: async (params = {}) => {
    try {
      const sales = await apiService.get('/api/sales/', params);
      return sales;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales');
    }
  },

  // Get sale by ID
  getSale: async (saleId) => {
    try {
      const sale = await apiService.get(`/api/sales/${saleId}`);
      return sale;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale');
    }
  },

  // Create new sale
  createSale: async (saleData) => {
    try {
      const sale = await apiService.post('/api/sales/', saleData);
      return sale;
    } catch (error) {
      throw new Error(error.message || 'Failed to create sale');
    }
  },

  // Update sale
  updateSale: async (saleId, saleData) => {
    try {
      const sale = await apiService.put(`/api/sales/${saleId}`, saleData);
      return sale;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale');
    }
  },

  // Delete sale
  deleteSale: async (saleId) => {
    try {
      await apiService.delete(`/api/sales/${saleId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete sale');
    }
  },

  // Cancel sale
  cancelSale: async (saleId) => {
    try {
      const sale = await apiService.post(`/api/sales/${saleId}/cancel`);
      return sale;
    } catch (error) {
      throw new Error(error.message || 'Failed to cancel sale');
    }
  },

  // Complete sale
  completeSale: async (saleId) => {
    try {
      const sale = await apiService.post(`/api/sales/${saleId}/complete`);
      return sale;
    } catch (error) {
      throw new Error(error.message || 'Failed to complete sale');
    }
  },

  // Get sale items
  getSaleItems: async (saleId) => {
    try {
      const items = await apiService.get(`/api/sales/${saleId}/items`);
      return items;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale items');
    }
  },

  // Add sale item
  addSaleItem: async (saleId, itemData) => {
    try {
      const item = await apiService.post(`/api/sales/${saleId}/items`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to add sale item');
    }
  },

  // Update sale item
  updateSaleItem: async (saleId, itemId, itemData) => {
    try {
      const item = await apiService.put(`/api/sales/${saleId}/items/${itemId}`, itemData);
      return item;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale item');
    }
  },

  // Remove sale item
  removeSaleItem: async (saleId, itemId) => {
    try {
      await apiService.delete(`/api/sales/${saleId}/items/${itemId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove sale item');
    }
  },

  // Get sale payments
  getSalePayments: async (saleId) => {
    try {
      const payments = await apiService.get(`/api/sales/${saleId}/payments`);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale payments');
    }
  },

  // Add sale payment
  addSalePayment: async (saleId, paymentData) => {
    try {
      const payment = await apiService.post(`/api/sales/${saleId}/payments`, paymentData);
      return payment;
    } catch (error) {
      throw new Error(error.message || 'Failed to add sale payment');
    }
  },

  // Get sale statistics
  getSaleStatistics: async (params = {}) => {
    try {
      const statistics = await apiService.get('/api/sales/statistics', params);
      return statistics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale statistics');
    }
  },

  // Get sale reports
  getSaleReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/sales/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale reports');
    }
  },

  // Export sales
  exportSales: async (format = 'csv', filters = {}) => {
    try {
      const response = await apiService.get('/api/sales/export', {
        format,
        ...filters,
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export sales');
    }
  },

  // Search sales
  searchSales: async (query, params = {}) => {
    try {
      const sales = await apiService.get('/api/sales/search', {
        q: query,
        ...params,
      });
      return sales;
    } catch (error) {
      throw new Error(error.message || 'Failed to search sales');
    }
  },

  // Get sale dashboard
  getSaleDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/sales/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale dashboard');
    }
  },

  // Get sale trends
  getSaleTrends: async (params = {}) => {
    try {
      const trends = await apiService.get('/api/sales/trends', params);
      return trends;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale trends');
    }
  },

  // Get top selling products
  getTopSellingProducts: async (params = {}) => {
    try {
      const products = await apiService.get('/api/sales/top-products', params);
      return products;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch top selling products');
    }
  },

  // Get customer sales
  getCustomerSales: async (customerId, params = {}) => {
    try {
      const sales = await apiService.get(`/api/sales/customer/${customerId}`, params);
      return sales;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer sales');
    }
  },

  // Get sales by date range
  getSalesByDateRange: async (startDate, endDate, params = {}) => {
    try {
      const sales = await apiService.get('/api/sales/date-range', {
        start_date: startDate,
        end_date: endDate,
        ...params,
      });
      return sales;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales by date range');
    }
  },
};