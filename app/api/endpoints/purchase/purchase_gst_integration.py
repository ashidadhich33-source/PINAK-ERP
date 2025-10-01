# backend/app/api/endpoints/purchase_gst_integration.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.purchase.purchase_gst_integration import PurchaseGST, PurchaseEInvoice, PurchaseEWaybill
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PurchaseGSTResponse(BaseModel):
    id: int
    purchase_bill_id: int
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    gst_rate: Decimal

    class Config:
        from_attributes = True

@router.get("/purchase-gst", response_model=List[PurchaseGSTResponse])
async def get_purchase_gst(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase GST records for a company"""
    
    gst_records = db.query(PurchaseGST).filter(
        PurchaseGST.company_id == company_id
    ).all()
    
    return gst_records

@router.get("/purchase-e-invoices", response_model=List[dict])
async def get_purchase_e_invoices(
    company_id: int,
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase e-invoices for a company"""
    
    e_invoices = db.query(PurchaseEInvoice).filter(
        PurchaseEInvoice.company_id == company_id
    ).all()
    
    return [
        {
            "id": e_invoice.id,
            "purchase_bill_id": e_invoice.purchase_bill_id,
            "irn": e_invoice.irn,
            "ack_no": e_invoice.ack_no,
            "ack_date": e_invoice.ack_date,
            "status": e_invoice.status
        }
        for e_invoice in e_invoices
    ]

@router.post("/generate-purchase-e-invoice/{purchase_bill_id}")
async def generate_purchase_e_invoice(
    purchase_bill_id: int,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Generate e-invoice for a purchase"""
    
    # Check if e-invoice already exists
    existing_e_invoice = db.query(PurchaseEInvoice).filter(
        PurchaseEInvoice.purchase_bill_id == purchase_bill_id
    ).first()
    
    if existing_e_invoice:
        raise HTTPException(
            status_code=400,
            detail="E-invoice already exists for this purchase"
        )
    
    # Create e-invoice record
    e_invoice = PurchaseEInvoice(
        purchase_bill_id=purchase_bill_id,
        status="pending",
        created_by=current_user.id
    )
    
    db.add(e_invoice)
    db.commit()
    db.refresh(e_invoice)
    
    return {"message": "Purchase e-invoice generation initiated", "e_invoice_id": e_invoice.id}