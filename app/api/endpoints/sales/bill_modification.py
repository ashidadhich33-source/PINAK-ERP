# backend/app/api/endpoints/sales/bill_modification.py
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
class SalesInvoiceItemUpdate(BaseModel):
    item_id: Optional[int] = None
    barcode: Optional[str] = None
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    discount_percent: Decimal = Field(ge=0, le=100, default=0)
    discount_amount: Decimal = Field(ge=0, default=0)
    tax_rate: Decimal = Field(ge=0, le=100, default=0)
    tax_amount: Decimal = Field(ge=0, default=0)
    line_total: Decimal = Field(ge=0)


class SalesInvoiceUpdateRequest(BaseModel):
    customer_id: Optional[int] = None
    payment_mode: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[List[SalesInvoiceItemUpdate]] = None
    subtotal: Optional[Decimal] = Field(None, ge=0)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    tax_amount: Optional[Decimal] = Field(None, ge=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)


class SalesInvoiceModificationResponse(BaseModel):
    message: str
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[float] = None


# Endpoints
@router.get("/invoices/{invoice_id}/can-modify")
async def can_modify_sales_invoice(
    invoice_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Check if a sales invoice can be modified"""
    
    try:
        can_modify = bill_modification_service.can_modify_sales_invoice(
            db, invoice_id, current_user.role
        )
        return can_modify
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check modification permission: {str(e)}"
        )


@router.put("/invoices/{invoice_id}", response_model=SalesInvoiceModificationResponse)
async def modify_sales_invoice(
    invoice_id: int,
    invoice_data: SalesInvoiceUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.edit")),
    db: Session = Depends(get_db)
):
    """Modify a sales invoice
    
    **Restrictions:**
    - Cannot modify cancelled or paid invoices
    - Only admin can modify invoices from previous days
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
        result = bill_modification_service.modify_sales_invoice(
            db=db,
            invoice_id=invoice_id,
            invoice_data=invoice_data.dict(exclude_unset=True),
            user_id=current_user.id,
            user_role=current_user.role
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify sales invoice: {str(e)}"
        )


@router.delete("/invoices/{invoice_id}", response_model=SalesInvoiceModificationResponse)
async def delete_sales_invoice(
    invoice_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.delete")),
    db: Session = Depends(get_db)
):
    """Delete a sales invoice
    
    **Restrictions:**
    - Cannot delete cancelled or paid invoices
    - Only admin can delete invoices from previous days
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
        result = bill_modification_service.delete_sales_invoice(
            db=db,
            invoice_id=invoice_id,
            user_role=current_user.role
        )
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete sales invoice: {str(e)}"
        )