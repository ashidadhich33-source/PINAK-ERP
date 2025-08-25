from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date

class SaleItemCreate(BaseModel):
    barcode: str
    qty: int = Field(..., gt=0)
    discount_pct: Optional[Decimal] = Field(default=Decimal('0'), ge=0, le=100)

class PaymentSplit(BaseModel):
    payment_mode_id: str
    amount: Decimal = Field(..., gt=0)

class SaleCreate(BaseModel):
    series_id: Optional[str] = None
    customer_mobile: Optional[str] = Field(None, regex="^[0-9]{10}$")
    staff_id: Optional[str] = None
    agent_id: Optional[str] = None
    tax_region: Optional[str] = "local"
    items: List[SaleItemCreate]
    coupon_code: Optional[str] = None
    redeem_points: Optional[int] = Field(default=0, ge=0)
    redeem_otp: Optional[str] = None
    return_credit_id: Optional[str] = None
    payments: List[PaymentSplit]
    round_off: Optional[float] = 0.01
    send_whatsapp: bool = False

class SaleResponse(BaseModel):
    id: str
    bill_no: str
    bill_date: datetime
    customer_mobile: Optional[str]
    gross_incl: Decimal
    discount_incl: Decimal
    coupon_incl: Optional[Decimal]
    base_excl: Decimal
    tax_amt_info: Decimal
    redeem_points: int
    redeem_value: Decimal
    return_credit_used_value: Decimal
    final_payable: Decimal
    round_off: Decimal
    
    class Config:
        from_attributes = True

class CouponValidateRequest(BaseModel):
    coupon_code: str
    bill_amount: Decimal
    customer_mobile: Optional[str] = None

class LoyaltyRedeemRequest(BaseModel):
    customer_mobile: str = Field(..., regex="^[0-9]{10}$")
    points_to_redeem: int = Field(..., gt=0)
    otp: Optional[str] = None

class POSSearchResponse(BaseModel):
    barcode: str
    style_code: str
    color: Optional[str]
    size: Optional[str]
    mrp: float
    hsn: Optional[str]
    available_qty: int

class SaleReturnCreate(BaseModel):
    # Will be implemented in next section
    pass

class SaleReturnResponse(BaseModel):
    # Will be implemented in next section
    pass

class ReturnCreditResponse(BaseModel):
    id: str
    rc_no: str
    customer_mobile: Optional[str]
    rc_amount_incl: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True