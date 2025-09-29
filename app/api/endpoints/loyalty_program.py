# backend/app/api/endpoints/loyalty_program.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.loyalty_program_service import loyalty_program_service

router = APIRouter()

# Pydantic schemas for Loyalty Program
class LoyaltyProgramCreateRequest(BaseModel):
    program_name: str
    program_code: str
    program_type: str
    start_date: date
    end_date: Optional[date] = None
    description: Optional[str] = None
    auto_enrollment: bool = False
    enrollment_conditions: Optional[dict] = None
    program_config: Optional[dict] = None
    terms_conditions: Optional[str] = None
    notes: Optional[str] = None

class LoyaltyProgramResponse(BaseModel):
    id: int
    company_id: int
    program_name: str
    program_code: str
    description: Optional[str] = None
    program_type: str
    is_active: bool
    start_date: date
    end_date: Optional[date] = None
    auto_enrollment: bool
    enrollment_conditions: Optional[dict] = None
    program_config: dict
    terms_conditions: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Tier
class LoyaltyTierCreateRequest(BaseModel):
    loyalty_program_id: int
    tier_name: str
    tier_code: str
    tier_level: int
    min_points: Decimal
    max_points: Optional[Decimal] = None
    tier_benefits: Optional[dict] = None
    tier_discount: Optional[Decimal] = None
    tier_multiplier: Decimal = 1.0
    display_order: int = 0
    notes: Optional[str] = None

class LoyaltyTierResponse(BaseModel):
    id: int
    company_id: int
    loyalty_program_id: int
    tier_name: str
    tier_code: str
    tier_level: int
    min_points: Decimal
    max_points: Optional[Decimal] = None
    tier_benefits: Optional[dict] = None
    tier_discount: Optional[Decimal] = None
    tier_multiplier: Decimal
    is_active: bool
    display_order: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Customer Loyalty Tier
class CustomerLoyaltyTierCreateRequest(BaseModel):
    customer_id: int
    loyalty_program_id: int
    loyalty_tier_id: int

class CustomerLoyaltyTierResponse(BaseModel):
    id: int
    company_id: int
    customer_id: int
    loyalty_program_id: int
    loyalty_tier_id: int
    current_points: Decimal
    lifetime_points: Decimal
    tier_achieved_date: Optional[datetime] = None
    tier_expiry_date: Optional[datetime] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Point
class LoyaltyPointCreateRequest(BaseModel):
    loyalty_program_id: int
    point_name: str
    point_code: str
    point_value: Decimal
    point_type: str
    point_category: str
    earning_conditions: Optional[dict] = None
    expiry_days: Optional[int] = None
    notes: Optional[str] = None

class LoyaltyPointResponse(BaseModel):
    id: int
    company_id: int
    loyalty_program_id: int
    point_name: str
    point_code: str
    point_value: Decimal
    point_type: str
    point_category: str
    earning_conditions: Optional[dict] = None
    expiry_days: Optional[int] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Point Transaction
class LoyaltyPointTransactionCreateRequest(BaseModel):
    customer_id: int
    loyalty_program_id: int
    loyalty_point_id: int
    points_amount: Decimal
    transaction_reference: Optional[str] = None
    description: Optional[str] = None

class LoyaltyPointTransactionResponse(BaseModel):
    id: int
    company_id: int
    customer_id: int
    loyalty_program_id: int
    loyalty_point_id: int
    transaction_type: str
    points_amount: Decimal
    points_balance: Decimal
    transaction_reference: Optional[str] = None
    transaction_date: datetime
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Reward
class LoyaltyRewardCreateRequest(BaseModel):
    loyalty_program_id: int
    reward_name: str
    reward_code: str
    reward_type: str
    reward_value: Decimal
    points_required: Decimal
    reward_conditions: Optional[dict] = None
    max_redemptions: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None

class LoyaltyRewardResponse(BaseModel):
    id: int
    company_id: int
    loyalty_program_id: int
    reward_name: str
    reward_code: str
    reward_type: str
    reward_value: Decimal
    points_required: Decimal
    reward_conditions: Optional[dict] = None
    max_redemptions: Optional[int] = None
    current_redemptions: int
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Reward Redemption
class LoyaltyRewardRedemptionCreateRequest(BaseModel):
    customer_id: int
    loyalty_program_id: int
    loyalty_reward_id: int
    points_amount: Decimal
    transaction_reference: Optional[str] = None
    description: Optional[str] = None

class LoyaltyRewardRedemptionResponse(BaseModel):
    id: int
    company_id: int
    customer_id: int
    loyalty_program_id: int
    loyalty_reward_id: int
    redemption_code: str
    points_used: Decimal
    reward_value: Decimal
    redemption_date: datetime
    redemption_status: str
    transaction_reference: Optional[str] = None
    expiry_date: Optional[datetime] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Analytics
class LoyaltyAnalyticsResponse(BaseModel):
    id: int
    company_id: int
    loyalty_program_id: int
    analytics_date: date
    total_customers: int
    active_customers: int
    total_points_earned: Decimal
    total_points_redeemed: Decimal
    total_points_expired: Decimal
    total_rewards_redemptions: int
    total_reward_value: Decimal
    average_points_per_customer: Decimal
    redemption_rate: Decimal
    analytics_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Loyalty Campaign
class LoyaltyCampaignCreateRequest(BaseModel):
    loyalty_program_id: int
    campaign_name: str
    campaign_code: str
    campaign_type: str
    campaign_config: dict
    target_customers: Optional[dict] = None
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str] = None

class LoyaltyCampaignResponse(BaseModel):
    id: int
    company_id: int
    loyalty_program_id: int
    campaign_name: str
    campaign_code: str
    campaign_type: str
    campaign_config: dict
    target_customers: Optional[dict] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    campaign_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Loyalty Program Endpoints
@router.post("/loyalty-programs", response_model=LoyaltyProgramResponse)
async def create_loyalty_program(
    program_data: LoyaltyProgramCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Create loyalty program"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        program = loyalty_program_service.create_loyalty_program(
            db=db,
            company_id=company_id,
            program_name=program_data.program_name,
            program_code=program_data.program_code,
            program_type=program_data.program_type,
            start_date=program_data.start_date,
            end_date=program_data.end_date,
            description=program_data.description,
            auto_enrollment=program_data.auto_enrollment,
            enrollment_conditions=program_data.enrollment_conditions,
            program_config=program_data.program_config,
            terms_conditions=program_data.terms_conditions,
            notes=program_data.notes,
            user_id=current_user.id
        )
        
        return program
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty program: {str(e)}"
        )

@router.get("/loyalty-programs", response_model=List[LoyaltyProgramResponse])
async def get_loyalty_programs(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    program_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty programs"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    programs = loyalty_program_service.get_loyalty_programs(
        db=db,
        company_id=company_id,
        is_active=is_active,
        program_type=program_type
    )
    
    return programs

# Loyalty Tier Endpoints
@router.post("/loyalty-tiers", response_model=LoyaltyTierResponse)
async def create_loyalty_tier(
    tier_data: LoyaltyTierCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Create loyalty tier"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        tier = loyalty_program_service.create_loyalty_tier(
            db=db,
            company_id=company_id,
            loyalty_program_id=tier_data.loyalty_program_id,
            tier_name=tier_data.tier_name,
            tier_code=tier_data.tier_code,
            tier_level=tier_data.tier_level,
            min_points=tier_data.min_points,
            max_points=tier_data.max_points,
            tier_benefits=tier_data.tier_benefits,
            tier_discount=tier_data.tier_discount,
            tier_multiplier=tier_data.tier_multiplier,
            display_order=tier_data.display_order,
            notes=tier_data.notes,
            user_id=current_user.id
        )
        
        return tier
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty tier: {str(e)}"
        )

@router.get("/loyalty-tiers", response_model=List[LoyaltyTierResponse])
async def get_loyalty_tiers(
    loyalty_program_id: int = Query(...),
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty tiers"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    tiers = loyalty_program_service.get_loyalty_tiers(
        db=db,
        company_id=company_id,
        loyalty_program_id=loyalty_program_id,
        is_active=is_active
    )
    
    return tiers

# Customer Loyalty Tier Endpoints
@router.post("/customer-loyalty-tiers", response_model=CustomerLoyaltyTierResponse)
async def assign_customer_tier(
    tier_data: CustomerLoyaltyTierCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Assign customer to loyalty tier"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        customer_tier = loyalty_program_service.assign_customer_tier(
            db=db,
            company_id=company_id,
            customer_id=tier_data.customer_id,
            loyalty_program_id=tier_data.loyalty_program_id,
            loyalty_tier_id=tier_data.loyalty_tier_id,
            user_id=current_user.id
        )
        
        return customer_tier
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign customer tier: {str(e)}"
        )

# Loyalty Point Endpoints
@router.post("/loyalty-points", response_model=LoyaltyPointResponse)
async def create_loyalty_point(
    point_data: LoyaltyPointCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Create loyalty point"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        point = loyalty_program_service.create_loyalty_point(
            db=db,
            company_id=company_id,
            loyalty_program_id=point_data.loyalty_program_id,
            point_name=point_data.point_name,
            point_code=point_data.point_code,
            point_value=point_data.point_value,
            point_type=point_data.point_type,
            point_category=point_data.point_category,
            earning_conditions=point_data.earning_conditions,
            expiry_days=point_data.expiry_days,
            notes=point_data.notes,
            user_id=current_user.id
        )
        
        return point
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty point: {str(e)}"
        )

@router.post("/loyalty-points/earn", response_model=LoyaltyPointTransactionResponse)
async def earn_loyalty_points(
    transaction_data: LoyaltyPointTransactionCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Earn loyalty points"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        transaction = loyalty_program_service.earn_loyalty_points(
            db=db,
            company_id=company_id,
            customer_id=transaction_data.customer_id,
            loyalty_program_id=transaction_data.loyalty_program_id,
            loyalty_point_id=transaction_data.loyalty_point_id,
            points_amount=transaction_data.points_amount,
            transaction_reference=transaction_data.transaction_reference,
            description=transaction_data.description,
            user_id=current_user.id
        )
        
        return transaction
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to earn loyalty points: {str(e)}"
        )

# Loyalty Reward Endpoints
@router.post("/loyalty-rewards", response_model=LoyaltyRewardResponse)
async def create_loyalty_reward(
    reward_data: LoyaltyRewardCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Create loyalty reward"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        reward = loyalty_program_service.create_loyalty_reward(
            db=db,
            company_id=company_id,
            loyalty_program_id=reward_data.loyalty_program_id,
            reward_name=reward_data.reward_name,
            reward_code=reward_data.reward_code,
            reward_type=reward_data.reward_type,
            reward_value=reward_data.reward_value,
            points_required=reward_data.points_required,
            reward_conditions=reward_data.reward_conditions,
            max_redemptions=reward_data.max_redemptions,
            start_date=reward_data.start_date,
            end_date=reward_data.end_date,
            notes=reward_data.notes,
            user_id=current_user.id
        )
        
        return reward
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty reward: {str(e)}"
        )

@router.get("/loyalty-rewards", response_model=List[LoyaltyRewardResponse])
async def get_loyalty_rewards(
    loyalty_program_id: int = Query(...),
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty rewards"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    rewards = loyalty_program_service.get_loyalty_rewards(
        db=db,
        company_id=company_id,
        loyalty_program_id=loyalty_program_id,
        is_active=is_active
    )
    
    return rewards

@router.post("/loyalty-rewards/redeem", response_model=LoyaltyRewardRedemptionResponse)
async def redeem_loyalty_points(
    redemption_data: LoyaltyRewardRedemptionCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Redeem loyalty points"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        redemption = loyalty_program_service.redeem_loyalty_points(
            db=db,
            company_id=company_id,
            customer_id=redemption_data.customer_id,
            loyalty_program_id=redemption_data.loyalty_program_id,
            loyalty_reward_id=redemption_data.loyalty_reward_id,
            points_amount=redemption_data.points_amount,
            transaction_reference=redemption_data.transaction_reference,
            description=redemption_data.description,
            user_id=current_user.id
        )
        
        return redemption
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to redeem loyalty points: {str(e)}"
        )

# Loyalty Analytics Endpoints
@router.get("/loyalty-analytics", response_model=LoyaltyAnalyticsResponse)
async def get_loyalty_analytics(
    loyalty_program_id: int = Query(...),
    analytics_date: Optional[date] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = loyalty_program_service.get_loyalty_analytics(
        db=db,
        company_id=company_id,
        loyalty_program_id=loyalty_program_id,
        analytics_date=analytics_date
    )
    
    return analytics

# Loyalty Campaign Endpoints
@router.post("/loyalty-campaigns", response_model=LoyaltyCampaignResponse)
async def create_loyalty_campaign(
    campaign_data: LoyaltyCampaignCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("loyalty.manage")),
    db: Session = Depends(get_db)
):
    """Create loyalty campaign"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        campaign = loyalty_program_service.create_loyalty_campaign(
            db=db,
            company_id=company_id,
            loyalty_program_id=campaign_data.loyalty_program_id,
            campaign_name=campaign_data.campaign_name,
            campaign_code=campaign_data.campaign_code,
            campaign_type=campaign_data.campaign_type,
            campaign_config=campaign_data.campaign_config,
            target_customers=campaign_data.target_customers,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            notes=campaign_data.notes,
            user_id=current_user.id
        )
        
        return campaign
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create loyalty campaign: {str(e)}"
        )

@router.get("/loyalty-campaigns", response_model=List[LoyaltyCampaignResponse])
async def get_loyalty_campaigns(
    loyalty_program_id: int = Query(...),
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    campaign_status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty campaigns"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    campaigns = loyalty_program_service.get_loyalty_campaigns(
        db=db,
        company_id=company_id,
        loyalty_program_id=loyalty_program_id,
        is_active=is_active,
        campaign_status=campaign_status
    )
    
    return campaigns