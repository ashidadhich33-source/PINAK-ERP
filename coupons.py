from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import random
import string

from ...database import get_db
from ...models import Coupon, Customer, Staff
from ...services.whatsapp_service import WhatsAppService
from ...core.security import get_current_user
from ...core.constants import CouponType
from ...schemas.coupon_schema import (
    CouponCreate, CouponUpdate, CouponResponse, CouponBulkCreate
)

router = APIRouter()

def generate_coupon_code(length: int = 8) -> str:
    """Generate random coupon code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new coupon"""
    # Generate code if not provided
    code = coupon_data.code or generate_coupon_code()
    
    # Check if code already exists
    existing = db.query(Coupon).filter(Coupon.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
    
    # Validate customer if mobile provided
    if coupon_data.bound_mobile:
        customer = db.query(Customer).filter(
            Customer.mobile == coupon_data.bound_mobile
        ).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get staff if provided
    staff_id = coupon_data.sent_by_staff_id or current_user.id
    
    coupon = Coupon(
        id=str(uuid.uuid4()),
        code=code,
        type=coupon_data.type,
        value=coupon_data.value,
        max_cap=coupon_data.max_cap if coupon_data.type == CouponType.PERCENT else None,
        valid_from=coupon_data.valid_from or date.today(),
        valid_to=coupon_data.valid_to,
        min_bill=coupon_data.min_bill,
        bound_mobile=coupon_data.bound_mobile,
        active=True,
        sent_by_staff_id=staff_id,
        created_at=datetime.utcnow()
    )
    
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    return coupon

@router.get("/", response_model=List[CouponResponse])
async def get_coupons(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    expired: Optional[bool] = None,
    customer_mobile: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all coupons with filters"""
    query = db.query(Coupon)
    
    if active is not None:
        query = query.filter(Coupon.active == active)
    
    if expired is not None:
        if expired:
            query = query.filter(Coupon.valid_to < date.today())
        else:
            query = query.filter(
                or_(
                    Coupon.valid_to >= date.today(),
                    Coupon.valid_to.is_(None)
                )
            )
    
    if customer_mobile:
        query = query.filter(Coupon.bound_mobile == customer_mobile)
    
    coupons = query.offset(skip).limit(limit).all()
    return coupons

@router.get("/{coupon_code}", response_model=CouponResponse)
async def get_coupon(
    coupon_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get coupon by code"""
    coupon = db.query(Coupon).filter(Coupon.code == coupon_code).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    return coupon

@router.put("/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: str,
    coupon_update: CouponUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update coupon"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    # Update fields
    for field, value in coupon_update.dict(exclude_unset=True).items():
        setattr(coupon, field, value)
    
    db.commit()
    db.refresh(coupon)
    
    return coupon

@router.post("/{coupon_id}/deactivate")
async def deactivate_coupon(
    coupon_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deactivate a coupon"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.active = False
    db.commit()
    
    return {"success": True, "message": "Coupon deactivated successfully"}

@router.post("/bulk-create")
async def bulk_create_coupons(
    bulk_data: CouponBulkCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create multiple coupons at once"""
    created_coupons = []
    
    for i in range(bulk_data.quantity):
        code = generate_coupon_code()
        
        # Ensure unique code
        while db.query(Coupon).filter(Coupon.code == code).first():
            code = generate_coupon_code()
        
        coupon = Coupon(
            id=str(uuid.uuid4()),
            code=code,
            type=bulk_data.type,
            value=bulk_data.value,
            max_cap=bulk_data.max_cap if bulk_data.type == CouponType.PERCENT else None,
            valid_from=bulk_data.valid_from or date.today(),
            valid_to=bulk_data.valid_to,
            min_bill=bulk_data.min_bill,
            active=True,
            sent_by_staff_id=current_user.id,
            created_at=datetime.utcnow()
        )
        
        db.add(coupon)
        created_coupons.append(code)
    
    db.commit()
    
    return {
        "success": True,
        "created": len(created_coupons),
        "coupon_codes": created_coupons
    }

@router.post("/{coupon_id}/send-whatsapp")
async def send_coupon_whatsapp(
    coupon_id: str,
    mobile: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send coupon to customer via WhatsApp"""
    if len(mobile) != 10:
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()