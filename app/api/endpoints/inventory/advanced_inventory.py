# backend/app/api/endpoints/advanced_inventory.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.advanced_inventory_service import advanced_inventory_service

router = APIRouter()

# Pydantic schemas for Inventory Groups
class InventoryGroupCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    group_code: Optional[str] = None
    display_order: int = 0
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Group name must be at least 2 characters')
        return v

class InventoryGroupResponse(BaseModel):
    id: int
    company_id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    group_code: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Inventory Attributes
class InventoryAttributeCreateRequest(BaseModel):
    name: str
    attribute_type: str
    description: Optional[str] = None
    is_required: bool = False
    options: Optional[List[str]] = None
    display_order: int = 0
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Attribute name must be at least 2 characters')
        return v
    
    @validator('attribute_type')
    def validate_attribute_type(cls, v):
        valid_types = ['text', 'number', 'select', 'color', 'size']
        if v not in valid_types:
            raise ValueError(f'Attribute type must be one of: {", ".join(valid_types)}')
        return v

class InventoryAttributeResponse(BaseModel):
    id: int
    company_id: int
    name: str
    attribute_type: str
    description: Optional[str] = None
    is_required: bool
    is_active: bool
    display_order: int
    options: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Inventory Variants
class InventoryVariantCreateRequest(BaseModel):
    item_id: int
    variant_name: str
    variant_code: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    current_stock: Decimal = 0
    minimum_stock: Decimal = 0
    maximum_stock: Optional[Decimal] = None
    is_default: bool = False

class InventoryVariantResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    variant_name: str
    variant_code: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    mrp: Optional[Decimal] = None
    current_stock: Decimal
    minimum_stock: Decimal
    maximum_stock: Optional[Decimal] = None
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Seasonal Planning
class SeasonalPlanCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    season_start_date: datetime
    season_end_date: datetime
    target_sales: Optional[Decimal] = None
    target_margin: Optional[Decimal] = None
    planned_inventory_turnover: Optional[Decimal] = None

class SeasonalItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    planned_quantity: Decimal = 0
    planned_sales: Optional[Decimal] = None
    planned_margin: Optional[Decimal] = None
    priority: int = 1

# Inventory Groups Endpoints
@router.post("/groups", response_model=InventoryGroupResponse)
async def create_inventory_group(
    group_data: InventoryGroupCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Create new inventory group"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        group = advanced_inventory_service.create_inventory_group(
            db=db,
            company_id=company_id,
            name=group_data.name,
            description=group_data.description,
            parent_id=group_data.parent_id,
            group_code=group_data.group_code,
            display_order=group_data.display_order,
            user_id=current_user.id
        )
        
        return group
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create inventory group: {str(e)}"
        )

@router.get("/groups/hierarchy", response_model=dict)
async def get_inventory_group_hierarchy(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get inventory group hierarchy"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    hierarchy = advanced_inventory_service.get_inventory_group_hierarchy(
        db=db,
        company_id=company_id
    )
    
    return hierarchy

# Inventory Attributes Endpoints
@router.post("/attributes", response_model=InventoryAttributeResponse)
async def create_inventory_attribute(
    attribute_data: InventoryAttributeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Create new inventory attribute"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        attribute = advanced_inventory_service.create_inventory_attribute(
            db=db,
            company_id=company_id,
            name=attribute_data.name,
            attribute_type=attribute_data.attribute_type,
            description=attribute_data.description,
            is_required=attribute_data.is_required,
            options=attribute_data.options,
            display_order=attribute_data.display_order,
            user_id=current_user.id
        )
        
        return attribute
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create inventory attribute: {str(e)}"
        )

@router.get("/attributes", response_model=List[InventoryAttributeResponse])
async def get_inventory_attributes(
    company_id: int = Query(...),
    attribute_type: Optional[str] = Query(None),
    is_required: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get inventory attributes"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    attributes = advanced_inventory_service.get_inventory_attributes(
        db=db,
        company_id=company_id,
        attribute_type=attribute_type,
        is_required=is_required
    )
    
    return attributes

# Inventory Variants Endpoints
@router.post("/variants", response_model=InventoryVariantResponse)
async def create_inventory_variant(
    variant_data: InventoryVariantCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Create new inventory variant"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        variant = advanced_inventory_service.create_inventory_variant(
            db=db,
            company_id=company_id,
            item_id=variant_data.item_id,
            variant_name=variant_data.variant_name,
            variant_code=variant_data.variant_code,
            barcode=variant_data.barcode,
            sku=variant_data.sku,
            cost_price=variant_data.cost_price,
            selling_price=variant_data.selling_price,
            mrp=variant_data.mrp,
            current_stock=variant_data.current_stock,
            minimum_stock=variant_data.minimum_stock,
            maximum_stock=variant_data.maximum_stock,
            is_default=variant_data.is_default,
            user_id=current_user.id
        )
        
        return variant
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create inventory variant: {str(e)}"
        )

@router.get("/variants/{item_id}", response_model=List[InventoryVariantResponse])
async def get_item_variants(
    item_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get variants for an item"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    variants = advanced_inventory_service.get_item_variants(
        db=db,
        company_id=company_id,
        item_id=item_id
    )
    
    return variants

@router.put("/variants/{variant_id}/attributes")
async def update_variant_attributes(
    variant_id: int,
    attributes: List[dict],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Update variant attributes"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        variant_attributes = advanced_inventory_service.update_variant_attributes(
            db=db,
            company_id=company_id,
            variant_id=variant_id,
            attributes=attributes,
            user_id=current_user.id
        )
        
        return {
            "message": "Variant attributes updated successfully",
            "attributes_count": len(variant_attributes)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update variant attributes: {str(e)}"
        )

# Seasonal Planning Endpoints
@router.post("/seasonal-plans")
async def create_seasonal_plan(
    plan_data: SeasonalPlanCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Create new seasonal plan"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        plan = advanced_inventory_service.create_seasonal_plan(
            db=db,
            company_id=company_id,
            name=plan_data.name,
            description=plan_data.description,
            season_start_date=plan_data.season_start_date,
            season_end_date=plan_data.season_end_date,
            target_sales=plan_data.target_sales,
            target_margin=plan_data.target_margin,
            planned_inventory_turnover=plan_data.planned_inventory_turnover,
            user_id=current_user.id
        )
        
        return {
            "message": "Seasonal plan created successfully",
            "plan_id": plan.id,
            "plan_name": plan.name
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create seasonal plan: {str(e)}"
        )

@router.post("/seasonal-plans/{plan_id}/items")
async def add_item_to_seasonal_plan(
    plan_id: int,
    item_data: SeasonalItemCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.manage")),
    db: Session = Depends(get_db)
):
    """Add item to seasonal plan"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        seasonal_item = advanced_inventory_service.add_item_to_seasonal_plan(
            db=db,
            company_id=company_id,
            seasonal_plan_id=plan_id,
            item_id=item_data.item_id,
            variant_id=item_data.variant_id,
            planned_quantity=item_data.planned_quantity,
            planned_sales=item_data.planned_sales,
            planned_margin=item_data.planned_margin,
            priority=item_data.priority,
            user_id=current_user.id
        )
        
        return {
            "message": "Item added to seasonal plan successfully",
            "seasonal_item_id": seasonal_item.id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item to seasonal plan: {str(e)}"
        )

@router.get("/seasonal-plans/{plan_id}/analysis")
async def get_seasonal_plan_analysis(
    plan_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get seasonal plan analysis"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        analysis = advanced_inventory_service.get_seasonal_plan_analysis(
            db=db,
            company_id=company_id,
            seasonal_plan_id=plan_id
        )
        
        return analysis
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get seasonal plan analysis: {str(e)}"
        )

# Analytics and Reports Endpoints
@router.get("/analytics")
async def get_inventory_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get inventory analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = advanced_inventory_service.get_inventory_analytics(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return analytics

@router.get("/recommendations")
async def get_inventory_recommendations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get inventory recommendations"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    recommendations = advanced_inventory_service.get_inventory_recommendations(
        db=db,
        company_id=company_id
    )
    
    return {
        "recommendations": recommendations,
        "total_recommendations": len(recommendations)
    }

# Attribute Types Endpoint
@router.get("/attribute-types")
async def get_attribute_types(
    current_user: User = Depends(require_permission("inventory.view"))
):
    """Get available attribute types"""
    
    attribute_types = [
        {
            "type": "text",
            "name": "Text",
            "description": "Free text input",
            "examples": ["Brand", "Model", "Description"]
        },
        {
            "type": "number",
            "name": "Number",
            "description": "Numeric input",
            "examples": ["Weight", "Length", "Width", "Height"]
        },
        {
            "type": "select",
            "name": "Select",
            "description": "Dropdown selection",
            "examples": ["Category", "Type", "Status"]
        },
        {
            "type": "color",
            "name": "Color",
            "description": "Color selection",
            "examples": ["Red", "Blue", "Green", "Black"]
        },
        {
            "type": "size",
            "name": "Size",
            "description": "Size selection",
            "examples": ["S", "M", "L", "XL", "XXL"]
        }
    ]
    
    return {
        "attribute_types": attribute_types,
        "total_types": len(attribute_types)
    }