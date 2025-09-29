# backend/app/api/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date

from ...database import get_db
from ...models.payment import Payment, PaymentMethod
from ...models.enhanced_sales import SalesInvoice
from ...models.enhanced_purchase import PurchaseInvoice
from ...models.customer import Customer, Supplier
from ...models.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    display_name: str
    method_type: str
    is_active: bool
    requires_reference: bool
    charge_percent: Decimal
    charge_amount: Decimal

    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    payment_type: str  # received, paid
    amount: Decimal
    reference_type: Optional[str] = None  # sales_invoice, purchase_invoice
    reference_id: Optional[int] = None
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    payment_method_id: int
    transaction_reference: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    cheque_date: Optional[date] = None
    remarks: Optional[str] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than zero')
        return v

    @validator('payment_type')
    def validate_payment_type(cls, v):
        if v not in ['received', 'paid']:
            raise ValueError('Payment type must be either "received" or "paid"')
        return v

class PaymentResponse(BaseModel):
    id: int
    payment_number: str
    payment_date: datetime
    payment_type: str
    amount: Decimal
    reference_type: Optional[str]
    reference_id: Optional[int]
    reference_number: Optional[str]
    customer_id: Optional[int]
    supplier_id: Optional[int]
    party_name: str
    payment_method_id: int
    payment_method_name: str
    transaction_reference: Optional[str]
    bank_name: Optional[str]
    branch_name: Optional[str]
    cheque_date: Optional[datetime]
    status: str
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Helper functions
def generate_payment_number(db: Session, payment_type: str) -> str:
    """Generate unique payment number"""
    today = datetime.now()
    prefix = f"{'PR' if payment_type == 'received' else 'PP'}{today.strftime('%Y%m%d')}"
    
    last_payment = db.query(Payment).filter(
        Payment.payment_number.like(f"{prefix}%")
    ).order_by(desc(Payment.payment_number)).first()
    
    if last_payment:
        try:
            last_seq = int(last_payment.payment_number[-4:])
            next_seq = last_seq + 1
        except:
            next_seq = 1
    else:
        next_seq = 1
    
    return f"{prefix}{next_seq:04d}"

# Payment Method endpoints
@router.get("/methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active payment methods"""
    
    methods = db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()
    return [PaymentMethodResponse.from_orm(method) for method in methods]

# Payment endpoints
@router.get("", response_model=List[PaymentResponse])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    payment_type: Optional[str] = Query(None),
    payment_method_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    supplier_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payments with filtering"""
    
    query = db.query(Payment)
    
    # Apply filters
    if search:
        search_filter = or_(
            Payment.payment_number.ilike(f"%{search}%"),
            Payment.party_name.ilike(f"%{search}%"),
            Payment.transaction_reference.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    if payment_method_id:
        query = query.filter(Payment.payment_method_id == payment_method_id)
    
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    
    if supplier_id:
        query = query.filter(Payment.supplier_id == supplier_id)
    
    if date_from:
        query = query.filter(Payment.payment_date >= datetime.combine(date_from, datetime.min.time()))
    
    if date_to:
        query = query.filter(Payment.payment_date <= datetime.combine(date_to, datetime.max.time()))
    
    payments = query.order_by(desc(Payment.payment_date)).offset(skip).limit(limit).all()
    
    return [PaymentResponse.from_orm(payment) for payment in payments]

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment by ID"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse.from_orm(payment)

@router.post("", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new payment"""
    
    # Validate payment method
    payment_method = db.query(PaymentMethod).filter(PaymentMethod.id == payment_data.payment_method_id).first()
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method not found"
        )
    
    # Validate party (customer or supplier)
    party_name = ""
    if payment_data.customer_id:
        customer = db.query(Customer).filter(Customer.id == payment_data.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer not found"
            )
        party_name = customer.name
        
        if payment_data.payment_type != "received":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer payments must be of type 'received'"
            )
    
    elif payment_data.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == payment_data.supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier not found"
            )
        party_name = supplier.name
        
        if payment_data.payment_type != "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier payments must be of type 'paid'"
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either customer_id or supplier_id must be provided"
        )
    
    # Validate reference if provided
    reference_number = None
    if payment_data.reference_id and payment_data.reference_type:
        if payment_data.reference_type == "sales_invoice":
            invoice = db.query(SalesInvoice).filter(SalesInvoice.id == payment_data.reference_id).first()
            if not invoice:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sales invoice not found"
                )
            reference_number = invoice.invoice_number
            
            # Validate amount doesn't exceed outstanding balance
            if payment_data.amount > invoice.balance_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment amount cannot exceed outstanding balance of {invoice.balance_amount}"
                )
        
        elif payment_data.reference_type == "purchase_invoice":
            invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == payment_data.reference_id).first()
            if not invoice:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Purchase invoice not found"
                )
            reference_number = invoice.invoice_number
            
            # Validate amount doesn't exceed outstanding balance
            if payment_data.amount > invoice.balance_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment amount cannot exceed outstanding balance of {invoice.balance_amount}"
                )
    
    # Validate required fields for certain payment methods
    if payment_method.requires_reference and not payment_data.transaction_reference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction reference is required for {payment_method.display_name}"
        )
    
    # Generate payment number
    payment_number = generate_payment_number(db, payment_data.payment_type)
    
    # Create payment
    db_payment = Payment(
        payment_number=payment_number,
        payment_type=payment_data.payment_type,
        amount=payment_data.amount,
        reference_type=payment_data.reference_type,
        reference_id=payment_data.reference_id,
        reference_number=reference_number,
        customer_id=payment_data.customer_id,
        supplier_id=payment_data.supplier_id,
        party_name=party_name,
        payment_method_id=payment_data.payment_method_id,
        payment_method_name=payment_method.name,
        transaction_reference=payment_data.transaction_reference,
        bank_name=payment_data.bank_name,
        branch_name=payment_data.branch_name,
        cheque_date=datetime.combine(payment_data.cheque_date, datetime.min.time()) if payment_data.cheque_date else None,
        remarks=payment_data.remarks,
        status="completed",
        created_by=current_user.id
    )
    
    db.add(db_payment)
    db.flush()  # Get payment ID
    
    # Update invoice payment status if reference provided
    if payment_data.reference_id and payment_data.reference_type:
        if payment_data.reference_type == "sales_invoice":
            invoice = db.query(SalesInvoice).filter(SalesInvoice.id == payment_data.reference_id).first()
            invoice.paid_amount += payment_data.amount
            invoice.balance_amount = invoice.total_amount - invoice.paid_amount
            
            # Update payment status
            if invoice.balance_amount <= 0:
                invoice.payment_status = "paid"
            elif invoice.paid_amount > 0:
                invoice.payment_status = "partial"
        
        elif payment_data.reference_type == "purchase_invoice":
            invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == payment_data.reference_id).first()
            invoice.paid_amount += payment_data.amount
            invoice.balance_amount = invoice.total_amount - invoice.paid_amount
            
            # Update status
            if invoice.balance_amount <= 0:
                invoice.status = "paid"
            elif invoice.paid_amount > 0:
                invoice.status = "partial"
    
    # Update customer/supplier balance
    if payment_data.customer_id:
        customer = db.query(Customer).filter(Customer.id == payment_data.customer_id).first()
        customer.current_balance -= payment_data.amount  # Received payment reduces customer balance
    
    elif payment_data.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == payment_data.supplier_id).first()
        supplier.current_balance -= payment_data.amount  # Paid amount reduces supplier balance
    
    db.commit()
    db.refresh(db_payment)
    
    return PaymentResponse.from_orm(db_payment)

@router.put("/{payment_id}/status")
async def update_payment_status(
    payment_id: int,
    new_status: str = Query(..., regex="^(completed|pending|bounced|cancelled)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update payment status"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    old_status = payment.status
    payment.status = new_status
    payment.updated_by = current_user.id
    
    # Handle status change effects
    if old_status == "completed" and new_status in ["bounced", "cancelled"]:
        # Reverse the payment effects
        if payment.reference_id and payment.reference_type:
            if payment.reference_type == "sales_invoice":
                invoice = db.query(SalesInvoice).filter(SalesInvoice.id == payment.reference_id).first()
                if invoice:
                    invoice.paid_amount -= payment.amount
                    invoice.balance_amount = invoice.total_amount - invoice.paid_amount
                    
                    # Update payment status
                    if invoice.paid_amount <= 0:
                        invoice.payment_status = "pending"
                    elif invoice.balance_amount > 0:
                        invoice.payment_status = "partial"
            
            elif payment.reference_type == "purchase_invoice":
                invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == payment.reference_id).first()
                if invoice:
                    invoice.paid_amount -= payment.amount
                    invoice.balance_amount = invoice.total_amount - invoice.paid_amount
                    
                    # Update status
                    if invoice.paid_amount <= 0:
                        invoice.status = "pending"
                    elif invoice.balance_amount > 0:
                        invoice.status = "partial"
        
        # Reverse customer/supplier balance update
        if payment.customer_id:
            customer = db.query(Customer).filter(Customer.id == payment.customer_id).first()
            if customer:
                customer.current_balance += payment.amount
        
        elif payment.supplier_id:
            supplier = db.query(Supplier).filter(Supplier.id == payment.supplier_id).first()
            if supplier:
                supplier.current_balance += payment.amount
    
    db.commit()
    
    return {"message": f"Payment status updated to {new_status}"}

# Analytics endpoints
@router.get("/analytics/daily-collections")
async def get_daily_collections(
    date_from: date = Query(...),
    date_to: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily payment collections"""
    
    from sqlalchemy import func
    
    daily_collections = db.query(
        func.date(Payment.payment_date).label('payment_date'),
        Payment.payment_type,
        Payment.payment_method_name,
        func.count(Payment.id).label('transaction_count'),
        func.sum(Payment.amount).label('total_amount')
    ).filter(
        and_(
            Payment.payment_date >= datetime.combine(date_from, datetime.min.time()),
            Payment.payment_date <= datetime.combine(date_to, datetime.max.time()),
            Payment.status == 'completed'
        )
    ).group_by(
        func.date(Payment.payment_date),
        Payment.payment_type,
        Payment.payment_method_name
    ).all()
    
    return {
        "period": {"from": date_from, "to": date_to},
        "collections": [
            {
                "date": str(row.payment_date),
                "payment_type": row.payment_type,
                "payment_method": row.payment_method_name,
                "transaction_count": row.transaction_count,
                "total_amount": float(row.total_amount or 0)
            }
            for row in daily_collections
        ]
    }

@router.get("/analytics/payment-methods")
async def get_payment_method_analytics(
    period_days: int = Query(30, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment method wise analytics"""
    
    from datetime import timedelta
    from sqlalchemy import func
    
    start_date = datetime.now() - timedelta(days=period_days)
    
    method_analytics = db.query(
        Payment.payment_method_name,
        Payment.payment_type,
        func.count(Payment.id).label('transaction_count'),
        func.sum(Payment.amount).label('total_amount'),
        func.avg(Payment.amount).label('average_amount')
    ).filter(
        and_(
            Payment.payment_date >= start_date,
            Payment.status == 'completed'
        )
    ).group_by(
        Payment.payment_method_name,
        Payment.payment_type
    ).all()
    
    return {
        "period_days": period_days,
        "method_analytics": [
            {
                "payment_method": row.payment_method_name,
                "payment_type": row.payment_type,
                "transaction_count": row.transaction_count,
                "total_amount": float(row.total_amount or 0),
                "average_amount": float(row.average_amount or 0)
            }
            for row in method_analytics
        ]
    }

@router.get("/analytics/outstanding-summary")
async def get_outstanding_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get outstanding payments summary"""
    
    from sqlalchemy import func
    
    # Customer outstanding (Receivables)
    customer_outstanding = db.query(
        func.sum(SalesInvoice.balance_amount).label('total_receivables'),
        func.count(SalesInvoice.id).label('pending_invoices')
    ).filter(
        and_(
            SalesInvoice.balance_amount > 0,
            SalesInvoice.status != 'cancelled'
        )
    ).first()
    
    # Supplier outstanding (Payables)
    supplier_outstanding = db.query(
        func.sum(PurchaseInvoice.balance_amount).label('total_payables'),
        func.count(PurchaseInvoice.id).label('pending_invoices')
    ).filter(
        and_(
            PurchaseInvoice.balance_amount > 0,
            PurchaseInvoice.status != 'cancelled'
        )
    ).first()
    
    # Recent payments summary
    recent_payments = db.query(
        Payment.payment_type,
        func.sum(Payment.amount).label('total_amount')
    ).filter(
        and_(
            Payment.payment_date >= datetime.now() - timedelta(days=30),
            Payment.status == 'completed'
        )
    ).group_by(Payment.payment_type).all()
    
    recent_received = sum(float(p.total_amount) for p in recent_payments if p.payment_type == 'received')
    recent_paid = sum(float(p.total_amount) for p in recent_payments if p.payment_type == 'paid')
    
    return {
        "receivables": {
            "total_amount": float(customer_outstanding.total_receivables or 0),
            "pending_invoices": customer_outstanding.pending_invoices or 0
        },
        "payables": {
            "total_amount": float(supplier_outstanding.total_payables or 0),
            "pending_invoices": supplier_outstanding.pending_invoices or 0
        },
        "recent_30_days": {
            "received": recent_received,
            "paid": recent_paid,
            "net_flow": recent_received - recent_paid
        }
    }