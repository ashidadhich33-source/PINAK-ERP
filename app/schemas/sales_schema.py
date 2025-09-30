"""
Sales Management Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class SaleStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    INVOICED = "invoiced"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


# Sales Invoice Schemas
class SalesInvoiceCreate(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=100)
    customer_id: int
    invoice_date: date
    due_date: Optional[date] = None
    payment_terms: Optional[str] = Field(None, max_length=100)
    delivery_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    subtotal: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="INR", max_length=3)
    exchange_rate: Decimal = Field(default=1, gt=0)
    is_gst_applicable: bool = Field(default=True)
    cgst_amount: Decimal = Field(default=0, ge=0)
    sgst_amount: Decimal = Field(default=0, ge=0)
    igst_amount: Decimal = Field(default=0, ge=0)
    cess_amount: Decimal = Field(default=0, ge=0)
    tds_amount: Decimal = Field(default=0, ge=0)
    tcs_amount: Decimal = Field(default=0, ge=0)
    round_off: Decimal = Field(default=0)
    final_amount: Decimal = Field(..., ge=0)
    sales_items: List[Dict[str, Any]] = Field(..., min_items=1)


class SalesInvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    customer_id: Optional[int] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    is_gst_applicable: Optional[bool] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    cess_amount: Optional[Decimal] = None
    tds_amount: Optional[Decimal] = None
    tcs_amount: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None


class SalesInvoiceResponse(BaseModel):
    id: int
    company_id: int
    invoice_number: str
    customer_id: int
    invoice_date: date
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal
    is_gst_applicable: bool
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    tds_amount: Decimal
    tcs_amount: Decimal
    round_off: Decimal
    final_amount: Decimal
    status: InvoiceStatus
    payment_status: PaymentStatus
    paid_amount: Decimal
    balance_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Item Schemas
class SalesItemCreate(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    total_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    tax_amount: Decimal = Field(default=0, ge=0)
    net_amount: Decimal = Field(..., ge=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=500)


class SalesItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = None


class SalesItemResponse(BaseModel):
    id: int
    sales_invoice_id: int
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    discount_percent: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Return Schemas
class SalesReturnCreate(BaseModel):
    return_number: str = Field(..., min_length=1, max_length=100)
    sales_invoice_id: int
    return_date: date
    reason: str = Field(..., min_length=1, max_length=200)
    return_type: str = Field(..., regex="^(quality_issue|damaged|wrong_item|customer_request|other)$")
    notes: Optional[str] = Field(None, max_length=1000)
    return_items: List[Dict[str, Any]] = Field(..., min_items=1)


class SalesReturnUpdate(BaseModel):
    return_number: Optional[str] = None
    return_date: Optional[date] = None
    reason: Optional[str] = None
    return_type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class SalesReturnResponse(BaseModel):
    id: int
    company_id: int
    return_number: str
    sales_invoice_id: int
    return_date: date
    reason: str
    return_type: str
    notes: Optional[str] = None
    status: str
    total_quantity: Decimal
    total_amount: Decimal
    refund_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Payment Schemas
class SalesPaymentCreate(BaseModel):
    sales_invoice_id: int
    payment_date: date
    payment_method: str = Field(..., regex="^(cash|bank_transfer|cheque|upi|card|other)$")
    payment_amount: Decimal = Field(..., gt=0)
    reference_number: Optional[str] = Field(None, max_length=100)
    bank_account_id: Optional[int] = None
    cheque_number: Optional[str] = Field(None, max_length=50)
    cheque_date: Optional[date] = None
    upi_id: Optional[str] = Field(None, max_length=100)
    card_number: Optional[str] = Field(None, max_length=20)
    card_type: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)


class SalesPaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_amount: Optional[Decimal] = None
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None
    upi_id: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class SalesPaymentResponse(BaseModel):
    id: int
    company_id: int
    sales_invoice_id: int
    payment_date: date
    payment_method: str
    payment_amount: Decimal
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None
    upi_id: Optional[str] = None
    card_number: Optional[str] = None
    card_type: Optional[str] = None
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Quote Schemas
class SalesQuoteCreate(BaseModel):
    quote_number: str = Field(..., min_length=1, max_length=100)
    customer_id: int
    quote_date: date
    valid_until: Optional[date] = None
    delivery_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    subtotal: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="INR", max_length=3)
    exchange_rate: Decimal = Field(default=1, gt=0)
    is_gst_applicable: bool = Field(default=True)
    cgst_amount: Decimal = Field(default=0, ge=0)
    sgst_amount: Decimal = Field(default=0, ge=0)
    igst_amount: Decimal = Field(default=0, ge=0)
    cess_amount: Decimal = Field(default=0, ge=0)
    round_off: Decimal = Field(default=0)
    final_amount: Decimal = Field(..., ge=0)
    quote_items: List[Dict[str, Any]] = Field(..., min_items=1)


class SalesQuoteUpdate(BaseModel):
    quote_number: Optional[str] = None
    customer_id: Optional[int] = None
    quote_date: Optional[date] = None
    valid_until: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    is_gst_applicable: Optional[bool] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    cess_amount: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    status: Optional[str] = None


class SalesQuoteResponse(BaseModel):
    id: int
    company_id: int
    quote_number: str
    customer_id: int
    quote_date: date
    valid_until: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal
    is_gst_applicable: bool
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    round_off: Decimal
    final_amount: Decimal
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Order Schemas
class SalesOrderCreate(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=100)
    customer_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    subtotal: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(default=0, ge=0)
    tax_amount: Decimal = Field(default=0, ge=0)
    total_amount: Decimal = Field(..., ge=0)
    currency: str = Field(default="INR", max_length=3)
    exchange_rate: Decimal = Field(default=1, gt=0)
    is_gst_applicable: bool = Field(default=True)
    cgst_amount: Decimal = Field(default=0, ge=0)
    sgst_amount: Decimal = Field(default=0, ge=0)
    igst_amount: Decimal = Field(default=0, ge=0)
    cess_amount: Decimal = Field(default=0, ge=0)
    round_off: Decimal = Field(default=0)
    final_amount: Decimal = Field(..., ge=0)
    order_items: List[Dict[str, Any]] = Field(..., min_items=1)


class SalesOrderUpdate(BaseModel):
    order_number: Optional[str] = None
    customer_id: Optional[int] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    is_gst_applicable: Optional[bool] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    cess_amount: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    status: Optional[SaleStatus] = None


class SalesOrderResponse(BaseModel):
    id: int
    company_id: int
    order_number: str
    customer_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    exchange_rate: Decimal
    is_gst_applicable: bool
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    cess_amount: Decimal
    round_off: Decimal
    final_amount: Decimal
    status: SaleStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Analytics Schemas
class SalesAnalyticsResponse(BaseModel):
    total_sales: Decimal
    total_invoices: int
    average_invoice_value: Decimal
    total_customers: int
    active_customers: int
    pending_invoices: int
    overdue_payments: int
    top_customers: List[Dict[str, Any]]
    monthly_sales: List[Dict[str, Any]]
    category_wise_analysis: Dict[str, Any]
    payment_analysis: Dict[str, Any]
    customer_performance: List[Dict[str, Any]]
    sales_trends: List[Dict[str, Any]]


# Sales Import/Export Schemas
class SalesImportRequest(BaseModel):
    import_type: str = Field(..., regex="^(invoices|customers|payments|returns)$")
    file_path: str
    mapping: Dict[str, str] = Field(..., description="Column mapping")
    options: Dict[str, Any] = Field(default_factory=dict)


class SalesImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]
    warnings: List[str]


class SalesExportRequest(BaseModel):
    export_type: str = Field(..., regex="^(invoices|customers|analytics|payments|returns)$")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    customer_ids: Optional[List[int]] = None
    status: Optional[str] = None
    format: str = Field(default="csv", regex="^(csv|excel|json)$")
    include_inactive: bool = Field(default=False)


# Sales Commission Schemas
class SalesCommissionCreate(BaseModel):
    sales_invoice_id: int
    salesperson_id: int
    commission_rate: Decimal = Field(..., ge=0, le=100)
    commission_amount: Decimal = Field(..., ge=0)
    commission_type: str = Field(..., regex="^(percentage|fixed)$")
    payment_status: str = Field(default="pending", regex="^(pending|paid|cancelled)$")
    payment_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class SalesCommissionUpdate(BaseModel):
    commission_rate: Optional[Decimal] = None
    commission_amount: Optional[Decimal] = None
    commission_type: Optional[str] = None
    payment_status: Optional[str] = None
    payment_date: Optional[date] = None
    notes: Optional[str] = None


class SalesCommissionResponse(BaseModel):
    id: int
    company_id: int
    sales_invoice_id: int
    salesperson_id: int
    commission_rate: Decimal
    commission_amount: Decimal
    commission_type: str
    payment_status: str
    payment_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Sales Discount Schemas
class SalesDiscountCreate(BaseModel):
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


class SalesDiscountUpdate(BaseModel):
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


class SalesDiscountResponse(BaseModel):
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