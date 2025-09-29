# backend/app/api/endpoints/enhanced_item_master.py
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
from ...services.enhanced_item_master_service import enhanced_item_master_service

router = APIRouter()

# Pydantic schemas for HSN Code
class HSNCodeCreateRequest(BaseModel):
    hsn_code: str
    description: str
    gst_rate: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    
    @validator('hsn_code')
    def validate_hsn_code(cls, v):
        if not v or len(v) < 4:
            raise ValueError('HSN code must be at least 4 characters')
        return v
    
    @validator('gst_rate')
    def validate_gst_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('GST rate must be between 0 and 100')
        return v

class HSNCodeResponse(BaseModel):
    id: int
    company_id: int
    hsn_code: str
    description: str
    gst_rate: Decimal
    cgst_rate: Decimal
    sgst_rate: Decimal
    igst_rate: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Barcode
class BarcodeCreateRequest(BaseModel):
    item_id: int
    barcode: str
    barcode_type: str = 'EAN13'
    variant_id: Optional[int] = None
    is_primary: bool = False
    
    @validator('barcode')
    def validate_barcode(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Barcode must be at least 3 characters')
        return v

class BarcodeResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    variant_id: Optional[int] = None
    barcode: str
    barcode_type: str
    is_primary: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Specifications
class ItemSpecificationCreateRequest(BaseModel):
    item_id: int
    specification_name: str
    specification_value: str
    specification_unit: Optional[str] = None
    display_order: int = 0

class ItemSpecificationResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    specification_name: str
    specification_value: str
    specification_unit: Optional[str] = None
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Images
class ItemImageCreateRequest(BaseModel):
    item_id: int
    image_url: str
    image_type: str = 'product'
    variant_id: Optional[int] = None
    display_order: int = 0
    is_primary: bool = False
    alt_text: Optional[str] = None

class ItemImageResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    variant_id: Optional[int] = None
    image_url: str
    image_type: str
    display_order: int
    is_primary: bool
    alt_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Pricing
class ItemPricingCreateRequest(BaseModel):
    item_id: int
    price_type: str
    price: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    variant_id: Optional[int] = None

class ItemPricingResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    variant_id: Optional[int] = None
    price_type: str
    price: Decimal
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Categories
class ItemCategoryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    category_code: Optional[str] = None
    display_order: int = 0

class ItemCategoryResponse(BaseModel):
    id: int
    company_id: int
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    category_code: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Brands
class ItemBrandCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    brand_code: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None

class ItemBrandResponse(BaseModel):
    id: int
    company_id: int
    name: str
    description: Optional[str] = None
    brand_code: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Item Reviews
class ItemReviewCreateRequest(BaseModel):
    item_id: int
    rating: int
    title: Optional[str] = None
    review_text: Optional[str] = None
    customer_id: Optional[int] = None
    is_verified: bool = False

class ItemReviewResponse(BaseModel):
    id: int
    company_id: int
    item_id: int
    customer_id: Optional[int] = None
    rating: int
    title: Optional[str] = None
    review_text: Optional[str] = None
    is_verified: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# HSN Code Endpoints
@router.post("/hsn-codes", response_model=HSNCodeResponse)
async def create_hsn_code(
    hsn_data: HSNCodeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Create new HSN code"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        hsn_code = enhanced_item_master_service.create_hsn_code(
            db=db,
            company_id=company_id,
            hsn_code=hsn_data.hsn_code,
            description=hsn_data.description,
            gst_rate=hsn_data.gst_rate,
            effective_from=hsn_data.effective_from,
            effective_to=hsn_data.effective_to,
            user_id=current_user.id
        )
        
        return hsn_code
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create HSN code: {str(e)}"
        )

@router.get("/hsn-codes", response_model=List[HSNCodeResponse])
async def get_hsn_codes(
    company_id: int = Query(...),
    search_term: Optional[str] = Query(None),
    gst_rate: Optional[Decimal] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get HSN codes"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    hsn_codes = enhanced_item_master_service.get_hsn_codes(
        db=db,
        company_id=company_id,
        search_term=search_term,
        gst_rate=gst_rate,
        is_active=is_active
    )
    
    return hsn_codes

# Barcode Endpoints
@router.post("/barcodes", response_model=BarcodeResponse)
async def create_barcode(
    barcode_data: BarcodeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Create new barcode"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        barcode = enhanced_item_master_service.create_barcode(
            db=db,
            company_id=company_id,
            item_id=barcode_data.item_id,
            barcode=barcode_data.barcode,
            barcode_type=barcode_data.barcode_type,
            variant_id=barcode_data.variant_id,
            is_primary=barcode_data.is_primary,
            user_id=current_user.id
        )
        
        return barcode
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create barcode: {str(e)}"
        )

@router.get("/barcodes/search")
async def search_item_by_barcode(
    barcode: str = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Search item by barcode"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    item = enhanced_item_master_service.get_item_by_barcode(
        db=db,
        company_id=company_id,
        barcode=barcode
    )
    
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found for barcode"
        )
    
    return {
        "item": {
            "id": item.id,
            "name": item.name,
            "barcode": barcode,
            "price": item.selling_price,
            "stock": item.current_stock
        }
    }

@router.get("/barcodes/{item_id}", response_model=List[BarcodeResponse])
async def get_item_barcodes(
    item_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item barcodes"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    barcodes = enhanced_item_master_service.get_item_barcodes(
        db=db,
        company_id=company_id,
        item_id=item_id
    )
    
    return barcodes

# Item Specifications Endpoints
@router.post("/specifications", response_model=ItemSpecificationResponse)
async def add_item_specification(
    spec_data: ItemSpecificationCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Add item specification"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        specification = enhanced_item_master_service.add_item_specification(
            db=db,
            company_id=company_id,
            item_id=spec_data.item_id,
            specification_name=spec_data.specification_name,
            specification_value=spec_data.specification_value,
            specification_unit=spec_data.specification_unit,
            display_order=spec_data.display_order,
            user_id=current_user.id
        )
        
        return specification
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item specification: {str(e)}"
        )

@router.get("/specifications/{item_id}", response_model=List[ItemSpecificationResponse])
async def get_item_specifications(
    item_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item specifications"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    specifications = enhanced_item_master_service.get_item_specifications(
        db=db,
        company_id=company_id,
        item_id=item_id
    )
    
    return specifications

# Item Images Endpoints
@router.post("/images", response_model=ItemImageResponse)
async def add_item_image(
    image_data: ItemImageCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Add item image"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        image = enhanced_item_master_service.add_item_image(
            db=db,
            company_id=company_id,
            item_id=image_data.item_id,
            image_url=image_data.image_url,
            image_type=image_data.image_type,
            variant_id=image_data.variant_id,
            display_order=image_data.display_order,
            is_primary=image_data.is_primary,
            alt_text=image_data.alt_text,
            user_id=current_user.id
        )
        
        return image
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item image: {str(e)}"
        )

@router.get("/images/{item_id}", response_model=List[ItemImageResponse])
async def get_item_images(
    item_id: int,
    company_id: int = Query(...),
    image_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item images"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    images = enhanced_item_master_service.get_item_images(
        db=db,
        company_id=company_id,
        item_id=item_id,
        image_type=image_type
    )
    
    return images

# Item Pricing Endpoints
@router.post("/pricing", response_model=ItemPricingResponse)
async def add_item_pricing(
    pricing_data: ItemPricingCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Add item pricing"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        pricing = enhanced_item_master_service.add_item_pricing(
            db=db,
            company_id=company_id,
            item_id=pricing_data.item_id,
            price_type=pricing_data.price_type,
            price=pricing_data.price,
            effective_from=pricing_data.effective_from,
            effective_to=pricing_data.effective_to,
            variant_id=pricing_data.variant_id,
            user_id=current_user.id
        )
        
        return pricing
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item pricing: {str(e)}"
        )

@router.get("/pricing/{item_id}", response_model=List[ItemPricingResponse])
async def get_item_pricing(
    item_id: int,
    company_id: int = Query(...),
    price_type: Optional[str] = Query(None),
    as_on_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item pricing"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    pricing = enhanced_item_master_service.get_item_pricing(
        db=db,
        company_id=company_id,
        item_id=item_id,
        price_type=price_type,
        as_on_date=as_on_date
    )
    
    return pricing

# Item Categories Endpoints
@router.post("/categories", response_model=ItemCategoryResponse)
async def create_item_category(
    category_data: ItemCategoryCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Create item category"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        category = enhanced_item_master_service.create_item_category(
            db=db,
            company_id=company_id,
            name=category_data.name,
            description=category_data.description,
            parent_id=category_data.parent_id,
            category_code=category_data.category_code,
            display_order=category_data.display_order,
            user_id=current_user.id
        )
        
        return category
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create item category: {str(e)}"
        )

@router.get("/categories", response_model=List[ItemCategoryResponse])
async def get_item_categories(
    company_id: int = Query(...),
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item categories"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    categories = enhanced_item_master_service.get_item_categories(
        db=db,
        company_id=company_id,
        parent_id=parent_id,
        is_active=is_active
    )
    
    return categories

# Item Brands Endpoints
@router.post("/brands", response_model=ItemBrandResponse)
async def create_item_brand(
    brand_data: ItemBrandCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Create item brand"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        brand = enhanced_item_master_service.create_item_brand(
            db=db,
            company_id=company_id,
            name=brand_data.name,
            description=brand_data.description,
            brand_code=brand_data.brand_code,
            logo_url=brand_data.logo_url,
            website=brand_data.website,
            user_id=current_user.id
        )
        
        return brand
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create item brand: {str(e)}"
        )

@router.get("/brands", response_model=List[ItemBrandResponse])
async def get_item_brands(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item brands"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    brands = enhanced_item_master_service.get_item_brands(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    
    return brands

# Item Reviews Endpoints
@router.post("/reviews", response_model=ItemReviewResponse)
async def add_item_review(
    review_data: ItemReviewCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Add item review"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        review = enhanced_item_master_service.add_item_review(
            db=db,
            company_id=company_id,
            item_id=review_data.item_id,
            rating=review_data.rating,
            title=review_data.title,
            review_text=review_data.review_text,
            customer_id=review_data.customer_id,
            is_verified=review_data.is_verified,
            user_id=current_user.id
        )
        
        return review
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item review: {str(e)}"
        )

@router.get("/reviews/{item_id}", response_model=List[ItemReviewResponse])
async def get_item_reviews(
    item_id: int,
    company_id: int = Query(...),
    is_approved: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item reviews"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    reviews = enhanced_item_master_service.get_item_reviews(
        db=db,
        company_id=company_id,
        item_id=item_id,
        is_approved=is_approved
    )
    
    return reviews

@router.get("/reviews/{item_id}/rating-summary")
async def get_item_rating_summary(
    item_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get item rating summary"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    rating_summary = enhanced_item_master_service.get_item_rating_summary(
        db=db,
        company_id=company_id,
        item_id=item_id
    )
    
    return rating_summary

# Item Wishlist Endpoints
@router.post("/wishlist")
async def add_to_wishlist(
    item_id: int = Query(...),
    customer_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Add item to wishlist"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        wishlist_item = enhanced_item_master_service.add_to_wishlist(
            db=db,
            company_id=company_id,
            item_id=item_id,
            customer_id=customer_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Item added to wishlist successfully",
            "wishlist_item_id": wishlist_item.id
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item to wishlist: {str(e)}"
        )

@router.get("/wishlist/{customer_id}")
async def get_customer_wishlist(
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.view")),
    db: Session = Depends(get_db)
):
    """Get customer wishlist"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    items = enhanced_item_master_service.get_customer_wishlist(
        db=db,
        company_id=company_id,
        customer_id=customer_id
    )
    
    return {
        "customer_id": customer_id,
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "price": item.selling_price,
                "image": item.image_url if hasattr(item, 'image_url') else None
            }
            for item in items
        ],
        "total_items": len(items)
    }

@router.delete("/wishlist/{item_id}/{customer_id}")
async def remove_from_wishlist(
    item_id: int,
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("item_master.manage")),
    db: Session = Depends(get_db)
):
    """Remove item from wishlist"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    success = enhanced_item_master_service.remove_from_wishlist(
        db=db,
        company_id=company_id,
        item_id=item_id,
        customer_id=customer_id
    )
    
    if success:
        return {"message": "Item removed from wishlist successfully"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Item not found in wishlist"
        )