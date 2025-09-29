# backend/app/api/endpoints/payment_gateways/payment_gateways.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.core import Company, User
from ...models.payment_gateways import PaymentGateway, PaymentTransaction, PaymentRefund, PaymentGatewayType, PaymentStatus
from ...core.security import get_current_user, require_permission
from ...services.payment_gateways.razorpay_service import RazorpayService
from ...services.payment_gateways.payu_service import PayUService
from ...services.payment_gateways.phonepay_service import PhonePeService

router = APIRouter()

# Pydantic schemas for Payment Gateway
class PaymentGatewayCreateRequest(BaseModel):
    gateway_name: str
    gateway_type: str
    api_key: str
    api_secret: str
    merchant_id: Optional[str] = None
    webhook_secret: Optional[str] = None
    is_test_mode: bool = True
    processing_fee_percent: Decimal = Decimal('0.00')
    processing_fee_fixed: Decimal = Decimal('0.00')
    gst_on_fee: bool = True
    supported_currencies: Optional[List[str]] = None
    supported_payment_methods: Optional[List[str]] = None
    min_amount: Decimal = Decimal('1.00')
    max_amount: Decimal = Decimal('1000000.00')
    
    @validator('gateway_name')
    def validate_gateway_name(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Gateway name must be at least 3 characters')
        return v
    
    @validator('gateway_type')
    def validate_gateway_type(cls, v):
        if v not in ['razorpay', 'payu', 'phonepay']:
            raise ValueError('Invalid gateway type')
        return v

class PaymentGatewayResponse(BaseModel):
    id: int
    gateway_name: str
    gateway_type: str
    is_active: bool
    is_default: bool
    is_test_mode: bool
    processing_fee_percent: Decimal
    processing_fee_fixed: Decimal
    supported_currencies: List[str]
    supported_payment_methods: List[str]
    min_amount: Decimal
    max_amount: Decimal
    created_at: datetime
    
    class Config:
        orm_mode = True

class PaymentTransactionCreateRequest(BaseModel):
    amount: Decimal
    currency: str = 'INR'
    customer_id: Optional[int] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class PaymentTransactionResponse(BaseModel):
    id: int
    transaction_id: str
    amount: Decimal
    currency: str
    payment_status: str
    payment_method: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    customer_id: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    payment_url: Optional[str] = None
    
    class Config:
        orm_mode = True

class PaymentRefundRequest(BaseModel):
    transaction_id: int
    refund_amount: Optional[Decimal] = None
    refund_reason: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('refund_amount')
    def validate_refund_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Refund amount must be greater than 0')
        return v

# Payment Gateway Management
@router.post("/gateways", response_model=PaymentGatewayResponse)
async def create_payment_gateway(
    gateway_data: PaymentGatewayCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment gateway"""
    try:
        # Check permissions
        if not current_user.has_permission("payment_gateways.create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create gateway
        gateway = PaymentGateway(
            gateway_name=gateway_data.gateway_name,
            gateway_type=PaymentGatewayType(gateway_data.gateway_type),
            api_key=gateway_data.api_key,
            api_secret=gateway_data.api_secret,
            merchant_id=gateway_data.merchant_id,
            webhook_secret=gateway_data.webhook_secret,
            is_test_mode=gateway_data.is_test_mode,
            processing_fee_percent=gateway_data.processing_fee_percent,
            processing_fee_fixed=gateway_data.processing_fee_fixed,
            gst_on_fee=gateway_data.gst_on_fee,
            supported_currencies=gateway_data.supported_currencies or ['INR'],
            supported_payment_methods=gateway_data.supported_payment_methods or ['card', 'upi', 'netbanking'],
            min_amount=gateway_data.min_amount,
            max_amount=gateway_data.max_amount
        )
        
        db.add(gateway)
        db.commit()
        db.refresh(gateway)
        
        return gateway
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gateways", response_model=List[PaymentGatewayResponse])
async def get_payment_gateways(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payment gateways"""
    try:
        gateways = db.query(PaymentGateway).filter(PaymentGateway.is_active == True).all()
        return gateways
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gateways/{gateway_id}", response_model=PaymentGatewayResponse)
async def get_payment_gateway(
    gateway_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment gateway"""
    try:
        gateway = db.query(PaymentGateway).filter(PaymentGateway.id == gateway_id).first()
        if not gateway:
            raise HTTPException(status_code=404, detail="Payment gateway not found")
        
        return gateway
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Payment Transaction Management
@router.post("/transactions", response_model=PaymentTransactionResponse)
async def create_payment_transaction(
    transaction_data: PaymentTransactionCreateRequest,
    gateway_id: int = Query(..., description="Payment gateway ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment transaction"""
    try:
        # Check permissions
        if not current_user.has_permission("payments.create"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get gateway
        gateway = db.query(PaymentGateway).filter(PaymentGateway.id == gateway_id).first()
        if not gateway:
            raise HTTPException(status_code=404, detail="Payment gateway not found")
        
        # Create transaction
        transaction = PaymentTransaction(
            transaction_id=f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            gateway_id=gateway_id,
            customer_id=transaction_data.customer_id,
            customer_email=transaction_data.customer_email,
            customer_phone=transaction_data.customer_phone,
            reference_type=transaction_data.reference_type,
            reference_id=transaction_data.reference_id,
            reference_number=transaction_data.reference_number,
            payment_method=transaction_data.payment_method,
            notes=transaction_data.notes,
            initiated_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Initialize payment gateway service
        if gateway.gateway_type == PaymentGatewayType.RAZORPAY:
            service = RazorpayService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PAYU:
            service = PayUService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PHONEPE:
            service = PhonePeService(gateway)
        else:
            raise HTTPException(status_code=400, detail="Unsupported gateway type")
        
        # Create payment order
        customer_data = {}
        if transaction_data.customer_id:
            customer_data['customer_id'] = transaction_data.customer_id
        if transaction_data.customer_email:
            customer_data['email'] = transaction_data.customer_email
        if transaction_data.customer_phone:
            customer_data['phone'] = transaction_data.customer_phone
        
        if gateway.gateway_type == PaymentGatewayType.RAZORPAY:
            result = service.create_payment_order(
                amount=transaction_data.amount,
                currency=transaction_data.currency,
                order_id=transaction.transaction_id,
                customer_data=customer_data
            )
        elif gateway.gateway_type == PaymentGatewayType.PAYU:
            result = service.create_payment_request(
                amount=transaction_data.amount,
                currency=transaction_data.currency,
                order_id=transaction.transaction_id,
                customer_data=customer_data
            )
        elif gateway.gateway_type == PaymentGatewayType.PHONEPE:
            result = service.create_payment_request(
                amount=transaction_data.amount,
                currency=transaction_data.currency,
                order_id=transaction.transaction_id,
                customer_data=customer_data
            )
        
        if result['success']:
            transaction.gateway_transaction_id = result.get('order_id') or result.get('transaction_id')
            transaction.payment_url = result.get('payment_url')
            transaction.gateway_response = result
            
            db.commit()
            
            return transaction
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Payment creation failed'))
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions", response_model=List[PaymentTransactionResponse])
async def get_payment_transactions(
    status: Optional[str] = Query(None, description="Filter by payment status"),
    gateway_id: Optional[int] = Query(None, description="Filter by gateway ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment transactions"""
    try:
        query = db.query(PaymentTransaction)
        
        if status:
            query = query.filter(PaymentTransaction.payment_status == status)
        if gateway_id:
            query = query.filter(PaymentTransaction.gateway_id == gateway_id)
        
        transactions = query.order_by(PaymentTransaction.created_at.desc()).all()
        return transactions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions/{transaction_id}", response_model=PaymentTransactionResponse)
async def get_payment_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment transaction"""
    try:
        transaction = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        
        return transaction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Payment Refund Management
@router.post("/refunds")
async def create_payment_refund(
    refund_data: PaymentRefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a payment refund"""
    try:
        # Check permissions
        if not current_user.has_permission("payments.refund"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Get transaction
        transaction = db.query(PaymentTransaction).filter(PaymentTransaction.id == refund_data.transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        
        if transaction.payment_status != PaymentStatus.SUCCESS:
            raise HTTPException(status_code=400, detail="Cannot refund unsuccessful payment")
        
        # Get gateway
        gateway = db.query(PaymentGateway).filter(PaymentGateway.id == transaction.gateway_id).first()
        if not gateway:
            raise HTTPException(status_code=404, detail="Payment gateway not found")
        
        # Initialize payment gateway service
        if gateway.gateway_type == PaymentGatewayType.RAZORPAY:
            service = RazorpayService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PAYU:
            service = PayUService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PHONEPE:
            service = PhonePeService(gateway)
        else:
            raise HTTPException(status_code=400, detail="Unsupported gateway type")
        
        # Create refund
        refund_amount = refund_data.refund_amount or transaction.amount
        result = service.refund_payment(
            payment_id=transaction.gateway_transaction_id,
            amount=refund_amount,
            refund_reason=refund_data.refund_reason
        )
        
        if result['success']:
            # Create refund record
            refund = PaymentRefund(
                refund_id=f"refund_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                transaction_id=transaction.id,
                refund_amount=refund_amount,
                refund_reason=refund_data.refund_reason,
                refund_status='processed',
                gateway_response=result,
                processed_at=datetime.utcnow()
            )
            
            db.add(refund)
            
            # Update transaction
            transaction.refund_amount = refund_amount
            if refund_amount >= transaction.amount:
                transaction.payment_status = PaymentStatus.REFUNDED
            else:
                transaction.payment_status = PaymentStatus.PARTIALLY_REFUNDED
            
            db.commit()
            
            return {
                'success': True,
                'refund_id': refund.refund_id,
                'refund_amount': float(refund_amount),
                'refund_status': refund.refund_status
            }
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Refund failed'))
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Payment Gateway Webhooks
@router.post("/webhooks/{gateway_id}")
async def handle_payment_webhook(
    gateway_id: int,
    payload: dict,
    signature: str = Query(..., description="Webhook signature"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle payment gateway webhooks"""
    try:
        # Get gateway
        gateway = db.query(PaymentGateway).filter(PaymentGateway.id == gateway_id).first()
        if not gateway:
            raise HTTPException(status_code=404, detail="Payment gateway not found")
        
        # Initialize payment gateway service
        if gateway.gateway_type == PaymentGatewayType.RAZORPAY:
            service = RazorpayService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PAYU:
            service = PayUService(gateway)
        elif gateway.gateway_type == PaymentGatewayType.PHONEPE:
            service = PhonePeService(gateway)
        else:
            raise HTTPException(status_code=400, detail="Unsupported gateway type")
        
        # Process webhook
        result = service.process_webhook(payload, signature)
        
        if result['success']:
            # Update transaction status
            transaction = db.query(PaymentTransaction).filter(
                PaymentTransaction.gateway_transaction_id == result.get('payment_id')
            ).first()
            
            if transaction:
                transaction.payment_status = PaymentStatus(result.get('status', 'pending'))
                transaction.completed_at = datetime.utcnow()
                transaction.gateway_response = result
                
                db.commit()
            
            return {'success': True, 'message': 'Webhook processed successfully'}
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Webhook processing failed'))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Payment Analytics
@router.get("/analytics")
async def get_payment_analytics(
    start_date: Optional[date] = Query(None, description="Start date for analytics"),
    end_date: Optional[date] = Query(None, description="End date for analytics"),
    gateway_id: Optional[int] = Query(None, description="Filter by gateway ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment analytics"""
    try:
        # Check permissions
        if not current_user.has_permission("payments.analytics"):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build query
        query = db.query(PaymentTransaction)
        
        if start_date:
            query = query.filter(PaymentTransaction.initiated_at >= start_date)
        if end_date:
            query = query.filter(PaymentTransaction.initiated_at <= end_date)
        if gateway_id:
            query = query.filter(PaymentTransaction.gateway_id == gateway_id)
        
        transactions = query.all()
        
        # Calculate analytics
        total_transactions = len(transactions)
        successful_transactions = len([t for t in transactions if t.payment_status == PaymentStatus.SUCCESS])
        failed_transactions = len([t for t in transactions if t.payment_status == PaymentStatus.FAILED])
        
        total_amount = sum([float(t.amount) for t in transactions])
        successful_amount = sum([float(t.amount) for t in transactions if t.payment_status == PaymentStatus.SUCCESS])
        
        success_rate = (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        return {
            'total_transactions': total_transactions,
            'successful_transactions': successful_transactions,
            'failed_transactions': failed_transactions,
            'total_amount': total_amount,
            'successful_amount': successful_amount,
            'success_rate': success_rate,
            'average_transaction_amount': total_amount / total_transactions if total_transactions > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))