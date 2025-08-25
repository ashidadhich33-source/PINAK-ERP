from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

from ...database import get_db
from ...models import (
    Sale, SaleItem, SaleReturn, SaleReturnItem, ReturnCredit,
    Customer, Item, Stock, BillSeries
)
from ...services.gst_service import GSTService
from ...services.stock_service import StockService
from ...services.whatsapp_service import WhatsAppService
from ...core.security import get_current_user
from ...core.constants import TaxRegion, ReturnCreditStatus
from ...schemas.sale_return_schema import (
    SaleReturnCreate, SaleReturnResponse, SaleReturnItemCreate,
    SaleLineSearchResponse, ReturnCreditResponse
)

router = APIRouter()

def get_next_return_number(db: Session) -> str:
    """Generate next sale return number"""
    series = db.query(BillSeries).filter(
        BillSeries.code == "SR",
        BillSeries.active == True
    ).first()
    
    if not series:
        raise HTTPException(status_code=404, detail="Sale Return series not found")
    
    sr_no = f"{series.prefix}-{str(series.next_no).zfill(series.width)}"
    series.next_no += 1
    
    return sr_no

@router.post("/return/search-sale-line")
async def search_sale_line_for_return(
    barcode: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search sale lines containing a barcode for return"""
    
    # Default date range (last 30 days if not specified)
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=30)
    
    # Find all sale items with this barcode within return window
    query = db.query(SaleItem).join(Sale).filter(
        SaleItem.barcode == barcode,
        Sale.bill_date >= from_date,
        Sale.bill_date <= datetime.combine(to_date, datetime.max.time())
    )
    
    sale_items = query.all()
    
    if not sale_items:
        raise HTTPException(
            status_code=404, 
            detail=f"No sales found for barcode {barcode} in the specified period"
        )
    
    result = []
    for sale_item in sale_items:
        sale = sale_item.sale
        
        # Calculate already returned quantity for this sale line
        already_returned = db.query(
            db.func.sum(SaleReturnItem.return_qty)
        ).filter(
            SaleReturnItem.sale_item_id == sale_item.id
        ).scalar() or 0
        
        returnable_qty = sale_item.qty - already_returned
        
        if returnable_qty <= 0:
            continue  # Skip if fully returned
        
        # Get customer info
        customer_name = ""
        if sale.customer_mobile:
            customer = db.query(Customer).filter(
                Customer.mobile == sale.customer_mobile
            ).first()
            if customer:
                customer_name = customer.name
        
        result.append({
            "sale_id": sale.id,
            "sale_item_id": sale_item.id,
            "bill_no": sale.bill_no,
            "bill_date": sale.bill_date.strftime("%d-%m-%Y"),
            "customer_mobile": sale.customer_mobile or "",
            "customer_name": customer_name,
            "style_code": sale_item.style_code,
            "color": sale_item.color,
            "size": sale_item.size,
            "unit_mrp_incl": float(sale_item.mrp_incl),
            "disc_pct": float(sale_item.disc_pct),
            "line_amount_incl": float(sale_item.line_inclusive),
            "gst_rate": float(sale_item.gst_rate),
            "hsn": sale_item.hsn,
            "sold_qty": sale_item.qty,
            "already_returned_qty": already_returned,
            "returnable_qty": returnable_qty
        })
    
    return result

@router.post("/return/create")
async def create_sale_return(
    return_data: SaleReturnCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create sale return with return credit generation"""
    
    # Generate return number
    sr_no = get_next_return_number(db)
    
    # Get tax region from company settings
    tax_region = return_data.tax_region or TaxRegion.LOCAL
    
    # Create sale return record
    sale_return = SaleReturn(
        id=str(uuid.uuid4()),
        sr_series_id=return_data.sr_series_id,
        sr_no=sr_no,
        sr_date=datetime.utcnow(),
        customer_mobile=return_data.customer_mobile,
        tax_region=tax_region,
        reason=return_data.reason,
        created_by=current_user.id
    )
    
    total_return_amount = Decimal('0')
    customer_mobile_for_rc = None
    
    for item_data in return_data.items:
        # Validate original sale item
        sale_item = db.query(SaleItem).filter(
            SaleItem.id == item_data.sale_item_id
        ).first()
        
        if not sale_item:
            raise HTTPException(
                status_code=404, 
                detail=f"Original sale item not found"
            )
        
        sale = sale_item.sale
        
        # Check returnable quantity
        already_returned = db.query(
            db.func.sum(SaleReturnItem.return_qty)
        ).filter(
            SaleReturnItem.sale_item_id == sale_item.id
        ).scalar() or 0
        
        returnable_qty = sale_item.qty - already_returned
        
        if item_data.return_qty > returnable_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Return quantity exceeds returnable quantity. Max returnable: {returnable_qty}"
            )
        
        # Calculate return amount (based on original sale line amount, no coupon/points)
        unit_return_amount = sale_item.line_inclusive / sale_item.qty
        line_return_amount = unit_return_amount * item_data.return_qty
        
        # Extract GST info for return (informational)
        base_return = line_return_amount / (1 + sale_item.gst_rate / 100)
        tax_return = line_return_amount - base_return
        
        # Create return item
        return_item = SaleReturnItem(
            id=str(uuid.uuid4()),
            sales_return_id=sale_return.id,
            sale_id=sale.id,
            sale_item_id=sale_item.id,
            barcode=sale_item.barcode,
            style_code=sale_item.style_code,
            color=sale_item.color,
            size=sale_item.size,
            hsn=sale_item.hsn,
            gst_rate=sale_item.gst_rate,
            unit_mrp_incl=sale_item.mrp_incl,
            disc_pct_at_sale=sale_item.disc_pct,
            return_qty=item_data.return_qty,
            line_inclusive=line_return_amount,
            base_excl_info=base_return,
            tax_info=tax_return
        )
        
        sale_return.items.append(return_item)
        total_return_amount += line_return_amount
        
        # Restore stock
        StockService.update_stock(db, sale_item.barcode, item_data.return_qty, 'add')
        
        # Get customer mobile from original sale
        if sale.customer_mobile and not customer_mobile_for_rc:
            customer_mobile_for_rc = sale.customer_mobile
    
    # Set total on return
    sale_return.total_incl = total_return_amount
    
    # Create Return Credit
    rc_no = f"RC-{sr_no}"  # Return Credit number based on return number
    
    return_credit = ReturnCredit(
        id=str(uuid.uuid4()),
        rc_no=rc_no,
        customer_mobile=customer_mobile_for_rc or return_data.customer_mobile,
        sales_return_id=sale_return.id,
        rc_amount_incl=total_return_amount,
        status=ReturnCreditStatus.OPEN,
        created_at=datetime.utcnow()
    )
    
    sale_return.return_credit = return_credit
    
    # Save everything
    db.add(sale_return)
    db.add(return_credit)
    db.commit()
    db.refresh(sale_return)
    
    # Send WhatsApp notification if customer mobile exists
    if customer_mobile_for_rc:
        try:
            WhatsAppService.send_return_credit_notification(
                mobile=customer_mobile_for_rc,
                rc_no=rc_no,
                amount=total_return_amount
            )
        except:
            pass  # Don't fail return if WhatsApp fails
    
    return {
        "success": True,
        "sr_no": sr_no,
        "sr_date": sale_return.sr_date,
        "total_return_amount": float(total_return_amount),
        "rc_no": rc_no,
        "rc_amount": float(total_return_amount),
        "customer_mobile": customer_mobile_for_rc,
        "message": f"Sale return created. Return Credit {rc_no} of ₹{total_return_amount:.2f} issued."
    }

@router.get("/return/{sr_no}")
async def get_sale_return(
    sr_no: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get sale return details"""
    sale_return = db.query(SaleReturn).filter(
        SaleReturn.sr_no == sr_no
    ).first()
    
    if not sale_return:
        raise HTTPException(status_code=404, detail="Sale return not found")
    
    # Get return credit details
    return_credit = db.query(ReturnCredit).filter(
        ReturnCredit.sales_return_id == sale_return.id
    ).first()
    
    # Build response
    items = []
    for item in sale_return.items:
        items.append({
            "barcode": item.barcode,
            "style_code": item.style_code,
            "color": item.color,
            "size": item.size,
            "return_qty": item.return_qty,
            "unit_mrp": float(item.unit_mrp_incl),
            "disc_pct": float(item.disc_pct_at_sale),
            "line_amount": float(item.line_inclusive),
            "original_bill_no": item.original_sale.bill_no if item.original_sale else None
        })
    
    return {
        "sr_no": sale_return.sr_no,
        "sr_date": sale_return.sr_date,
        "customer_mobile": sale_return.customer_mobile,
        "total_amount": float(sale_return.total_incl),
        "reason": sale_return.reason,
        "items": items,
        "return_credit": {
            "rc_no": return_credit.rc_no if return_credit else None,
            "amount": float(return_credit.rc_amount_incl) if return_credit else 0,
            "status": return_credit.status if return_credit else None
        }
    }

@router.get("/returns")
async def get_sale_returns(
    skip: int = 0,
    limit: int = 100,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    customer_mobile: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get list of sale returns with filters"""
    query = db.query(SaleReturn)
    
    if from_date:
        query = query.filter(SaleReturn.sr_date >= from_date)
    if to_date:
        query = query.filter(
            SaleReturn.sr_date <= datetime.combine(to_date, datetime.max.time())
        )
    if customer_mobile:
        query = query.filter(SaleReturn.customer_mobile == customer_mobile)
    
    returns = query.offset(skip).limit(limit).all()
    
    result = []
    for ret in returns:
        # Get return credit
        rc = db.query(ReturnCredit).filter(
            ReturnCredit.sales_return_id == ret.id
        ).first()
        
        result.append({
            "sr_no": ret.sr_no,
            "sr_date": ret.sr_date.strftime("%d-%m-%Y"),
            "customer_mobile": ret.customer_mobile or "",
            "total_amount": float(ret.total_incl),
            "reason": ret.reason,
            "rc_no": rc.rc_no if rc else "",
            "rc_status": rc.status if rc else ""
        })
    
    return result