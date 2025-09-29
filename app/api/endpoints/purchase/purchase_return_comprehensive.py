# backend/app/api/endpoints/purchase/purchase_return_comprehensive.py
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
from ...services.enhanced_purchase_service import enhanced_purchase_service

router = APIRouter()

# Pydantic schemas for Purchase Return
class PurchaseReturnCreateRequest(BaseModel):
    return_number: str
    return_date: date
    supplier_id: int
    original_bill_id: Optional[int] = None
    return_reason: str
    return_type: str = 'defective'
    notes: Optional[str] = None
    
    @validator('return_number')
    def validate_return_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Return number must be at least 3 characters')
        return v

class PurchaseReturnItemCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    quantity: Decimal
    unit_price: Decimal
    return_reason: Optional[str] = None
    notes: Optional[str] = None

class PurchaseReturnUpdateRequest(BaseModel):
    return_reason: Optional[str] = None
    return_type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class PurchaseReturnResponse(BaseModel):
    id: int
    return_number: str
    return_date: date
    supplier_id: int
    original_bill_id: Optional[int]
    return_reason: str
    return_type: str
    total_quantity: Decimal
    total_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_gst_amount: Decimal
    net_amount: Decimal
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Phase 1: Accounting Integration Schemas
class PurchaseReturnAccountingCreateRequest(BaseModel):
    debit_account_id: int
    credit_account_id: int
    amount: Decimal
    tax_amount: Decimal = 0
    accounting_date: date

class PurchaseReturnPaymentCreateRequest(BaseModel):
    payment_method: str
    payment_reference: Optional[str] = None
    payment_amount: Decimal
    payment_date: date
    bank_account_id: Optional[int] = None
    cheque_number: Optional[str] = None
    cheque_date: Optional[date] = None
    notes: Optional[str] = None

class PurchaseReturnAnalyticCreateRequest(BaseModel):
    analytic_account_id: int
    analytic_plan_id: Optional[int] = None
    amount: Decimal
    percentage: Optional[Decimal] = None
    distribution_type: str = 'amount'
    notes: Optional[str] = None

# Phase 2: Indian Localization Schemas
class PurchaseReturnGSTCreateRequest(BaseModel):
    gst_number: Optional[str] = None
    place_of_supply: Optional[str] = None
    place_of_supply_type: str = 'intrastate'
    cgst_rate: Decimal = 0
    sgst_rate: Decimal = 0
    igst_rate: Decimal = 0
    cess_rate: Decimal = 0
    is_reverse_charge: bool = False
    composition_scheme: bool = False

class PurchaseReturnEInvoiceCreateRequest(BaseModel):
    irn: Optional[str] = None
    cancellation_reason: Optional[str] = None

class PurchaseReturnEWaybillCreateRequest(BaseModel):
    distance_km: Optional[Decimal] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_mobile: Optional[str] = None
    transport_mode: str = 'road'
    cancellation_reason: Optional[str] = None

class PurchaseReturnTDSCreateRequest(BaseModel):
    tds_section: Optional[str] = None
    tds_rate: Decimal = 0
    tds_certificate_no: Optional[str] = None
    tds_certificate_date: Optional[date] = None
    tds_deposit_date: Optional[date] = None
    tds_challan_no: Optional[str] = None

class PurchaseReturnTCSCreateRequest(BaseModel):
    tcs_section: Optional[str] = None
    tcs_rate: Decimal = 0
    tcs_collection_date: Optional[date] = None
    tcs_challan_no: Optional[str] = None

# Phase 3: Advanced Features Schemas
class PurchaseReturnWorkflowCreateRequest(BaseModel):
    workflow_type: str
    workflow_step: str
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    comments: Optional[str] = None
    priority: str = 'medium'

class PurchaseReturnDocumentCreateRequest(BaseModel):
    document_type: str
    document_name: str
    file_path: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    is_encrypted: bool = False
    version: str = '1.0'

class PurchaseReturnNotificationCreateRequest(BaseModel):
    notification_type: str
    recipient_id: Optional[int] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    subject: Optional[str] = None
    message: str

# Phase 4: Enhanced Integration Schemas
class PurchaseReturnInventoryCreateRequest(BaseModel):
    item_id: int
    variant_id: Optional[int] = None
    warehouse_id: int
    quantity_returned: Decimal
    quantity_received: Decimal = 0
    stock_adjustment: bool = True
    adjustment_type: str = 'reduce'
    serial_numbers: Optional[str] = None  # JSON array
    batch_numbers: Optional[str] = None  # JSON array
    expiry_dates: Optional[str] = None  # JSON array
    quality_status: str = 'good'
    condition_notes: Optional[str] = None

class PurchaseReturnSupplierCreateRequest(BaseModel):
    supplier_id: int
    credit_note_issued: bool = False
    credit_note_number: Optional[str] = None
    credit_note_date: Optional[date] = None
    credit_note_amount: Optional[Decimal] = None
    supplier_acknowledgment: bool = False
    supplier_notes: Optional[str] = None
    return_authorization: Optional[str] = None
    return_authorization_date: Optional[date] = None
    supplier_rating: Optional[int] = None
    feedback: Optional[str] = None

class PurchaseReturnPerformanceCreateRequest(BaseModel):
    processing_time_ms: Optional[int] = None
    memory_usage_mb: Optional[int] = None
    cpu_usage_percent: Optional[Decimal] = None
    database_queries: Optional[int] = None
    cache_hit_rate: Optional[Decimal] = None
    response_time_ms: Optional[int] = None
    throughput_per_second: Optional[Decimal] = None
    error_rate: Optional[Decimal] = None
    optimization_suggestions: Optional[str] = None
    performance_score: Optional[int] = None

class PurchaseReturnUserExperienceCreateRequest(BaseModel):
    user_id: int
    satisfaction_score: Optional[int] = None
    ease_of_use_score: Optional[int] = None
    interface_rating: Optional[int] = None
    responsiveness_rating: Optional[int] = None
    accessibility_score: Optional[int] = None
    completion_time_minutes: Optional[Decimal] = None
    error_count: int = 0
    help_requests: int = 0
    feedback: Optional[str] = None
    improvement_suggestions: Optional[str] = None

class PurchaseReturnSyncCreateRequest(BaseModel):
    sync_type: str
    sync_frequency: str = 'realtime'
    max_retries: int = 3

class PurchaseReturnAnalyticsCreateRequest(BaseModel):
    analytics_provider: str
    event_type: str
    event_data: Optional[str] = None  # JSON data
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    page_url: Optional[str] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

# Core Purchase Return Endpoints
@router.post("/purchase-returns", response_model=PurchaseReturnResponse)
async def create_purchase_return(
    return_data: PurchaseReturnCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        purchase_return = enhanced_purchase_service.create_purchase_return(
            db=db,
            company_id=company_id,
            return_number=return_data.return_number,
            return_date=return_data.return_date,
            supplier_id=return_data.supplier_id,
            original_bill_id=return_data.original_bill_id,
            return_reason=return_data.return_reason,
            return_type=return_data.return_type,
            notes=return_data.notes,
            user_id=current_user.id
        )
        
        return purchase_return
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create purchase return: {str(e)}"
        )

@router.get("/purchase-returns", response_model=List[PurchaseReturnResponse])
async def get_purchase_returns(
    company_id: int = Query(...),
    supplier_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase returns with filters"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        purchase_returns = enhanced_purchase_service.get_purchase_returns(
            db=db,
            company_id=company_id,
            supplier_id=supplier_id,
            status=status,
            return_type=return_type,
            start_date=start_date,
            end_date=end_date
        )
        
        return purchase_returns
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get purchase returns: {str(e)}"
        )

@router.get("/purchase-returns/{return_id}", response_model=PurchaseReturnResponse)
async def get_purchase_return(
    return_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get specific purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        purchase_return = enhanced_purchase_service.get_purchase_return_by_id(
            db=db,
            return_id=return_id,
            company_id=company_id
        )
        
        if not purchase_return:
            raise HTTPException(
                status_code=404,
                detail="Purchase return not found"
            )
        
        return purchase_return
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get purchase return: {str(e)}"
        )

@router.put("/purchase-returns/{return_id}", response_model=PurchaseReturnResponse)
async def update_purchase_return(
    return_id: int,
    return_data: PurchaseReturnUpdateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Update purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        purchase_return = enhanced_purchase_service.update_purchase_return(
            db=db,
            return_id=return_id,
            company_id=company_id,
            return_data=return_data.dict(exclude_unset=True),
            user_id=current_user.id
        )
        
        return purchase_return
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update purchase return: {str(e)}"
        )

@router.delete("/purchase-returns/{return_id}")
async def delete_purchase_return(
    return_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Delete purchase return"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        success = enhanced_purchase_service.delete_purchase_return(
            db=db,
            return_id=return_id,
            company_id=company_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Purchase return not found"
            )
        
        return {"message": "Purchase return deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete purchase return: {str(e)}"
        )

# Phase 1: Accounting Integration Endpoints
@router.post("/purchase-returns/{return_id}/accounting")
async def create_purchase_return_accounting(
    return_id: int,
    accounting_data: PurchaseReturnAccountingCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return accounting entry"""
    
    try:
        accounting_entry = enhanced_purchase_service.create_purchase_return_accounting(
            db=db,
            return_id=return_id,
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

@router.post("/purchase-returns/{return_id}/payments")
async def create_purchase_return_payment(
    return_id: int,
    payment_data: PurchaseReturnPaymentCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return payment"""
    
    try:
        payment = enhanced_purchase_service.create_purchase_return_payment(
            db=db,
            return_id=return_id,
            company_id=company_id,
            payment_data=payment_data.dict(),
            user_id=current_user.id
        )
        
        return payment
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/analytics")
async def create_purchase_return_analytic(
    return_id: int,
    analytic_data: PurchaseReturnAnalyticCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return analytic entry"""
    
    try:
        analytic_entry = enhanced_purchase_service.create_purchase_return_analytic(
            db=db,
            return_id=return_id,
            company_id=company_id,
            analytic_data=analytic_data.dict(),
            user_id=current_user.id
        )
        
        return analytic_entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create analytic entry: {str(e)}"
        )

# Phase 2: Indian Localization Endpoints
@router.post("/purchase-returns/{return_id}/gst")
async def create_purchase_return_gst(
    return_id: int,
    gst_data: PurchaseReturnGSTCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return GST entry"""
    
    try:
        gst_entry = enhanced_purchase_service.create_purchase_return_gst(
            db=db,
            return_id=return_id,
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

@router.post("/purchase-returns/{return_id}/einvoice")
async def create_purchase_return_einvoice(
    return_id: int,
    einvoice_data: PurchaseReturnEInvoiceCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return E-invoice"""
    
    try:
        einvoice = enhanced_purchase_service.create_purchase_return_einvoice(
            db=db,
            return_id=return_id,
            company_id=company_id,
            einvoice_data=einvoice_data.dict(),
            user_id=current_user.id
        )
        
        return einvoice
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create E-invoice: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/ewaybill")
async def create_purchase_return_ewaybill(
    return_id: int,
    ewaybill_data: PurchaseReturnEWaybillCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return E-waybill"""
    
    try:
        ewaybill = enhanced_purchase_service.create_purchase_return_ewaybill(
            db=db,
            return_id=return_id,
            company_id=company_id,
            ewaybill_data=ewaybill_data.dict(),
            user_id=current_user.id
        )
        
        return ewaybill
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create E-waybill: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/tds")
async def create_purchase_return_tds(
    return_id: int,
    tds_data: PurchaseReturnTDSCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return TDS entry"""
    
    try:
        tds_entry = enhanced_purchase_service.create_purchase_return_tds(
            db=db,
            return_id=return_id,
            company_id=company_id,
            tds_data=tds_data.dict(),
            user_id=current_user.id
        )
        
        return tds_entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create TDS entry: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/tcs")
async def create_purchase_return_tcs(
    return_id: int,
    tcs_data: PurchaseReturnTCSCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return TCS entry"""
    
    try:
        tcs_entry = enhanced_purchase_service.create_purchase_return_tcs(
            db=db,
            return_id=return_id,
            company_id=company_id,
            tcs_data=tcs_data.dict(),
            user_id=current_user.id
        )
        
        return tcs_entry
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create TCS entry: {str(e)}"
        )

# Phase 3: Advanced Features Endpoints
@router.post("/purchase-returns/{return_id}/workflows")
async def create_purchase_return_workflow(
    return_id: int,
    workflow_data: PurchaseReturnWorkflowCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return workflow"""
    
    try:
        workflow = enhanced_purchase_service.create_purchase_return_workflow(
            db=db,
            return_id=return_id,
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

@router.post("/purchase-returns/{return_id}/documents")
async def create_purchase_return_document(
    return_id: int,
    document_data: PurchaseReturnDocumentCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return document"""
    
    try:
        document = enhanced_purchase_service.create_purchase_return_document(
            db=db,
            return_id=return_id,
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

@router.post("/purchase-returns/{return_id}/notifications")
async def create_purchase_return_notification(
    return_id: int,
    notification_data: PurchaseReturnNotificationCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return notification"""
    
    try:
        notification = enhanced_purchase_service.create_purchase_return_notification(
            db=db,
            return_id=return_id,
            company_id=company_id,
            notification_data=notification_data.dict(),
            user_id=current_user.id
        )
        
        return notification
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create notification: {str(e)}"
        )

# Phase 4: Enhanced Integration Endpoints
@router.post("/purchase-returns/{return_id}/inventory")
async def create_purchase_return_inventory(
    return_id: int,
    inventory_data: PurchaseReturnInventoryCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return inventory integration"""
    
    try:
        inventory = enhanced_purchase_service.create_purchase_return_inventory(
            db=db,
            return_id=return_id,
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

@router.post("/purchase-returns/{return_id}/supplier")
async def create_purchase_return_supplier(
    return_id: int,
    supplier_data: PurchaseReturnSupplierCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return supplier integration"""
    
    try:
        supplier = enhanced_purchase_service.create_purchase_return_supplier(
            db=db,
            return_id=return_id,
            company_id=company_id,
            supplier_data=supplier_data.dict(),
            user_id=current_user.id
        )
        
        return supplier
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create supplier integration: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/performance")
async def create_purchase_return_performance(
    return_id: int,
    performance_data: PurchaseReturnPerformanceCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return performance tracking"""
    
    try:
        performance = enhanced_purchase_service.create_purchase_return_performance(
            db=db,
            return_id=return_id,
            company_id=company_id,
            performance_data=performance_data.dict(),
            user_id=current_user.id
        )
        
        return performance
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create performance tracking: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/user-experience")
async def create_purchase_return_user_experience(
    return_id: int,
    ux_data: PurchaseReturnUserExperienceCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return user experience tracking"""
    
    try:
        ux = enhanced_purchase_service.create_purchase_return_user_experience(
            db=db,
            return_id=return_id,
            company_id=company_id,
            ux_data=ux_data.dict(),
            user_id=current_user.id
        )
        
        return ux
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user experience tracking: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/sync")
async def create_purchase_return_sync(
    return_id: int,
    sync_data: PurchaseReturnSyncCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return synchronization"""
    
    try:
        sync = enhanced_purchase_service.create_purchase_return_sync(
            db=db,
            return_id=return_id,
            company_id=company_id,
            sync_data=sync_data.dict(),
            user_id=current_user.id
        )
        
        return sync
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create synchronization: {str(e)}"
        )

@router.post("/purchase-returns/{return_id}/analytics")
async def create_purchase_return_analytics(
    return_id: int,
    analytics_data: PurchaseReturnAnalyticsCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Create purchase return analytics tracking"""
    
    try:
        analytics = enhanced_purchase_service.create_purchase_return_analytics(
            db=db,
            return_id=return_id,
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
@router.post("/purchase-returns/bulk-process")
async def bulk_process_purchase_returns(
    return_ids: List[int],
    action: str,  # approve, reject, process, cancel
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.manage")),
    db: Session = Depends(get_db)
):
    """Bulk process purchase returns"""
    
    try:
        results = enhanced_purchase_service.bulk_process_purchase_returns(
            db=db,
            return_ids=return_ids,
            action=action,
            company_id=company_id,
            user_id=current_user.id
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to bulk process purchase returns: {str(e)}"
        )

# Reports and Analytics
@router.get("/purchase-returns/reports/summary")
async def get_purchase_return_summary_report(
    company_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    supplier_id: Optional[int] = Query(None),
    return_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase return summary report"""
    
    try:
        report = enhanced_purchase_service.get_purchase_return_summary_report(
            db=db,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            supplier_id=supplier_id,
            return_type=return_type
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get summary report: {str(e)}"
        )

@router.get("/purchase-returns/reports/analytics")
async def get_purchase_return_analytics_report(
    company_id: int = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase return analytics report"""
    
    try:
        report = enhanced_purchase_service.get_purchase_return_analytics_report(
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