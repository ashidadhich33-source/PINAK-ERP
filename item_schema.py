from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

class ItemBase(BaseModel):
    style_code: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = None
    size: Optional[str] = None
    hsn: Optional[str] = None
    mrp_incl: Optional[Decimal] = Field(None, ge=0)
    purchase_rate_basic: Optional[Decimal] = Field(None, ge=0)
    brand: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    status: str = "active"

class ItemCreate(ItemBase):
    barcode: str = Field(..., min_length=1, max_length=50)

class ItemUpdate(ItemBase):
    style_code: Optional[str] = None

class ItemResponse(ItemBase):
    barcode: str
    company_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ItemImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[Dict[str, Any]]

class StockResponse(BaseModel):
    barcode: str
    qty_on_hand: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    barcode: str
    qty: int = Field(..., gt=0)

class BulkStockUpdate(BaseModel):
    items: List[StockUpdate]