# backend/app/api/endpoints/financial_year_management.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ....database import get_db
from ....models.company import Company
from ....models.user import User
from ...core.security import get_current_user, require_permission
from ...services.financial_year_management_service import financial_year_management_service

router = APIRouter()

# Pydantic schemas for Financial Year
class FinancialYearCreateRequest(BaseModel):
    year_name: str
    year_code: str
    start_date: date
    end_date: date
    notes: Optional[str] = None

class FinancialYearResponse(BaseModel):
    id: int
    company_id: int
    year_name: str
    year_code: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
    closing_date: Optional[datetime] = None
    closed_by: Optional[int] = None
    opening_balance_entered: bool
    year_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Opening Balance
class OpeningBalanceCreateRequest(BaseModel):
    financial_year_id: int
    account_id: int
    debit_balance: Decimal = 0
    credit_balance: Decimal = 0
    balance_type: str = 'zero'
    notes: Optional[str] = None

class OpeningBalanceResponse(BaseModel):
    id: int
    company_id: int
    financial_year_id: int
    account_id: int
    debit_balance: Decimal
    credit_balance: Decimal
    balance_type: str
    is_verified: bool
    verified_by: Optional[int] = None
    verified_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Year Closing
class YearClosingCreateRequest(BaseModel):
    financial_year_id: int
    closing_type: str = 'full_closing'
    closing_notes: Optional[str] = None

class YearClosingResponse(BaseModel):
    id: int
    company_id: int
    financial_year_id: int
    closing_type: str
    closing_date: datetime
    closing_status: str
    closing_data: Optional[dict] = None
    closing_errors: Optional[dict] = None
    closing_notes: Optional[str] = None
    closed_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Data Carry Forward
class DataCarryForwardCreateRequest(BaseModel):
    from_year_id: int
    to_year_id: int
    carry_forward_type: str
    notes: Optional[str] = None

class DataCarryForwardResponse(BaseModel):
    id: int
    company_id: int
    from_year_id: int
    to_year_id: int
    carry_forward_type: str
    carry_forward_status: str
    carry_forward_data: Optional[dict] = None
    carry_forward_errors: Optional[dict] = None
    processed_date: Optional[datetime] = None
    processed_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Year Analytics
class YearAnalyticsResponse(BaseModel):
    id: int
    company_id: int
    financial_year_id: int
    analytics_date: date
    total_sales: Decimal
    total_purchases: Decimal
    total_expenses: Decimal
    total_income: Decimal
    net_profit: Decimal
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    cash_flow: Decimal
    inventory_value: Decimal
    customer_count: int
    supplier_count: int
    transaction_count: int
    analytics_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Year Backup
class YearBackupCreateRequest(BaseModel):
    financial_year_id: int
    backup_name: str
    backup_type: str = 'full'
    notes: Optional[str] = None

class YearBackupResponse(BaseModel):
    id: int
    company_id: int
    financial_year_id: int
    backup_name: str
    backup_type: str
    backup_path: str
    backup_size: Optional[int] = None
    backup_status: str
    backup_data: Optional[dict] = None
    backup_errors: Optional[dict] = None
    backup_date: datetime
    backup_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Year Report
class YearReportCreateRequest(BaseModel):
    financial_year_id: int
    report_name: str
    report_type: str
    notes: Optional[str] = None

class YearReportResponse(BaseModel):
    id: int
    company_id: int
    financial_year_id: int
    report_name: str
    report_type: str
    report_data: dict
    report_file_path: Optional[str] = None
    report_file_size: Optional[int] = None
    report_status: str
    generated_date: Optional[datetime] = None
    generated_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Financial Year Endpoints
@router.post("/financial-years", response_model=FinancialYearResponse)
async def create_financial_year(
    year_data: FinancialYearCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Create financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        year = financial_year_management_service.create_financial_year(
            db=db,
            company_id=company_id,
            year_name=year_data.year_name,
            year_code=year_data.year_code,
            start_date=year_data.start_date,
            end_date=year_data.end_date,
            notes=year_data.notes,
            user_id=current_user.id
        )
        
        return year
        
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

@router.get("/financial-years", response_model=List[FinancialYearResponse])
async def get_financial_years(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    is_closed: Optional[bool] = Query(None),
    year_status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get financial years"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    years = financial_year_management_service.get_financial_years(
        db=db,
        company_id=company_id,
        is_active=is_active,
        is_closed=is_closed,
        year_status=year_status
    )
    
    return years

@router.post("/financial-years/{year_id}/activate", response_model=FinancialYearResponse)
async def activate_financial_year(
    year_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Activate financial year"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        year = financial_year_management_service.activate_financial_year(
            db=db,
            company_id=company_id,
            year_id=year_id,
            user_id=current_user.id
        )
        
        return year
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate financial year: {str(e)}"
        )

@router.post("/financial-years/{year_id}/close", response_model=YearClosingResponse)
async def close_financial_year(
    year_id: int,
    closing_data: YearClosingCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
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
        closing = financial_year_management_service.close_financial_year(
            db=db,
            company_id=company_id,
            year_id=year_id,
            closing_type=closing_data.closing_type,
            user_id=current_user.id
        )
        
        return closing
        
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

# Opening Balance Endpoints
@router.post("/opening-balances", response_model=OpeningBalanceResponse)
async def create_opening_balance(
    balance_data: OpeningBalanceCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Create opening balance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        balance = financial_year_management_service.create_opening_balance(
            db=db,
            company_id=company_id,
            financial_year_id=balance_data.financial_year_id,
            account_id=balance_data.account_id,
            debit_balance=balance_data.debit_balance,
            credit_balance=balance_data.credit_balance,
            balance_type=balance_data.balance_type,
            notes=balance_data.notes,
            user_id=current_user.id
        )
        
        return balance
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create opening balance: {str(e)}"
        )

@router.get("/opening-balances", response_model=List[OpeningBalanceResponse])
async def get_opening_balances(
    financial_year_id: int = Query(...),
    company_id: int = Query(...),
    is_verified: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get opening balances"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    balances = financial_year_management_service.get_opening_balances(
        db=db,
        company_id=company_id,
        financial_year_id=financial_year_id,
        is_verified=is_verified
    )
    
    return balances

@router.post("/opening-balances/{balance_id}/verify", response_model=OpeningBalanceResponse)
async def verify_opening_balance(
    balance_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Verify opening balance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        balance = financial_year_management_service.verify_opening_balance(
            db=db,
            company_id=company_id,
            balance_id=balance_id,
            user_id=current_user.id
        )
        
        return balance
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify opening balance: {str(e)}"
        )

# Data Carry Forward Endpoints
@router.post("/data-carry-forward", response_model=DataCarryForwardResponse)
async def create_data_carry_forward(
    carry_forward_data: DataCarryForwardCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Create data carry forward"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        carry_forward = financial_year_management_service.create_data_carry_forward(
            db=db,
            company_id=company_id,
            from_year_id=carry_forward_data.from_year_id,
            to_year_id=carry_forward_data.to_year_id,
            carry_forward_type=carry_forward_data.carry_forward_type,
            user_id=current_user.id
        )
        
        return carry_forward
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create data carry forward: {str(e)}"
        )

# Year Analytics Endpoints
@router.get("/year-analytics", response_model=YearAnalyticsResponse)
async def get_year_analytics(
    financial_year_id: int = Query(...),
    analytics_date: Optional[date] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Get year analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = financial_year_management_service.get_year_analytics(
        db=db,
        company_id=company_id,
        financial_year_id=financial_year_id,
        analytics_date=analytics_date
    )
    
    return analytics

# Year Backup Endpoints
@router.post("/year-backups", response_model=YearBackupResponse)
async def create_year_backup(
    backup_data: YearBackupCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.manage")),
    db: Session = Depends(get_db)
):
    """Create year backup"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        backup = financial_year_management_service.create_year_backup(
            db=db,
            company_id=company_id,
            financial_year_id=backup_data.financial_year_id,
            backup_name=backup_data.backup_name,
            backup_type=backup_data.backup_type,
            user_id=current_user.id
        )
        
        return backup
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create year backup: {str(e)}"
        )

# Year Report Endpoints
@router.post("/year-reports", response_model=YearReportResponse)
async def generate_year_report(
    report_data: YearReportCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("financial_year.view")),
    db: Session = Depends(get_db)
):
    """Generate year report"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        report = financial_year_management_service.generate_year_report(
            db=db,
            company_id=company_id,
            financial_year_id=report_data.financial_year_id,
            report_name=report_data.report_name,
            report_type=report_data.report_type,
            user_id=current_user.id
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate year report: {str(e)}"
        )