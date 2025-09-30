# WhatsApp Business API Integration Guide

## Overview

This comprehensive WhatsApp integration provides your POS system with powerful customer communication capabilities including:

- **POS Receipt Delivery**: Automatically send receipts via WhatsApp after transactions
- **Loyalty Points Notifications**: Notify customers about points earned and redeemed
- **Invoice Delivery**: Send invoices with PDF attachments
- **Marketing Campaigns**: Run targeted marketing campaigns
- **Customer Opt-in/Opt-out Management**: Respect customer preferences
- **Template Management**: Create, submit, and manage WhatsApp templates

## Features

### 🛍️ POS Integration
- Automatic receipt delivery after POS transactions
- Loyalty points notifications
- Customer opt-in/opt-out management
- Transaction history tracking

### 📱 Marketing Platform
- Targeted marketing campaigns
- Customer segmentation
- Campaign analytics and reporting
- Template-based messaging

### 🎯 Template Management
- Pre-configured templates for common use cases
- Template approval workflow
- Variable substitution
- Multi-language support

### 🔒 Compliance & Security
- Customer opt-in/opt-out handling
- WhatsApp Business Policy compliance
- Secure webhook handling
- Message delivery tracking

## Setup Instructions

### 1. Prerequisites

Before setting up WhatsApp integration, ensure you have:

- **WhatsApp Business Account**: Verified business account
- **Facebook Business Manager**: Connected to your WhatsApp Business Account
- **Verified Phone Number**: Business phone number verified with WhatsApp
- **API Access**: WhatsApp Business API access

### 2. Get API Credentials

1. Go to [Facebook Business Manager](https://business.facebook.com/)
2. Navigate to WhatsApp Business API
3. Get the following credentials:
   - **Access Token**: Your WhatsApp API access token
   - **Phone Number ID**: Your WhatsApp phone number ID
   - **Business Account ID**: Your WhatsApp business account ID

### 3. Configure Environment Variables

Add the following to your `.env` file:

```env
# WhatsApp Configuration
WHATSAPP_ENABLED=true
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token_here
```

### 4. Initialize Templates

Use the API to initialize default templates:

```bash
POST /api/v1/whatsapp/setup/initialize
```

This will create templates for:
- POS receipts
- Loyalty points notifications
- Invoices
- Marketing promotions
- Order confirmations
- And more...

### 5. Submit Templates for Approval

1. Go to WhatsApp Business Manager
2. Navigate to Message Templates
3. Submit each template for approval
4. Wait for approval (usually 24-48 hours)

### 6. Configure Webhook

Set up webhook URL in WhatsApp Business Manager:
- **Webhook URL**: `https://yourdomain.com/api/v1/whatsapp/webhooks/`
- **Verify Token**: Use the same token from your environment variables

## API Endpoints

### Template Management

```bash
# Get all templates
GET /api/v1/whatsapp/templates/

# Create new template
POST /api/v1/whatsapp/templates/

# Submit template for approval
POST /api/v1/whatsapp/templates/{template_id}/submit

# Approve template
POST /api/v1/whatsapp/templates/{template_id}/approve
```

### Message Sending

```bash
# Send POS receipt
POST /api/v1/whatsapp/integration/pos/receipt

# Send loyalty points update
POST /api/v1/whatsapp/integration/loyalty/points

# Send invoice
POST /api/v1/whatsapp/integration/invoice

# Send marketing message
POST /api/v1/whatsapp/integration/marketing
```

### Campaign Management

```bash
# Create campaign
POST /api/v1/whatsapp/campaigns/

# Start campaign
POST /api/v1/whatsapp/campaigns/{campaign_id}/start

# Get campaign statistics
GET /api/v1/whatsapp/campaigns/{campaign_id}/statistics
```

### Customer Management

```bash
# Handle opt-in
POST /api/v1/whatsapp/integration/opt-in

# Handle opt-out
POST /api/v1/whatsapp/integration/opt-out

# Get customer preferences
GET /api/v1/whatsapp/integration/customer/{customer_id}/preferences
```

## Usage Examples

### 1. POS Transaction with WhatsApp Receipt

```python
# Complete POS transaction and send receipt
POST /api/v1/pos/pos-transactions/{transaction_id}/complete?send_whatsapp=true

# Response includes WhatsApp delivery status
{
    "message": "POS transaction completed successfully",
    "transaction_id": 123,
    "whatsapp_receipt": {
        "success": true,
        "message_id": "wamid.xxx",
        "status": "sent"
    },
    "loyalty_update": {
        "success": true,
        "message_id": "wamid.yyy",
        "status": "sent"
    }
}
```

### 2. Marketing Campaign

```python
# Create marketing campaign
POST /api/v1/whatsapp/campaigns/
{
    "name": "Summer Sale 2024",
    "description": "Special summer offers",
    "template_id": 1,
    "target_audience": {
        "customer_segments": ["premium_customers"],
        "loyalty_tiers": ["gold", "platinum"]
    },
    "variables": {
        "offer_title": "Summer Sale",
        "discount_percentage": 20,
        "valid_until": "2024-08-31"
    }
}

# Start campaign
POST /api/v1/whatsapp/campaigns/{campaign_id}/start
```

### 3. Customer Opt-in Flow

```python
# Customer opts in for marketing messages
POST /api/v1/whatsapp/integration/opt-in
{
    "phone_number": "+919876543210",
    "opt_type": "marketing",
    "customer_id": 123
}
```

## Template Examples

### POS Receipt Template

```
🛍️ Purchase Receipt

Thank you for your purchase at {{store_name}}!

Receipt #{{transaction_id}}
Date: {{date}}
Items: {{items_count}}
Total: ₹{{total_amount}}
Payment: {{payment_method}}

Thank you for shopping with us!

Visit us again soon!
[View Receipt]
```

### Loyalty Points Template

```
🎁 Loyalty Points Earned

Hello {{customer_name}}!

You earned {{points_earned}} loyalty points from your recent purchase.

Current Balance: {{current_balance}} points

Keep shopping to earn more rewards!

Redeem points at checkout
[View Rewards]
```

### Marketing Template

```
🎉 Special Offer!

Hello {{customer_name}}!

{{offer_title}}

{{offer_description}}

Get {{discount_percentage}}% OFF on your next purchase!

Valid until: {{valid_until}}

Don't miss out on this amazing deal!

Terms and conditions apply
[Shop Now]
```

## Best Practices

### 1. Customer Consent
- Always get explicit opt-in before sending messages
- Provide clear opt-out options
- Respect customer preferences immediately

### 2. Message Content
- Keep messages concise and clear
- Use appropriate emojis sparingly
- Include clear call-to-action buttons
- Personalize messages with customer data

### 3. Template Design
- Follow WhatsApp template guidelines
- Use appropriate categories (TRANSACTIONAL, MARKETING, UTILITY)
- Test templates before submission
- Include necessary variables

### 4. Campaign Management
- Segment customers appropriately
- Monitor delivery and engagement rates
- A/B test different templates
- Respect sending frequency limits

## Compliance

### WhatsApp Business Policy
- Follow WhatsApp Business Policy guidelines
- Use templates only for approved purposes
- Respect customer opt-out requests
- Maintain message quality standards

### Data Privacy
- Protect customer phone numbers
- Secure API credentials
- Log message activities appropriately
- Follow local data protection regulations

### Marketing Compliance
- Include unsubscribe options
- Respect sending time restrictions
- Follow local marketing regulations
- Maintain opt-in records

## Troubleshooting

### Common Issues

1. **Template Not Approved**
   - Check template content against WhatsApp guidelines
   - Ensure proper categorization
   - Wait for approval (24-48 hours)

2. **Message Delivery Failed**
   - Verify phone number format
   - Check customer opt-in status
   - Verify template approval status

3. **Webhook Not Working**
   - Check webhook URL accessibility
   - Verify SSL certificate
   - Check webhook verification token

4. **API Rate Limits**
   - Monitor API usage
   - Implement rate limiting
   - Use message queuing for bulk sends

### Debug Tools

```bash
# Check setup status
GET /api/v1/whatsapp/setup/status

# Preview templates
GET /api/v1/whatsapp/setup/templates/preview

# Test webhook
POST /api/v1/whatsapp/webhooks/test
```

## Monitoring and Analytics

### Message Statistics
- Delivery rates
- Read rates
- Failure rates
- Response rates

### Campaign Analytics
- Open rates
- Click-through rates
- Conversion rates
- Customer engagement

### System Health
- API response times
- Webhook processing
- Error rates
- Queue status

## Security Considerations

1. **API Credentials**
   - Store securely in environment variables
   - Rotate tokens regularly
   - Monitor access logs

2. **Webhook Security**
   - Verify webhook signatures
   - Use HTTPS endpoints
   - Implement rate limiting

3. **Data Protection**
   - Encrypt sensitive data
   - Implement access controls
   - Regular security audits

## Support and Resources

### Documentation
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy)
- [Template Guidelines](https://developers.facebook.com/docs/whatsapp/message-templates)

### API Support
- Use the built-in documentation at `/docs`
- Check system health at `/health`
- Monitor logs for debugging

### Community
- WhatsApp Developer Community
- Business API Support
- Template Review Process

## Conclusion

This WhatsApp integration provides a comprehensive solution for customer communication in your POS system. With proper setup and following best practices, you can enhance customer experience while maintaining compliance with WhatsApp policies and local regulations.

For additional support or customization, refer to the API documentation or contact your development team.