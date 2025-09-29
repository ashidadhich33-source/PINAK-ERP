# backend/app/api/endpoints/pos/pos_crm_integration.py
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
from ...services.pos.pos_crm_service import POSCRMService

router = APIRouter()

# Initialize service
pos_crm_service = POSCRMService()

# Pydantic schemas for POS CRM Integration
class POSCustomerSearchRequest(BaseModel):
    search_term: str
    search_type: str = "all"  # all, name, phone, email, customer_id
    limit: int = 10

class POSCustomerSearchResponse(BaseModel):
    customers: List[dict]
    total_count: int
    search_term: str

class POSCustomerCreateRequest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    customer_type: str = "regular"  # regular, vip, premium
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    notes: Optional[str] = None

class POSCustomerCreateResponse(BaseModel):
    customer_id: int
    customer_code: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    customer_type: str
    loyalty_points: int = 0
    message: str

class POSCustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    customer_type: Optional[str] = None
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    notes: Optional[str] = None

class POSCustomerInfoResponse(BaseModel):
    customer_id: int
    customer_code: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    customer_type: str
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    loyalty_points: int
    total_purchases: Decimal
    last_purchase_date: Optional[datetime] = None
    customer_tier: Optional[str] = None
    available_discounts: List[dict]
    loyalty_benefits: dict
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class POSCustomerTransactionHistoryRequest(BaseModel):
    customer_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    limit: int = 50
    offset: int = 0

class POSCustomerTransactionHistoryResponse(BaseModel):
    transactions: List[dict]
    total_count: int
    total_amount: Decimal
    average_transaction: Decimal
    customer_summary: dict

class POSCustomerLoyaltyRequest(BaseModel):
    customer_id: int
    points_to_redeem: Optional[int] = None
    points_to_earn: Optional[int] = None

class POSCustomerLoyaltyResponse(BaseModel):
    customer_id: int
    current_points: int
    points_earned: int
    points_redeemed: int
    loyalty_tier: str
    tier_benefits: dict
    next_tier_points: int
    next_tier_name: str

class POSCustomerAnalyticsRequest(BaseModel):
    customer_id: int
    from_date: Optional[date] = None
    to_date: Optional[date] = None

class POSCustomerAnalyticsResponse(BaseModel):
    customer_id: int
    total_transactions: int
    total_spent: Decimal
    average_transaction: Decimal
    favorite_categories: List[dict]
    purchase_frequency: dict
    loyalty_metrics: dict
    recommendations: List[dict]

# POS Customer Search Endpoints
@router.post("/customers/search", response_model=POSCustomerSearchResponse)
async def search_pos_customers(
    search_data: POSCustomerSearchRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Search customers for POS"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_crm_service.search_customers(
            db=db,
            company_id=company_id,
            search_term=search_data.search_term,
            search_type=search_data.search_type,
            limit=search_data.limit
        )
        
        return POSCustomerSearchResponse(
            customers=result['customers'],
            total_count=result['total_count'],
            search_term=search_data.search_term
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search customers: {str(e)}"
        )

@router.post("/customers", response_model=POSCustomerCreateResponse)
async def create_pos_customer(
    customer_data: POSCustomerCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Create new customer from POS"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_crm_service.create_customer(
            db=db,
            company_id=company_id,
            name=customer_data.name,
            phone=customer_data.phone,
            email=customer_data.email,
            address=customer_data.address,
            city=customer_data.city,
            state=customer_data.state,
            pincode=customer_data.pincode,
            customer_type=customer_data.customer_type,
            date_of_birth=customer_data.date_of_birth,
            anniversary_date=customer_data.anniversary_date,
            notes=customer_data.notes,
            user_id=current_user.id
        )
        
        return POSCustomerCreateResponse(
            customer_id=result['customer_id'],
            customer_code=result['customer_code'],
            name=result['name'],
            phone=result['phone'],
            email=result['email'],
            customer_type=result['customer_type'],
            loyalty_points=result['loyalty_points'],
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

@router.get("/customers/{customer_id}", response_model=POSCustomerInfoResponse)
async def get_pos_customer_info(
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get customer information for POS"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        customer_info = pos_crm_service.get_customer_info(
            db=db,
            company_id=company_id,
            customer_id=customer_id
        )
        
        return POSCustomerInfoResponse(**customer_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer info: {str(e)}"
        )

@router.put("/customers/{customer_id}", response_model=POSCustomerInfoResponse)
async def update_pos_customer(
    customer_id: int,
    customer_data: POSCustomerUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Update customer information from POS"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_crm_service.update_customer(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            name=customer_data.name,
            phone=customer_data.phone,
            email=customer_data.email,
            address=customer_data.address,
            city=customer_data.city,
            state=customer_data.state,
            pincode=customer_data.pincode,
            customer_type=customer_data.customer_type,
            date_of_birth=customer_data.date_of_birth,
            anniversary_date=customer_data.anniversary_date,
            notes=customer_data.notes,
            user_id=current_user.id
        )
        
        return POSCustomerInfoResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update customer: {str(e)}"
        )

@router.get("/customers/{customer_id}/transactions", response_model=POSCustomerTransactionHistoryResponse)
async def get_customer_transaction_history(
    customer_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get customer transaction history"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_crm_service.get_customer_transaction_history(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset
        )
        
        return POSCustomerTransactionHistoryResponse(
            transactions=result['transactions'],
            total_count=result['total_count'],
            total_amount=result['total_amount'],
            average_transaction=result['average_transaction'],
            customer_summary=result['customer_summary']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction history: {str(e)}"
        )

@router.get("/customers/{customer_id}/loyalty", response_model=POSCustomerLoyaltyResponse)
async def get_customer_loyalty_info(
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get customer loyalty information"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        loyalty_info = pos_crm_service.get_customer_loyalty_info(
            db=db,
            company_id=company_id,
            customer_id=customer_id
        )
        
        return POSCustomerLoyaltyResponse(**loyalty_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get loyalty info: {str(e)}"
        )

@router.get("/customers/{customer_id}/analytics", response_model=POSCustomerAnalyticsResponse)
async def get_customer_analytics(
    customer_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.analytics")),
    db: Session = Depends(get_db)
):
    """Get customer analytics and insights"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        analytics = pos_crm_service.get_customer_analytics(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return POSCustomerAnalyticsResponse(**analytics)
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer analytics: {str(e)}"
        )

@router.get("/customers/{customer_id}/benefits")
async def get_customer_benefits(
    customer_id: int,
    order_amount: Decimal = Query(0),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
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
        benefits = pos_crm_service.get_customer_benefits(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            order_amount=order_amount
        )
        
        return benefits
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer benefits: {str(e)}"
        )

@router.get("/customers/{customer_id}/recommendations")
async def get_customer_recommendations(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get product recommendations for customer"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        recommendations = pos_crm_service.get_customer_recommendations(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            limit=limit
        )
        
        return recommendations
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get recommendations: {str(e)}"
        )

@router.get("/customers/{customer_id}/quick-actions")
async def get_customer_quick_actions(
    customer_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get quick actions available for customer"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        quick_actions = pos_crm_service.get_customer_quick_actions(
            db=db,
            company_id=company_id,
            customer_id=customer_id
        )
        
        return quick_actions
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quick actions: {str(e)}"
        )

@router.post("/customers/{customer_id}/add-to-favorites")
async def add_item_to_customer_favorites(
    customer_id: int,
    item_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Add item to customer favorites"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        result = pos_crm_service.add_to_customer_favorites(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            item_id=item_id,
            user_id=current_user.id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add to favorites: {str(e)}"
        )

@router.get("/customers/{customer_id}/favorites")
async def get_customer_favorites(
    customer_id: int,
    limit: int = Query(20, ge=1, le=100),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("pos.customer")),
    db: Session = Depends(get_db)
):
    """Get customer favorite items"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        favorites = pos_crm_service.get_customer_favorites(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            limit=limit
        )
        
        return favorites
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get favorites: {str(e)}"
        )