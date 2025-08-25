# backend/app/models/sales.py
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Boolean, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class BillSeries(BaseModel):
    """Bill series configuration for different document types"""
    __tablename__ = "bill_series"
    
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(100))
    prefix = Column(String(10), nullable=False)
    next_no = Column(Integer, default=1)
    width = Column(Integer, default=5)
    fy = Column(String(10))  # Financial Year
    default_tax_region = Column(String(20), default='local')
    active = Column(Boolean, default=True)

class Sale(BaseModel):
    """POS Sale transaction"""
    __tablename__ = "sale"
    
    # Bill Information
    bill_no = Column(String(50), unique=True, nullable=False, index=True)
    bill_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    series_id = Column(Integer, ForeignKey('bill_series.id'))
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    customer_mobile = Column(String(15), nullable=True)
    
    # Staff Information
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    cashier_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Tax Information
    tax_region = Column(String(20), default='local')  # local or inter
    
    # Amount Information (All Inclusive)
    gross_incl = Column(Numeric(12, 2), default=0)
    discount_incl = Column(Numeric(10, 2), default=0)
    coupon_incl = Column(Numeric(10, 2), default=0)
    base_excl = Column(Numeric(12, 2), default=0)  # Base amount excluding tax
    tax_amt_info = Column(Numeric(10, 2), default=0)  # Total tax amount
    
    # Loyalty Points
    redeem_points = Column(Integer, default=0)
    redeem_value = Column(Numeric(10, 2), default=0)
    earned_points = Column(Integer, default=0)
    
    # Return Credit
    return_credit_used = Column(String(50), nullable=True)  # Return credit ID
    return_credit_used_value = Column(Numeric(10, 2), default=0)
    
    # Final Amount
    final_payable = Column(Numeric(12, 2), default=0)
    round_off = Column(Numeric(5, 2), default=0)
    
    # Status
    status = Column(String(20), default='completed')  # completed, cancelled
    
    # Relationships
    series = relationship("BillSeries")
    customer = relationship("Customer")
    staff = relationship("Staff")
    cashier = relationship("User", foreign_keys=[cashier_id])
    items = relationship("SaleItem", back_populates="sale")
    payments = relationship("SalePayment", back_populates="sale")

class SaleItem(BaseModel):
    """Sale line items"""
    __tablename__ = "sale_item"
    
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=False)
    
    # Item Information
    barcode = Column(String(50), nullable=False)
    style_code = Column(String(100), nullable=False)
    color = Column(String(50))
    size = Column(String(20))
    hsn = Column(String(20))
    
    # Quantity and Pricing
    qty = Column(Integer, default=1)
    mrp_incl = Column(Numeric(10, 2), nullable=False)
    disc_pct = Column(Numeric(5, 2), default=0)
    line_inclusive = Column(Numeric(12, 2), nullable=False)
    
    # Tax Information
    gst_rate = Column(Numeric(5, 2), default=0)
    cgst_rate = Column(Numeric(5, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    
    # Base and Tax Amounts (for info)
    base_excl_info = Column(Numeric(10, 2))
    tax_info = Column(Numeric(10, 2))
    
    # Relationships
    sale = relationship("Sale", back_populates="items")

class SalePayment(BaseModel):
    """Sale payment details"""
    __tablename__ = "sale_payment"
    
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=False)
    payment_mode_id = Column(Integer, ForeignKey('payment_mode.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    settlement_type = Column(String(20))  # cash, bank, supplier
    reference_no = Column(String(50))
    
    # Relationships
    sale = relationship("Sale", back_populates="payments")
    payment_mode = relationship("PaymentMode")

class SaleReturn(BaseModel):
    """Sale return transaction"""
    __tablename__ = "sale_return"
    
    sr_no = Column(String(50), unique=True, nullable=False, index=True)
    sr_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    sr_series_id = Column(Integer, ForeignKey('bill_series.id'))
    
    customer_mobile = Column(String(15))
    tax_region = Column(String(20), default='local')
    total_incl = Column(Numeric(12, 2), default=0)
    reason = Column(Text)
    
    # Relationships
    items = relationship("SaleReturnItem", back_populates="sales_return")
    return_credit = relationship("ReturnCredit", back_populates="sales_return", uselist=False)

class SaleReturnItem(BaseModel):
    """Sale return line items"""
    __tablename__ = "sale_return_item"
    
    sales_return_id = Column(Integer, ForeignKey('sale_return.id'), nullable=False)
    sale_id = Column(Integer, ForeignKey('sale.id'), nullable=False)
    sale_item_id = Column(Integer, ForeignKey('sale_item.id'), nullable=False)
    
    # Item Information
    barcode = Column(String(50), nullable=False)
    style_code = Column(String(100), nullable=False)
    color = Column(String(50))
    size = Column(String(20))
    hsn = Column(String(20))
    
    # Return Details
    gst_rate = Column(Numeric(5, 2), default=0)
    unit_mrp_incl = Column(Numeric(10, 2), nullable=False)
    disc_pct_at_sale = Column(Numeric(5, 2), default=0)
    return_qty = Column(Integer, default=1)
    line_inclusive = Column(Numeric(12, 2), nullable=False)
    
    # Tax Info
    base_excl_info = Column(Numeric(10, 2))
    tax_info = Column(Numeric(10, 2))
    
    # Relationships
    sales_return = relationship("SaleReturn", back_populates="items")
    original_sale = relationship("Sale", foreign_keys=[sale_id])
    original_sale_item = relationship("SaleItem", foreign_keys=[sale_item_id])

class ReturnCredit(BaseModel):
    """Return credit notes"""
    __tablename__ = "return_credit"
    
    rc_no = Column(String(50), unique=True, nullable=False, index=True)
    customer_mobile = Column(String(15))
    sales_return_id = Column(Integer, ForeignKey('sale_return.id'), nullable=False)
    rc_amount_incl = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default='open')  # open, partial, closed
    closed_at = Column(DateTime)
    
    # Relationships
    sales_return = relationship("SaleReturn", back_populates="return_credit")

class SalesOrder(BaseModel):
    """Sales order/quotation"""
    __tablename__ = "sales_order"
    
    # Document Information
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    delivery_date = Column(Date, nullable=True)
    
    # Customer Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    customer_name = Column(String(200), nullable=False)
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

class SalesOrderItem(BaseModel):
    """Sales order line items"""
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

class SalesInvoice(BaseModel):
    """Sales invoice"""
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

class SalesInvoiceItem(BaseModel):
    """Sales invoice line items"""
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
