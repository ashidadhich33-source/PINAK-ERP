# backend/app/api/endpoints/customers/customer_loyalty_integration.py
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
from ...services.customers.customer_loyalty_integration_service import CustomerLoyaltyIntegrationService

router = APIRouter()

# Initialize service
customer_loyalty_service = CustomerLoyaltyIntegrationService()

# Pydantic schemas for Customer Loyalty Integration
class CustomerCreateRequest(BaseModel):
    company_id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    customer_type: str = 'regular'
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    notes: Optional[str] = None

class LoyaltyPointsEarningRequest(BaseModel):
    customer_id: int
    transaction_type: str
    transaction_id: int
    transaction_number: str
    total_amount: Decimal

class LoyaltyPointsRedemptionRequest(BaseModel):
    customer_id: int
    points_to_redeem: int
    redemption_type: str
    redemption_id: Optional[int] = None
    redemption_number: Optional[str] = None

class CustomerLoyaltyResponse(BaseModel):
    success: bool
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    loyalty_integration: dict
    discount_integration: dict
    accounting_integration: dict
    message: str

class LoyaltyPointsResponse(BaseModel):
    success: bool
    points_earned: Optional[int] = None
    points_redeemed: Optional[int] = None
    new_balance: int
    new_tier: str
    tier_upgraded: Optional[bool] = None
    tier_downgraded: Optional[bool] = None
    message: str

class CustomerLoyaltyBenefitsResponse(BaseModel):
    customer_id: int
    current_points: int
    current_tier: str
    tier_benefits: dict
    available_rewards: List[dict]
    loyalty_history: List[dict]
    next_tier: dict
    loyalty_program: dict

class CustomerAnalyticsResponse(BaseModel):
    customer_id: int
    customer_name: str
    customer_type: str
    customer_tier: str
    loyalty_points: int
    sales_analytics: dict
    loyalty_analytics: dict
    purchase_behavior: dict
    recommendations: List[dict]
    last_updated: datetime

# Customer Loyalty Integration Endpoints
@router.post("/customers", response_model=CustomerLoyaltyResponse)
async def create_customer_with_loyalty_integration(
    customer_data: CustomerCreateRequest,
    current_user: User = Depends(require_permission("customers.create")),
    db: Session = Depends(get_db)
):
    """Create customer with full loyalty integration"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, customer_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create customer with loyalty integration
        result = customer_loyalty_service.create_customer_with_loyalty_integration(
            db, customer_data.dict()
        )
        
        return CustomerLoyaltyResponse(
            success=result['success'],
            customer_id=result['customer_id'],
            customer_name=result['customer_name'],
            loyalty_integration=result['loyalty_integration'],
            discount_integration=result['discount_integration'],
            accounting_integration=result['accounting_integration'],
            message=result['message']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create customer: {str(e)}"
        )

@router.post("/loyalty/earn", response_model=LoyaltyPointsResponse)
async def process_loyalty_points_earning(
    earning_data: LoyaltyPointsEarningRequest,
    current_user: User = Depends(require_permission("loyalty.earn")),
    db: Session = Depends(get_db)
):
    """Process loyalty points earning for customer"""
    
    try:
        # Process loyalty points earning
        result = customer_loyalty_service.process_loyalty_points_earning(
            db, earning_data.customer_id, earning_data.dict()
        )
        
        return LoyaltyPointsResponse(
            success=result['status'] == 'success',
            points_earned=result.get('points_earned'),
            new_balance=result.get('new_balance', 0),
            new_tier=result.get('new_tier', 'bronze'),
            tier_upgraded=result.get('tier_upgraded', False),
            message=result.get('message', 'Points processed successfully')
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process loyalty points earning: {str(e)}"
        )

@router.post("/loyalty/redeem", response_model=LoyaltyPointsResponse)
async def process_loyalty_points_redemption(
    redemption_data: LoyaltyPointsRedemptionRequest,
    current_user: User = Depends(require_permission("loyalty.redeem")),
    db: Session = Depends(get_db)
):
    """Process loyalty points redemption for customer"""
    
    try:
        # Process loyalty points redemption
        result = customer_loyalty_service.process_loyalty_points_redemption(
            db, redemption_data.customer_id, redemption_data.dict()
        )
        
        return LoyaltyPointsResponse(
            success=result['status'] == 'success',
            points_redeemed=result.get('points_redeemed'),
            new_balance=result.get('new_balance', 0),
            new_tier=result.get('new_tier', 'bronze'),
            tier_downgraded=result.get('tier_downgraded', False),
            message=result.get('message', 'Points redeemed successfully')
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process loyalty points redemption: {str(e)}"
        )

@router.get("/loyalty/benefits/{customer_id}", response_model=CustomerLoyaltyBenefitsResponse)
async def get_customer_loyalty_benefits(
    customer_id: int,
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty benefits and rewards"""
    
    try:
        # Get customer loyalty benefits
        benefits = customer_loyalty_service.get_customer_loyalty_benefits(db, customer_id)
        
        return CustomerLoyaltyBenefitsResponse(
            customer_id=benefits['customer_id'],
            current_points=benefits['current_points'],
            current_tier=benefits['current_tier'],
            tier_benefits=benefits['tier_benefits'],
            available_rewards=benefits['available_rewards'],
            loyalty_history=benefits['loyalty_history'],
            next_tier=benefits['next_tier'],
            loyalty_program=benefits['loyalty_program']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer loyalty benefits: {str(e)}"
        )

@router.get("/analytics/{customer_id}", response_model=CustomerAnalyticsResponse)
async def get_customer_analytics(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive customer analytics"""
    
    try:
        # Get customer analytics
        analytics = customer_loyalty_service.get_customer_analytics(db, customer_id)
        
        return CustomerAnalyticsResponse(
            customer_id=analytics['customer_id'],
            customer_name=analytics['customer_name'],
            customer_type=analytics['customer_type'],
            customer_tier=analytics['customer_tier'],
            loyalty_points=analytics['loyalty_points'],
            sales_analytics=analytics['sales_analytics'],
            loyalty_analytics=analytics['loyalty_analytics'],
            purchase_behavior=analytics['purchase_behavior'],
            recommendations=analytics['recommendations'],
            last_updated=analytics['last_updated']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer analytics: {str(e)}"
        )

@router.get("/loyalty/history/{customer_id}")
async def get_customer_loyalty_history(
    customer_id: int,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty history"""
    
    try:
        # Get loyalty history
        history = customer_loyalty_service.get_loyalty_history(db, customer_id, limit)
        
        return {
            "customer_id": customer_id,
            "loyalty_history": history,
            "total_records": len(history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer loyalty history: {str(e)}"
        )

@router.get("/recommendations/{customer_id}")
async def get_customer_recommendations(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.recommendations")),
    db: Session = Depends(get_db)
):
    """Get customer recommendations"""
    
    try:
        # Get customer analytics
        analytics = customer_loyalty_service.get_customer_analytics(db, customer_id)
        
        return {
            "customer_id": customer_id,
            "recommendations": analytics.get('recommendations', []),
            "purchase_behavior": analytics.get('purchase_behavior', {}),
            "last_updated": analytics.get('last_updated')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer recommendations: {str(e)}"
        )

@router.get("/tier-benefits/{tier}")
async def get_tier_benefits(
    tier: str,
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get tier-specific benefits"""
    
    try:
        # Get tier benefits
        benefits = customer_loyalty_service.get_tier_benefits(db, tier)
        
        return {
            "tier": tier,
            "benefits": benefits
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tier benefits: {str(e)}"
        )

@router.get("/integration-status")
async def get_customer_loyalty_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty integration status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get integration status
        integrations = company_service.get_company_integrations(db, company_id)
        
        return {
            "customer_loyalty_integration": {
                "customer_integration": integrations.get('customers', {}).get('status', 'unknown'),
                "loyalty_integration": integrations.get('loyalty', {}).get('status', 'unknown'),
                "discount_integration": integrations.get('discounts', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "sales_integration": integrations.get('sales', {}).get('status', 'unknown'),
                "pos_integration": integrations.get('pos', {}).get('status', 'unknown')
            },
            "loyalty_features": {
                "points_earning": "enabled",
                "points_redemption": "enabled",
                "tier_management": "enabled",
                "customer_benefits": "enabled",
                "loyalty_analytics": "enabled",
                "recommendations": "enabled"
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer loyalty integration status: {str(e)}"
        )

@router.get("/workflow-automation")
async def get_customer_loyalty_workflow_automation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("customers.automation")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty workflow automation status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get workflow automation status
        return {
            "customer_loyalty_workflow_automation": {
                "customer_creation": "enabled",
                "loyalty_initialization": "enabled",
                "points_earning": "enabled",
                "points_redemption": "enabled",
                "tier_management": "enabled",
                "benefits_assignment": "enabled",
                "analytics_tracking": "enabled"
            },
            "automation_rules": [
                "Auto-initialize loyalty for new customers",
                "Auto-assign tier-based benefits",
                "Auto-earn points on transactions",
                "Auto-update customer tiers",
                "Auto-track loyalty analytics",
                "Auto-generate recommendations"
            ],
            "loyalty_capabilities": [
                "Multi-tier loyalty system",
                "Points earning and redemption",
                "Customer-specific benefits",
                "Loyalty analytics and reporting",
                "Recommendation engine",
                "Integration with all modules"
            ],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer loyalty workflow automation: {str(e)}"
        )