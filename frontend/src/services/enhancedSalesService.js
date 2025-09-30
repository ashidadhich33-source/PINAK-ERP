import { apiService } from './apiService';

export const enhancedSalesService = {
  // Sale Challans
  getSaleChallans: async (params = {}) => {
    try {
      const challans = await apiService.get('/api/enhanced-sales/challans', params);
      return challans;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale challans');
    }
  },

  getSaleChallan: async (challanId) => {
    try {
      const challan = await apiService.get(`/api/enhanced-sales/challans/${challanId}`);
      return challan;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale challan');
    }
  },

  createSaleChallan: async (challanData) => {
    try {
      const challan = await apiService.post('/api/enhanced-sales/challans', challanData);
      return challan;
    } catch (error) {
      throw new Error(error.message || 'Failed to create sale challan');
    }
  },

  updateSaleChallan: async (challanId, challanData) => {
    try {
      const challan = await apiService.put(`/api/enhanced-sales/challans/${challanId}`, challanData);
      return challan;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale challan');
    }
  },

  deleteSaleChallan: async (challanId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/challans/${challanId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete sale challan');
    }
  },

  confirmSaleChallan: async (challanId) => {
    try {
      const challan = await apiService.post(`/api/enhanced-sales/challans/${challanId}/confirm`);
      return challan;
    } catch (error) {
      throw new Error(error.message || 'Failed to confirm sale challan');
    }
  },

  deliverSaleChallan: async (challanId) => {
    try {
      const challan = await apiService.post(`/api/enhanced-sales/challans/${challanId}/deliver`);
      return challan;
    } catch (error) {
      throw new Error(error.message || 'Failed to deliver sale challan');
    }
  },

  // Bill Series Management
  getBillSeries: async (params = {}) => {
    try {
      const series = await apiService.get('/api/enhanced-sales/bill-series', params);
      return series;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bill series');
    }
  },

  getBillSeriesById: async (seriesId) => {
    try {
      const series = await apiService.get(`/api/enhanced-sales/bill-series/${seriesId}`);
      return series;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch bill series');
    }
  },

  createBillSeries: async (seriesData) => {
    try {
      const series = await apiService.post('/api/enhanced-sales/bill-series', seriesData);
      return series;
    } catch (error) {
      throw new Error(error.message || 'Failed to create bill series');
    }
  },

  updateBillSeries: async (seriesId, seriesData) => {
    try {
      const series = await apiService.put(`/api/enhanced-sales/bill-series/${seriesId}`, seriesData);
      return series;
    } catch (error) {
      throw new Error(error.message || 'Failed to update bill series');
    }
  },

  deleteBillSeries: async (seriesId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/bill-series/${seriesId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete bill series');
    }
  },

  generateBillNumber: async (seriesId) => {
    try {
      const number = await apiService.post(`/api/enhanced-sales/bill-series/${seriesId}/generate-number`);
      return number;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate bill number');
    }
  },

  // Payment Modes
  getPaymentModes: async (params = {}) => {
    try {
      const modes = await apiService.get('/api/enhanced-sales/payment-modes', params);
      return modes;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment modes');
    }
  },

  getPaymentMode: async (modeId) => {
    try {
      const mode = await apiService.get(`/api/enhanced-sales/payment-modes/${modeId}`);
      return mode;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment mode');
    }
  },

  createPaymentMode: async (modeData) => {
    try {
      const mode = await apiService.post('/api/enhanced-sales/payment-modes', modeData);
      return mode;
    } catch (error) {
      throw new Error(error.message || 'Failed to create payment mode');
    }
  },

  updatePaymentMode: async (modeId, modeData) => {
    try {
      const mode = await apiService.put(`/api/enhanced-sales/payment-modes/${modeId}`, modeData);
      return mode;
    } catch (error) {
      throw new Error(error.message || 'Failed to update payment mode');
    }
  },

  deletePaymentMode: async (modeId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/payment-modes/${modeId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete payment mode');
    }
  },

  // Staff Management
  getStaff: async (params = {}) => {
    try {
      const staff = await apiService.get('/api/enhanced-sales/staff', params);
      return staff;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch staff');
    }
  },

  getStaffMember: async (staffId) => {
    try {
      const member = await apiService.get(`/api/enhanced-sales/staff/${staffId}`);
      return member;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch staff member');
    }
  },

  createStaff: async (staffData) => {
    try {
      const member = await apiService.post('/api/enhanced-sales/staff', staffData);
      return member;
    } catch (error) {
      throw new Error(error.message || 'Failed to create staff member');
    }
  },

  updateStaff: async (staffId, staffData) => {
    try {
      const member = await apiService.put(`/api/enhanced-sales/staff/${staffId}`, staffData);
      return member;
    } catch (error) {
      throw new Error(error.message || 'Failed to update staff member');
    }
  },

  deleteStaff: async (staffId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/staff/${staffId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete staff member');
    }
  },

  // Staff Targets
  getStaffTargets: async (params = {}) => {
    try {
      const targets = await apiService.get('/api/enhanced-sales/staff-targets', params);
      return targets;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch staff targets');
    }
  },

  getStaffTarget: async (targetId) => {
    try {
      const target = await apiService.get(`/api/enhanced-sales/staff-targets/${targetId}`);
      return target;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch staff target');
    }
  },

  createStaffTarget: async (targetData) => {
    try {
      const target = await apiService.post('/api/enhanced-sales/staff-targets', targetData);
      return target;
    } catch (error) {
      throw new Error(error.message || 'Failed to create staff target');
    }
  },

  updateStaffTarget: async (targetId, targetData) => {
    try {
      const target = await apiService.put(`/api/enhanced-sales/staff-targets/${targetId}`, targetData);
      return target;
    } catch (error) {
      throw new Error(error.message || 'Failed to update staff target');
    }
  },

  deleteStaffTarget: async (targetId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/staff-targets/${targetId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete staff target');
    }
  },

  // Sale Returns
  getSaleReturns: async (params = {}) => {
    try {
      const returns = await apiService.get('/api/sale-returns', params);
      return returns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale returns');
    }
  },

  getSaleReturn: async (returnId) => {
    try {
      const returnItem = await apiService.get(`/api/sale-returns/${returnId}`);
      return returnItem;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale return');
    }
  },

  createSaleReturn: async (returnData) => {
    try {
      const returnItem = await apiService.post('/api/sale-returns', returnData);
      return returnItem;
    } catch (error) {
      throw new Error(error.message || 'Failed to create sale return');
    }
  },

  updateSaleReturn: async (returnId, returnData) => {
    try {
      const returnItem = await apiService.put(`/api/sale-returns/${returnId}`, returnData);
      return returnItem;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale return');
    }
  },

  deleteSaleReturn: async (returnId) => {
    try {
      await apiService.delete(`/api/sale-returns/${returnId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete sale return');
    }
  },

  // Sale Orders
  getSaleOrders: async (params = {}) => {
    try {
      const orders = await apiService.get('/api/enhanced-sales/orders', params);
      return orders;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale orders');
    }
  },

  getSaleOrder: async (orderId) => {
    try {
      const order = await apiService.get(`/api/enhanced-sales/orders/${orderId}`);
      return order;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale order');
    }
  },

  createSaleOrder: async (orderData) => {
    try {
      const order = await apiService.post('/api/enhanced-sales/orders', orderData);
      return order;
    } catch (error) {
      throw new Error(error.message || 'Failed to create sale order');
    }
  },

  updateSaleOrder: async (orderId, orderData) => {
    try {
      const order = await apiService.put(`/api/enhanced-sales/orders/${orderId}`, orderData);
      return order;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale order');
    }
  },

  deleteSaleOrder: async (orderId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/orders/${orderId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete sale order');
    }
  },

  // Sale Invoices
  getSaleInvoices: async (params = {}) => {
    try {
      const invoices = await apiService.get('/api/enhanced-sales/invoices', params);
      return invoices;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale invoices');
    }
  },

  getSaleInvoice: async (invoiceId) => {
    try {
      const invoice = await apiService.get(`/api/enhanced-sales/invoices/${invoiceId}`);
      return invoice;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sale invoice');
    }
  },

  createSaleInvoice: async (invoiceData) => {
    try {
      const invoice = await apiService.post('/api/enhanced-sales/invoices', invoiceData);
      return invoice;
    } catch (error) {
      throw new Error(error.message || 'Failed to create sale invoice');
    }
  },

  updateSaleInvoice: async (invoiceId, invoiceData) => {
    try {
      const invoice = await apiService.put(`/api/enhanced-sales/invoices/${invoiceId}`, invoiceData);
      return invoice;
    } catch (error) {
      throw new Error(error.message || 'Failed to update sale invoice');
    }
  },

  deleteSaleInvoice: async (invoiceId) => {
    try {
      await apiService.delete(`/api/enhanced-sales/invoices/${invoiceId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete sale invoice');
    }
  },

  // Sales Analytics
  getSalesAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/enhanced-sales/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales analytics');
    }
  },

  getSalesDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/enhanced-sales/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales dashboard');
    }
  },

  getSalesReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/enhanced-sales/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch sales reports');
    }
  },

  // Export functionality
  exportSalesData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/enhanced-sales/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export sales data');
    }
  }
};