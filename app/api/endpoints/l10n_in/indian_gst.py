# backend/app/api/endpoints/l10n_in/indian_gst.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date

from ...database import get_db
from ...models.core import Company, User
from ...core.security import get_current_user, require_permission
from ...services.l10n_in.gst_service import indian_gst_service

router = APIRouter()

# Pydantic Models
class GSTCalculationRequest(BaseModel):
    taxable_amount: float
    supplier_state_code: str
    recipient_state_code: str
    gst_rate: float
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    
    @validator('taxable_amount')
    def validate_taxable_amount(cls, v):
        if v <= 0:
            raise ValueError('Taxable amount must be greater than 0')
        return v
    
    @validator('gst_rate')
    def validate_gst_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('GST rate must be between 0 and 100')
        return v

class GSTCalculationResponse(BaseModel):
    place_of_supply: str
    gst_rate: float
    cgst_rate: float
    cgst_amount: float
    sgst_rate: float
    sgst_amount: float
    igst_rate: float
    igst_amount: float
    cess_rate: float
    cess_amount: float
    total_gst_amount: float
    taxable_amount: float
    total_amount: float

class GSTSlabCreate(BaseModel):
    name: str
    tax_type: str
    rate: float
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
    igst_rate: Optional[float] = None
    cess_rate: Optional[float] = None
    description: Optional[str] = None

class GSTSlabResponse(BaseModel):
    id: int
    name: str
    tax_type: str
    rate: float
    cgst_rate: Optional[float] = None
    sgst_rate: Optional[float] = None
    igst_rate: Optional[float] = None
    cess_rate: Optional[float] = None
    description: Optional[str] = None

class HSNCodeResponse(BaseModel):
    id: int
    code: str
    description: str
    gst_rate: Optional[float] = None
    cess_rate: Optional[float] = None

class SACCodeResponse(BaseModel):
    id: int
    code: str
    description: str
    category: Optional[str] = None
    gst_rate: Optional[float] = None
    cess_rate: Optional[float] = None

class StateCodeResponse(BaseModel):
    id: int
    code: str
    name: str
    state_type: str

class GSTINValidationRequest(BaseModel):
    gstin: str

class GSTINValidationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    state_code: Optional[str] = None
    pan: Optional[str] = None

# API Endpoints

@router.post("/calculate-gst", response_model=GSTCalculationResponse)
async def calculate_gst(
    request: GSTCalculationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate GST for a transaction"""
    try:
        result = indian_gst_service.calculate_gst(
            db=db,
            company_id=current_user.company_id,
            taxable_amount=Decimal(str(request.taxable_amount)),
            supplier_state_code=request.supplier_state_code,
            recipient_state_code=request.recipient_state_code,
            gst_rate=Decimal(str(request.gst_rate)),
            hsn_code=request.hsn_code,
            sac_code=request.sac_code
        )
        
        return GSTCalculationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GST calculation failed: {str(e)}"
        )

@router.get("/gst-slabs", response_model=List[GSTSlabResponse])
async def get_gst_slabs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all GST slabs for the company"""
    try:
        slabs = indian_gst_service.get_gst_slabs(db, current_user.company_id)
        return [GSTSlabResponse(**slab) for slab in slabs]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch GST slabs: {str(e)}"
        )

@router.post("/gst-slabs", response_model=GSTSlabResponse)
async def create_gst_slab(
    request: GSTSlabCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new GST slab"""
    try:
        gst_slab = indian_gst_service.create_gst_slab(
            db=db,
            company_id=current_user.company_id,
            name=request.name,
            tax_type=request.tax_type,
            rate=Decimal(str(request.rate)),
            cgst_rate=Decimal(str(request.cgst_rate)) if request.cgst_rate else None,
            sgst_rate=Decimal(str(request.sgst_rate)) if request.sgst_rate else None,
            igst_rate=Decimal(str(request.igst_rate)) if request.igst_rate else None,
            cess_rate=Decimal(str(request.cess_rate)) if request.cess_rate else None,
            description=request.description
        )
        
        return GSTSlabResponse(
            id=gst_slab.id,
            name=gst_slab.name,
            tax_type=gst_slab.tax_type.value,
            rate=float(gst_slab.rate),
            cgst_rate=float(gst_slab.cgst_rate) if gst_slab.cgst_rate else None,
            sgst_rate=float(gst_slab.sgst_rate) if gst_slab.sgst_rate else None,
            igst_rate=float(gst_slab.igst_rate) if gst_slab.igst_rate else None,
            cess_rate=float(gst_slab.cess_rate) if gst_slab.cess_rate else None,
            description=gst_slab.description
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create GST slab: {str(e)}"
        )

@router.get("/hsn-codes", response_model=List[HSNCodeResponse])
async def get_hsn_codes(
    search: Optional[str] = Query(None, description="Search term for HSN codes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get HSN codes with optional search"""
    try:
        hsn_codes = indian_gst_service.get_hsn_codes(
            db, current_user.company_id, search
        )
        return [HSNCodeResponse(**hsn) for hsn in hsn_codes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch HSN codes: {str(e)}"
        )

@router.get("/sac-codes", response_model=List[SACCodeResponse])
async def get_sac_codes(
    search: Optional[str] = Query(None, description="Search term for SAC codes"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SAC codes with optional search"""
    try:
        sac_codes = indian_gst_service.get_sac_codes(
            db, current_user.company_id, search
        )
        return [SACCodeResponse(**sac) for sac in sac_codes]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch SAC codes: {str(e)}"
        )

@router.get("/state-codes", response_model=List[StateCodeResponse])
async def get_state_codes(
    db: Session = Depends(get_db)
):
    """Get all GST state codes"""
    try:
        states = indian_gst_service.get_state_codes(db)
        return [StateCodeResponse(**state) for state in states]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch state codes: {str(e)}"
        )

@router.post("/validate-gstin", response_model=GSTINValidationResponse)
async def validate_gstin(
    request: GSTINValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate GSTIN format"""
    try:
        result = indian_gst_service.validate_gstin(request.gstin)
        return GSTINValidationResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GSTIN validation failed: {str(e)}"
        )

@router.get("/place-of-supply-rules")
async def get_place_of_supply_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get place of supply rules"""
    try:
        rules = indian_gst_service.get_place_of_supply_rules(db, current_user.company_id)
        return rules
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch place of supply rules: {str(e)}"
        )

@router.get("/gst-summary")
async def get_gst_summary(
    from_date: date = Query(..., description="From date"),
    to_date: date = Query(..., description="To date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get GST summary for a period"""
    try:
        # This would typically query sales and purchase invoices
        # and calculate GST summary
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "gst_summary": {
                "total_sales": 0,
                "total_purchases": 0,
                "cgst_collected": 0,
                "sgst_collected": 0,
                "igst_collected": 0,
                "cess_collected": 0,
                "total_gst_collected": 0,
                "cgst_paid": 0,
                "sgst_paid": 0,
                "igst_paid": 0,
                "cess_paid": 0,
                "total_gst_paid": 0,
                "net_gst_payable": 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch GST summary: {str(e)}"
        )