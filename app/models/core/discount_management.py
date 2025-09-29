# backend/app/models/discount_management.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class DiscountType(BaseModel):
    """Discount type management"""
    __tablename__ = "discount_type"
    
    type_name = Column(String(100), nullable=False)
    type_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    calculation_method = Column(String(50), nullable=False)  # percentage, fixed, tiered
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    discount_rules = relationship("DiscountRule", back_populates="discount_type")
    
    def __repr__(self):
        return f"<DiscountType(name='{self.type_name}', code='{self.type_code}')>"

class DiscountRule(BaseModel):
    """Discount rule management"""
    __tablename__ = "discount_rule"
    
    rule_name = Column(String(200), nullable=False)
    rule_code = Column(String(100), unique=True, nullable=False)
    discount_type_id = Column(Integer, ForeignKey('discount_type.id'), nullable=False)
    rule_type = Column(String(50), nullable=False)  # item, category, customer, order, loyalty
    target_type = Column(String(50), nullable=True)  # item_id, category_id, customer_id, order_amount
    target_id = Column(Integer, nullable=True)
    condition_type = Column(String(50), nullable=False)  # quantity, amount, date, customer_type
    condition_value = Column(Numeric(15, 2), nullable=True)
    condition_operator = Column(String(20), nullable=False)  # >=, <=, =, >, <
    discount_value = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    max_discount_amount = Column(Numeric(15, 2), nullable=True)
    min_order_amount = Column(Numeric(15, 2), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_automatic = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    discount_type = relationship("DiscountType", back_populates="discount_rules")
    discount_applications = relationship("DiscountApplication", back_populates="discount_rule")
    
    def __repr__(self):
        return f"<DiscountRule(name='{self.rule_name}', type='{self.rule_type}')>"

class DiscountApplication(BaseModel):
    """Discount application tracking"""
    __tablename__ = "discount_application"
    
    rule_id = Column(Integer, ForeignKey('discount_rule.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # sale, purchase, return
    transaction_id = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    original_amount = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=False)
    final_amount = Column(Numeric(15, 2), nullable=False)
    applied_date = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    discount_rule = relationship("DiscountRule", back_populates="discount_applications")
    item = relationship("Item")
    customer = relationship("Customer")
    applied_by_user = relationship("User", foreign_keys=[applied_by])
    
    def __repr__(self):
        return f"<DiscountApplication(rule_id={self.rule_id}, amount={self.discount_amount})>"

class DiscountCoupon(BaseModel):
    """Discount coupon management"""
    __tablename__ = "discount_coupon"
    
    coupon_code = Column(String(50), unique=True, nullable=False)
    coupon_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    discount_type_id = Column(Integer, ForeignKey('discount_type.id'), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    max_discount_amount = Column(Numeric(15, 2), nullable=True)
    min_order_amount = Column(Numeric(15, 2), nullable=True)
    max_usage_count = Column(Integer, nullable=True)
    current_usage_count = Column(Integer, default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    is_single_use = Column(Boolean, default=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    discount_type = relationship("DiscountType")
    customer = relationship("Customer")
    coupon_usage = relationship("CouponUsage", back_populates="coupon")
    
    def __repr__(self):
        return f"<DiscountCoupon(code='{self.coupon_code}', name='{self.coupon_name}')>"

class CouponUsage(BaseModel):
    """Coupon usage tracking"""
    __tablename__ = "coupon_usage"
    
    coupon_id = Column(Integer, ForeignKey('discount_coupon.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # sale, purchase, return
    transaction_id = Column(Integer, nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=False)
    used_date = Column(DateTime, default=datetime.utcnow)
    used_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    coupon = relationship("DiscountCoupon", back_populates="coupon_usage")
    customer = relationship("Customer")
    used_by_user = relationship("User", foreign_keys=[used_by])
    
    def __repr__(self):
        return f"<CouponUsage(coupon_id={self.coupon_id}, customer_id={self.customer_id})>"

class DiscountTier(BaseModel):
    """Discount tier management"""
    __tablename__ = "discount_tier"
    
    tier_name = Column(String(100), nullable=False)
    tier_code = Column(String(50), unique=True, nullable=False)
    min_quantity = Column(Numeric(10, 2), nullable=False)
    max_quantity = Column(Numeric(10, 2), nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    tier_applications = relationship("TierApplication", back_populates="discount_tier")
    
    def __repr__(self):
        return f"<DiscountTier(name='{self.tier_name}', min_qty={self.min_quantity})>"

class TierApplication(BaseModel):
    """Tier application tracking"""
    __tablename__ = "tier_application"
    
    tier_id = Column(Integer, ForeignKey('discount_tier.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(15, 2), nullable=False)
    original_amount = Column(Numeric(15, 2), nullable=False)
    discount_amount = Column(Numeric(15, 2), nullable=False)
    final_amount = Column(Numeric(15, 2), nullable=False)
    applied_date = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    discount_tier = relationship("DiscountTier", back_populates="tier_applications")
    item = relationship("Item")
    customer = relationship("Customer")
    applied_by_user = relationship("User", foreign_keys=[applied_by])
    
    def __repr__(self):
        return f"<TierApplication(tier_id={self.tier_id}, item_id={self.item_id})>"

class CustomerDiscount(BaseModel):
    """Customer-specific discount management"""
    __tablename__ = "customer_discount"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    discount_type_id = Column(Integer, ForeignKey('discount_type.id'), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    max_discount_amount = Column(Numeric(15, 2), nullable=True)
    min_order_amount = Column(Numeric(15, 2), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    discount_type = relationship("DiscountType")
    
    def __repr__(self):
        return f"<CustomerDiscount(customer_id={self.customer_id}, value={self.discount_value})>"

class DiscountAnalytics(BaseModel):
    """Discount analytics tracking"""
    __tablename__ = "discount_analytics"
    
    analytics_date = Column(Date, nullable=False)
    rule_id = Column(Integer, ForeignKey('discount_rule.id'), nullable=True)
    coupon_id = Column(Integer, ForeignKey('discount_coupon.id'), nullable=True)
    total_applications = Column(Integer, default=0)
    total_discount_amount = Column(Numeric(15, 2), default=0)
    total_original_amount = Column(Numeric(15, 2), default=0)
    average_discount_percentage = Column(Numeric(5, 2), default=0)
    unique_customers = Column(Integer, default=0)
    conversion_rate = Column(Numeric(5, 2), default=0)
    
    # Relationships
    discount_rule = relationship("DiscountRule")
    discount_coupon = relationship("DiscountCoupon")
    
    def __repr__(self):
        return f"<DiscountAnalytics(date='{self.analytics_date}', applications={self.total_applications})>"

class DiscountReport(BaseModel):
    """Discount report management"""
    __tablename__ = "discount_report"
    
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # summary, detailed, customer, item
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    report_data = Column(JSON, nullable=True)
    total_discounts = Column(Numeric(15, 2), default=0)
    total_applications = Column(Integer, default=0)
    average_discount = Column(Numeric(15, 2), default=0)
    generated_date = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    generated_by_user = relationship("User", foreign_keys=[generated_by])
    
    def __repr__(self):
        return f"<DiscountReport(name='{self.report_name}', type='{self.report_type}')>"

class DiscountConfiguration(BaseModel):
    """Discount system configuration"""
    __tablename__ = "discount_configuration"
    
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<DiscountConfiguration(key='{self.config_key}', value='{self.config_value}')>"

class DiscountValidation(BaseModel):
    """Discount validation rules"""
    __tablename__ = "discount_validation"
    
    validation_name = Column(String(200), nullable=False)
    validation_type = Column(String(50), nullable=False)  # business_rule, system_rule, custom_rule
    validation_condition = Column(Text, nullable=False)
    validation_message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<DiscountValidation(name='{self.validation_name}', type='{self.validation_type}')>"

class DiscountAudit(BaseModel):
    """Discount audit trail"""
    __tablename__ = "discount_audit"
    
    action_type = Column(String(50), nullable=False)  # create, update, delete, apply, expire
    entity_type = Column(String(50), nullable=False)  # rule, coupon, application, tier
    entity_id = Column(Integer, nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    action_date = Column(DateTime, default=datetime.utcnow)
    action_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    action_by_user = relationship("User", foreign_keys=[action_by])
    
    def __repr__(self):
        return f"<DiscountAudit(action='{self.action_type}', entity='{self.entity_type}')>"