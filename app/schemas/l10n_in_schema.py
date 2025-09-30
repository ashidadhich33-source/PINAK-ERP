"""
Indian Localization Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class GSTRegistrationType(str, Enum):
    REGULAR = "regular"
    COMPOSITION = "composition"
    CASUAL = "casual"
    NON_RESIDENT = "non_resident"


class TDSType(str, Enum):
    TDS = "tds"
    TCS = "tcs"


class EInvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    GENERATED = "generated"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


# GST Tax Structure Schemas
class GSTTaxStructureCreate(BaseModel):
    tax_name: str = Field(..., min_length=1, max_length=100)
    cgst_rate: Decimal = Field(..., ge=0, le=100)
    sgst_rate: Decimal = Field(..., ge=0, le=100)
    igst_rate: Decimal = Field(..., ge=0, le=100)
    cess_rate: Decimal = Field(default=0, ge=0, le=100)
    is_active: bool = Field(default=True)
    description: Optional[str] = Field(None, max_length=500)
    hsn_code: Optional[str] = Field(None, max_length=10)
    sac_code: Optional[str] = Field(None, max_length=10)
    
    @validator('cgst_rate', 'sgst_rate', 'igst_rate')
    def validate_gst_rates(cls, v):
        if v < 0 or v > 100:
            raise ValueError('GST rates must be between 0 and 100')
        return v


class GSTTaxStructureUpdate(BaseModel):
    tax_name: Optional[str] = None
    cgst_rate: Optional[Decimal] = None
    sgst_rate: Optional[Decimal] = None
    igst_rate: Optional[Decimal] = None
    cess_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None


class GSTTaxStructureResponse(BaseModel):
    id: int
    company_id: int
    tax_name: str
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    cess_rate: Decimal
    is_active: bool
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Indian Geography Schemas
class StateCreate(BaseModel):
    state_code: str = Field(..., min_length=2, max_length=2)
    state_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = Field(default=True)


class StateUpdate(BaseModel):
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    is_active: Optional[bool] = None


class StateResponse(BaseModel):
    id: int
    state_code: str
    state_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DistrictCreate(BaseModel):
    district_code: str = Field(..., min_length=1, max_length=10)
    district_name: str = Field(..., min_length=1, max_length=100)
    state_id: int
    is_active: bool = Field(default=True)


class DistrictUpdate(BaseModel):
    district_code: Optional[str] = None
    district_name: Optional[str] = None
    state_id: Optional[int] = None
    is_active: Optional[bool] = None


class DistrictResponse(BaseModel):
    id: int
    district_code: str
    district_name: str
    state_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PincodeCreate(BaseModel):
    pincode: str = Field(..., min_length=6, max_length=6)
    area_name: str = Field(..., min_length=1, max_length=200)
    district_id: int
    state_id: int
    is_active: bool = Field(default=True)
    
    @validator('pincode')
    def validate_pincode(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Pincode must be 6 digits')
        return v


class PincodeUpdate(BaseModel):
    pincode: Optional[str] = None
    area_name: Optional[str] = None
    district_id: Optional[int] = None
    state_id: Optional[int] = None
    is_active: Optional[bool] = None


class PincodeResponse(BaseModel):
    id: int
    pincode: str
    area_name: str
    district_id: int
    state_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Indian Banking Schemas
class BankCreate(BaseModel):
    bank_code: str = Field(..., min_length=1, max_length=10)
    bank_name: str = Field(..., min_length=1, max_length=200)
    bank_type: str = Field(..., regex="^(public|private|cooperative|foreign|payment)$")
    is_active: bool = Field(default=True)


class BankUpdate(BaseModel):
    bank_code: Optional[str] = None
    bank_name: Optional[str] = None
    bank_type: Optional[str] = None
    is_active: Optional[bool] = None


class BankResponse(BaseModel):
    id: int
    bank_code: str
    bank_name: str
    bank_type: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BankBranchCreate(BaseModel):
    ifsc_code: str = Field(..., min_length=11, max_length=11)
    branch_name: str = Field(..., min_length=1, max_length=200)
    bank_id: int
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=6)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: bool = Field(default=True)
    
    @validator('ifsc_code')
    def validate_ifsc_code(cls, v):
        if len(v) != 11:
            raise ValueError('IFSC code must be 11 characters')
        return v


class BankBranchUpdate(BaseModel):
    ifsc_code: Optional[str] = None
    branch_name: Optional[str] = None
    bank_id: Optional[int] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class BankBranchResponse(BaseModel):
    id: int
    ifsc_code: str
    branch_name: str
    bank_id: int
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# TDS/TCS Schemas
class TDSCreate(BaseModel):
    tds_type: TDSType
    section_code: str = Field(..., min_length=1, max_length=10)
    section_description: str = Field(..., min_length=1, max_length=200)
    tds_rate: Decimal = Field(..., ge=0, le=100)
    threshold_amount: Decimal = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=500)


class TDSUpdate(BaseModel):
    tds_type: Optional[TDSType] = None
    section_code: Optional[str] = None
    section_description: Optional[str] = None
    tds_rate: Optional[Decimal] = None
    threshold_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class TDSResponse(BaseModel):
    id: int
    company_id: int
    tds_type: TDSType
    section_code: str
    section_description: str
    tds_rate: Decimal
    threshold_amount: Decimal
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# E-Invoicing Schemas
class EInvoiceCreate(BaseModel):
    invoice_id: int
    irn: Optional[str] = Field(None, max_length=100)
    ack_no: Optional[str] = Field(None, max_length=100)
    ack_date: Optional[datetime] = None
    qr_code: Optional[str] = Field(None, max_length=500)
    status: EInvoiceStatus = EInvoiceStatus.DRAFT
    error_message: Optional[str] = Field(None, max_length=1000)
    generated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = Field(None, max_length=200)


class EInvoiceUpdate(BaseModel):
    irn: Optional[str] = None
    ack_no: Optional[str] = None
    ack_date: Optional[datetime] = None
    qr_code: Optional[str] = None
    status: Optional[EInvoiceStatus] = None
    error_message: Optional[str] = None
    generated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class EInvoiceResponse(BaseModel):
    id: int
    company_id: int
    invoice_id: int
    irn: Optional[str] = None
    ack_no: Optional[str] = None
    ack_date: Optional[datetime] = None
    qr_code: Optional[str] = None
    status: EInvoiceStatus
    error_message: Optional[str] = None
    generated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# E-Waybill Schemas
class EWaybillCreate(BaseModel):
    ewaybill_number: str = Field(..., min_length=1, max_length=100)
    invoice_id: int
    distance: Decimal = Field(..., ge=0)
    transport_mode: str = Field(..., regex="^(road|rail|air|ship)$")
    vehicle_number: Optional[str] = Field(None, max_length=20)
    driver_name: Optional[str] = Field(None, max_length=100)
    driver_phone: Optional[str] = Field(None, max_length=20)
    transporter_id: Optional[str] = Field(None, max_length=50)
    transporter_name: Optional[str] = Field(None, max_length=200)
    transporter_phone: Optional[str] = Field(None, max_length=20)
    dispatch_from: str = Field(..., min_length=1, max_length=200)
    dispatch_to: str = Field(..., min_length=1, max_length=200)
    dispatch_date: date
    valid_until: Optional[datetime] = None
    status: str = Field(default="active", regex="^(active|expired|cancelled)$")
    notes: Optional[str] = Field(None, max_length=500)


class EWaybillUpdate(BaseModel):
    ewaybill_number: Optional[str] = None
    distance: Optional[Decimal] = None
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    transporter_id: Optional[str] = None
    transporter_name: Optional[str] = None
    transporter_phone: Optional[str] = None
    dispatch_from: Optional[str] = None
    dispatch_to: Optional[str] = None
    dispatch_date: Optional[date] = None
    valid_until: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class EWaybillResponse(BaseModel):
    id: int
    company_id: int
    ewaybill_number: str
    invoice_id: int
    distance: Decimal
    transport_mode: str
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    transporter_id: Optional[str] = None
    transporter_name: Optional[str] = None
    transporter_phone: Optional[str] = None
    dispatch_from: str
    dispatch_to: str
    dispatch_date: date
    valid_until: Optional[datetime] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Indian Chart of Accounts Schemas
class IndianChartOfAccountCreate(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=20)
    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: str = Field(..., regex="^(asset|liability|equity|income|expense)$")
    parent_account_id: Optional[int] = None
    gst_applicable: bool = Field(default=False)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=10)
    sac_code: Optional[str] = Field(None, max_length=10)
    is_tds_applicable: bool = Field(default=False)
    tds_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_tcs_applicable: bool = Field(default=False)
    tcs_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: bool = Field(default=True)
    description: Optional[str] = Field(None, max_length=500)


class IndianChartOfAccountUpdate(BaseModel):
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    parent_account_id: Optional[int] = None
    gst_applicable: Optional[bool] = None
    gst_rate: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    is_tds_applicable: Optional[bool] = None
    tds_rate: Optional[Decimal] = None
    is_tcs_applicable: Optional[bool] = None
    tcs_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class IndianChartOfAccountResponse(BaseModel):
    id: int
    company_id: int
    account_code: str
    account_name: str
    account_type: str
    parent_account_id: Optional[int] = None
    gst_applicable: bool
    gst_rate: Optional[Decimal] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    is_tds_applicable: bool
    tds_rate: Optional[Decimal] = None
    is_tcs_applicable: bool
    tcs_rate: Optional[Decimal] = None
    is_active: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Pincode Lookup Schemas
class PincodeLookupRequest(BaseModel):
    pincode: str = Field(..., min_length=6, max_length=6)
    
    @validator('pincode')
    def validate_pincode(cls, v):
        if not v.isdigit():
            raise ValueError('Pincode must contain only digits')
        return v


class PincodeLookupResponse(BaseModel):
    pincode: str
    area_name: str
    district_name: str
    state_name: str
    state_code: str
    is_active: bool

    class Config:
        from_attributes = True


# GST Compliance Schemas
class GSTComplianceRequest(BaseModel):
    gst_number: str = Field(..., min_length=15, max_length=15)
    return_period: str = Field(..., regex="^[0-9]{4}-[0-9]{2}$")
    return_type: str = Field(..., regex="^(gstr1|gstr3b|gstr9|gstr9c)$")


class GSTComplianceResponse(BaseModel):
    gst_number: str
    return_period: str
    return_type: str
    filing_status: str
    due_date: date
    filed_date: Optional[date] = None
    late_fee: Optional[Decimal] = None
    penalty: Optional[Decimal] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# Indian Localization Analytics Schemas
class IndianLocalizationAnalyticsResponse(BaseModel):
    total_gst_returns: int
    pending_returns: int
    overdue_returns: int
    total_tds_deducted: Decimal
    total_tcs_collected: Decimal
    e_invoices_generated: int
    e_waybills_generated: int
    compliance_score: Decimal
    monthly_gst_filing: List[Dict[str, Any]]
    tds_tcs_summary: Dict[str, Any]
    geography_analysis: Dict[str, Any]
    banking_analysis: Dict[str, Any]