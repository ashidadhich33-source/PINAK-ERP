# backend/app/api/endpoints/sales_gst_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.sales.sales_gst_integration import SaleGST, SaleEInvoice, SaleEWaybill
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class SaleGSTResponse(BaseModel):
    id: int
    sale_invoice_id: int
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    gst_rate: Decimal

    class Config:
        from_attributes = True

@router.get("/sale-gst", response_model=List[SaleGSTResponse])
async def get_sale_gst(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale GST records for a company"""
    
    gst_records = db.query(SaleGST).filter(
        SaleGST.company_id == company_id
    ).all()
    
    return gst_records

@router.get("/sale-e-invoices", response_model=List[dict])
async def get_sale_e_invoices(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale e-invoices for a company"""
    
    e_invoices = db.query(SaleEInvoice).filter(
        SaleEInvoice.company_id == company_id
    ).all()
    
    return [
        {
            "id": e_invoice.id,
            "sale_invoice_id": e_invoice.sale_invoice_id,
            "irn": e_invoice.irn,
            "ack_no": e_invoice.ack_no,
            "ack_date": e_invoice.ack_date,
            "status": e_invoice.status
        }
        for e_invoice in e_invoices
    ]

@router.get("/sale-e-waybills", response_model=List[dict])
async def get_sale_e_waybills(
    company_id: int,
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sale e-waybills for a company"""
    
    e_waybills = db.query(SaleEWaybill).filter(
        SaleEWaybill.company_id == company_id
    ).all()
    
    return [
        {
            "id": e_waybill.id,
            "sale_invoice_id": e_waybill.sale_invoice_id,
            "ewb_no": e_waybill.ewb_no,
            "ewb_date": e_waybill.ewb_date,
            "status": e_waybill.status
        }
        for e_waybill in e_waybills
    ]

@router.post("/generate-e-invoice/{sale_invoice_id}")
async def generate_e_invoice(
    sale_invoice_id: int,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Generate e-invoice for a sale"""
    
    # Check if e-invoice already exists
    existing_e_invoice = db.query(SaleEInvoice).filter(
        SaleEInvoice.sale_invoice_id == sale_invoice_id
    ).first()
    
    if existing_e_invoice:
        raise HTTPException(
            status_code=400,
            detail="E-invoice already exists for this sale"
        )
    
    # Create e-invoice record
    e_invoice = SaleEInvoice(
        sale_invoice_id=sale_invoice_id,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(e_invoice)
    db.commit()
    db.refresh(e_invoice)
    
    return {"message": "E-invoice generation initiated", "e_invoice_id": e_invoice.id}

@router.post("/generate-e-waybill/{sale_invoice_id}")
async def generate_e_waybill(
    sale_invoice_id: int,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Generate e-waybill for a sale"""
    
    # Check if e-waybill already exists
    existing_e_waybill = db.query(SaleEWaybill).filter(
        SaleEWaybill.sale_invoice_id == sale_invoice_id
    ).first()
    
    if existing_e_waybill:
        raise HTTPException(
            status_code=400,
            detail="E-waybill already exists for this sale"
        )
    
    # Create e-waybill record
    e_waybill = SaleEWaybill(
        sale_invoice_id=sale_invoice_id,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(e_waybill)
    db.commit()
    db.refresh(e_waybill)
    
    return {"message": "E-waybill generation initiated", "e_waybill_id": e_waybill.id}