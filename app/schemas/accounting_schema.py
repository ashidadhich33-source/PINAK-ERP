"""
Accounting Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class JournalEntryStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


# Chart of Accounts Schemas
class ChartOfAccountCreate(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: AccountType
    parent_account_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    is_system_account: bool = Field(default=False)
    opening_balance: Decimal = Field(default=0)
    balance_type: str = Field(default="debit", regex="^(debit|credit)$")
    gst_applicable: bool = Field(default=False)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=10)
    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    ifsc_code: Optional[str] = Field(None, max_length=11)


class ChartOfAccountUpdate(BaseModel):
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[AccountType] = None
    parent_account_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_system_account: Optional[bool] = None
    opening_balance: Optional[Decimal] = None
    balance_type: Optional[str] = None
    gst_applicable: Optional[bool] = None
    gst_rate: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None


class ChartOfAccountResponse(BaseModel):
    id: int
    company_id: int
    account_code: str
    account_name: str
    account_type: AccountType
    parent_account_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool
    is_system_account: bool
    opening_balance: Decimal
    balance_type: str
    gst_applicable: bool
    gst_rate: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None
    current_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryCreate(BaseModel):
    entry_date: date
    narration: Optional[str] = Field(None, max_length=500)
    reference_number: Optional[str] = Field(None, max_length=100)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)
    entry_items: List[Dict[str, Any]] = Field(..., min_items=2, description="List of journal entry items")


class JournalEntryItemCreate(BaseModel):
    account_id: int
    debit_amount: Decimal = Field(default=0, ge=0)
    credit_amount: Decimal = Field(default=0, ge=0)
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    
    @validator('debit_amount', 'credit_amount')
    def validate_amounts(cls, v, values):
        if v < 0:
            raise ValueError('Amounts cannot be negative')
        return v


class JournalEntryUpdate(BaseModel):
    entry_date: Optional[date] = None
    narration: Optional[str] = None
    reference_number: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[JournalEntryStatus] = None


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
    status: JournalEntryStatus
    is_reversed: bool
    reversed_entry_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Trial Balance Schemas
class TrialBalanceCreate(BaseModel):
    balance_date: date
    financial_year_id: int
    notes: Optional[str] = Field(None, max_length=500)


class TrialBalanceUpdate(BaseModel):
    balance_date: Optional[date] = None
    financial_year_id: Optional[int] = None
    notes: Optional[str] = None


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
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Balance Sheet Schemas
class BalanceSheetCreate(BaseModel):
    sheet_date: date
    financial_year_id: int
    notes: Optional[str] = Field(None, max_length=500)


class BalanceSheetUpdate(BaseModel):
    sheet_date: Optional[date] = None
    financial_year_id: Optional[int] = None
    notes: Optional[str] = None


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
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Profit & Loss Statement Schemas
class ProfitLossStatementCreate(BaseModel):
    statement_date: date
    financial_year_id: int
    from_date: date
    to_date: date
    notes: Optional[str] = Field(None, max_length=500)


class ProfitLossStatementUpdate(BaseModel):
    statement_date: Optional[date] = None
    financial_year_id: Optional[int] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    notes: Optional[str] = None


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
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Account Balance Schemas
class AccountBalanceCreate(BaseModel):
    account_id: int
    financial_year_id: int
    balance_date: date
    debit_balance: Decimal = Field(default=0, ge=0)
    credit_balance: Decimal = Field(default=0, ge=0)
    opening_balance: Decimal = Field(default=0)


class AccountBalanceUpdate(BaseModel):
    debit_balance: Optional[Decimal] = None
    credit_balance: Optional[Decimal] = None
    opening_balance: Optional[Decimal] = None


class AccountBalanceResponse(BaseModel):
    id: int
    account_id: int
    financial_year_id: int
    balance_date: date
    debit_balance: Decimal
    credit_balance: Decimal
    opening_balance: Decimal
    current_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Financial Year Schemas
class FinancialYearCreate(BaseModel):
    year_name: str = Field(..., min_length=4, max_length=20)
    start_date: date
    end_date: date
    is_active: bool = Field(default=False)
    is_closed: bool = Field(default=False)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class FinancialYearUpdate(BaseModel):
    year_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    is_closed: Optional[bool] = None
    notes: Optional[str] = None


class FinancialYearResponse(BaseModel):
    id: int
    company_id: int
    year_name: str
    start_date: date
    end_date: date
    is_active: bool
    is_closed: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Banking Schemas
class BankAccountCreate(BaseModel):
    account_name: str = Field(..., min_length=1, max_length=200)
    bank_name: str = Field(..., min_length=1, max_length=100)
    account_number: str = Field(..., min_length=1, max_length=50)
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    branch_name: Optional[str] = Field(None, max_length=100)
    account_type: str = Field(..., regex="^(savings|current|fixed|recurring)$")
    opening_balance: Decimal = Field(default=0)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=500)


class BankAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    opening_balance: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class BankAccountResponse(BaseModel):
    id: int
    company_id: int
    account_name: str
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: Optional[str] = None
    account_type: str
    opening_balance: Decimal
    current_balance: Decimal
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Bank Transaction Schemas
class BankTransactionCreate(BaseModel):
    bank_account_id: int
    transaction_date: date
    transaction_type: str = Field(..., regex="^(debit|credit)$")
    amount: Decimal = Field(..., gt=0)
    reference_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    balance_after: Optional[Decimal] = None
    is_reconciled: bool = Field(default=False)
    reconciled_date: Optional[date] = None


class BankTransactionUpdate(BaseModel):
    transaction_date: Optional[date] = None
    transaction_type: Optional[str] = None
    amount: Optional[Decimal] = None
    reference_number: Optional[str] = None
    description: Optional[str] = None
    balance_after: Optional[Decimal] = None
    is_reconciled: Optional[bool] = None
    reconciled_date: Optional[date] = None


class BankTransactionResponse(BaseModel):
    id: int
    bank_account_id: int
    transaction_date: date
    transaction_type: str
    amount: Decimal
    reference_number: Optional[str] = None
    description: Optional[str] = None
    balance_after: Optional[Decimal] = None
    is_reconciled: bool
    reconciled_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Advanced Reporting Schemas
class FinancialReportRequest(BaseModel):
    report_type: str = Field(..., regex="^(balance_sheet|profit_loss|cash_flow|trial_balance|aged_receivables|aged_payables)$")
    financial_year_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    include_zero_balances: bool = Field(default=False)
    group_by: Optional[str] = Field(None, regex="^(account_type|parent_account|none)$")
    format: str = Field(default="json", regex="^(json|pdf|excel|csv)$")


class FinancialReportResponse(BaseModel):
    report_type: str
    financial_year_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    generated_at: datetime
    data: Dict[str, Any]
    summary: Dict[str, Any]
    file_path: Optional[str] = None


# Accounting Analytics Schemas
class AccountingAnalyticsResponse(BaseModel):
    total_assets: Decimal
    total_liabilities: Decimal
    total_equity: Decimal
    net_profit: Decimal
    total_income: Decimal
    total_expenses: Decimal
    cash_flow: Decimal
    debt_to_equity_ratio: Decimal
    current_ratio: Decimal
    quick_ratio: Decimal
    gross_profit_margin: Decimal
    net_profit_margin: Decimal
    return_on_assets: Decimal
    return_on_equity: Decimal
    monthly_trends: List[Dict[str, Any]]
    top_accounts: List[Dict[str, Any]]
    aging_analysis: Dict[str, Any]


# Journal Entry Reversal Schema
class JournalEntryReversalRequest(BaseModel):
    original_entry_id: int
    reversal_date: date
    reversal_reason: str = Field(..., min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)


class JournalEntryReversalResponse(BaseModel):
    original_entry_id: int
    reversal_entry_id: int
    reversal_date: date
    reversal_reason: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True