from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    kid1_name: Optional[str] = Field(None, max_length=100)
    kid1_dob: Optional[date] = None
    kid2_name: Optional[str] = Field(None, max_length=100)
    kid2_dob: Optional[date] = None
    kid3_name: Optional[str] = Field(None, max_length=100)
    kid3_dob: Optional[date] = None

class CustomerCreate(CustomerBase):
    mobile: str = Field(..., regex="^[0-9]{10}$")

class CustomerUpdate(CustomerBase):
    name: Optional[str] = None

class CustomerResponse(BaseModel):
    mobile: str
    name: str
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    lifetime_purchase: Decimal
    points_balance: int
    grade: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    kids_info: List[Dict[str, Any]]
    total_bills: int
    total_purchase: Decimal
    last_purchase_date: Optional[datetime]
    total_returns: int
    total_return_amount: Decimal
    open_return_credits: List[Dict[str, Any]]
    recent_point_transactions: List[Dict[str, Any]]
    active_coupons: List[Dict[str, Any]]

class CustomerImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]

class CustomerActivityResponse(BaseModel):
    mobile: str
    name: str
    last_purchase_date: Optional[datetime]
    days_inactive: int
    lifetime_purchase: Decimal
    grade: str

class CustomerBirthdayResponse(BaseModel):
    customer_mobile: str
    customer_name: str
    email: Optional[str]
    birthday_kids: List[Dict[str, Any]]

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
    id: str
    name: str
    amount_from: Decimal
    amount_to: Decimal
    earn_pct: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True