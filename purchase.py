from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class PurchaseOrder(BaseModel):
    __tablename__ = "purchase_order"
    
    # Document Information
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_date = Column(Date, nullable=True)
    
    # Supplier Information
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier_name = Column(String(200), nullable=False)
    
    # Status
    status = Column(String(20), default='pending')  # pending, confirmed, received, cancelled
    
    # Financial Information
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    order_items = relationship("PurchaseOrderItem", back_populates="order")
    
    def __repr__(self):
        return f"<PurchaseOrder(number='{self.order_number}', supplier='{self.supplier_name}')>"

class PurchaseOrderItem(BaseModel):
    __tablename__ = "purchase_order_item"
    
    order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Item Information
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    
    # Quantity and Pricing
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Tax Information
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    
    # Receipt tracking
    received_quantity = Column(Numeric(12, 3), default=0)
    pending_quantity = Column(Numeric(12, 3), default=0)
    
    # Relationships
    order = relationship("PurchaseOrder", back_populates="order_items")
    item = relationship("Item")
    
    def __repr__(self):
        return f"<PurchaseOrderItem(order_id={self.order_id}, item='{self.item_name}')>"

class PurchaseInvoice(BaseModel):
    __tablename__ = "purchase_invoice"
    
    # Document Information
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Supplier Information
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier_name = Column(String(200), nullable=False)
    supplier_gst = Column(String(15), nullable=True)
    
    # Financial Information
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    paid_amount = Column(Numeric(12, 2), default=0)
    balance_amount = Column(Numeric(12, 2), default=0)
    
    # Status
    status = Column(String(20), default='pending')  # pending, paid, overdue
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_invoices")
    invoice_items = relationship("PurchaseInvoiceItem", back_populates="invoice")
    
    def __repr__(self):
        return f"<PurchaseInvoice(number='{self.invoice_number}', amount={self.total_amount})>"

class PurchaseInvoiceItem(BaseModel):
    __tablename__ = "purchase_invoice_item"
    
    invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Item Information
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    
    # Quantity and Pricing
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Tax Information
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    
    # Relationships
    invoice = relationship("PurchaseInvoice", back_populates="invoice_items")
    item = relationship("Item")
    
    def __repr__(self):
        return f"<PurchaseInvoiceItem(invoice_id={self.invoice_id}, item='{self.item_name}')>"