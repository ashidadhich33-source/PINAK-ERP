import { apiService } from './apiService';

export const loyaltyService = {
  // Loyalty Programs
  getLoyaltyPrograms: async () => {
    try {
      const programs = await apiService.get('/api/loyalty/programs');
      return programs;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty programs');
    }
  },

  getLoyaltyProgram: async (programId) => {
    try {
      const program = await apiService.get(`/api/loyalty/programs/${programId}`);
      return program;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty program');
    }
  },

  createLoyaltyProgram: async (programData) => {
    try {
      const result = await apiService.post('/api/loyalty/programs', programData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty program');
    }
  },

  updateLoyaltyProgram: async (programId, programData) => {
    try {
      const result = await apiService.put(`/api/loyalty/programs/${programId}`, programData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty program');
    }
  },

  deleteLoyaltyProgram: async (programId) => {
    try {
      const result = await apiService.delete(`/api/loyalty/programs/${programId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty program');
    }
  },

  // Loyalty Transactions
  getLoyaltyTransactions: async (params = {}) => {
    try {
      const transactions = await apiService.get('/api/loyalty/transactions', params);
      return transactions;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty transactions');
    }
  },

  getLoyaltyTransaction: async (transactionId) => {
    try {
      const transaction = await apiService.get(`/api/loyalty/transactions/${transactionId}`);
      return transaction;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty transaction');
    }
  },

  createLoyaltyTransaction: async (transactionData) => {
    try {
      const result = await apiService.post('/api/loyalty/transactions', transactionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty transaction');
    }
  },

  updateLoyaltyTransaction: async (transactionId, transactionData) => {
    try {
      const result = await apiService.put(`/api/loyalty/transactions/${transactionId}`, transactionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty transaction');
    }
  },

  deleteLoyaltyTransaction: async (transactionId) => {
    try {
      const result = await apiService.delete(`/api/loyalty/transactions/${transactionId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete loyalty transaction');
    }
  },

  // Points Management
  getCustomerPoints: async (customerId) => {
    try {
      const points = await apiService.get(`/api/loyalty/customers/${customerId}/points`);
      return points;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer points');
    }
  },

  addPoints: async (customerId, pointsData) => {
    try {
      const result = await apiService.post(`/api/loyalty/customers/${customerId}/points`, pointsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add points');
    }
  },

  redeemPoints: async (customerId, redemptionData) => {
    try {
      const result = await apiService.post(`/api/loyalty/customers/${customerId}/redeem`, redemptionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to redeem points');
    }
  },

  // Tier Management
  getCustomerTiers: async () => {
    try {
      const tiers = await apiService.get('/api/loyalty/tiers');
      return tiers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer tiers');
    }
  },

  getCustomerTier: async (tierId) => {
    try {
      const tier = await apiService.get(`/api/loyalty/tiers/${tierId}`);
      return tier;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer tier');
    }
  },

  createCustomerTier: async (tierData) => {
    try {
      const result = await apiService.post('/api/loyalty/tiers', tierData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create customer tier');
    }
  },

  updateCustomerTier: async (tierId, tierData) => {
    try {
      const result = await apiService.put(`/api/loyalty/tiers/${tierId}`, tierData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update customer tier');
    }
  },

  deleteCustomerTier: async (tierId) => {
    try {
      const result = await apiService.delete(`/api/loyalty/tiers/${tierId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete customer tier');
    }
  },

  // Reward Catalog
  getRewards: async () => {
    try {
      const rewards = await apiService.get('/api/loyalty/rewards');
      return rewards;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch rewards');
    }
  },

  getReward: async (rewardId) => {
    try {
      const reward = await apiService.get(`/api/loyalty/rewards/${rewardId}`);
      return reward;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch reward');
    }
  },

  createReward: async (rewardData) => {
    try {
      const result = await apiService.post('/api/loyalty/rewards', rewardData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create reward');
    }
  },

  updateReward: async (rewardId, rewardData) => {
    try {
      const result = await apiService.put(`/api/loyalty/rewards/${rewardId}`, rewardData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update reward');
    }
  },

  deleteReward: async (rewardId) => {
    try {
      const result = await apiService.delete(`/api/loyalty/rewards/${rewardId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete reward');
    }
  },

  // Loyalty Analytics
  getLoyaltyAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/loyalty/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty analytics');
    }
  },

  getProgramAnalytics: async (programId) => {
    try {
      const analytics = await apiService.get(`/api/loyalty/programs/${programId}/analytics`);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch program analytics');
    }
  },

  getCustomerLoyaltyHistory: async (customerId) => {
    try {
      const history = await apiService.get(`/api/loyalty/customers/${customerId}/history`);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer loyalty history');
    }
  },

  // Loyalty Reports
  getLoyaltyReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/loyalty/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty reports');
    }
  },

  exportLoyaltyReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/loyalty/reports/export/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export loyalty report');
    }
  },

  // Loyalty Settings
  getLoyaltySettings: async () => {
    try {
      const settings = await apiService.get('/api/loyalty/settings');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty settings');
    }
  },

  updateLoyaltySettings: async (settingsData) => {
    try {
      const result = await apiService.put('/api/loyalty/settings', settingsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update loyalty settings');
    }
  },

  // Loyalty Notifications
  getLoyaltyNotifications: async () => {
    try {
      const notifications = await apiService.get('/api/loyalty/notifications');
      return notifications;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty notifications');
    }
  },

  sendLoyaltyNotification: async (notificationData) => {
    try {
      const result = await apiService.post('/api/loyalty/notifications', notificationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send loyalty notification');
    }
  },

  // Loyalty Validation
  validateLoyaltyProgram: async (programData) => {
    try {
      const result = await apiService.post('/api/loyalty/validate', programData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate loyalty program');
    }
  },

  validatePointsRedemption: async (redemptionData) => {
    try {
      const result = await apiService.post('/api/loyalty/validate-redemption', redemptionData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate points redemption');
    }
  },

  // Loyalty Program Status Management
  activateLoyaltyProgram: async (programId) => {
    try {
      const result = await apiService.post(`/api/loyalty/programs/${programId}/activate`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to activate loyalty program');
    }
  },

  deactivateLoyaltyProgram: async (programId) => {
    try {
      const result = await apiService.post(`/api/loyalty/programs/${programId}/deactivate`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to deactivate loyalty program');
    }
  },

  // Loyalty Export
  exportLoyaltyData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/loyalty/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export loyalty data');
    }
  },

  // Loyalty Tiers
  createLoyaltyTier: async (tierData) => {
    try {
      const tier = await apiService.post('/api/loyalty/loyalty-tiers', tierData);
      return tier;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty tier');
    }
  },

  getLoyaltyTiers: async (params = {}) => {
    try {
      const tiers = await apiService.get('/api/loyalty/loyalty-tiers', params);
      return tiers;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty tiers');
    }
  },

  // Customer Loyalty Tiers
  createCustomerLoyaltyTier: async (customerTierData) => {
    try {
      const customerTier = await apiService.post('/api/loyalty/customer-loyalty-tiers', customerTierData);
      return customerTier;
    } catch (error) {
      throw new Error(error.message || 'Failed to create customer loyalty tier');
    }
  },

  // Loyalty Points
  createLoyaltyPoint: async (pointData) => {
    try {
      const point = await apiService.post('/api/loyalty/loyalty-points', pointData);
      return point;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty point');
    }
  },

  earnLoyaltyPoint: async (earnData) => {
    try {
      const result = await apiService.post('/api/loyalty/loyalty-points/earn', earnData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to earn loyalty point');
    }
  },

  // Loyalty Rewards
  createLoyaltyReward: async (rewardData) => {
    try {
      const reward = await apiService.post('/api/loyalty/loyalty-rewards', rewardData);
      return reward;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty reward');
    }
  },

  getLoyaltyRewards: async (params = {}) => {
    try {
      const rewards = await apiService.get('/api/loyalty/loyalty-rewards', params);
      return rewards;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty rewards');
    }
  },

  redeemLoyaltyReward: async (redeemData) => {
    try {
      const result = await apiService.post('/api/loyalty/loyalty-rewards/redeem', redeemData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to redeem loyalty reward');
    }
  },

  // Loyalty Campaigns
  createLoyaltyCampaign: async (campaignData) => {
    try {
      const campaign = await apiService.post('/api/loyalty/loyalty-campaigns', campaignData);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to create loyalty campaign');
    }
  },

  getLoyaltyCampaigns: async (params = {}) => {
    try {
      const campaigns = await apiService.get('/api/loyalty/loyalty-campaigns', params);
      return campaigns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch loyalty campaigns');
    }
  },
};