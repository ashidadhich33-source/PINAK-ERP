import { apiService } from './apiService';

class IntegrationService {
  constructor() {
    this.integrations = new Map();
    this.setupIntegrations();
  }

  setupIntegrations() {
    // Payment gateways
    this.integrations.set('stripe', {
      name: 'Stripe',
      type: 'payment',
      config: {
        publishableKey: process.env.VITE_STRIPE_PUBLISHABLE_KEY,
        apiUrl: 'https://api.stripe.com/v1'
      }
    });

    this.integrations.set('razorpay', {
      name: 'Razorpay',
      type: 'payment',
      config: {
        keyId: process.env.VITE_RAZORPAY_KEY_ID,
        apiUrl: 'https://api.razorpay.com/v1'
      }
    });

    this.integrations.set('paypal', {
      name: 'PayPal',
      type: 'payment',
      config: {
        clientId: process.env.VITE_PAYPAL_CLIENT_ID,
        apiUrl: 'https://api.paypal.com/v1'
      }
    });

    // Shipping providers
    this.integrations.set('shiprocket', {
      name: 'Shiprocket',
      type: 'shipping',
      config: {
        apiUrl: 'https://apiv2.shiprocket.in',
        token: process.env.VITE_SHIPROCKET_TOKEN
      }
    });

    this.integrations.set('delhivery', {
      name: 'Delhivery',
      type: 'shipping',
      config: {
        apiUrl: 'https://track.delhivery.com/api',
        token: process.env.VITE_DELHIVERY_TOKEN
      }
    });

    // Communication services
    this.integrations.set('twilio', {
      name: 'Twilio',
      type: 'communication',
      config: {
        accountSid: process.env.VITE_TWILIO_ACCOUNT_SID,
        authToken: process.env.VITE_TWILIO_AUTH_TOKEN,
        apiUrl: 'https://api.twilio.com/2010-04-01'
      }
    });

    this.integrations.set('sendgrid', {
      name: 'SendGrid',
      type: 'communication',
      config: {
        apiKey: process.env.VITE_SENDGRID_API_KEY,
        apiUrl: 'https://api.sendgrid.com/v3'
      }
    });

    // Analytics services
    this.integrations.set('google_analytics', {
      name: 'Google Analytics',
      type: 'analytics',
      config: {
        trackingId: process.env.VITE_GA_TRACKING_ID,
        apiUrl: 'https://www.google-analytics.com/analytics.js'
      }
    });

    this.integrations.set('mixpanel', {
      name: 'Mixpanel',
      type: 'analytics',
      config: {
        token: process.env.VITE_MIXPANEL_TOKEN,
        apiUrl: 'https://api.mixpanel.com'
      }
    });

    // Cloud storage
    this.integrations.set('aws_s3', {
      name: 'AWS S3',
      type: 'storage',
      config: {
        accessKeyId: process.env.VITE_AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.VITE_AWS_SECRET_ACCESS_KEY,
        region: process.env.VITE_AWS_REGION,
        bucket: process.env.VITE_AWS_S3_BUCKET
      }
    });

    this.integrations.set('cloudinary', {
      name: 'Cloudinary',
      type: 'storage',
      config: {
        cloudName: process.env.VITE_CLOUDINARY_CLOUD_NAME,
        apiKey: process.env.VITE_CLOUDINARY_API_KEY,
        apiSecret: process.env.VITE_CLOUDINARY_API_SECRET
      }
    });
  }

  // Payment gateway methods
  async processPayment(paymentData) {
    const { gateway, amount, currency, customer, orderId } = paymentData;
    
    try {
      switch (gateway) {
        case 'stripe':
          return await this.processStripePayment(paymentData);
        case 'razorpay':
          return await this.processRazorpayPayment(paymentData);
        case 'paypal':
          return await this.processPayPalPayment(paymentData);
        default:
          throw new Error(`Unsupported payment gateway: ${gateway}`);
      }
    } catch (error) {
      throw new Error(`Payment processing failed: ${error.message}`);
    }
  }

  async processStripePayment(paymentData) {
    const { amount, currency, customer, orderId } = paymentData;
    
    try {
      const response = await apiService.post('/api/integrations/stripe/payment', {
        amount: amount * 100, // Convert to cents
        currency,
        customer,
        orderId,
        metadata: {
          order_id: orderId
        }
      });
      
      return {
        success: true,
        paymentId: response.data.id,
        status: response.data.status,
        gateway: 'stripe'
      };
    } catch (error) {
      throw new Error(`Stripe payment failed: ${error.message}`);
    }
  }

  async processRazorpayPayment(paymentData) {
    const { amount, currency, customer, orderId } = paymentData;
    
    try {
      const response = await apiService.post('/api/integrations/razorpay/payment', {
        amount: amount * 100, // Convert to paise
        currency,
        customer,
        orderId,
        notes: {
          order_id: orderId
        }
      });
      
      return {
        success: true,
        paymentId: response.data.id,
        status: response.data.status,
        gateway: 'razorpay'
      };
    } catch (error) {
      throw new Error(`Razorpay payment failed: ${error.message}`);
    }
  }

  async processPayPalPayment(paymentData) {
    const { amount, currency, customer, orderId } = paymentData;
    
    try {
      const response = await apiService.post('/api/integrations/paypal/payment', {
        amount,
        currency,
        customer,
        orderId,
        custom_id: orderId
      });
      
      return {
        success: true,
        paymentId: response.data.id,
        status: response.data.status,
        gateway: 'paypal'
      };
    } catch (error) {
      throw new Error(`PayPal payment failed: ${error.message}`);
    }
  }

  // Shipping provider methods
  async createShipment(shipmentData) {
    const { provider, orderId, customer, items, address } = shipmentData;
    
    try {
      switch (provider) {
        case 'shiprocket':
          return await this.createShiprocketShipment(shipmentData);
        case 'delhivery':
          return await this.createDelhiveryShipment(shipmentData);
        default:
          throw new Error(`Unsupported shipping provider: ${provider}`);
      }
    } catch (error) {
      throw new Error(`Shipment creation failed: ${error.message}`);
    }
  }

  async createShiprocketShipment(shipmentData) {
    const { orderId, customer, items, address } = shipmentData;
    
    try {
      const response = await apiService.post('/api/integrations/shiprocket/shipment', {
        order_id: orderId,
        customer,
        items,
        address,
        channel_id: 'ERP'
      });
      
      return {
        success: true,
        shipmentId: response.data.shipment_id,
        awb: response.data.awb,
        trackingUrl: response.data.tracking_url,
        provider: 'shiprocket'
      };
    } catch (error) {
      throw new Error(`Shiprocket shipment creation failed: ${error.message}`);
    }
  }

  async createDelhiveryShipment(shipmentData) {
    const { orderId, customer, items, address } = shipmentData;
    
    try {
      const response = await apiService.post('/api/integrations/delhivery/shipment', {
        order_id: orderId,
        customer,
        items,
        address
      });
      
      return {
        success: true,
        shipmentId: response.data.shipment_id,
        awb: response.data.awb,
        trackingUrl: response.data.tracking_url,
        provider: 'delhivery'
      };
    } catch (error) {
      throw new Error(`Delhivery shipment creation failed: ${error.message}`);
    }
  }

  async trackShipment(trackingData) {
    const { provider, trackingId } = trackingData;
    
    try {
      const response = await apiService.get(`/api/integrations/${provider}/track/${trackingId}`);
      
      return {
        success: true,
        trackingId,
        status: response.data.status,
        updates: response.data.updates,
        provider
      };
    } catch (error) {
      throw new Error(`Shipment tracking failed: ${error.message}`);
    }
  }

  // Communication methods
  async sendSMS(smsData) {
    const { provider, to, message } = smsData;
    
    try {
      switch (provider) {
        case 'twilio':
          return await this.sendTwilioSMS(smsData);
        default:
          throw new Error(`Unsupported SMS provider: ${provider}`);
      }
    } catch (error) {
      throw new Error(`SMS sending failed: ${error.message}`);
    }
  }

  async sendTwilioSMS(smsData) {
    const { to, message } = smsData;
    
    try {
      const response = await apiService.post('/api/integrations/twilio/sms', {
        to,
        body: message
      });
      
      return {
        success: true,
        messageId: response.data.sid,
        status: response.data.status,
        provider: 'twilio'
      };
    } catch (error) {
      throw new Error(`Twilio SMS failed: ${error.message}`);
    }
  }

  async sendEmail(emailData) {
    const { provider, to, subject, body, attachments } = emailData;
    
    try {
      switch (provider) {
        case 'sendgrid':
          return await this.sendSendGridEmail(emailData);
        default:
          throw new Error(`Unsupported email provider: ${provider}`);
      }
    } catch (error) {
      throw new Error(`Email sending failed: ${error.message}`);
    }
  }

  async sendSendGridEmail(emailData) {
    const { to, subject, body, attachments } = emailData;
    
    try {
      const response = await apiService.post('/api/integrations/sendgrid/email', {
        to,
        subject,
        html: body,
        attachments
      });
      
      return {
        success: true,
        messageId: response.data.message_id,
        status: response.data.status,
        provider: 'sendgrid'
      };
    } catch (error) {
      throw new Error(`SendGrid email failed: ${error.message}`);
    }
  }

  // Analytics methods
  async trackEvent(eventData) {
    const { provider, event, properties } = eventData;
    
    try {
      switch (provider) {
        case 'google_analytics':
          return await this.trackGoogleAnalyticsEvent(eventData);
        case 'mixpanel':
          return await this.trackMixpanelEvent(eventData);
        default:
          throw new Error(`Unsupported analytics provider: ${provider}`);
      }
    } catch (error) {
      throw new Error(`Event tracking failed: ${error.message}`);
    }
  }

  async trackGoogleAnalyticsEvent(eventData) {
    const { event, properties } = eventData;
    
    try {
      const response = await apiService.post('/api/integrations/google-analytics/event', {
        event,
        properties
      });
      
      return {
        success: true,
        eventId: response.data.event_id,
        provider: 'google_analytics'
      };
    } catch (error) {
      throw new Error(`Google Analytics tracking failed: ${error.message}`);
    }
  }

  async trackMixpanelEvent(eventData) {
    const { event, properties } = eventData;
    
    try {
      const response = await apiService.post('/api/integrations/mixpanel/event', {
        event,
        properties
      });
      
      return {
        success: true,
        eventId: response.data.event_id,
        provider: 'mixpanel'
      };
    } catch (error) {
      throw new Error(`Mixpanel tracking failed: ${error.message}`);
    }
  }

  // Storage methods
  async uploadFile(fileData) {
    const { provider, file, folder, options } = fileData;
    
    try {
      switch (provider) {
        case 'aws_s3':
          return await this.uploadToS3(fileData);
        case 'cloudinary':
          return await this.uploadToCloudinary(fileData);
        default:
          throw new Error(`Unsupported storage provider: ${provider}`);
      }
    } catch (error) {
      throw new Error(`File upload failed: ${error.message}`);
    }
  }

  async uploadToS3(fileData) {
    const { file, folder, options } = fileData;
    
    try {
      const response = await apiService.post('/api/integrations/aws-s3/upload', {
        file,
        folder,
        options
      });
      
      return {
        success: true,
        fileUrl: response.data.url,
        fileId: response.data.key,
        provider: 'aws_s3'
      };
    } catch (error) {
      throw new Error(`S3 upload failed: ${error.message}`);
    }
  }

  async uploadToCloudinary(fileData) {
    const { file, folder, options } = fileData;
    
    try {
      const response = await apiService.post('/api/integrations/cloudinary/upload', {
        file,
        folder,
        options
      });
      
      return {
        success: true,
        fileUrl: response.data.url,
        fileId: response.data.public_id,
        provider: 'cloudinary'
      };
    } catch (error) {
      throw new Error(`Cloudinary upload failed: ${error.message}`);
    }
  }

  // Integration management
  async getIntegrations() {
    try {
      const response = await apiService.get('/api/integrations');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch integrations: ${error.message}`);
    }
  }

  async getIntegration(integrationId) {
    try {
      const response = await apiService.get(`/api/integrations/${integrationId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch integration: ${error.message}`);
    }
  }

  async createIntegration(integrationData) {
    try {
      const response = await apiService.post('/api/integrations', integrationData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create integration: ${error.message}`);
    }
  }

  async updateIntegration(integrationId, integrationData) {
    try {
      const response = await apiService.put(`/api/integrations/${integrationId}`, integrationData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to update integration: ${error.message}`);
    }
  }

  async deleteIntegration(integrationId) {
    try {
      await apiService.delete(`/api/integrations/${integrationId}`);
      return true;
    } catch (error) {
      throw new Error(`Failed to delete integration: ${error.message}`);
    }
  }

  async testIntegration(integrationId) {
    try {
      const response = await apiService.post(`/api/integrations/${integrationId}/test`);
      return response.data;
    } catch (error) {
      throw new Error(`Integration test failed: ${error.message}`);
    }
  }

  // Utility methods
  getAvailableIntegrations() {
    return Array.from(this.integrations.values());
  }

  getIntegrationByType(type) {
    return Array.from(this.integrations.values()).filter(integration => integration.type === type);
  }

  getIntegrationConfig(integrationId) {
    return this.integrations.get(integrationId);
  }
}

// Create singleton instance
const integrationService = new IntegrationService();

export default integrationService;