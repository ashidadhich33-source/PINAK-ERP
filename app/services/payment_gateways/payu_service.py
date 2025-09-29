# backend/app/services/payment_gateways/payu_service.py
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

class PayUService:
    """PayU Payment Gateway Service"""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.merchant_key = gateway.api_key
        self.merchant_salt = gateway.api_secret
        self.is_test_mode = gateway.is_test_mode
        
        # PayU URLs
        if self.is_test_mode:
            self.base_url = "https://test.payu.in"
        else:
            self.base_url = "https://secure.payu.in"
    
    def _generate_hash(self, params: Dict[str, Any]) -> str:
        """Generate PayU hash for authentication"""
        try:
            # Sort parameters by key
            sorted_params = sorted(params.items())
            
            # Create hash string
            hash_string = ""
            for key, value in sorted_params:
                if value and key != 'hash':
                    hash_string += f"{key}={value}&"
            
            # Add salt
            hash_string += f"salt={self.merchant_salt}"
            
            # Generate SHA512 hash
            hash_object = hashlib.sha512(hash_string.encode())
            return hash_object.hexdigest()
            
        except Exception as e:
            logger.error(f"PayU hash generation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to generate PayU hash: {str(e)}")
    
    def create_payment_request(self, amount: Decimal, currency: str = 'INR',
                             order_id: str = None, customer_data: Dict = None,
                             product_info: str = None) -> Dict[str, Any]:
        """Create a PayU payment request"""
        try:
            # Generate order ID if not provided
            if not order_id:
                order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare payment parameters
            payment_params = {
                'key': self.merchant_key,
                'txnid': order_id,
                'amount': str(amount),
                'productinfo': product_info or 'ERP Payment',
                'firstname': customer_data.get('name', 'Customer') if customer_data else 'Customer',
                'email': customer_data.get('email', '') if customer_data else '',
                'phone': customer_data.get('phone', '') if customer_data else '',
                'surl': self.gateway.return_url or f"{self.base_url}/success",
                'furl': self.gateway.cancel_url or f"{self.base_url}/failure",
                'udf1': customer_data.get('customer_id', '') if customer_data else '',
                'udf2': customer_data.get('reference_type', '') if customer_data else '',
                'udf3': customer_data.get('reference_id', '') if customer_data else '',
                'udf4': customer_data.get('reference_number', '') if customer_data else '',
                'udf5': customer_data.get('notes', '') if customer_data else ''
            }
            
            # Generate hash
            payment_params['hash'] = self._generate_hash(payment_params)
            
            # Create payment URL
            payment_url = f"{self.base_url}/_payment"
            
            return {
                'success': True,
                'payment_url': payment_url,
                'payment_params': payment_params,
                'order_id': order_id,
                'amount': amount,
                'currency': currency,
                'hash': payment_params['hash']
            }
            
        except Exception as e:
            logger.error(f"PayU payment request creation failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to create PayU payment request: {str(e)}")
    
    def verify_payment_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PayU payment response"""
        try:
            # Extract response parameters
            txnid = response_data.get('txnid')
            amount = response_data.get('amount')
            productinfo = response_data.get('productinfo')
            firstname = response_data.get('firstname')
            email = response_data.get('email')
            phone = response_data.get('phone')
            status = response_data.get('status')
            hash_received = response_data.get('hash')
            
            # Create verification parameters
            verification_params = {
                'key': self.merchant_key,
                'txnid': txnid,
                'amount': amount,
                'productinfo': productinfo,
                'firstname': firstname,
                'email': email,
                'phone': phone,
                'status': status
            }
            
            # Generate hash for verification
            hash_generated = self._generate_hash(verification_params)
            
            # Verify hash
            if hash_generated != hash_received:
                raise PaymentValidationError("Invalid PayU payment response hash")
            
            return {
                'success': True,
                'transaction_id': txnid,
                'amount': Decimal(amount),
                'status': status,
                'customer_name': firstname,
                'customer_email': email,
                'customer_phone': phone,
                'product_info': productinfo,
                'verified': True
            }
            
        except Exception as e:
            logger.error(f"PayU payment verification failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to verify PayU payment: {str(e)}")
    
    def get_payment_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get PayU payment status"""
        try:
            # Prepare status check parameters
            status_params = {
                'key': self.merchant_key,
                'command': 'verify_payment',
                'hash': '',
                'var1': transaction_id
            }
            
            # Generate hash
            status_params['hash'] = self._generate_hash(status_params)
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/merchant/postservice.php?form=2",
                data=status_params,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'status': response_data.get('status'),
                    'amount': Decimal(response_data.get('amount', 0)),
                    'response': response_data
                }
            else:
                raise PaymentGatewayError(f"PayU API request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"PayU payment status check failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to check PayU payment status: {str(e)}")
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None,
                      refund_reason: str = None) -> Dict[str, Any]:
        """Refund a PayU payment"""
        try:
            # Prepare refund parameters
            refund_params = {
                'key': self.merchant_key,
                'command': 'refund',
                'var1': transaction_id,
                'var2': str(amount) if amount else '0',  # 0 for full refund
                'var3': refund_reason or 'Refund request'
            }
            
            # Generate hash
            refund_params['hash'] = self._generate_hash(refund_params)
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/merchant/postservice.php?form=2",
                data=refund_params,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'refund_amount': amount,
                    'refund_status': response_data.get('status'),
                    'refund_id': response_data.get('refund_id'),
                    'response': response_data
                }
            else:
                raise PaymentGatewayError(f"PayU refund request failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"PayU payment refund failed: {str(e)}")
            raise PaymentGatewayError(f"Failed to refund PayU payment: {str(e)}")
    
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
                'method': 'netbanking',
                'name': 'Net Banking',
                'enabled': True,
                'fee_percent': 0.0,
                'fee_fixed': 0.0
            },
            {
                'method': 'upi',
                'name': 'UPI',
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