"""
Core System Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING = "pending"


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    UPI = "upi"
    CARD = "card"
    DIGITAL_WALLET = "digital_wallet"
    OTHER = "other"


# Company Schemas
class CompanyCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    company_code: Optional[str] = Field(None, max_length=50)
    legal_name: Optional[str] = Field(None, max_length=200)
    registration_number: Optional[str] = Field(None, max_length=50)
    gst_number: Optional[str] = Field(None, max_length=15)
    pan_number: Optional[str] = Field(None, max_length=10)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="India", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    currency: str = Field(default="INR", max_length=3)
    timezone: str = Field(default="Asia/Kolkata")
    financial_year_start: date
    financial_year_end: date
    logo_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @validator('financial_year_end')
    def validate_financial_year(cls, v, values):
        if 'financial_year_start' in values and v <= values['financial_year_start']:
            raise ValueError('financial_year_end must be after financial_year_start')
        return v


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    company_code: Optional[str] = None
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    financial_year_start: Optional[date] = None
    financial_year_end: Optional[date] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    company_code: Optional[str] = None
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    currency: str
    timezone: str
    financial_year_start: date
    financial_year_end: date
    logo_url: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Staff Schemas
class StaffCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="India", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    date_of_birth: Optional[date] = None
    date_of_joining: date
    date_of_leaving: Optional[date] = None
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)
    salary: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=1000)


class StaffUpdate(BaseModel):
    employee_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: Optional[date] = None
    date_of_leaving: Optional[date] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    salary: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class StaffResponse(BaseModel):
    id: int
    company_id: int
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: date
    date_of_leaving: Optional[date] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    salary: Optional[Decimal] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Expense Schemas
class ExpenseCreate(BaseModel):
    expense_number: str = Field(..., min_length=1, max_length=100)
    expense_date: date
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    vendor_id: Optional[int] = None
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    is_billable: bool = Field(default=False)
    is_reimbursable: bool = Field(default=False)
    receipt_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None


class ExpenseUpdate(BaseModel):
    expense_number: Optional[str] = None
    expense_date: Optional[date] = None
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = None
    vendor_id: Optional[int] = None
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    is_billable: Optional[bool] = None
    is_reimbursable: Optional[bool] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    company_id: int
    expense_number: str
    expense_date: date
    category: str
    description: str
    amount: Decimal
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    vendor_id: Optional[int] = None
    employee_id: Optional[int] = None
    project_id: Optional[int] = None
    is_billable: bool
    is_reimbursable: bool
    receipt_url: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    payment_number: str = Field(..., min_length=1, max_length=100)
    payment_date: date
    payment_type: str = Field(..., regex="^(receipt|payment|transfer)$")
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    reference_number: Optional[str] = Field(None, max_length=100)
    bank_account_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    counterparty_type: Optional[str] = Field(None, regex="^(customer|supplier|employee|other)$")
    description: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    is_reconciled: bool = Field(default=False)
    reconciled_date: Optional[date] = None


class PaymentUpdate(BaseModel):
    payment_number: Optional[str] = None
    payment_date: Optional[date] = None
    payment_type: Optional[str] = None
    amount: Optional[Decimal] = None
    payment_method: Optional[PaymentMethod] = None
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    counterparty_type: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: Optional[bool] = None
    reconciled_date: Optional[date] = None
    status: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    company_id: int
    payment_number: str
    payment_date: date
    payment_type: str
    amount: Decimal
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    counterparty_id: Optional[int] = None
    counterparty_type: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_reconciled: bool
    reconciled_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# GST Schemas
class GSTCreate(BaseModel):
    gst_number: str = Field(..., min_length=15, max_length=15)
    registration_type: str = Field(..., regex="^(regular|composition|casual|non_resident)$")
    registration_date: date
    business_nature: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=6, max_length=6)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=1000)


class GSTUpdate(BaseModel):
    registration_type: Optional[str] = None
    registration_date: Optional[date] = None
    business_nature: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class GSTResponse(BaseModel):
    id: int
    company_id: int
    gst_number: str
    registration_type: str
    registration_date: date
    business_nature: str
    address: str
    city: str
    state: str
    postal_code: str
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Discount Management Schemas
class DiscountCreate(BaseModel):
    discount_name: str = Field(..., min_length=1, max_length=100)
    discount_type: str = Field(..., regex="^(percentage|fixed|buy_x_get_y|volume)$")
    discount_value: Decimal = Field(..., ge=0)
    minimum_amount: Decimal = Field(default=0, ge=0)
    maximum_discount: Optional[Decimal] = Field(None, ge=0)
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool = Field(default=True)
    applicable_items: Optional[List[int]] = None
    applicable_customers: Optional[List[int]] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    usage_count: int = Field(default=0, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class DiscountUpdate(BaseModel):
    discount_name: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    minimum_amount: Optional[Decimal] = None
    maximum_discount: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    applicable_items: Optional[List[int]] = None
    applicable_customers: Optional[List[int]] = None
    usage_limit: Optional[int] = None
    notes: Optional[str] = None


class DiscountResponse(BaseModel):
    id: int
    company_id: int
    discount_name: str
    discount_type: str
    discount_value: Decimal
    minimum_amount: Decimal
    maximum_discount: Optional[Decimal] = None
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool
    applicable_items: Optional[List[int]] = None
    applicable_customers: Optional[List[int]] = None
    usage_limit: Optional[int] = None
    usage_count: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Report Studio Schemas
class ReportCreate(BaseModel):
    report_name: str = Field(..., min_length=1, max_length=100)
    report_type: str = Field(..., regex="^(financial|operational|analytical|custom)$")
    description: Optional[str] = Field(None, max_length=500)
    query: str = Field(..., min_length=1, max_length=10000)
    parameters: Optional[Dict[str, Any]] = None
    is_public: bool = Field(default=False)
    is_active: bool = Field(default=True)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None


class ReportUpdate(BaseModel):
    report_name: Optional[str] = None
    report_type: Optional[str] = None
    description: Optional[str] = None
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class ReportResponse(BaseModel):
    id: int
    company_id: int
    report_name: str
    report_type: str
    description: Optional[str] = None
    query: str
    parameters: Optional[Dict[str, Any]] = None
    is_public: bool
    is_active: bool
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# System Integration Schemas
class IntegrationCreate(BaseModel):
    integration_name: str = Field(..., min_length=1, max_length=100)
    integration_type: str = Field(..., regex="^(api|webhook|file_import|file_export|database)$")
    description: Optional[str] = Field(None, max_length=500)
    configuration: Dict[str, Any] = Field(..., description="Integration configuration")
    is_active: bool = Field(default=True)
    is_automated: bool = Field(default=False)
    schedule: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class IntegrationUpdate(BaseModel):
    integration_name: Optional[str] = None
    integration_type: Optional[str] = None
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_automated: Optional[bool] = None
    schedule: Optional[str] = None
    notes: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: int
    company_id: int
    integration_name: str
    integration_type: str
    description: Optional[str] = None
    configuration: Dict[str, Any]
    is_active: bool
    is_automated: bool
    schedule: Optional[str] = None
    notes: Optional[str] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Backup Schemas
class BackupCreate(BaseModel):
    backup_name: str = Field(..., min_length=1, max_length=100)
    backup_type: str = Field(..., regex="^(full|incremental|differential)$")
    description: Optional[str] = Field(None, max_length=500)
    include_data: bool = Field(default=True)
    include_files: bool = Field(default=True)
    compression: bool = Field(default=True)
    encryption: bool = Field(default=False)
    password: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class BackupUpdate(BaseModel):
    backup_name: Optional[str] = None
    backup_type: Optional[str] = None
    description: Optional[str] = None
    include_data: Optional[bool] = None
    include_files: Optional[bool] = None
    compression: Optional[bool] = None
    encryption: Optional[bool] = None
    password: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class BackupResponse(BaseModel):
    id: int
    company_id: int
    backup_name: str
    backup_type: str
    description: Optional[str] = None
    include_data: bool
    include_files: bool
    compression: bool
    encryption: bool
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# System Settings Schemas
class SystemSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    number_format: Optional[str] = None
    decimal_places: Optional[int] = None
    gst_enabled: Optional[bool] = None
    loyalty_enabled: Optional[bool] = None
    whatsapp_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    backup_enabled: Optional[bool] = None
    backup_frequency: Optional[str] = None
    backup_retention: Optional[int] = None
    auto_backup: Optional[bool] = None
    notification_settings: Optional[Dict[str, Any]] = None
    integration_settings: Optional[Dict[str, Any]] = None
    security_settings: Optional[Dict[str, Any]] = None


class SystemSettingsResponse(BaseModel):
    company_name: str
    currency: str
    timezone: str
    date_format: str
    time_format: str
    number_format: str
    decimal_places: int
    gst_enabled: bool
    loyalty_enabled: bool
    whatsapp_enabled: bool
    email_enabled: bool
    backup_enabled: bool
    backup_frequency: str
    backup_retention: int
    auto_backup: bool
    notification_settings: Dict[str, Any]
    integration_settings: Dict[str, Any]
    security_settings: Dict[str, Any]
    updated_at: datetime

    class Config:
        from_attributes = True