# backend/app/api/endpoints/payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.core.payment import Payment, PaymentMethod, PaymentGateway
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    payment_method: str
    reference: str
    description: str
    company_id: int

class PaymentResponse(BaseModel):
    id: int
    amount: Decimal
    payment_date: date
    payment_method: str
    reference: str
    description: str
    status: str

    class Config:
        from_attributes = True

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(require_permission("payments.create")),
    db: Session = Depends(get_db)
):
    """Create a new payment"""
    
    # Create payment
    payment = Payment(
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        payment_method=payment_data.payment_method,
        reference=payment_data.reference,
        description=payment_data.description,
        company_id=payment_data.company_id,
        created_by=current_user.id
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment

@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    company_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_permission("payments.view")),
    db: Session = Depends(get_db)
):
    """Get payments for a company"""
    
    query = db.query(Payment).filter(Payment.company_id == company_id)
    
    if start_date:
        query = query.filter(Payment.payment_date >= start_date)
    
    if end_date:
        query = query.filter(Payment.payment_date <= end_date)
    
    payments = query.all()
    return payments

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(require_permission("payments.view")),
    db: Session = Depends(get_db)
):
    """Get a specific payment"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment

@router.put("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(require_permission("payments.update")),
    db: Session = Depends(get_db)
):
    """Update a payment"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Update payment fields
    payment.amount = payment_data.amount
    payment.payment_date = payment_data.payment_date
    payment.payment_method = payment_data.payment_method
    payment.reference = payment_data.reference
    payment.description = payment_data.description
    payment.updated_by = current_user.id
    
    db.commit()
    db.refresh(payment)
    
    return payment

@router.delete("/payments/{payment_id}")
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(require_permission("payments.delete")),
    db: Session = Depends(get_db)
):
    """Delete a payment"""
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Soft delete
    payment.is_active = False
    payment.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Payment deleted successfully"}

@router.get("/payment-methods", response_model=List[dict])
async def get_payment_methods(
    current_user: User = Depends(require_permission("payments.view")),
    db: Session = Depends(get_db)
):
    """Get available payment methods"""
    
    methods = db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()
    
    return [
        {
            "id": method.id,
            "name": method.name,
            "description": method.description,
            "is_active": method.is_active
        }
        for method in methods
    ]