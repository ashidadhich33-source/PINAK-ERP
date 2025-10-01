# backend/app/models/loyalty_program.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class LoyaltyProgram(BaseModel):
    """Loyalty program management"""
    __tablename__ = "loyalty_program"
    
    program_name = Column(String(200), nullable=False)
    program_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    program_type = Column(String(50), nullable=False)  # points, tier, cashback, stamp
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    auto_enrollment = Column(Boolean, default=False)
    enrollment_conditions = Column(JSON, nullable=True)
    program_config = Column(JSON, nullable=False)  # Program configuration
    terms_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_tiers = relationship("LoyaltyTier", back_populates="loyalty_program")
    loyalty_points = relationship("LoyaltyPoint", back_populates="loyalty_program")
    loyalty_rewards = relationship("LoyaltyReward", back_populates="loyalty_program")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="loyalty_program")
    loyalty_analytics = relationship("LoyaltyAnalytics", back_populates="loyalty_program")
    
    def __repr__(self):
        return f"<LoyaltyProgram(name='{self.program_name}', code='{self.program_code}')>"

class LoyaltyTier(BaseModel):
    """Loyalty tier management"""
    __tablename__ = "loyalty_tier"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    tier_name = Column(String(100), nullable=False)
    tier_code = Column(String(50), nullable=False)
    tier_level = Column(Integer, nullable=False)
    min_points = Column(Numeric(15, 2), nullable=False)
    max_points = Column(Numeric(15, 2), nullable=True)
    tier_benefits = Column(JSON, nullable=True)  # Tier benefits
    tier_discount = Column(Numeric(5, 2), nullable=True)  # Tier discount percentage
    tier_multiplier = Column(Numeric(5, 2), default=1.0)  # Points multiplier
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram", back_populates="loyalty_tiers")
    customer_tiers = relationship("CustomerLoyaltyTier", back_populates="loyalty_tier")
    
    def __repr__(self):
        return f"<LoyaltyTier(name='{self.tier_name}', level={self.tier_level})>"

class CustomerLoyaltyTier(BaseModel):
    """Customer loyalty tier management"""
    __tablename__ = "customer_loyalty_tier"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    loyalty_tier_id = Column(Integer, ForeignKey('loyalty_tier.id'), nullable=False)
    current_points = Column(Numeric(15, 2), default=0)
    lifetime_points = Column(Numeric(15, 2), default=0)
    tier_achieved_date = Column(DateTime, nullable=True)
    tier_expiry_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    loyalty_program = relationship("LoyaltyProgram")
    loyalty_tier = relationship("LoyaltyTier", back_populates="customer_tiers")
    
    def __repr__(self):
        return f"<CustomerLoyaltyTier(customer_id={self.customer_id}, tier_id={self.loyalty_tier_id})>"

class LoyaltyPoint(BaseModel):
    """Loyalty point management"""
    __tablename__ = "loyalty_point"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    point_name = Column(String(200), nullable=False)
    point_code = Column(String(50), unique=True, nullable=False)
    point_value = Column(Numeric(15, 2), nullable=False)  # Points per unit
    point_type = Column(String(50), nullable=False)  # earn, redeem, expire, transfer
    point_category = Column(String(50), nullable=False)  # purchase, referral, bonus, penalty
    earning_conditions = Column(JSON, nullable=True)  # Earning conditions
    expiry_days = Column(Integer, nullable=True)  # Points expiry in days
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram", back_populates="loyalty_points")
    point_transactions = relationship("LoyaltyPointTransaction", back_populates="loyalty_point")
    
    def __repr__(self):
        return f"<LoyaltyPoint(name='{self.point_name}', value={self.point_value})>"

class LoyaltyPointTransaction(BaseModel):
    """Loyalty point transaction management"""
    __tablename__ = "loyalty_point_transaction"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    loyalty_point_id = Column(Integer, ForeignKey('loyalty_point.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # earn, redeem, expire, transfer, adjust
    points_amount = Column(Numeric(15, 2), nullable=False)
    points_balance = Column(Numeric(15, 2), nullable=False)
    transaction_reference = Column(String(100), nullable=True)  # Sale ID, Purchase ID, etc.
    transaction_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    loyalty_program = relationship("LoyaltyProgram")
    loyalty_point = relationship("LoyaltyPoint", back_populates="point_transactions")
    
    def __repr__(self):
        return f"<LoyaltyPointTransaction(customer_id={self.customer_id}, points={self.points_amount})>"

class LoyaltyReward(BaseModel):
    """Loyalty reward management"""
    __tablename__ = "loyalty_reward"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    reward_name = Column(String(200), nullable=False)
    reward_code = Column(String(50), unique=True, nullable=False)
    reward_type = Column(String(50), nullable=False)  # discount, free_item, cashback, gift
    reward_value = Column(Numeric(15, 2), nullable=False)
    points_required = Column(Numeric(15, 2), nullable=False)
    reward_conditions = Column(JSON, nullable=True)  # Reward conditions
    max_redemptions = Column(Integer, nullable=True)
    current_redemptions = Column(Integer, default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram", back_populates="loyalty_rewards")
    reward_redemptions = relationship("LoyaltyRewardRedemption", back_populates="loyalty_reward")
    
    def __repr__(self):
        return f"<LoyaltyReward(name='{self.reward_name}', points={self.points_required})>"

class LoyaltyRewardRedemption(BaseModel):
    """Loyalty reward redemption management"""
    __tablename__ = "loyalty_reward_redemption"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    loyalty_reward_id = Column(Integer, ForeignKey('loyalty_reward.id'), nullable=False)
    redemption_code = Column(String(100), unique=True, nullable=False)
    points_used = Column(Numeric(15, 2), nullable=False)
    reward_value = Column(Numeric(15, 2), nullable=False)
    redemption_date = Column(DateTime, default=datetime.utcnow)
    redemption_status = Column(String(20), default='pending')  # pending, completed, cancelled, expired
    transaction_reference = Column(String(100), nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    loyalty_program = relationship("LoyaltyProgram")
    loyalty_reward = relationship("LoyaltyReward", back_populates="reward_redemptions")
    
    def __repr__(self):
        return f"<LoyaltyRewardRedemption(customer_id={self.customer_id}, reward_id={self.loyalty_reward_id})>"

class LoyaltyTransaction(BaseModel):
    """Loyalty transaction management"""
    __tablename__ = "loyalty_program_transaction"
    
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, redemption, bonus, penalty, transfer
    transaction_reference = Column(String(100), nullable=True)
    points_earned = Column(Numeric(15, 2), default=0)
    points_redeemed = Column(Numeric(15, 2), default=0)
    points_balance = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    loyalty_program = relationship("LoyaltyProgram", back_populates="loyalty_transactions")
    
    def __repr__(self):
        return f"<LoyaltyTransaction(customer_id={self.customer_id}, type='{self.transaction_type}')>"

class LoyaltyAnalytics(BaseModel):
    """Loyalty analytics management"""
    __tablename__ = "loyalty_analytics"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    analytics_date = Column(Date, nullable=False)
    total_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    total_points_earned = Column(Numeric(15, 2), default=0)
    total_points_redeemed = Column(Numeric(15, 2), default=0)
    total_points_expired = Column(Numeric(15, 2), default=0)
    total_rewards_redemptions = Column(Integer, default=0)
    total_reward_value = Column(Numeric(15, 2), default=0)
    average_points_per_customer = Column(Numeric(15, 2), default=0)
    redemption_rate = Column(Numeric(5, 2), default=0)
    analytics_data = Column(JSON, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram", back_populates="loyalty_analytics")
    
    def __repr__(self):
        return f"<LoyaltyAnalytics(program_id={self.loyalty_program_id}, date='{self.analytics_date}')>"

class LoyaltyCampaign(BaseModel):
    """Loyalty campaign management"""
    __tablename__ = "loyalty_campaign"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    campaign_name = Column(String(200), nullable=False)
    campaign_code = Column(String(50), unique=True, nullable=False)
    campaign_type = Column(String(50), nullable=False)  # bonus_points, double_points, tier_upgrade, special_reward
    campaign_config = Column(JSON, nullable=False)  # Campaign configuration
    target_customers = Column(JSON, nullable=True)  # Target customer criteria
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    campaign_status = Column(String(20), default='draft')  # draft, active, paused, completed, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram")
    campaign_participants = relationship("LoyaltyCampaignParticipant", back_populates="loyalty_campaign")
    
    def __repr__(self):
        return f"<LoyaltyCampaign(name='{self.campaign_name}', type='{self.campaign_type}')>"

class LoyaltyCampaignParticipant(BaseModel):
    """Loyalty campaign participant management"""
    __tablename__ = "loyalty_campaign_participant"
    
    loyalty_campaign_id = Column(Integer, ForeignKey('loyalty_campaign.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    participation_date = Column(DateTime, default=datetime.utcnow)
    participation_status = Column(String(20), default='active')  # active, completed, cancelled
    points_earned = Column(Numeric(15, 2), default=0)
    rewards_claimed = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_campaign = relationship("LoyaltyCampaign", back_populates="campaign_participants")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<LoyaltyCampaignParticipant(campaign_id={self.loyalty_campaign_id}, customer_id={self.customer_id})>"

class LoyaltyReferral(BaseModel):
    """Loyalty referral management"""
    __tablename__ = "loyalty_referral"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    referrer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    referee_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    referral_code = Column(String(100), unique=True, nullable=False)
    referral_date = Column(DateTime, default=datetime.utcnow)
    referral_status = Column(String(20), default='pending')  # pending, completed, cancelled
    referrer_points = Column(Numeric(15, 2), default=0)
    referee_points = Column(Numeric(15, 2), default=0)
    completion_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram")
    referrer = relationship("Customer", foreign_keys=[referrer_id])
    referee = relationship("Customer", foreign_keys=[referee_id])
    
    def __repr__(self):
        return f"<LoyaltyReferral(referrer_id={self.referrer_id}, referee_id={self.referee_id})>"

class LoyaltyNotification(BaseModel):
    """Loyalty notification management"""
    __tablename__ = "loyalty_notification"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    notification_type = Column(String(50), nullable=False)  # points_earned, points_expiring, tier_upgrade, reward_available
    notification_title = Column(String(200), nullable=False)
    notification_message = Column(Text, nullable=False)
    notification_data = Column(JSON, nullable=True)
    notification_date = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    read_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<LoyaltyNotification(customer_id={self.customer_id}, type='{self.notification_type}')>"

class LoyaltyConfiguration(BaseModel):
    """Loyalty configuration management"""
    __tablename__ = "loyalty_configuration"
    
    loyalty_program_id = Column(Integer, ForeignKey('loyalty_program.id'), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    loyalty_program = relationship("LoyaltyProgram")
    
    def __repr__(self):
        return f"<LoyaltyConfiguration(program_id={self.loyalty_program_id}, key='{self.config_key}')>"