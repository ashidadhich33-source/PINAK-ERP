import { apiService } from './apiService';

export const customersService = {
  // Get all customers
  getCustomers: async (params = {}) => {
    try {
      const customers = await apiService.get('/api/customers/', params);
      return customers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customers');
    }
  },

  // Get customer by ID
  getCustomer: async (customerId) => {
    try {
      const customer = await apiService.get(`/api/customers/${customerId}`);
      return customer;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer');
    }
  },

  // Create new customer
  createCustomer: async (customerData) => {
    try {
      const customer = await apiService.post('/api/customers/', customerData);
      return customer;
    } catch (error) {
      throw new Error(error.message || 'Failed to create customer');
    }
  },

  // Update customer
  updateCustomer: async (customerId, customerData) => {
    try {
      const customer = await apiService.put(`/api/customers/${customerId}`, customerData);
      return customer;
    } catch (error) {
      throw new Error(error.message || 'Failed to update customer');
    }
  },

  // Delete customer
  deleteCustomer: async (customerId) => {
    try {
      await apiService.delete(`/api/customers/${customerId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete customer');
    }
  },

  // Toggle customer status
  toggleCustomerStatus: async (customerId) => {
    try {
      const response = await apiService.put(`/api/customers/${customerId}/toggle-status`);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to toggle customer status');
    }
  },

  // Get customer statistics
  getCustomerStats: async (customerId) => {
    try {
      const stats = await apiService.get(`/api/customers/${customerId}/stats`);
      return stats;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer statistics');
    }
  },

  // Get customer orders
  getCustomerOrders: async (customerId, params = {}) => {
    try {
      const orders = await apiService.get(`/api/customers/${customerId}/orders`, params);
      return orders;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer orders');
    }
  },

  // Get customer payments
  getCustomerPayments: async (customerId, params = {}) => {
    try {
      const payments = await apiService.get(`/api/customers/${customerId}/payments`, params);
      return payments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer payments');
    }
  },

  // Search customers
  searchCustomers: async (query, params = {}) => {
    try {
      const customers = await apiService.get('/api/customers/search', {
        q: query,
        ...params,
      });
      return customers;
    } catch (error) {
      throw new Error(error.message || 'Failed to search customers');
    }
  },

  // Export customers
  exportCustomers: async (format = 'csv', filters = {}) => {
    try {
      const response = await apiService.get('/api/customers/export', {
        format,
        ...filters,
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export customers');
    }
  },

  // Import customers
  importCustomers: async (file, onProgress = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiService.upload('/api/customers/import', formData, onProgress);
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to import customers');
    }
  },

  // Get customer groups
  getCustomerGroups: async () => {
    try {
      const groups = await apiService.get('/api/customers/groups');
      return groups;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer groups');
    }
  },

  // Create customer group
  createCustomerGroup: async (groupData) => {
    try {
      const group = await apiService.post('/api/customers/groups', groupData);
      return group;
    } catch (error) {
      throw new Error(error.message || 'Failed to create customer group');
    }
  },

  // Update customer group
  updateCustomerGroup: async (groupId, groupData) => {
    try {
      const group = await apiService.put(`/api/customers/groups/${groupId}`, groupData);
      return group;
    } catch (error) {
      throw new Error(error.message || 'Failed to update customer group');
    }
  },

  // Delete customer group
  deleteCustomerGroup: async (groupId) => {
    try {
      await apiService.delete(`/api/customers/groups/${groupId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete customer group');
    }
  },
};