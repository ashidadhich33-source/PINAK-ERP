"""
WhatsApp Cloud API Integration Service
Complete implementation for ERP system
"""

import requests
import json
import os
import io
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
import logging
from pathlib import Path
import asyncio
import aiohttp

from ..config import settings
from ..services.core import PDFService
from ..models import Sale, Customer

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    WhatsApp Cloud API Service for sending messages
    Handles OTP, invoices, notifications, and marketing messages
    """
    
    # API Configuration
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    @classmethod
    def _get_headers(cls) -> Dict[str, str]:
        """Get authorization headers for WhatsApp API"""
        return {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def _get_url(cls, endpoint: str = "messages") -> str:
        """Construct API URL"""
        return f"{cls.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/{endpoint}"
    
    @classmethod
    def _format_phone_number(cls, mobile: str) -> str:
        """
        Format phone number for WhatsApp API
        Adds country code if not present
        """
        # Remove any spaces or special characters
        mobile = ''.join(filter(str.isdigit, mobile))
        
        # Add India country code if not present
        if len(mobile) == 10:
            mobile = "91" + mobile
        
        return mobile
    
    @classmethod
    def _log_message(cls, message_type: str, recipient: str, status: str, response: Dict = None):
        """Log WhatsApp message activity"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": message_type,
            "recipient": recipient,
            "status": status,
            "response": response
        }
        
        if status == "success":
            logger.info(f"WhatsApp message sent: {log_data}")
        else:
            logger.error(f"WhatsApp message failed: {log_data}")
    
    # =====================================
    # OTP Messages
    
    @classmethod
    def send_otp(cls, mobile: str, otp: str) -> bool:
        """
        Send OTP for loyalty points redemption
        Uses template: loyalty_otp_template
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "template",
                "template": {
                    "name": settings.WHATSAPP_OTP_TEMPLATE or "loyalty_otp_template",
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": otp
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("OTP", mobile, "success", response.json())
                return True
            else:
                cls._log_message("OTP", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending OTP to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Invoice Messages
    
    @classmethod
    def send_invoice(cls, mobile: str, bill_no: str, amount: Decimal, 
                    points_earned: int = 0, points_balance: int = 0,
                    db_session=None) -> bool:
        """
        Send invoice with PDF attachment
        First sends text message, then PDF
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            # Step 1: Send invoice notification message
            text_message = (
                f"Thank you for shopping with us! 🛍️\n\n"
                f"Bill No: {bill_no}\n"
                f"Amount: ₹{amount:.2f}\n"
            )
            
            if points_earned > 0:
                text_message += (
                    f"Points Earned: {points_earned}\n"
                    f"Points Balance: {points_balance}\n"
                )
            
            text_message += "\nYour invoice PDF is attached below."
            
            # Send text message
            text_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": text_message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=text_payload
            )
            
            if response.status_code != 200:
                cls._log_message("Invoice Text", mobile, "failed", response.json())
                return False
            
            # Step 2: Generate and send PDF
            if db_session:
                sale = db_session.query(Sale).filter(Sale.bill_no == bill_no).first()
                if sale:
                    # Generate PDF (you'll need to implement PDFService)
                    pdf_content = PDFService.generate_invoice_pdf(sale)
                    
                    # Upload PDF to WhatsApp
                    media_id = cls._upload_media(pdf_content, "application/pdf", f"{bill_no}.pdf")
                    
                    if media_id:
                        # Send PDF document
                        doc_payload = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": formatted_phone,
                            "type": "document",
                            "document": {
                                "id": media_id,
                                "caption": f"Invoice: {bill_no}",
                                "filename": f"{bill_no}.pdf"
                            }
                        }
                        
                        response = requests.post(
                            cls._get_url(),
                            headers=cls._get_headers(),
                            json=doc_payload
                        )
            
            cls._log_message("Invoice", mobile, "success", {"bill_no": bill_no})
            return True
            
        except Exception as e:
            logger.error(f"Error sending invoice to {mobile}: {str(e)}")
            return False
    
    @classmethod
    def _upload_media(cls, content: bytes, mime_type: str, filename: str) -> Optional[str]:
        """
        Upload media to WhatsApp and get media ID
        """
        try:
            upload_url = cls._get_url("media")
            
            files = {
                'file': (filename, content, mime_type)
            }
            
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
            }
            
            response = requests.post(
                upload_url,
                headers=headers,
                files=files,
                data={
                    "messaging_product": "whatsapp"
                }
            )
            
            if response.status_code == 200:
                return response.json().get("id")
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            return None
    
    # =====================================
    # Return Credit Notifications
    
    @classmethod
    def send_return_credit_notification(cls, mobile: str, rc_no: str, amount: Decimal) -> bool:
        """
        Send return credit notification to customer
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            message = (
                f"Return Credit Issued ✅\n\n"
                f"Credit Note: {rc_no}\n"
                f"Amount: ₹{amount:.2f}\n\n"
                f"This credit can be used in your next purchase.\n"
                f"Valid for 6 months from issue date.\n\n"
                f"Thank you for shopping with us!"
            )
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Return Credit", mobile, "success", {"rc_no": rc_no})
                return True
            else:
                cls._log_message("Return Credit", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending return credit to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Coupon Messages
    
    @classmethod
    def send_coupon(cls, mobile: str, coupon_code: str, discount_value: str, valid_till: str) -> bool:
        """
        Send coupon to customer
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            message = (
                f"🎁 Special Offer Just for You! 🎁\n\n"
                f"Coupon Code: *{coupon_code}*\n"
                f"Discount: {discount_value}\n"
                f"Valid Till: {valid_till}\n\n"
                f"Use this code at checkout to avail your discount.\n"
                f"Terms & conditions apply.\n\n"
                f"Happy Shopping! 🛍️"
            )
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Coupon", mobile, "success", {"coupon": coupon_code})
                return True
            else:
                cls._log_message("Coupon", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending coupon to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Birthday Wishes
    
    @classmethod
    def send_birthday_wishes(cls, mobile: str, customer_name: str, kid_name: str) -> bool:
        """
        Send birthday wishes for customer's kids
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            message = (
                f"🎂 Happy Birthday {kid_name}! 🎉\n\n"
                f"Dear {customer_name},\n\n"
                f"Wishing {kid_name} a very Happy Birthday! "
                f"May this special day be filled with joy, laughter, and wonderful memories.\n\n"
                f"As a birthday gift, enjoy 20% off on your next purchase! "
                f"Visit our store to claim your special birthday discount.\n\n"
                f"Best Wishes,\n"
                f"{settings.COMPANY_NAME or 'Your Store'} 🎈"
            )
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Birthday", mobile, "success", {"kid": kid_name})
                return True
            else:
                cls._log_message("Birthday", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending birthday wishes to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Promotional Messages
    
    @classmethod
    def send_promotional_message(cls, mobile: str, message: str, 
                                 image_url: Optional[str] = None) -> bool:
        """
        Send promotional/marketing messages
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            if image_url:
                # Send image with caption
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": formatted_phone,
                    "type": "image",
                    "image": {
                        "link": image_url,
                        "caption": message
                    }
                }
            else:
                # Send text only
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": formatted_phone,
                    "type": "text",
                    "text": {
                        "preview_url": True,
                        "body": message
                    }
                }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Promotional", mobile, "success")
                return True
            else:
                cls._log_message("Promotional", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending promotional message to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Bulk Messaging
    
    @classmethod
    async def send_bulk_messages(cls, recipients: List[Dict[str, str]], 
                                 message_template: str,
                                 personalized: bool = True) -> Dict[str, int]:
        """
        Send bulk messages asynchronously
        Recipients: [{"mobile": "xxx", "name": "xxx", "custom_field": "xxx"}]
        """
        results = {"success": 0, "failed": 0}
        
        async def send_single(recipient):
            try:
                mobile = recipient.get("mobile")
                
                if personalized:
                    # Replace placeholders in template
                    message = message_template
                    for key, value in recipient.items():
                        placeholder = f"{{{key}}}"
                        if placeholder in message:
                            message = message.replace(placeholder, str(value))
                else:
                    message = message_template
                
                # Send message
                success = cls.send_promotional_message(mobile, message)
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    
                # Rate limiting - 80 messages per second max
                await asyncio.sleep(0.015)
                
            except Exception as e:
                logger.error(f"Error in bulk send: {str(e)}")
                results["failed"] += 1
        
        # Send all messages concurrently with limit
        tasks = [send_single(recipient) for recipient in recipients]
        await asyncio.gather(*tasks)
        
        return results
    
    # =====================================
    # Order Status Updates
    
    @classmethod
    def send_order_status(cls, mobile: str, order_no: str, status: str, 
                         details: Optional[str] = None) -> bool:
        """
        Send order/purchase status updates
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            status_messages = {
                "confirmed": f"✅ Order {order_no} Confirmed!\nYour order has been confirmed and is being processed.",
                "ready": f"📦 Order {order_no} is Ready!\nYour order is ready for pickup/delivery.",
                "delivered": f"✅ Order {order_no} Delivered!\nThank you for your purchase. We hope you enjoy your items!",
                "cancelled": f"❌ Order {order_no} Cancelled\nYour order has been cancelled. Any payment will be refunded."
            }
            
            message = status_messages.get(status, f"Order {order_no} Status: {status}")
            
            if details:
                message += f"\n\n{details}"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Order Status", mobile, "success", {"order": order_no})
                return True
            else:
                cls._log_message("Order Status", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending order status to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Payment Reminders
    
    @classmethod
    def send_payment_reminder(cls, mobile: str, amount: Decimal, due_date: date, 
                             bill_details: Optional[str] = None) -> bool:
        """
        Send payment reminder for credit purchases
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            message = (
                f"💳 Payment Reminder\n\n"
                f"Amount Due: ₹{amount:.2f}\n"
                f"Due Date: {due_date.strftime('%d-%m-%Y')}\n"
            )
            
            if bill_details:
                message += f"\nBill Details:\n{bill_details}\n"
            
            message += (
                f"\nPlease make the payment by the due date to avoid any late charges.\n"
                f"Thank you for your business!"
            )
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Payment Reminder", mobile, "success")
                return True
            else:
                cls._log_message("Payment Reminder", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending payment reminder to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Interactive Messages (Buttons/Lists)
    
    @classmethod
    def send_interactive_buttons(cls, mobile: str, body_text: str, 
                                 buttons: List[Dict[str, str]]) -> bool:
        """
        Send interactive message with buttons
        buttons: [{"id": "btn1", "title": "Yes"}, {"id": "btn2", "title": "No"}]
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": body_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": btn["id"],
                                    "title": btn["title"][:20]  # Max 20 chars
                                }
                            } for btn in buttons[:3]  # Max 3 buttons
                        ]
                    }
                }
            }
            
            response = requests.post(
                cls._get_url(),
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                cls._log_message("Interactive", mobile, "success")
                return True
            else:
                cls._log_message("Interactive", mobile, "failed", response.json())
                return False
                
        except Exception as e:
            logger.error(f"Error sending interactive message to {mobile}: {str(e)}")
            return False
    
    # =====================================
    # Webhook Handler for Incoming Messages
    
    @classmethod
    def handle_webhook(cls, webhook_data: Dict) -> Dict[str, Any]:
        """
        Handle incoming webhook from WhatsApp
        Process incoming messages, status updates, etc.
        """
        try:
            entry = webhook_data.get("entry", [])
            if not entry:
                return {"status": "no_entry"}
            
            changes = entry[0].get("changes", [])
            if not changes:
                return {"status": "no_changes"}
            
            value = changes[0].get("value", {})
            
            # Handle message status updates
            if "statuses" in value:
                status = value["statuses"][0]
                message_id = status.get("id")
                status_type = status.get("status")  # sent, delivered, read
                recipient = status.get("recipient_id")
                
                logger.info(f"Message {message_id} to {recipient}: {status_type}")
                return {"status": "status_update", "type": status_type}
            
            # Handle incoming messages
            if "messages" in value:
                message = value["messages"][0]
                from_number = message.get("from")
                message_type = message.get("type")
                
                if message_type == "text":
                    text = message.get("text", {}).get("body")
                    # Process text message
                    logger.info(f"Received text from {from_number}: {text}")
                    
                elif message_type == "interactive":
                    interactive = message.get("interactive", {})
                    response_type = interactive.get("type")
                    
                    if response_type == "button_reply":
                        button_id = interactive.get("button_reply", {}).get("id")
                        # Process button response
                        logger.info(f"Button clicked by {from_number}: {button_id}")
                
                return {"status": "message_received", "from": from_number}
            
            return {"status": "unknown"}
            
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    # =====================================
    # Template Management
    
    @classmethod
    def create_message_template(cls, name: str, category: str, 
                               components: List[Dict]) -> bool:
        """
        Create a new message template
        Note: Templates need to be approved by WhatsApp
        """
        try:
            url = f"{cls.BASE_URL}/{settings.WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates"
            
            payload = {
                "name": name,
                "category": category,  # MARKETING, UTILITY, or AUTHENTICATION
                "language": "en",
                "components": components
            }
            
            response = requests.post(
                url,
                headers=cls._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Template {name} created successfully")
                return True
            else:
                logger.error(f"Failed to create template: {response.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return False
    
    # =====================================
    # Utility Functions
    
    @classmethod
    def check_phone_number_status(cls, mobile: str) -> Dict[str, Any]:
        """
        Check if a phone number has WhatsApp
        """
        try:
            formatted_phone = cls._format_phone_number(mobile)
            
            url = f"{cls.BASE_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/phone_numbers"
            params = {"numbers": formatted_phone}
            
            response = requests.get(
                url,
                headers=cls._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "exists": True,
                    "is_whatsapp": data.get("is_valid", False)
                }
            
            return {"exists": False, "is_whatsapp": False}
            
        except Exception as e:
            logger.error(f"Error checking phone status: {str(e)}")
            return {"exists": False, "is_whatsapp": False}
    
    @classmethod
    def get_media_url(cls, media_id: str) -> Optional[str]:
        """
        Get download URL for uploaded media
        """
        try:
            url = f"{cls.BASE_URL}/{media_id}"
            
            response = requests.get(
                url,
                headers=cls._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("url")
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting media URL: {str(e)}")
            return None