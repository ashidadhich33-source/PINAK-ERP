from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    gstin: Optional[str] = Field(None, regex="^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9]{1}$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, regex="^[0-9]{10}$")
    location_type: str = Field(..., regex="^(local|inter)$")

class SupplierCreate(SupplierBase):
    create_payment_mode: bool = False  # For card machine suppliers

class SupplierUpdate(SupplierBase):
    name: Optional[str] = None
    location_type: Optional[str] = None
    active: Optional[bool] = None

class SupplierResponse(BaseModel):
    id: str
    name: str
    gstin: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location_type: str
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SupplierDetailResponse(SupplierResponse):
    total_bills: int
    total_purchase: Decimal
    last_purchase_date: Optional[datetime]
    total_returns: int
    total_return_amount: Decimal
    pending_amount: Decimal
    recent_transactions: List[Dict[str, Any]]
    payment_modes: List[Dict[str, Any]]

class SupplierImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]