import { apiService } from './apiService';

export const marketingService = {
  // WhatsApp Integration
  getWhatsAppTemplates: async () => {
    try {
      const templates = await apiService.get('/api/marketing/whatsapp/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp templates');
    }
  },

  getWhatsAppTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/marketing/whatsapp/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp template');
    }
  },

  createWhatsAppTemplate: async (templateData) => {
    try {
      const result = await apiService.post('/api/marketing/whatsapp/templates', templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create WhatsApp template');
    }
  },

  updateWhatsAppTemplate: async (templateId, templateData) => {
    try {
      const result = await apiService.put(`/api/marketing/whatsapp/templates/${templateId}`, templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update WhatsApp template');
    }
  },

  deleteWhatsAppTemplate: async (templateId) => {
    try {
      const result = await apiService.delete(`/api/marketing/whatsapp/templates/${templateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete WhatsApp template');
    }
  },

  getWhatsAppCampaigns: async () => {
    try {
      const campaigns = await apiService.get('/api/marketing/whatsapp/campaigns');
      return campaigns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp campaigns');
    }
  },

  getWhatsAppCampaign: async (campaignId) => {
    try {
      const campaign = await apiService.get(`/api/marketing/whatsapp/campaigns/${campaignId}`);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch WhatsApp campaign');
    }
  },

  createWhatsAppCampaign: async (campaignData) => {
    try {
      const result = await apiService.post('/api/marketing/whatsapp/campaigns', campaignData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create WhatsApp campaign');
    }
  },

  updateWhatsAppCampaign: async (campaignId, campaignData) => {
    try {
      const result = await apiService.put(`/api/marketing/whatsapp/campaigns/${campaignId}`, campaignData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update WhatsApp campaign');
    }
  },

  deleteWhatsAppCampaign: async (campaignId) => {
    try {
      const result = await apiService.delete(`/api/marketing/whatsapp/campaigns/${campaignId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete WhatsApp campaign');
    }
  },

  // Customer Segmentation
  getCustomerSegments: async () => {
    try {
      const segments = await apiService.get('/api/marketing/segments');
      return segments;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer segments');
    }
  },

  getCustomerSegment: async (segmentId) => {
    try {
      const segment = await apiService.get(`/api/marketing/segments/${segmentId}`);
      return segment;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch customer segment');
    }
  },

  createCustomerSegment: async (segmentData) => {
    try {
      const result = await apiService.post('/api/marketing/segments', segmentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create customer segment');
    }
  },

  updateCustomerSegment: async (segmentId, segmentData) => {
    try {
      const result = await apiService.put(`/api/marketing/segments/${segmentId}`, segmentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update customer segment');
    }
  },

  deleteCustomerSegment: async (segmentId) => {
    try {
      const result = await apiService.delete(`/api/marketing/segments/${segmentId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete customer segment');
    }
  },

  // Marketing Campaigns
  getMarketingCampaigns: async () => {
    try {
      const campaigns = await apiService.get('/api/marketing/campaigns');
      return campaigns;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing campaigns');
    }
  },

  getMarketingCampaign: async (campaignId) => {
    try {
      const campaign = await apiService.get(`/api/marketing/campaigns/${campaignId}`);
      return campaign;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing campaign');
    }
  },

  createMarketingCampaign: async (campaignData) => {
    try {
      const result = await apiService.post('/api/marketing/campaigns', campaignData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create marketing campaign');
    }
  },

  updateMarketingCampaign: async (campaignId, campaignData) => {
    try {
      const result = await apiService.put(`/api/marketing/campaigns/${campaignId}`, campaignData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update marketing campaign');
    }
  },

  deleteMarketingCampaign: async (campaignId) => {
    try {
      const result = await apiService.delete(`/api/marketing/campaigns/${campaignId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete marketing campaign');
    }
  },

  // Marketing Automation
  getMarketingAutomations: async () => {
    try {
      const automations = await apiService.get('/api/marketing/automations');
      return automations;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing automations');
    }
  },

  getMarketingAutomation: async (automationId) => {
    try {
      const automation = await apiService.get(`/api/marketing/automations/${automationId}`);
      return automation;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing automation');
    }
  },

  createMarketingAutomation: async (automationData) => {
    try {
      const result = await apiService.post('/api/marketing/automations', automationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create marketing automation');
    }
  },

  updateMarketingAutomation: async (automationId, automationData) => {
    try {
      const result = await apiService.put(`/api/marketing/automations/${automationId}`, automationData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update marketing automation');
    }
  },

  deleteMarketingAutomation: async (automationId) => {
    try {
      const result = await apiService.delete(`/api/marketing/automations/${automationId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete marketing automation');
    }
  },

  // Email Marketing
  getEmailTemplates: async () => {
    try {
      const templates = await apiService.get('/api/marketing/email/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch email templates');
    }
  },

  getEmailTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/marketing/email/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch email template');
    }
  },

  createEmailTemplate: async (templateData) => {
    try {
      const result = await apiService.post('/api/marketing/email/templates', templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create email template');
    }
  },

  updateEmailTemplate: async (templateId, templateData) => {
    try {
      const result = await apiService.put(`/api/marketing/email/templates/${templateId}`, templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update email template');
    }
  },

  deleteEmailTemplate: async (templateId) => {
    try {
      const result = await apiService.delete(`/api/marketing/email/templates/${templateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete email template');
    }
  },

  // SMS Marketing
  getSMSTemplates: async () => {
    try {
      const templates = await apiService.get('/api/marketing/sms/templates');
      return templates;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch SMS templates');
    }
  },

  getSMSTemplate: async (templateId) => {
    try {
      const template = await apiService.get(`/api/marketing/sms/templates/${templateId}`);
      return template;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch SMS template');
    }
  },

  createSMSTemplate: async (templateData) => {
    try {
      const result = await apiService.post('/api/marketing/sms/templates', templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to create SMS template');
    }
  },

  updateSMSTemplate: async (templateId, templateData) => {
    try {
      const result = await apiService.put(`/api/marketing/sms/templates/${templateId}`, templateData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update SMS template');
    }
  },

  deleteSMSTemplate: async (templateId) => {
    try {
      const result = await apiService.delete(`/api/marketing/sms/templates/${templateId}`);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to delete SMS template');
    }
  },

  // Marketing Analytics
  getMarketingAnalytics: async (params = {}) => {
    try {
      const analytics = await apiService.get('/api/marketing/analytics', params);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing analytics');
    }
  },

  getCampaignAnalytics: async (campaignId) => {
    try {
      const analytics = await apiService.get(`/api/marketing/campaigns/${campaignId}/analytics`);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch campaign analytics');
    }
  },

  getSegmentAnalytics: async (segmentId) => {
    try {
      const analytics = await apiService.get(`/api/marketing/segments/${segmentId}/analytics`);
      return analytics;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch segment analytics');
    }
  },

  // Marketing Reports
  getMarketingReports: async (params = {}) => {
    try {
      const reports = await apiService.get('/api/marketing/reports', params);
      return reports;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing reports');
    }
  },

  exportMarketingReport: async (reportType, params = {}) => {
    try {
      const result = await apiService.post(`/api/marketing/reports/export/${reportType}`, params);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to export marketing report');
    }
  },

  // Marketing Settings
  getMarketingSettings: async () => {
    try {
      const settings = await apiService.get('/api/marketing/settings');
      return settings;
    } catch (error) {
      throw new Error(error.message || 'Failed to fetch marketing settings');
    }
  },

  updateMarketingSettings: async (settingsData) => {
    try {
      const result = await apiService.put('/api/marketing/settings', settingsData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to update marketing settings');
    }
  },

  // Marketing Validation
  validateMarketingCampaign: async (campaignData) => {
    try {
      const result = await apiService.post('/api/marketing/validate', campaignData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate marketing campaign');
    }
  },

  validateCustomerSegment: async (segmentData) => {
    try {
      const result = await apiService.post('/api/marketing/validate-segment', segmentData);
      return result;
    } catch (error) {
      throw new Error(error.message || 'Failed to validate customer segment');
    }
  }
};