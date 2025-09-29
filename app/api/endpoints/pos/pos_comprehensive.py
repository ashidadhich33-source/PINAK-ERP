# backend/app/api/endpoints/pos/pos_comprehensive.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.pos_service import pos_service

router = APIRouter()

# Pydantic schemas for POS
class POSSessionCreateRequest(BaseModel):
    session_number: str
    session_date: date
    store_id: int
    opening_cash: Decimal = 0
    notes: Optional[str] = None
    
    @validator('session_number')
    def validate_session_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Session number must be at least 3 characters')
        return v

class POSSessionCloseRequest(BaseModel):
    closing_cash: Decimal
    notes: Optional[str] = None

class POSTransactionCreateRequest(BaseModel):
    transaction_number: str
    customer_id: Optional[int] = None
    transaction_type: str = 'sale'
    subtotal: Decimal
    discount_amount: Decimal = 0
    tax_amount: Decimal = 0
    total_amount: Decimal
    payment_method: str
    payment_reference: Optional[str] = None
    cgst_amount: Decimal = 0
    sgst_amount: Decimal = 0
    igst_amount: Decimal = 0
    total_gst_amount: Decimal = 0
    notes: Optional[str] = None

class POSTransactionItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    discount_amount: Decimal = 0
    tax_rate: Decimal = 0
    tax_amount: Decimal = 0
    net_amount: Decimal
    serial_numbers: Optional[str] = None  # JSON array
    batch_numbers: Optional[str] = None  # JSON array
    expiry_dates: Optional[str] = None  # JSON array

class POSPaymentCreateRequest(BaseModel):
    payment_method: str
    payment_amount: Decimal
    payment_reference: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    card_holder_name: Optional[str] = None
    authorization_code: Optional[str] = None
    upi_id: Optional[str] = None
    wallet_type: Optional[str] = None
    wallet_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_id_bank: Optional[str] = None

class StoreCreateRequest(BaseModel):
    store_code: str
    store_name: str
    store_address: Optional[str] = None
    store_city: Optional[str] = None
    store_state: Optional[str] = None
    store_pincode: Optional[str] = None
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    currency: str = 'INR'
    timezone: str = 'Asia/Kolkata'
    tax_number: Optional[str] = None
    gst_number: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None

class StoreStaffCreateRequest(BaseModel):
    store_id: int
    user_id: int
    role: str
    is_active: bool = True

class POSReceiptCreateRequest(BaseModel):
    receipt_type: str = 'sale'
    receipt_template: str = 'standard'
    receipt_header: Optional[str] = None
    receipt_footer: Optional[str] = None
    receipt_content: Optional[str] = None
    digital_receipt_url: Optional[str] = None
    qr_code: Optional[str] = None

# Response schemas
class POSSessionResponse(BaseModel):
    id: int
    session_number: str
    session_date: date
    store_id: int
    cashier_id: int
    opening_cash: Decimal
    closing_cash: Optional[Decimal]
    expected_cash: Optional[Decimal]
    cash_difference: Optional[Decimal]
    total_sales: Decimal
    total_transactions: int
    total_returns: Decimal
    total_exchanges: Decimal
    status: str
    opened_at: datetime
    closed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class POSTransactionResponse(BaseModel):
    id: int
    transaction_number: str
    session_id: int
    customer_id: Optional[int]
    transaction_type: str
    transaction_date: datetime
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: str
    payment_reference: Optional[str]
    payment_status: str
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    status: str
    is_void: bool
    void_reason: Optional[str]
    void_date: Optional[datetime]
    original_transaction_id: Optional[int]
    exchange_id: Optional[int]
    return_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StoreResponse(BaseModel):
    id: int
    store_code: str
    store_name: str
    store_address: Optional[str]
    store_city: Optional[str]
    store_state: Optional[str]
    store_pincode: Optional[str]
    store_phone: Optional[str]
    store_email: Optional[str]
    currency: str
    timezone: str
    tax_number: Optional[str]
    gst_number: Optional[str]
    is_active: bool
    opening_time: Optional[str]
    closing_time: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# POS Session Endpoints
@router.post("/pos-sessions", response_model=POSSessionResponse)
async def create_pos_session(
    session_data: POSSessionCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Create POS session"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        pos_session = pos_service.create_pos_session(
            db=db,
            company_id=company_id,
            session_number=session_data.session_number,
            session_date=session_data.session_date,
            store_id=session_data.store_id,
            opening_cash=session_data.opening_cash,
            notes=session_data.notes,
            cashier_id=current_user.id
        )
        
        return pos_session
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create POS session: {str(e)}"
        )

@router.get("/pos-sessions", response_model=List[POSSessionResponse])
async def get_pos_sessions(
    company_id: int = Query(...),
    store_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS sessions with filters"""
    
    try:
        pos_sessions = pos_service.get_pos_sessions(
            db=db,
            company_id=company_id,
            store_id=store_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return pos_sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS sessions: {str(e)}"
        )

@router.get("/pos-sessions/{session_id}", response_model=POSSessionResponse)
async def get_pos_session(
    session_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get specific POS session"""
    
    try:
        pos_session = pos_service.get_pos_session_by_id(
            db=db,
            session_id=session_id,
            company_id=company_id
        )
        
        if not pos_session:
            raise HTTPException(
                status_code=404,
                detail="POS session not found"
            )
        
        return pos_session
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS session: {str(e)}"
        )

@router.post("/pos-sessions/{session_id}/close")
async def close_pos_session(
    session_id: int,
    close_data: POSSessionCloseRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Close POS session"""
    
    try:
        result = pos_service.close_pos_session(
            db=db,
            session_id=session_id,
            company_id=company_id,
            closing_cash=close_data.closing_cash,
            notes=close_data.notes,
            user_id=current_user.id
        )
        
        return {
            "message": "POS session closed successfully",
            "session_id": session_id,
            "cash_difference": result.get("cash_difference"),
            "total_sales": result.get("total_sales")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close POS session: {str(e)}"
        )

# POS Transaction Endpoints
@router.post("/pos-transactions", response_model=POSTransactionResponse)
async def create_pos_transaction(
    transaction_data: POSTransactionCreateRequest,
    session_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Create POS transaction"""
    
    try:
        pos_transaction = pos_service.create_pos_transaction(
            db=db,
            company_id=company_id,
            session_id=session_id,
            transaction_number=transaction_data.transaction_number,
            customer_id=transaction_data.customer_id,
            transaction_type=transaction_data.transaction_type,
            subtotal=transaction_data.subtotal,
            discount_amount=transaction_data.discount_amount,
            tax_amount=transaction_data.tax_amount,
            total_amount=transaction_data.total_amount,
            payment_method=transaction_data.payment_method,
            payment_reference=transaction_data.payment_reference,
            cgst_amount=transaction_data.cgst_amount,
            sgst_amount=transaction_data.sgst_amount,
            igst_amount=transaction_data.igst_amount,
            total_gst_amount=transaction_data.total_gst_amount,
            notes=transaction_data.notes,
            user_id=current_user.id
        )
        
        return pos_transaction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create POS transaction: {str(e)}"
        )

@router.get("/pos-transactions", response_model=List[POSTransactionResponse])
async def get_pos_transactions(
    company_id: int = Query(...),
    session_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS transactions with filters"""
    
    try:
        pos_transactions = pos_service.get_pos_transactions(
            db=db,
            company_id=company_id,
            session_id=session_id,
            customer_id=customer_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return pos_transactions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS transactions: {str(e)}"
        )

@router.get("/pos-transactions/{transaction_id}", response_model=POSTransactionResponse)
async def get_pos_transaction(
    transaction_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get specific POS transaction"""
    
    try:
        pos_transaction = pos_service.get_pos_transaction_by_id(
            db=db,
            transaction_id=transaction_id,
            company_id=company_id
        )
        
        if not pos_transaction:
            raise HTTPException(
                status_code=404,
                detail="POS transaction not found"
            )
        
        return pos_transaction
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS transaction: {str(e)}"
        )

@router.post("/pos-transactions/{transaction_id}/items")
async def add_items_to_pos_transaction(
    transaction_id: int,
    items: List[POSTransactionItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Add items to POS transaction"""
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        transaction_items = pos_service.add_items_to_pos_transaction(
            db=db,
            company_id=company_id,
            transaction_id=transaction_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to POS transaction successfully",
            "items_count": len(transaction_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to POS transaction: {str(e)}"
        )

@router.post("/pos-transactions/{transaction_id}/payments")
async def add_payment_to_pos_transaction(
    transaction_id: int,
    payment_data: POSPaymentCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Add payment to POS transaction"""
    
    try:
        payment = pos_service.add_payment_to_pos_transaction(
            db=db,
            company_id=company_id,
            transaction_id=transaction_id,
            payment_data=payment_data.dict(),
            user_id=current_user.id
        )
        
        return payment
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add payment to POS transaction: {str(e)}"
        )

@router.post("/pos-transactions/{transaction_id}/void")
async def void_pos_transaction(
    transaction_id: int,
    void_reason: str,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Void POS transaction"""
    
    try:
        result = pos_service.void_pos_transaction(
            db=db,
            transaction_id=transaction_id,
            company_id=company_id,
            void_reason=void_reason,
            user_id=current_user.id
        )
        
        return {
            "message": "POS transaction voided successfully",
            "transaction_id": transaction_id,
            "void_reason": void_reason
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to void POS transaction: {str(e)}"
        )

# Store Management Endpoints
@router.post("/stores", response_model=StoreResponse)
async def create_store(
    store_data: StoreCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Create store"""
    
    try:
        store = pos_service.create_store(
            db=db,
            company_id=company_id,
            store_code=store_data.store_code,
            store_name=store_data.store_name,
            store_address=store_data.store_address,
            store_city=store_data.store_city,
            store_state=store_data.store_state,
            store_pincode=store_data.store_pincode,
            store_phone=store_data.store_phone,
            store_email=store_data.store_email,
            currency=store_data.currency,
            timezone=store_data.timezone,
            tax_number=store_data.tax_number,
            gst_number=store_data.gst_number,
            opening_time=store_data.opening_time,
            closing_time=store_data.closing_time,
            user_id=current_user.id
        )
        
        return store
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create store: {str(e)}"
        )

@router.get("/stores", response_model=List[StoreResponse])
async def get_stores(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get stores"""
    
    try:
        stores = pos_service.get_stores(
            db=db,
            company_id=company_id,
            is_active=is_active
        )
        
        return stores
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stores: {str(e)}"
        )

# POS Receipt Endpoints
@router.post("/pos-transactions/{transaction_id}/receipt")
async def create_pos_receipt(
    transaction_id: int,
    receipt_data: POSReceiptCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Create POS receipt"""
    
    try:
        receipt = pos_service.create_pos_receipt(
            db=db,
            company_id=company_id,
            transaction_id=transaction_id,
            receipt_data=receipt_data.dict(),
            user_id=current_user.id
        )
        
        return receipt
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create POS receipt: {str(e)}"
        )

@router.post("/pos-transactions/{transaction_id}/print-receipt")
async def print_pos_receipt(
    transaction_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Print POS receipt"""
    
    try:
        result = pos_service.print_pos_receipt(
            db=db,
            transaction_id=transaction_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "POS receipt printed successfully",
            "transaction_id": transaction_id,
            "receipt_number": result.get("receipt_number"),
            "print_count": result.get("print_count")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to print POS receipt: {str(e)}"
        )

# POS Analytics Endpoints
@router.get("/pos-analytics/dashboard")
async def get_pos_dashboard(
    company_id: int = Query(...),
    store_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS dashboard analytics"""
    
    try:
        dashboard = pos_service.get_pos_dashboard(
            db=db,
            company_id=company_id,
            store_id=store_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS dashboard: {str(e)}"
        )

@router.get("/pos-analytics/sales-report")
async def get_pos_sales_report(
    company_id: int = Query(...),
    store_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS sales report"""
    
    try:
        report = pos_service.get_pos_sales_report(
            db=db,
            company_id=company_id,
            store_id=store_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get POS sales report: {str(e)}"
        )

# POS Integration Endpoints
@router.post("/pos-transactions/{transaction_id}/link-exchange")
async def link_exchange_to_pos_transaction(
    transaction_id: int,
    exchange_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Link exchange to POS transaction"""
    
    try:
        result = pos_service.link_exchange_to_pos_transaction(
            db=db,
            transaction_id=transaction_id,
            exchange_id=exchange_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Exchange linked to POS transaction successfully",
            "transaction_id": transaction_id,
            "exchange_id": exchange_id,
            "difference_amount": result.get("difference_amount")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to link exchange to POS transaction: {str(e)}"
        )

@router.post("/pos-transactions/{transaction_id}/link-return")
async def link_return_to_pos_transaction(
    transaction_id: int,
    return_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.manage")),
    db: Session = Depends(get_db)
):
    """Link return to POS transaction"""
    
    try:
        result = pos_service.link_return_to_pos_transaction(
            db=db,
            transaction_id=transaction_id,
            return_id=return_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Return linked to POS transaction successfully",
            "transaction_id": transaction_id,
            "return_id": return_id,
            "refund_amount": result.get("refund_amount")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to link return to POS transaction: {str(e)}"
        )