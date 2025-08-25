# backend/app/api/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
import io
import pandas as pd

from ...database import get_db
from ...models.item import Item, ItemCategory, Brand
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.stock_service import StockService

router = APIRouter()

# Pydantic schemas for request/response
class ItemCategoryResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True

class BrandResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ItemResponse(BaseModel):
    id: int
    barcode: str
    style_code: str
    sku: Optional[str] = None
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    mrp_inclusive: bool = True
    purchase_rate: Optional[Decimal] = None
    purchase_rate_inclusive: bool = False
    selling_price: Optional[Decimal] = None
    selling_price_inclusive: bool = True
    landed_cost: Optional[Decimal] = None
    margin_percent: Optional[Decimal] = None
    is_stockable: bool = True
    track_inventory: bool = True
    min_stock_level: Decimal = 0
    max_stock_level: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    uom: str = "PCS"
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    status: str = "active"
    is_service: bool = False
    is_serialized: bool = False
    allow_negative_stock: bool = False
    current_stock: Optional[Decimal] = None
    stock_value: Optional[Decimal] = None
    category_name: Optional[str] = None
    brand_name: Optional[str] = None

    class Config:
        from_attributes = True

class ItemCreateRequest(BaseModel):
    barcode: str
    style_code: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = 18.00
    mrp: Optional[Decimal] = None
    mrp_inclusive: bool = True
    purchase_rate: Optional[Decimal] = None
    purchase_rate_inclusive: bool = False
    selling_price: Optional[Decimal] = None
    selling_price_inclusive: bool = True
    landed_cost: Optional[Decimal] = None
    margin_percent: Optional[Decimal] = None
    is_stockable: bool = True
    track_inventory: bool = True
    min_stock_level: Decimal = 0
    max_stock_level: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    uom: str = "PCS"
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    is_service: bool = False
    is_serialized: bool = False
    allow_negative_stock: bool = False

    @validator('barcode')
    def barcode_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Barcode cannot be empty')
        return v.strip()

    @validator('style_code')
    def style_code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Style code cannot be empty')
        return v.strip()

class ItemUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    mrp_inclusive: Optional[bool] = None
    purchase_rate: Optional[Decimal] = None
    purchase_rate_inclusive: Optional[bool] = None
    selling_price: Optional[Decimal] = None
    selling_price_inclusive: Optional[bool] = None
    landed_cost: Optional[Decimal] = None
    margin_percent: Optional[Decimal] = None
    min_stock_level: Optional[Decimal] = None
    max_stock_level: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    status: Optional[str] = None
    allow_negative_stock: Optional[bool] = None

class CategoryCreateRequest(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None

class BrandCreateRequest(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None

# Item endpoints
@router.get("", response_model=List[ItemResponse])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in barcode, style_code, or name"),
    category_id: Optional[int] = Query(None),
    brand: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    low_stock: bool = Query(False, description="Show items with stock below minimum level"),
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get items with filtering and pagination"""
    
    query = db.query(Item)
    
    # Apply filters
    if search:
        search_filter = or_(
            Item.barcode.ilike(f"%{search}%"),
            Item.style_code.ilike(f"%{search}%"),
            Item.name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if category_id:
        query = query.filter(Item.category_id == category_id)
    
    if brand:
        query = query.filter(Item.brand.ilike(f"%{brand}%"))
    
    if status:
        query = query.filter(Item.status == status)
    
    # Get items
    items = query.offset(skip).limit(limit).all()
    
    # Convert to response format and add stock information
    stock_service = StockService()
    result = []
    
    for item in items:
        # Get current stock
        current_stock = stock_service.get_item_stock(db, item.id) if item.track_inventory else None
        
        # Skip if low_stock filter is applied and stock is not low
        if low_stock and current_stock is not None:
            if current_stock >= item.min_stock_level:
                continue
        
        # Get category and brand names
        category_name = None
        if item.category_id:
            category = db.query(ItemCategory).filter(ItemCategory.id == item.category_id).first()
            category_name = category.display_name if category else None
        
        item_data = ItemResponse.from_orm(item)
        item_data.current_stock = current_stock
        item_data.stock_value = (current_stock * item.landed_cost) if (current_stock and item.landed_cost) else 0
        item_data.category_name = category_name
        item_data.brand_name = item.brand
        
        result.append(item_data)
    
    return result

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get item by ID"""
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Get current stock and category name
    stock_service = StockService()
    current_stock = stock_service.get_item_stock(db, item.id) if item.track_inventory else None
    
    category_name = None
    if item.category_id:
        category = db.query(ItemCategory).filter(ItemCategory.id == item.category_id).first()
        category_name = category.display_name if category else None
    
    item_data = ItemResponse.from_orm(item)
    item_data.current_stock = current_stock
    item_data.stock_value = (current_stock * item.landed_cost) if (current_stock and item.landed_cost) else 0
    item_data.category_name = category_name
    item_data.brand_name = item.brand
    
    return item_data

@router.get("/barcode/{barcode}", response_model=ItemResponse)
async def get_item_by_barcode(
    barcode: str,
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get item by barcode (for POS scanning)"""
    
    item = db.query(Item).filter(Item.barcode == barcode).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Get current stock
    stock_service = StockService()
    current_stock = stock_service.get_item_stock(db, item.id) if item.track_inventory else None
    
    item_data = ItemResponse.from_orm(item)
    item_data.current_stock = current_stock
    item_data.stock_value = (current_stock * item.landed_cost) if (current_stock and item.landed_cost) else 0
    
    return item_data

@router.post("", response_model=ItemResponse)
async def create_item(
    item_data: ItemCreateRequest,
    current_user: User = Depends(require_permission("items.create")),
    db: Session = Depends(get_db)
):
    """Create new item"""
    
    # Check if barcode already exists
    existing_item = db.query(Item).filter(Item.barcode == item_data.barcode).first()
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item with this barcode already exists"
        )
    
    # Validate category if provided
    if item_data.category_id:
        category = db.query(ItemCategory).filter(ItemCategory.id == item_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID"
            )
    
    # Create item
    db_item = Item(
        **item_data.dict(),
        created_by=current_user.id
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Initialize stock if stockable
    if db_item.is_stockable and db_item.track_inventory:
        stock_service = StockService()
        stock_service.initialize_item_stock(db, db_item.id)
    
    return ItemResponse.from_orm(db_item)

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdateRequest,
    current_user: User = Depends(require_permission("items.edit")),
    db: Session = Depends(get_db)
):
    """Update item"""
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Validate category if provided
    if item_data.category_id:
        category = db.query(ItemCategory).filter(ItemCategory.id == item_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID"
            )
    
    # Update item fields
    update_data = item_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_by = current_user.id
    
    db.commit()
    db.refresh(item)
    
    return ItemResponse.from_orm(item)

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(require_permission("items.delete")),
    db: Session = Depends(get_db)
):
    """Delete item (soft delete by setting status to inactive)"""
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    # Check if item has stock or transactions
    stock_service = StockService()
    current_stock = stock_service.get_item_stock(db, item_id)
    
    if current_stock and current_stock > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete item with stock. Adjust stock to zero first."
        )
    
    # Soft delete
    item.status = 'inactive'
    item.is_active = False
    item.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Item deleted successfully"}

# Category endpoints
@router.get("/categories", response_model=List[ItemCategoryResponse])
async def get_categories(
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get all categories"""
    categories = db.query(ItemCategory).filter(ItemCategory.is_active == True).all()
    return [ItemCategoryResponse.from_orm(cat) for cat in categories]

@router.post("/categories", response_model=ItemCategoryResponse)
async def create_category(
    category_data: CategoryCreateRequest,
    current_user: User = Depends(require_permission("items.create")),
    db: Session = Depends(get_db)
):
    """Create new category"""
    
    # Check if category name already exists
    existing = db.query(ItemCategory).filter(ItemCategory.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    # Validate parent category if provided
    if category_data.parent_id:
        parent = db.query(ItemCategory).filter(ItemCategory.id == category_data.parent_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent category ID"
            )
    
    db_category = ItemCategory(
        **category_data.dict(),
        created_by=current_user.id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return ItemCategoryResponse.from_orm(db_category)

# Brand endpoints
@router.get("/brands", response_model=List[BrandResponse])
async def get_brands(
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get all brands"""
    brands = db.query(Brand).filter(Brand.is_active == True).all()
    return [BrandResponse.from_orm(brand) for brand in brands]

@router.post("/brands", response_model=BrandResponse)
async def create_brand(
    brand_data: BrandCreateRequest,
    current_user: User = Depends(require_permission("items.create")),
    db: Session = Depends(get_db)
):
    """Create new brand"""
    
    # Check if brand name already exists
    existing = db.query(Brand).filter(Brand.name == brand_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this name already exists"
        )
    
    db_brand = Brand(
        **brand_data.dict(),
        created_by=current_user.id
    )
    
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    
    return BrandResponse.from_orm(db_brand)

# Import/Export endpoints
@router.post("/import-excel")
async def import_items_from_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("items.import")),
    db: Session = Depends(get_db)
):
    """Import items from Excel file"""
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Read Excel file
        content = await file.read()
        df = pd.read_excel(io.BytesIO(content))
        
        # Validate required columns
        required_columns = ['barcode', 'style_code', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        created_items = 0
        updated_items = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if item exists
                existing_item = db.query(Item).filter(Item.barcode == row['barcode']).first()
                
                # Prepare item data
                item_data = {
                    'barcode': str(row['barcode']).strip(),
                    'style_code': str(row['style_code']).strip(),
                    'name': str(row['name']).strip(),
                    'description': str(row.get('description', '')).strip() if pd.notna(row.get('description')) else None,
                    'color': str(row.get('color', '')).strip() if pd.notna(row.get('color')) else None,
                    'size': str(row.get('size', '')).strip() if pd.notna(row.get('size')) else None,
                    'brand': str(row.get('brand', '')).strip() if pd.notna(row.get('brand')) else None,
                    'gender': str(row.get('gender', '')).strip() if pd.notna(row.get('gender')) else None,
                    'hsn_code': str(row.get('hsn_code', '')).strip() if pd.notna(row.get('hsn_code')) else None,
                    'gst_rate': float(row.get('gst_rate', 18.0)) if pd.notna(row.get('gst_rate')) else 18.0,
                    'mrp': float(row.get('mrp', 0)) if pd.notna(row.get('mrp')) else None,
                    'purchase_rate': float(row.get('purchase_rate', 0)) if pd.notna(row.get('purchase_rate')) else None,
                    'selling_price': float(row.get('selling_price', 0)) if pd.notna(row.get('selling_price')) else None,
                    'uom': str(row.get('uom', 'PCS')).strip() if pd.notna(row.get('uom')) else 'PCS',
                    'status': 'active'
                }
                
                if existing_item:
                    # Update existing item
                    for key, value in item_data.items():
                        if key != 'barcode':  # Don't update barcode
                            setattr(existing_item, key, value)
                    existing_item.updated_by = current_user.id
                    updated_items += 1
                else:
                    # Create new item
                    item_data['created_by'] = current_user.id
                    new_item = Item(**item_data)
                    db.add(new_item)
                    created_items += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        # Commit changes if no errors
        if not errors:
            db.commit()
        else:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Import failed. Errors: {'; '.join(errors[:5])}"  # Show first 5 errors
            )
        
        return {
            "message": f"Import completed successfully",
            "created_items": created_items,
            "updated_items": updated_items,
            "total_processed": created_items + updated_items
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/export-excel")
async def export_items_to_excel(
    current_user: User = Depends(require_permission("items.export")),
    db: Session = Depends(get_db)
):
    """Export items to Excel file"""
    
    from fastapi.responses import StreamingResponse
    import xlsxwriter
    
    # Get all active items
    items = db.query(Item).filter(Item.status == 'active').all()
    
    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Items')
    
    # Define headers
    headers = [
        'Barcode', 'Style Code', 'Name', 'Description', 'Color', 'Size', 
        'Brand', 'Gender', 'HSN Code', 'GST Rate', 'MRP', 'Purchase Rate', 
        'Selling Price', 'UOM', 'Current Stock', 'Status'
    ]
    
    # Write headers
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Write data
    stock_service = StockService()
    for row, item in enumerate(items, start=1):
        current_stock = stock_service.get_item_stock(db, item.id) if item.track_inventory else 0
        
        data = [
            item.barcode,
            item.style_code,
            item.name,
            item.description or '',
            item.color or '',
            item.size or '',
            item.brand or '',
            item.gender or '',
            item.hsn_code or '',
            float(item.gst_rate) if item.gst_rate else 0,
            float(item.mrp) if item.mrp else 0,
            float(item.purchase_rate) if item.purchase_rate else 0,
            float(item.selling_price) if item.selling_price else 0,
            item.uom,
            float(current_stock) if current_stock else 0,
            item.status
        ]
        
        for col, value in enumerate(data):
            worksheet.write(row, col, value)
    
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.read()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=items_export.xlsx"}
    )

@router.get("/low-stock")
async def get_low_stock_items(
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get items with stock below minimum level"""
    
    stock_service = StockService()
    low_stock_items = []
    
    # Get all trackable items
    items = db.query(Item).filter(
        and_(Item.track_inventory == True, Item.status == 'active')
    ).all()
    
    for item in items:
        current_stock = stock_service.get_item_stock(db, item.id)
        if current_stock is not None and current_stock <= item.min_stock_level:
            low_stock_items.append({
                "id": item.id,
                "barcode": item.barcode,
                "name": item.name,
                "current_stock": float(current_stock),
                "min_stock_level": float(item.min_stock_level),
                "shortage": float(item.min_stock_level - current_stock)
            })
    
    return {
        "items": low_stock_items,
        "total_count": len(low_stock_items)
    }

@router.get("/stock-valuation")
async def get_stock_valuation(
    current_user: User = Depends(require_permission("items.view")),
    db: Session = Depends(get_db)
):
    """Get stock valuation report"""
    
    stock_service = StockService()
    total_items = 0
    total_quantity = 0
    total_value = 0
    
    items_valuation = []
    
    # Get all stockable items
    items = db.query(Item).filter(
        and_(Item.track_inventory == True, Item.status == 'active')
    ).all()
    
    for item in items:
        current_stock = stock_service.get_item_stock(db, item.id)
        if current_stock is not None and current_stock > 0:
            item_value = current_stock * (item.landed_cost or item.purchase_rate or 0)
            
            items_valuation.append({
                "id": item.id,
                "barcode": item.barcode,
                "name": item.name,
                "current_stock": float(current_stock),
                "unit_cost": float(item.landed_cost or item.purchase_rate or 0),
                "total_value": float(item_value)
            })
            
            total_items += 1
            total_quantity += current_stock
            total_value += item_value
    
    return {
        "summary": {
            "total_items": total_items,
            "total_quantity": float(total_quantity),
            "total_value": float(total_value)
        },
        "items": sorted(items_valuation, key=lambda x: x['total_value'], reverse=True)
    }