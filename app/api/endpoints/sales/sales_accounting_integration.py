# backend/app/api/endpoints/sales_accounting_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.sales.sales_accounting_integration import SaleJournalEntry, SalePayment, SaleAnalytic
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class SaleJournalEntryResponse(BaseModel):
    id: int
    sale_invoice_id: int
    journal_entry_id: int
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/sale-journal-entries", response_model=List[SaleJournalEntryResponse])
async def get_sale_journal_entries(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale journal entries for a company"""
    
    entries = db.query(SaleJournalEntry).filter(
        SaleJournalEntry.company_id == company_id
    ).all()
    
    return entries

@router.get("/sale-payments", response_model=List[dict])
async def get_sale_payments(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale payments for a company"""
    
    payments = db.query(SalePayment).filter(
        SalePayment.company_id == company_id
    ).all()
    
    return [
        {
            "id": payment.id,
            "sale_invoice_id": payment.sale_invoice_id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "payment_method": payment.payment_method
        }
        for payment in payments
    ]

@router.get("/sale-analytics", response_model=List[dict])
async def get_sale_analytics(
    company_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale analytics for a company"""
    
    query = db.query(SaleAnalytic).filter(
        SaleAnalytic.company_id == company_id
    )
    
    if start_date:
        query = query.filter(SaleAnalytic.analysis_date >= start_date)
    
    if end_date:
        query = query.filter(SaleAnalytic.analysis_date <= end_date)
    
    analytics = query.all()
    
    return [
        {
            "id": analytic.id,
            "analysis_date": analytic.analysis_date,
            "total_sales": analytic.total_sales,
            "total_profit": analytic.total_profit,
            "customer_count": analytic.customer_count
        }
        for analytic in analytics
    ]