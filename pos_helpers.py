"""Helper endpoints for POS operations"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from ...database import get_db
from ...models import Sale, Staff, PaymentMode, Coupon
from ...core.security import get_current_user

router = APIRouter()

@router.get("/staff/active")
async def get_active_staff(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of active staff for POS"""
    staff_list = db.query(Staff).filter(Staff.active == True).all()
    
    result = []
    for staff in staff_list:
        result.append({
            "id": staff.id,
            "code": staff.code,
            "name": staff.name
        })
    
    return result

@router.get("/payment-modes/active")
async def get_active_payment_modes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of active payment modes"""
    modes = db.query(PaymentMode).filter(PaymentMode.active == True).all()
    
    result = []
    for mode in modes:
        result.append({
            "id": mode.id,
            "name": mode.name,
            "settlement_type": mode.settlement_type
        })
    
    return result

@router.post("/bill/modify")
async def modify_bill(
    bill_no: str,
    admin_override: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Load bill for modification"""
    sale = db.query(Sale).filter(Sale.bill_no == bill_no).first()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Check if bill can be modified
    today = date.today()
    bill_date = sale.bill_date.date()
    
    if bill_date != today and not admin_override:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admin can modify bills from previous days"
            )
    
    # Build response with full bill details
    items = []
    for item in sale.items:
        items.append({
            "barcode": item.barcode,
            "style_code": item.style_code,
            "color": item.color,
            "size": item.size,
            "qty": item.qty,
            "mrp": float(item.mrp_incl),
            "disc_pct": float(item.disc_pct),
            "line_amount": float(item.line_inclusive)
        })
    
    payments = []
    for payment in sale.payments:
        payments.append({
            "payment_mode_id": payment.payment_mode_id,
            "payment_mode_name": payment.payment_mode.name if payment.payment_mode else "",
            "amount": float(payment.amount)
        })
    
    return {
        "bill_no": sale.bill_no,
        "bill_date": sale.bill_date,
        "customer_mobile": sale.customer_mobile,
        "staff_id": sale.staff_id,
        "items": items,
        "payments": payments,
        "gross_amount": float(sale.gross_incl),
        "discount_amount": float(sale.discount_incl),
        "coupon_discount": float(sale.coupon_incl) if sale.coupon_incl else 0,
        "redeem_points": sale.redeem_points,
        "redeem_value": float(sale.redeem_value),
        "return_credit_used": float(sale.return_credit_used_value),
        "final_payable": float(sale.final_payable),
        "editable": True
    }

@router.get("/bill/previous/{bill_no}")
async def get_previous_bill(
    bill_no: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Navigate to previous bill"""
    # Extract number from bill_no (e.g., S-00001 -> 1)
    parts = bill_no.split('-')
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid bill number format")
    
    prefix = parts[0]
    number = int(parts[1])
    
    if number <= 1:
        raise HTTPException(status_code=404, detail="No previous bill")
    
    prev_number = number - 1
    prev_bill_no = f"{prefix}-{str(prev_number).zfill(5)}"
    
    sale = db.query(Sale).filter(Sale.bill_no == prev_bill_no).first()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Previous bill not found")
    
    return {"bill_no": prev_bill_no}

@router.get("/bill/next/{bill_no}")
async def get_next_bill(
    bill_no: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Navigate to next bill"""
    # Extract number from bill_no
    parts = bill_no.split('-')
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid bill number format")
    
    prefix = parts[0]
    number = int(parts[1])
    
    next_number = number + 1
    next_bill_no = f"{prefix}-{str(next_number).zfill(5)}"
    
    sale = db.query(Sale).filter(Sale.bill_no == next_bill_no).first()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Next bill not found")
    
    return {"bill_no": next_bill_no}

@router.get("/bill/history/{customer_mobile}")
async def get_customer_bill_history(
    customer_mobile: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get customer's purchase history"""
    if len(customer_mobile) != 10:
        raise HTTPException(status_code=400, detail="Invalid mobile number")
    
    sales = db.query(Sale).filter(
        Sale.customer_mobile == customer_mobile
    ).order_by(Sale.bill_date.desc()).limit(limit).all()
    
    result = []
    for sale in sales:
        result.append({
            "bill_no": sale.bill_no,
            "bill_date": sale.bill_date.strftime("%d-%m-%Y"),
            "amount": float(sale.final_payable),
            "items_count": len(sale.items)
        })
    
    return result