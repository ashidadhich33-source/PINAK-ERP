"""
Inventory Management Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    EXPIRED = "expired"


class ItemType(str, Enum):
    PRODUCT = "product"
    SERVICE = "service"
    ASSET = "asset"
    CONSUMABLE = "consumable"


# Item Schemas
class ItemCreate(BaseModel):
    item_code: str = Field(..., min_length=1, max_length=50)
    item_name: str = Field(..., min_length=1, max_length=200)
    item_type: ItemType = ItemType.PRODUCT
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=1000)
    barcode: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=50)
    hsn_code: Optional[str] = Field(None, max_length=10)
    sac_code: Optional[str] = Field(None, max_length=10)
    gst_rate: Decimal = Field(default=0, ge=0, le=100)
    cess_rate: Decimal = Field(default=0, ge=0, le=100)
    purchase_price: Decimal = Field(default=0, ge=0)
    selling_price: Decimal = Field(default=0, ge=0)
    mrp: Decimal = Field(default=0, ge=0)
    wholesale_price: Decimal = Field(default=0, ge=0)
    minimum_selling_price: Decimal = Field(default=0, ge=0)
    reorder_level: Decimal = Field(default=0, ge=0)
    reorder_quantity: Decimal = Field(default=0, ge=0)
    maximum_stock: Optional[Decimal] = Field(None, ge=0)
    track_serial_numbers: bool = Field(default=False)
    track_batch_numbers: bool = Field(default=False)
    track_expiry_dates: bool = Field(default=False)
    is_taxable: bool = Field(default=True)
    is_active: bool = Field(default=True)
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=100)
    origin_country: Optional[str] = Field(None, max_length=100)
    shelf_life_days: Optional[int] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None


class ItemUpdate(BaseModel):
    item_code: Optional[str] = None
    item_name: Optional[str] = None
    item_type: Optional[ItemType] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    cess_rate: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    wholesale_price: Optional[Decimal] = None
    minimum_selling_price: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    maximum_stock: Optional[Decimal] = None
    track_serial_numbers: Optional[bool] = None
    track_batch_numbers: Optional[bool] = None
    track_expiry_dates: Optional[bool] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    origin_country: Optional[str] = None
    shelf_life_days: Optional[int] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None


class ItemResponse(BaseModel):
    id: int
    company_id: int
    item_code: str
    item_name: str
    item_type: ItemType
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    unit_id: Optional[int] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    hsn_code: Optional[str] = None
    sac_code: Optional[str] = None
    gst_rate: Decimal
    cess_rate: Decimal
    purchase_price: Decimal
    selling_price: Decimal
    mrp: Decimal
    wholesale_price: Decimal
    minimum_selling_price: Decimal
    reorder_level: Decimal
    reorder_quantity: Decimal
    maximum_stock: Optional[Decimal] = None
    track_serial_numbers: bool
    track_batch_numbers: bool
    track_expiry_dates: bool
    is_taxable: bool
    is_active: bool
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    origin_country: Optional[str] = None
    shelf_life_days: Optional[int] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    total_value: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Item Variant Schemas
class ItemVariantCreate(BaseModel):
    item_id: int
    variant_name: str = Field(..., min_length=1, max_length=100)
    variant_code: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=50)
    selling_price: Decimal = Field(..., ge=0)
    purchase_price: Decimal = Field(default=0, ge=0)
    mrp: Decimal = Field(default=0, ge=0)
    wholesale_price: Decimal = Field(default=0, ge=0)
    minimum_selling_price: Decimal = Field(default=0, ge=0)
    weight: Optional[Decimal] = Field(None, ge=0)
    color: Optional[str] = Field(None, max_length=50)
    size: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)
    attributes: Optional[Dict[str, Any]] = None


class ItemVariantUpdate(BaseModel):
    variant_name: Optional[str] = None
    variant_code: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    selling_price: Optional[Decimal] = None
    purchase_price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    wholesale_price: Optional[Decimal] = None
    minimum_selling_price: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: Optional[bool] = None
    attributes: Optional[Dict[str, Any]] = None


class ItemVariantResponse(BaseModel):
    id: int
    item_id: int
    variant_name: str
    variant_code: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    selling_price: Decimal
    purchase_price: Decimal
    mrp: Decimal
    wholesale_price: Decimal
    minimum_selling_price: Decimal
    weight: Optional[Decimal] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    is_active: bool
    attributes: Optional[Dict[str, Any]] = None
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stock Movement Schemas
class StockMovementCreate(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    movement_type: StockMovementType
    quantity: Decimal = Field(..., description="Positive for IN, negative for OUT")
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=100)
    unit_cost: Decimal = Field(default=0, ge=0)
    total_cost: Decimal = Field(default=0, ge=0)
    batch_number: Optional[str] = Field(None, max_length=50)
    serial_numbers: Optional[List[str]] = None
    expiry_date: Optional[date] = None
    location_from: Optional[str] = Field(None, max_length=100)
    location_to: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    movement_date: Optional[datetime] = None


class StockMovementUpdate(BaseModel):
    movement_type: Optional[StockMovementType] = None
    quantity: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    batch_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None
    expiry_date: Optional[date] = None
    location_from: Optional[str] = None
    location_to: Optional[str] = None
    notes: Optional[str] = None
    movement_date: Optional[datetime] = None


class StockMovementResponse(BaseModel):
    id: int
    item_id: int
    variant_id: Optional[int] = None
    movement_type: StockMovementType
    quantity: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    unit_cost: Decimal
    total_cost: Decimal
    batch_number: Optional[str] = None
    serial_numbers: Optional[List[str]] = None
    expiry_date: Optional[date] = None
    location_from: Optional[str] = None
    location_to: Optional[str] = None
    notes: Optional[str] = None
    movement_date: datetime
    balance_after: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stock Adjustment Schemas
class StockAdjustmentCreate(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    adjustment_type: str = Field(..., regex="^(increase|decrease)$")
    quantity: Decimal = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=200)
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    adjustment_date: Optional[date] = None


class StockAdjustmentUpdate(BaseModel):
    adjustment_type: Optional[str] = None
    quantity: Optional[Decimal] = None
    reason: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    adjustment_date: Optional[date] = None
    status: Optional[str] = None


class StockAdjustmentResponse(BaseModel):
    id: int
    item_id: int
    variant_id: Optional[int] = None
    adjustment_type: str
    quantity: Decimal
    reason: str
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    adjustment_date: date
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Group Schemas
class InventoryGroupCreate(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100)
    parent_group_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, ge=0)


class InventoryGroupUpdate(BaseModel):
    group_name: Optional[str] = None
    parent_group_id: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class InventoryGroupResponse(BaseModel):
    id: int
    company_id: int
    group_name: str
    parent_group_id: Optional[int] = None
    description: Optional[str] = None
    is_active: bool
    sort_order: int
    item_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stock Transfer Schemas
class StockTransferCreate(BaseModel):
    transfer_number: str = Field(..., min_length=1, max_length=100)
    from_location: str = Field(..., min_length=1, max_length=100)
    to_location: str = Field(..., min_length=1, max_length=100)
    transfer_date: date
    expected_delivery_date: Optional[date] = None
    status: str = Field(default="pending", regex="^(pending|in_transit|delivered|cancelled)$")
    notes: Optional[str] = Field(None, max_length=500)
    transfer_items: List[Dict[str, Any]] = Field(..., min_items=1)


class StockTransferUpdate(BaseModel):
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    transfer_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class StockTransferResponse(BaseModel):
    id: int
    company_id: int
    transfer_number: str
    from_location: str
    to_location: str
    transfer_date: date
    expected_delivery_date: Optional[date] = None
    status: str
    notes: Optional[str] = None
    total_items: int
    total_quantity: Decimal
    total_value: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Analytics Schemas
class InventoryAnalyticsResponse(BaseModel):
    total_items: int
    active_items: int
    out_of_stock_items: int
    low_stock_items: int
    total_stock_value: Decimal
    average_stock_value: Decimal
    top_selling_items: List[Dict[str, Any]]
    slow_moving_items: List[Dict[str, Any]]
    stock_turnover_ratio: Decimal
    stock_aging_analysis: Dict[str, Any]
    category_wise_analysis: Dict[str, Any]
    monthly_movements: List[Dict[str, Any]]


# Stock Reorder Schemas
class StockReorderRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    reorder_quantity: Decimal = Field(..., gt=0)
    supplier_id: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)


class StockReorderResponse(BaseModel):
    id: int
    item_id: int
    variant_id: Optional[int] = None
    reorder_quantity: Decimal
    supplier_id: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Import/Export Schemas
class InventoryImportRequest(BaseModel):
    import_type: str = Field(..., regex="^(items|stock_movements|variants)$")
    file_path: str
    mapping: Dict[str, str] = Field(..., description="Column mapping")
    options: Dict[str, Any] = Field(default_factory=dict)


class InventoryImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]
    warnings: List[str]


class InventoryExportRequest(BaseModel):
    export_type: str = Field(..., regex="^(items|stock_movements|analytics|low_stock)$")
    item_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    format: str = Field(default="csv", regex="^(csv|excel|json)$")
    include_inactive: bool = Field(default=False)


# Stock Valuation Schemas
class StockValuationRequest(BaseModel):
    valuation_method: str = Field(..., regex="^(fifo|lifo|weighted_average|standard_cost)$")
    valuation_date: date
    include_zero_stock: bool = Field(default=False)
    category_ids: Optional[List[int]] = None


class StockValuationResponse(BaseModel):
    valuation_method: str
    valuation_date: date
    total_value: Decimal
    item_count: int
    valuation_details: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True