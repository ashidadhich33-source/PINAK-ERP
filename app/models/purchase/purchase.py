# backend/app/models/purchase.py
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Boolean, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class PurchaseBill(BaseModel):
    """Purchase bill from supplier"""
    __tablename__ = "purchase_bill"
    
    # Bill Information
    pb_no = Column(String(50), unique=True, nullable=False, index=True)
    pb_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    pb_series_id = Column(Integer, ForeignKey('bill_series.id'))
    
    # Supplier Information
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier_bill_no = Column(String(50))
    supplier_bill_date = Column(Date)
    
    # Payment Information
    payment_mode = Column(String(20), default='credit')  # cash or credit
    
    # Tax Information
    tax_region = Column(String(20), default='local')  # local or inter
    reverse_charge = Column(Boolean, default=False)
    
    # Amount Information
    total_taxable = Column(Numeric(12, 2), default=0)
    total_cgst = Column(Numeric(10, 2), default=0)
    total_sgst = Column(Numeric(10, 2), default=0)
    total_igst = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(12, 2), default=0)
    
    # Status
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    
    # Usage Tracking
    used_in_pos = Column(Boolean, default=False)
    used_in_sales = Column(Boolean, default=False)
    pos_transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=True)
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=True)
    modification_locked = Column(Boolean, default=False)
    
    # Relationships
    supplier = relationship("Supplier")
    items = relationship("PurchaseBillItem", back_populates="purchase_bill")
    series = relationship("BillSeries")

class PurchaseBillItem(BaseModel):
    """Purchase bill line items"""
    __tablename__ = "purchase_bill_item"
    
    purchase_bill_id = Column(Integer, ForeignKey('purchase_bill.id'), nullable=False)
    
    # Item Information
    barcode = Column(String(50), nullable=False)
    style_code = Column(String(100), nullable=False)
    size = Column(String(20))
    hsn = Column(String(20))
    
    # Quantity and Pricing
    qty = Column(Integer, default=1)
    basic_rate = Column(Numeric(10, 2), nullable=False)
    
    # Tax Information
    gst_rate = Column(Numeric(5, 2), default=0)
    cgst_rate = Column(Numeric(5, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    
    # Amount Calculations
    line_taxable = Column(Numeric(12, 2), nullable=False)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # MRP Information
    mrp = Column(Numeric(10, 2))
    
    # Usage Tracking
    used_in_pos = Column(Boolean, default=False)
    used_in_sales = Column(Boolean, default=False)
    pos_transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=True)
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=True)
    modification_locked = Column(Boolean, default=False)
    
    # Relationships
    purchase_bill = relationship("PurchaseBill", back_populates="items")

class PurchaseReturn(BaseModel):
    """Purchase return to supplier"""
    __tablename__ = "purchase_return_basic"
    
    # Return Information
    pr_no = Column(String(50), unique=True, nullable=False, index=True)
    pr_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    pr_series_id = Column(Integer, ForeignKey('bill_series.id'))
    
    # Supplier Information
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    supplier_bill_no = Column(String(50))
    supplier_bill_date = Column(Date)
    
    # Tax Information
    tax_region = Column(String(20), default='local')
    
    # Amount Information
    total_taxable = Column(Numeric(12, 2), default=0)
    total_cgst = Column(Numeric(10, 2), default=0)
    total_sgst = Column(Numeric(10, 2), default=0)
    total_igst = Column(Numeric(10, 2), default=0)
    grand_total = Column(Numeric(12, 2), default=0)
    
    # Reason
    reason = Column(Text)
    
    # Relationships
    supplier = relationship("Supplier")
    items = relationship("PurchaseReturnItem", back_populates="purchase_return")
    series = relationship("BillSeries")

class PurchaseReturnItem(BaseModel):
    """Purchase return line items"""
    __tablename__ = "purchase_return_item_basic"
    
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    
    # Item Information
    barcode = Column(String(50), nullable=False)
    style_code = Column(String(100), nullable=False)
    size = Column(String(20))
    hsn = Column(String(20))
    
    # Return Details
    qty = Column(Integer, default=1)
    basic_rate = Column(Numeric(10, 2), nullable=False)
    
    # Tax Information
    gst_rate = Column(Numeric(5, 2), default=0)
    cgst_rate = Column(Numeric(5, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    
    # Amount Calculations
    line_taxable = Column(Numeric(12, 2), nullable=False)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    line_total = Column(Numeric(12, 2), nullable=False)
    
    # Relationships
    purchase_return = relationship("PurchaseReturn", back_populates="items")

class PurchaseOrder(BaseModel):
    """Purchase order to supplier"""
    __tablename__ = "purchase_order_basic"
    
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

class PurchaseOrderItem(BaseModel):
    """Purchase order line items"""
    __tablename__ = "purchase_order_item_basic"
    
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

class PurchaseInvoice(BaseModel):
    """Purchase invoice from supplier"""
    __tablename__ = "purchase_invoice_basic"
    
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

class PurchaseInvoiceItem(BaseModel):
    """Purchase invoice line items"""
    __tablename__ = "purchase_invoice_item_basic"
    
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
    
    # Batch Information
    batch_number = Column(String(50), nullable=True)
    expiry_date = Column(Date, nullable=True)
    
    # Relationships
    invoice = relationship("PurchaseInvoice", back_populates="invoice_items")
    item = relationship("Item")
