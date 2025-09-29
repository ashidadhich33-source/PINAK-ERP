# backend/app/services/payment_gateways/phonepay_service.py
import requests
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
import logging
from urllib.parse import urlencode

from ...models.payment_gateways import PaymentGateway, PaymentTransaction, PaymentRefund
from ...core.exceptions import PaymentGatewayError, PaymentValidationError

logger = logging.getLogger(__name__)

class PhonePeService:
    """PhonePe Payment Gateway Service"""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.merchant_id = gateway.merchant_id
        self.api_key = gateway.api_key
        self.api_secret = gateway.api_secret
        self.is_test_mode = gateway.is_test_mode
        
        # PhonePe URLs
        if self.is_test_mode:
            self.base_url = "https://api-preprod.phonepe.com/apis/pg-sandbox"
        else:
            self.base_url = "https://api.phonepe.com/apis/pg"
    
    def _generate_checksum(self, payload: str) -> str:
        """Generate PhonePe checksum for authentication"""
        try:
            checksum = hmac.new(
                self.api_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return checksum
            
        except Exception as e:
            logger.error(f"PhonePe checksum generation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to generate PhonePe checksum: {str(e)}")
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make authenticated request to PhonePe API"""
        try:
            # Convert payload to JSON
            payload_json = json.dumps(payload)
            
            # Generate checksum
            checksum = self._generate_checksum(payload_json)
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-VERIFY': checksum,
                'X-MERCHANT-ID': self.merchant_id
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}{endpoint}",
                data=payload_json,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise PaymentGatewayError(f"PhonePe API request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"PhonePe API request failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to make PhonePe API request: {str(e)}")
    
    def create_payment_request(self, amount: Decimal, currency: str = 'INR',
                             order_id: str = None, customer_data: Dict = None,
                             redirect_url: str = None) -> Dict[str, Any]:
        """Create a PhonePe payment request"""
        try:
            # Generate order ID if not provided
            if not order_id:
                order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare payment request
            payment_request = {
                'merchantId': self.merchant_id,
                'merchantTransactionId': order_id,
                'merchantUserId': customer_data.get('customer_id', '') if customer_data else '',
                'amount': int(amount * 100),  # Amount in paise
                'redirectUrl': redirect_url or self.gateway.return_url,
                'redirectMode': 'POST',
                'callbackUrl': self.gateway.webhook_url,
                'mobileNumber': customer_data.get('phone', '') if customer_data else '',
                'paymentInstrument': {
                    'type': 'PAY_PAGE'
                }
            }
            
            # Make API request
            response = self._make_request('/pg/v1/pay', payment_request)
            
            if response.get('success'):
                return {
                    'success': True,
                    'payment_url': response['data']['instrumentResponse']['redirectInfo']['url'],
                    'order_id': order_id,
                    'amount': amount,
                    'currency': currency,
                    'merchant_transaction_id': response['data']['merchantTransactionId'],
                    'transaction_id': response['data']['transactionId']
                }
            else:
                raise PaymentGatewayError(f"PhonePe payment request failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"PhonePe payment request creation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to create PhonePe payment request: {str(e)}")
    
    def check_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check PhonePe payment status"""
        try:
            # Prepare status check request
            status_request = {
                'merchantId': self.merchant_id,
                'merchantTransactionId': transaction_id
            }
            
            # Make API request
            response = self._make_request('/pg/v1/status', status_request)
            
            if response.get('success'):
                payment_data = response['data']
                return {
                    'success': True,
                    'transaction_id': payment_data['transactionId'],
                    'merchant_transaction_id': payment_data['merchantTransactionId'],
                    'amount': Decimal(payment_data['amount']) / 100,
                    'currency': payment_data['currency'],
                    'status': payment_data['state'],
                    'response_code': payment_data['responseCode'],
                    'response_message': payment_data['responseMessage']
                }
            else:
                raise PaymentGatewayError(f"PhonePe status check failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"PhonePe payment status check failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to check PhonePe payment status: {str(e)}")
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None,
                      refund_reason: str = None) -> Dict[str, Any]:
        """Refund a PhonePe payment"""
        try:
            # Prepare refund request
            refund_request = {
                'merchantId': self.merchant_id,
                'merchantUserId': 'refund_user',
                'originalTransactionId': transaction_id,
                'amount': int(amount * 100) if amount else 0,  # 0 for full refund
                'callbackUrl': self.gateway.webhook_url
            }
            
            # Make API request
            response = self._make_request('/pg/v1/refund', refund_request)
            
            if response.get('success'):
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'refund_amount': amount,
                    'refund_status': response['data']['state'],
                    'refund_id': response['data']['transactionId'],
                    'response_code': response['data']['responseCode'],
                    'response_message': response['data']['responseMessage']
                }
            else:
                raise PaymentGatewayError(f"PhonePe refund request failed: {response.get('message', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"PhonePe payment refund failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to refund PhonePe payment: {str(e)}")
    
    def verify_webhook(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify PhonePe webhook signature"""
        try:
            # Extract checksum from signature
            received_checksum = signature.split('###')[1] if '###' in signature else signature
            
            # Generate expected checksum
            payload_json = json.dumps(payload)
            expected_checksum = self._generate_checksum(payload_json)
            
            return hmac.compare_digest(received_checksum, expected_checksum)
            
        except Exception as e:
            logger.error(f"PhonePe webhook verification failed: {str(e)}")
            return False
    
    def process_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """Process PhonePe webhook"""
        try:
            # Verify webhook signature
            if not self.verify_webhook(payload, signature):
                raise PaymentValidationError("Invalid PhonePe webhook signature")
            
            # Extract payment data
            payment_data = payload.get('data', {})
            
            return {
                'success': True,
                'transaction_id': payment_data.get('transactionId'),
                'merchant_transaction_id': payment_data.get('merchantTransactionId'),
                'amount': Decimal(payment_data.get('amount', 0)) / 100,
                'currency': payment_data.get('currency'),
                'status': payment_data.get('state'),
                'response_code': payment_data.get('responseCode'),
                'response_message': payment_data.get('responseMessage')
            }
            
        except Exception as e:
            logger.error(f"PhonePe webhook processing failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to process PhonePe webhook: {str(e)}")
    
    def get_payment_methods(self) -> List[Dict[str, Any]]:
        """Get available payment methods"""
        return [
            {
                'method': 'upi',
                'name': 'UPI',
                'enabled': True,
                'fee_percent': 0.0,
                'fee_fixed': 0.0
            },
            {
                'method': 'card',
                'name': 'Credit/Debit Card',
                'enabled': True,
                'fee_percent': float(self.gateway.processing_fee_percent),
                'fee_fixed': float(self.gateway.processing_fee_fixed)
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