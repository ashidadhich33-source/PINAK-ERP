# backend/app/api/endpoints/core/discount_integration.py
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
from ...services.core.discount_integration_service import DiscountIntegrationService

router = APIRouter()

# Initialize service
discount_integration_service = DiscountIntegrationService()

# Pydantic schemas for Discount Integration
class DiscountRuleCreateRequest(BaseModel):
    company_id: int
    rule_name: str
    rule_type: str
    target_id: Optional[int] = None
    condition_type: Optional[str] = None
    condition_value: Optional[Decimal] = None
    condition_operator: Optional[str] = None
    discount_type_id: int
    discount_value: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    priority: int = 0
    is_active: bool = True
    description: Optional[str] = None

class DiscountCouponCreateRequest(BaseModel):
    company_id: int
    coupon_code: str
    coupon_name: str
    description: Optional[str] = None
    discount_type_id: int
    discount_value: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_usage_count: Optional[int] = None
    is_single_use: bool = False
    customer_id: Optional[int] = None
    is_active: bool = True

class DiscountApplicationRequest(BaseModel):
    transaction_type: str
    transaction_id: int
    applied_discounts: List[dict]

class DiscountIntegrationResponse(BaseModel):
    success: bool
    rule_id: Optional[int] = None
    coupon_id: Optional[int] = None
    rule_name: Optional[str] = None
    coupon_code: Optional[str] = None
    integration_results: dict
    message: str

class DiscountApplicationResponse(BaseModel):
    success: bool
    total_discount: Decimal
    discount_applications: List[dict]
    accounting_result: dict
    message: str

class DiscountAnalyticsResponse(BaseModel):
    total_discounts: int
    total_discount_amount: Decimal
    average_discount: Decimal
    rule_usage: List[dict]
    coupon_usage: List[dict]
    period: dict

# Discount Integration Endpoints
@router.post("/rules", response_model=DiscountIntegrationResponse)
async def create_discount_rule_with_integrations(
    rule_data: DiscountRuleCreateRequest,
    current_user: User = Depends(require_permission("discounts.create")),
    db: Session = Depends(get_db)
):
    """Create discount rule with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, rule_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create discount rule with integrations
        result = discount_integration_service.create_discount_rule_with_integrations(
            db, rule_data.dict()
        )
        
        return DiscountIntegrationResponse(
            success=result['success'],
            rule_id=result['rule_id'],
            rule_name=result['rule_name'],
            integration_results=result['integration_results'],
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
            detail=f"Failed to create discount rule: {str(e)}"
        )

@router.post("/coupons", response_model=DiscountIntegrationResponse)
async def create_discount_coupon_with_integrations(
    coupon_data: DiscountCouponCreateRequest,
    current_user: User = Depends(require_permission("discounts.create")),
    db: Session = Depends(get_db)
):
    """Create discount coupon with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, coupon_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create discount coupon with integrations
        result = discount_integration_service.create_discount_coupon_with_integrations(
            db, coupon_data.dict()
        )
        
        return DiscountIntegrationResponse(
            success=result['success'],
            coupon_id=result['coupon_id'],
            coupon_code=result['coupon_code'],
            integration_results=result['integration_results'],
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
            detail=f"Failed to create discount coupon: {str(e)}"
        )

@router.post("/apply", response_model=DiscountApplicationResponse)
async def apply_discount_to_transaction(
    application_data: DiscountApplicationRequest,
    current_user: User = Depends(require_permission("discounts.apply")),
    db: Session = Depends(get_db)
):
    """Apply discount to transaction with full integrations"""
    
    try:
        # Apply discount to transaction
        result = discount_integration_service.apply_discount_to_transaction(
            db, application_data.dict()
        )
        
        return DiscountApplicationResponse(
            success=result['success'],
            total_discount=result['total_discount'],
            discount_applications=result['discount_applications'],
            accounting_result=result['accounting_result'],
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
            detail=f"Failed to apply discount: {str(e)}"
        )

@router.get("/analytics", response_model=DiscountAnalyticsResponse)
async def get_discount_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("discounts.analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive discount analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get discount analytics
        analytics = discount_integration_service.get_discount_analytics(db, company_id, from_date, to_date)
        
        return DiscountAnalyticsResponse(
            total_discounts=analytics['total_discounts'],
            total_discount_amount=analytics['total_discount_amount'],
            average_discount=analytics['average_discount'],
            rule_usage=analytics['rule_usage'],
            coupon_usage=analytics['coupon_usage'],
            period=analytics['period']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discount analytics: {str(e)}"
        )

@router.get("/rules/{rule_id}/applicable")
async def check_rule_applicability(
    rule_id: int,
    transaction_data: dict,
    current_user: User = Depends(require_permission("discounts.view")),
    db: Session = Depends(get_db)
):
    """Check if discount rule is applicable to transaction"""
    
    try:
        # Get discount rule
        from ...models.core.discount_management import DiscountRule
        discount_rule = db.query(DiscountRule).filter(DiscountRule.id == rule_id).first()
        
        if not discount_rule:
            raise HTTPException(
                status_code=404,
                detail="Discount rule not found"
            )
        
        # Check applicability
        is_applicable = discount_integration_service.is_rule_applicable(discount_rule, transaction_data)
        
        return {
            "rule_id": rule_id,
            "rule_name": discount_rule.rule_name,
            "is_applicable": is_applicable,
            "transaction_data": transaction_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check rule applicability: {str(e)}"
        )

@router.get("/coupons/{coupon_code}/applicable")
async def check_coupon_applicability(
    coupon_code: str,
    transaction_data: dict,
    current_user: User = Depends(require_permission("discounts.view")),
    db: Session = Depends(get_db)
):
    """Check if discount coupon is applicable to transaction"""
    
    try:
        # Get discount coupon
        from ...models.core.discount_management import DiscountCoupon
        discount_coupon = db.query(DiscountCoupon).filter(
            DiscountCoupon.coupon_code == coupon_code
        ).first()
        
        if not discount_coupon:
            raise HTTPException(
                status_code=404,
                detail="Discount coupon not found"
            )
        
        # Check applicability
        is_applicable = discount_integration_service.is_coupon_applicable(discount_coupon, transaction_data)
        
        return {
            "coupon_code": coupon_code,
            "coupon_name": discount_coupon.coupon_name,
            "is_applicable": is_applicable,
            "transaction_data": transaction_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check coupon applicability: {str(e)}"
        )

@router.get("/calculate")
async def calculate_discount_amount(
    rule_id: Optional[int] = Query(None),
    coupon_code: Optional[str] = Query(None),
    amount: Decimal = Query(...),
    current_user: User = Depends(require_permission("discounts.calculate")),
    db: Session = Depends(get_db)
):
    """Calculate discount amount for rule or coupon"""
    
    try:
        if rule_id:
            # Calculate for rule
            from ...models.core.discount_management import DiscountRule
            discount_rule = db.query(DiscountRule).filter(DiscountRule.id == rule_id).first()
            
            if not discount_rule:
                raise HTTPException(
                    status_code=404,
                    detail="Discount rule not found"
                )
            
            discount_amount = discount_integration_service.calculate_discount_amount(discount_rule, amount)
            
            return {
                "type": "rule",
                "rule_id": rule_id,
                "rule_name": discount_rule.rule_name,
                "amount": amount,
                "discount_amount": discount_amount,
                "final_amount": amount - discount_amount
            }
        
        elif coupon_code:
            # Calculate for coupon
            from ...models.core.discount_management import DiscountCoupon
            discount_coupon = db.query(DiscountCoupon).filter(
                DiscountCoupon.coupon_code == coupon_code
            ).first()
            
            if not discount_coupon:
                raise HTTPException(
                    status_code=404,
                    detail="Discount coupon not found"
                )
            
            discount_amount = discount_integration_service.calculate_coupon_discount(discount_coupon, amount)
            
            return {
                "type": "coupon",
                "coupon_code": coupon_code,
                "coupon_name": discount_coupon.coupon_name,
                "amount": amount,
                "discount_amount": discount_amount,
                "final_amount": amount - discount_amount
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Either rule_id or coupon_code must be provided"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate discount: {str(e)}"
        )

@router.get("/integration-status")
async def get_discount_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discounts.view")),
    db: Session = Depends(get_db)
):
    """Get discount integration status with other modules"""
    
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
            "discount_integration": {
                "inventory_integration": integrations.get('inventory', {}).get('status', 'unknown'),
                "customer_integration": integrations.get('customers', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "sales_integration": integrations.get('sales', {}).get('status', 'unknown'),
                "pos_integration": integrations.get('pos', {}).get('status', 'unknown')
            },
            "discount_features": {
                "rule_management": "enabled",
                "coupon_management": "enabled",
                "automatic_application": "enabled",
                "accounting_integration": "enabled",
                "analytics_tracking": "enabled"
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discount integration status: {str(e)}"
        )

@router.get("/workflow-automation")
async def get_discount_workflow_automation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discounts.automation")),
    db: Session = Depends(get_db)
):
    """Get discount workflow automation status"""
    
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
            "discount_workflow_automation": {
                "rule_creation": "enabled",
                "coupon_creation": "enabled",
                "automatic_application": "enabled",
                "accounting_integration": "enabled",
                "analytics_tracking": "enabled"
            },
            "automation_rules": [
                "Auto-create discount rules",
                "Auto-create discount coupons",
                "Auto-apply applicable discounts",
                "Auto-create accounting entries",
                "Auto-track discount analytics",
                "Auto-send notifications"
            ],
            "discount_capabilities": [
                "Rule-based discounts",
                "Coupon-based discounts",
                "Customer-specific discounts",
                "Tier-based discounts",
                "Automatic application",
                "Analytics and reporting"
            ],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discount workflow automation: {str(e)}"
        )