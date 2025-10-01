# backend/app/api/endpoints/purchase_accounting_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.purchase.purchase_accounting_integration import PurchaseJournalEntry, PurchasePayment
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PurchaseJournalEntryResponse(BaseModel):
    id: int
    purchase_bill_id: int
    journal_entry_id: int
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/purchase-journal-entries", response_model=List[PurchaseJournalEntryResponse])
async def get_purchase_journal_entries(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase journal entries for a company"""
    
    entries = db.query(PurchaseJournalEntry).filter(
        PurchaseJournalEntry.company_id == company_id
    ).all()
    
    return entries

@router.get("/purchase-payments", response_model=List[dict])
async def get_purchase_payments(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase payments for a company"""
    
    payments = db.query(PurchasePayment).filter(
        PurchasePayment.company_id == company_id
    ).all()
    
    return [
        {
            "id": payment.id,
            "purchase_bill_id": payment.purchase_bill_id,
            "amount": payment.amount,
            "payment_date": payment.payment_date,
            "payment_method": payment.payment_method
        }
        for payment in payments
    ]

@router.post("/purchase-payments")
async def create_purchase_payment(
    purchase_bill_id: int,
    amount: Decimal,
    payment_date: date,
    payment_method: str,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Create a new purchase payment"""
    
    # Check if purchase bill exists
    bill = db.query(PurchaseBill).filter(PurchaseBill.id == purchase_bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")
    
    # Create payment
    payment = PurchasePayment(
        purchase_bill_id=purchase_bill_id,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        company_id=bill.company_id,
        created_by=current_user.id
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {"message": "Purchase payment created successfully", "payment_id": payment.id}