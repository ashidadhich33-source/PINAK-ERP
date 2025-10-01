# backend/app/api/endpoints/indian_gst.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.l10n_in.gst_tax_structure import GSTTaxStructure
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class GSTTaxStructureResponse(BaseModel):
    id: int
    tax_rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    description: str
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/gst-tax-structures", response_model=List[GSTTaxStructureResponse])
async def get_gst_tax_structures(
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST tax structures"""
    
    tax_structures = db.query(GSTTaxStructure).filter(
        GSTTaxStructure.is_active == True
    ).all()
    
    return tax_structures

@router.get("/gst-tax-structures/{tax_id}", response_model=GSTTaxStructureResponse)
async def get_gst_tax_structure(
    tax_id: int,
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get a specific GST tax structure"""
    
    tax_structure = db.query(GSTTaxStructure).filter(GSTTaxStructure.id == tax_id).first()
    if not tax_structure:
        raise HTTPException(status_code=404, detail="GST tax structure not found")
    
    return tax_structure

@router.get("/gst-calculator")
async def calculate_gst(
    amount: Decimal,
    tax_rate: Decimal,
    is_interstate: bool = False,
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Calculate GST for a given amount"""
    
    if is_interstate:
        # Interstate - IGST
        igst_amount = (amount * tax_rate) / 100
        cgst_amount = Decimal('0')
        sgst_amount = Decimal('0')
    else:
        # Intrastate - CGST + SGST
        half_rate = tax_rate / 2
        cgst_amount = (amount * half_rate) / 100
        sgst_amount = (amount * half_rate) / 100
        igst_amount = Decimal('0')
    
    total_gst = cgst_amount + sgst_amount + igst_amount
    total_amount = amount + total_gst
    
    return {
        "base_amount": float(amount),
        "tax_rate": float(tax_rate),
        "is_interstate": is_interstate,
        "cgst_amount": float(cgst_amount),
        "sgst_amount": float(sgst_amount),
        "igst_amount": float(igst_amount),
        "total_gst": float(total_gst),
        "total_amount": float(total_amount)
    }