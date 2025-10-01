# backend/app/api/endpoints/purchases.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.purchase.purchase import PurchaseBill, PurchaseBillItem
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PurchaseBillCreate(BaseModel):
    bill_number: str
    bill_date: date
    supplier_id: int
    company_id: int
    items: List[dict]

class PurchaseBillResponse(BaseModel):
    id: int
    bill_number: str
    bill_date: date
    supplier_id: int
    total_amount: Decimal
    status: str

    class Config:
        from_attributes = True

@router.post("/purchase-bills", response_model=PurchaseBillResponse)
async def create_purchase_bill(
    bill_data: PurchaseBillCreate,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Create a new purchase bill"""
    
    # Create purchase bill
    purchase_bill = PurchaseBill(
        bill_number=bill_data.bill_number,
        bill_date=bill_data.bill_date,
        supplier_id=bill_data.supplier_id,
        company_id=bill_data.company_id,
        created_by=current_user.id
    )
    
    db.add(purchase_bill)
    db.flush()
    
    # Add bill items
    total_amount = Decimal('0')
    for item_data in bill_data.items:
        item = PurchaseBillItem(
            purchase_bill_id=purchase_bill.id,
            item_id=item_data['item_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['quantity'] * item_data['unit_price'],
            created_by=current_user.id
        )
        db.add(item)
        total_amount += item.total_price
    
    purchase_bill.total_amount = total_amount
    
    db.commit()
    db.refresh(purchase_bill)
    
    return purchase_bill

@router.get("/purchase-bills", response_model=List[PurchaseBillResponse])
async def get_purchase_bills(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase bills for a company"""
    
    bills = db.query(PurchaseBill).filter(
        PurchaseBill.company_id == company_id
    ).all()
    
    return bills

@router.get("/purchase-bills/{bill_id}", response_model=PurchaseBillResponse)
async def get_purchase_bill(
    bill_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get a specific purchase bill"""
    
    bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")
    
    return bill

@router.put("/purchase-bills/{bill_id}/approve")
async def approve_purchase_bill(
    bill_id: int,
    current_user: User = Depends(require_permission("purchase.update")),
    db: Session = Depends(get_db)
):
    """Approve a purchase bill"""
    
    bill = db.query(PurchaseBill).filter(PurchaseBill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Purchase bill not found")
    
    if bill.status == "approved":
        raise HTTPException(status_code=400, detail="Purchase bill is already approved")
    
    bill.status = "approved"
    bill.approved_by = current_user.id
    bill.approved_at = datetime.utcnow()
    bill.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Purchase bill approved successfully"}