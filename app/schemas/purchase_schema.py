from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class PurchaseBillItemCreate(BaseModel):
    barcode: str
    qty: int = Field(..., gt=0)
    basic_rate: Decimal = Field(..., ge=0)

class PurchaseBillItemResponse(BaseModel):
    id: str
    barcode: str
    style_code: str
    size: Optional[str]
    hsn: Optional[str]
    qty: int
    basic_rate: Decimal
    gst_rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    line_taxable: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    line_total: Decimal
    mrp: Optional[Decimal]
    
    class Config:
        from_attributes = True

class PurchaseBillCreate(BaseModel):
    pb_series_id: Optional[str] = None
    payment_mode: str = "cash"  # cash or credit
    supplier_id: str
    supplier_bill_no: Optional[str] = None
    supplier_bill_date: Optional[date] = None
    reverse_charge: bool = False
    items: List[PurchaseBillItemCreate]

class PurchaseBillResponse(BaseModel):
    id: str
    pb_no: str
    pb_date: datetime
    payment_mode: str
    supplier_id: str
    tax_region: str
    supplier_bill_no: Optional[str]
    supplier_bill_date: Optional[date]
    reverse_charge: bool
    total_taxable: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_igst: Decimal
    grand_total: Decimal
    items: List[PurchaseBillItemResponse]
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PurchaseReturnItemCreate(BaseModel):
    barcode: str
    qty: int = Field(..., gt=0)
    basic_rate: Decimal = Field(..., ge=0)

class PurchaseReturnCreate(BaseModel):
    pr_series_id: Optional[str] = None
    supplier_id: str
    supplier_bill_no: Optional[str] = None
    supplier_bill_date: Optional[date] = None
    reason: str
    items: List[PurchaseReturnItemCreate]

class PurchaseReturnResponse(BaseModel):
    id: str
    pr_no: str
    pr_date: datetime
    supplier_id: str
    tax_region: str
    reason: str
    total_taxable: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_igst: Decimal
    grand_total: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True