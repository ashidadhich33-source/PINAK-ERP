# backend/app/api/endpoints/chart_of_accounts.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import date, datetime

from ...database import get_db
from ...models.company import Company, ChartOfAccount
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.chart_of_accounts_service import chart_of_accounts_service

router = APIRouter()

# Pydantic schemas
class ChartOfAccountCreateRequest(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    parent_id: Optional[int] = None
    gst_applicable: bool = False
    
    @validator('account_code')
    def validate_account_code(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Account code must be at least 2 characters')
        return v
    
    @validator('account_name')
    def validate_account_name(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Account name must be at least 2 characters')
        return v
    
    @validator('account_type')
    def validate_account_type(cls, v):
        allowed_types = ['Asset', 'Liability', 'Equity', 'Income', 'Expense']
        if v not in allowed_types:
            raise ValueError(f'Account type must be one of: {", ".join(allowed_types)}')
        return v

class ChartOfAccountUpdateRequest(BaseModel):
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    parent_id: Optional[int] = None
    gst_applicable: Optional[bool] = None
    is_active: Optional[bool] = None

class ChartOfAccountResponse(BaseModel):
    id: int
    company_id: int
    account_code: str
    account_name: str
    account_type: str
    parent_id: Optional[int] = None
    gst_applicable: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AccountBalanceResponse(BaseModel):
    account: dict
    period: dict
    opening_balance: Decimal
    debit_total: Decimal
    credit_total: Decimal
    closing_balance: Decimal
    balance_type: str

class TrialBalanceResponse(BaseModel):
    period: dict
    trial_balance: List[dict]
    totals: dict

class BalanceSheetResponse(BaseModel):
    as_on_date: date
    assets: dict
    liabilities: dict
    equity: dict
    totals: dict

class ProfitLossResponse(BaseModel):
    period: dict
    income: dict
    expenses: dict
    net_profit: Decimal
    net_profit_percentage: Decimal

# Chart of Accounts Management Endpoints
@router.post("/", response_model=ChartOfAccountResponse)
async def create_account(
    account_data: ChartOfAccountCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.create")),
    db: Session = Depends(get_db)
):
    """Create new chart of account"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        account = chart_of_accounts_service.create_account(
            db=db,
            company_id=company_id,
            account_code=account_data.account_code,
            account_name=account_data.account_name,
            account_type=account_data.account_type,
            parent_id=account_data.parent_id,
            gst_applicable=account_data.gst_applicable,
            user_id=current_user.id
        )
        
        return account
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account: {str(e)}"
        )

@router.get("/", response_model=List[ChartOfAccountResponse])
async def list_accounts(
    company_id: int = Query(...),
    account_type: Optional[str] = Query(None),
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """List chart of accounts for company"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    accounts = chart_of_accounts_service.list_accounts(
        db=db,
        company_id=company_id,
        account_type=account_type,
        parent_id=parent_id,
        is_active=is_active
    )
    
    return accounts

@router.get("/hierarchy", response_model=dict)
async def get_account_hierarchy(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get account hierarchy"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    hierarchy = chart_of_accounts_service.get_account_hierarchy(
        db=db,
        company_id=company_id
    )
    
    return hierarchy

@router.get("/{account_id}", response_model=ChartOfAccountResponse)
async def get_account(
    account_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get account by ID"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    account = chart_of_accounts_service.get_account_by_id(
        db=db,
        company_id=company_id,
        account_id=account_id
    )
    
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    return account

@router.put("/{account_id}", response_model=ChartOfAccountResponse)
async def update_account(
    account_id: int,
    account_data: ChartOfAccountUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.update")),
    db: Session = Depends(get_db)
):
    """Update account"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        account = chart_of_accounts_service.update_account(
            db=db,
            company_id=company_id,
            account_id=account_id,
            account_data=account_data.dict(exclude_unset=True),
            user_id=current_user.id
        )
        
        return account
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update account: {str(e)}"
        )

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.delete")),
    db: Session = Depends(get_db)
):
    """Delete account (soft delete)"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = chart_of_accounts_service.delete_account(
            db=db,
            company_id=company_id,
            account_id=account_id,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to delete account"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete account: {str(e)}"
        )

@router.post("/initialize-indian")
async def initialize_indian_chart_of_accounts(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.create")),
    db: Session = Depends(get_db)
):
    """Initialize Indian chart of accounts"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        accounts = chart_of_accounts_service.create_indian_chart_of_accounts(
            db=db,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Indian chart of accounts initialized successfully",
            "accounts_created": len(accounts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize Indian chart of accounts: {str(e)}"
        )

# Account Balance Endpoints
@router.get("/{account_id}/balance", response_model=AccountBalanceResponse)
async def get_account_balance(
    account_id: int,
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get account balance for period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        balance = chart_of_accounts_service.get_account_balance(
            db=db,
            company_id=company_id,
            account_id=account_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return AccountBalanceResponse(**balance)
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get account balance: {str(e)}"
        )

@router.get("/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get trial balance for period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        trial_balance = chart_of_accounts_service.get_trial_balance(
            db=db,
            company_id=company_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return TrialBalanceResponse(**trial_balance)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trial balance: {str(e)}"
        )

@router.get("/balance-sheet", response_model=BalanceSheetResponse)
async def get_balance_sheet(
    company_id: int = Query(...),
    as_on_date: date = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get balance sheet as on date"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        balance_sheet = chart_of_accounts_service.get_balance_sheet(
            db=db,
            company_id=company_id,
            as_on_date=as_on_date
        )
        
        return BalanceSheetResponse(**balance_sheet)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get balance sheet: {str(e)}"
        )

@router.get("/profit-loss", response_model=ProfitLossResponse)
async def get_profit_loss(
    company_id: int = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Get profit and loss statement for period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        profit_loss = chart_of_accounts_service.get_profit_loss(
            db=db,
            company_id=company_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return ProfitLossResponse(**profit_loss)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get profit and loss statement: {str(e)}"
        )

# Export Endpoints
@router.get("/export/excel")
async def export_chart_of_accounts_excel(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Export chart of accounts to Excel"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        excel_data = chart_of_accounts_service.export_chart_of_accounts_excel(
            db=db,
            company_id=company_id
        )
        
        return {
            "message": "Chart of accounts exported successfully",
            "file_size": len(excel_data),
            "file_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export chart of accounts: {str(e)}"
        )

# Account Type Endpoints
@router.get("/types")
async def get_account_types(
    current_user: User = Depends(require_permission("chart_of_accounts.view"))
):
    """Get available account types"""
    
    account_types = [
        {
            "type": "Asset",
            "description": "Resources owned by the company",
            "normal_balance": "Debit",
            "examples": ["Cash", "Bank", "Inventory", "Equipment"]
        },
        {
            "type": "Liability",
            "description": "Debts owed by the company",
            "normal_balance": "Credit",
            "examples": ["Accounts Payable", "Loans", "GST Payable"]
        },
        {
            "type": "Equity",
            "description": "Owner's claim on company assets",
            "normal_balance": "Credit",
            "examples": ["Share Capital", "Retained Earnings"]
        },
        {
            "type": "Income",
            "description": "Revenue earned by the company",
            "normal_balance": "Credit",
            "examples": ["Sales", "Service Revenue", "Interest Income"]
        },
        {
            "type": "Expense",
            "description": "Costs incurred by the company",
            "normal_balance": "Debit",
            "examples": ["Rent", "Salaries", "Marketing", "Utilities"]
        }
    ]
    
    return {
        "account_types": account_types,
        "total_types": len(account_types)
    }

# Account Validation Endpoints
@router.post("/validate-code")
async def validate_account_code(
    account_code: str = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("chart_of_accounts.view")),
    db: Session = Depends(get_db)
):
    """Validate account code availability"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    existing_account = chart_of_accounts_service.get_account_by_code(
        db=db,
        company_id=company_id,
        account_code=account_code
    )
    
    is_available = existing_account is None
    
    return {
        "account_code": account_code,
        "is_available": is_available,
        "message": "Account code is available" if is_available else "Account code already exists"
    }