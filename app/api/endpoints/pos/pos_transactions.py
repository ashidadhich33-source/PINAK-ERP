# backend/app/api/endpoints/pos_transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.pos.pos_models import POSTransaction
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class POSTransactionCreate(BaseModel):
    transaction_number: str
    customer_id: Optional[int] = None
    staff_id: int
    session_id: int
    subtotal: Decimal
    tax_amount: Decimal = 0
    discount_amount: Decimal = 0
    total_amount: Decimal
    notes: Optional[str] = None
    company_id: int

class POSTransactionResponse(BaseModel):
    id: int
    transaction_number: str
    transaction_date: datetime
    customer_id: Optional[int]
    staff_id: int
    session_id: int
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_status: str
    status: str

    class Config:
        from_attributes = True

@router.post("/transactions", response_model=POSTransactionResponse)
async def create_pos_transaction(
    transaction_data: POSTransactionCreate,
    current_user: User = Depends(require_permission("pos.create")),
    db: Session = Depends(get_db)
):
    """Create a new POS transaction"""
    
    # Create POS transaction
    pos_transaction = POSTransaction(
        transaction_number=transaction_data.transaction_number,
        customer_id=transaction_data.customer_id,
        staff_id=transaction_data.staff_id,
        session_id=transaction_data.session_id,
        subtotal=transaction_data.subtotal,
        tax_amount=transaction_data.tax_amount,
        discount_amount=transaction_data.discount_amount,
        total_amount=transaction_data.total_amount,
        notes=transaction_data.notes,
        company_id=transaction_data.company_id,
        created_by=current_user.id
    )
    
    db.add(pos_transaction)
    db.commit()
    db.refresh(pos_transaction)
    
    return pos_transaction

@router.get("/transactions", response_model=List[POSTransactionResponse])
async def get_pos_transactions(
    company_id: int,
    session_id: Optional[int] = None,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS transactions for a company"""
    
    query = db.query(POSTransaction).filter(POSTransaction.company_id == company_id)
    
    if session_id:
        query = query.filter(POSTransaction.session_id == session_id)
    
    transactions = query.all()
    return transactions

@router.get("/transactions/{transaction_id}", response_model=POSTransactionResponse)
async def get_pos_transaction(
    transaction_id: int,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get a specific POS transaction"""
    
    transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="POS transaction not found")
    
    return transaction

@router.put("/transactions/{transaction_id}/void")
async def void_pos_transaction(
    transaction_id: int,
    reason: str,
    current_user: User = Depends(require_permission("pos.update")),
    db: Session = Depends(get_db)
):
    """Void a POS transaction"""
    
    transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="POS transaction not found")
    
    if transaction.status == "cancelled":
        raise HTTPException(status_code=400, detail="Transaction is already cancelled")
    
    # Void the transaction
    transaction.status = "cancelled"
    transaction.notes = f"Voided: {reason}"
    transaction.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "POS transaction voided successfully"}