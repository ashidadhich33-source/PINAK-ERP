# backend/app/api/endpoints/pos/pos_discount_integration.py
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
from ...services.pos.pos_discount_service import POSDiscountService

router = APIRouter()

# Initialize service
pos_discount_service = POSDiscountService()

# Pydantic schemas for POS Discount Integration
class POSDiscountCalculationRequest(BaseModel):
    transaction_id: Optional[int] = None
    customer_id: Optional[int] = None
    store_id: Optional[int] = None
    subtotal: Decimal
    items: List[dict] = []
    applied_coupons: List[str] = []
    loyalty_points_used: int = 0

class POSDiscountCalculationResponse(BaseModel):
    subtotal: Decimal
    discounts: List[dict]
    total_discount: Decimal
    final_amount: Decimal
    customer_benefits: dict
    loyalty_points: int
    available_coupons: List[dict]
    calculation_id: Optional[int] = None

class POSApplyCouponRequest(BaseModel):
    transaction_id: int
    coupon_code: str
    customer_id: Optional[int] = None

class POSApplyCouponResponse(BaseModel):
    success: bool
    discount_amount: Decimal
    coupon_name: str
    message: str
    final_amount: Decimal

class POSRemoveDiscountRequest(BaseModel):
    transaction_id: int
    discount_id: int

class POSRemoveDiscountResponse(BaseModel):
    success: bool
    message: str
    final_amount: Decimal

class POSLoyaltyPointsRequest(BaseModel):
    transaction_id: int
    customer_id: int
    points_to_redeem: int

class POSLoyaltyPointsResponse(BaseModel):
    success: bool
    points_redeemed: int
    discount_amount: Decimal
    points_balance: int
    final_amount: Decimal

class POSDiscountAnalyticsRequest(BaseModel):
    from_date: date
    to_date: date
    store_id: Optional[int] = None
    discount_type: Optional[str] = None

class POSDiscountAnalyticsResponse(BaseModel):
    total_transactions: int
    total_discount_amount: Decimal
    average_discount_per_transaction: Decimal
    discount_breakdown: dict
    top_discounts: List[dict]
    customer_analytics: dict

# POS Discount Calculation Endpoints
@router.post("/calculate-discounts", response_model=POSDiscountCalculationResponse)
async def calculate_pos_discounts(
    calculation_data: POSDiscountCalculationRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Calculate all applicable discounts for POS transaction"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert request to transaction data
        transaction_data = {
            'transaction_id': calculation_data.transaction_id,
            'customer_id': calculation_data.customer_id,
            'store_id': calculation_data.store_id,
            'subtotal': calculation_data.subtotal,
            'items': calculation_data.items,
            'applied_coupons': calculation_data.applied_coupons,
            'loyalty_points_used': calculation_data.loyalty_points_used
        }
        
        # Calculate discounts
        result = pos_discount_service.calculate_transaction_discounts(
            db=db,
            transaction_data=transaction_data,
            customer_id=calculation_data.customer_id,
            store_id=calculation_data.store_id
        )
        
        return POSDiscountCalculationResponse(
            subtotal=result['subtotal'],
            discounts=result['discounts'],
            total_discount=result['total_discount'],
            final_amount=result['final_amount'],
            customer_benefits=result.get('customer_benefits', {}),
            loyalty_points=result.get('loyalty_points', 0),
            available_coupons=result.get('available_coupons', []),
            calculation_id=calculation_data.transaction_id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate discounts: {str(e)}"
        )

@router.post("/apply-coupon", response_model=POSApplyCouponResponse)
async def apply_coupon_to_pos_transaction(
    coupon_data: POSApplyCouponRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Apply coupon to POS transaction"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_discount_service.apply_coupon(
            db=db,
            transaction_id=coupon_data.transaction_id,
            coupon_code=coupon_data.coupon_code,
            customer_id=coupon_data.customer_id,
            user_id=current_user.id
        )
        
        # Get updated transaction total
        transaction = db.query(POSTransaction).filter(
            POSTransaction.id == coupon_data.transaction_id
        ).first()
        
        return POSApplyCouponResponse(
            success=result['success'],
            discount_amount=result['discount_amount'],
            coupon_name=result['coupon_name'],
            message=result['message'],
            final_amount=transaction.total_amount if transaction else 0
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply coupon: {str(e)}"
        )

@router.post("/remove-discount", response_model=POSRemoveDiscountResponse)
async def remove_discount_from_pos_transaction(
    discount_data: POSRemoveDiscountRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Remove discount from POS transaction"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get discount record
        discount = db.query(POSTransactionDiscount).filter(
            POSTransactionDiscount.id == discount_data.discount_id,
            POSTransactionDiscount.transaction_id == discount_data.transaction_id
        ).first()
        
        if not discount:
            raise ValueError("Discount not found")
        
        # Remove discount
        db.delete(discount)
        db.commit()
        
        # Recalculate transaction total
        transaction = db.query(POSTransaction).filter(
            POSTransaction.id == discount_data.transaction_id
        ).first()
        
        if transaction:
            # Recalculate total without this discount
            transaction.total_amount = transaction.subtotal - sum(
                d.applied_amount for d in transaction.discounts if d.id != discount_data.discount_id
            )
            db.commit()
        
        return POSRemoveDiscountResponse(
            success=True,
            message="Discount removed successfully",
            final_amount=transaction.total_amount if transaction else 0
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove discount: {str(e)}"
        )

@router.post("/redeem-loyalty-points", response_model=POSLoyaltyPointsResponse)
async def redeem_loyalty_points(
    loyalty_data: POSLoyaltyPointsRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Redeem loyalty points for discount"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get customer loyalty information
        from ...services.loyalty.loyalty_service import loyalty_service
        
        result = loyalty_service.redeem_points(
            db=db,
            customer_id=loyalty_data.customer_id,
            points_to_redeem=loyalty_data.points_to_redeem,
            transaction_id=loyalty_data.transaction_id,
            user_id=current_user.id
        )
        
        return POSLoyaltyPointsResponse(
            success=result['success'],
            points_redeemed=result['points_redeemed'],
            discount_amount=result['discount_amount'],
            points_balance=result['points_balance'],
            final_amount=result['final_amount']
        )
        
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

@router.get("/available-discounts")
async def get_available_discounts(
    customer_id: Optional[int] = Query(None),
    store_id: Optional[int] = Query(None),
    order_amount: Decimal = Query(0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Get all available discounts for POS"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get available discounts
        transaction_data = {
            'subtotal': order_amount,
            'items': [],
            'customer_id': customer_id,
            'store_id': store_id
        }
        
        result = pos_discount_service.calculate_transaction_discounts(
            db=db,
            transaction_data=transaction_data,
            customer_id=customer_id,
            store_id=store_id
        )
        
        return {
            "available_discounts": result['discounts'],
            "available_coupons": result.get('available_coupons', []),
            "customer_benefits": result.get('customer_benefits', {}),
            "loyalty_points": result.get('loyalty_points', 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available discounts: {str(e)}"
        )

@router.get("/discount-analytics", response_model=POSDiscountAnalyticsResponse)
async def get_discount_analytics(
    from_date: date = Query(...),
    to_date: date = Query(...),
    store_id: Optional[int] = Query(None),
    discount_type: Optional[str] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.analytics")),
    db: Session = Depends(get_db)
):
    """Get POS discount analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get analytics data
        from ...services.pos.pos_analytics_service import pos_analytics_service
        
        analytics = pos_analytics_service.get_discount_analytics(
            db=db,
            company_id=company_id,
            from_date=from_date,
            to_date=to_date,
            store_id=store_id,
            discount_type=discount_type
        )
        
        return POSDiscountAnalyticsResponse(
            total_transactions=analytics['total_transactions'],
            total_discount_amount=analytics['total_discount_amount'],
            average_discount_per_transaction=analytics['average_discount_per_transaction'],
            discount_breakdown=analytics['discount_breakdown'],
            top_discounts=analytics['top_discounts'],
            customer_analytics=analytics['customer_analytics']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get discount analytics: {str(e)}"
        )

@router.get("/customer-benefits/{customer_id}")
async def get_customer_benefits(
    customer_id: int,
    order_amount: Decimal = Query(0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Get customer-specific benefits and discounts"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get customer benefits
        benefits = pos_discount_service.get_customer_benefits(
            db=db,
            customer_id=customer_id,
            order_amount=order_amount
        )
        
        return benefits
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer benefits: {str(e)}"
        )

@router.get("/coupons/validate/{coupon_code}")
async def validate_coupon(
    coupon_code: str,
    customer_id: Optional[int] = Query(None),
    order_amount: Decimal = Query(0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Validate coupon code"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get coupon
        from ...models.core.discount_management import DiscountCoupon
        coupon = db.query(DiscountCoupon).filter(
            DiscountCoupon.coupon_code == coupon_code,
            DiscountCoupon.is_active == True
        ).first()
        
        if not coupon:
            return {
                "valid": False,
                "message": "Invalid coupon code"
            }
        
        # Validate coupon
        is_valid = pos_discount_service.validate_coupon(coupon, customer_id)
        
        if not is_valid:
            return {
                "valid": False,
                "message": "Coupon is not valid for this transaction"
            }
        
        # Calculate discount amount
        discount_amount = pos_discount_service.calculate_coupon_discount(coupon, order_amount)
        
        return {
            "valid": True,
            "coupon_name": coupon.coupon_name,
            "discount_amount": discount_amount,
            "discount_percentage": coupon.discount_percentage,
            "max_discount_amount": coupon.max_discount_amount,
            "min_order_amount": coupon.min_order_amount
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate coupon: {str(e)}"
        )

@router.get("/loyalty-points/{customer_id}")
async def get_customer_loyalty_points(
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.discount")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty points and benefits"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Get customer loyalty information
        from ...services.loyalty.loyalty_service import loyalty_service
        
        loyalty_info = loyalty_service.get_customer_loyalty_info(
            db=db,
            customer_id=customer_id
        )
        
        return loyalty_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get loyalty points: {str(e)}"
        )