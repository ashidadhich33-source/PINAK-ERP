from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid
import random
import string

from ...database import get_db
from ...models import (
    LoyaltyGrade, Customer, PointTransaction, Sale, Coupon, Staff
)
from ...services.whatsapp_service import WhatsAppService
from ...core.security import get_current_user
from ...core.constants import CouponType
from ...schemas.loyalty_schema import (
    LoyaltyGradeCreate, LoyaltyGradeUpdate, LoyaltyGradeResponse,
    PointTransactionResponse, CustomerGradeUpgradeResponse
)

router = APIRouter()

@router.post("/grades", response_model=LoyaltyGradeResponse)
async def create_loyalty_grade(
    grade_data: LoyaltyGradeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new loyalty grade"""
    # Check for overlapping ranges
    existing = db.query(LoyaltyGrade).filter(
        or_(
            and_(
                LoyaltyGrade.amount_from <= grade_data.amount_from,
                LoyaltyGrade.amount_to >= grade_data.amount_from
            ),
            and_(
                LoyaltyGrade.amount_from <= grade_data.amount_to,
                LoyaltyGrade.amount_to >= grade_data.amount_to
            )
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Grade range overlaps with existing grade: {existing.name}"
        )
    
    grade = LoyaltyGrade(
        id=str(uuid.uuid4()),
        name=grade_data.name,
        amount_from=grade_data.amount_from,
        amount_to=grade_data.amount_to,
        earn_pct=grade_data.earn_pct,
        created_at=datetime.utcnow()
    )
    
    db.add(grade)
    db.commit()
    db.refresh(grade)
    
    return grade

@router.get("/grades", response_model=List[LoyaltyGradeResponse])
async def get_loyalty_grades(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all loyalty grades"""
    grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from).all()
    return grades

@router.put("/grades/{grade_id}", response_model=LoyaltyGradeResponse)
async def update_loyalty_grade(
    grade_id: str,
    grade_update: LoyaltyGradeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update loyalty grade"""
    grade = db.query(LoyaltyGrade).filter(LoyaltyGrade.id == grade_id).first()
    
    if not grade:
        raise HTTPException(status_code=404, detail="Loyalty grade not found")
    
    # Check for overlapping ranges if amounts are being updated
    if grade_update.amount_from or grade_update.amount_to:
        amount_from = grade_update.amount_from or grade.amount_from
        amount_to = grade_update.amount_to or grade.amount_to
        
        existing = db.query(LoyaltyGrade).filter(
            LoyaltyGrade.id != grade_id,
            or_(
                and_(
                    LoyaltyGrade.amount_from <= amount_from,
                    LoyaltyGrade.amount_to >= amount_from
                ),
                and_(
                    LoyaltyGrade.amount_from <= amount_to,
                    LoyaltyGrade.amount_to >= amount_to
                )
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Grade range overlaps with existing grade: {existing.name}"
            )
    
    # Update fields
    for field, value in grade_update.dict(exclude_unset=True).items():
        setattr(grade, field, value)
    
    grade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(grade)
    
    # Update customer grades if ranges changed
    if grade_update.amount_from or grade_update.amount_to:
        update_customer_grades(db)
    
    return grade

@router.delete("/grades/{grade_id}")
async def delete_loyalty_grade(
    grade_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete loyalty grade"""
    grade = db.query(LoyaltyGrade).filter(LoyaltyGrade.id == grade_id).first()
    
    if not grade:
        raise HTTPException(status_code=404, detail="Loyalty grade not found")
    
    # Check if any customers have this grade
    customers_with_grade = db.query(Customer).filter(
        Customer.grade == grade.name
    ).count()
    
    if customers_with_grade > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete grade. {customers_with_grade} customers have this grade"
        )
    
    db.delete(grade)
    db.commit()
    
    return {"success": True, "message": "Loyalty grade deleted successfully"}

@router.get("/points/transactions/{mobile}")
async def get_point_transactions(
    mobile: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get point transactions for a customer"""
    if len(mobile) != 10:
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    
    transactions = db.query(PointTransaction).filter(
        PointTransaction.customer_mobile == mobile
    ).order_by(PointTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for txn in transactions:
        result.append({
            "id": txn.id,
            "date": txn.created_at,
            "type": txn.transaction_type,
            "points": txn.points,
            "reference_type": txn.reference_type,
            "reference_id": txn.reference_id,
            "description": get_transaction_description(db, txn)
        })
    
    # Get current balance
    customer = db.query(Customer).filter(Customer.mobile == mobile).first()
    
    return {
        "transactions": result,
        "current_balance": customer.points_balance if customer else 0
    }

@router.post("/points/manual-adjustment")
async def manual_point_adjustment(
    mobile: str,
    points: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Manually adjust customer points (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can adjust points manually")
    
    customer = db.query(Customer).filter(Customer.mobile == mobile).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if adjustment would make balance negative
    if customer.points_balance + points < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Adjustment would make balance negative. Current: {customer.points_balance}"
        )
    
    # Update balance
    customer.points_balance += points
    
    # Create transaction record
    transaction = PointTransaction(
        id=str(uuid.uuid4()),
        customer_mobile=mobile,
        transaction_type='adjustment',
        points=points,
        reference_type='manual',
        reference_id=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "success": True,
        "new_balance": customer.points_balance,
        "adjustment": points,
        "reason": reason
    }

@router.post("/grades/bulk-upgrade")
async def bulk_grade_upgrade(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Recalculate and upgrade all customer grades based on lifetime purchase"""
    upgraded_count = update_customer_grades(db)
    
    return {
        "success": True,
        "customers_upgraded": upgraded_count,
        "message": f"Successfully upgraded {upgraded_count} customers"
    }

def update_customer_grades(db: Session) -> int:
    """Helper function to update customer grades based on lifetime purchase"""
    grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from).all()
    customers = db.query(Customer).all()
    
    upgraded_count = 0
    
    for customer in customers:
        old_grade = customer.grade
        new_grade = None
        
        for grade in grades:
            if customer.lifetime_purchase >= grade.amount_from and customer.lifetime_purchase <= grade.amount_to:
                new_grade = grade.name
                break
        
        if new_grade and new_grade != old_grade:
            customer.grade = new_grade
            upgraded_count += 1
    
    db.commit()
    return upgraded_count

def get_transaction_description(db: Session, transaction: PointTransaction) -> str:
    """Generate description for point transaction"""
    if transaction.reference_type == 'sale':
        sale = db.query(Sale).filter(Sale.id == transaction.reference_id).first()
        if sale:
            return f"Purchase - Bill {sale.bill_no}"
    elif transaction.reference_type == 'sale_return':
        # Return transactions typically don't affect points
        return "Sale Return Adjustment"
    elif transaction.reference_type == 'manual':
        return "Manual Adjustment by Admin"
    elif transaction.reference_type == 'promotion':
        return "Promotional Points"
    
    return transaction.reference_type.title()