# backend/app/api/endpoints/gst.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.core.user import User
from ...core.security import get_current_user, require_permission
from ...services.core.gst_service import gst_service

router = APIRouter()

# Pydantic schemas
class GSTSlabResponse(BaseModel):
    id: int
    rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    description: str
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/gst-slabs", response_model=List[GSTSlabResponse])
async def get_gst_slabs(
    company_id: int,
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST slabs for a company"""
    
    try:
        slabs = gst_service.get_gst_slabs(db, company_id)
        return slabs
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get GST slabs: {str(e)}"
        )

@router.post("/gst-slabs", response_model=GSTSlabResponse)
async def create_gst_slab(
    rate: Decimal,
    cgst_rate: Decimal,
    sgst_rate: Decimal,
    igst_rate: Decimal,
    description: str,
    company_id: int,
    current_user: User = Depends(require_permission("gst.create")),
    db: Session = Depends(get_db)
):
    """Create a new GST slab"""
    
    try:
        slab = gst_service.create_gst_slab(
            db=db,
            company_id=company_id,
            rate=rate,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            description=description,
            created_by=current_user.id
        )
        return slab
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create GST slab: {str(e)}"
        )

@router.get("/gst-calculator")
async def calculate_gst(
    amount: Decimal,
    tax_rate: Decimal,
    is_interstate: bool = False,
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Calculate GST for a given amount"""
    
    try:
        result = gst_service.calculate_gst(
            amount=amount,
            tax_rate=tax_rate,
            is_interstate=is_interstate
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate GST: {str(e)}"
        )

@router.get("/gst-reports")
async def get_gst_reports(
    company_id: int,
    start_date: date,
    end_date: date,
    report_type: str = "summary",
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST reports"""
    
    try:
        reports = gst_service.get_gst_reports(
            db=db,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type
        )
        return reports
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get GST reports: {str(e)}"
        )

@router.get("/gst-returns")
async def get_gst_returns(
    company_id: int,
    return_period: str,
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST returns data"""
    
    try:
        returns_data = gst_service.get_gst_returns(
            db=db,
            company_id=company_id,
            return_period=return_period
        )
        return returns_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get GST returns: {str(e)}"
        )