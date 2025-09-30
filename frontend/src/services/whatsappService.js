import { apiService } from './apiService';

export const whatsappService = {
  // WhatsApp Configuration
  getWhatsAppConfig: async () => {
    try {
      const config = await apiService.get('/api/whatsapp/config');
      return config;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp configuration');
    }
  },

  updateWhatsAppConfig: async (configData) => {
    try {
      const config = await apiService.put('/api/whatsapp/config', configData);
      return config;
    } catch (error) {
      throw new Error(error.message || 'Failed to update WhatsApp configuration');
    }
  },

  testWhatsAppConnection: async () => {
    try {
      const result = await apiService.post('/api/whatsapp/test-connection');
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to test WhatsApp connection');
    }
  },

  // Message Templates
  getMessageTemplates: async (params = {}) => {
    try {
      const templates = await apiService.get('/api/whatsapp/templates', params);
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch message templates');
    }
  },

  getMessageTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/whatsapp/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch message template');
    }
  },

  createMessageTemplate: async (templateData) => {
    try {
      const template = await apiService.post('/api/whatsapp/templates', templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to create message template');
    }
  },

  updateMessageTemplate: async (templateId, templateData) => {
    try {
      const template = await apiService.put(`/api/whatsapp/templates/${templateId}`, templateData);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to update message template');
    }
  },

  deleteMessageTemplate: async (templateId) => {
    try {
      await apiService.delete(`/api/whatsapp/templates/${templateId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete message template');
    }
  },

  // Send Messages
  sendMessage: async (messageData) => {
    try {
      const result = await apiService.post('/api/whatsapp/send-message', messageData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send message');
    }
  },

  sendBulkMessage: async (bulkMessageData) => {
    try {
      const result = await apiService.post('/api/whatsapp/send-bulk-message', bulkMessageData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send bulk message');
    }
  },

  sendTemplateMessage: async (templateMessageData) => {
    try {
      const result = await apiService.post('/api/whatsapp/send-template-message', templateMessageData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send template message');
    }
  },

  // Message History
  getMessageHistory: async (params = {}) => {
    try {
      const history = await apiService.get('/api/whatsapp/message-history', params);
      return history;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch message history');
    }
  },

  getMessage: async (messageId) => {
    try {
      const message = await apiService.get(`/api/whatsapp/messages/${messageId}`);
      return message;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch message');
    }
  },

  // Customer Communication
  getCustomerMessages: async (customerId, params = {}) => {
    try {
      const messages = await apiService.get(`/api/whatsapp/customers/${customerId}/messages`, params);
      return messages;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer messages');
    }
  },

  sendCustomerMessage: async (customerId, messageData) => {
    try {
      const result = await apiService.post(`/api/whatsapp/customers/${customerId}/send-message`, messageData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to send customer message');
    }
  },

  // Campaign Management
  getCampaigns: async (params = {}) => {
    try {
      const campaigns = await apiService.get('/api/whatsapp/campaigns', params);
      return campaigns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch campaigns');
    }
  },

  getCampaign: async (campaignId) => {
    try {
      const campaign = await apiService.get(`/api/whatsapp/campaigns/${campaignId}`);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch campaign');
    }
  },

  createCampaign: async (campaignData) => {
    try {
      const campaign = await apiService.post('/api/whatsapp/campaigns', campaignData);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to create campaign');
    }
  },

  updateCampaign: async (campaignId, campaignData) => {
    try {
      const campaign = await apiService.put(`/api/whatsapp/campaigns/${campaignId}`, campaignData);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to update campaign');
    }
  },

  deleteCampaign: async (campaignId) => {
    try {
      await apiService.delete(`/api/whatsapp/campaigns/${campaignId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete campaign');
    }
  },

  startCampaign: async (campaignId) => {
    try {
      const result = await apiService.post(`/api/whatsapp/campaigns/${campaignId}/start`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to start campaign');
    }
  },

  stopCampaign: async (campaignId) => {
    try {
      const result = await apiService.post(`/api/whatsapp/campaigns/${campaignId}/stop`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to stop campaign');
    }
  },

  // Campaign Recipients
  getCampaignRecipients: async (campaignId, params = {}) => {
    try {
      const recipients = await apiService.get(`/api/whatsapp/campaigns/${campaignId}/recipients`, params);
      return recipients;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch campaign recipients');
    }
  },

  addCampaignRecipients: async (campaignId, recipientsData) => {
    try {
      const result = await apiService.post(`/api/whatsapp/campaigns/${campaignId}/recipients`, recipientsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to add campaign recipients');
    }
  },

  removeCampaignRecipient: async (campaignId, recipientId) => {
    try {
      await apiService.delete(`/api/whatsapp/campaigns/${campaignId}/recipients/${recipientId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to remove campaign recipient');
    }
  },

  // Webhook Management
  getWebhooks: async (params = {}) => {
    try {
      const webhooks = await apiService.get('/api/whatsapp/webhooks', params);
      return webhooks;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch webhooks');
    }
  },

  getWebhook: async (webhookId) => {
    try {
      const webhook = await apiService.get(`/api/whatsapp/webhooks/${webhookId}`);
      return webhook;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch webhook');
    }
  },

  createWebhook: async (webhookData) => {
    try {
      const webhook = await apiService.post('/api/whatsapp/webhooks', webhookData);
      return webhook;
    } catch (error) {
      throw new Error(error.message || 'Failed to create webhook');
    }
  },

  updateWebhook: async (webhookId, webhookData) => {
    try {
      const webhook = await apiService.put(`/api/whatsapp/webhooks/${webhookId}`, webhookData);
      return webhook;
    } catch (error) {
      throw new Error(error.message || 'Failed to update webhook');
    }
  },

  deleteWebhook: async (webhookId) => {
    try {
      await apiService.delete(`/api/whatsapp/webhooks/${webhookId}`);
      return true;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete webhook');
    }
  },

  // Analytics
  getWhatsAppAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/whatsapp/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp analytics');
    }
  },

  getWhatsAppDashboard: async () => {
    try {
      const dashboard = await apiService.get('/api/whatsapp/dashboard');
      return dashboard;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp dashboard');
    }
  },

  getWhatsAppReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/whatsapp/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp reports');
    }
  },

  // Message Status
  getMessageStatus: async (messageId) => {
    try {
      const status = await apiService.get(`/api/whatsapp/messages/${messageId}/status`);
      return status;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch message status');
    }
  },

  // Delivery Reports
  getDeliveryReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/whatsapp/delivery-reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch delivery reports');
    }
  },

  // Export functionality
  exportWhatsAppData: async (format, data, filters = {}) => {
    try {
      const response = await apiService.post('/api/whatsapp/export', {
        format,
        data,
        filters
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Failed to export WhatsApp data');
    }
  }
};