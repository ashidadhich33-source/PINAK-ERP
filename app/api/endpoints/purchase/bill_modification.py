# backend/app/api/endpoints/purchase/bill_modification.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal

from ....core.deps import get_db, get_current_user, require_permission
from ....models.core.user import User
from ....services.core.bill_modification_service import bill_modification_service


router = APIRouter()


# Schemas
class PurchaseBillItemUpdate(BaseModel):
    barcode: str
    style_code: str
    size: Optional[str] = None
    hsn: Optional[str] = None
    qty: int = Field(gt=0)
    basic_rate: Decimal = Field(gt=0)
    cgst_rate: Decimal = Field(ge=0, le=100, default=0)
    sgst_rate: Decimal = Field(ge=0, le=100, default=0)
    igst_rate: Decimal = Field(ge=0, le=100, default=0)
    line_taxable: Decimal = Field(ge=0)
    cgst_amount: Decimal = Field(ge=0, default=0)
    sgst_amount: Decimal = Field(ge=0, default=0)
    igst_amount: Decimal = Field(ge=0, default=0)
    line_total: Decimal = Field(ge=0)
    mrp: Optional[Decimal] = None


class PurchaseBillUpdateRequest(BaseModel):
    supplier_id: Optional[int] = None
    supplier_bill_no: Optional[str] = None
    supplier_bill_date: Optional[date] = None
    payment_mode: Optional[str] = Field(None, regex="^(cash|credit)$")
    tax_region: Optional[str] = Field(None, regex="^(local|inter)$")
    reverse_charge: Optional[bool] = None
    items: Optional[List[PurchaseBillItemUpdate]] = None
    total_taxable: Optional[Decimal] = Field(None, ge=0)
    total_cgst: Optional[Decimal] = Field(None, ge=0)
    total_sgst: Optional[Decimal] = Field(None, ge=0)
    total_igst: Optional[Decimal] = Field(None, ge=0)
    grand_total: Optional[Decimal] = Field(None, ge=0)


class PurchaseBillUsageResponse(BaseModel):
    bill_id: int
    pb_no: str
    used_in_pos: bool
    used_in_sales: bool
    modification_locked: bool
    can_modify: bool
    can_delete: bool
    items_used_in_pos: List[Dict[str, Any]]
    items_used_in_sales: List[Dict[str, Any]]


class BillModificationResponse(BaseModel):
    message: str
    bill_id: Optional[int] = None
    pb_no: Optional[str] = None
    grand_total: Optional[float] = None


# Endpoints
@router.get("/bills/{bill_id}/check-usage", response_model=PurchaseBillUsageResponse)
async def check_purchase_bill_usage(
    bill_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Check if a purchase bill's items have been used in POS or Sales"""
    
    try:
        usage_info = bill_modification_service.check_purchase_bill_usage(db, bill_id)
        return usage_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check bill usage: {str(e)}"
        )


@router.get("/bills/{bill_id}/can-modify")
async def can_modify_purchase_bill(
    bill_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchases.view")),
    db: Session = Depends(get_db)
):
    """Check if a purchase bill can be modified"""
    
    try:
        can_modify = bill_modification_service.can_modify_purchase_bill(
            db, bill_id, current_user.role
        )
        return can_modify
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check modification permission: {str(e)}"
        )


@router.put("/bills/{bill_id}", response_model=BillModificationResponse)
async def modify_purchase_bill(
    bill_id: int,
    bill_data: PurchaseBillUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchases.edit")),
    db: Session = Depends(get_db)
):
    """Modify a purchase bill
    
    **Restrictions:**
    - Cannot modify if items have been used in POS or Sales transactions
    - Only admin can modify bills from previous days
    - Locked items cannot be modified
    """
    
    # Check if user has access to company
    from ....services.core.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = bill_modification_service.modify_purchase_bill(
            db=db,
            bill_id=bill_id,
            bill_data=bill_data.dict(exclude_unset=True),
            user_id=current_user.id,
            user_role=current_user.role
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify purchase bill: {str(e)}"
        )


@router.delete("/bills/{bill_id}", response_model=BillModificationResponse)
async def delete_purchase_bill(
    bill_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchases.delete")),
    db: Session = Depends(get_db)
):
    """Delete a purchase bill
    
    **Restrictions:**
    - Cannot delete if items have been used in POS or Sales transactions
    - Only admin can delete bills from previous days
    - All items must be unlocked
    """
    
    # Check if user has access to company
    from ....services.core.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = bill_modification_service.delete_purchase_bill(
            db=db,
            bill_id=bill_id,
            user_role=current_user.role
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete purchase bill: {str(e)}"
        )