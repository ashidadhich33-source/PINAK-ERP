# backend/app/models/supplier.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Supplier(BaseModel):
    __tablename__ = "supplier"
    
    # Basic Information
    supplier_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    supplier_type = Column(String(20), default='vendor')  # vendor, manufacturer, distributor
    
    # Contact Information
    contact_person = Column(String(100), nullable=True)
    mobile = Column(String(15), nullable=True)
    phone = Column(String(15), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Address Information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default='India')
    postal_code = Column(String(10), nullable=True)
    
    # Business Information
    gst_number = Column(String(15), nullable=True)
    pan_number = Column(String(10), nullable=True)
    business_license = Column(String(100), nullable=True)
    
    # Financial Information
    credit_days = Column(Integer, default=0)
    payment_terms = Column(String(100), nullable=True)
    opening_balance = Column(Numeric(12, 2), default=0)
    current_balance = Column(Numeric(12, 2), default=0)
    
    # Banking Information
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    ifsc_code = Column(String(11), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    
    # Status and Rating
    status = Column(String(20), default='active')  # active, inactive, blocked
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    
    # Purchase tracking
    first_purchase_date = Column(DateTime, nullable=True)
    last_purchase_date = Column(DateTime, nullable=True)
    total_purchase_amount = Column(Numeric(15, 2), default=0)
    total_orders = Column(Integer, default=0)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    purchase_invoices = relationship("PurchaseInvoice", back_populates="supplier")
    preferred_items = relationship("Item", back_populates="preferred_supplier")
    
    def update_balance(self, amount: float):
        """Update supplier balance"""
        self.current_balance += amount
    
    def __repr__(self):
        return f"<Supplier(code='{self.supplier_code}', name='{self.name}')>"

class CustomerGroup(BaseModel):
    __tablename__ = "customer_group"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    discount_percent = Column(Numeric(5, 2), default=0)
    price_list = Column(String(50), nullable=True)
    credit_limit = Column(Numeric(12, 2), default=0)
    credit_days = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<CustomerGroup(name='{self.name}')>"

class SupplierGroup(BaseModel):
    __tablename__ = "supplier_group"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    payment_terms = Column(String(100), nullable=True)
    credit_days = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<SupplierGroup(name='{self.name}')>"