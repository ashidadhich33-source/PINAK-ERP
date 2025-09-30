# backend/app/schemas/banking_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Enums
class BankAccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    FIXED_DEPOSIT = "fixed_deposit"
    RECURRING_DEPOSIT = "recurring_deposit"
    LOAN = "loan"
    CREDIT_CARD = "credit_card"

class PaymentMethodType(str, Enum):
    CASH = "cash"
    CHEQUE = "cheque"
    DD = "dd"  # Demand Draft
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"
    UPI = "upi"
    CARD = "card"
    ONLINE = "online"
    WALLET = "wallet"

class StatementStatus(str, Enum):
    DRAFT = "draft"
    IMPORTED = "imported"
    RECONCILED = "reconciled"
    CLOSED = "closed"

class ReconciliationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"

# Bank Account Schemas
class BankAccountCreate(BaseModel):
    account_name: str = Field(..., min_length=3, max_length=100)
    account_number: str = Field(..., min_length=5, max_length=50)
    bank_name: str = Field(..., min_length=3, max_length=100)
    bank_code: Optional[str] = Field(None, max_length=20)
    account_type: BankAccountType
    currency_code: str = Field(default="INR", max_length=3)
    opening_balance: Decimal = Field(default=0)
    ifsc_code: Optional[str] = Field(None, max_length=11)
    micr_code: Optional[str] = Field(None, max_length=9)
    branch_name: Optional[str] = Field(None, max_length=100)
    branch_address: Optional[str] = Field(None, max_length=500)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('ifsc_code')
    def validate_ifsc_code(cls, v):
        if v and len(v) != 11:
            raise ValueError('IFSC code must be exactly 11 characters')
        return v.upper() if v else v
    
    @validator('micr_code')
    def validate_micr_code(cls, v):
        if v and len(v) != 9:
            raise ValueError('MICR code must be exactly 9 characters')
        return v

class BankAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, min_length=3, max_length=100)
    bank_name: Optional[str] = Field(None, min_length=3, max_length=100)
    bank_code: Optional[str] = Field(None, max_length=20)
    account_type: Optional[BankAccountType] = None
    currency_code: Optional[str] = Field(None, max_length=3)
    ifsc_code: Optional[str] = Field(None, max_length=11)
    micr_code: Optional[str] = Field(None, max_length=9)
    branch_name: Optional[str] = Field(None, max_length=100)
    branch_address: Optional[str] = Field(None, max_length=500)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None

class BankAccountResponse(BaseModel):
    id: int
    company_id: int
    account_name: str
    account_number: str
    bank_name: str
    bank_code: Optional[str]
    account_type: str
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
        from_attributes = True

# Bank Statement Schemas
class BankStatementCreate(BaseModel):
    bank_account_id: int
    statement_date: date
    balance_start: Decimal = Field(default=0)
    balance_end: Decimal = Field(default=0)
    notes: Optional[str] = Field(None, max_length=1000)

class BankStatementUpdate(BaseModel):
    statement_date: Optional[date] = None
    balance_start: Optional[Decimal] = None
    balance_end: Optional[Decimal] = None
    status: Optional[StatementStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)

class BankStatementResponse(BaseModel):
    id: int
    company_id: int
    bank_account_id: int
    statement_date: date
    balance_start: Decimal
    balance_end: Decimal
    total_debit: Decimal
    total_credit: Decimal
    total_entries: int
    status: str
    imported_date: Optional[datetime]
    imported_by: Optional[int]
    file_name: Optional[str]
    file_path: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Bank Statement Line Schemas
class BankStatementLineCreate(BaseModel):
    statement_id: int
    line_date: date
    amount: Decimal
    balance: Decimal
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    partner_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)

class BankStatementLineUpdate(BaseModel):
    line_date: Optional[date] = None
    amount: Optional[Decimal] = None
    balance: Optional[Decimal] = None
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    partner_id: Optional[int] = None
    is_reconciled: Optional[bool] = None
    reconciled_amount: Optional[Decimal] = None
    reconciliation_date: Optional[datetime] = None
    reconciled_by: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)

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
        from_attributes = True

# Payment Method Schemas
class PaymentMethodCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    payment_type: PaymentMethodType
    requires_bank_account: bool = Field(default=False)
    requires_reference: bool = Field(default=False)
    processing_fee: Decimal = Field(default=0, ge=0)
    processing_fee_type: str = Field(default="fixed", regex="^(fixed|percentage)$")
    description: Optional[str] = Field(None, max_length=500)
    configuration: Optional[Dict[str, Any]] = None

class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    payment_type: Optional[PaymentMethodType] = None
    requires_bank_account: Optional[bool] = None
    requires_reference: Optional[bool] = None
    processing_fee: Optional[Decimal] = Field(None, ge=0)
    processing_fee_type: Optional[str] = Field(None, regex="^(fixed|percentage)$")
    description: Optional[str] = Field(None, max_length=500)
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class PaymentMethodResponse(BaseModel):
    id: int
    company_id: int
    name: str
    code: str
    payment_type: str
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
        from_attributes = True

# Payment Term Schemas
class PaymentTermCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    days: int = Field(..., ge=0)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=500)

class PaymentTermUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    days: Optional[int] = Field(None, ge=0)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class PaymentTermResponse(BaseModel):
    id: int
    company_id: int
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
        from_attributes = True

# Cash Rounding Schemas
class CashRoundingCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    rounding_method: str = Field(..., regex="^(up|down|half_up|half_down)$")
    rounding_precision: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)

class CashRoundingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    rounding_method: Optional[str] = Field(None, regex="^(up|down|half_up|half_down)$")
    rounding_precision: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CashRoundingResponse(BaseModel):
    id: int
    company_id: int
    name: str
    rounding_method: str
    rounding_precision: Decimal
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Bank Reconciliation Schemas
class BankReconciliationCreate(BaseModel):
    bank_account_id: int
    reconciliation_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_debits: Decimal = Field(default=0, ge=0)
    total_credits: Decimal = Field(default=0, ge=0)
    difference_amount: Decimal = Field(default=0)
    status: ReconciliationStatus = Field(default=ReconciliationStatus.PENDING)
    notes: Optional[str] = Field(None, max_length=1000)

class BankReconciliationUpdate(BaseModel):
    reconciliation_date: Optional[date] = None
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    total_debits: Optional[Decimal] = Field(None, ge=0)
    total_credits: Optional[Decimal] = Field(None, ge=0)
    difference_amount: Optional[Decimal] = None
    status: Optional[ReconciliationStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)

class BankReconciliationResponse(BaseModel):
    id: int
    company_id: int
    bank_account_id: int
    reconciliation_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_debits: Decimal
    total_credits: Decimal
    difference_amount: Decimal
    status: str
    total_items: int
    total_adjustment_value: Decimal
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Banking Statistics Schemas
class BankingStatisticsResponse(BaseModel):
    total_accounts: int
    active_accounts: int
    total_statements: int
    reconciled_statements: int
    unreconciled_amount: Decimal
    last_reconciliation: Optional[date]
    total_balance: Decimal
    account_wise_balance: List[Dict[str, Any]]
    recent_transactions: List[Dict[str, Any]]
    pending_reconciliations: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Banking Dashboard Schemas
class BankingDashboardResponse(BaseModel):
    company_id: int
    summary: BankingStatisticsResponse
    bank_accounts: List[BankAccountResponse]
    recent_statements: List[BankStatementResponse]
    active_reconciliations: List[BankReconciliationResponse]
    payment_methods: List[PaymentMethodResponse]
    payment_terms: List[PaymentTermResponse]
    cash_rounding_rules: List[CashRoundingResponse]
    
    class Config:
        from_attributes = True