# backend/app/api/endpoints/expenses.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from app.database import get_db
from app.models.core.expense import Expense, ExpenseHead
from app.models.core.user import User
from app.core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class ExpenseCreate(BaseModel):
    expense_date: date
    amount: Decimal
    description: str
    category_id: int
    company_id: int
    payment_method: str = "cash"

class ExpenseResponse(BaseModel):
    id: int
    expense_date: date
    amount: Decimal
    description: str
    category_id: int
    payment_method: str
    status: str

    class Config:
        from_attributes = True

@router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(require_permission("expenses.create")),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    
    # Create expense
    expense = Expense(
        expense_date=expense_data.expense_date,
        amount=expense_data.amount,
        description=expense_data.description,
        category_id=expense_data.category_id,
        company_id=expense_data.company_id,
        payment_method=expense_data.payment_method,
        created_by=current_user.id
    )
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense

@router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    company_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_permission("expenses.view")),
    db: Session = Depends(get_db)
):
    """Get expenses for a company"""
    
    query = db.query(Expense).filter(Expense.company_id == company_id)
    
    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    
    expenses = query.all()
    return expenses

@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(require_permission("expenses.view")),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return expense

@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseCreate,
    current_user: User = Depends(require_permission("expenses.update")),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Update expense fields
    expense.expense_date = expense_data.expense_date
    expense.amount = expense_data.amount
    expense.description = expense_data.description
    expense.category_id = expense_data.category_id
    expense.payment_method = expense_data.payment_method
    expense.updated_by = current_user.id
    
    db.commit()
    db.refresh(expense)
    
    return expense

@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(require_permission("expenses.delete")),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Soft delete
    expense.is_active = False
    expense.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Expense deleted successfully"}

@router.get("/expense-categories", response_model=List[dict])
async def get_expense_categories(
    company_id: int,
    current_user: User = Depends(require_permission("expenses.view")),
    db: Session = Depends(get_db)
):
    """Get expense categories for a company"""
    
    categories = db.query(ExpenseCategory).filter(
        ExpenseCategory.company_id == company_id,
        ExpenseCategory.is_active == True
    ).all()
    
    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active
        }
        for category in categories
    ]