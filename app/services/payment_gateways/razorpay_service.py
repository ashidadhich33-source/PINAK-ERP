# backend/app/services/payment_gateways/razorpay_service.py
import razorpay
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
import logging

from ...models.payment_gateways import PaymentGateway, PaymentTransaction, PaymentRefund
from ...core.exceptions import PaymentGatewayError, PaymentValidationError

logger = logging.getLogger(__name__)

class RazorpayService:
    """Razorpay Payment Gateway Service"""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.client = razorpay.Client(
            auth=(gateway.api_key, gateway.api_secret)
        )
        self.is_test_mode = gateway.is_test_mode
    
    def create_payment_order(self, amount: Decimal, currency: str = 'INR', 
                           order_id: str = None, customer_data: Dict = None) -> Dict[str, Any]:
        """Create a Razorpay payment order"""
        try:
            # Convert amount to paise (Razorpay expects amount in smallest currency unit)
            amount_paise = int(amount * 100)
            
            order_data = {
                'amount': amount_paise,
                'currency': currency,
                'receipt': order_id or f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'notes': customer_data or {}
            }
            
            # Add customer information if provided
            if customer_data:
                if 'name' in customer_data:
                    order_data['notes']['customer_name'] = customer_data['name']
                if 'email' in customer_data:
                    order_data['notes']['customer_email'] = customer_data['email']
                if 'phone' in customer_data:
                    order_data['notes']['customer_phone'] = customer_data['phone']
            
            response = self.client.order.create(data=order_data)
            
            return {
                'success': True,
                'order_id': response['id'],
                'amount': amount,
                'currency': currency,
                'receipt': response['receipt'],
                'status': response['status'],
                'created_at': response['created_at']
            }
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to create Razorpay order: {str(e)}")
    
    def create_payment_link(self, amount: Decimal, description: str, 
                          customer_data: Dict = None, expires_at: datetime = None) -> Dict[str, Any]:
        """Create a Razorpay payment link"""
        try:
            amount_paise = int(amount * 100)
            
            payment_link_data = {
                'amount': amount_paise,
                'currency': 'INR',
                'description': description,
                'customer': customer_data or {},
                'notify': {
                    'sms': True,
                    'email': True
                }
            }
            
            if expires_at:
                payment_link_data['expire_by'] = int(expires_at.timestamp())
            
            response = self.client.payment_link.create(data=payment_link_data)
            
            return {
                'success': True,
                'payment_link_id': response['id'],
                'short_url': response['short_url'],
                'amount': amount,
                'status': response['status'],
                'created_at': response['created_at']
            }
            
        except Exception as e:
            logger.error(f"Razorpay payment link creation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to create Razorpay payment link: {str(e)}")
    
    def capture_payment(self, payment_id: str, amount: Decimal = None) -> Dict[str, Any]:
        """Capture a Razorpay payment"""
        try:
            capture_data = {}
            if amount:
                capture_data['amount'] = int(amount * 100)
            
            response = self.client.payment.capture(payment_id, capture_data)
            
            return {
                'success': True,
                'payment_id': response['id'],
                'amount': Decimal(response['amount']) / 100,
                'currency': response['currency'],
                'status': response['status'],
                'captured': response['captured']
            }
            
        except Exception as e:
            logger.error(f"Razorpay payment capture failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to capture Razorpay payment: {str(e)}")
    
    def refund_payment(self, payment_id: str, amount: Decimal = None, 
                      notes: str = None) -> Dict[str, Any]:
        """Refund a Razorpay payment"""
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = int(amount * 100)
            if notes:
                refund_data['notes'] = notes
            
            response = self.client.payment.refund(payment_id, refund_data)
            
            return {
                'success': True,
                'refund_id': response['id'],
                'payment_id': response['payment_id'],
                'amount': Decimal(response['amount']) / 100,
                'currency': response['currency'],
                'status': response['status'],
                'notes': response.get('notes', ''),
                'created_at': response['created_at']
            }
            
        except Exception as e:
            logger.error(f"Razorpay payment refund failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to refund Razorpay payment: {str(e)}")
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get Razorpay payment details"""
        try:
            response = self.client.payment.fetch(payment_id)
            
            return {
                'success': True,
                'payment_id': response['id'],
                'amount': Decimal(response['amount']) / 100,
                'currency': response['currency'],
                'status': response['status'],
                'method': response['method'],
                'description': response.get('description', ''),
                'captured': response['captured'],
                'created_at': response['created_at']
            }
            
        except Exception as e:
            logger.error(f"Razorpay payment fetch failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to fetch Razorpay payment: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Razorpay webhook signature"""
        try:
            expected_signature = hmac.new(
                self.gateway.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Razorpay webhook signature verification failed: {str(e)}")
            return False
    
    def process_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """Process Razorpay webhook"""
        try:
            # Verify signature
            if not self.verify_webhook_signature(json.dumps(payload), signature):
                raise PaymentValidationError("Invalid webhook signature")
            
            event_type = payload.get('event')
            payment_data = payload.get('payload', {}).get('payment', {})
            
            return {
                'success': True,
                'event_type': event_type,
                'payment_id': payment_data.get('id'),
                'amount': Decimal(payment_data.get('amount', 0)) / 100,
                'currency': payment_data.get('currency'),
                'status': payment_data.get('status'),
                'method': payment_data.get('method'),
                'created_at': payment_data.get('created_at')
            }
            
        except Exception as e:
            logger.error(f"Razorpay webhook processing failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to process Razorpay webhook: {str(e)}")
    
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods"""
        return [
            {
                'method': 'card',
                'name': 'Credit/Debit Card',
                'enabled': True,
                'fee_percent': float(self.gateway.processing_fee_percent),
                'fee_fixed': float(self.gateway.processing_fee_fixed)
            },
            {
                'method': 'upi',
                'name': 'UPI',
                'enabled': True,
                'fee_percent': 0.0,
                'fee_fixed': 0.0
            },
            {
                'method': 'netbanking',
                'name': 'Net Banking',
                'enabled': True,
                'fee_percent': 0.0,
                'fee_fixed': 0.0
            },
            {
                'method': 'wallet',
                'name': 'Digital Wallet',
                'enabled': True,
                'fee_percent': 0.0,
                'fee_fixed': 0.0
            }
        ]
    
    def calculate_fees(self, amount: Decimal) -> Dict[str, Decimal]:
        """Calculate payment gateway fees"""
        try:
            # Calculate percentage fee
            percentage_fee = amount * self.gateway.processing_fee_percent / 100
            
            # Add fixed fee
            total_fee = percentage_fee + self.gateway.processing_fee_fixed
            
            # Add GST on fees if applicable
            gst_on_fee = Decimal('0.00')
            if self.gateway.gst_on_fee:
                gst_on_fee = total_fee * Decimal('0.18')  # 18% GST
            
            return {
                'percentage_fee': percentage_fee,
                'fixed_fee': self.gateway.processing_fee_fixed,
                'total_fee': total_fee,
                'gst_on_fee': gst_on_fee,
                'total_fee_with_gst': total_fee + gst_on_fee
            }
            
        except Exception as e:
            logger.error(f"Fee calculation failed: {str(e)}")
            return {
                'percentage_fee': Decimal('0.00'),
                'fixed_fee': Decimal('0.00'),
                'total_fee': Decimal('0.00'),
                'gst_on_fee': Decimal('0.00'),
                'total_fee_with_gst': Decimal('0.00')
            }