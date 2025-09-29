# backend/app/services/enhanced_item_master_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.enhanced_item_master import (
    HSNCode, Barcode, ItemSpecification, ItemImage, ItemPricing,
    ItemSupplier, ItemCategory, ItemBrand, ItemTag, ItemTagMapping,
    ItemReview, ItemWishlist
)
from ..models.item import Item
from ..models.supplier import Supplier
from ..models.customer import Customer

logger = logging.getLogger(__name__)

class EnhancedItemMasterService:
    """Service class for enhanced item master management"""
    
    def __init__(self):
        pass
    
    # HSN Code Management
    def create_hsn_code(
        self, 
        db: Session, 
        company_id: int,
        hsn_code: str,
        description: str,
        gst_rate: Decimal,
        effective_from: date,
        effective_to: Optional[date] = None,
        user_id: int = None
    ) -> HSNCode:
        """Create new HSN code"""
        
        # Check if HSN code already exists
        existing_hsn = db.query(HSNCode).filter(
            HSNCode.company_id == company_id,
            HSNCode.hsn_code == hsn_code
        ).first()
        
        if existing_hsn:
            raise ValueError(f"HSN code {hsn_code} already exists")
        
        # Calculate CGST, SGST, IGST rates
        cgst_rate = gst_rate / 2
        sgst_rate = gst_rate / 2
        igst_rate = gst_rate
        
        # Create HSN code
        hsn = HSNCode(
            company_id=company_id,
            hsn_code=hsn_code,
            description=description,
            gst_rate=gst_rate,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            effective_from=effective_from,
            effective_to=effective_to,
            created_by=user_id
        )
        
        db.add(hsn)
        db.commit()
        db.refresh(hsn)
        
        logger.info(f"HSN code created: {hsn_code}")
        
        return hsn
    
    def get_hsn_codes(
        self, 
        db: Session, 
        company_id: int,
        search_term: Optional[str] = None,
        gst_rate: Optional[Decimal] = None,
        is_active: Optional[bool] = None
    ) -> List[HSNCode]:
        """Get HSN codes"""
        
        query = db.query(HSNCode).filter(HSNCode.company_id == company_id)
        
        if search_term:
            query = query.filter(
                or_(
                    HSNCode.hsn_code.ilike(f"%{search_term}%"),
                    HSNCode.description.ilike(f"%{search_term}%")
                )
            )
        
        if gst_rate is not None:
            query = query.filter(HSNCode.gst_rate == gst_rate)
        
        if is_active is not None:
            query = query.filter(HSNCode.is_active == is_active)
        
        hsn_codes = query.order_by(HSNCode.hsn_code).all()
        
        return hsn_codes
    
    # Barcode Management
    def create_barcode(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        barcode: str,
        barcode_type: str = 'EAN13',
        variant_id: Optional[int] = None,
        is_primary: bool = False,
        user_id: int = None
    ) -> Barcode:
        """Create new barcode"""
        
        # Check if barcode already exists
        existing_barcode = db.query(Barcode).filter(
            Barcode.company_id == company_id,
            Barcode.barcode == barcode
        ).first()
        
        if existing_barcode:
            raise ValueError(f"Barcode {barcode} already exists")
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # If setting as primary, unset other primary barcodes for this item
        if is_primary:
            db.query(Barcode).filter(
                Barcode.item_id == item_id,
                Barcode.company_id == company_id,
                Barcode.is_primary == True
            ).update({"is_primary": False})
        
        # Create barcode
        barcode_obj = Barcode(
            company_id=company_id,
            item_id=item_id,
            variant_id=variant_id,
            barcode=barcode,
            barcode_type=barcode_type,
            is_primary=is_primary,
            created_by=user_id
        )
        
        db.add(barcode_obj)
        db.commit()
        db.refresh(barcode_obj)
        
        logger.info(f"Barcode created: {barcode}")
        
        return barcode_obj
    
    def get_item_by_barcode(
        self, 
        db: Session, 
        company_id: int,
        barcode: str
    ) -> Optional[Item]:
        """Get item by barcode"""
        
        barcode_obj = db.query(Barcode).filter(
            Barcode.company_id == company_id,
            Barcode.barcode == barcode,
            Barcode.is_active == True
        ).first()
        
        if not barcode_obj:
            return None
        
        return barcode_obj.item
    
    def get_item_barcodes(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> List[Barcode]:
        """Get all barcodes for an item"""
        
        barcodes = db.query(Barcode).filter(
            Barcode.company_id == company_id,
            Barcode.item_id == item_id,
            Barcode.is_active == True
        ).order_by(Barcode.is_primary.desc(), Barcode.created_at).all()
        
        return barcodes
    
    # Item Specifications Management
    def add_item_specification(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        specification_name: str,
        specification_value: str,
        specification_unit: Optional[str] = None,
        display_order: int = 0,
        user_id: int = None
    ) -> ItemSpecification:
        """Add item specification"""
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Create specification
        specification = ItemSpecification(
            company_id=company_id,
            item_id=item_id,
            specification_name=specification_name,
            specification_value=specification_value,
            specification_unit=specification_unit,
            display_order=display_order,
            created_by=user_id
        )
        
        db.add(specification)
        db.commit()
        db.refresh(specification)
        
        logger.info(f"Item specification added: {specification_name}")
        
        return specification
    
    def get_item_specifications(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> List[ItemSpecification]:
        """Get item specifications"""
        
        specifications = db.query(ItemSpecification).filter(
            ItemSpecification.company_id == company_id,
            ItemSpecification.item_id == item_id
        ).order_by(ItemSpecification.display_order, ItemSpecification.specification_name).all()
        
        return specifications
    
    # Item Images Management
    def add_item_image(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        image_url: str,
        image_type: str = 'product',
        variant_id: Optional[int] = None,
        display_order: int = 0,
        is_primary: bool = False,
        alt_text: Optional[str] = None,
        user_id: int = None
    ) -> ItemImage:
        """Add item image"""
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # If setting as primary, unset other primary images for this item
        if is_primary:
            db.query(ItemImage).filter(
                ItemImage.item_id == item_id,
                ItemImage.company_id == company_id,
                ItemImage.is_primary == True
            ).update({"is_primary": False})
        
        # Create image
        image = ItemImage(
            company_id=company_id,
            item_id=item_id,
            variant_id=variant_id,
            image_url=image_url,
            image_type=image_type,
            display_order=display_order,
            is_primary=is_primary,
            alt_text=alt_text,
            created_by=user_id
        )
        
        db.add(image)
        db.commit()
        db.refresh(image)
        
        logger.info(f"Item image added: {image_url}")
        
        return image
    
    def get_item_images(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        image_type: Optional[str] = None
    ) -> List[ItemImage]:
        """Get item images"""
        
        query = db.query(ItemImage).filter(
            ItemImage.company_id == company_id,
            ItemImage.item_id == item_id
        )
        
        if image_type:
            query = query.filter(ItemImage.image_type == image_type)
        
        images = query.order_by(ItemImage.display_order, ItemImage.created_at).all()
        
        return images
    
    # Item Pricing Management
    def add_item_pricing(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        price_type: str,
        price: Decimal,
        effective_from: date,
        effective_to: Optional[date] = None,
        variant_id: Optional[int] = None,
        user_id: int = None
    ) -> ItemPricing:
        """Add item pricing"""
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Create pricing
        pricing = ItemPricing(
            company_id=company_id,
            item_id=item_id,
            variant_id=variant_id,
            price_type=price_type,
            price=price,
            effective_from=effective_from,
            effective_to=effective_to,
            created_by=user_id
        )
        
        db.add(pricing)
        db.commit()
        db.refresh(pricing)
        
        logger.info(f"Item pricing added: {price_type} - {price}")
        
        return pricing
    
    def get_item_pricing(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        price_type: Optional[str] = None,
        as_on_date: Optional[date] = None
    ) -> List[ItemPricing]:
        """Get item pricing"""
        
        query = db.query(ItemPricing).filter(
            ItemPricing.company_id == company_id,
            ItemPricing.item_id == item_id,
            ItemPricing.is_active == True
        )
        
        if price_type:
            query = query.filter(ItemPricing.price_type == price_type)
        
        if as_on_date:
            query = query.filter(
                ItemPricing.effective_from <= as_on_date,
                or_(
                    ItemPricing.effective_to.is_(None),
                    ItemPricing.effective_to >= as_on_date
                )
            )
        
        pricing = query.order_by(ItemPricing.effective_from.desc()).all()
        
        return pricing
    
    # Item Supplier Management
    def add_item_supplier(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        supplier_id: int,
        supplier_item_code: Optional[str] = None,
        supplier_item_name: Optional[str] = None,
        supplier_price: Optional[Decimal] = None,
        minimum_order_quantity: Decimal = 1,
        lead_time_days: int = 0,
        is_primary: bool = False,
        user_id: int = None
    ) -> ItemSupplier:
        """Add item supplier"""
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Validate supplier
        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.company_id == company_id
        ).first()
        
        if not supplier:
            raise ValueError("Supplier not found")
        
        # If setting as primary, unset other primary suppliers for this item
        if is_primary:
            db.query(ItemSupplier).filter(
                ItemSupplier.item_id == item_id,
                ItemSupplier.company_id == company_id,
                ItemSupplier.is_primary == True
            ).update({"is_primary": False})
        
        # Create item supplier
        item_supplier = ItemSupplier(
            company_id=company_id,
            item_id=item_id,
            supplier_id=supplier_id,
            supplier_item_code=supplier_item_code,
            supplier_item_name=supplier_item_name,
            supplier_price=supplier_price,
            minimum_order_quantity=minimum_order_quantity,
            lead_time_days=lead_time_days,
            is_primary=is_primary,
            created_by=user_id
        )
        
        db.add(item_supplier)
        db.commit()
        db.refresh(item_supplier)
        
        logger.info(f"Item supplier added: {supplier.name}")
        
        return item_supplier
    
    def get_item_suppliers(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> List[ItemSupplier]:
        """Get item suppliers"""
        
        suppliers = db.query(ItemSupplier).filter(
            ItemSupplier.company_id == company_id,
            ItemSupplier.item_id == item_id,
            ItemSupplier.is_active == True
        ).order_by(ItemSupplier.is_primary.desc(), ItemSupplier.supplier_item_name).all()
        
        return suppliers
    
    # Item Categories Management
    def create_item_category(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        category_code: Optional[str] = None,
        display_order: int = 0,
        user_id: int = None
    ) -> ItemCategory:
        """Create item category"""
        
        # Generate category code if not provided
        if not category_code:
            category_code = name.lower().replace(' ', '_')
        
        # Check if category code already exists
        existing_category = db.query(ItemCategory).filter(
            ItemCategory.company_id == company_id,
            ItemCategory.category_code == category_code
        ).first()
        
        if existing_category:
            raise ValueError(f"Category code {category_code} already exists")
        
        # Validate parent category if provided
        if parent_id:
            parent_category = db.query(ItemCategory).filter(
                ItemCategory.id == parent_id,
                ItemCategory.company_id == company_id
            ).first()
            
            if not parent_category:
                raise ValueError("Parent category not found")
        
        # Create category
        category = ItemCategory(
            company_id=company_id,
            name=name,
            description=description,
            parent_id=parent_id,
            category_code=category_code,
            display_order=display_order,
            created_by=user_id
        )
        
        db.add(category)
        db.commit()
        db.refresh(category)
        
        logger.info(f"Item category created: {name}")
        
        return category
    
    def get_item_categories(
        self, 
        db: Session, 
        company_id: int,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[ItemCategory]:
        """Get item categories"""
        
        query = db.query(ItemCategory).filter(ItemCategory.company_id == company_id)
        
        if parent_id is not None:
            query = query.filter(ItemCategory.parent_id == parent_id)
        
        if is_active is not None:
            query = query.filter(ItemCategory.is_active == is_active)
        
        categories = query.order_by(ItemCategory.display_order, ItemCategory.name).all()
        
        return categories
    
    # Item Brands Management
    def create_item_brand(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        description: Optional[str] = None,
        brand_code: Optional[str] = None,
        logo_url: Optional[str] = None,
        website: Optional[str] = None,
        user_id: int = None
    ) -> ItemBrand:
        """Create item brand"""
        
        # Generate brand code if not provided
        if not brand_code:
            brand_code = name.lower().replace(' ', '_')
        
        # Check if brand code already exists
        existing_brand = db.query(ItemBrand).filter(
            ItemBrand.company_id == company_id,
            ItemBrand.brand_code == brand_code
        ).first()
        
        if existing_brand:
            raise ValueError(f"Brand code {brand_code} already exists")
        
        # Create brand
        brand = ItemBrand(
            company_id=company_id,
            name=name,
            description=description,
            brand_code=brand_code,
            logo_url=logo_url,
            website=website,
            created_by=user_id
        )
        
        db.add(brand)
        db.commit()
        db.refresh(brand)
        
        logger.info(f"Item brand created: {name}")
        
        return brand
    
    def get_item_brands(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None
    ) -> List[ItemBrand]:
        """Get item brands"""
        
        query = db.query(ItemBrand).filter(ItemBrand.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(ItemBrand.is_active == is_active)
        
        brands = query.order_by(ItemBrand.name).all()
        
        return brands
    
    # Item Tags Management
    def create_item_tag(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        user_id: int = None
    ) -> ItemTag:
        """Create item tag"""
        
        # Create tag
        tag = ItemTag(
            company_id=company_id,
            name=name,
            description=description,
            color=color,
            created_by=user_id
        )
        
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        logger.info(f"Item tag created: {name}")
        
        return tag
    
    def add_item_tag(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        tag_id: int,
        user_id: int = None
    ) -> ItemTagMapping:
        """Add tag to item"""
        
        # Check if mapping already exists
        existing_mapping = db.query(ItemTagMapping).filter(
            ItemTagMapping.company_id == company_id,
            ItemTagMapping.item_id == item_id,
            ItemTagMapping.tag_id == tag_id
        ).first()
        
        if existing_mapping:
            raise ValueError("Tag already assigned to item")
        
        # Create mapping
        mapping = ItemTagMapping(
            company_id=company_id,
            item_id=item_id,
            tag_id=tag_id,
            created_by=user_id
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        
        logger.info(f"Tag added to item: {tag_id}")
        
        return mapping
    
    def get_item_tags(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> List[ItemTag]:
        """Get item tags"""
        
        tags = db.query(ItemTag).join(
            ItemTagMapping, ItemTag.id == ItemTagMapping.tag_id
        ).filter(
            ItemTagMapping.company_id == company_id,
            ItemTagMapping.item_id == item_id,
            ItemTag.is_active == True
        ).order_by(ItemTag.name).all()
        
        return tags
    
    # Item Reviews Management
    def add_item_review(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        rating: int,
        title: Optional[str] = None,
        review_text: Optional[str] = None,
        customer_id: Optional[int] = None,
        is_verified: bool = False,
        user_id: int = None
    ) -> ItemReview:
        """Add item review"""
        
        # Validate rating
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Validate item
        item = db.query(Item).filter(
            Item.id == item_id,
            Item.company_id == company_id
        ).first()
        
        if not item:
            raise ValueError("Item not found")
        
        # Create review
        review = ItemReview(
            company_id=company_id,
            item_id=item_id,
            customer_id=customer_id,
            rating=rating,
            title=title,
            review_text=review_text,
            is_verified=is_verified,
            created_by=user_id
        )
        
        db.add(review)
        db.commit()
        db.refresh(review)
        
        logger.info(f"Item review added: {rating} stars")
        
        return review
    
    def get_item_reviews(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        is_approved: Optional[bool] = None
    ) -> List[ItemReview]:
        """Get item reviews"""
        
        query = db.query(ItemReview).filter(
            ItemReview.company_id == company_id,
            ItemReview.item_id == item_id
        )
        
        if is_approved is not None:
            query = query.filter(ItemReview.is_approved == is_approved)
        
        reviews = query.order_by(ItemReview.created_at.desc()).all()
        
        return reviews
    
    def get_item_rating_summary(
        self, 
        db: Session, 
        company_id: int,
        item_id: int
    ) -> Dict:
        """Get item rating summary"""
        
        reviews = db.query(ItemReview).filter(
            ItemReview.company_id == company_id,
            ItemReview.item_id == item_id,
            ItemReview.is_approved == True
        ).all()
        
        if not reviews:
            return {
                "average_rating": 0,
                "total_reviews": 0,
                "rating_breakdown": {}
            }
        
        total_reviews = len(reviews)
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / total_reviews
        
        # Rating breakdown
        rating_breakdown = {}
        for i in range(1, 6):
            count = sum(1 for review in reviews if review.rating == i)
            rating_breakdown[i] = count
        
        return {
            "average_rating": round(average_rating, 1),
            "total_reviews": total_reviews,
            "rating_breakdown": rating_breakdown
        }
    
    # Item Wishlist Management
    def add_to_wishlist(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        customer_id: int,
        user_id: int = None
    ) -> ItemWishlist:
        """Add item to wishlist"""
        
        # Check if already in wishlist
        existing_wishlist = db.query(ItemWishlist).filter(
            ItemWishlist.company_id == company_id,
            ItemWishlist.item_id == item_id,
            ItemWishlist.customer_id == customer_id
        ).first()
        
        if existing_wishlist:
            raise ValueError("Item already in wishlist")
        
        # Create wishlist item
        wishlist_item = ItemWishlist(
            company_id=company_id,
            item_id=item_id,
            customer_id=customer_id,
            created_by=user_id
        )
        
        db.add(wishlist_item)
        db.commit()
        db.refresh(wishlist_item)
        
        logger.info(f"Item added to wishlist: {item_id}")
        
        return wishlist_item
    
    def get_customer_wishlist(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int
    ) -> List[Item]:
        """Get customer wishlist"""
        
        items = db.query(Item).join(
            ItemWishlist, Item.id == ItemWishlist.item_id
        ).filter(
            ItemWishlist.company_id == company_id,
            ItemWishlist.customer_id == customer_id,
            Item.is_active == True
        ).order_by(ItemWishlist.created_at.desc()).all()
        
        return items
    
    def remove_from_wishlist(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        customer_id: int
    ) -> bool:
        """Remove item from wishlist"""
        
        wishlist_item = db.query(ItemWishlist).filter(
            ItemWishlist.company_id == company_id,
            ItemWishlist.item_id == item_id,
            ItemWishlist.customer_id == customer_id
        ).first()
        
        if not wishlist_item:
            return False
        
        db.delete(wishlist_item)
        db.commit()
        
        logger.info(f"Item removed from wishlist: {item_id}")
        
        return True

# Global service instance
enhanced_item_master_service = EnhancedItemMasterService()