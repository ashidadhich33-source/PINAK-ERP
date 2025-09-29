# backend/app/api/endpoints/discount_management.py
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
from ...services.discount_management_service import discount_management_service

router = APIRouter()

# Pydantic schemas for Discount Type
class DiscountTypeCreateRequest(BaseModel):
    type_name: str
    type_code: str
    calculation_method: str
    description: Optional[str] = None
    is_default: bool = False
    notes: Optional[str] = None

class DiscountTypeResponse(BaseModel):
    id: int
    company_id: int
    type_name: str
    type_code: str
    description: Optional[str] = None
    calculation_method: str
    is_active: bool
    is_default: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Discount Rule
class DiscountRuleCreateRequest(BaseModel):
    rule_name: str
    rule_code: str
    discount_type_id: int
    rule_type: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    condition_type: str = 'quantity'
    condition_value: Optional[Decimal] = None
    condition_operator: str = '>='
    discount_value: Decimal = 0
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    priority: int = 0
    is_automatic: bool = False
    notes: Optional[str] = None

class DiscountRuleResponse(BaseModel):
    id: int
    company_id: int
    rule_name: str
    rule_code: str
    discount_type_id: int
    rule_type: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    condition_type: str
    condition_value: Optional[Decimal] = None
    condition_operator: str
    discount_value: Decimal
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    priority: int
    is_active: bool
    is_automatic: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Discount Coupon
class DiscountCouponCreateRequest(BaseModel):
    coupon_code: str
    coupon_name: str
    discount_type_id: int
    discount_value: Decimal = 0
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    max_usage_count: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_single_use: bool = False
    customer_id: Optional[int] = None
    notes: Optional[str] = None

class DiscountCouponResponse(BaseModel):
    id: int
    company_id: int
    coupon_code: str
    coupon_name: str
    discount_type_id: int
    discount_value: Decimal
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    max_usage_count: Optional[int] = None
    current_usage_count: int
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    is_single_use: bool
    customer_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Discount Tier
class DiscountTierCreateRequest(BaseModel):
    tier_name: str
    tier_code: str
    min_quantity: Decimal
    max_quantity: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    display_order: int = 0
    notes: Optional[str] = None

class DiscountTierResponse(BaseModel):
    id: int
    company_id: int
    tier_name: str
    tier_code: str
    min_quantity: Decimal
    max_quantity: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    is_active: bool
    display_order: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Customer Discount
class CustomerDiscountCreateRequest(BaseModel):
    customer_id: int
    discount_type_id: int
    discount_value: Decimal = 0
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None

class CustomerDiscountResponse(BaseModel):
    id: int
    company_id: int
    customer_id: int
    discount_type_id: int
    discount_value: Decimal
    discount_percentage: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Discount Report
class DiscountReportCreateRequest(BaseModel):
    report_name: str
    report_type: str
    from_date: date
    to_date: date
    notes: Optional[str] = None

class DiscountReportResponse(BaseModel):
    id: int
    company_id: int
    report_name: str
    report_type: str
    from_date: date
    to_date: date
    total_discounts: Decimal
    total_applications: int
    average_discount: Decimal
    generated_date: datetime
    generated_by: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Discount Type Endpoints
@router.post("/discount-types", response_model=DiscountTypeResponse)
async def create_discount_type(
    type_data: DiscountTypeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Create discount type"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        discount_type = discount_management_service.create_discount_type(
            db=db,
            company_id=company_id,
            type_name=type_data.type_name,
            type_code=type_data.type_code,
            calculation_method=type_data.calculation_method,
            description=type_data.description,
            is_default=type_data.is_default,
            notes=type_data.notes,
            user_id=current_user.id
        )
        
        return discount_type
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create discount type: {str(e)}"
        )

@router.get("/discount-types", response_model=List[DiscountTypeResponse])
async def get_discount_types(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("discount.view")),
    db: Session = Depends(get_db)
):
    """Get discount types"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    types = discount_management_service.get_discount_types(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    
    return types

# Discount Rule Endpoints
@router.post("/discount-rules", response_model=DiscountRuleResponse)
async def create_discount_rule(
    rule_data: DiscountRuleCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Create discount rule"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        rule = discount_management_service.create_discount_rule(
            db=db,
            company_id=company_id,
            rule_name=rule_data.rule_name,
            rule_code=rule_data.rule_code,
            discount_type_id=rule_data.discount_type_id,
            rule_type=rule_data.rule_type,
            target_type=rule_data.target_type,
            target_id=rule_data.target_id,
            condition_type=rule_data.condition_type,
            condition_value=rule_data.condition_value,
            condition_operator=rule_data.condition_operator,
            discount_value=rule_data.discount_value,
            discount_percentage=rule_data.discount_percentage,
            max_discount_amount=rule_data.max_discount_amount,
            min_order_amount=rule_data.min_order_amount,
            start_date=rule_data.start_date,
            end_date=rule_data.end_date,
            priority=rule_data.priority,
            is_automatic=rule_data.is_automatic,
            notes=rule_data.notes,
            user_id=current_user.id
        )
        
        return rule
        
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

@router.get("/discount-rules", response_model=List[DiscountRuleResponse])
async def get_discount_rules(
    company_id: int = Query(...),
    rule_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("discount.view")),
    db: Session = Depends(get_db)
):
    """Get discount rules"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    rules = discount_management_service.get_discount_rules(
        db=db,
        company_id=company_id,
        rule_type=rule_type,
        is_active=is_active
    )
    
    return rules

@router.post("/discount-rules/{rule_id}/apply")
async def apply_discount_rule(
    rule_id: int,
    transaction_type: str = Query(...),
    transaction_id: int = Query(...),
    item_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    original_amount: Decimal = Query(0),
    quantity: Decimal = Query(1),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Apply discount rule"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        application = discount_management_service.apply_discount_rule(
            db=db,
            company_id=company_id,
            rule_id=rule_id,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            item_id=item_id,
            customer_id=customer_id,
            original_amount=original_amount,
            quantity=quantity,
            user_id=current_user.id
        )
        
        return {
            "message": "Discount rule applied successfully",
            "application_id": application.id,
            "discount_amount": application.discount_amount,
            "final_amount": application.final_amount
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply discount rule: {str(e)}"
        )

# Discount Coupon Endpoints
@router.post("/discount-coupons", response_model=DiscountCouponResponse)
async def create_discount_coupon(
    coupon_data: DiscountCouponCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Create discount coupon"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        coupon = discount_management_service.create_discount_coupon(
            db=db,
            company_id=company_id,
            coupon_code=coupon_data.coupon_code,
            coupon_name=coupon_data.coupon_name,
            discount_type_id=coupon_data.discount_type_id,
            discount_value=coupon_data.discount_value,
            discount_percentage=coupon_data.discount_percentage,
            max_discount_amount=coupon_data.max_discount_amount,
            min_order_amount=coupon_data.min_order_amount,
            max_usage_count=coupon_data.max_usage_count,
            start_date=coupon_data.start_date,
            end_date=coupon_data.end_date,
            is_single_use=coupon_data.is_single_use,
            customer_id=coupon_data.customer_id,
            notes=coupon_data.notes,
            user_id=current_user.id
        )
        
        return coupon
        
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

@router.post("/discount-coupons/apply")
async def apply_discount_coupon(
    coupon_code: str = Query(...),
    customer_id: int = Query(...),
    transaction_type: str = Query(...),
    transaction_id: int = Query(...),
    order_amount: Decimal = Query(0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Apply discount coupon"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        usage = discount_management_service.apply_discount_coupon(
            db=db,
            company_id=company_id,
            coupon_code=coupon_code,
            customer_id=customer_id,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            order_amount=order_amount,
            user_id=current_user.id
        )
        
        return {
            "message": "Discount coupon applied successfully",
            "usage_id": usage.id,
            "discount_amount": usage.discount_amount
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply discount coupon: {str(e)}"
        )

# Discount Tier Endpoints
@router.post("/discount-tiers", response_model=DiscountTierResponse)
async def create_discount_tier(
    tier_data: DiscountTierCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Create discount tier"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        tier = discount_management_service.create_discount_tier(
            db=db,
            company_id=company_id,
            tier_name=tier_data.tier_name,
            tier_code=tier_data.tier_code,
            min_quantity=tier_data.min_quantity,
            max_quantity=tier_data.max_quantity,
            discount_percentage=tier_data.discount_percentage,
            discount_amount=tier_data.discount_amount,
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
            detail=f"Failed to create discount tier: {str(e)}"
        )

@router.post("/discount-tiers/apply")
async def apply_discount_tier(
    item_id: int = Query(...),
    quantity: Decimal = Query(...),
    unit_price: Decimal = Query(...),
    customer_id: Optional[int] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Apply discount tier"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        application = discount_management_service.apply_discount_tier(
            db=db,
            company_id=company_id,
            item_id=item_id,
            quantity=quantity,
            unit_price=unit_price,
            customer_id=customer_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Discount tier applied successfully",
            "application_id": application.id,
            "discount_amount": application.discount_amount,
            "final_amount": application.final_amount
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply discount tier: {str(e)}"
        )

# Customer Discount Endpoints
@router.post("/customer-discounts", response_model=CustomerDiscountResponse)
async def create_customer_discount(
    discount_data: CustomerDiscountCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.manage")),
    db: Session = Depends(get_db)
):
    """Create customer discount"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        customer_discount = discount_management_service.create_customer_discount(
            db=db,
            company_id=company_id,
            customer_id=discount_data.customer_id,
            discount_type_id=discount_data.discount_type_id,
            discount_value=discount_data.discount_value,
            discount_percentage=discount_data.discount_percentage,
            max_discount_amount=discount_data.max_discount_amount,
            min_order_amount=discount_data.min_order_amount,
            start_date=discount_data.start_date,
            end_date=discount_data.end_date,
            notes=discount_data.notes,
            user_id=current_user.id
        )
        
        return customer_discount
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create customer discount: {str(e)}"
        )

# Discount Analytics Endpoints
@router.get("/analytics")
async def get_discount_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    rule_id: Optional[int] = Query(None),
    coupon_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("discount.view")),
    db: Session = Depends(get_db)
):
    """Get discount analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = discount_management_service.get_discount_analytics(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date,
        rule_id=rule_id,
        coupon_id=coupon_id
    )
    
    return analytics

# Discount Report Endpoints
@router.post("/reports", response_model=DiscountReportResponse)
async def generate_discount_report(
    report_data: DiscountReportCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("discount.view")),
    db: Session = Depends(get_db)
):
    """Generate discount report"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        report = discount_management_service.generate_discount_report(
            db=db,
            company_id=company_id,
            report_name=report_data.report_name,
            report_type=report_data.report_type,
            from_date=report_data.from_date,
            to_date=report_data.to_date,
            user_id=current_user.id
        )
        
        return report
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate discount report: {str(e)}"
        )