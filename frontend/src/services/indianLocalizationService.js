import { apiService } from './apiService';

export const indianLocalizationService = {
  // GST Management
  getGSTSlabs: async (params = {}) => {
    try {
      const slabs = await apiService.get('/api/indian-gst/gst-slabs', params);
      return slabs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST slabs');
    }
  },

  getGSTSlab: async (slabId) => {
    try {
      const slab = await apiService.get(`/api/indian-gst/gst-slabs/${slabId}`);
      return slab;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch GST slab');
    }
  },

  createGSTSlab: async (slabData) => {
    try {
      const slab = await apiService.post('/api/indian-gst/gst-slabs', slabData);
      return slab;
    } catch (error) {
      throw new Error(error.message || 'Failed to create GST slab');
    }
  },

  updateGSTSlab: async (slabId, slabData) => {
    try {
      const slab = await apiService.put(`/api/indian-gst/gst-slabs/${slabId}`, slabData);
      return slab;
    } catch (error) {
      throw new Error(error.message || 'Failed to update GST slab');
    }
  },

  deleteGSTSlab: async (slabId) => {
    try {
      await apiService.delete(`/api/indian-gst/gst-slabs/${slabId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete GST slab');
    }
  },

  // GST Calculation
  calculateGST: async (calculationData) => {
    try {
      const result = await apiService.post('/api/indian-gst/calculate', calculationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to calculate GST');
    }
  },

  // HSN Codes
  getHSNCodes: async (params = {}) => {
    try {
      const codes = await apiService.get('/api/indian-gst/hsn-codes', params);
      return codes;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch HSN codes');
    }
  },

  getHSNCode: async (codeId) => {
    try {
      const code = await apiService.get(`/api/indian-gst/hsn-codes/${codeId}`);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch HSN code');
    }
  },

  createHSNCode: async (codeData) => {
    try {
      const code = await apiService.post('/api/indian-gst/hsn-codes', codeData);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to create HSN code');
    }
  },

  updateHSNCode: async (codeId, codeData) => {
    try {
      const code = await apiService.put(`/api/indian-gst/hsn-codes/${codeId}`, codeData);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to update HSN code');
    }
  },

  deleteHSNCode: async (codeId) => {
    try {
      await apiService.delete(`/api/indian-gst/hsn-codes/${codeId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete HSN code');
    }
  },

  // SAC Codes
  getSACCodes: async (params = {}) => {
    try {
      const codes = await apiService.get('/api/indian-gst/sac-codes', params);
      return codes;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch SAC codes');
    }
  },

  getSACCode: async (codeId) => {
    try {
      const code = await apiService.get(`/api/indian-gst/sac-codes/${codeId}`);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch SAC code');
    }
  },

  createSACCode: async (codeData) => {
    try {
      const code = await apiService.post('/api/indian-gst/sac-codes', codeData);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to create SAC code');
    }
  },

  updateSACCode: async (codeId, codeData) => {
    try {
      const code = await apiService.put(`/api/indian-gst/sac-codes/${codeId}`, codeData);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to update SAC code');
    }
  },

  deleteSACCode: async (codeId) => {
    try {
      await apiService.delete(`/api/indian-gst/sac-codes/${codeId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete SAC code');
    }
  },

  // State Codes
  getStateCodes: async (params = {}) => {
    try {
      const codes = await apiService.get('/api/indian-gst/state-codes', params);
      return codes;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch state codes');
    }
  },

  getStateCode: async (codeId) => {
    try {
      const code = await apiService.get(`/api/indian-gst/state-codes/${codeId}`);
      return code;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch state code');
    }
  },

  // GSTIN Validation
  validateGSTIN: async (gstin) => {
    try {
      const result = await apiService.post('/api/indian-gst/validate-gstin', { gstin });
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate GSTIN');
    }
  },

  // Indian Geography
  getStates: async (params = {}) => {
    try {
      const states = await apiService.get('/api/indian-geography/states', params);
      return states;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch states');
    }
  },

  getState: async (stateId) => {
    try {
      const state = await apiService.get(`/api/indian-geography/states/${stateId}`);
      return state;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch state');
    }
  },

  getDistricts: async (stateId, params = {}) => {
    try {
      const districts = await apiService.get(`/api/indian-geography/states/${stateId}/districts`, params);
      return districts;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch districts');
    }
  },

  getDistrict: async (districtId) => {
    try {
      const district = await apiService.get(`/api/indian-geography/districts/${districtId}`);
      return district;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch district');
    }
  },

  getCities: async (districtId, params = {}) => {
    try {
      const cities = await apiService.get(`/api/indian-geography/districts/${districtId}/cities`, params);
      return cities;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch cities');
    }
  },

  getCity: async (cityId) => {
    try {
      const city = await apiService.get(`/api/indian-geography/cities/${cityId}`);
      return city;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch city');
    }
  },

  // Pincode Lookup
  getPincodeDetails: async (pincode) => {
    try {
      const details = await apiService.get(`/api/pincode-lookup/${pincode}`);
      return details;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch pincode details');
    }
  },

  searchPincodes: async (query, params = {}) => {
    try {
      const pincodes = await apiService.get('/api/pincode-lookup/search', {
        q: query,
        ...params
      });
      return pincodes;
    } catch (error) {
      throw new Error(error.message || 'Failed to search pincodes');
    }
  },

  // Indian Banking
  getIndianBanks: async (params = {}) => {
    try {
      const banks = await apiService.get('/api/indian-banking/banks', params);
      return banks;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian banks');
    }
  },

  getIndianBank: async (bankId) => {
    try {
      const bank = await apiService.get(`/api/indian-banking/banks/${bankId}`);
      return bank;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch Indian bank');
    }
  },

  searchBanks: async (query, params = {}) => {
    try {
      const banks = await apiService.get('/api/indian-banking/banks/search', {
        q: query,
        ...params
      });
      return banks;
    } catch (error) {
      throw new Error(error.message || 'Failed to search banks');
    }
  },

  // IFSC Code Lookup
  getIFSCDetails: async (ifscCode) => {
    try {
      const details = await apiService.get(`/api/indian-banking/ifsc/${ifscCode}`);
      return details;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch IFSC details');
    }
  },

  searchIFSC: async (query, params = {}) => {
    try {
      const ifscCodes = await apiService.get('/api/indian-banking/ifsc/search', {
        q: query,
        ...params
      });
      return ifscCodes;
    } catch (error) {
      throw new Error(error.message || 'Failed to search IFSC codes');
    }
  },

  // TDS Management
  getTDSSlabs: async (params = {}) => {
    try {
      const slabs = await apiService.get('/api/indian-gst/tds-slabs', params);
      return slabs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch TDS slabs');
    }
  },

  createTDSSlab: async (slabData) => {
    try {
      const slab = await apiService.post('/api/indian-gst/tds-slabs', slabData);
      return slab;
    } catch (error) {
      throw new Error(error.message || 'Failed to create TDS slab');
    }
  },

  // TCS Management
  getTCSSlabs: async (params = {}) => {
    try {
      const slabs = await apiService.get('/api/indian-gst/tcs-slabs', params);
      return slabs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch TCS slabs');
    }
  },

  createTCSSlab: async (slabData) => {
    try {
      const slab = await apiService.post('/api/indian-gst/tcs-slabs', slabData);
      return slab;
    } catch (error) {
      throw new Error(error.message || 'Failed to create TCS slab');
    }
  },

  // E-Invoicing
  getEInvoices: async (params = {}) => {
    try {
      const invoices = await apiService.get('/api/indian-gst/e-invoices', params);
      return invoices;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch e-invoices');
    }
  },

  generateEInvoice: async (invoiceData) => {
    try {
      const invoice = await apiService.post('/api/indian-gst/e-invoices', invoiceData);
      return invoice;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate e-invoice');
    }
  },

  // E-Waybill
  getEWaybills: async (params = {}) => {
    try {
      const waybills = await apiService.get('/api/indian-gst/e-waybills', params);
      return waybills;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch e-waybills');
    }
  },

  generateEWaybill: async (waybillData) => {
    try {
      const waybill = await apiService.post('/api/indian-gst/e-waybills', waybillData);
      return waybill;
    } catch (error) {
      throw new Error(error.message || 'Failed to generate e-waybill');
    }
  }
};