# backend/app/api/endpoints/accounting/banking.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.accounting.banking import (
    BankAccount, BankStatement, BankStatementLine, PaymentMethod,
    PaymentTerm, CashRounding, BankReconciliation, ReconciliationLine,
    BankImportTemplate, BankImportLog, BankAccountType, PaymentMethodType,
    StatementStatus, ReconciliationStatus
)

router = APIRouter()

# --- Schemas ---
class BankAccountCreate(BaseModel):
    account_name: str = Field(..., min_length=3, max_length=100)
    account_number: str = Field(..., min_length=5, max_length=50)
    bank_name: str = Field(..., min_length=3, max_length=100)
    bank_code: Optional[str] = None
    account_type: BankAccountType
    currency_code: str = Field(default="INR", max_length=3)
    opening_balance: Decimal = Field(default=0)
    ifsc_code: Optional[str] = Field(None, max_length=11)
    micr_code: Optional[str] = Field(None, max_length=9)
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    notes: Optional[str] = None

class BankAccountResponse(BaseModel):
    id: int
    account_name: str
    account_number: str
    bank_name: str
    bank_code: Optional[str]
    account_type: BankAccountType
    currency_code: str
    opening_balance: Decimal
    current_balance: Decimal
    is_active: bool
    is_primary: bool
    ifsc_code: Optional[str]
    micr_code: Optional[str]
    branch_name: Optional[str]
    branch_address: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class BankStatementCreate(BaseModel):
    bank_account_id: int
    statement_date: date
    balance_start: Decimal = Field(default=0)
    balance_end: Decimal = Field(default=0)
    notes: Optional[str] = None

class BankStatementResponse(BaseModel):
    id: int
    bank_account_id: int
    statement_date: date
    balance_start: Decimal
    balance_end: Decimal
    total_debit: Decimal
    total_credit: Decimal
    total_entries: int
    status: StatementStatus
    imported_date: Optional[datetime]
    imported_by: Optional[int]
    file_name: Optional[str]
    file_path: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class BankStatementLineCreate(BaseModel):
    statement_id: int
    line_date: date
    amount: Decimal
    balance: Decimal
    description: Optional[str] = None
    reference: Optional[str] = None
    partner_id: Optional[int] = None
    notes: Optional[str] = None

class BankStatementLineResponse(BaseModel):
    id: int
    statement_id: int
    line_date: date
    amount: Decimal
    balance: Decimal
    description: Optional[str]
    reference: Optional[str]
    partner_id: Optional[int]
    payment_id: Optional[int]
    is_reconciled: bool
    reconciled_amount: Decimal
    reconciliation_date: Optional[datetime]
    reconciled_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PaymentMethodCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    payment_type: PaymentMethodType
    requires_bank_account: bool = Field(default=False)
    requires_reference: bool = Field(default=False)
    processing_fee: Decimal = Field(default=0)
    processing_fee_type: str = Field(default="fixed", regex="^(fixed|percentage)$")
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    code: str
    payment_type: PaymentMethodType
    is_active: bool
    requires_bank_account: bool
    requires_reference: bool
    processing_fee: Decimal
    processing_fee_type: str
    description: Optional[str]
    configuration: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PaymentTermCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    days: int = Field(..., ge=0)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    description: Optional[str] = None

class PaymentTermResponse(BaseModel):
    id: int
    name: str
    code: str
    days: int
    discount_days: Optional[int]
    discount_percentage: Optional[Decimal]
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class CashRoundingCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    rounding_method: str = Field(..., regex="^(up|down|half_up|half_down)$")
    rounding_precision: Decimal = Field(..., gt=0)
    description: Optional[str] = None

class CashRoundingResponse(BaseModel):
    id: int
    name: str
    rounding_method: str
    rounding_precision: Decimal
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Bank Accounts
@router.post("/bank-accounts", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    account_data: BankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new bank account"""
    account = BankAccount(**account_data.dict())
    account.current_balance = account.opening_balance
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.get("/bank-accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(
    account_type: Optional[BankAccountType] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_primary: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all bank accounts"""
    query = db.query(BankAccount)
    
    if account_type:
        query = query.filter(BankAccount.account_type == account_type)
    if is_active is not None:
        query = query.filter(BankAccount.is_active == is_active)
    if is_primary is not None:
        query = query.filter(BankAccount.is_primary == is_primary)
    
    return query.all()

@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get specific bank account"""
    account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    return account

# Bank Statements
@router.post("/bank-statements", response_model=BankStatementResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_statement(
    statement_data: BankStatementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new bank statement"""
    # Check if bank account exists
    account = db.query(BankAccount).filter(BankAccount.id == statement_data.bank_account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    
    statement = BankStatement(
        **statement_data.dict(),
        imported_by=current_user.id,
        imported_date=datetime.now()
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    return statement

@router.get("/bank-statements", response_model=List[BankStatementResponse])
async def get_bank_statements(
    bank_account_id: Optional[int] = Query(None),
    status: Optional[StatementStatus] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all bank statements"""
    query = db.query(BankStatement)
    
    if bank_account_id:
        query = query.filter(BankStatement.bank_account_id == bank_account_id)
    if status:
        query = query.filter(BankStatement.status == status)
    if date_from:
        query = query.filter(BankStatement.statement_date >= date_from)
    if date_to:
        query = query.filter(BankStatement.statement_date <= date_to)
    
    return query.order_by(BankStatement.statement_date.desc()).all()

@router.get("/bank-statements/{statement_id}", response_model=BankStatementResponse)
async def get_bank_statement(
    statement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get specific bank statement"""
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank statement not found")
    return statement

# Bank Statement Lines
@router.post("/bank-statement-lines", response_model=BankStatementLineResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_statement_line(
    line_data: BankStatementLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new bank statement line"""
    # Check if statement exists
    statement = db.query(BankStatement).filter(BankStatement.id == line_data.statement_id).first()
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank statement not found")
    
    line = BankStatementLine(**line_data.dict())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line

@router.get("/bank-statement-lines", response_model=List[BankStatementLineResponse])
async def get_bank_statement_lines(
    statement_id: Optional[int] = Query(None),
    is_reconciled: Optional[bool] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all bank statement lines"""
    query = db.query(BankStatementLine)
    
    if statement_id:
        query = query.filter(BankStatementLine.statement_id == statement_id)
    if is_reconciled is not None:
        query = query.filter(BankStatementLine.is_reconciled == is_reconciled)
    if date_from:
        query = query.filter(BankStatementLine.line_date >= date_from)
    if date_to:
        query = query.filter(BankStatementLine.line_date <= date_to)
    
    return query.order_by(BankStatementLine.line_date.desc()).all()

# Payment Methods
@router.post("/payment-methods", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_method(
    method_data: PaymentMethodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new payment method"""
    method = PaymentMethod(**method_data.dict())
    db.add(method)
    db.commit()
    db.refresh(method)
    return method

@router.get("/payment-methods", response_model=List[PaymentMethodResponse])
async def get_payment_methods(
    payment_type: Optional[PaymentMethodType] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all payment methods"""
    query = db.query(PaymentMethod)
    
    if payment_type:
        query = query.filter(PaymentMethod.payment_type == payment_type)
    if is_active is not None:
        query = query.filter(PaymentMethod.is_active == is_active)
    
    return query.all()

# Payment Terms
@router.post("/payment-terms", response_model=PaymentTermResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_term(
    term_data: PaymentTermCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new payment term"""
    term = PaymentTerm(**term_data.dict())
    db.add(term)
    db.commit()
    db.refresh(term)
    return term

@router.get("/payment-terms", response_model=List[PaymentTermResponse])
async def get_payment_terms(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all payment terms"""
    query = db.query(PaymentTerm)
    
    if is_active is not None:
        query = query.filter(PaymentTerm.is_active == is_active)
    
    return query.all()

# Cash Rounding
@router.post("/cash-rounding", response_model=CashRoundingResponse, status_code=status.HTTP_201_CREATED)
async def create_cash_rounding(
    rounding_data: CashRoundingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create new cash rounding rule"""
    rounding = CashRounding(**rounding_data.dict())
    db.add(rounding)
    db.commit()
    db.refresh(rounding)
    return rounding

@router.get("/cash-rounding", response_model=List[CashRoundingResponse])
async def get_cash_rounding_rules(
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get all cash rounding rules"""
    query = db.query(CashRounding)
    
    if is_active is not None:
        query = query.filter(CashRounding.is_active == is_active)
    
    return query.all()

# Bank Statement Import
@router.post("/bank-statements/import")
async def import_bank_statement(
    bank_account_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Import bank statement from file"""
    # Check if bank account exists
    account = db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    
    # This would contain the actual import logic
    # For now, just returning a placeholder response
    return {
        "message": "Bank statement import initiated",
        "bank_account_id": bank_account_id,
        "file_name": file.filename,
        "status": "processing"
    }

# Bank Reconciliation
@router.post("/bank-reconciliation")
async def create_bank_reconciliation(
    bank_account_id: int,
    reconciliation_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_banking"))
):
    """Create bank reconciliation"""
    # Check if bank account exists
    account = db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found")
    
    # This would contain the actual reconciliation logic
    # For now, just returning a placeholder response
    return {
        "message": "Bank reconciliation created",
        "bank_account_id": bank_account_id,
        "reconciliation_date": reconciliation_date,
        "status": "created"
    }

# Banking Statistics
@router.get("/banking-statistics")
async def get_banking_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_banking"))
):
    """Get banking statistics"""
    # This would contain the actual statistics logic
    # For now, just returning placeholder data
    return {
        "total_accounts": 5,
        "active_accounts": 4,
        "total_statements": 12,
        "reconciled_statements": 8,
        "unreconciled_amount": 15000.00,
        "last_reconciliation": "2024-01-15"
    }