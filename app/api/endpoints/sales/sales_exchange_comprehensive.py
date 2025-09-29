# backend/app/api/endpoints/sales/sales_exchange_comprehensive.py
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

# Pydantic schemas for Sales Exchange
class SalesExchangeCreateRequest(BaseModel):
    exchange_number: str
    exchange_date: date
    customer_id: int
    staff_id: Optional[int] = None
    original_bill_id: int
    exchange_reason: str
    exchange_type: str = 'size_exchange'
    exchange_notes: Optional[str] = None
    exchange_fee: Decimal = 0
    
    @validator('exchange_number')
    def validate_exchange_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Exchange number must be at least 3 characters')
        return v

class SalesExchangeItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    original_quantity: Decimal
    original_unit_price: Decimal
    new_item_id: Optional[int] = None  # If exchanging for different item
    new_variant_id: Optional[int] = None
    new_quantity: Decimal
    new_unit_price: Decimal
    exchange_reason: Optional[str] = None
    condition_notes: Optional[str] = None

class SalesExchangeUpdateRequest(BaseModel):
    exchange_reason: Optional[str] = None
    exchange_type: Optional[str] = None
    exchange_notes: Optional[str] = None
    status: Optional[str] = None
    exchange_fee: Optional[Decimal] = None

class SalesExchangeResponse(BaseModel):
    id: int
    exchange_number: str
    exchange_date: date
    customer_id: int
    staff_id: Optional[int]
    original_bill_id: int
    original_bill_number: str
    original_bill_date: date
    exchange_reason: str
    exchange_type: str
    exchange_notes: Optional[str]
    exchange_fee: Decimal
    original_items_value: Decimal
    new_items_value: Decimal
    difference_amount: Decimal
    original_cgst_amount: Decimal
    original_sgst_amount: Decimal
    original_igst_amount: Decimal
    original_total_gst_amount: Decimal
    new_cgst_amount: Decimal
    new_sgst_amount: Decimal
    new_igst_amount: Decimal
    new_total_gst_amount: Decimal
    gst_difference: Decimal
    net_difference: Decimal
    status: str
    processed_date: Optional[datetime]
    completed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Exchange Workflow Schemas
class SalesExchangeWorkflowCreateRequest(BaseModel):
    workflow_step: str
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    comments: Optional[str] = None
    priority: str = 'medium'

class SalesExchangeDocumentCreateRequest(BaseModel):
    document_type: str
    document_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    is_encrypted: bool = False
    version: str = '1.0'

# Exchange Inventory Schemas
class SalesExchangeInventoryCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    warehouse_id: int
    original_quantity_returned: Decimal
    original_serial_numbers: Optional[str] = None  # JSON array
    original_batch_numbers: Optional[str] = None  # JSON array
    original_expiry_dates: Optional[str] = None  # JSON array
    original_condition: str = 'good'
    new_item_id: Optional[int] = None
    new_variant_id: Optional[int] = None
    new_quantity_issued: Decimal
    new_serial_numbers: Optional[str] = None  # JSON array
    new_batch_numbers: Optional[str] = None  # JSON array
    new_expiry_dates: Optional[str] = None  # JSON array

# Exchange Accounting Schemas
class SalesExchangeAccountingCreateRequest(BaseModel):
    debit_account_id: int
    credit_account_id: int
    amount: Decimal
    tax_amount: Decimal = 0
    accounting_date: date
    exchange_type: str = 'exchange'
    notes: Optional[str] = None

# Exchange GST Schemas
class SalesExchangeGSTCreateRequest(BaseModel):
    gst_number: Optional[str] = None
    place_of_supply: Optional[str] = None
    place_of_supply_type: str = 'intrastate'
    original_cgst_rate: Decimal = 0
    original_sgst_rate: Decimal = 0
    original_igst_rate: Decimal = 0
    original_cess_rate: Decimal = 0
    new_cgst_rate: Decimal = 0
    new_sgst_rate: Decimal = 0
    new_igst_rate: Decimal = 0
    new_cess_rate: Decimal = 0

# Exchange Customer Schemas
class SalesExchangeCustomerCreateRequest(BaseModel):
    customer_id: int
    exchange_policy_accepted: bool = False
    customer_signature: Optional[str] = None
    customer_satisfaction_rating: Optional[int] = None
    customer_feedback: Optional[str] = None
    would_recommend: Optional[bool] = None

# Exchange Analytics Schemas
class SalesExchangeAnalyticsCreateRequest(BaseModel):
    analytics_provider: str
    event_type: str
    event_data: Optional[str] = None  # JSON data
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    exchange_duration_minutes: Optional[Decimal] = None
    staff_efficiency_score: Optional[int] = None
    customer_satisfaction_score: Optional[int] = None

# Core Sales Exchange Endpoints
@router.post("/sales-exchanges", response_model=SalesExchangeResponse)
async def create_sales_exchange(
    exchange_data: SalesExchangeCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange for B2C retail"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        sales_exchange = enhanced_sales_service.create_sales_exchange(
            db=db,
            company_id=company_id,
            exchange_number=exchange_data.exchange_number,
            exchange_date=exchange_data.exchange_date,
            customer_id=exchange_data.customer_id,
            staff_id=exchange_data.staff_id,
            original_bill_id=exchange_data.original_bill_id,
            exchange_reason=exchange_data.exchange_reason,
            exchange_type=exchange_data.exchange_type,
            exchange_notes=exchange_data.exchange_notes,
            exchange_fee=exchange_data.exchange_fee,
            user_id=current_user.id
        )
        
        return sales_exchange
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sales exchange: {str(e)}"
        )

@router.get("/sales-exchanges", response_model=List[SalesExchangeResponse])
async def get_sales_exchanges(
    company_id: int = Query(...),
    customer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    exchange_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sales exchanges with filters"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        sales_exchanges = enhanced_sales_service.get_sales_exchanges(
            db=db,
            company_id=company_id,
            customer_id=customer_id,
            status=status,
            exchange_type=exchange_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return sales_exchanges
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales exchanges: {str(e)}"
        )

@router.get("/sales-exchanges/{exchange_id}", response_model=SalesExchangeResponse)
async def get_sales_exchange(
    exchange_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get specific sales exchange"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        sales_exchange = enhanced_sales_service.get_sales_exchange_by_id(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id
        )
        
        if not sales_exchange:
            raise HTTPException(
                status_code=404,
                detail="Sales exchange not found"
            )
        
        return sales_exchange
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales exchange: {str(e)}"
        )

@router.put("/sales-exchanges/{exchange_id}", response_model=SalesExchangeResponse)
async def update_sales_exchange(
    exchange_id: int,
    exchange_data: SalesExchangeUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Update sales exchange"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        sales_exchange = enhanced_sales_service.update_sales_exchange(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            exchange_data=exchange_data.dict(exclude_unset=True),
            user_id=current_user.id
        )
        
        return sales_exchange
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update sales exchange: {str(e)}"
        )

@router.delete("/sales-exchanges/{exchange_id}")
async def delete_sales_exchange(
    exchange_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Delete sales exchange"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_sales_service.delete_sales_exchange(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Sales exchange not found"
            )
        
        return {"message": "Sales exchange deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete sales exchange: {str(e)}"
        )

# Exchange Item Management
@router.post("/sales-exchanges/{exchange_id}/items")
async def add_items_to_sales_exchange(
    exchange_id: int,
    items: List[SalesExchangeItemCreateRequest],
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Add items to sales exchange"""
    
    try:
        # Convert Pydantic models to dictionaries
        items_data = [item.dict() for item in items]
        
        exchange_items = enhanced_sales_service.add_items_to_sales_exchange(
            db=db,
            company_id=company_id,
            exchange_id=exchange_id,
            items=items_data,
            user_id=current_user.id
        )
        
        return {
            "message": "Items added to sales exchange successfully",
            "items_count": len(exchange_items)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add items to sales exchange: {str(e)}"
        )

@router.post("/sales-exchanges/{exchange_id}/process")
async def process_sales_exchange(
    exchange_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Process sales exchange - create new bill and complete exchange"""
    
    try:
        result = enhanced_sales_service.process_sales_exchange(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Sales exchange processed successfully",
            "new_bill_id": result.get("new_bill_id"),
            "difference_amount": result.get("difference_amount"),
            "exchange_completed": result.get("exchange_completed")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process sales exchange: {str(e)}"
        )

# Exchange Workflow Endpoints
@router.post("/sales-exchanges/{exchange_id}/workflows")
async def create_sales_exchange_workflow(
    exchange_id: int,
    workflow_data: SalesExchangeWorkflowCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange workflow"""
    
    try:
        workflow = enhanced_sales_service.create_sales_exchange_workflow(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            workflow_data=workflow_data.dict(),
            user_id=current_user.id
        )
        
        return workflow
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.post("/sales-exchanges/{exchange_id}/documents")
async def create_sales_exchange_document(
    exchange_id: int,
    document_data: SalesExchangeDocumentCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange document"""
    
    try:
        document = enhanced_sales_service.create_sales_exchange_document(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            document_data=document_data.dict(),
            user_id=current_user.id
        )
        
        return document
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create document: {str(e)}"
        )

# Exchange Inventory Endpoints
@router.post("/sales-exchanges/{exchange_id}/inventory")
async def create_sales_exchange_inventory(
    exchange_id: int,
    inventory_data: SalesExchangeInventoryCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange inventory integration"""
    
    try:
        inventory = enhanced_sales_service.create_sales_exchange_inventory(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            inventory_data=inventory_data.dict(),
            user_id=current_user.id
        )
        
        return inventory
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create inventory integration: {str(e)}"
        )

# Exchange Accounting Endpoints
@router.post("/sales-exchanges/{exchange_id}/accounting")
async def create_sales_exchange_accounting(
    exchange_id: int,
    accounting_data: SalesExchangeAccountingCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange accounting entry"""
    
    try:
        accounting_entry = enhanced_sales_service.create_sales_exchange_accounting(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            accounting_data=accounting_data.dict(),
            user_id=current_user.id
        )
        
        return accounting_entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create accounting entry: {str(e)}"
        )

# Exchange GST Endpoints
@router.post("/sales-exchanges/{exchange_id}/gst")
async def create_sales_exchange_gst(
    exchange_id: int,
    gst_data: SalesExchangeGSTCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange GST entry"""
    
    try:
        gst_entry = enhanced_sales_service.create_sales_exchange_gst(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            gst_data=gst_data.dict(),
            user_id=current_user.id
        )
        
        return gst_entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create GST entry: {str(e)}"
        )

# Exchange Customer Endpoints
@router.post("/sales-exchanges/{exchange_id}/customer")
async def create_sales_exchange_customer(
    exchange_id: int,
    customer_data: SalesExchangeCustomerCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange customer integration"""
    
    try:
        customer = enhanced_sales_service.create_sales_exchange_customer(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            customer_data=customer_data.dict(),
            user_id=current_user.id
        )
        
        return customer
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create customer integration: {str(e)}"
        )

# Exchange Analytics Endpoints
@router.post("/sales-exchanges/{exchange_id}/analytics")
async def create_sales_exchange_analytics(
    exchange_id: int,
    analytics_data: SalesExchangeAnalyticsCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Create sales exchange analytics tracking"""
    
    try:
        analytics = enhanced_sales_service.create_sales_exchange_analytics(
            db=db,
            exchange_id=exchange_id,
            company_id=company_id,
            analytics_data=analytics_data.dict(),
            user_id=current_user.id
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create analytics tracking: {str(e)}"
        )

# Bulk Operations
@router.post("/sales-exchanges/bulk-process")
async def bulk_process_sales_exchanges(
    exchange_ids: List[int],
    action: str,  # approve, reject, process, cancel
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Bulk process sales exchanges"""
    
    try:
        results = enhanced_sales_service.bulk_process_sales_exchanges(
            db=db,
            exchange_ids=exchange_ids,
            action=action,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk process sales exchanges: {str(e)}"
        )

# Reports and Analytics
@router.get("/sales-exchanges/reports/summary")
async def get_sales_exchange_summary_report(
    company_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    customer_id: Optional[int] = Query(None),
    exchange_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sales exchange summary report"""
    
    try:
        report = enhanced_sales_service.get_sales_exchange_summary_report(
            db=db,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            customer_id=customer_id,
            exchange_type=exchange_type
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary report: {str(e)}"
        )

@router.get("/sales-exchanges/reports/analytics")
async def get_sales_exchange_analytics_report(
    company_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sales exchange analytics report"""
    
    try:
        report = enhanced_sales_service.get_sales_exchange_analytics_report(
            db=db,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics report: {str(e)}"
        )

# Special B2C Exchange Endpoints
@router.get("/sales-exchanges/pending-for-pos")
async def get_pending_exchanges_for_pos(
    company_id: int = Query(...),
    customer_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get pending exchanges that can be used in POS"""
    
    try:
        pending_exchanges = enhanced_sales_service.get_pending_exchanges_for_pos(
            db=db,
            company_id=company_id,
            customer_id=customer_id
        )
        
        return pending_exchanges
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending exchanges: {str(e)}"
        )

@router.post("/sales-exchanges/{exchange_id}/link-to-pos")
async def link_exchange_to_pos_bill(
    exchange_id: int,
    pos_bill_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.manage")),
    db: Session = Depends(get_db)
):
    """Link exchange to POS bill for B2C workflow"""
    
    try:
        result = enhanced_sales_service.link_exchange_to_pos_bill(
            db=db,
            exchange_id=exchange_id,
            pos_bill_id=pos_bill_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Exchange linked to POS bill successfully",
            "exchange_id": exchange_id,
            "pos_bill_id": pos_bill_id,
            "difference_amount": result.get("difference_amount")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to link exchange to POS bill: {str(e)}"
        )