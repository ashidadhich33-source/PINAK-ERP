# backend/app/models/enhanced_item_master.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class HSNCode(BaseModel):
    """HSN Code for GST compliance"""
    __tablename__ = "hsn_code"
    
    hsn_code = Column(String(10), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), nullable=False)
    sgst_rate = Column(Numeric(5, 2), nullable=False)
    igst_rate = Column(Numeric(5, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    items = relationship("Item", back_populates="hsn_code_ref")
    
    def __repr__(self):
        return f"<HSNCode(code='{self.hsn_code}', description='{self.description}')>"

class Barcode(BaseModel):
    """Barcode management for items"""
    __tablename__ = "barcode"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    barcode = Column(String(50), unique=True, nullable=False, index=True)
    barcode_type = Column(String(20), default='EAN13')  # EAN13, UPC, Code128, QR
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    item = relationship("Item", back_populates="barcodes")
    variant = relationship("InventoryVariant", back_populates="barcodes")
    
    def __repr__(self):
        return f"<Barcode(barcode='{self.barcode}', item_id={self.item_id})>"

class ItemSpecification(BaseModel):
    """Item specifications and technical details"""
    __tablename__ = "item_specification"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    specification_name = Column(String(100), nullable=False)
    specification_value = Column(String(500), nullable=False)
    specification_unit = Column(String(20), nullable=True)
    display_order = Column(Integer, default=0)
    
    # Relationships
    item = relationship("Item", back_populates="specifications")
    
    def __repr__(self):
        return f"<ItemSpecification(name='{self.specification_name}', value='{self.specification_value}')>"

class ItemImage(BaseModel):
    """Item images management"""
    __tablename__ = "item_image"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    image_url = Column(String(500), nullable=False)
    image_type = Column(String(20), default='product')  # product, thumbnail, gallery
    display_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    alt_text = Column(String(200), nullable=True)
    
    # Relationships
    item = relationship("Item", back_populates="images")
    variant = relationship("InventoryVariant", back_populates="images")
    
    def __repr__(self):
        return f"<ItemImage(url='{self.image_url}', type='{self.image_type}')>"

class ItemPricing(BaseModel):
    """Item pricing management"""
    __tablename__ = "item_pricing"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    price_type = Column(String(20), nullable=False)  # cost, selling, mrp, wholesale
    price = Column(Numeric(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    item = relationship("Item", back_populates="pricing")
    variant = relationship("InventoryVariant", back_populates="pricing")
    
    def __repr__(self):
        return f"<ItemPricing(type='{self.price_type}', price={self.price})>"

class ItemSupplier(BaseModel):
    """Item supplier relationships"""
    __tablename__ = "item_supplier"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier_item_code = Column(String(100), nullable=True)
    supplier_item_name = Column(String(200), nullable=True)
    supplier_price = Column(Numeric(10, 2), nullable=True)
    minimum_order_quantity = Column(Numeric(10, 2), default=1)
    lead_time_days = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    item = relationship("Item", back_populates="suppliers")
    supplier = relationship("Supplier", back_populates="items")
    
    def __repr__(self):
        return f"<ItemSupplier(item_id={self.item_id}, supplier_id={self.supplier_id})>"

class ItemCategory(BaseModel):
    """Item categories for classification"""
    __tablename__ = "enhanced_item_category"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('item_category.id'), nullable=True)
    category_code = Column(String(50), unique=True, nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent_category = relationship("ItemCategory", remote_side=[BaseModel.id], back_populates="child_categories")
    child_categories = relationship("ItemCategory", back_populates="parent_category")
    items = relationship("Item", back_populates="category")
    
    def __repr__(self):
        return f"<ItemCategory(name='{self.name}', code='{self.category_code}')>"

class ItemBrand(BaseModel):
    """Item brands for classification"""
    __tablename__ = "item_brand"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    brand_code = Column(String(50), unique=True, nullable=False)
    logo_url = Column(String(500), nullable=True)
    website = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    items = relationship("Item", back_populates="brand")
    
    def __repr__(self):
        return f"<ItemBrand(name='{self.name}', code='{self.brand_code}')>"

class ItemTag(BaseModel):
    """Item tags for flexible classification"""
    __tablename__ = "item_tag"
    
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, default=True)
    
    # Relationships
    item_tags = relationship("ItemTagMapping", back_populates="tag")
    
    def __repr__(self):
        return f"<ItemTag(name='{self.name}')>"

class ItemTagMapping(BaseModel):
    """Mapping between items and tags"""
    __tablename__ = "item_tag_mapping"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('item_tag.id'), nullable=False)
    
    # Relationships
    item = relationship("Item", back_populates="tag_mappings")
    tag = relationship("ItemTag", back_populates="item_tags")
    
    def __repr__(self):
        return f"<ItemTagMapping(item_id={self.item_id}, tag_id={self.tag_id})>"

class ItemReview(BaseModel):
    """Item reviews and ratings"""
    __tablename__ = "item_review"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(200), nullable=True)
    review_text = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=True)
    
    # Relationships
    item = relationship("Item", back_populates="reviews")
    customer = relationship("Customer", back_populates="item_reviews")
    
    def __repr__(self):
        return f"<ItemReview(item_id={self.item_id}, rating={self.rating})>"

class ItemWishlist(BaseModel):
    """Item wishlist for customers"""
    __tablename__ = "item_wishlist"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    
    # Relationships
    item = relationship("Item", back_populates="wishlist_items")
    customer = relationship("Customer", back_populates="wishlist_items")
    
    def __repr__(self):
        return f"<ItemWishlist(item_id={self.item_id}, customer_id={self.customer_id})>"