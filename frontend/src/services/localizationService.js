import { apiService } from './apiService';

export const localizationService = {
  // Indian Geography
  getIndianStates: async () => {
    try {
      const states = await apiService.get('/api/localization/indian/states');
      return states;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian states');
    }
  },

  getIndianState: async (stateId) => {
    try {
      const state = await apiService.get(`/api/localization/indian/states/${stateId}`);
      return state;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian state');
    }
  },

  createIndianState: async (stateData) => {
    try {
      const result = await apiService.post('/api/localization/indian/states', stateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create Indian state');
    }
  },

  updateIndianState: async (stateId, stateData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/states/${stateId}`, stateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update Indian state');
    }
  },

  deleteIndianState: async (stateId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/states/${stateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete Indian state');
    }
  },

  getIndianCities: async () => {
    try {
      const cities = await apiService.get('/api/localization/indian/cities');
      return cities;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian cities');
    }
  },

  getIndianCity: async (cityId) => {
    try {
      const city = await apiService.get(`/api/localization/indian/cities/${cityId}`);
      return city;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian city');
    }
  },

  createIndianCity: async (cityData) => {
    try {
      const result = await apiService.post('/api/localization/indian/cities', cityData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create Indian city');
    }
  },

  updateIndianCity: async (cityId, cityData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/cities/${cityId}`, cityData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update Indian city');
    }
  },

  deleteIndianCity: async (cityId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/cities/${cityId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete Indian city');
    }
  },

  getIndianPincodes: async () => {
    try {
      const pincodes = await apiService.get('/api/localization/indian/pincodes');
      return pincodes;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian pincodes');
    }
  },

  getIndianPincode: async (pincodeId) => {
    try {
      const pincode = await apiService.get(`/api/localization/indian/pincodes/${pincodeId}`);
      return pincode;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian pincode');
    }
  },

  createIndianPincode: async (pincodeData) => {
    try {
      const result = await apiService.post('/api/localization/indian/pincodes', pincodeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create Indian pincode');
    }
  },

  updateIndianPincode: async (pincodeId, pincodeData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/pincodes/${pincodeId}`, pincodeData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update Indian pincode');
    }
  },

  deleteIndianPincode: async (pincodeId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/pincodes/${pincodeId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete Indian pincode');
    }
  },

  // Address Validation
  validateIndianAddress: async (addressData) => {
    try {
      const result = await apiService.post('/api/localization/indian/validate-address', addressData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate Indian address');
    }
  },

  // Indian GST
  getGSTRates: async () => {
    try {
      const rates = await apiService.get('/api/localization/indian/gst/rates');
      return rates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST rates');
    }
  },

  getGSTRate: async (rateId) => {
    try {
      const rate = await apiService.get(`/api/localization/indian/gst/rates/${rateId}`);
      return rate;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST rate');
    }
  },

  createGSTRate: async (rateData) => {
    try {
      const result = await apiService.post('/api/localization/indian/gst/rates', rateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create GST rate');
    }
  },

  updateGSTRate: async (rateId, rateData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/gst/rates/${rateId}`, rateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update GST rate');
    }
  },

  deleteGSTRate: async (rateId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/gst/rates/${rateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete GST rate');
    }
  },

  getGSTReturns: async () => {
    try {
      const returns = await apiService.get('/api/localization/indian/gst/returns');
      return returns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST returns');
    }
  },

  getGSTReturn: async (returnId) => {
    try {
      const returnItem = await apiService.get(`/api/localization/indian/gst/returns/${returnId}`);
      return returnItem;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST return');
    }
  },

  createGSTReturn: async (returnData) => {
    try {
      const result = await apiService.post('/api/localization/indian/gst/returns', returnData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create GST return');
    }
  },

  updateGSTReturn: async (returnId, returnData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/gst/returns/${returnId}`, returnData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update GST return');
    }
  },

  deleteGSTReturn: async (returnId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/gst/returns/${returnId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete GST return');
    }
  },

  getGSTReports: async () => {
    try {
      const reports = await apiService.get('/api/localization/indian/gst/reports');
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST reports');
    }
  },

  // GST Calculation
  calculateGST: async (calculationData) => {
    try {
      const result = await apiService.post('/api/localization/indian/gst/calculate', calculationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to calculate GST');
    }
  },

  // Indian Banking
  getIndianBanks: async () => {
    try {
      const banks = await apiService.get('/api/localization/indian/banks');
      return banks;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian banks');
    }
  },

  getIndianBank: async (bankId) => {
    try {
      const bank = await apiService.get(`/api/localization/indian/banks/${bankId}`);
      return bank;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian bank');
    }
  },

  createIndianBank: async (bankData) => {
    try {
      const result = await apiService.post('/api/localization/indian/banks', bankData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create Indian bank');
    }
  },

  updateIndianBank: async (bankId, bankData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/banks/${bankId}`, bankData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update Indian bank');
    }
  },

  deleteIndianBank: async (bankId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/banks/${bankId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete Indian bank');
    }
  },

  // UPI Integration
  getUPIProviders: async () => {
    try {
      const providers = await apiService.get('/api/localization/indian/upi/providers');
      return providers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch UPI providers');
    }
  },

  getUPIProvider: async (providerId) => {
    try {
      const provider = await apiService.get(`/api/localization/indian/upi/providers/${providerId}`);
      return provider;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch UPI provider');
    }
  },

  createUPIProvider: async (providerData) => {
    try {
      const result = await apiService.post('/api/localization/indian/upi/providers', providerData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create UPI provider');
    }
  },

  updateUPIProvider: async (providerId, providerData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/upi/providers/${providerId}`, providerData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update UPI provider');
    }
  },

  deleteUPIProvider: async (providerId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/upi/providers/${providerId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete UPI provider');
    }
  },

  // Payment Gateways
  getPaymentGateways: async () => {
    try {
      const gateways = await apiService.get('/api/localization/indian/payment/gateways');
      return gateways;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment gateways');
    }
  },

  getPaymentGateway: async (gatewayId) => {
    try {
      const gateway = await apiService.get(`/api/localization/indian/payment/gateways/${gatewayId}`);
      return gateway;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch payment gateway');
    }
  },

  createPaymentGateway: async (gatewayData) => {
    try {
      const result = await apiService.post('/api/localization/indian/payment/gateways', gatewayData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create payment gateway');
    }
  },

  updatePaymentGateway: async (gatewayId, gatewayData) => {
    try {
      const result = await apiService.put(`/api/localization/indian/payment/gateways/${gatewayId}`, gatewayData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update payment gateway');
    }
  },

  deletePaymentGateway: async (gatewayId) => {
    try {
      const result = await apiService.delete(`/api/localization/indian/payment/gateways/${gatewayId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete payment gateway');
    }
  },

  // Banking Transactions
  getBankingTransactions: async () => {
    try {
      const transactions = await apiService.get('/api/localization/indian/banking/transactions');
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch banking transactions');
    }
  },

  // NEFT/RTGS
  processNEFT: async (neftData) => {
    try {
      const result = await apiService.post('/api/localization/indian/banking/neft', neftData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process NEFT');
    }
  },

  processRTGS: async (rtgsData) => {
    try {
      const result = await apiService.post('/api/localization/indian/banking/rtgs', rtgsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to process RTGS');
    }
  },

  // Indian Compliance
  getComplianceReports: async () => {
    try {
      const reports = await apiService.get('/api/localization/indian/compliance/reports');
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch compliance reports');
    }
  },

  getAuditTrails: async () => {
    try {
      const trails = await apiService.get('/api/localization/indian/compliance/audit-trails');
      return trails;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch audit trails');
    }
  },

  // Indian Localization Settings
  getLocalizationSettings: async () => {
    try {
      const settings = await apiService.get('/api/localization/indian/settings');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch localization settings');
    }
  },

  updateLocalizationSettings: async (settingsData) => {
    try {
      const result = await apiService.put('/api/localization/indian/settings', settingsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update localization settings');
    }
  }
};