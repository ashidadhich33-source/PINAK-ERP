# backend/app/api/endpoints/sales_return_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.sales.sales_return_integration import SaleReturnComprehensive, SaleReturnItemComprehensive
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class SaleReturnCreate(BaseModel):
    original_invoice_id: int
    return_date: date
    return_reason: str
    customer_id: int
    company_id: int
    items: List[dict]

class SaleReturnResponse(BaseModel):
    id: int
    return_number: str
    return_date: date
    original_invoice_id: int
    customer_id: int
    total_amount: Decimal
    status: str

    class Config:
        from_attributes = True

@router.post("/sale-returns", response_model=SaleReturnResponse)
async def create_sale_return(
    return_data: SaleReturnCreate,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create a new sale return"""
    
    # Create sale return
    sale_return = SaleReturnComprehensive(
        original_invoice_id=return_data.original_invoice_id,
        return_date=return_data.return_date,
        return_reason=return_data.return_reason,
        customer_id=return_data.customer_id,
        company_id=return_data.company_id,
        created_by=current_user.id
    )
    
    db.add(sale_return)
    db.flush()
    
    # Add return items
    total_amount = Decimal('0')
    for item_data in return_data.items:
        item = SaleReturnItemComprehensive(
            sale_return_id=sale_return.id,
            item_id=item_data['item_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['quantity'] * item_data['unit_price'],
            reason=item_data.get('reason', ''),
            created_by=current_user.id
        )
        db.add(item)
        total_amount += item.total_price
    
    sale_return.total_amount = total_amount
    sale_return.return_number = f"SR{sale_return.id:06d}"
    
    db.commit()
    db.refresh(sale_return)
    
    return sale_return

@router.get("/sale-returns", response_model=List[SaleReturnResponse])
async def get_sale_returns(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale returns for a company"""
    
    returns = db.query(SaleReturnComprehensive).filter(
        SaleReturnComprehensive.company_id == company_id
    ).all()
    
    return returns

@router.get("/sale-returns/{return_id}", response_model=SaleReturnResponse)
async def get_sale_return(
    return_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get a specific sale return"""
    
    sale_return = db.query(SaleReturnComprehensive).filter(
        SaleReturnComprehensive.id == return_id
    ).first()
    
    if not sale_return:
        raise HTTPException(status_code=404, detail="Sale return not found")
    
    return sale_return

@router.put("/sale-returns/{return_id}/approve")
async def approve_sale_return(
    return_id: int,
    current_user: User = Depends(require_permission("sales.update")),
    db: Session = Depends(get_db)
):
    """Approve a sale return"""
    
    sale_return = db.query(SaleReturnComprehensive).filter(
        SaleReturnComprehensive.id == return_id
    ).first()
    
    if not sale_return:
        raise HTTPException(status_code=404, detail="Sale return not found")
    
    if sale_return.status == "approved":
        raise HTTPException(status_code=400, detail="Sale return is already approved")
    
    sale_return.status = "approved"
    sale_return.approved_by = current_user.id
    sale_return.approved_at = datetime.utcnow()
    sale_return.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Sale return approved successfully"}

@router.put("/sale-returns/{return_id}/reject")
async def reject_sale_return(
    return_id: int,
    reason: str,
    current_user: User = Depends(require_permission("sales.update")),
    db: Session = Depends(get_db)
):
    """Reject a sale return"""
    
    sale_return = db.query(SaleReturnComprehensive).filter(
        SaleReturnComprehensive.id == return_id
    ).first()
    
    if not sale_return:
        raise HTTPException(status_code=404, detail="Sale return not found")
    
    if sale_return.status == "rejected":
        raise HTTPException(status_code=400, detail="Sale return is already rejected")
    
    sale_return.status = "rejected"
    sale_return.rejection_reason = reason
    sale_return.rejected_by = current_user.id
    sale_return.rejected_at = datetime.utcnow()
    sale_return.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Sale return rejected successfully"}