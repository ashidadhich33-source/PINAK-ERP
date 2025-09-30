# backend/app/schemas/compliance_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Enums
class ComplianceType(str, Enum):
    GST = "gst"
    TDS = "tds"
    TCS = "tcs"
    E_INVOICE = "e_invoice"
    E_WAYBILL = "e_waybill"

class ComplianceStatus(str, Enum):
    DRAFT = "draft"
    FILED = "filed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# GST Registration Schemas
class GSTRegistrationCreate(BaseModel):
    gst_number: str = Field(..., min_length=15, max_length=15)
    registration_type: str = Field(..., regex="^(regular|composition|casual|non-resident)$")
    registration_date: date
    business_name: str = Field(..., min_length=1, max_length=200)
    business_address: str = Field(..., min_length=1)
    business_type: str = Field(..., min_length=1, max_length=50)
    pan_number: str = Field(..., min_length=10, max_length=10)
    aadhar_number: Optional[str] = Field(None, min_length=12, max_length=12)
    mobile_number: Optional[str] = Field(None, min_length=10, max_length=10)
    email: Optional[str] = Field(None, max_length=100)
    state_code: str = Field(..., min_length=2, max_length=2)
    
    @validator('gst_number')
    def validate_gst_number(cls, v):
        if len(v) != 15:
            raise ValueError('GST number must be exactly 15 characters')
        if not v.isalnum():
            raise ValueError('GST number must contain only alphanumeric characters')
        return v.upper()
    
    @validator('pan_number')
    def validate_pan_number(cls, v):
        if len(v) != 10:
            raise ValueError('PAN number must be exactly 10 characters')
        if not v.isalnum():
            raise ValueError('PAN number must contain only alphanumeric characters')
        return v.upper()

class GSTRegistrationResponse(BaseModel):
    id: int
    company_id: int
    gst_number: str
    registration_type: str
    registration_date: date
    business_name: str
    business_address: str
    business_type: str
    pan_number: str
    aadhar_number: Optional[str]
    mobile_number: Optional[str]
    email: Optional[str]
    state_code: str
    is_active: bool
    suspension_date: Optional[date]
    cancellation_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# GST Return Schemas
class GSTReturnCreate(BaseModel):
    gst_registration_id: int
    return_period: str = Field(..., regex="^\d{4}-\d{2}$")
    return_type: str = Field(..., regex="^(GSTR-1|GSTR-3B|GSTR-9|GSTR-9C)$")
    gst_number: str = Field(..., min_length=15, max_length=15)
    filing_date: date
    due_date: date
    total_sales: Decimal = Field(default=0, ge=0)
    total_purchases: Decimal = Field(default=0, ge=0)
    output_tax: Decimal = Field(default=0, ge=0)
    input_tax: Decimal = Field(default=0, ge=0)
    net_tax: Decimal = Field(default=0)
    interest_amount: Decimal = Field(default=0, ge=0)
    penalty_amount: Decimal = Field(default=0, ge=0)
    total_payable: Decimal = Field(default=0)

class GSTReturnResponse(BaseModel):
    id: int
    company_id: int
    gst_registration_id: int
    return_period: str
    return_type: str
    gst_number: str
    filing_date: date
    due_date: date
    status: str
    total_sales: Decimal
    total_purchases: Decimal
    output_tax: Decimal
    input_tax: Decimal
    net_tax: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    total_payable: Decimal
    acknowledgment_number: Optional[str]
    filing_reference: Optional[str]
    filed_by: Optional[int]
    filed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# GST Payment Schemas
class GSTPaymentCreate(BaseModel):
    gst_registration_id: int
    gst_return_id: Optional[int] = None
    payment_date: date
    payment_amount: Decimal = Field(..., gt=0)
    payment_mode: str = Field(..., regex="^(online|offline|challan)$")
    payment_reference: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    bank_branch: Optional[str] = Field(None, max_length=100)

class GSTPaymentResponse(BaseModel):
    id: int
    company_id: int
    gst_registration_id: int
    gst_return_id: Optional[int]
    payment_date: date
    payment_amount: Decimal
    payment_mode: str
    payment_reference: Optional[str]
    bank_name: Optional[str]
    bank_branch: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# TDS Return Schemas
class TDSReturnCreate(BaseModel):
    return_period: str = Field(..., regex="^\d{4}-\d{2}$")
    return_type: str = Field(..., regex="^(24Q|26Q|27Q|27EQ)$")
    pan_number: str = Field(..., min_length=10, max_length=10)
    filing_date: date
    due_date: date
    total_tds_deducted: Decimal = Field(default=0, ge=0)
    total_tds_deposited: Decimal = Field(default=0, ge=0)
    interest_amount: Decimal = Field(default=0, ge=0)
    penalty_amount: Decimal = Field(default=0, ge=0)
    total_payable: Decimal = Field(default=0)

class TDSReturnResponse(BaseModel):
    id: int
    company_id: int
    return_period: str
    return_type: str
    pan_number: str
    filing_date: date
    due_date: date
    status: str
    total_tds_deducted: Decimal
    total_tds_deposited: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    total_payable: Decimal
    acknowledgment_number: Optional[str]
    filed_by: Optional[int]
    filed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# TCS Return Schemas
class TCSReturnCreate(BaseModel):
    return_period: str = Field(..., regex="^\d{4}-\d{2}$")
    return_type: str = Field(..., regex="^(27EQ)$")
    pan_number: str = Field(..., min_length=10, max_length=10)
    filing_date: date
    due_date: date
    total_tcs_collected: Decimal = Field(default=0, ge=0)
    total_tcs_deposited: Decimal = Field(default=0, ge=0)
    interest_amount: Decimal = Field(default=0, ge=0)
    penalty_amount: Decimal = Field(default=0, ge=0)
    total_payable: Decimal = Field(default=0)

class TCSReturnResponse(BaseModel):
    id: int
    company_id: int
    return_period: str
    return_type: str
    pan_number: str
    filing_date: date
    due_date: date
    status: str
    total_tcs_collected: Decimal
    total_tcs_deposited: Decimal
    interest_amount: Decimal
    penalty_amount: Decimal
    total_payable: Decimal
    acknowledgment_number: Optional[str]
    filed_by: Optional[int]
    filed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# E-Invoice Schemas
class EInvoiceItemCreate(BaseModel):
    item_id: Optional[int] = None
    item_name: str = Field(..., min_length=1, max_length=200)
    hsn_code: Optional[str] = Field(None, min_length=4, max_length=8)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    tax_amount: Decimal = Field(default=0, ge=0)

class EInvoiceCreate(BaseModel):
    invoice_id: int
    invoice_number: str = Field(..., min_length=1, max_length=50)
    invoice_date: date
    customer_id: Optional[int] = None
    customer_gst: Optional[str] = Field(None, min_length=15, max_length=15)
    total_amount: Decimal = Field(..., gt=0)
    tax_amount: Decimal = Field(..., ge=0)
    items: List[EInvoiceItemCreate] = Field(..., min_items=1)

class EInvoiceResponse(BaseModel):
    id: int
    company_id: int
    invoice_id: int
    invoice_number: str
    invoice_date: date
    customer_id: Optional[int]
    customer_gst: Optional[str]
    total_amount: Decimal
    tax_amount: Decimal
    irn: Optional[str]
    qr_code: Optional[str]
    status: str
    ack_number: Optional[str]
    ack_date: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# E-Waybill Schemas
class EWaybillItemCreate(BaseModel):
    item_id: Optional[int] = None
    item_name: str = Field(..., min_length=1, max_length=200)
    hsn_code: Optional[str] = Field(None, min_length=4, max_length=8)
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_price: Decimal = Field(..., gt=0)

class EWaybillCreate(BaseModel):
    waybill_number: str = Field(..., min_length=1, max_length=50)
    waybill_date: date
    invoice_id: Optional[int] = None
    invoice_number: Optional[str] = Field(None, max_length=50)
    invoice_date: Optional[date] = None
    customer_id: Optional[int] = None
    customer_gst: Optional[str] = Field(None, min_length=15, max_length=15)
    total_amount: Decimal = Field(..., gt=0)
    distance: Optional[int] = Field(None, ge=0)
    transport_mode: Optional[str] = Field(None, regex="^(road|rail|air|ship)$")
    vehicle_number: Optional[str] = Field(None, max_length=20)
    driver_name: Optional[str] = Field(None, max_length=100)
    driver_mobile: Optional[str] = Field(None, min_length=10, max_length=10)
    items: List[EWaybillItemCreate] = Field(..., min_items=1)

class EWaybillResponse(BaseModel):
    id: int
    company_id: int
    waybill_number: str
    waybill_date: date
    invoice_id: Optional[int]
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    customer_id: Optional[int]
    customer_gst: Optional[str]
    total_amount: Decimal
    ewb_number: Optional[str]
    status: str
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    distance: Optional[int]
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    driver_name: Optional[str]
    driver_mobile: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Compliance Settings Schemas
class ComplianceSettingsCreate(BaseModel):
    gst_auto_filing: bool = False
    gst_auto_payment: bool = False
    gst_notification_days: int = Field(default=7, ge=1, le=30)
    tds_auto_filing: bool = False
    tds_auto_payment: bool = False
    tds_notification_days: int = Field(default=7, ge=1, le=30)
    tcs_auto_filing: bool = False
    tcs_auto_payment: bool = False
    tcs_notification_days: int = Field(default=7, ge=1, le=30)
    e_invoice_auto_generation: bool = False
    e_invoice_threshold: Decimal = Field(default=50000, ge=0)
    e_waybill_auto_generation: bool = False
    e_waybill_threshold: Decimal = Field(default=50000, ge=0)

class ComplianceSettingsResponse(BaseModel):
    id: int
    company_id: int
    gst_auto_filing: bool
    gst_auto_payment: bool
    gst_notification_days: int
    tds_auto_filing: bool
    tds_auto_payment: bool
    tds_notification_days: int
    tcs_auto_filing: bool
    tcs_auto_payment: bool
    tcs_notification_days: int
    e_invoice_auto_generation: bool
    e_invoice_threshold: Decimal
    e_waybill_auto_generation: bool
    e_waybill_threshold: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Compliance Alert Schemas
class ComplianceAlertResponse(BaseModel):
    id: int
    company_id: int
    alert_type: str
    compliance_type: str
    title: str
    message: str
    due_date: Optional[date]
    priority: str
    status: str
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Compliance Log Schemas
class ComplianceLogResponse(BaseModel):
    id: int
    company_id: int
    compliance_type: str
    action: str
    reference_id: Optional[int]
    reference_type: Optional[str]
    status: str
    message: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Compliance Dashboard Schemas
class ComplianceDashboardResponse(BaseModel):
    company_id: int
    gst_summary: Dict[str, Any]
    tds_summary: Dict[str, Any]
    tcs_summary: Dict[str, Any]
    e_invoice_summary: Dict[str, Any]
    e_waybill_summary: Dict[str, Any]
    active_alerts: List[ComplianceAlertResponse]
    upcoming_due_dates: List[Dict[str, Any]]
    recent_activities: List[ComplianceLogResponse]
    
    class Config:
        from_attributes = True