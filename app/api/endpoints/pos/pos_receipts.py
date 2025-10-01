# backend/app/api/endpoints/pos_receipts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.pos.pos_models import POSReceipt
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class POSReceiptCreate(BaseModel):
    transaction_id: int
    session_id: int
    receipt_number: str
    receipt_type: str = "sale"
    total_amount: Decimal
    tax_amount: Decimal = 0
    discount_amount: Decimal = 0
    company_id: int

class POSReceiptResponse(BaseModel):
    id: int
    transaction_id: int
    session_id: int
    receipt_number: str
    receipt_date: datetime
    receipt_type: str
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    status: str

    class Config:
        from_attributes = True

@router.post("/receipts", response_model=POSReceiptResponse)
async def create_pos_receipt(
    receipt_data: POSReceiptCreate,
    current_user: User = Depends(require_permission("pos.create")),
    db: Session = Depends(get_db)
):
    """Create a new POS receipt"""
    
    # Create POS receipt
    pos_receipt = POSReceipt(
        transaction_id=receipt_data.transaction_id,
        session_id=receipt_data.session_id,
        receipt_number=receipt_data.receipt_number,
        receipt_type=receipt_data.receipt_type,
        total_amount=receipt_data.total_amount,
        tax_amount=receipt_data.tax_amount,
        discount_amount=receipt_data.discount_amount,
        company_id=receipt_data.company_id,
        created_by=current_user.id
    )
    
    db.add(pos_receipt)
    db.commit()
    db.refresh(pos_receipt)
    
    return pos_receipt

@router.get("/receipts", response_model=List[POSReceiptResponse])
async def get_pos_receipts(
    company_id: int,
    session_id: Optional[int] = None,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get POS receipts for a company"""
    
    query = db.query(POSReceipt).filter(POSReceipt.company_id == company_id)
    
    if session_id:
        query = query.filter(POSReceipt.session_id == session_id)
    
    receipts = query.all()
    return receipts

@router.get("/receipts/{receipt_id}", response_model=POSReceiptResponse)
async def get_pos_receipt(
    receipt_id: int,
    current_user: User = Depends(require_permission("pos.view")),
    db: Session = Depends(get_db)
):
    """Get a specific POS receipt"""
    
    receipt = db.query(POSReceipt).filter(POSReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="POS receipt not found")
    
    return receipt