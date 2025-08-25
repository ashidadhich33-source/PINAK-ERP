from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class SaleReturnItemCreate(BaseModel):
    sale_id: str
    sale_item_id: str
    return_qty: int = Field(..., gt=0)

class SaleReturnCreate(BaseModel):
    sr_series_id: Optional[str] = None
    customer_mobile: Optional[str] = Field(None, regex="^[0-9]{10}$")
    tax_region: Optional[str] = "local"
    reason: str
    items: List[SaleReturnItemCreate]

class SaleReturnResponse(BaseModel):
    id: str
    sr_no: str
    sr_date: datetime
    customer_mobile: Optional[str]
    total_incl: Decimal
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SaleLineSearchResponse(BaseModel):
    sale_id: str
    sale_item_id: str
    bill_no: str
    bill_date: str
    customer_mobile: str
    customer_name: str
    style_code: str
    color: Optional[str]
    size: Optional[str]
    unit_mrp_incl: float
    disc_pct: float
    line_amount_incl: float
    gst_rate: float
    hsn: Optional[str]
    sold_qty: int
    already_returned_qty: int
    returnable_qty: int

class ReturnCreditResponse(BaseModel):
    id: str
    rc_no: str
    customer_mobile: Optional[str]
    rc_amount_incl: Decimal
    status: str
    created_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True