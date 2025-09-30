"""
WhatsApp Template Management for Business Use Cases
Pre-configured templates for common business scenarios
"""
from typing import Dict, List, Any
from datetime import datetime


class WhatsAppTemplateManager:
    """Manages pre-configured WhatsApp templates for business use"""
    
    @staticmethod
    def get_default_templates() -> List[Dict[str, Any]]:
        """Get default templates for common business scenarios"""
        return [
            {
                "name": "pos_receipt",
                "category": "TRANSACTIONAL",
                "language": "en",
                "header_text": "🛍️ Purchase Receipt",
                "body_text": "Thank you for your purchase at {{store_name}}!\n\nReceipt #{{transaction_id}}\nDate: {{date}}\nItems: {{items_count}}\nTotal: ₹{{total_amount}}\nPayment: {{payment_method}}\n\nThank you for shopping with us!",
                "footer_text": "Visit us again soon!",
                "button_text": "View Receipt",
                "button_url": "{{receipt_url}}",
                "variables": ["store_name", "transaction_id", "date", "items_count", "total_amount", "payment_method", "receipt_url"]
            },
            {
                "name": "loyalty_points_earned",
                "category": "TRANSACTIONAL", 
                "language": "en",
                "header_text": "🎁 Loyalty Points Earned",
                "body_text": "Hello {{customer_name}}!\n\nYou earned {{points_earned}} loyalty points from your recent purchase.\n\nCurrent Balance: {{current_balance}} points\n\nKeep shopping to earn more rewards!",
                "footer_text": "Redeem points at checkout",
                "button_text": "View Rewards",
                "button_url": "{{rewards_url}}",
                "variables": ["customer_name", "points_earned", "current_balance", "rewards_url"]
            },
            {
                "name": "loyalty_points_redemption",
                "category": "TRANSACTIONAL",
                "language": "en", 
                "header_text": "🎁 Points Redeemed",
                "body_text": "Hello {{customer_name}}!\n\nYou redeemed {{points_redeemed}} loyalty points.\nPoints used: {{points_redeemed}}\nRemaining balance: {{current_balance}} points\n\nThank you for being a loyal customer!",
                "footer_text": "Keep earning more points",
                "button_text": "View Balance",
                "button_url": "{{balance_url}}",
                "variables": ["customer_name", "points_redeemed", "current_balance", "balance_url"]
            },
            {
                "name": "invoice",
                "category": "TRANSACTIONAL",
                "language": "en",
                "header_text": "📄 Invoice",
                "body_text": "Hello {{customer_name}}!\n\nYour invoice is ready:\nInvoice #{{invoice_number}}\nAmount: ₹{{total_amount}}\nDue Date: {{due_date}}\n\nPlease find the PDF attached.",
                "footer_text": "Thank you for your business",
                "button_text": "Pay Now",
                "button_url": "{{payment_url}}",
                "variables": ["customer_name", "invoice_number", "total_amount", "due_date", "payment_url"]
            },
            {
                "name": "marketing_promotion",
                "category": "MARKETING",
                "language": "en",
                "header_text": "🎉 Special Offer!",
                "body_text": "Hello {{customer_name}}!\n\n{{offer_title}}\n\n{{offer_description}}\n\nGet {{discount_percentage}}% OFF on your next purchase!\n\nValid until: {{valid_until}}\n\nDon't miss out on this amazing deal!",
                "footer_text": "Terms and conditions apply",
                "button_text": "Shop Now",
                "button_url": "{{shop_url}}",
                "variables": ["customer_name", "offer_title", "offer_description", "discount_percentage", "valid_until", "shop_url"]
            },
            {
                "name": "order_confirmation",
                "category": "TRANSACTIONAL",
                "language": "en",
                "header_text": "✅ Order Confirmed",
                "body_text": "Hello {{customer_name}}!\n\nYour order has been confirmed!\n\nOrder #{{order_number}}\nTotal: ₹{{total_amount}}\nExpected Delivery: {{delivery_date}}\n\nWe'll notify you when your order is ready for pickup/delivery.",
                "footer_text": "Thank you for your order",
                "button_text": "Track Order",
                "button_url": "{{tracking_url}}",
                "variables": ["customer_name", "order_number", "total_amount", "delivery_date", "tracking_url"]
            },
            {
                "name": "order_ready",
                "category": "TRANSACTIONAL",
                "language": "en",
                "header_text": "📦 Order Ready",
                "body_text": "Hello {{customer_name}}!\n\nYour order is ready for pickup!\n\nOrder #{{order_number}}\nPickup Location: {{pickup_location}}\nPickup Time: {{pickup_time}}\n\nPlease bring a valid ID for verification.",
                "footer_text": "We look forward to seeing you",
                "button_text": "Get Directions",
                "button_url": "{{directions_url}}",
                "variables": ["customer_name", "order_number", "pickup_location", "pickup_time", "directions_url"]
            },
            {
                "name": "appointment_reminder",
                "category": "UTILITY",
                "language": "en",
                "header_text": "📅 Appointment Reminder",
                "body_text": "Hello {{customer_name}}!\n\nThis is a reminder about your upcoming appointment:\n\nDate: {{appointment_date}}\nTime: {{appointment_time}}\nService: {{service_name}}\nLocation: {{location}}\n\nPlease arrive 10 minutes early.",
                "footer_text": "We look forward to seeing you",
                "button_text": "Reschedule",
                "button_url": "{{reschedule_url}}",
                "variables": ["customer_name", "appointment_date", "appointment_time", "service_name", "location", "reschedule_url"]
            },
            {
                "name": "payment_reminder",
                "category": "TRANSACTIONAL",
                "language": "en",
                "header_text": "💳 Payment Reminder",
                "body_text": "Hello {{customer_name}}!\n\nThis is a friendly reminder about your pending payment:\n\nInvoice #{{invoice_number}}\nAmount: ₹{{total_amount}}\nDue Date: {{due_date}}\n\nPlease make the payment to avoid any late fees.",
                "footer_text": "Thank you for your prompt payment",
                "button_text": "Pay Now",
                "button_url": "{{payment_url}}",
                "variables": ["customer_name", "invoice_number", "total_amount", "due_date", "payment_url"]
            },
            {
                "name": "welcome_new_customer",
                "category": "UTILITY",
                "language": "en",
                "header_text": "👋 Welcome!",
                "body_text": "Hello {{customer_name}}!\n\nWelcome to {{store_name}}!\n\nWe're excited to have you as our customer. As a new member, you'll enjoy:\n• Exclusive offers and discounts\n• Loyalty points on every purchase\n• Priority customer support\n\nStart shopping now and earn your first rewards!",
                "footer_text": "Thank you for choosing us",
                "button_text": "Start Shopping",
                "button_url": "{{shop_url}}",
                "variables": ["customer_name", "store_name", "shop_url"]
            }
        ]
    
    @staticmethod
    def get_template_by_use_case(use_case: str) -> Dict[str, Any]:
        """Get template for specific use case"""
        templates = WhatsAppTemplateManager.get_default_templates()
        for template in templates:
            if template["name"] == use_case:
                return template
        return None
    
    @staticmethod
    def get_templates_by_category(category: str) -> List[Dict[str, Any]]:
        """Get templates by category"""
        templates = WhatsAppTemplateManager.get_default_templates()
        return [t for t in templates if t["category"] == category]
    
    @staticmethod
    def create_template_from_use_case(use_case: str, custom_variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a template from a use case with custom variables"""
        base_template = WhatsAppTemplateManager.get_template_by_use_case(use_case)
        if not base_template:
            return None
        
        template = base_template.copy()
        if custom_variables:
            template.update(custom_variables)
        
        return template
    
    @staticmethod
    def validate_template_variables(template: Dict[str, Any], provided_variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare template variables"""
        required_variables = template.get("variables", [])
        validated_variables = {}
        
        for var in required_variables:
            if var in provided_variables:
                validated_variables[var] = provided_variables[var]
            else:
                # Provide default values for missing variables
                validated_variables[var] = WhatsAppTemplateManager.get_default_variable_value(var)
        
        return validated_variables
    
    @staticmethod
    def get_default_variable_value(variable_name: str) -> str:
        """Get default value for template variable"""
        defaults = {
            "store_name": "Our Store",
            "customer_name": "Valued Customer",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "total_amount": "0.00",
            "items_count": "0",
            "payment_method": "Cash",
            "points_earned": "0",
            "points_redeemed": "0",
            "current_balance": "0",
            "invoice_number": "N/A",
            "due_date": "N/A",
            "order_number": "N/A",
            "delivery_date": "N/A",
            "pickup_location": "Store",
            "pickup_time": "N/A",
            "appointment_date": "N/A",
            "appointment_time": "N/A",
            "service_name": "Service",
            "location": "Store",
            "offer_title": "Special Offer",
            "offer_description": "Great deals available",
            "discount_percentage": "10",
            "valid_until": "N/A",
            "receipt_url": "#",
            "rewards_url": "#",
            "balance_url": "#",
            "payment_url": "#",
            "tracking_url": "#",
            "directions_url": "#",
            "reschedule_url": "#",
            "shop_url": "#"
        }
        return defaults.get(variable_name, "N/A")