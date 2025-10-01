# backend/app/api/endpoints/companies.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import date, datetime
import json

from app.database import get_db
from app.models.core.company import Company, UserCompany, FinancialYear, GSTSlab, ChartOfAccount
from app.models.core.user import User
from app.core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class CompanyCreateRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    business_type: Optional[str] = None
    financial_year_start: date = date(2024, 4, 1)
    financial_year_end: date = date(2025, 3, 31)
    current_financial_year: str = "2024-25"
    currency_code: str = "INR"
    currency_symbol: str = "₹"
    gst_registration_type: str = "regular"
    gst_state_code: Optional[str] = None
    theme_color: str = "#007bff"
    description: Optional[str] = None

class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    business_type: Optional[str] = None
    financial_year_start: Optional[date] = None
    financial_year_end: Optional[date] = None
    current_financial_year: Optional[str] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    gst_registration_type: Optional[str] = None
    gst_state_code: Optional[str] = None
    theme_color: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    legal_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    current_financial_year: str
    currency_code: str
    currency_symbol: str
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCompanyRequest(BaseModel):
    user_id: int
    role: str = "user"
    is_active: bool = True
    is_default: bool = False
    permissions: Optional[dict] = None

class UserCompanyResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    role: str
    is_active: bool
    is_default: bool
    last_accessed: Optional[datetime] = None
    access_count: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True

# Company Management Endpoints
@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreateRequest,
    current_user: User = Depends(require_permission("companies.create")),
    db: Session = Depends(get_db)
):
    """Create a new company"""
    
    # Check if GST number already exists
    if company_data.gst_number:
        existing_gst = db.query(Company).filter(
            Company.gst_number == company_data.gst_number
        ).first()
        if existing_gst:
            raise HTTPException(
                status_code=400,
                detail="Company with this GST number already exists"
            )
    
    # Check if PAN number already exists
    if company_data.pan_number:
        existing_pan = db.query(Company).filter(
            Company.pan_number == company_data.pan_number
        ).first()
        if existing_pan:
            raise HTTPException(
                status_code=400,
                detail="Company with this PAN number already exists"
            )
    
    # Create company
    company = Company(
        **company_data.dict(),
        created_by=current_user.id
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    # Create user-company association
    user_company = UserCompany(
        user_id=current_user.id,
        company_id=company.id,
        role="admin",
        is_active=True,
        is_default=True
    )
    
    db.add(user_company)
    
    # Create default financial year
    financial_year = FinancialYear(
        company_id=company.id,
        year_name=company.current_financial_year,
        start_date=company.financial_year_start,
        end_date=company.financial_year_end,
        is_active=True,
        created_by=current_user.id
    )
    
    db.add(financial_year)
    
    # Create default GST slabs
    default_gst_slabs = [
        {"rate": 0.00, "cgst_rate": 0.00, "sgst_rate": 0.00, "igst_rate": 0.00, "description": "0% GST"},
        {"rate": 5.00, "cgst_rate": 2.50, "sgst_rate": 2.50, "igst_rate": 5.00, "description": "5% GST"},
        {"rate": 12.00, "cgst_rate": 6.00, "sgst_rate": 6.00, "igst_rate": 12.00, "description": "12% GST"},
        {"rate": 18.00, "cgst_rate": 9.00, "sgst_rate": 9.00, "igst_rate": 18.00, "description": "18% GST"},
        {"rate": 28.00, "cgst_rate": 14.00, "sgst_rate": 14.00, "igst_rate": 28.00, "description": "28% GST"}
    ]
    
    for slab_data in default_gst_slabs:
        gst_slab = GSTSlab(
            company_id=company.id,
            effective_from=company.financial_year_start,
            **slab_data,
            created_by=current_user.id
        )
        db.add(gst_slab)
    
    db.commit()
    
    return company

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("companies.view")),
    db: Session = Depends(get_db)
):
    """List companies accessible to current user"""
    
    # Get user's companies
    user_companies = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.is_active == True
    ).all()
    
    company_ids = [uc.company_id for uc in user_companies]
    
    if not company_ids:
        return []
    
    query = db.query(Company).filter(Company.id.in_(company_ids))
    
    if search:
        query = query.filter(
            or_(
                Company.name.ilike(f"%{search}%"),
                Company.gst_number.ilike(f"%{search}%"),
                Company.pan_number.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)
    
    companies = query.offset(skip).limit(limit).all()
    return companies

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    current_user: User = Depends(require_permission("companies.view")),
    db: Session = Depends(get_db)
):
    """Get company details"""
    
    # Check if user has access to this company
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.is_active == True
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    return company

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdateRequest,
    current_user: User = Depends(require_permission("companies.update")),
    db: Session = Depends(get_db)
):
    """Update company details"""
    
    # Check if user has access to this company
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.is_active == True
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    # Update company fields
    update_data = company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_by = current_user.id
    company.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(company)
    
    return company

@router.delete("/{company_id}")
async def delete_company(
    company_id: int,
    current_user: User = Depends(require_permission("companies.delete")),
    db: Session = Depends(get_db)
):
    """Delete company (soft delete)"""
    
    # Check if user has admin access to this company
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin",
        UserCompany.is_active == True
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=403,
            detail="Admin access required to delete company"
        )
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    # Soft delete
    company.is_active = False
    company.updated_by = current_user.id
    company.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Company deleted successfully"}

# User-Company Management Endpoints
@router.post("/{company_id}/users", response_model=UserCompanyResponse)
async def add_user_to_company(
    company_id: int,
    user_company_data: UserCompanyRequest,
    current_user: User = Depends(require_permission("companies.manage_users")),
    db: Session = Depends(get_db)
):
    """Add user to company"""
    
    # Check if current user has admin access to this company
    admin_access = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin",
        UserCompany.is_active == True
    ).first()
    
    if not admin_access:
        raise HTTPException(
            status_code=403,
            detail="Admin access required to manage users"
        )
    
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_company_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if user is already associated with this company
    existing_association = db.query(UserCompany).filter(
        UserCompany.user_id == user_company_data.user_id,
        UserCompany.company_id == company_id
    ).first()
    
    if existing_association:
        raise HTTPException(
            status_code=400,
            detail="User is already associated with this company"
        )
    
    # Create user-company association
    user_company = UserCompany(
        user_id=user_company_data.user_id,
        company_id=company_id,
        role=user_company_data.role,
        is_active=user_company_data.is_active,
        is_default=user_company_data.is_default,
        permissions=json.dumps(user_company_data.permissions) if user_company_data.permissions else None,
        created_by=current_user.id
    )
    
    db.add(user_company)
    db.commit()
    db.refresh(user_company)
    
    # Add user information to response
    user_company.user_name = user.full_name
    user_company.user_email = user.email
    
    return user_company

@router.get("/{company_id}/users", response_model=List[UserCompanyResponse])
async def list_company_users(
    company_id: int,
    current_user: User = Depends(require_permission("companies.view_users")),
    db: Session = Depends(get_db)
):
    """List users associated with company"""
    
    # Check if user has access to this company
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.is_active == True
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    user_companies = db.query(UserCompany).filter(
        UserCompany.company_id == company_id
    ).all()
    
    # Add user information to response
    for uc in user_companies:
        user = db.query(User).filter(User.id == uc.user_id).first()
        if user:
            uc.user_name = user.full_name
            uc.user_email = user.email
    
    return user_companies

@router.put("/{company_id}/users/{user_id}", response_model=UserCompanyResponse)
async def update_user_company(
    company_id: int,
    user_id: int,
    user_company_data: UserCompanyRequest,
    current_user: User = Depends(require_permission("companies.manage_users")),
    db: Session = Depends(get_db)
):
    """Update user-company association"""
    
    # Check if current user has admin access to this company
    admin_access = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin",
        UserCompany.is_active == True
    ).first()
    
    if not admin_access:
        raise HTTPException(
            status_code=403,
            detail="Admin access required to manage users"
        )
    
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=404,
            detail="User-company association not found"
        )
    
    # Update user-company association
    update_data = user_company_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "permissions" and value:
            setattr(user_company, field, json.dumps(value))
        else:
            setattr(user_company, field, value)
    
    user_company.updated_by = current_user.id
    user_company.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user_company)
    
    # Add user information to response
    user = db.query(User).filter(User.id == user_company.user_id).first()
    if user:
        user_company.user_name = user.full_name
        user_company.user_email = user.email
    
    return user_company

@router.delete("/{company_id}/users/{user_id}")
async def remove_user_from_company(
    company_id: int,
    user_id: int,
    current_user: User = Depends(require_permission("companies.manage_users")),
    db: Session = Depends(get_db)
):
    """Remove user from company"""
    
    # Check if current user has admin access to this company
    admin_access = db.query(UserCompany).filter(
        UserCompany.user_id == current_user.id,
        UserCompany.company_id == company_id,
        UserCompany.role == "admin",
        UserCompany.is_active == True
    ).first()
    
    if not admin_access:
        raise HTTPException(
            status_code=403,
            detail="Admin access required to manage users"
        )
    
    user_company = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()
    
    if not user_company:
        raise HTTPException(
            status_code=404,
            detail="User-company association not found"
        )
    
    # Soft delete
    user_company.is_active = False
    user_company.updated_by = current_user.id
    user_company.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "User removed from company successfully"}