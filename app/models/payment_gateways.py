# backend/app/models/payment_gateways.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class PaymentGatewayType(PyEnum):
    """Payment Gateway Types"""
    RAZORPAY = "razorpay"
    PAYU = "payu"
    PHONEPE = "phonepay"
    STRIPE = "stripe"
    PAYPAL = "paypal"

class PaymentStatus(PyEnum):
    """Payment Status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"

class PaymentGateway(BaseModel):
    """Payment Gateway Configuration"""
    __tablename__ = "payment_gateway"
    
    gateway_name = Column(String(100), nullable=False)
    gateway_type = Column(Enum(PaymentGatewayType), nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Gateway Configuration
    api_key = Column(String(500), nullable=False)
    api_secret = Column(String(500), nullable=False)
    webhook_secret = Column(String(500), nullable=True)
    merchant_id = Column(String(100), nullable=True)
    
    # Gateway Settings
    supported_currencies = Column(JSON, nullable=True)  # ["INR", "USD"]
    supported_payment_methods = Column(JSON, nullable=True)  # ["card", "upi", "netbanking"]
    min_amount = Column(Numeric(10, 2), default=1.00)
    max_amount = Column(Numeric(15, 2), default=1000000.00)
    
    # Fee Configuration
    processing_fee_percent = Column(Numeric(5, 4), default=0.00)
    processing_fee_fixed = Column(Numeric(10, 2), default=0.00)
    gst_on_fee = Column(Boolean, default=True)
    
    # Gateway URLs
    api_url = Column(String(500), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    return_url = Column(String(500), nullable=True)
    cancel_url = Column(String(500), nullable=True)
    
    # Additional Configuration
    additional_config = Column(JSON, nullable=True)
    is_test_mode = Column(Boolean, default=True)
    
    # Relationships
    payments = relationship("PaymentTransaction", back_populates="gateway")
    
    def __repr__(self):
        return f"<PaymentGateway(name='{self.gateway_name}', type='{self.gateway_type}')>"

class PaymentTransaction(BaseModel):
    """Payment Transaction Records"""
    __tablename__ = "payment_transaction"
    
    # Transaction Details
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    gateway_transaction_id = Column(String(200), nullable=True, index=True)
    order_id = Column(String(100), nullable=True, index=True)
    
    # Payment Information
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default='INR')
    payment_method = Column(String(50), nullable=True)  # card, upi, netbanking, wallet
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Gateway Information
    gateway_id = Column(Integer, ForeignKey('payment_gateway.id'), nullable=False)
    gateway_response = Column(JSON, nullable=True)
    gateway_fees = Column(Numeric(10, 2), default=0.00)
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    customer_email = Column(String(100), nullable=True)
    customer_phone = Column(String(15), nullable=True)
    
    # Transaction References
    reference_type = Column(String(50), nullable=True)  # sales_invoice, purchase_invoice
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Payment URLs
    payment_url = Column(String(1000), nullable=True)
    callback_url = Column(String(1000), nullable=True)
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Additional Information
    failure_reason = Column(Text, nullable=True)
    refund_amount = Column(Numeric(12, 2), default=0.00)
    refund_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    gateway = relationship("PaymentGateway", back_populates="payments")
    customer = relationship("Customer")
    refunds = relationship("PaymentRefund", back_populates="transaction")
    
    def __repr__(self):
        return f"<PaymentTransaction(id='{self.transaction_id}', amount={self.amount}, status='{self.payment_status}')>"

class PaymentRefund(BaseModel):
    """Payment Refund Records"""
    __tablename__ = "payment_refund"
    
    # Refund Details
    refund_id = Column(String(100), unique=True, nullable=False, index=True)
    gateway_refund_id = Column(String(200), nullable=True, index=True)
    transaction_id = Column(Integer, ForeignKey('payment_transaction.id'), nullable=False)
    
    # Refund Information
    refund_amount = Column(Numeric(12, 2), nullable=False)
    refund_reason = Column(Text, nullable=True)
    refund_status = Column(String(20), default='pending')  # pending, processed, failed
    
    # Gateway Response
    gateway_response = Column(JSON, nullable=True)
    gateway_fees = Column(Numeric(10, 2), default=0.00)
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Additional Information
    failure_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("PaymentTransaction", back_populates="refunds")
    
    def __repr__(self):
        return f"<PaymentRefund(id='{self.refund_id}', amount={self.refund_amount}, status='{self.refund_status}')>"

class PaymentWebhook(BaseModel):
    """Payment Webhook Logs"""
    __tablename__ = "payment_webhook"
    
    # Webhook Details
    webhook_id = Column(String(100), unique=True, nullable=False, index=True)
    gateway_id = Column(Integer, ForeignKey('payment_gateway.id'), nullable=False)
    transaction_id = Column(String(100), nullable=True, index=True)
    
    # Webhook Information
    event_type = Column(String(50), nullable=False)  # payment.success, payment.failed
    webhook_data = Column(JSON, nullable=False)
    signature = Column(String(500), nullable=True)
    
    # Processing Status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    received_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gateway = relationship("PaymentGateway")
    
    def __repr__(self):
        return f"<PaymentWebhook(id='{self.webhook_id}', event='{self.event_type}', processed={self.processed})>"

class PaymentAnalytics(BaseModel):
    """Payment Analytics and Reporting"""
    __tablename__ = "payment_analytics"
    
    # Analytics Period
    date = Column(DateTime, nullable=False, index=True)
    gateway_id = Column(Integer, ForeignKey('payment_gateway.id'), nullable=True)
    
    # Transaction Metrics
    total_transactions = Column(Integer, default=0)
    successful_transactions = Column(Integer, default=0)
    failed_transactions = Column(Integer, default=0)
    cancelled_transactions = Column(Integer, default=0)
    
    # Amount Metrics
    total_amount = Column(Numeric(15, 2), default=0.00)
    successful_amount = Column(Numeric(15, 2), default=0.00)
    failed_amount = Column(Numeric(15, 2), default=0.00)
    refunded_amount = Column(Numeric(15, 2), default=0.00)
    
    # Fee Metrics
    total_fees = Column(Numeric(12, 2), default=0.00)
    gateway_fees = Column(Numeric(12, 2), default=0.00)
    processing_fees = Column(Numeric(12, 2), default=0.00)
    
    # Performance Metrics
    success_rate = Column(Numeric(5, 2), default=0.00)
    average_transaction_amount = Column(Numeric(12, 2), default=0.00)
    average_processing_time = Column(Numeric(8, 2), default=0.00)  # in seconds
    
    # Relationships
    gateway = relationship("PaymentGateway")
    
    def __repr__(self):
        return f"<PaymentAnalytics(date='{self.date}', transactions={self.total_transactions}, amount={self.total_amount})>"