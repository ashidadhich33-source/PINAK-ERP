# backend/app/api/endpoints/banking.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from app.database import get_db
from app.models.accounting.banking import BankAccount, BankStatement, BankReconciliation
from app.models.core.user import User
from app.core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class BankAccountCreate(BaseModel):
    account_name: str
    account_number: str
    bank_name: str
    ifsc_code: str
    company_id: int

class BankAccountResponse(BaseModel):
    id: int
    account_name: str
    account_number: str
    bank_name: str
    ifsc_code: str
    current_balance: Decimal
    is_active: bool

    class Config:
        from_attributes = True

class BankTransactionCreate(BaseModel):
    bank_account_id: int
    transaction_date: date
    amount: Decimal
    transaction_type: str  # debit or credit
    description: str
    reference: Optional[str] = None

class BankTransactionResponse(BaseModel):
    id: int
    bank_account_id: int
    transaction_date: date
    amount: Decimal
    transaction_type: str
    description: str
    reference: Optional[str]
    balance_after: Decimal

    class Config:
        from_attributes = True

@router.post("/bank-accounts", response_model=BankAccountResponse)
async def create_bank_account(
    account_data: BankAccountCreate,
    current_user: User = Depends(require_permission("banking.create")),
    db: Session = Depends(get_db)
):
    """Create a new bank account"""
    
    # Check if account number already exists
    existing_account = db.query(BankAccount).filter(
        BankAccount.account_number == account_data.account_number,
        BankAccount.company_id == account_data.company_id
    ).first()
    
    if existing_account:
        raise HTTPException(
            status_code=400,
            detail="Bank account with this number already exists"
        )
    
    # Create bank account
    bank_account = BankAccount(
        account_name=account_data.account_name,
        account_number=account_data.account_number,
        bank_name=account_data.bank_name,
        ifsc_code=account_data.ifsc_code,
        company_id=account_data.company_id,
        created_by=current_user.id
    )
    
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    
    return bank_account

@router.get("/bank-accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(
    company_id: int,
    current_user: User = Depends(require_permission("banking.view")),
    db: Session = Depends(get_db)
):
    """Get bank accounts for a company"""
    
    accounts = db.query(BankAccount).filter(
        BankAccount.company_id == company_id
    ).all()
    
    return accounts

@router.post("/bank-transactions", response_model=BankTransactionResponse)
async def create_bank_transaction(
    transaction_data: BankTransactionCreate,
    current_user: User = Depends(require_permission("banking.create")),
    db: Session = Depends(get_db)
):
    """Create a new bank transaction"""
    
    # Get bank account
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == transaction_data.bank_account_id
    ).first()
    
    if not bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Create transaction
    transaction = BankTransaction(
        bank_account_id=transaction_data.bank_account_id,
        transaction_date=transaction_data.transaction_date,
        amount=transaction_data.amount,
        transaction_type=transaction_data.transaction_type,
        description=transaction_data.description,
        reference=transaction_data.reference,
        created_by=current_user.id
    )
    
    db.add(transaction)
    
    # Update bank account balance
    if transaction_data.transaction_type == "credit":
        bank_account.current_balance += transaction_data.amount
    else:
        bank_account.current_balance -= transaction_data.amount
    
    db.commit()
    db.refresh(transaction)
    
    # Set balance after transaction
    transaction.balance_after = bank_account.current_balance
    
    return transaction

@router.get("/bank-transactions", response_model=List[BankTransactionResponse])
async def get_bank_transactions(
    bank_account_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_permission("banking.view")),
    db: Session = Depends(get_db)
):
    """Get bank transactions for an account"""
    
    query = db.query(BankTransaction).filter(
        BankTransaction.bank_account_id == bank_account_id
    )
    
    if start_date:
        query = query.filter(BankTransaction.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(BankTransaction.transaction_date <= end_date)
    
    transactions = query.order_by(BankTransaction.transaction_date.desc()).all()
    
    return transactions

@router.get("/bank-reconciliation/{bank_account_id}")
async def get_bank_reconciliation(
    bank_account_id: int,
    reconciliation_date: date,
    current_user: User = Depends(require_permission("banking.view")),
    db: Session = Depends(get_db)
):
    """Get bank reconciliation data"""
    
    # Get bank account
    bank_account = db.query(BankAccount).filter(
        BankAccount.id == bank_account_id
    ).first()
    
    if not bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Get transactions up to reconciliation date
    transactions = db.query(BankTransaction).filter(
        BankTransaction.bank_account_id == bank_account_id,
        BankTransaction.transaction_date <= reconciliation_date
    ).all()
    
    # Calculate reconciled balance
    reconciled_balance = sum(
        t.amount if t.transaction_type == "credit" else -t.amount
        for t in transactions
    )
    
    return {
        "bank_account": {
            "id": bank_account.id,
            "account_name": bank_account.account_name,
            "account_number": bank_account.account_number
        },
        "reconciliation_date": reconciliation_date,
        "reconciled_balance": float(reconciled_balance),
        "transactions_count": len(transactions)
    }