# backend/app/api/endpoints/double_entry_accounting.py
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
from ...services.double_entry_accounting_service import double_entry_accounting_service

router = APIRouter()

# Pydantic schemas for Journal Entry
class JournalEntryCreateRequest(BaseModel):
    entry_date: date
    narration: Optional[str] = None
    reference_number: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None

class JournalEntryItemCreateRequest(BaseModel):
    account_id: int
    debit_amount: Decimal = 0
    credit_amount: Decimal = 0
    description: Optional[str] = None
    reference: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: int
    company_id: int
    entry_number: str
    entry_date: date
    reference_number: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    narration: Optional[str] = None
    total_debit: Decimal
    total_credit: Decimal
    status: str
    is_reversed: bool
    reversed_entry_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Trial Balance
class TrialBalanceResponse(BaseModel):
    id: int
    company_id: int
    balance_date: date
    financial_year_id: int
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Balance Sheet
class BalanceSheetResponse(BaseModel):
    id: int
    company_id: int
    sheet_date: date
    financial_year_id: int
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    is_balanced: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Profit & Loss Statement
class ProfitLossStatementResponse(BaseModel):
    id: int
    company_id: int
    statement_date: date
    financial_year_id: int
    from_date: date
    to_date: date
    total_income: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Cash Flow Statement
class CashFlowStatementResponse(BaseModel):
    id: int
    company_id: int
    statement_date: date
    financial_year_id: int
    from_date: date
    to_date: date
    operating_cash_flow: Decimal
    investing_cash_flow: Decimal
    financing_cash_flow: Decimal
    net_cash_flow: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Account Reconciliation
class AccountReconciliationCreateRequest(BaseModel):
    account_id: int
    reconciliation_date: date
    opening_balance: Decimal = 0
    closing_balance: Decimal = 0
    book_balance: Decimal = 0
    bank_balance: Decimal = 0
    notes: Optional[str] = None

class ReconciliationItemCreateRequest(BaseModel):
    transaction_id: Optional[int] = None
    transaction_type: Optional[str] = None
    transaction_date: Optional[date] = None
    description: Optional[str] = None
    book_amount: Decimal = 0
    bank_amount: Decimal = 0
    is_reconciled: bool = False

class AccountReconciliationResponse(BaseModel):
    id: int
    company_id: int
    account_id: int
    reconciliation_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    book_balance: Decimal
    bank_balance: Decimal
    difference: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Accounting Period
class AccountingPeriodCreateRequest(BaseModel):
    period_name: str
    period_type: str
    start_date: date
    end_date: date
    financial_year_id: int
    notes: Optional[str] = None

class AccountingPeriodResponse(BaseModel):
    id: int
    company_id: int
    period_name: str
    period_type: str
    start_date: date
    end_date: date
    financial_year_id: int
    is_closed: bool
    closing_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Journal Entry Endpoints
@router.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry_data: JournalEntryCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Create journal entry"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        entry = double_entry_accounting_service.create_journal_entry(
            db=db,
            company_id=company_id,
            entry_date=entry_data.entry_date,
            narration=entry_data.narration,
            reference_number=entry_data.reference_number,
            reference_type=entry_data.reference_type,
            reference_id=entry_data.reference_id,
            notes=entry_data.notes,
            user_id=current_user.id
        )
        
        return entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create journal entry: {str(e)}"
        )

@router.post("/journal-entries/{entry_id}/items")
async def add_items_to_journal_entry(
    entry_id: int,
    items: List[JournalEntryItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Add items to journal entry"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        entry_items = double_entry_accounting_service.add_items_to_journal_entry(
            db=db,
            company_id=company_id,
            entry_id=entry_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to journal entry successfully",
            "items_count": len(entry_items)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to journal entry: {str(e)}"
        )

@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    entry_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Post journal entry"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = double_entry_accounting_service.post_journal_entry(
            db=db,
            company_id=company_id,
            entry_id=entry_id,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Journal entry posted successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to post journal entry"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post journal entry: {str(e)}"
        )

@router.post("/journal-entries/{entry_id}/reverse")
async def reverse_journal_entry(
    entry_id: int,
    reversal_date: date = Query(...),
    reversal_narration: Optional[str] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Reverse journal entry"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        reversal_entry = double_entry_accounting_service.reverse_journal_entry(
            db=db,
            company_id=company_id,
            entry_id=entry_id,
            reversal_date=reversal_date,
            reversal_narration=reversal_narration,
            user_id=current_user.id
        )
        
        return {
            "message": "Journal entry reversed successfully",
            "reversal_entry_id": reversal_entry.id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reverse journal entry: {str(e)}"
        )

# Trial Balance Endpoints
@router.post("/trial-balance", response_model=TrialBalanceResponse)
async def generate_trial_balance(
    balance_date: date = Query(...),
    financial_year_id: Optional[int] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Generate trial balance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        trial_balance = double_entry_accounting_service.generate_trial_balance(
            db=db,
            company_id=company_id,
            balance_date=balance_date,
            financial_year_id=financial_year_id,
            user_id=current_user.id
        )
        
        return trial_balance
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate trial balance: {str(e)}"
        )

# Balance Sheet Endpoints
@router.post("/balance-sheet", response_model=BalanceSheetResponse)
async def generate_balance_sheet(
    sheet_date: date = Query(...),
    financial_year_id: Optional[int] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Generate balance sheet"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        balance_sheet = double_entry_accounting_service.generate_balance_sheet(
            db=db,
            company_id=company_id,
            sheet_date=sheet_date,
            financial_year_id=financial_year_id,
            user_id=current_user.id
        )
        
        return balance_sheet
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate balance sheet: {str(e)}"
        )

# Profit & Loss Statement Endpoints
@router.post("/profit-loss-statement", response_model=ProfitLossStatementResponse)
async def generate_profit_loss_statement(
    from_date: date = Query(...),
    to_date: date = Query(...),
    financial_year_id: Optional[int] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Generate profit & loss statement"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        statement = double_entry_accounting_service.generate_profit_loss_statement(
            db=db,
            company_id=company_id,
            from_date=from_date,
            to_date=to_date,
            financial_year_id=financial_year_id,
            user_id=current_user.id
        )
        
        return statement
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate profit & loss statement: {str(e)}"
        )

# Cash Flow Statement Endpoints
@router.post("/cash-flow-statement", response_model=CashFlowStatementResponse)
async def generate_cash_flow_statement(
    from_date: date = Query(...),
    to_date: date = Query(...),
    financial_year_id: Optional[int] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Generate cash flow statement"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        statement = double_entry_accounting_service.generate_cash_flow_statement(
            db=db,
            company_id=company_id,
            from_date=from_date,
            to_date=to_date,
            financial_year_id=financial_year_id,
            user_id=current_user.id
        )
        
        return statement
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate cash flow statement: {str(e)}"
        )

# Account Reconciliation Endpoints
@router.post("/account-reconciliation", response_model=AccountReconciliationResponse)
async def create_account_reconciliation(
    reconciliation_data: AccountReconciliationCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Create account reconciliation"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        reconciliation = double_entry_accounting_service.create_account_reconciliation(
            db=db,
            company_id=company_id,
            account_id=reconciliation_data.account_id,
            reconciliation_date=reconciliation_data.reconciliation_date,
            opening_balance=reconciliation_data.opening_balance,
            closing_balance=reconciliation_data.closing_balance,
            book_balance=reconciliation_data.book_balance,
            bank_balance=reconciliation_data.bank_balance,
            notes=reconciliation_data.notes,
            user_id=current_user.id
        )
        
        return reconciliation
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account reconciliation: {str(e)}"
        )

@router.post("/account-reconciliation/{reconciliation_id}/items")
async def add_reconciliation_items(
    reconciliation_id: int,
    items: List[ReconciliationItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Add items to account reconciliation"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        reconciliation_items = double_entry_accounting_service.add_reconciliation_items(
            db=db,
            company_id=company_id,
            reconciliation_id=reconciliation_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to reconciliation successfully",
            "items_count": len(reconciliation_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to reconciliation: {str(e)}"
        )

# Accounting Period Endpoints
@router.post("/accounting-periods", response_model=AccountingPeriodResponse)
async def create_accounting_period(
    period_data: AccountingPeriodCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Create accounting period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        period = double_entry_accounting_service.create_accounting_period(
            db=db,
            company_id=company_id,
            period_name=period_data.period_name,
            period_type=period_data.period_type,
            start_date=period_data.start_date,
            end_date=period_data.end_date,
            financial_year_id=period_data.financial_year_id,
            notes=period_data.notes,
            user_id=current_user.id
        )
        
        return period
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create accounting period: {str(e)}"
        )

@router.post("/accounting-periods/{period_id}/close")
async def close_accounting_period(
    period_id: int,
    closing_date: date = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("accounting.manage")),
    db: Session = Depends(get_db)
):
    """Close accounting period"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = double_entry_accounting_service.close_accounting_period(
            db=db,
            company_id=company_id,
            period_id=period_id,
            closing_date=closing_date,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Accounting period closed successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to close accounting period"
            )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close accounting period: {str(e)}"
        )

# Financial Summary Endpoint
@router.get("/financial-summary")
async def get_financial_summary(
    company_id: int = Query(...),
    financial_year_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get financial summary"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        summary = double_entry_accounting_service.get_financial_summary(
            db=db,
            company_id=company_id,
            financial_year_id=financial_year_id
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
            detail=f"Failed to get financial summary: {str(e)}"
        )