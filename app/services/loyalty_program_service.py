# backend/app/services/loyalty_program_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid

from ..models.loyalty_program import (
    LoyaltyProgram, LoyaltyTier, CustomerLoyaltyTier, LoyaltyPoint, LoyaltyPointTransaction,
    LoyaltyReward, LoyaltyRewardRedemption, LoyaltyTransaction, LoyaltyAnalytics,
    LoyaltyCampaign, LoyaltyCampaignParticipant, LoyaltyReferral, LoyaltyNotification,
    LoyaltyConfiguration
)
from ..models.customer import Customer

logger = logging.getLogger(__name__)

class LoyaltyProgramService:
    """Service class for loyalty program management"""
    
    def __init__(self):
        pass
    
    # Loyalty Program Management
    def create_loyalty_program(
        self, 
        db: Session, 
        company_id: int,
        program_name: str,
        program_code: str,
        program_type: str,
        start_date: date,
        end_date: date = None,
        description: str = None,
        auto_enrollment: bool = False,
        enrollment_conditions: Dict = None,
        program_config: Dict = None,
        terms_conditions: str = None,
        notes: str = None,
        user_id: int = None
    ) -> LoyaltyProgram:
        """Create loyalty program"""
        
        # Check if program code already exists
        existing_program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.company_id == company_id,
            LoyaltyProgram.program_code == program_code
        ).first()
        
        if existing_program:
            raise ValueError(f"Loyalty program code {program_code} already exists")
        
        # Create loyalty program
        program = LoyaltyProgram(
            company_id=company_id,
            program_name=program_name,
            program_code=program_code,
            program_type=program_type,
            start_date=start_date,
            end_date=end_date,
            description=description,
            auto_enrollment=auto_enrollment,
            enrollment_conditions=enrollment_conditions,
            program_config=program_config or {},
            terms_conditions=terms_conditions,
            notes=notes,
            created_by=user_id
        )
        
        db.add(program)
        db.commit()
        db.refresh(program)
        
        logger.info(f"Loyalty program created: {program_name}")
        
        return program
    
    def get_loyalty_programs(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None,
        program_type: Optional[str] = None
    ) -> List[LoyaltyProgram]:
        """Get loyalty programs"""
        
        query = db.query(LoyaltyProgram).filter(LoyaltyProgram.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(LoyaltyProgram.is_active == is_active)
        
        if program_type:
            query = query.filter(LoyaltyProgram.program_type == program_type)
        
        programs = query.order_by(LoyaltyProgram.program_name).all()
        
        return programs
    
    # Loyalty Tier Management
    def create_loyalty_tier(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        tier_name: str,
        tier_code: str,
        tier_level: int,
        min_points: Decimal,
        max_points: Decimal = None,
        tier_benefits: Dict = None,
        tier_discount: Decimal = None,
        tier_multiplier: Decimal = 1.0,
        display_order: int = 0,
        notes: str = None,
        user_id: int = None
    ) -> LoyaltyTier:
        """Create loyalty tier"""
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Create loyalty tier
        tier = LoyaltyTier(
            company_id=company_id,
            loyalty_program_id=loyalty_program_id,
            tier_name=tier_name,
            tier_code=tier_code,
            tier_level=tier_level,
            min_points=min_points,
            max_points=max_points,
            tier_benefits=tier_benefits,
            tier_discount=tier_discount,
            tier_multiplier=tier_multiplier,
            display_order=display_order,
            notes=notes,
            created_by=user_id
        )
        
        db.add(tier)
        db.commit()
        db.refresh(tier)
        
        logger.info(f"Loyalty tier created: {tier_name}")
        
        return tier
    
    def get_loyalty_tiers(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        is_active: Optional[bool] = None
    ) -> List[LoyaltyTier]:
        """Get loyalty tiers"""
        
        query = db.query(LoyaltyTier).filter(
            LoyaltyTier.company_id == company_id,
            LoyaltyTier.loyalty_program_id == loyalty_program_id
        )
        
        if is_active is not None:
            query = query.filter(LoyaltyTier.is_active == is_active)
        
        tiers = query.order_by(LoyaltyTier.tier_level).all()
        
        return tiers
    
    # Customer Loyalty Tier Management
    def assign_customer_tier(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        loyalty_program_id: int,
        loyalty_tier_id: int,
        user_id: int = None
    ) -> CustomerLoyaltyTier:
        """Assign customer to loyalty tier"""
        
        # Validate customer
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Validate loyalty tier
        tier = db.query(LoyaltyTier).filter(
            LoyaltyTier.id == loyalty_tier_id,
            LoyaltyTier.loyalty_program_id == loyalty_program_id
        ).first()
        
        if not tier:
            raise ValueError("Loyalty tier not found")
        
        # Check if customer already has a tier in this program
        existing_tier = db.query(CustomerLoyaltyTier).filter(
            CustomerLoyaltyTier.customer_id == customer_id,
            CustomerLoyaltyTier.loyalty_program_id == loyalty_program_id
        ).first()
        
        if existing_tier:
            # Update existing tier
            existing_tier.loyalty_tier_id = loyalty_tier_id
            existing_tier.tier_achieved_date = datetime.utcnow()
            existing_tier.updated_by = user_id
            existing_tier.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Customer tier updated: {customer.name}")
            
            return existing_tier
        else:
            # Create new customer tier
            customer_tier = CustomerLoyaltyTier(
                company_id=company_id,
                customer_id=customer_id,
                loyalty_program_id=loyalty_program_id,
                loyalty_tier_id=loyalty_tier_id,
                tier_achieved_date=datetime.utcnow(),
                created_by=user_id
            )
            
            db.add(customer_tier)
            db.commit()
            db.refresh(customer_tier)
            
            logger.info(f"Customer tier assigned: {customer.name}")
            
            return customer_tier
    
    # Loyalty Point Management
    def create_loyalty_point(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        point_name: str,
        point_code: str,
        point_value: Decimal,
        point_type: str,
        point_category: str,
        earning_conditions: Dict = None,
        expiry_days: int = None,
        notes: str = None,
        user_id: int = None
    ) -> LoyaltyPoint:
        """Create loyalty point"""
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Create loyalty point
        point = LoyaltyPoint(
            company_id=company_id,
            loyalty_program_id=loyalty_program_id,
            point_name=point_name,
            point_code=point_code,
            point_value=point_value,
            point_type=point_type,
            point_category=point_category,
            earning_conditions=earning_conditions,
            expiry_days=expiry_days,
            notes=notes,
            created_by=user_id
        )
        
        db.add(point)
        db.commit()
        db.refresh(point)
        
        logger.info(f"Loyalty point created: {point_name}")
        
        return point
    
    def earn_loyalty_points(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        loyalty_program_id: int,
        loyalty_point_id: int,
        points_amount: Decimal,
        transaction_reference: str = None,
        description: str = None,
        user_id: int = None
    ) -> LoyaltyPointTransaction:
        """Earn loyalty points"""
        
        # Validate customer
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Validate loyalty point
        point = db.query(LoyaltyPoint).filter(
            LoyaltyPoint.id == loyalty_point_id,
            LoyaltyPoint.loyalty_program_id == loyalty_program_id
        ).first()
        
        if not point:
            raise ValueError("Loyalty point not found")
        
        # Get current customer tier
        customer_tier = db.query(CustomerLoyaltyTier).filter(
            CustomerLoyaltyTier.customer_id == customer_id,
            CustomerLoyaltyTier.loyalty_program_id == loyalty_program_id
        ).first()
        
        # Calculate points with tier multiplier
        if customer_tier and customer_tier.loyalty_tier.tier_multiplier:
            points_amount = points_amount * customer_tier.loyalty_tier.tier_multiplier
        
        # Get current points balance
        current_balance = self._get_customer_points_balance(db, customer_id, loyalty_program_id)
        new_balance = current_balance + points_amount
        
        # Create point transaction
        transaction = LoyaltyPointTransaction(
            company_id=company_id,
            customer_id=customer_id,
            loyalty_program_id=loyalty_program_id,
            loyalty_point_id=loyalty_point_id,
            transaction_type='earn',
            points_amount=points_amount,
            points_balance=new_balance,
            transaction_reference=transaction_reference,
            description=description,
            created_by=user_id
        )
        
        db.add(transaction)
        
        # Update customer tier points
        if customer_tier:
            customer_tier.current_points = new_balance
            customer_tier.lifetime_points += points_amount
            customer_tier.updated_by = user_id
            customer_tier.updated_at = datetime.utcnow()
        else:
            # Create customer tier if not exists
            customer_tier = CustomerLoyaltyTier(
                company_id=company_id,
                customer_id=customer_id,
                loyalty_program_id=loyalty_program_id,
                loyalty_tier_id=1,  # Default tier
                current_points=new_balance,
                lifetime_points=points_amount,
                created_by=user_id
            )
            db.add(customer_tier)
        
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Loyalty points earned: {points_amount} for customer {customer_id}")
        
        return transaction
    
    def redeem_loyalty_points(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        loyalty_program_id: int,
        loyalty_reward_id: int,
        points_amount: Decimal,
        transaction_reference: str = None,
        description: str = None,
        user_id: int = None
    ) -> LoyaltyRewardRedemption:
        """Redeem loyalty points"""
        
        # Validate customer
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Validate loyalty reward
        reward = db.query(LoyaltyReward).filter(
            LoyaltyReward.id == loyalty_reward_id,
            LoyaltyReward.loyalty_program_id == loyalty_program_id
        ).first()
        
        if not reward:
            raise ValueError("Loyalty reward not found")
        
        # Check if customer has enough points
        current_balance = self._get_customer_points_balance(db, customer_id, loyalty_program_id)
        if current_balance < points_amount:
            raise ValueError("Insufficient loyalty points")
        
        # Check if reward is available
        if reward.max_redemptions and reward.current_redemptions >= reward.max_redemptions:
            raise ValueError("Reward redemption limit reached")
        
        # Create redemption code
        redemption_code = f"RED-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        # Create reward redemption
        redemption = LoyaltyRewardRedemption(
            company_id=company_id,
            customer_id=customer_id,
            loyalty_program_id=loyalty_program_id,
            loyalty_reward_id=loyalty_reward_id,
            redemption_code=redemption_code,
            points_used=points_amount,
            reward_value=reward.reward_value,
            transaction_reference=transaction_reference,
            description=description,
            created_by=user_id
        )
        
        db.add(redemption)
        
        # Create point transaction for redemption
        new_balance = current_balance - points_amount
        point_transaction = LoyaltyPointTransaction(
            company_id=company_id,
            customer_id=customer_id,
            loyalty_program_id=loyalty_program_id,
            loyalty_point_id=1,  # Default point type for redemption
            transaction_type='redeem',
            points_amount=-points_amount,
            points_balance=new_balance,
            transaction_reference=transaction_reference,
            description=description,
            created_by=user_id
        )
        
        db.add(point_transaction)
        
        # Update customer tier points
        customer_tier = db.query(CustomerLoyaltyTier).filter(
            CustomerLoyaltyTier.customer_id == customer_id,
            CustomerLoyaltyTier.loyalty_program_id == loyalty_program_id
        ).first()
        
        if customer_tier:
            customer_tier.current_points = new_balance
            customer_tier.updated_by = user_id
            customer_tier.updated_at = datetime.utcnow()
        
        # Update reward redemption count
        reward.current_redemptions += 1
        
        db.commit()
        db.refresh(redemption)
        
        logger.info(f"Loyalty points redeemed: {points_amount} for customer {customer_id}")
        
        return redemption
    
    def _get_customer_points_balance(
        self, 
        db: Session, 
        customer_id: int, 
        loyalty_program_id: int
    ) -> Decimal:
        """Get customer points balance"""
        
        # Get latest transaction for balance
        latest_transaction = db.query(LoyaltyPointTransaction).filter(
            LoyaltyPointTransaction.customer_id == customer_id,
            LoyaltyPointTransaction.loyalty_program_id == loyalty_program_id
        ).order_by(LoyaltyPointTransaction.transaction_date.desc()).first()
        
        if latest_transaction:
            return latest_transaction.points_balance
        else:
            return Decimal(0)
    
    # Loyalty Reward Management
    def create_loyalty_reward(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        reward_name: str,
        reward_code: str,
        reward_type: str,
        reward_value: Decimal,
        points_required: Decimal,
        start_date: date,
        reward_conditions: Dict = None,
        max_redemptions: int = None,
        end_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> LoyaltyReward:
        """Create loyalty reward"""
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Create loyalty reward
        reward = LoyaltyReward(
            company_id=company_id,
            loyalty_program_id=loyalty_program_id,
            reward_name=reward_name,
            reward_code=reward_code,
            reward_type=reward_type,
            reward_value=reward_value,
            points_required=points_required,
            reward_conditions=reward_conditions,
            max_redemptions=max_redemptions,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            created_by=user_id
        )
        
        db.add(reward)
        db.commit()
        db.refresh(reward)
        
        logger.info(f"Loyalty reward created: {reward_name}")
        
        return reward
    
    def get_loyalty_rewards(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        is_active: Optional[bool] = None
    ) -> List[LoyaltyReward]:
        """Get loyalty rewards"""
        
        query = db.query(LoyaltyReward).filter(
            LoyaltyReward.company_id == company_id,
            LoyaltyReward.loyalty_program_id == loyalty_program_id
        )
        
        if is_active is not None:
            query = query.filter(LoyaltyReward.is_active == is_active)
        
        rewards = query.order_by(LoyaltyReward.points_required).all()
        
        return rewards
    
    # Loyalty Analytics
    def get_loyalty_analytics(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        analytics_date: Optional[date] = None
    ) -> LoyaltyAnalytics:
        """Get loyalty analytics"""
        
        # Get or create analytics record
        analytics = db.query(LoyaltyAnalytics).filter(
            LoyaltyAnalytics.loyalty_program_id == loyalty_program_id,
            LoyaltyAnalytics.analytics_date == (analytics_date or date.today())
        ).first()
        
        if not analytics:
            # Create new analytics record
            analytics = LoyaltyAnalytics(
                company_id=company_id,
                loyalty_program_id=loyalty_program_id,
                analytics_date=analytics_date or date.today(),
                created_by=1  # System user
            )
            
            db.add(analytics)
            db.commit()
            db.refresh(analytics)
        
        # Calculate analytics
        self._calculate_loyalty_analytics(db, analytics)
        
        return analytics
    
    def _calculate_loyalty_analytics(
        self, 
        db: Session, 
        analytics: LoyaltyAnalytics
    ):
        """Calculate loyalty analytics"""
        
        # Get total customers
        total_customers = db.query(CustomerLoyaltyTier).filter(
            CustomerLoyaltyTier.loyalty_program_id == analytics.loyalty_program_id
        ).count()
        
        # Get active customers (with points > 0)
        active_customers = db.query(CustomerLoyaltyTier).filter(
            CustomerLoyaltyTier.loyalty_program_id == analytics.loyalty_program_id,
            CustomerLoyaltyTier.current_points > 0
        ).count()
        
        # Get total points earned
        total_points_earned = db.query(func.sum(LoyaltyPointTransaction.points_amount)).filter(
            LoyaltyPointTransaction.loyalty_program_id == analytics.loyalty_program_id,
            LoyaltyPointTransaction.transaction_type == 'earn'
        ).scalar() or 0
        
        # Get total points redeemed
        total_points_redeemed = db.query(func.sum(LoyaltyPointTransaction.points_amount)).filter(
            LoyaltyPointTransaction.loyalty_program_id == analytics.loyalty_program_id,
            LoyaltyPointTransaction.transaction_type == 'redeem'
        ).scalar() or 0
        
        # Get total rewards redemptions
        total_rewards_redemptions = db.query(LoyaltyRewardRedemption).filter(
            LoyaltyRewardRedemption.loyalty_program_id == analytics.loyalty_program_id
        ).count()
        
        # Get total reward value
        total_reward_value = db.query(func.sum(LoyaltyRewardRedemption.reward_value)).filter(
            LoyaltyRewardRedemption.loyalty_program_id == analytics.loyalty_program_id
        ).scalar() or 0
        
        # Calculate average points per customer
        if total_customers > 0:
            average_points_per_customer = total_points_earned / total_customers
        else:
            average_points_per_customer = 0
        
        # Calculate redemption rate
        if total_points_earned > 0:
            redemption_rate = (abs(total_points_redeemed) / total_points_earned) * 100
        else:
            redemption_rate = 0
        
        # Update analytics
        analytics.total_customers = total_customers
        analytics.active_customers = active_customers
        analytics.total_points_earned = total_points_earned
        analytics.total_points_redeemed = abs(total_points_redeemed)
        analytics.total_rewards_redemptions = total_rewards_redemptions
        analytics.total_reward_value = total_reward_value
        analytics.average_points_per_customer = average_points_per_customer
        analytics.redemption_rate = redemption_rate
        
        # Update analytics data
        analytics.analytics_data = {
            "calculated_date": datetime.utcnow().isoformat(),
            "program_id": analytics.loyalty_program_id,
            "analytics_date": analytics.analytics_date.isoformat()
        }
        
        db.commit()
    
    # Loyalty Campaign Management
    def create_loyalty_campaign(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        campaign_name: str,
        campaign_code: str,
        campaign_type: str,
        campaign_config: Dict,
        start_date: date,
        target_customers: Dict = None,
        end_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> LoyaltyCampaign:
        """Create loyalty campaign"""
        
        # Validate loyalty program
        program = db.query(LoyaltyProgram).filter(
            LoyaltyProgram.id == loyalty_program_id,
            LoyaltyProgram.company_id == company_id
        ).first()
        
        if not program:
            raise ValueError("Loyalty program not found")
        
        # Create loyalty campaign
        campaign = LoyaltyCampaign(
            company_id=company_id,
            loyalty_program_id=loyalty_program_id,
            campaign_name=campaign_name,
            campaign_code=campaign_code,
            campaign_type=campaign_type,
            campaign_config=campaign_config,
            target_customers=target_customers,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            created_by=user_id
        )
        
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        logger.info(f"Loyalty campaign created: {campaign_name}")
        
        return campaign
    
    def get_loyalty_campaigns(
        self, 
        db: Session, 
        company_id: int,
        loyalty_program_id: int,
        is_active: Optional[bool] = None,
        campaign_status: Optional[str] = None
    ) -> List[LoyaltyCampaign]:
        """Get loyalty campaigns"""
        
        query = db.query(LoyaltyCampaign).filter(
            LoyaltyCampaign.company_id == company_id,
            LoyaltyCampaign.loyalty_program_id == loyalty_program_id
        )
        
        if is_active is not None:
            query = query.filter(LoyaltyCampaign.is_active == is_active)
        
        if campaign_status:
            query = query.filter(LoyaltyCampaign.campaign_status == campaign_status)
        
        campaigns = query.order_by(LoyaltyCampaign.start_date.desc()).all()
        
        return campaigns

# Global service instance
loyalty_program_service = LoyaltyProgramService()