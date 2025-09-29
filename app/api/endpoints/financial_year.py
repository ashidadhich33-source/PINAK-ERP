# backend/app/api/endpoints/financial_year.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date, datetime

from ...database import get_db
from ...models.company import Company, FinancialYear
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.financial_year_service import financial_year_service

router = APIRouter()

# Pydantic schemas
class FinancialYearCreateRequest(BaseModel):
    year_name: str
    start_date: date
    end_date: date
    
    @validator('year_name')
    def validate_year_name(cls, v):
        if not v or len(v) < 4:
            raise ValueError('Year name must be at least 4 characters')
        return v

class FinancialYearUpdateRequest(BaseModel):
    year_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class FinancialYearResponse(BaseModel):
    id: int
    company_id: int
    year_name: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
    closed_at: Optional[datetime] = None
    closed_by: Optional[int] = None
    opening_balances: Optional[dict] = None
    closing_remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OpeningBalanceRequest(BaseModel):
    opening_balances: dict

class ClosingBalanceResponse(BaseModel):
    financial_year: dict
    account_balances: dict
    stock_balances: List[dict]
    customer_balances: List[dict]
    supplier_balances: List[dict]
    calculated_at: str

class CarryForwardRequest(BaseModel):
    from_fy_id: int
    to_fy_id: int

class CarryForwardResponse(BaseModel):
    from_financial_year: str
    to_financial_year: str
    opening_balances: dict
    carried_forward_at: str

# Financial Year Management Endpoints
@router.post("/", response_model=FinancialYearResponse)
async def create_financial_year(
    fy_data: FinancialYearCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.create")),
    db: Session = Depends(get_db)
):
    """Create new financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    # Validate financial year dates
    is_valid, message = financial_year_service.validate_financial_year_dates(
        fy_data.start_date, fy_data.end_date
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=message
        )
    
    try:
        financial_year = financial_year_service.create_financial_year(
            db=db,
            company_id=company_id,
            year_name=fy_data.year_name,
            start_date=fy_data.start_date,
            end_date=fy_data.end_date,
            user_id=current_user.id
        )
        
        return financial_year
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create financial year: {str(e)}"
        )

@router.get("/", response_model=List[FinancialYearResponse])
async def list_financial_years(
    company_id: int = Query(...),
    include_closed: bool = Query(False),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """List financial years for company"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    financial_years = financial_year_service.list_financial_years(
        db=db,
        company_id=company_id,
        include_closed=include_closed
    )
    
    return financial_years

@router.get("/active", response_model=FinancialYearResponse)
async def get_active_financial_year(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get active financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    financial_year = financial_year_service.get_active_financial_year(
        db=db,
        company_id=company_id
    )
    
    if not financial_year:
        raise HTTPException(
            status_code=404,
            detail="No active financial year found"
        )
    
    return financial_year

@router.get("/{fy_id}", response_model=FinancialYearResponse)
async def get_financial_year(
    fy_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get financial year by ID"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    financial_year = financial_year_service.get_financial_year_by_id(
        db=db,
        company_id=company_id,
        fy_id=fy_id
    )
    
    if not financial_year:
        raise HTTPException(
            status_code=404,
            detail="Financial year not found"
        )
    
    return financial_year

@router.put("/{fy_id}", response_model=FinancialYearResponse)
async def update_financial_year(
    fy_id: int,
    fy_data: FinancialYearUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.update")),
    db: Session = Depends(get_db)
):
    """Update financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    financial_year = financial_year_service.get_financial_year_by_id(
        db=db,
        company_id=company_id,
        fy_id=fy_id
    )
    
    if not financial_year:
        raise HTTPException(
            status_code=404,
            detail="Financial year not found"
        )
    
    if financial_year.is_closed:
        raise HTTPException(
            status_code=400,
            detail="Cannot update closed financial year"
        )
    
    # Update financial year fields
    update_data = fy_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(financial_year, field, value)
    
    financial_year.updated_by = current_user.id
    financial_year.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(financial_year)
    
    return financial_year

@router.post("/{fy_id}/close")
async def close_financial_year(
    fy_id: int,
    closing_remarks: Optional[str] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.close")),
    db: Session = Depends(get_db)
):
    """Close financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        financial_year = financial_year_service.close_financial_year(
            db=db,
            company_id=company_id,
            fy_id=fy_id,
            user_id=current_user.id,
            closing_remarks=closing_remarks
        )
        
        return {
            "message": "Financial year closed successfully",
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "closed_at": financial_year.closed_at
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close financial year: {str(e)}"
        )

@router.get("/{fy_id}/closing-balances", response_model=ClosingBalanceResponse)
async def get_closing_balances(
    fy_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get closing balances for financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    financial_year = financial_year_service.get_financial_year_by_id(
        db=db,
        company_id=company_id,
        fy_id=fy_id
    )
    
    if not financial_year:
        raise HTTPException(
            status_code=404,
            detail="Financial year not found"
        )
    
    # Calculate closing balances
    closing_balances = financial_year_service._calculate_closing_balances(
        db=db,
        company_id=company_id,
        fy_id=fy_id
    )
    
    return ClosingBalanceResponse(**closing_balances)

@router.post("/{fy_id}/opening-balances")
async def create_opening_balances(
    fy_id: int,
    opening_data: OpeningBalanceRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Create opening balances for financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        financial_year = financial_year_service.create_opening_balances(
            db=db,
            company_id=company_id,
            fy_id=fy_id,
            opening_balances=opening_data.opening_balances,
            user_id=current_user.id
        )
        
        return {
            "message": "Opening balances created successfully",
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create opening balances: {str(e)}"
        )

@router.post("/carry-forward", response_model=CarryForwardResponse)
async def carry_forward_data(
    carry_data: CarryForwardRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Carry forward data between financial years"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = financial_year_service.carry_forward_data(
            db=db,
            company_id=company_id,
            from_fy_id=carry_data.from_fy_id,
            to_fy_id=carry_data.to_fy_id,
            user_id=current_user.id
        )
        
        return CarryForwardResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to carry forward data: {str(e)}"
        )

@router.get("/{fy_id}/summary")
async def get_financial_year_summary(
    fy_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get financial year summary"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        summary = financial_year_service.get_financial_year_summary(
            db=db,
            company_id=company_id,
            fy_id=fy_id
        )
        
        return summary
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get financial year summary: {str(e)}"
        )

@router.get("/{fy_id}/reports")
async def get_financial_year_reports(
    fy_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get financial year reports"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        reports = financial_year_service.get_financial_year_reports(
            db=db,
            company_id=company_id,
            fy_id=fy_id
        )
        
        return reports
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get financial year reports: {str(e)}"
        )

@router.get("/suggestions")
async def get_financial_year_suggestions(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get financial year suggestions"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    suggestions = financial_year_service.get_financial_year_suggestions(
        db=db,
        company_id=company_id
    )
    
    return {
        "suggestions": suggestions
    }

@router.post("/validate-dates")
async def validate_financial_year_dates(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(require_permission("financial_year.view"))
):
    """Validate financial year dates"""
    
    is_valid, message = financial_year_service.validate_financial_year_dates(
        start_date, end_date
    )
    
    return {
        "is_valid": is_valid,
        "message": message,
        "start_date": start_date,
        "end_date": end_date
    }