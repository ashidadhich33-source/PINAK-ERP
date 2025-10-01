# backend/app/models/item.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..base import BaseModel

class ItemCategory(BaseModel):
    __tablename__ = "item_category"
    
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('item_category.id'), nullable=True)
    
    # Self-referencing relationship for subcategories
    parent = relationship("ItemCategory", remote_side=[BaseModel.id])
    children = relationship("ItemCategory", back_populates="parent")
    items = relationship("Item", back_populates="category")
    
    def __repr__(self):
        return f"<ItemCategory(name='{self.name}')>"

class Brand(BaseModel):
    __tablename__ = "brand"
    
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("Item", back_populates="brand_obj")
    
    def __repr__(self):
        return f"<Brand(name='{self.name}')>"

class Item(BaseModel):
    __tablename__ = "item"
    
    # Primary identifiers
    barcode = Column(String(50), unique=True, nullable=False, index=True)
    style_code = Column(String(100), nullable=False, index=True)
    sku = Column(String(100), nullable=True, unique=True)
    
    # Product details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Variants
    color = Column(String(50), nullable=True)
    size = Column(String(20), nullable=True)
    material = Column(String(100), nullable=True)
    
    # Classification
    category_id = Column(Integer, ForeignKey('item_category.id'), nullable=True)
    brand = Column(String(100), nullable=True)
    brand_id = Column(Integer, ForeignKey('brand.id'), nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, unisex, kids
    
    # Tax Information
    hsn_code = Column(String(20), nullable=True)  # HSN/SAC code for GST
    gst_rate = Column(Numeric(5, 2), nullable=True, default=0.00)
    cess_rate = Column(Numeric(5, 2), nullable=True, default=0.00)
    
    # Pricing
    mrp = Column(Numeric(10, 2), nullable=True)  # Maximum Retail Price
    mrp_inclusive = Column(Boolean, default=True)  # Whether MRP includes tax
    purchase_rate = Column(Numeric(10, 2), nullable=True)
    purchase_rate_inclusive = Column(Boolean, default=False)
    selling_price = Column(Numeric(10, 2), nullable=True)
    selling_price_inclusive = Column(Boolean, default=True)
    
    # Cost and Margin
    landed_cost = Column(Numeric(10, 2), nullable=True)
    margin_percent = Column(Numeric(5, 2), nullable=True)
    
    # Inventory Settings
    is_stockable = Column(Boolean, default=True)
    track_inventory = Column(Boolean, default=True)
    min_stock_level = Column(Numeric(10, 2), default=0)
    max_stock_level = Column(Numeric(10, 2), nullable=True)
    reorder_level = Column(Numeric(10, 2), nullable=True)
    
    # Unit of Measure
    uom = Column(String(20), default="PCS")  # Unit of Measure: PCS, KG, LTR, etc.
    weight = Column(Numeric(8, 3), nullable=True)  # in KG
    dimensions = Column(String(50), nullable=True)  # L x W x H
    
    # Status and Flags
    status = Column(String(20), default='active')  # active, inactive, discontinued
    is_service = Column(Boolean, default=False)
    is_serialized = Column(Boolean, default=False)
    allow_negative_stock = Column(Boolean, default=False)
    
    # Images and Files
    image_path = Column(String(500), nullable=True)
    additional_images = Column(Text, nullable=True)  # JSON array of image paths
    
    # Supplier Information
    preferred_supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    supplier_item_code = Column(String(100), nullable=True)
    
    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    brand_obj = relationship("Brand", back_populates="items")
    preferred_supplier = relationship("Supplier", back_populates="preferred_items")
    stock_movements = relationship("StockMovement", back_populates="item")
    creator = relationship("User", foreign_keys=[BaseModel.created_by])
    
    # Current stock (computed property)
    @property
    def current_stock(self):
        """Get current stock quantity"""
        if not self.track_inventory:
            return None
        # This will be calculated from stock movements
        return 0  # Placeholder
    
    @property
    def stock_value(self):
        """Get current stock value"""
        if self.current_stock and self.landed_cost:
            return self.current_stock * self.landed_cost
        return 0
    
    def calculate_selling_price_from_margin(self):
        """Calculate selling price based on cost and margin"""
        if self.landed_cost and self.margin_percent:
            return self.landed_cost * (1 + self.margin_percent / 100)
        return None
    
    def __repr__(self):
        return f"<Item(barcode='{self.barcode}', name='{self.name}')>"