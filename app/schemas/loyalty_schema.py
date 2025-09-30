"""
Loyalty Program Pydantic Schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date
from enum import Enum


class LoyaltyTransactionType(str, Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    ADJUSTED = "adjusted"
    BONUS = "bonus"
    REFUND = "refund"


class LoyaltyProgramStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DRAFT = "draft"


class LoyaltyTierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# Loyalty Grade Schemas
class LoyaltyGradeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    amount_from: Decimal = Field(..., ge=0)
    amount_to: Decimal = Field(..., ge=0)
    earn_pct: Decimal = Field(..., ge=0, le=100)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    free_delivery: bool = Field(default=False)
    priority_support: bool = Field(default=False)
    badge_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('amount_to')
    def validate_amount_range(cls, v, values):
        if 'amount_from' in values and v < values['amount_from']:
            raise ValueError('amount_to must be greater than amount_from')
        return v


class LoyaltyGradeUpdate(BaseModel):
    name: Optional[str] = None
    amount_from: Optional[Decimal] = None
    amount_to: Optional[Decimal] = None
    earn_pct: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    free_delivery: Optional[bool] = None
    priority_support: Optional[bool] = None
    badge_color: Optional[str] = None
    description: Optional[str] = None


class LoyaltyGradeResponse(BaseModel):
    id: int
    name: str
    amount_from: Decimal
    amount_to: Decimal
    earn_pct: Decimal
    discount_percent: Decimal
    free_delivery: bool
    priority_support: bool
    badge_color: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Transaction Schemas
class LoyaltyTransactionCreate(BaseModel):
    customer_id: int
    transaction_type: LoyaltyTransactionType
    points: int = Field(..., description="Positive for earned, negative for redeemed")
    reference_type: Optional[str] = Field(None, max_length=30)
    reference_id: Optional[int] = None
    reference_number: Optional[str] = Field(None, max_length=50)
    expiry_date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=200)


class LoyaltyTransactionUpdate(BaseModel):
    transaction_type: Optional[LoyaltyTransactionType] = None
    points: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    expiry_date: Optional[date] = None
    description: Optional[str] = None
    is_expired: Optional[bool] = None


class LoyaltyTransactionResponse(BaseModel):
    id: int
    customer_id: int
    transaction_type: LoyaltyTransactionType
    points: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    balance_before: int
    balance_after: int
    expiry_date: Optional[date] = None
    is_expired: bool
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Points Schemas
class LoyaltyPointsCreate(BaseModel):
    customer_id: int
    points: int = Field(..., description="Total points balance")
    expiry_date: Optional[date] = None
    is_active: bool = Field(default=True)


class LoyaltyPointsUpdate(BaseModel):
    points: Optional[int] = None
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class LoyaltyPointsResponse(BaseModel):
    id: int
    customer_id: int
    points: int
    expiry_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Reward Schemas
class LoyaltyRewardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    points_required: int = Field(..., gt=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    discount_amount: Optional[Decimal] = Field(None, ge=0)
    free_item_id: Optional[int] = None
    free_item_quantity: Optional[int] = Field(None, gt=0)
    is_active: bool = Field(default=True)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    usage_limit: Optional[int] = Field(None, gt=0)
    usage_count: int = Field(default=0, ge=0)


class LoyaltyRewardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    points_required: Optional[int] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    free_item_id: Optional[int] = None
    free_item_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    usage_limit: Optional[int] = None


class LoyaltyRewardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    points_required: int
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    free_item_id: Optional[int] = None
    free_item_quantity: Optional[int] = None
    is_active: bool
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    usage_limit: Optional[int] = None
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Program Schemas
class LoyaltyProgramCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: LoyaltyProgramStatus = LoyaltyProgramStatus.ACTIVE
    start_date: date
    end_date: Optional[date] = None
    points_per_rupee: Decimal = Field(default=1, ge=0)
    minimum_purchase: Decimal = Field(default=0, ge=0)
    maximum_points_per_transaction: Optional[int] = Field(None, gt=0)
    points_expiry_days: Optional[int] = Field(None, gt=0)
    auto_enrollment: bool = Field(default=False)
    welcome_bonus_points: int = Field(default=0, ge=0)
    birthday_bonus_points: int = Field(default=0, ge=0)
    anniversary_bonus_points: int = Field(default=0, ge=0)


class LoyaltyProgramUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LoyaltyProgramStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    points_per_rupee: Optional[Decimal] = None
    minimum_purchase: Optional[Decimal] = None
    maximum_points_per_transaction: Optional[int] = None
    points_expiry_days: Optional[int] = None
    auto_enrollment: Optional[bool] = None
    welcome_bonus_points: Optional[int] = None
    birthday_bonus_points: Optional[int] = None
    anniversary_bonus_points: Optional[int] = None


class LoyaltyProgramResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: LoyaltyProgramStatus
    start_date: date
    end_date: Optional[date] = None
    points_per_rupee: Decimal
    minimum_purchase: Decimal
    maximum_points_per_transaction: Optional[int] = None
    points_expiry_days: Optional[int] = None
    auto_enrollment: bool
    welcome_bonus_points: int
    birthday_bonus_points: int
    anniversary_bonus_points: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Rule Schemas
class LoyaltyRuleCreate(BaseModel):
    program_id: int
    rule_name: str = Field(..., min_length=1, max_length=100)
    rule_type: str = Field(..., regex="^(purchase|category|item|time|frequency)$")
    condition: Dict[str, Any] = Field(..., description="Rule condition as JSON")
    points_multiplier: Decimal = Field(default=1, ge=0)
    is_active: bool = Field(default=True)
    priority: int = Field(default=0, ge=0)
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class LoyaltyRuleUpdate(BaseModel):
    rule_name: Optional[str] = None
    rule_type: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    points_multiplier: Optional[Decimal] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class LoyaltyRuleResponse(BaseModel):
    id: int
    program_id: int
    rule_name: str
    rule_type: str
    condition: Dict[str, Any]
    points_multiplier: Decimal
    is_active: bool
    priority: int
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Tier Schemas
class LoyaltyTierCreate(BaseModel):
    program_id: int
    tier_name: str = Field(..., min_length=1, max_length=50)
    tier_level: int = Field(..., gt=0)
    minimum_points: int = Field(..., ge=0)
    maximum_points: Optional[int] = Field(None, ge=0)
    benefits: Dict[str, Any] = Field(default_factory=dict)
    status: LoyaltyTierStatus = LoyaltyTierStatus.ACTIVE
    badge_color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    icon_url: Optional[str] = None
    
    @validator('maximum_points')
    def validate_points_range(cls, v, values):
        if v is not None and 'minimum_points' in values and v < values['minimum_points']:
            raise ValueError('maximum_points must be greater than minimum_points')
        return v


class LoyaltyTierUpdate(BaseModel):
    tier_name: Optional[str] = None
    tier_level: Optional[int] = None
    minimum_points: Optional[int] = None
    maximum_points: Optional[int] = None
    benefits: Optional[Dict[str, Any]] = None
    status: Optional[LoyaltyTierStatus] = None
    badge_color: Optional[str] = None
    icon_url: Optional[str] = None


class LoyaltyTierResponse(BaseModel):
    id: int
    program_id: int
    tier_name: str
    tier_level: int
    minimum_points: int
    maximum_points: Optional[int] = None
    benefits: Dict[str, Any]
    status: LoyaltyTierStatus
    badge_color: Optional[str] = None
    icon_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Customer Loyalty Balance Schema
class CustomerLoyaltyBalance(BaseModel):
    customer_id: int
    total_points: int
    available_points: int
    pending_points: int
    expired_points: int
    tier_name: Optional[str] = None
    tier_level: Optional[int] = None
    next_tier_points: Optional[int] = None
    points_expiring_soon: int = Field(default=0, ge=0)
    last_earned_date: Optional[datetime] = None
    last_redeemed_date: Optional[datetime] = None


# Loyalty Redemption Schemas
class LoyaltyRedemptionCreate(BaseModel):
    customer_id: int
    reward_id: int
    points_used: int = Field(..., gt=0)
    redemption_code: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)


class LoyaltyRedemptionUpdate(BaseModel):
    points_used: Optional[int] = None
    redemption_code: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class LoyaltyRedemptionResponse(BaseModel):
    id: int
    customer_id: int
    reward_id: int
    points_used: int
    redemption_code: Optional[str] = None
    status: str
    notes: Optional[str] = None
    redeemed_at: datetime
    expires_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Loyalty Analytics Schemas
class LoyaltyAnalyticsResponse(BaseModel):
    total_customers: int
    active_customers: int
    total_points_earned: int
    total_points_redeemed: int
    total_points_expired: int
    average_points_per_customer: Decimal
    top_earning_customers: List[Dict[str, Any]]
    popular_rewards: List[Dict[str, Any]]
    points_distribution: Dict[str, int]
    monthly_earnings: List[Dict[str, Any]]
    monthly_redemptions: List[Dict[str, Any]]


# Loyalty Import/Export Schemas
class LoyaltyImportRequest(BaseModel):
    import_type: str = Field(..., regex="^(customers|transactions|rewards)$")
    file_path: str
    mapping: Dict[str, str] = Field(..., description="Column mapping")
    options: Dict[str, Any] = Field(default_factory=dict)


class LoyaltyImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]
    warnings: List[str]


class LoyaltyExportRequest(BaseModel):
    export_type: str = Field(..., regex="^(customers|transactions|rewards|analytics)$")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    customer_ids: Optional[List[int]] = None
    format: str = Field(default="csv", regex="^(csv|excel|json)$")
    include_inactive: bool = Field(default=False)