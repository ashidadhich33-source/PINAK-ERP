"""
POS (Point of Sale) Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class POSSessionStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class POSPaymentMethod(str, Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    UPI = "upi"
    DIGITAL_WALLET = "digital_wallet"
    NET_BANKING = "net_banking"
    CHEQUE = "cheque"
    GIFT_CARD = "gift_card"
    LOYALTY_POINTS = "loyalty_points"


class POSTransactionType(str, Enum):
    SALE = "sale"
    RETURN = "return"
    EXCHANGE = "exchange"
    REFUND = "refund"
    VOID = "void"
    DISCOUNT = "discount"


# POS Session Schemas
class POSSessionCreate(BaseModel):
    session_number: str = Field(..., min_length=3, max_length=100)
    session_date: date
    store_id: int
    opening_cash: Decimal = Field(default=0, ge=0)
    notes: Optional[str] = None
    
    @validator('session_number')
    def validate_session_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Session number must be at least 3 characters')
        return v


class POSSessionUpdate(BaseModel):
    closing_cash: Optional[Decimal] = None
    notes: Optional[str] = None
    status: Optional[POSSessionStatus] = None


class POSSessionResponse(BaseModel):
    id: int
    session_number: str
    session_date: date
    store_id: int
    cashier_id: int
    opening_cash: Decimal
    closing_cash: Optional[Decimal] = None
    expected_cash: Optional[Decimal] = None
    cash_difference: Optional[Decimal] = None
    total_sales: Decimal
    total_transactions: int
    status: POSSessionStatus
    notes: Optional[str] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Transaction Schemas
class POSTransactionCreate(BaseModel):
    transaction_number: str = Field(..., min_length=1, max_length=100)
    customer_id: Optional[int] = None
    transaction_type: POSTransactionType = POSTransactionType.SALE
    subtotal: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    payment_method: POSPaymentMethod
    payment_reference: Optional[str] = None
    cgst_amount: Decimal = Field(default=0, ge=0)
    sgst_amount: Decimal = Field(default=0, ge=0)
    igst_amount: Decimal = Field(default=0, ge=0)
    total_gst_amount: Decimal = Field(default=0, ge=0)
    notes: Optional[str] = None


class POSTransactionUpdate(BaseModel):
    customer_id: Optional[int] = None
    transaction_type: Optional[POSTransactionType] = None
    subtotal: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    payment_method: Optional[POSPaymentMethod] = None
    payment_reference: Optional[str] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    total_gst_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class POSTransactionResponse(BaseModel):
    id: int
    company_id: int
    session_id: int
    transaction_number: str
    customer_id: Optional[int] = None
    transaction_type: POSTransactionType
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: POSPaymentMethod
    payment_reference: Optional[str] = None
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completed_by: Optional[int] = None

    class Config:
        from_attributes = True


# POS Transaction Item Schemas
class POSTransactionItemCreate(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    total_price: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    tax_amount: Decimal = Field(default=0, ge=0)
    net_amount: Decimal = Field(..., ge=0)
    serial_numbers: Optional[str] = None  # JSON array
    batch_numbers: Optional[str] = None  # JSON array
    expiry_dates: Optional[str] = None  # JSON array


class POSTransactionItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    expiry_dates: Optional[str] = None


class POSTransactionItemResponse(BaseModel):
    id: int
    transaction_id: int
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    serial_numbers: Optional[str] = None
    batch_numbers: Optional[str] = None
    expiry_dates: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Payment Schemas
class POSPaymentCreate(BaseModel):
    payment_method: POSPaymentMethod
    payment_amount: Decimal = Field(..., gt=0)
    payment_reference: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    card_holder_name: Optional[str] = None
    authorization_code: Optional[str] = None
    upi_id: Optional[str] = None
    wallet_type: Optional[str] = None
    wallet_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_id_bank: Optional[str] = None


class POSPaymentUpdate(BaseModel):
    payment_method: Optional[POSPaymentMethod] = None
    payment_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    card_holder_name: Optional[str] = None
    authorization_code: Optional[str] = None
    upi_id: Optional[str] = None
    wallet_type: Optional[str] = None
    wallet_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_id_bank: Optional[str] = None
    status: Optional[str] = None


class POSPaymentResponse(BaseModel):
    id: int
    transaction_id: int
    payment_method: POSPaymentMethod
    payment_amount: Decimal
    payment_reference: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    card_holder_name: Optional[str] = None
    authorization_code: Optional[str] = None
    upi_id: Optional[str] = None
    wallet_type: Optional[str] = None
    wallet_transaction_id: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_id_bank: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Store Schemas
class StoreCreate(BaseModel):
    store_code: str = Field(..., min_length=1, max_length=50)
    store_name: str = Field(..., min_length=1, max_length=200)
    store_address: Optional[str] = None
    store_city: Optional[str] = None
    store_state: Optional[str] = None
    store_pincode: Optional[str] = None
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    currency: str = Field(default="INR", max_length=3)
    timezone: str = Field(default="Asia/Kolkata")
    tax_number: Optional[str] = None
    gst_number: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None


class StoreUpdate(BaseModel):
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    store_city: Optional[str] = None
    store_state: Optional[str] = None
    store_pincode: Optional[str] = None
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    tax_number: Optional[str] = None
    gst_number: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    id: int
    company_id: int
    store_code: str
    store_name: str
    store_address: Optional[str] = None
    store_city: Optional[str] = None
    store_state: Optional[str] = None
    store_pincode: Optional[str] = None
    store_phone: Optional[str] = None
    store_email: Optional[str] = None
    currency: str
    timezone: str
    tax_number: Optional[str] = None
    gst_number: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Store Staff Schemas
class StoreStaffCreate(BaseModel):
    store_id: int
    user_id: int
    role: str = Field(..., min_length=1, max_length=50)
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool = True


class StoreStaffUpdate(BaseModel):
    role: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class StoreStaffResponse(BaseModel):
    id: int
    store_id: int
    user_id: int
    role: str
    permissions: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Receipt Schemas
class POSReceiptCreate(BaseModel):
    transaction_id: int
    receipt_number: str = Field(..., min_length=1, max_length=100)
    receipt_type: str = Field(default="sale", regex="^(sale|return|exchange)$")
    customer_copy: bool = Field(default=True)
    merchant_copy: bool = Field(default=True)
    print_count: int = Field(default=0, ge=0)
    receipt_data: Optional[Dict[str, Any]] = None


class POSReceiptUpdate(BaseModel):
    receipt_number: Optional[str] = None
    receipt_type: Optional[str] = None
    customer_copy: Optional[bool] = None
    merchant_copy: Optional[bool] = None
    print_count: Optional[int] = None
    receipt_data: Optional[Dict[str, Any]] = None


class POSReceiptResponse(BaseModel):
    id: int
    transaction_id: int
    receipt_number: str
    receipt_type: str
    customer_copy: bool
    merchant_copy: bool
    print_count: int
    receipt_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Analytics Schemas
class POSAnalyticsResponse(BaseModel):
    id: int
    store_id: int
    session_id: int
    analytics_date: date
    total_sales: Decimal
    total_transactions: int
    average_transaction_value: Decimal
    total_customers: int
    new_customers: int
    returning_customers: int
    cash_sales: Decimal
    card_sales: Decimal
    upi_sales: Decimal
    other_sales: Decimal
    total_discounts: Decimal
    total_taxes: Decimal
    peak_hour: Optional[str] = None
    slow_hour: Optional[str] = None
    top_selling_items: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Inventory Schemas
class POSInventoryCreate(BaseModel):
    store_id: int
    item_id: int
    variant_id: Optional[int] = None
    current_stock: Decimal = Field(..., ge=0)
    reserved_stock: Decimal = Field(default=0, ge=0)
    available_stock: Decimal = Field(..., ge=0)
    reorder_level: Decimal = Field(default=0, ge=0)
    reorder_quantity: Decimal = Field(default=0, ge=0)
    last_updated: Optional[datetime] = None


class POSInventoryUpdate(BaseModel):
    current_stock: Optional[Decimal] = None
    reserved_stock: Optional[Decimal] = None
    available_stock: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    last_updated: Optional[datetime] = None


class POSInventoryResponse(BaseModel):
    id: int
    store_id: int
    item_id: int
    variant_id: Optional[int] = None
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# POS Transaction Completion Schema
class POSTransactionComplete(BaseModel):
    send_whatsapp: bool = Field(default=True, description="Send WhatsApp receipt to customer")
    send_sms: bool = Field(default=False, description="Send SMS receipt to customer")
    send_email: bool = Field(default=False, description="Send email receipt to customer")
    print_receipt: bool = Field(default=True, description="Print physical receipt")
    loyalty_points: bool = Field(default=True, description="Process loyalty points")


# POS Search Schemas
class POSSearchRequest(BaseModel):
    search_term: str = Field(..., min_length=1, max_length=100)
    search_type: str = Field(default="barcode", regex="^(barcode|name|sku|category)$")
    store_id: Optional[int] = None
    include_variants: bool = Field(default=True)
    include_inactive: bool = Field(default=False)


class POSSearchResponse(BaseModel):
    barcode: str
    style_code: str
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: Decimal
    hsn: Optional[str] = None
    available_qty: Decimal
    item_id: int
    variant_id: Optional[int] = None
    item_name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    unit_price: Decimal
    discount_percent: Decimal = 0
    tax_rate: Decimal = 0
    is_active: bool = True

    class Config:
        from_attributes = True