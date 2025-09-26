from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    customer_type: str = Field(default="retail", regex="^(retail|wholesale|corporate)$")
    mobile: Optional[str] = Field(None, regex="^[0-9]{10,15}$")
    phone: Optional[str] = Field(None, regex="^[0-9]{10,15}$")
    email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=200)
    address_line1: Optional[str] = Field(None, max_length=200)
    address_line2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="India")
    postal_code: Optional[str] = Field(None, max_length=10)
    gst_number: Optional[str] = Field(None, regex="^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
    pan_number: Optional[str] = Field(None, regex="^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    business_name: Optional[str] = Field(None, max_length=200)
    credit_limit: Decimal = Field(default=Decimal('0'))
    payment_terms: Optional[str] = Field(None, max_length=100)
    discount_percent: Decimal = Field(default=Decimal('0'), ge=0, le=100)
    price_list: Optional[str] = Field(None, regex="^(retail|wholesale|special)$")
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    gender: Optional[str] = Field(None, regex="^(male|female|other)$")

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    customer_type: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    business_name: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    discount_percent: Optional[Decimal] = None
    price_list: Optional[str] = None
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[str] = None
    is_loyalty_member: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    customer_code: str
    status: str = "active"
    is_loyalty_member: bool = False
    loyalty_card_number: Optional[str] = None
    first_sale_date: Optional[datetime] = None
    last_sale_date: Optional[datetime] = None
    total_sales_amount: Decimal = Decimal('0')
    total_transactions: int = 0
    opening_balance: Decimal = Decimal('0')
    current_balance: Decimal = Decimal('0')
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    # Additional computed fields can be added here if needed
    pass

class CustomerImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]

class CustomerActivityResponse(BaseModel):
    customer_code: str
    name: str
    mobile: Optional[str]
    last_sale_date: Optional[datetime]
    total_sales_amount: Decimal
    total_transactions: int

class LoyaltyGradeCreate(BaseModel):
    name: str
    amount_from: Decimal = Field(..., ge=0)
    amount_to: Decimal = Field(..., ge=0)
    earn_pct: Decimal = Field(..., ge=0, le=100)
    
    @validator('amount_to')
    def validate_amount_range(cls, v, values):
        if 'amount_from' in values and v < values['amount_from']:
            raise ValueError('amount_to must be greater than amount_from')
        return v

class LoyaltyGradeResponse(BaseModel):
    id: int
    name: str
    amount_from: Decimal
    amount_to: Decimal
    earn_pct: Decimal
    discount_percent: Decimal
    badge_color: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True