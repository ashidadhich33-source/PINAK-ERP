# backend/app/api/endpoints/enhanced_sales.py
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
from ...services.enhanced_sales_service import enhanced_sales_service

router = APIRouter()

# Pydantic schemas for Sale Challan
class SaleChallanCreateRequest(BaseModel):
    customer_id: int
    challan_date: date
    challan_type: str = 'delivery'
    staff_id: Optional[int] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None

class SaleChallanItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    notes: Optional[str] = None

class SaleChallanResponse(BaseModel):
    id: int
    company_id: int
    challan_number: str
    challan_date: date
    customer_id: int
    staff_id: Optional[int] = None
    challan_type: str
    delivery_address: Optional[str] = None
    delivery_date: Optional[date] = None
    delivery_time: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    total_quantity: Decimal
    total_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Bill Series
class BillSeriesCreateRequest(BaseModel):
    series_name: str
    series_code: str
    document_type: str
    prefix: str
    suffix: Optional[str] = None
    starting_number: int = 1
    number_length: int = 6
    is_default: bool = False
    notes: Optional[str] = None

class BillSeriesResponse(BaseModel):
    id: int
    company_id: int
    series_name: str
    series_code: str
    document_type: str
    prefix: str
    suffix: Optional[str] = None
    starting_number: int
    current_number: int
    number_length: int
    is_active: bool
    is_default: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Payment Mode
class PaymentModeCreateRequest(BaseModel):
    mode_name: str
    mode_code: str
    mode_type: str
    is_default: bool = False
    requires_reference: bool = False
    requires_approval: bool = False
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    processing_fee_percentage: Decimal = 0
    processing_fee_fixed: Decimal = 0
    notes: Optional[str] = None

class PaymentModeResponse(BaseModel):
    id: int
    company_id: int
    mode_name: str
    mode_code: str
    mode_type: str
    is_active: bool
    is_default: bool
    requires_reference: bool
    requires_approval: bool
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    processing_fee_percentage: Decimal
    processing_fee_fixed: Decimal
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Staff
class StaffCreateRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: date
    designation: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[Decimal] = None
    commission_percentage: Decimal = 0

class StaffResponse(BaseModel):
    id: int
    company_id: int
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: date
    date_of_leaving: Optional[date] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[Decimal] = None
    commission_percentage: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Staff Target
class StaffTargetCreateRequest(BaseModel):
    staff_id: int
    target_period: str
    target_date: date
    target_amount: Decimal
    target_quantity: Optional[Decimal] = None
    commission_rate: Decimal = 0
    bonus_amount: Decimal = 0
    notes: Optional[str] = None

class StaffTargetResponse(BaseModel):
    id: int
    company_id: int
    staff_id: int
    target_period: str
    target_date: date
    target_amount: Decimal
    achieved_amount: Decimal
    target_quantity: Optional[Decimal] = None
    achieved_quantity: Decimal
    commission_rate: Decimal
    bonus_amount: Decimal
    achievement_percentage: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Sale Return
class SaleReturnCreateRequest(BaseModel):
    customer_id: int
    return_date: date
    return_reason: Optional[str] = None
    return_type: str = 'defective'
    original_bill_id: Optional[int] = None
    staff_id: Optional[int] = None
    notes: Optional[str] = None

class SaleReturnItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    original_bill_item_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    gst_rate: Optional[Decimal] = None
    return_reason: Optional[str] = None
    notes: Optional[str] = None

class SaleReturnResponse(BaseModel):
    id: int
    company_id: int
    return_number: str
    return_date: date
    customer_id: int
    staff_id: Optional[int] = None
    original_bill_id: Optional[int] = None
    original_bill_number: Optional[str] = None
    original_bill_date: Optional[date] = None
    return_reason: Optional[str] = None
    return_type: str
    total_quantity: Decimal
    total_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    net_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Sale Challan Endpoints
@router.post("/sale-challans", response_model=SaleChallanResponse)
async def create_sale_challan(
    challan_data: SaleChallanCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sale challan"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        challan = enhanced_sales_service.create_sale_challan(
            db=db,
            company_id=company_id,
            customer_id=challan_data.customer_id,
            challan_date=challan_data.challan_date,
            challan_type=challan_data.challan_type,
            staff_id=challan_data.staff_id,
            delivery_address=challan_data.delivery_address,
            delivery_date=challan_data.delivery_date,
            delivery_time=challan_data.delivery_time,
            contact_person=challan_data.contact_person,
            contact_phone=challan_data.contact_phone,
            notes=challan_data.notes,
            user_id=current_user.id
        )
        
        return challan
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sale challan: {str(e)}"
        )

@router.post("/sale-challans/{challan_id}/items")
async def add_items_to_challan(
    challan_id: int,
    items: List[SaleChallanItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Add items to sale challan"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        challan_items = enhanced_sales_service.add_items_to_challan(
            db=db,
            company_id=company_id,
            challan_id=challan_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to sale challan successfully",
            "items_count": len(challan_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to sale challan: {str(e)}"
        )

@router.post("/sale-challans/{challan_id}/deliver")
async def deliver_challan_items(
    challan_id: int,
    item_deliveries: List[dict],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Deliver challan items"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_sales_service.deliver_challan_items(
            db=db,
            company_id=company_id,
            challan_id=challan_id,
            item_deliveries=item_deliveries,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Challan items delivered successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to deliver challan items"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deliver challan items: {str(e)}"
        )

# Bill Series Endpoints
@router.post("/bill-series", response_model=BillSeriesResponse)
async def create_bill_series(
    series_data: BillSeriesCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create bill series"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        series = enhanced_sales_service.create_bill_series(
            db=db,
            company_id=company_id,
            series_name=series_data.series_name,
            series_code=series_data.series_code,
            document_type=series_data.document_type,
            prefix=series_data.prefix,
            suffix=series_data.suffix,
            starting_number=series_data.starting_number,
            number_length=series_data.number_length,
            is_default=series_data.is_default,
            notes=series_data.notes,
            user_id=current_user.id
        )
        
        return series
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create bill series: {str(e)}"
        )

@router.get("/bill-series", response_model=List[BillSeriesResponse])
async def get_bill_series(
    company_id: int = Query(...),
    document_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get bill series"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    series = enhanced_sales_service.get_bill_series(
        db=db,
        company_id=company_id,
        document_type=document_type,
        is_active=is_active
    )
    
    return series

@router.get("/bill-series/generate-number")
async def generate_bill_number(
    document_type: str = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Generate next bill number"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        bill_number = enhanced_sales_service.generate_bill_number(
            db=db,
            company_id=company_id,
            document_type=document_type
        )
        
        return {
            "document_type": document_type,
            "bill_number": bill_number
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate bill number: {str(e)}"
        )

# Payment Mode Endpoints
@router.post("/payment-modes", response_model=PaymentModeResponse)
async def create_payment_mode(
    mode_data: PaymentModeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create payment mode"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        mode = enhanced_sales_service.create_payment_mode(
            db=db,
            company_id=company_id,
            mode_name=mode_data.mode_name,
            mode_code=mode_data.mode_code,
            mode_type=mode_data.mode_type,
            is_default=mode_data.is_default,
            requires_reference=mode_data.requires_reference,
            requires_approval=mode_data.requires_approval,
            minimum_amount=mode_data.minimum_amount,
            maximum_amount=mode_data.maximum_amount,
            processing_fee_percentage=mode_data.processing_fee_percentage,
            processing_fee_fixed=mode_data.processing_fee_fixed,
            notes=mode_data.notes,
            user_id=current_user.id
        )
        
        return mode
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment mode: {str(e)}"
        )

@router.get("/payment-modes", response_model=List[PaymentModeResponse])
async def get_payment_modes(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get payment modes"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    modes = enhanced_sales_service.get_payment_modes(
        db=db,
        company_id=company_id,
        is_active=is_active
    )
    
    return modes

# Staff Management Endpoints
@router.post("/staff", response_model=StaffResponse)
async def create_staff(
    staff_data: StaffCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create staff member"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        staff = enhanced_sales_service.create_staff(
            db=db,
            company_id=company_id,
            employee_id=staff_data.employee_id,
            first_name=staff_data.first_name,
            last_name=staff_data.last_name,
            email=staff_data.email,
            phone=staff_data.phone,
            address=staff_data.address,
            date_of_birth=staff_data.date_of_birth,
            date_of_joining=staff_data.date_of_joining,
            designation=staff_data.designation,
            department=staff_data.department,
            salary=staff_data.salary,
            commission_percentage=staff_data.commission_percentage,
            user_id=current_user.id
        )
        
        return staff
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create staff: {str(e)}"
        )

@router.get("/staff", response_model=List[StaffResponse])
async def get_staff(
    company_id: int = Query(...),
    is_active: Optional[bool] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get staff members"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    staff = enhanced_sales_service.get_staff(
        db=db,
        company_id=company_id,
        is_active=is_active,
        department=department
    )
    
    return staff

# Staff Target Endpoints
@router.post("/staff-targets", response_model=StaffTargetResponse)
async def create_staff_target(
    target_data: StaffTargetCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create staff target"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        target = enhanced_sales_service.create_staff_target(
            db=db,
            company_id=company_id,
            staff_id=target_data.staff_id,
            target_period=target_data.target_period,
            target_date=target_data.target_date,
            target_amount=target_data.target_amount,
            target_quantity=target_data.target_quantity,
            commission_rate=target_data.commission_rate,
            bonus_amount=target_data.bonus_amount,
            notes=target_data.notes,
            user_id=current_user.id
        )
        
        return target
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create staff target: {str(e)}"
        )

@router.post("/staff-targets/{staff_id}/update-achievement")
async def update_staff_target_achievement(
    staff_id: int,
    target_date: date = Query(...),
    achieved_amount: Decimal = Query(...),
    achieved_quantity: Optional[Decimal] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Update staff target achievement"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_sales_service.update_staff_target_achievement(
            db=db,
            company_id=company_id,
            staff_id=staff_id,
            target_date=target_date,
            achieved_amount=achieved_amount,
            achieved_quantity=achieved_quantity
        )
        
        if success:
            return {"message": "Staff target achievement updated successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to update staff target achievement"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update staff target achievement: {str(e)}"
        )

# Sale Return Endpoints
@router.post("/sale-returns", response_model=SaleReturnResponse)
async def create_sale_return(
    return_data: SaleReturnCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sale return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        sale_return = enhanced_sales_service.create_sale_return(
            db=db,
            company_id=company_id,
            customer_id=return_data.customer_id,
            return_date=return_data.return_date,
            return_reason=return_data.return_reason,
            return_type=return_data.return_type,
            original_bill_id=return_data.original_bill_id,
            staff_id=return_data.staff_id,
            notes=return_data.notes,
            user_id=current_user.id
        )
        
        return sale_return
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sale return: {str(e)}"
        )

@router.post("/sale-returns/{return_id}/items")
async def add_items_to_sale_return(
    return_id: int,
    items: List[SaleReturnItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Add items to sale return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        return_items = enhanced_sales_service.add_items_to_sale_return(
            db=db,
            company_id=company_id,
            return_id=return_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to sale return successfully",
            "items_count": len(return_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to sale return: {str(e)}"
        )

@router.post("/sale-returns/{return_id}/process")
async def process_sale_return(
    return_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Process sale return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_sales_service.process_sale_return(
            db=db,
            company_id=company_id,
            return_id=return_id,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "Sale return processed successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to process sale return"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process sale return: {str(e)}"
        )

# POS Session Endpoints
@router.post("/pos-sessions/start")
async def start_pos_session(
    staff_id: int = Query(...),
    opening_cash: Decimal = Query(0),
    notes: Optional[str] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Start POS session"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        session = enhanced_sales_service.start_pos_session(
            db=db,
            company_id=company_id,
            staff_id=staff_id,
            opening_cash=opening_cash,
            notes=notes,
            user_id=current_user.id
        )
        
        return {
            "message": "POS session started successfully",
            "session_id": session.id,
            "session_number": session.session_number
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start POS session: {str(e)}"
        )

@router.post("/pos-sessions/{session_id}/close")
async def close_pos_session(
    session_id: int,
    closing_cash: Decimal = Query(...),
    notes: Optional[str] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Close POS session"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_sales_service.close_pos_session(
            db=db,
            company_id=company_id,
            session_id=session_id,
            closing_cash=closing_cash,
            notes=notes,
            user_id=current_user.id
        )
        
        if success:
            return {"message": "POS session closed successfully"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to close POS session"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close POS session: {str(e)}"
        )

# Sales Analytics Endpoints
@router.get("/analytics")
async def get_sales_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    staff_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sales analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = enhanced_sales_service.get_sales_analytics(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date,
        staff_id=staff_id
    )
    
    return analytics