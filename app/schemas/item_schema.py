from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

class ItemBase(BaseModel):
    barcode: str = Field(..., min_length=1, max_length=50)
    style_code: str = Field(..., min_length=1, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=20)
    material: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    brand: Optional[str] = Field(None, max_length=100)
    brand_id: Optional[int] = None
    gender: Optional[str] = Field(None, regex="^(male|female|unisex|kids)$")
    hsn_code: Optional[str] = Field(None, max_length=20)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    cess_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    mrp: Optional[Decimal] = Field(None, ge=0)
    mrp_inclusive: bool = True
    purchase_rate: Optional[Decimal] = Field(None, ge=0)
    purchase_rate_inclusive: bool = False
    selling_price: Optional[Decimal] = Field(None, ge=0)
    selling_price_inclusive: bool = True
    landed_cost: Optional[Decimal] = Field(None, ge=0)
    margin_percent: Optional[Decimal] = Field(None, ge=0)
    is_stockable: bool = True
    track_inventory: bool = True
    min_stock_level: Decimal = Field(default=Decimal('0'), ge=0)
    max_stock_level: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    uom: str = Field(default="PCS", max_length=20)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    status: str = Field(default="active", regex="^(active|inactive|discontinued)$")
    is_service: bool = False
    is_serialized: bool = False
    allow_negative_stock: bool = False
    image_path: Optional[str] = Field(None, max_length=500)
    additional_images: Optional[str] = None
    preferred_supplier_id: Optional[int] = None
    supplier_item_code: Optional[str] = Field(None, max_length=100)

class ItemCreate(ItemBase):
    barcode: str = Field(..., min_length=1, max_length=50)

class ItemUpdate(ItemBase):
    style_code: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    current_stock: Optional[Decimal] = None
    stock_value: Decimal = Decimal('0')
    created_at: datetime
    updated_at: Optional[datetime] = None

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