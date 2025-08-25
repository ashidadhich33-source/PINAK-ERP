# backend/app/models/sales.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class SalesOrder(BaseModel):
    __tablename__ = "sales_order"
    
    # Document Information
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_date = Column(Date, nullable=True)
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    customer_name = Column(String(200), nullable=False)  # Denormalized for performance
    customer_mobile = Column(String(15), nullable=True)
    
    # Status
    status = Column(String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    
    # Financial Information
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    order_items = relationship("SalesOrderItem", back_populates="order")
    
    def calculate_totals(self):
        """Calculate order totals from line items"""
        self.subtotal = sum(item.line_total for item in self.order_items)
        if self.discount_percent > 0:
            self.discount_amount = self.subtotal * (self.discount_percent / 100)
        total_before_tax = self.subtotal - self.discount_amount
        self.tax_amount = sum(item.tax_amount for item in self.order_items)
        self.total_amount = total_before_tax + self.tax_amount
    
    def __repr__(self):
        return f"<SalesOrder(number='{self.order_number}', customer='{self.customer_name}')>"

class SalesOrderItem(BaseModel):
    __tablename__ = "sales_order_item"
    
    order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Item Information (denormalized)
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    
    # Quantity and Pricing
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Tax Information
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    
    # Fulfillment
    delivered_quantity = Column(Numeric(12, 3), default=0)
    pending_quantity = Column(Numeric(12, 3), default=0)
    
    # Relationships
    order = relationship("SalesOrder", back_populates="order_items")
    item = relationship("Item")
    
    def calculate_line_total(self):
        """Calculate line total including discount and tax"""
        base_amount = self.quantity * self.unit_price
        if self.discount_percent > 0:
            self.discount_amount = base_amount * (self.discount_percent / 100)
        self.line_total = base_amount - self.discount_amount
        self.tax_amount = self.line_total * (self.tax_rate / 100)
        self.pending_quantity = self.quantity - self.delivered_quantity
    
    def __repr__(self):
        return f"<SalesOrderItem(order_id={self.order_id}, item='{self.item_name}')>"

class SalesInvoice(BaseModel):
    __tablename__ = "sales_invoice"
    
    # Document Information
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=True)
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    customer_name = Column(String(200), nullable=False)
    customer_address = Column(Text, nullable=True)
    customer_gst = Column(String(15), nullable=True)
    customer_mobile = Column(String(15), nullable=True)
    
    # Reference
    order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=True)
    reference_number = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(20), default='pending')  # pending, paid, overdue, cancelled
    payment_status = Column(String(20), default='pending')  # pending, partial, paid
    
    # Financial Information
    subtotal = Column(Numeric(12, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    round_off = Column(Numeric(5, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    paid_amount = Column(Numeric(12, 2), default=0)
    balance_amount = Column(Numeric(12, 2), default=0)
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)
    
    # POS Information
    is_pos_sale = Column(Boolean, default=False)
    cashier_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="sales_invoices")
    order = relationship("SalesOrder")
    invoice_items = relationship("SalesInvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="sales_invoice")
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        self.subtotal = sum(item.line_total for item in self.invoice_items)
        self.tax_amount = sum(item.tax_amount for item in self.invoice_items)
        total_before_round = self.subtotal - self.discount_amount + self.tax_amount
        self.total_amount = total_before_round + self.round_off
        self.balance_amount = self.total_amount - self.paid_amount
    
    def __repr__(self):
        return f"<SalesInvoice(number='{self.invoice_number}', amount={self.total_amount})>"

class SalesInvoiceItem(BaseModel):
    __tablename__ = "sales_invoice_item"
    
    invoice_id = Column(Integer, ForeignKey('sales_invoice.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    
    # Item Information
    item_code = Column(String(50), nullable=False)
    item_name = Column(String(200), nullable=False)
    hsn_code = Column(String(20), nullable=True)
    
    # Quantity and Pricing
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_percent = Column(Numeric(5, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Tax Information
    cgst_rate = Column(Numeric(5, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    
    # Serial/Batch Information
    serial_numbers = Column(Text, nullable=True)  # JSON array
    batch_number = Column(String(50), nullable=True)
    
    # Relationships
    invoice = relationship("SalesInvoice", back_populates="invoice_items")
    item = relationship("Item")
    
    def calculate_tax(self):
        """Calculate GST amounts"""
        taxable_amount = self.line_total
        self.cgst_amount = taxable_amount * (self.cgst_rate / 100)
        self.sgst_amount = taxable_amount * (self.sgst_rate / 100)
        self.igst_amount = taxable_amount * (self.igst_rate / 100)
        self.tax_amount = self.cgst_amount + self.sgst_amount + self.igst_amount
    
    def __repr__(self):
        return f"<SalesInvoiceItem(invoice_id={self.invoice_id}, item='{self.item_name}')>"