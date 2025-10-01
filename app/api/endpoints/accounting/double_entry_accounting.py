# backend/app/api/endpoints/double_entry_accounting.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.accounting.double_entry_accounting import JournalEntry, JournalEntryLine, Account
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class JournalEntryCreate(BaseModel):
    date: date
    reference: str
    description: str
    company_id: int
    lines: List[dict]

class JournalEntryResponse(BaseModel):
    id: int
    date: date
    reference: str
    description: str
    total_debit: Decimal
    total_credit: Decimal
    is_balanced: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/journal-entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry_data: JournalEntryCreate,
    current_user: User = Depends(require_permission("accounting.create")),
    db: Session = Depends(get_db)
):
    """Create a new journal entry"""
    
    # Create journal entry
    journal_entry = JournalEntry(
        date=entry_data.date,
        reference=entry_data.reference,
        description=entry_data.description,
        company_id=entry_data.company_id,
        created_by=current_user.id
    )
    
    db.add(journal_entry)
    db.flush()
    
    # Add journal entry lines
    total_debit = Decimal('0')
    total_credit = Decimal('0')
    
    for line_data in entry_data.lines:
        line = JournalEntryLine(
            journal_entry_id=journal_entry.id,
            account_id=line_data['account_id'],
            debit=line_data.get('debit', 0),
            credit=line_data.get('credit', 0),
            description=line_data.get('description', ''),
            created_by=current_user.id
        )
        db.add(line)
        
        total_debit += line.debit
        total_credit += line.credit
    
    # Check if entry is balanced
    journal_entry.is_balanced = total_debit == total_credit
    
    db.commit()
    db.refresh(journal_entry)
    
    return journal_entry

@router.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get journal entries"""
    
    entries = db.query(JournalEntry).offset(skip).limit(limit).all()
    return entries

@router.get("/journal-entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: int,
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get a specific journal entry"""
    
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    return entry

@router.get("/accounts", response_model=List[dict])
async def get_accounts(
    current_user: User = Depends(require_permission("accounting.view")),
    db: Session = Depends(get_db)
):
    """Get chart of accounts"""
    
    accounts = db.query(Account).all()
    return [
        {
            "id": account.id,
            "code": account.code,
            "name": account.name,
            "type": account.type,
            "balance": account.balance
        }
        for account in accounts
    ]