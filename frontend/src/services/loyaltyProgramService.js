import { apiService } from './apiService';

export const loyaltyProgramService = {
  // Loyalty Programs
  getLoyaltyPrograms: async (params = {}) => {
    try {
      const programs = await apiService.get('/api/loyalty-program/programs', params);
      return programs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty programs');
    }
  },

  getLoyaltyProgram: async (programId) => {
    try {
      const program = await apiService.get(`/api/loyalty-program/programs/${programId}`);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty program');
    }
  },

  createLoyaltyProgram: async (programData) => {
    try {
      const program = await apiService.post('/api/loyalty-program/programs', programData);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty program');
    }
  },

  updateLoyaltyProgram: async (programId, programData) => {
    try {
      const program = await apiService.put(`/api/loyalty-program/programs/${programId}`, programData);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty program');
    }
  },

  deleteLoyaltyProgram: async (programId) => {
    try {
      await apiService.delete(`/api/loyalty-program/programs/${programId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty program');
    }
  },

  activateLoyaltyProgram: async (programId) => {
    try {
      const program = await apiService.post(`/api/loyalty-program/programs/${programId}/activate`);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to activate loyalty program');
    }
  },

  deactivateLoyaltyProgram: async (programId) => {
    try {
      const program = await apiService.post(`/api/loyalty-program/programs/${programId}/deactivate`);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to deactivate loyalty program');
    }
  },

  // Loyalty Tiers
  getLoyaltyTiers: async (programId, params = {}) => {
    try {
      const tiers = await apiService.get(`/api/loyalty-program/programs/${programId}/tiers`, params);
      return tiers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty tiers');
    }
  },

  getLoyaltyTier: async (tierId) => {
    try {
      const tier = await apiService.get(`/api/loyalty-program/tiers/${tierId}`);
      return tier;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty tier');
    }
  },

  createLoyaltyTier: async (programId, tierData) => {
    try {
      const tier = await apiService.post(`/api/loyalty-program/programs/${programId}/tiers`, tierData);
      return tier;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty tier');
    }
  },

  updateLoyaltyTier: async (tierId, tierData) => {
    try {
      const tier = await apiService.put(`/api/loyalty-program/tiers/${tierId}`, tierData);
      return tier;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty tier');
    }
  },

  deleteLoyaltyTier: async (tierId) => {
    try {
      await apiService.delete(`/api/loyalty-program/tiers/${tierId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty tier');
    }
  },

  // Customer Loyalty Tiers
  getCustomerLoyaltyTiers: async (params = {}) => {
    try {
      const customerTiers = await apiService.get('/api/loyalty-program/customer-tiers', params);
      return customerTiers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer loyalty tiers');
    }
  },

  getCustomerLoyaltyTier: async (customerId, programId) => {
    try {
      const customerTier = await apiService.get(`/api/loyalty-program/customers/${customerId}/programs/${programId}`);
      return customerTier;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer loyalty tier');
    }
  },

  updateCustomerLoyaltyTier: async (customerId, programId, tierData) => {
    try {
      const customerTier = await apiService.put(`/api/loyalty-program/customers/${customerId}/programs/${programId}`, tierData);
      return customerTier;
    } catch (error) {
      throw new Error(error.message || 'Failed to update customer loyalty tier');
    }
  },

  // Loyalty Points
  getLoyaltyPoints: async (params = {}) => {
    try {
      const points = await apiService.get('/api/loyalty-program/points', params);
      return points;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty points');
    }
  },

  getLoyaltyPoint: async (pointId) => {
    try {
      const point = await apiService.get(`/api/loyalty-program/points/${pointId}`);
      return point;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty point');
    }
  },

  createLoyaltyPoint: async (programId, pointData) => {
    try {
      const point = await apiService.post(`/api/loyalty-program/programs/${programId}/points`, pointData);
      return point;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty point');
    }
  },

  updateLoyaltyPoint: async (pointId, pointData) => {
    try {
      const point = await apiService.put(`/api/loyalty-program/points/${pointId}`, pointData);
      return point;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty point');
    }
  },

  deleteLoyaltyPoint: async (pointId) => {
    try {
      await apiService.delete(`/api/loyalty-program/points/${pointId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty point');
    }
  },

  // Loyalty Point Transactions
  getLoyaltyPointTransactions: async (params = {}) => {
    try {
      const transactions = await apiService.get('/api/loyalty-program/point-transactions', params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty point transactions');
    }
  },

  getLoyaltyPointTransaction: async (transactionId) => {
    try {
      const transaction = await apiService.get(`/api/loyalty-program/point-transactions/${transactionId}`);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty point transaction');
    }
  },

  createLoyaltyPointTransaction: async (transactionData) => {
    try {
      const transaction = await apiService.post('/api/loyalty-program/point-transactions', transactionData);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty point transaction');
    }
  },

  // Customer Points
  getCustomerPoints: async (customerId, params = {}) => {
    try {
      const points = await apiService.get(`/api/loyalty-program/customers/${customerId}/points`, params);
      return points;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer points');
    }
  },

  getCustomerPointBalance: async (customerId, programId) => {
    try {
      const balance = await apiService.get(`/api/loyalty-program/customers/${customerId}/programs/${programId}/balance`);
      return balance;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer point balance');
    }
  },

  addCustomerPoints: async (customerId, programId, pointsData) => {
    try {
      const result = await apiService.post(`/api/loyalty-program/customers/${customerId}/programs/${programId}/add-points`, pointsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add customer points');
    }
  },

  redeemCustomerPoints: async (customerId, programId, redemptionData) => {
    try {
      const result = await apiService.post(`/api/loyalty-program/customers/${customerId}/programs/${programId}/redeem-points`, redemptionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to redeem customer points');
    }
  },

  // Loyalty Rewards
  getLoyaltyRewards: async (params = {}) => {
    try {
      const rewards = await apiService.get('/api/loyalty-program/rewards', params);
      return rewards;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty rewards');
    }
  },

  getLoyaltyReward: async (rewardId) => {
    try {
      const reward = await apiService.get(`/api/loyalty-program/rewards/${rewardId}`);
      return reward;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty reward');
    }
  },

  createLoyaltyReward: async (programId, rewardData) => {
    try {
      const reward = await apiService.post(`/api/loyalty-program/programs/${programId}/rewards`, rewardData);
      return reward;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty reward');
    }
  },

  updateLoyaltyReward: async (rewardId, rewardData) => {
    try {
      const reward = await apiService.put(`/api/loyalty-program/rewards/${rewardId}`, rewardData);
      return reward;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty reward');
    }
  },

  deleteLoyaltyReward: async (rewardId) => {
    try {
      await apiService.delete(`/api/loyalty-program/rewards/${rewardId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty reward');
    }
  },

  // Reward Redemptions
  getRewardRedemptions: async (params = {}) => {
    try {
      const redemptions = await apiService.get('/api/loyalty-program/reward-redemptions', params);
      return redemptions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reward redemptions');
    }
  },

  getRewardRedemption: async (redemptionId) => {
    try {
      const redemption = await apiService.get(`/api/loyalty-program/reward-redemptions/${redemptionId}`);
      return redemption;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reward redemption');
    }
  },

  createRewardRedemption: async (redemptionData) => {
    try {
      const redemption = await apiService.post('/api/loyalty-program/reward-redemptions', redemptionData);
      return redemption;
    } catch (error) {
      throw new Error(error.message || 'Failed to create reward redemption');
    }
  },

  updateRewardRedemption: async (redemptionId, redemptionData) => {
    try {
      const redemption = await apiService.put(`/api/loyalty-program/reward-redemptions/${redemptionId}`, redemptionData);
      return redemption;
    } catch (error) {
      throw new Error(error.message || 'Failed to update reward redemption');
    }
  },

  // Loyalty Analytics
  getLoyaltyAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/loyalty-program/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty analytics');
    }
  },

  getLoyaltyDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/loyalty-program/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty dashboard');
    }
  },

  getLoyaltyReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/loyalty-program/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty reports');
    }
  },

  // Customer Loyalty History
  getCustomerLoyaltyHistory: async (customerId, params = {}) => {
    try {
      const history = await apiService.get(`/api/loyalty-program/customers/${customerId}/history`, params);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer loyalty history');
    }
  },

  // Export functionality
  exportLoyaltyData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/loyalty-program/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export loyalty data');
    }
  }
};