# backend/app/models/customer.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, Date
from sqlalchemy.orm import relationship
from ..base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customer"
    
    # Basic Information
    customer_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    customer_type = Column(String(20), default='retail')  # retail, wholesale, corporate
    
    # Contact Information
    mobile = Column(String(15), nullable=True, index=True)
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
    business_name = Column(String(200), nullable=True)
    
    # Financial Information
    credit_limit = Column(Numeric(12, 2), default=0)
    payment_terms = Column(String(100), nullable=True)  # e.g., "Net 30", "COD"
    opening_balance = Column(Numeric(12, 2), default=0)
    current_balance = Column(Numeric(12, 2), default=0)
    
    # Discount and Pricing
    discount_percent = Column(Numeric(5, 2), default=0)
    price_list = Column(String(50), nullable=True)  # retail, wholesale, special
    
    # Personal Information (for retail)
    date_of_birth = Column(Date, nullable=True)
    anniversary_date = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    
    # Status and Flags
    status = Column(String(20), default='active')  # active, inactive, blocked
    is_loyalty_member = Column(Boolean, default=False)
    loyalty_card_number = Column(String(50), nullable=True, unique=True)
    
    # Sales tracking
    first_sale_date = Column(DateTime, nullable=True)
    last_sale_date = Column(DateTime, nullable=True)
    total_sales_amount = Column(Numeric(15, 2), default=0)
    total_transactions = Column(Integer, default=0)
    
    # Relationships
    sales_orders = relationship("SalesOrder", back_populates="customer")
    sales_invoices = relationship("SalesInvoice", back_populates="customer")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="customer")
    
    def update_balance(self, amount: float):
        """Update customer balance"""
        self.current_balance += amount
    
    def is_credit_limit_exceeded(self, additional_amount: float = 0) -> bool:
        """Check if credit limit is exceeded"""
        if self.credit_limit <= 0:  # No limit set
            return False
        return (self.current_balance + additional_amount) > self.credit_limit
    
    def __repr__(self):
        return f"<Customer(code='{self.customer_code}', name='{self.name}')>"