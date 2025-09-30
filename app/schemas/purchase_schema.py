"""
Purchase Management Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class PurchaseStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    INVOICED = "invoiced"
    PAID = "paid"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class PurchaseItemStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    PARTIALLY_RECEIVED = "partially_received"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"


# Purchase Order Schemas
class PurchaseOrderCreate(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=100)
    supplier_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
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
    purchase_items: List[Dict[str, Any]] = Field(..., min_items=1)


class PurchaseOrderUpdate(BaseModel):
    order_number: Optional[str] = None
    supplier_id: Optional[int] = None
    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
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
    status: Optional[PurchaseStatus] = None


class PurchaseOrderResponse(BaseModel):
    id: int
    company_id: int
    order_number: str
    supplier_id: int
    order_date: date
    expected_delivery_date: Optional[date] = None
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
    status: PurchaseStatus
    payment_status: PaymentStatus
    received_quantity: Decimal
    pending_quantity: Decimal
    invoiced_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Item Schemas
class PurchaseItemCreate(BaseModel):
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
    received_quantity: Decimal = Field(default=0, ge=0)
    pending_quantity: Decimal = Field(..., gt=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = Field(None, max_length=500)


class PurchaseItemUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    net_amount: Optional[Decimal] = None
    received_quantity: Optional[Decimal] = None
    pending_quantity: Optional[Decimal] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = None
    status: Optional[PurchaseItemStatus] = None


class PurchaseItemResponse(BaseModel):
    id: int
    purchase_order_id: int
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
    received_quantity: Decimal
    pending_quantity: Decimal
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    serial_numbers: Optional[List[str]] = None
    notes: Optional[str] = None
    status: PurchaseItemStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Receipt Schemas
class PurchaseReceiptCreate(BaseModel):
    receipt_number: str = Field(..., min_length=1, max_length=100)
    purchase_order_id: int
    receipt_date: date
    supplier_invoice_number: Optional[str] = Field(None, max_length=100)
    supplier_invoice_date: Optional[date] = None
    warehouse_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)
    receipt_items: List[Dict[str, Any]] = Field(..., min_items=1)


class PurchaseReceiptUpdate(BaseModel):
    receipt_number: Optional[str] = None
    receipt_date: Optional[date] = None
    supplier_invoice_number: Optional[str] = None
    supplier_invoice_date: Optional[date] = None
    warehouse_id: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class PurchaseReceiptResponse(BaseModel):
    id: int
    company_id: int
    receipt_number: str
    purchase_order_id: int
    receipt_date: date
    supplier_invoice_number: Optional[str] = None
    supplier_invoice_date: Optional[date] = None
    warehouse_id: Optional[int] = None
    notes: Optional[str] = None
    status: str
    total_quantity: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Return Schemas
class PurchaseReturnCreate(BaseModel):
    return_number: str = Field(..., min_length=1, max_length=100)
    purchase_order_id: int
    return_date: date
    reason: str = Field(..., min_length=1, max_length=200)
    return_type: str = Field(..., regex="^(quality_issue|damaged|wrong_item|excess|other)$")
    notes: Optional[str] = Field(None, max_length=1000)
    return_items: List[Dict[str, Any]] = Field(..., min_items=1)


class PurchaseReturnUpdate(BaseModel):
    return_number: Optional[str] = None
    return_date: Optional[date] = None
    reason: Optional[str] = None
    return_type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class PurchaseReturnResponse(BaseModel):
    id: int
    company_id: int
    return_number: str
    purchase_order_id: int
    return_date: date
    reason: str
    return_type: str
    notes: Optional[str] = None
    status: str
    total_quantity: Decimal
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Payment Schemas
class PurchasePaymentCreate(BaseModel):
    purchase_order_id: int
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


class PurchasePaymentUpdate(BaseModel):
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


class PurchasePaymentResponse(BaseModel):
    id: int
    company_id: int
    purchase_order_id: int
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


# Supplier Schemas
class SupplierCreate(BaseModel):
    supplier_name: str = Field(..., min_length=1, max_length=200)
    supplier_code: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="India", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    gst_number: Optional[str] = Field(None, max_length=15)
    pan_number: Optional[str] = Field(None, max_length=10)
    credit_limit: Decimal = Field(default=0, ge=0)
    payment_terms: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="INR", max_length=3)
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(None, max_length=1000)


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    company_id: int
    supplier_name: str
    supplier_code: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    credit_limit: Decimal
    payment_terms: Optional[str] = None
    currency: str
    is_active: bool
    notes: Optional[str] = None
    total_purchases: Decimal
    total_payments: Decimal
    outstanding_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Purchase Analytics Schemas
class PurchaseAnalyticsResponse(BaseModel):
    total_orders: int
    total_amount: Decimal
    average_order_value: Decimal
    total_suppliers: int
    active_suppliers: int
    pending_orders: int
    overdue_payments: int
    top_suppliers: List[Dict[str, Any]]
    monthly_purchases: List[Dict[str, Any]]
    category_wise_analysis: Dict[str, Any]
    payment_analysis: Dict[str, Any]
    supplier_performance: List[Dict[str, Any]]


# Purchase Import/Export Schemas
class PurchaseImportRequest(BaseModel):
    import_type: str = Field(..., regex="^(orders|suppliers|receipts)$")
    file_path: str
    mapping: Dict[str, str] = Field(..., description="Column mapping")
    options: Dict[str, Any] = Field(default_factory=dict)


class PurchaseImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]
    warnings: List[str]


class PurchaseExportRequest(BaseModel):
    export_type: str = Field(..., regex="^(orders|suppliers|analytics|payments)$")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    supplier_ids: Optional[List[int]] = None
    status: Optional[str] = None
    format: str = Field(default="csv", regex="^(csv|excel|json)$")
    include_inactive: bool = Field(default=False)


# Purchase Approval Schemas
class PurchaseApprovalRequest(BaseModel):
    purchase_order_id: int
    approval_status: str = Field(..., regex="^(approved|rejected)$")
    approval_notes: Optional[str] = Field(None, max_length=500)
    approved_amount: Optional[Decimal] = Field(None, ge=0)


class PurchaseApprovalResponse(BaseModel):
    purchase_order_id: int
    approval_status: str
    approval_notes: Optional[str] = None
    approved_amount: Optional[Decimal] = None
    approved_by: int
    approved_at: datetime

    class Config:
        from_attributes = True


# Purchase Comparison Schemas
class PurchaseComparisonRequest(BaseModel):
    item_ids: List[int] = Field(..., min_items=1)
    supplier_ids: Optional[List[int]] = None
    comparison_date: Optional[date] = None


class PurchaseComparisonResponse(BaseModel):
    item_id: int
    item_name: str
    suppliers: List[Dict[str, Any]]
    best_price: Decimal
    best_supplier: str
    price_variance: Decimal
    recommendation: str

    class Config:
        from_attributes = True