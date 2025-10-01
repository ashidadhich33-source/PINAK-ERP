# backend/app/api/endpoints/pos_payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.pos.pos_models import POSPayment
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class POSPaymentCreate(BaseModel):
    transaction_id: int
    session_id: int
    payment_method: str
    amount: Decimal
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    company_id: int

class POSPaymentResponse(BaseModel):
    id: int
    transaction_id: int
    session_id: int
    payment_method: str
    amount: Decimal
    payment_date: datetime
    reference_number: Optional[str]
    status: str

    class Config:
        from_attributes = True

@router.post("/payments", response_model=POSPaymentResponse)
async def create_pos_payment(
    payment_data: POSPaymentCreate,
    current_user: User = Depends(require_permission("pos.create")),
    db: Session = Depends(get_db)
):
    """Create a new POS payment"""
    
    # Create POS payment
    pos_payment = POSPayment(
        transaction_id=payment_data.transaction_id,
        session_id=payment_data.session_id,
        payment_method=payment_data.payment_method,
        amount=payment_data.amount,
        reference_number=payment_data.reference_number,
        notes=payment_data.notes,
        company_id=payment_data.company_id,
        created_by=current_user.id
    )
    
    db.add(pos_payment)
    db.commit()
    db.refresh(pos_payment)
    
    return pos_payment

@router.get("/payments", response_model=List[POSPaymentResponse])
async def get_pos_payments(
    company_id: int,
    session_id: Optional[int] = None,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS payments for a company"""
    
    query = db.query(POSPayment).filter(POSPayment.company_id == company_id)
    
    if session_id:
        query = query.filter(POSPayment.session_id == session_id)
    
    payments = query.all()
    return payments

@router.get("/payments/{payment_id}", response_model=POSPaymentResponse)
async def get_pos_payment(
    payment_id: int,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get a specific POS payment"""
    
    payment = db.query(POSPayment).filter(POSPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="POS payment not found")
    
    return payment