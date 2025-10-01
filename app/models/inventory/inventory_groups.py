# backend/app/models/inventory_groups.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class InventoryGroup(BaseModel):
    """Inventory Groups for organizing items"""
    __tablename__ = "inventory_group"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('inventory_group.id'), nullable=True)
    group_code = Column(String(50), unique=True, nullable=False)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent_group = relationship("InventoryGroup", remote_side=[BaseModel.id], back_populates="child_groups")
    child_groups = relationship("InventoryGroup", back_populates="parent_group")
    items = relationship("Item", back_populates="inventory_group")
    
    def __repr__(self):
        return f"<InventoryGroup(name='{self.name}', code='{self.group_code}')>"

class InventoryAttribute(BaseModel):
    """Inventory Attributes for item characteristics"""
    __tablename__ = "inventory_attribute"
    
    name = Column(String(100), nullable=False)
    attribute_type = Column(String(50), nullable=False)  # text, number, select, color, size
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # For select type attributes
    options = Column(Text, nullable=True)  # JSON string of options
    
    # Relationships
    item_attributes = relationship("ItemAttribute", back_populates="attribute")
    
    def __repr__(self):
        return f"<InventoryAttribute(name='{self.name}', type='{self.attribute_type}')>"

class InventoryVariant(BaseModel):
    """Inventory Variants for item variations"""
    __tablename__ = "inventory_variant"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_name = Column(String(200), nullable=False)
    variant_code = Column(String(100), nullable=True)
    barcode = Column(String(50), nullable=True)
    sku = Column(String(100), nullable=True)
    
    # Pricing
    cost_price = Column(Numeric(10, 2), nullable=True)
    selling_price = Column(Numeric(10, 2), nullable=True)
    mrp = Column(Numeric(10, 2), nullable=True)
    
    # Inventory
    current_stock = Column(Numeric(10, 2), default=0)
    minimum_stock = Column(Numeric(10, 2), default=0)
    maximum_stock = Column(Numeric(10, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Relationships
    item = relationship("Item", back_populates="variants")
    variant_attributes = relationship("ItemVariantAttribute", back_populates="variant")
    
    def __repr__(self):
        return f"<InventoryVariant(name='{self.variant_name}', item_id={self.item_id})>"

class ItemVariantAttribute(BaseModel):
    """Item Variant Attributes linking variants to attribute values"""
    __tablename__ = "item_variant_attribute"
    
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=False)
    attribute_id = Column(Integer, ForeignKey('inventory_attribute.id'), nullable=False)
    attribute_value = Column(String(200), nullable=False)
    
    # Relationships
    variant = relationship("InventoryVariant", back_populates="variant_attributes")
    attribute = relationship("InventoryAttribute", back_populates="item_attributes")
    
    def __repr__(self):
        return f"<ItemVariantAttribute(variant_id={self.variant_id}, attribute_id={self.attribute_id})>"

class SeasonalPlan(BaseModel):
    """Seasonal Planning for inventory management"""
    __tablename__ = "seasonal_plan"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    season_start_date = Column(DateTime, nullable=False)
    season_end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Planning parameters
    target_sales = Column(Numeric(12, 2), nullable=True)
    target_margin = Column(Numeric(5, 2), nullable=True)  # Percentage
    planned_inventory_turnover = Column(Numeric(5, 2), nullable=True)
    
    # Relationships
    seasonal_items = relationship("SeasonalItem", back_populates="seasonal_plan")
    
    def __repr__(self):
        return f"<SeasonalPlan(name='{self.name}', start='{self.season_start_date}')>"

class SeasonalItem(BaseModel):
    """Seasonal Items for planning"""
    __tablename__ = "seasonal_item"
    
    seasonal_plan_id = Column(Integer, ForeignKey('seasonal_plan.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    
    # Planning data
    planned_quantity = Column(Numeric(10, 2), nullable=False)
    planned_sales = Column(Numeric(12, 2), nullable=True)
    planned_margin = Column(Numeric(5, 2), nullable=True)
    priority = Column(Integer, default=1)  # 1=High, 2=Medium, 3=Low
    
    # Actual performance
    actual_quantity = Column(Numeric(10, 2), default=0)
    actual_sales = Column(Numeric(12, 2), default=0)
    actual_margin = Column(Numeric(5, 2), default=0)
    
    # Relationships
    seasonal_plan = relationship("SeasonalPlan", back_populates="seasonal_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<SeasonalItem(plan_id={self.seasonal_plan_id}, item_id={self.item_id})>"