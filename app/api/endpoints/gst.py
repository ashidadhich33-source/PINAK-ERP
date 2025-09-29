# backend/app/api/endpoints/gst.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date, datetime

from ...database import get_db
from ...models.company import Company, GSTSlab
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.gst_calculation_service import gst_calculation_service

router = APIRouter()

# Pydantic schemas
class GSTCalculationRequest(BaseModel):
    amount: Decimal
    gst_rate: Decimal
    gst_type: str = "cgst_sgst"  # cgst_sgst or igst
    state_code: Optional[str] = None

class GSTCalculationResponse(BaseModel):
    base_amount: Decimal
    gst_rate: Decimal
    gst_amount: Decimal
    total_amount: Decimal
    gst_type: str
    cgst_rate: Decimal
    sgst_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_rate: Decimal
    igst_amount: Decimal

class GSTSlabCreateRequest(BaseModel):
    rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    description: Optional[str] = None
    is_default: bool = False

class GSTSlabUpdateRequest(BaseModel):
    rate: Optional[Decimal] = None
    cgst_rate: Optional[Decimal] = None
    sgst_rate: Optional[Decimal] = None
    igst_rate: Optional[Decimal] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None

class GSTSlabResponse(BaseModel):
    id: int
    rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    description: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GSTLiabilityResponse(BaseModel):
    period: dict
    sales_gst: dict
    purchase_gst: dict
    net_liability: dict

class GSTReturnDataResponse(BaseModel):
    company_details: dict
    sales_data: List[dict]
    purchase_data: List[dict]

# GST Calculation Endpoints
@router.post("/calculate", response_model=GSTCalculationResponse)
async def calculate_gst(
    calculation_data: GSTCalculationRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("gst.calculate")),
    db: Session = Depends(get_db)
):
    """Calculate GST for given amount and rate"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = gst_calculation_service.calculate_gst(
            db=db,
            company_id=company_id,
            amount=calculation_data.amount,
            gst_rate=calculation_data.gst_rate,
            gst_type=calculation_data.gst_type,
            state_code=calculation_data.state_code
        )
        
        return GSTCalculationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"GST calculation failed: {str(e)}"
        )

@router.get("/rates", response_model=List[dict])
async def get_gst_rates(
    company_id: int = Query(...),
    effective_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get available GST rates for company"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    rates = gst_calculation_service.get_available_gst_rates(
        db=db,
        company_id=company_id,
        effective_date=effective_date
    )
    
    return rates

@router.get("/liability", response_model=GSTLiabilityResponse)
async def get_gst_liability(
    company_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST liability for a period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    liability = gst_calculation_service.calculate_gst_liability(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return GSTLiabilityResponse(**liability)

@router.get("/return-data", response_model=GSTReturnDataResponse)
async def get_gst_return_data(
    company_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST return data (GSTR-1 format)"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    return_data = gst_calculation_service.generate_gst_return_data(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return GSTReturnDataResponse(**return_data)

@router.get("/state-codes", response_model=List[dict])
async def get_gst_state_codes(
    current_user: User = Depends(require_permission("gst.view"))
):
    """Get list of GST state codes"""
    
    state_codes = gst_calculation_service.get_gst_state_codes()
    return state_codes

@router.post("/validate-gst", response_model=dict)
async def validate_gst_number(
    gst_number: str = Query(...),
    current_user: User = Depends(require_permission("gst.view"))
):
    """Validate GST number format"""
    
    is_valid = gst_calculation_service.validate_gst_number(gst_number)
    
    return {
        "gst_number": gst_number,
        "is_valid": is_valid,
        "message": "Valid GST number" if is_valid else "Invalid GST number format"
    }

# GST Slab Management Endpoints
@router.post("/slabs", response_model=GSTSlabResponse)
async def create_gst_slab(
    slab_data: GSTSlabCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("gst.manage")),
    db: Session = Depends(get_db)
):
    """Create new GST slab"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    # Check if GST slab with same rate already exists
    existing_slab = db.query(GSTSlab).filter(
        GSTSlab.company_id == company_id,
        GSTSlab.rate == slab_data.rate,
        GSTSlab.effective_from <= slab_data.effective_from,
        or_(
            GSTSlab.effective_to.is_(None),
            GSTSlab.effective_to >= slab_data.effective_from
        ),
        GSTSlab.is_active == True
    ).first()
    
    if existing_slab:
        raise HTTPException(
            status_code=400,
            detail="GST slab with this rate already exists for the given period"
        )
    
    # Create GST slab
    gst_slab = GSTSlab(
        company_id=company_id,
        **slab_data.dict(),
        created_by=current_user.id
    )
    
    db.add(gst_slab)
    db.commit()
    db.refresh(gst_slab)
    
    return gst_slab

@router.get("/slabs", response_model=List[GSTSlabResponse])
async def list_gst_slabs(
    company_id: int = Query(...),
    effective_date: Optional[date] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """List GST slabs for company"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    query = db.query(GSTSlab).filter(GSTSlab.company_id == company_id)
    
    if effective_date:
        query = query.filter(
            GSTSlab.effective_from <= effective_date,
            or_(
                GSTSlab.effective_to.is_(None),
                GSTSlab.effective_to >= effective_date
            )
        )
    
    if is_active is not None:
        query = query.filter(GSTSlab.is_active == is_active)
    
    slabs = query.order_by(GSTSlab.rate).all()
    return slabs

@router.get("/slabs/{slab_id}", response_model=GSTSlabResponse)
async def get_gst_slab(
    slab_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST slab by ID"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    slab = db.query(GSTSlab).filter(
        GSTSlab.id == slab_id,
        GSTSlab.company_id == company_id
    ).first()
    
    if not slab:
        raise HTTPException(
            status_code=404,
            detail="GST slab not found"
        )
    
    return slab

@router.put("/slabs/{slab_id}", response_model=GSTSlabResponse)
async def update_gst_slab(
    slab_id: int,
    slab_data: GSTSlabUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("gst.manage")),
    db: Session = Depends(get_db)
):
    """Update GST slab"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    slab = db.query(GSTSlab).filter(
        GSTSlab.id == slab_id,
        GSTSlab.company_id == company_id
    ).first()
    
    if not slab:
        raise HTTPException(
            status_code=404,
            detail="GST slab not found"
        )
    
    # Update slab fields
    update_data = slab_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(slab, field, value)
    
    slab.updated_by = current_user.id
    slab.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(slab)
    
    return slab

@router.delete("/slabs/{slab_id}")
async def delete_gst_slab(
    slab_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("gst.manage")),
    db: Session = Depends(get_db)
):
    """Delete GST slab (soft delete)"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    slab = db.query(GSTSlab).filter(
        GSTSlab.id == slab_id,
        GSTSlab.company_id == company_id
    ).first()
    
    if not slab:
        raise HTTPException(
            status_code=404,
            detail="GST slab not found"
        )
    
    # Soft delete
    slab.is_active = False
    slab.updated_by = current_user.id
    slab.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "GST slab deleted successfully"}

# GST Reports Endpoints
@router.get("/reports/summary")
async def get_gst_summary_report(
    company_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST summary report"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    liability = gst_calculation_service.calculate_gst_liability(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "company_name": company.name,
        "gst_number": company.gst_number,
        "period": f"{from_date} to {to_date}",
        "gst_liability": liability
    }

@router.get("/reports/rate-wise")
async def get_gst_rate_wise_report(
    company_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: User = Depends(require_permission("gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST rate-wise report"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    # This would require additional implementation
    # For now, return basic structure
    return {
        "company_name": company.name,
        "period": f"{from_date} to {to_date}",
        "rate_wise_summary": "Implementation pending"
    }