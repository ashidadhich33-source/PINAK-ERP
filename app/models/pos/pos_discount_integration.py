# backend/app/models/pos/pos_discount_integration.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class POSTransactionDiscount(BaseModel):
    """POS transaction discount tracking"""
    __tablename__ = "pos_transaction_discount"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    discount_rule_id = Column(Integer, ForeignKey('discount_rule.id'), nullable=True)
    discount_coupon_id = Column(Integer, ForeignKey('discount_coupon.id'), nullable=True)
    discount_type = Column(String(50), nullable=False)  # rule, coupon, loyalty, manual, customer
    discount_name = Column(String(200), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    applied_amount = Column(Numeric(15, 2), nullable=False)
    priority = Column(Integer, default=0)
    is_automatic = Column(Boolean, default=True)
    applied_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    applied_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="discounts")
    discount_rule = relationship("DiscountRule")
    discount_coupon = relationship("DiscountCoupon")
    applied_by_user = relationship("User", foreign_keys=[applied_by])
    
    def __repr__(self):
        return f"<POSTransactionDiscount(transaction_id={self.transaction_id}, amount={self.applied_amount})>"

class POSCustomerDiscount(BaseModel):
    """POS customer-specific discount tracking"""
    __tablename__ = "pos_customer_discount"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    discount_type = Column(String(50), nullable=False)  # customer_specific, loyalty, vip
    discount_name = Column(String(200), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    applied_amount = Column(Numeric(15, 2), nullable=False)
    customer_tier = Column(String(50), nullable=True)  # bronze, silver, gold, platinum
    loyalty_points_used = Column(Integer, default=0)
    loyalty_points_earned = Column(Integer, default=0)
    applied_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="customer_discounts")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<POSCustomerDiscount(customer_id={self.customer_id}, amount={self.applied_amount})>"

class POSLoyaltyTransaction(BaseModel):
    """POS loyalty program transaction tracking"""
    __tablename__ = "pos_loyalty_transaction"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    points_earned = Column(Integer, default=0)
    points_redeemed = Column(Integer, default=0)
    points_balance_before = Column(Integer, nullable=False)
    points_balance_after = Column(Integer, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String(50), nullable=False)  # earn, redeem, expire, adjust
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="loyalty_transactions")
    customer = relationship("Customer")
    loyalty_program = relationship("LoyaltyProgram")
    
    def __repr__(self):
        return f"<POSLoyaltyTransaction(customer_id={self.customer_id}, points={self.points_earned})>"

class POSDiscountCalculation(BaseModel):
    """POS discount calculation history"""
    __tablename__ = "pos_discount_calculation"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    calculation_step = Column(String(50), nullable=False)  # initial, rule_applied, coupon_applied, final
    subtotal = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), default=0)
    tax_amount = Column(Numeric(15, 2), default=0)
    final_amount = Column(Numeric(15, 2), nullable=False)
    calculation_data = Column(JSON, nullable=True)  # Detailed calculation steps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    calculated_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="discount_calculations")
    calculated_by_user = relationship("User", foreign_keys=[calculated_by])
    
    def __repr__(self):
        return f"<POSDiscountCalculation(transaction_id={self.transaction_id}, step='{self.calculation_step}')>"

class POSPromotion(BaseModel):
    """POS promotion management"""
    __tablename__ = "pos_promotion"
    
    promotion_name = Column(String(200), nullable=False)
    promotion_code = Column(String(100), unique=True, nullable=False)
    promotion_type = Column(String(50), nullable=False)  # buy_x_get_y, percentage_off, fixed_amount
    promotion_description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    max_usage_count = Column(Integer, nullable=True)
    current_usage_count = Column(Integer, default=0)
    min_order_amount = Column(Numeric(15, 2), nullable=True)
    max_discount_amount = Column(Numeric(15, 2), nullable=True)
    promotion_config = Column(JSON, nullable=True)  # Promotion-specific configuration
    target_customers = Column(JSON, nullable=True)  # Customer segments
    target_items = Column(JSON, nullable=True)  # Item categories or specific items
    notes = Column(Text, nullable=True)
    
    # Relationships
    promotion_usage = relationship("POSPromotionUsage", back_populates="promotion")
    
    def __repr__(self):
        return f"<POSPromotion(name='{self.promotion_name}', code='{self.promotion_code}')>"

class POSPromotionUsage(BaseModel):
    """POS promotion usage tracking"""
    __tablename__ = "pos_promotion_usage"
    
    promotion_id = Column(Integer, ForeignKey('pos_promotion.id'), nullable=False)
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    discount_amount = Column(Numeric(15, 2), nullable=False)
    used_date = Column(DateTime, default=datetime.utcnow)
    used_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    promotion = relationship("POSPromotion", back_populates="promotion_usage")
    transaction = relationship("POSTransaction")
    customer = relationship("Customer")
    used_by_user = relationship("User", foreign_keys=[used_by])
    
    def __repr__(self):
        return f"<POSPromotionUsage(promotion_id={self.promotion_id}, transaction_id={self.transaction_id})>"

class POSDiscountAnalytics(BaseModel):
    """POS discount analytics tracking"""
    __tablename__ = "pos_discount_analytics"
    
    analytics_date = Column(Date, nullable=False)
    store_id = Column(Integer, ForeignKey('store.id'), nullable=True)
    total_transactions = Column(Integer, default=0)
    total_discount_amount = Column(Numeric(15, 2), default=0)
    total_discount_percentage = Column(Numeric(5, 2), default=0)
    average_discount_per_transaction = Column(Numeric(15, 2), default=0)
    discount_rule_usage = Column(JSON, nullable=True)  # Rule usage statistics
    coupon_usage = Column(JSON, nullable=True)  # Coupon usage statistics
    customer_discount_usage = Column(JSON, nullable=True)  # Customer discount statistics
    loyalty_usage = Column(JSON, nullable=True)  # Loyalty program statistics
    promotion_usage = Column(JSON, nullable=True)  # Promotion usage statistics
    
    # Relationships
    store = relationship("Store")
    
    def __repr__(self):
        return f"<POSDiscountAnalytics(date='{self.analytics_date}', total_discount={self.total_discount_amount})>"

class POSDiscountConfiguration(BaseModel):
    """POS discount system configuration"""
    __tablename__ = "pos_discount_configuration"
    
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    store_id = Column(Integer, ForeignKey('store.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    store = relationship("Store")
    
    def __repr__(self):
        return f"<POSDiscountConfiguration(key='{self.config_key}', value='{self.config_value}')>"

class POSDiscountAudit(BaseModel):
    """POS discount audit trail"""
    __tablename__ = "pos_discount_audit"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # apply, remove, modify, expire
    discount_type = Column(String(50), nullable=False)  # rule, coupon, loyalty, manual
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    action_date = Column(DateTime, default=datetime.utcnow)
    action_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction")
    action_by_user = relationship("User", foreign_keys=[action_by])
    
    def __repr__(self):
        return f"<POSDiscountAudit(transaction_id={self.transaction_id}, action='{self.action_type}')>"