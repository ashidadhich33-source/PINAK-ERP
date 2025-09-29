# backend/app/api/endpoints/purchase/purchase_accounting_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.purchase.purchase_accounting_integration import (
    PurchaseJournalEntry, PurchasePayment, PurchaseAnalytic, PurchaseWorkflow,
    PurchaseDocument, PurchaseAuditTrail, JournalEntryStatus, PaymentStatus
)

router = APIRouter()

# --- Schemas ---
class PurchaseJournalEntryCreate(BaseModel):
    purchase_invoice_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    entry_type: str = Field(..., min_length=3, max_length=50)
    total_amount: Decimal = Field(..., gt=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    net_amount: Decimal = Field(..., gt=0)
    debit_account_id: Optional[int] = None
    credit_account_id: Optional[int] = None
    tax_account_id: Optional[int] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseJournalEntryResponse(BaseModel):
    id: int
    purchase_invoice_id: Optional[int]
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    journal_entry_id: int
    entry_type: str
    entry_status: JournalEntryStatus
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    net_amount: Decimal
    debit_account_id: Optional[int]
    credit_account_id: Optional[int]
    tax_account_id: Optional[int]
    reference_number: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchasePaymentCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    payment_id: Optional[int] = None
    bank_account_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    payment_amount: Decimal = Field(..., gt=0)
    payment_date: date
    payment_reference: Optional[str] = None
    payment_notes: Optional[str] = None
    due_date: Optional[date] = None
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    metadata: Optional[Dict[str, Any]] = None

class PurchasePaymentResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    payment_id: Optional[int]
    bank_account_id: Optional[int]
    payment_method_id: Optional[int]
    payment_amount: Decimal
    payment_date: date
    payment_status: PaymentStatus
    payment_reference: Optional[str]
    payment_notes: Optional[str]
    due_date: Optional[date]
    discount_days: Optional[int]
    discount_percentage: Optional[Decimal]
    discount_amount: Decimal
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseAnalyticCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    analytic_account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    distribution_method: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseAnalyticResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    analytic_account_id: int
    amount: Decimal
    percentage: Optional[Decimal]
    distribution_method: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Purchase Journal Entries
@router.post("/purchase-journal-entries", response_model=PurchaseJournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_journal_entry(
    entry_data: PurchaseJournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_accounting"))
):
    """Create new purchase journal entry"""
    entry = PurchaseJournalEntry(**entry_data.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/purchase-journal-entries", response_model=List[PurchaseJournalEntryResponse])
async def get_purchase_journal_entries(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    entry_type: Optional[str] = Query(None),
    entry_status: Optional[JournalEntryStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get all purchase journal entries"""
    query = db.query(PurchaseJournalEntry)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseJournalEntry.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseJournalEntry.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseJournalEntry.purchase_return_id == purchase_return_id)
    if entry_type:
        query = query.filter(PurchaseJournalEntry.entry_type == entry_type)
    if entry_status:
        query = query.filter(PurchaseJournalEntry.entry_status == entry_status)
    
    return query.order_by(PurchaseJournalEntry.created_at.desc()).all()

@router.get("/purchase-journal-entries/{entry_id}", response_model=PurchaseJournalEntryResponse)
async def get_purchase_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get specific purchase journal entry"""
    entry = db.query(PurchaseJournalEntry).filter(PurchaseJournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase journal entry not found")
    return entry

# Purchase Payments
@router.post("/purchase-payments", response_model=PurchasePaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_payment(
    payment_data: PurchasePaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_accounting"))
):
    """Create new purchase payment"""
    payment = PurchasePayment(**payment_data.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/purchase-payments", response_model=List[PurchasePaymentResponse])
async def get_purchase_payments(
    purchase_invoice_id: Optional[int] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    payment_date_from: Optional[date] = Query(None),
    payment_date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get all purchase payments"""
    query = db.query(PurchasePayment)
    
    if purchase_invoice_id:
        query = query.filter(PurchasePayment.purchase_invoice_id == purchase_invoice_id)
    if payment_status:
        query = query.filter(PurchasePayment.payment_status == payment_status)
    if payment_date_from:
        query = query.filter(PurchasePayment.payment_date >= payment_date_from)
    if payment_date_to:
        query = query.filter(PurchasePayment.payment_date <= payment_date_to)
    
    return query.order_by(PurchasePayment.payment_date.desc()).all()

@router.get("/purchase-payments/{payment_id}", response_model=PurchasePaymentResponse)
async def get_purchase_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get specific purchase payment"""
    payment = db.query(PurchasePayment).filter(PurchasePayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase payment not found")
    return payment

# Purchase Analytics
@router.post("/purchase-analytics", response_model=PurchaseAnalyticResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_analytic(
    analytic_data: PurchaseAnalyticCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_accounting"))
):
    """Create new purchase analytic"""
    analytic = PurchaseAnalytic(**analytic_data.dict())
    db.add(analytic)
    db.commit()
    db.refresh(analytic)
    return analytic

@router.get("/purchase-analytics", response_model=List[PurchaseAnalyticResponse])
async def get_purchase_analytics(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    analytic_account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get all purchase analytics"""
    query = db.query(PurchaseAnalytic)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseAnalytic.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseAnalytic.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseAnalytic.purchase_return_id == purchase_return_id)
    if analytic_account_id:
        query = query.filter(PurchaseAnalytic.analytic_account_id == analytic_account_id)
    
    return query.order_by(PurchaseAnalytic.created_at.desc()).all()

# Auto-create Journal Entries
@router.post("/auto-create-journal-entries/{purchase_invoice_id}")
async def auto_create_journal_entry(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_accounting"))
):
    """Auto-create journal entry for purchase invoice"""
    # This would contain the actual logic to create journal entries
    # For now, returning a placeholder response
    return {
        "message": "Journal entry creation initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }

# Purchase Accounting Statistics
@router.get("/purchase-accounting-statistics")
async def get_purchase_accounting_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_accounting"))
):
    """Get purchase accounting statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_purchases": 75000.00,
        "total_payments": 60000.00,
        "outstanding_amount": 15000.00,
        "journal_entries_created": 35,
        "pending_journal_entries": 3,
        "payment_completion_rate": 80.0
    }