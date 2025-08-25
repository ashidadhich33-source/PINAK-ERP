# backend/app/models/loyalty.py
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class LoyaltyGrade(BaseModel):
    """Customer loyalty grades/tiers"""
    __tablename__ = "loyalty_grade"
    
    name = Column(String(50), unique=True, nullable=False)
    amount_from = Column(Numeric(12, 2), nullable=False)
    amount_to = Column(Numeric(12, 2), nullable=False)
    earn_pct = Column(Numeric(5, 2), nullable=False)  # Points earning percentage
    
    # Benefits
    discount_percent = Column(Numeric(5, 2), default=0)
    free_delivery = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    
    # Display
    badge_color = Column(String(7))  # Hex color code
    description = Column(String(500))

class LoyaltyTransaction(BaseModel):
    """Loyalty points transactions"""
    __tablename__ = "loyalty_transaction"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # earned, redeemed, expired, adjusted
    points = Column(Integer, nullable=False)  # Positive for earned, negative for redeemed
    
    # Reference
    reference_type = Column(String(30))  # sale, return, manual, expiry
    reference_id = Column(Integer)
    reference_number = Column(String(50))
    
    # Balance tracking
    balance_before = Column(Integer, default=0)
    balance_after = Column(Integer, default=0)
    
    # Expiry
    expiry_date = Column(Date)
    is_expired = Column(Boolean, default=False)
    
    # Description
    description = Column(String(200))
    
    # Relationships
    customer = relationship("Customer", back_populates="loyalty_transactions")

class PointTransaction(BaseModel):
    """Simple point transactions for POS"""
    __tablename__ = "point_transaction"
    
    customer_mobile = Column(String(15), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)  # earned, redeemed, adjustment
    points = Column(Integer, nullable=False)
    
    # Reference
    reference_type = Column(String(30))
    reference_id = Column(String(50))
    
    # Created info is in BaseModel

class Coupon(BaseModel):
    """Discount coupons"""
    __tablename__ = "coupon"
    
    code = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(String(20), nullable=False)  # percent or flat
    value = Column(Numeric(10, 2), nullable=False)
    max_cap = Column(Numeric(10, 2))  # Maximum discount amount for percentage coupons
    
    # Validity
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date)
    
    # Conditions
    min_bill = Column(Numeric(10, 2), default=0)
    bound_mobile = Column(String(15))  # If coupon is for specific customer
    
    # Usage tracking
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Staff who sent
    sent_by_staff_id = Column(Integer, ForeignKey('staff.id'))
    
    # Relationships
    sent_by = relationship("Staff")
