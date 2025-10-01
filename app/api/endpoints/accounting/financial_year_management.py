# backend/app/api/endpoints/financial_year_management.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date

from ...database import get_db
from ...models.accounting.financial_year_management import FinancialYear, FinancialYearPeriod, FinancialYearStatus
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class FinancialYearCreate(BaseModel):
    year_name: str
    start_date: date
    end_date: date
    company_id: int

class FinancialYearResponse(BaseModel):
    id: int
    year_name: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
    company_id: int

    class Config:
        from_attributes = True

@router.post("/financial-years", response_model=FinancialYearResponse)
async def create_financial_year(
    year_data: FinancialYearCreate,
    current_user: User = Depends(require_permission("accounting.create")),
    db: Session = Depends(get_db)
):
    """Create a new financial year"""
    
    # Check if financial year already exists
    existing_year = db.query(FinancialYear).filter(
        FinancialYear.year_name == year_data.year_name,
        FinancialYear.company_id == year_data.company_id
    ).first()
    
    if existing_year:
        raise HTTPException(
            status_code=400,
            detail="Financial year with this name already exists"
        )
    
    # Create financial year
    financial_year = FinancialYear(
        year_name=year_data.year_name,
        start_date=year_data.start_date,
        end_date=year_data.end_date,
        company_id=year_data.company_id,
        created_by=current_user.id
    )
    
    db.add(financial_year)
    db.commit()
    db.refresh(financial_year)
    
    return financial_year

@router.get("/financial-years", response_model=List[FinancialYearResponse])
async def get_financial_years(
    company_id: int,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get financial years for a company"""
    
    years = db.query(FinancialYear).filter(
        FinancialYear.company_id == company_id
    ).all()
    
    return years

@router.get("/financial-years/{year_id}", response_model=FinancialYearResponse)
async def get_financial_year(
    year_id: int,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get a specific financial year"""
    
    year = db.query(FinancialYear).filter(FinancialYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    return year

@router.put("/financial-years/{year_id}/activate")
async def activate_financial_year(
    year_id: int,
    current_user: User = Depends(require_permission("accounting.update")),
    db: Session = Depends(get_db)
):
    """Activate a financial year"""
    
    year = db.query(FinancialYear).filter(FinancialYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    # Deactivate all other years for this company
    db.query(FinancialYear).filter(
        FinancialYear.company_id == year.company_id,
        FinancialYear.id != year_id
    ).update({"is_active": False})
    
    # Activate this year
    year.is_active = True
    year.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Financial year activated successfully"}

@router.put("/financial-years/{year_id}/close")
async def close_financial_year(
    year_id: int,
    current_user: User = Depends(require_permission("accounting.update")),
    db: Session = Depends(get_db)
):
    """Close a financial year"""
    
    year = db.query(FinancialYear).filter(FinancialYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Financial year not found")
    
    if year.is_closed:
        raise HTTPException(status_code=400, detail="Financial year is already closed")
    
    # Close the year
    year.is_closed = True
    year.closed_by = current_user.id
    year.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Financial year closed successfully"}