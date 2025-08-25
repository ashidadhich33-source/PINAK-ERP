from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class ExpenseHeadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    budget_monthly: Optional[Decimal] = Field(None, ge=0)
    requires_approval: bool = False

class ExpenseHeadCreate(ExpenseHeadBase):
    pass

class ExpenseHeadUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    budget_monthly: Optional[Decimal] = None
    requires_approval: Optional[bool] = None
    active: Optional[bool] = None

class ExpenseHeadResponse(ExpenseHeadBase):
    id: str
    active: bool
    created_at: datetime
    created_by: str
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    date: Optional[date] = None
    head_id: str
    amount: Decimal = Field(..., gt=0)
    mode: str = Field(..., regex="^(cash|bank|online)$")
    payment_mode_id: Optional[str] = None
    reference_no: Optional[str] = None
    vendor_name: Optional[str] = None
    bill_no: Optional[str] = None
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    mode: Optional[str] = None
    payment_mode_id: Optional[str] = None
    reference_no: Optional[str] = None
    vendor_name: Optional[str] = None
    bill_no: Optional[str] = None
    description: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: str
    date: date
    head_id: str
    amount: Decimal
    mode: str
    payment_mode_id: Optional[str]
    reference_no: Optional[str]
    vendor_name: Optional[str]
    bill_no: Optional[str]
    description: Optional[str]
    status: str
    created_by: str
    created_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    
    class Config:
        from_attributes = True

class ExpenseDetailResponse(ExpenseResponse):
    head_name: str
    head_category: str
    payment_mode_name: Optional[str]
    created_by_name: Optional[str]
    approved_by_name: Optional[str]

class ExpenseSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    categories: List[Dict[str, Any]]
    total_expense: float

class CashFlowResponse(BaseModel):
    period_start: date
    period_end: date
    opening_balance: Decimal
    cash_sales: Decimal
    cash_expenses: Decimal
    cash_purchases: Decimal
    total_cash_in: Decimal
    total_cash_out: Decimal
    closing_balance: Decimal
    daily_breakdown: List[Dict[str, Any]]

class BankReconciliationResponse(BaseModel):
    period_start: date
    period_end: date
    bank_collections: Decimal
    bank_expenses: Decimal
    net_bank_balance: Decimal
    supplier_collections: Decimal
    total_card_collections: Decimal

class ExpenseImportResponse(BaseModel):
    success: bool
    imported: int
    errors: List[str]

class ExpenseBulkApprovalRequest(BaseModel):
    expense_ids: List[str]
    notes: Optional[str] = None