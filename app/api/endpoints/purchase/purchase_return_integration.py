# backend/app/api/endpoints/purchase_return_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.purchase.purchase_return_integration import PurchaseReturnComprehensive, PurchaseReturnItemComprehensive
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PurchaseReturnCreate(BaseModel):
    original_bill_id: int
    return_date: date
    return_reason: str
    supplier_id: int
    company_id: int
    items: List[dict]

class PurchaseReturnResponse(BaseModel):
    id: int
    return_number: str
    return_date: date
    original_bill_id: int
    supplier_id: int
    total_amount: Decimal
    status: str

    class Config:
        from_attributes = True

@router.post("/purchase-returns", response_model=PurchaseReturnResponse)
async def create_purchase_return(
    return_data: PurchaseReturnCreate,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Create a new purchase return"""
    
    # Create purchase return
    purchase_return = PurchaseReturnComprehensive(
        original_bill_id=return_data.original_bill_id,
        return_date=return_data.return_date,
        return_reason=return_data.return_reason,
        supplier_id=return_data.supplier_id,
        company_id=return_data.company_id,
        created_by=current_user.id
    )
    
    db.add(purchase_return)
    db.flush()
    
    # Add return items
    total_amount = Decimal('0')
    for item_data in return_data.items:
        item = PurchaseReturnItemComprehensive(
            purchase_return_id=purchase_return.id,
            item_id=item_data['item_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['quantity'] * item_data['unit_price'],
            reason=item_data.get('reason', ''),
            created_by=current_user.id
        )
        db.add(item)
        total_amount += item.total_price
    
    purchase_return.total_amount = total_amount
    purchase_return.return_number = f"PR{purchase_return.id:06d}"
    
    db.commit()
    db.refresh(purchase_return)
    
    return purchase_return

@router.get("/purchase-returns", response_model=List[PurchaseReturnResponse])
async def get_purchase_returns(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase returns for a company"""
    
    returns = db.query(PurchaseReturnComprehensive).filter(
        PurchaseReturnComprehensive.company_id == company_id
    ).all()
    
    return returns

@router.get("/purchase-returns/{return_id}", response_model=PurchaseReturnResponse)
async def get_purchase_return(
    return_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get a specific purchase return"""
    
    purchase_return = db.query(PurchaseReturnComprehensive).filter(
        PurchaseReturnComprehensive.id == return_id
    ).first()
    
    if not purchase_return:
        raise HTTPException(status_code=404, detail="Purchase return not found")
    
    return purchase_return

@router.put("/purchase-returns/{return_id}/approve")
async def approve_purchase_return(
    return_id: int,
    current_user: User = Depends(require_permission("purchase.update")),
    db: Session = Depends(get_db)
):
    """Approve a purchase return"""
    
    purchase_return = db.query(PurchaseReturnComprehensive).filter(
        PurchaseReturnComprehensive.id == return_id
    ).first()
    
    if not purchase_return:
        raise HTTPException(status_code=404, detail="Purchase return not found")
    
    if purchase_return.status == "approved":
        raise HTTPException(status_code=400, detail="Purchase return is already approved")
    
    purchase_return.status = "approved"
    purchase_return.approved_by = current_user.id
    purchase_return.approved_at = datetime.utcnow()
    purchase_return.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Purchase return approved successfully"}