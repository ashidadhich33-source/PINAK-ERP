# backend/app/models/stock.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class StockLocation(BaseModel):
    __tablename__ = "stock_location"
    
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    is_main_location = Column(Boolean, default=False)
    
    # Relationships
    stock_items = relationship("StockItem", back_populates="location")
    stock_movements = relationship("StockMovement", back_populates="location")
    
    def __repr__(self):
        return f"<StockLocation(code='{self.code}', name='{self.name}')>"

class StockItem(BaseModel):
    __tablename__ = "stock_item"
    
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=False)
    
    # Stock quantities
    quantity = Column(Numeric(12, 3), default=0, nullable=False)
    reserved_quantity = Column(Numeric(12, 3), default=0, nullable=False)  # For pending orders
    available_quantity = Column(Numeric(12, 3), default=0, nullable=False)  # quantity - reserved
    
    # Cost tracking
    average_cost = Column(Numeric(10, 2), default=0, nullable=False)
    last_cost = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Last movement tracking
    last_movement_date = Column(DateTime, nullable=True)
    last_movement_type = Column(String(20), nullable=True)
    
    # Relationships
    item = relationship("Item")
    location = relationship("StockLocation", back_populates="stock_items")
    
    def update_available_quantity(self):
        """Update available quantity based on total and reserved"""
        self.available_quantity = self.quantity - self.reserved_quantity
    
    def __repr__(self):
        return f"<StockItem(item_id={self.item_id}, location_id={self.location_id}, qty={self.quantity})>"

class StockMovement(BaseModel):
    __tablename__ = "stock_movement"
    
    # Reference information
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=False)
    
    # Movement details
    movement_type = Column(String(30), nullable=False)  # in, out, adjustment, transfer, opening
    reference_type = Column(String(30), nullable=True)  # purchase, sales, adjustment, transfer
    reference_id = Column(Integer, nullable=True)  # ID of the reference document
    reference_number = Column(String(100), nullable=True)
    
    # Quantities
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    total_cost = Column(Numeric(12, 2), nullable=True)
    
    # Before and after quantities (for audit trail)
    quantity_before = Column(Numeric(12, 3), nullable=True)
    quantity_after = Column(Numeric(12, 3), nullable=True)
    
    # Additional information
    batch_number = Column(String(50), nullable=True)
    serial_number = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Movement date
    movement_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    item = relationship("Item", back_populates="stock_movements")
    location = relationship("StockLocation", back_populates="stock_movements")
    
    def __repr__(self):
        return f"<StockMovement(item_id={self.item_id}, type='{self.movement_type}', qty={self.quantity})>"

class StockAdjustment(BaseModel):
    __tablename__ = "stock_adjustment"
    
    # Document details
    adjustment_number = Column(String(50), unique=True, nullable=False)
    adjustment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=False)
    
    # Adjustment information
    adjustment_type = Column(String(20), nullable=False)  # increase, decrease, recount
    reason = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default='draft')  # draft, approved, cancelled
    approved_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Totals
    total_items = Column(Integer, default=0)
    total_adjustment_value = Column(Numeric(12, 2), default=0)
    
    # Relationships
    location = relationship("StockLocation")
    approved_by_user = relationship("User")
    adjustment_items = relationship("StockAdjustmentItem", back_populates="adjustment")
    
    def __repr__(self):
        return f"<StockAdjustment(number='{self.adjustment_number}', date='{self.adjustment_date}')>"

class StockAdjustmentItem(BaseModel):
    __tablename__ = "stock_adjustment_item"
    
    adjustment_id = Column(Integer, ForeignKey('stock_adjustment.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Quantities
    book_quantity = Column(Numeric(12, 3), nullable=False)  # System quantity
    physical_quantity = Column(Numeric(12, 3), nullable=False)  # Counted quantity
    adjustment_quantity = Column(Numeric(12, 3), nullable=False)  # Difference
    
    # Cost information
    unit_cost = Column(Numeric(10, 2), nullable=True)
    adjustment_value = Column(Numeric(12, 2), nullable=True)
    
    # Additional info
    batch_number = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Relationships
    adjustment = relationship("StockAdjustment", back_populates="adjustment_items")
    item = relationship("Item")
    
    def calculate_adjustment(self):
        """Calculate adjustment quantity and value"""
        self.adjustment_quantity = self.physical_quantity - self.book_quantity
        if self.unit_cost:
            self.adjustment_value = self.adjustment_quantity * self.unit_cost
    
    def __repr__(self):
        return f"<StockAdjustmentItem(item_id={self.item_id}, adj_qty={self.adjustment_quantity})>"

class StockTransfer(BaseModel):
    __tablename__ = "stock_transfer"
    
    # Document details
    transfer_number = Column(String(50), unique=True, nullable=False)
    transfer_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Locations
    from_location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=False)
    to_location_id = Column(Integer, ForeignKey('stock_location.id'), nullable=False)
    
    # Status
    status = Column(String(20), default='draft')  # draft, in_transit, received, cancelled
    remarks = Column(Text, nullable=True)
    
    # Tracking
    sent_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    received_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    received_at = Column(DateTime, nullable=True)
    
    # Relationships
    from_location = relationship("StockLocation", foreign_keys=[from_location_id])
    to_location = relationship("StockLocation", foreign_keys=[to_location_id])
    transfer_items = relationship("StockTransferItem", back_populates="transfer")
    
    def __repr__(self):
        return f"<StockTransfer(number='{self.transfer_number}', status='{self.status}')>"

class StockTransferItem(BaseModel):
    __tablename__ = "stock_transfer_item"
    
    transfer_id = Column(Integer, ForeignKey('stock_transfer.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Quantities
    quantity_sent = Column(Numeric(12, 3), nullable=False)
    quantity_received = Column(Numeric(12, 3), nullable=True)
    
    # Cost
    unit_cost = Column(Numeric(10, 2), nullable=True)
    
    # Additional info
    batch_number = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Relationships
    transfer = relationship("StockTransfer", back_populates="transfer_items")
    item = relationship("Item")
    
    def __repr__(self):
        return f"<StockTransferItem(item_id={self.item_id}, qty_sent={self.quantity_sent})>"