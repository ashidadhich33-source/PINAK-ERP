# backend/app/api/endpoints/sales/sales_accounting_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.sales.sales_accounting_integration import (
    SaleJournalEntry, SalePayment, SaleAnalytic, SaleWorkflow,
    SaleDocument, SaleAuditTrail, JournalEntryStatus, PaymentStatus
)

router = APIRouter()

# --- Schemas ---
class SaleJournalEntryCreate(BaseModel):
    sale_invoice_id: Optional[int] = None
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleJournalEntryResponse(BaseModel):
    id: int
    sale_invoice_id: Optional[int]
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

class SalePaymentCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
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

class SalePaymentResponse(BaseModel):
    id: int
    sale_invoice_id: int
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

class SaleAnalyticCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
    analytic_account_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    distribution_method: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SaleAnalyticResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

# Sale Journal Entries
@router.post("/sale-journal-entries", response_model=SaleJournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_journal_entry(
    entry_data: SaleJournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_accounting"))
):
    """Create new sale journal entry"""
    entry = SaleJournalEntry(**entry_data.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/sale-journal-entries", response_model=List[SaleJournalEntryResponse])
async def get_sale_journal_entries(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    entry_type: Optional[str] = Query(None),
    entry_status: Optional[JournalEntryStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get all sale journal entries"""
    query = db.query(SaleJournalEntry)
    
    if sale_invoice_id:
        query = query.filter(SaleJournalEntry.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleJournalEntry.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleJournalEntry.sale_return_id == sale_return_id)
    if entry_type:
        query = query.filter(SaleJournalEntry.entry_type == entry_type)
    if entry_status:
        query = query.filter(SaleJournalEntry.entry_status == entry_status)
    
    return query.order_by(SaleJournalEntry.created_at.desc()).all()

@router.get("/sale-journal-entries/{entry_id}", response_model=SaleJournalEntryResponse)
async def get_sale_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get specific sale journal entry"""
    entry = db.query(SaleJournalEntry).filter(SaleJournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale journal entry not found")
    return entry

# Sale Payments
@router.post("/sale-payments", response_model=SalePaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_payment(
    payment_data: SalePaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_accounting"))
):
    """Create new sale payment"""
    payment = SalePayment(**payment_data.dict())
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.get("/sale-payments", response_model=List[SalePaymentResponse])
async def get_sale_payments(
    sale_invoice_id: Optional[int] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    payment_date_from: Optional[date] = Query(None),
    payment_date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get all sale payments"""
    query = db.query(SalePayment)
    
    if sale_invoice_id:
        query = query.filter(SalePayment.sale_invoice_id == sale_invoice_id)
    if payment_status:
        query = query.filter(SalePayment.payment_status == payment_status)
    if payment_date_from:
        query = query.filter(SalePayment.payment_date >= payment_date_from)
    if payment_date_to:
        query = query.filter(SalePayment.payment_date <= payment_date_to)
    
    return query.order_by(SalePayment.payment_date.desc()).all()

@router.get("/sale-payments/{payment_id}", response_model=SalePaymentResponse)
async def get_sale_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get specific sale payment"""
    payment = db.query(SalePayment).filter(SalePayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale payment not found")
    return payment

# Sale Analytics
@router.post("/sale-analytics", response_model=SaleAnalyticResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_analytic(
    analytic_data: SaleAnalyticCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_accounting"))
):
    """Create new sale analytic"""
    analytic = SaleAnalytic(**analytic_data.dict())
    db.add(analytic)
    db.commit()
    db.refresh(analytic)
    return analytic

@router.get("/sale-analytics", response_model=List[SaleAnalyticResponse])
async def get_sale_analytics(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    analytic_account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get all sale analytics"""
    query = db.query(SaleAnalytic)
    
    if sale_invoice_id:
        query = query.filter(SaleAnalytic.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleAnalytic.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleAnalytic.sale_return_id == sale_return_id)
    if analytic_account_id:
        query = query.filter(SaleAnalytic.analytic_account_id == analytic_account_id)
    
    return query.order_by(SaleAnalytic.created_at.desc()).all()

# Auto-create Journal Entries
@router.post("/auto-create-journal-entries/{sale_invoice_id}")
async def auto_create_journal_entry(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_accounting"))
):
    """Auto-create journal entry for sale invoice"""
    # This would contain the actual logic to create journal entries
    # For now, returning a placeholder response
    return {
        "message": "Journal entry creation initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }

# Sales Accounting Statistics
@router.get("/sales-accounting-statistics")
async def get_sales_accounting_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_accounting"))
):
    """Get sales accounting statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_sales": 100000.00,
        "total_payments": 85000.00,
        "outstanding_amount": 15000.00,
        "journal_entries_created": 45,
        "pending_journal_entries": 5,
        "payment_collection_rate": 85.0
    }