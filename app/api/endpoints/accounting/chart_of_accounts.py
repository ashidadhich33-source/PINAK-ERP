# backend/app/api/endpoints/chart_of_accounts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal

from app.database import get_db
# from app.models.accounting.chart_of_accounts import ChartOfAccount, AccountCategory, AccountSubCategory
from app.models.core.user import User
from app.core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class AccountCreate(BaseModel):
    code: str
    name: str
    type: str
    parent_id: Optional[int] = None
    company_id: int

class AccountResponse(BaseModel):
    id: int
    code: str
    name: str
    type: str
    parent_id: Optional[int]
    balance: Decimal
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(require_permission("accounting.create")),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    
    # Check if account code already exists
    existing_account = db.query(ChartOfAccount).filter(
        ChartOfAccount.code == account_data.code,
        ChartOfAccount.company_id == account_data.company_id
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail="Account with this code already exists"
        )
    
    # Create account
    account = ChartOfAccount(
        code=account_data.code,
        name=account_data.name,
        type=account_data.type,
        parent_id=account_data.parent_id,
        company_id=account_data.company_id,
        created_by=current_user.id
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return account

@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    company_id: int,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get chart of accounts for a company"""
    
    accounts = db.query(ChartOfAccount).filter(
        ChartOfAccount.company_id == company_id
    ).all()
    
    return accounts

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get a specific account"""
    
    account = db.query(ChartOfAccount).filter(ChartOfAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return account

@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountCreate,
    current_user: User = Depends(require_permission("accounting.update")),
    db: Session = Depends(get_db)
):
    """Update an account"""
    
    account = db.query(ChartOfAccount).filter(ChartOfAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Update account fields
    account.code = account_data.code
    account.name = account_data.name
    account.type = account_data.type
    account.parent_id = account_data.parent_id
    account.updated_by = current_user.id
    
    db.commit()
    db.refresh(account)
    
    return account

@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: int,
    current_user: User = Depends(require_permission("accounting.delete")),
    db: Session = Depends(get_db)
):
    """Delete an account"""
    
    account = db.query(ChartOfAccount).filter(ChartOfAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Soft delete
    account.is_active = False
    account.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Account deleted successfully"}