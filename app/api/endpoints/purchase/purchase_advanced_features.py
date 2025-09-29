# backend/app/api/endpoints/purchase/purchase_advanced_features.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.purchase.purchase_advanced_features_integration import (
    PurchaseAdvancedWorkflow, PurchaseDocumentManagement, PurchaseAdvancedReporting,
    PurchaseAuditTrailAdvanced, PurchaseNotification, PurchaseDashboard,
    WorkflowStatus, DocumentType, ReportType
)

router = APIRouter()

# --- Schemas ---
class PurchaseAdvancedWorkflowCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    approval_workflow_id: int = Field(..., gt=0)
    approval_record_id: Optional[int] = None
    workflow_type: str = Field(..., min_length=3, max_length=50)
    priority: str = Field(default='medium', max_length=20)
    initiated_by: int = Field(..., gt=0)
    due_date: Optional[datetime] = None
    auto_approve: bool = False
    require_approval: bool = True
    approval_levels: int = Field(default=1, ge=1)
    current_level: int = Field(default=1, ge=1)
    escalation_enabled: bool = False
    escalation_days: Optional[int] = Field(None, ge=1)
    workflow_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseAdvancedWorkflowResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    approval_workflow_id: int
    approval_record_id: Optional[int]
    workflow_type: str
    workflow_status: WorkflowStatus
    priority: str
    initiated_by: int
    initiated_date: datetime
    completed_date: Optional[datetime]
    due_date: Optional[datetime]
    auto_approve: bool
    require_approval: bool
    approval_levels: int
    current_level: int
    escalation_enabled: bool
    escalation_days: Optional[int]
    workflow_data: Optional[Dict[str, Any]]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseDocumentManagementCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    document_attachment_id: int = Field(..., gt=0)
    document_type: DocumentType
    document_name: str = Field(..., min_length=1, max_length=255)
    document_description: Optional[str] = None
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, ge=0)
    file_extension: Optional[str] = Field(None, max_length=10)
    mime_type: Optional[str] = Field(None, max_length=100)
    is_required: bool = False
    is_public: bool = False
    is_encrypted: bool = False
    version: str = Field(default='1.0', max_length=20)
    checksum: Optional[str] = Field(None, max_length=64)
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseDocumentManagementResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    document_attachment_id: int
    document_type: DocumentType
    document_name: str
    document_description: Optional[str]
    file_path: str
    file_size: Optional[int]
    file_extension: Optional[str]
    mime_type: Optional[str]
    is_required: bool
    is_public: bool
    is_encrypted: bool
    version: str
    checksum: Optional[str]
    upload_status: str
    upload_date: Optional[datetime]
    last_accessed: Optional[datetime]
    access_count: int
    tags: Optional[Dict[str, Any]]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseAdvancedReportingCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    report_template_id: Optional[int] = None
    report_instance_id: Optional[int] = None
    report_type: ReportType
    report_name: str = Field(..., min_length=1, max_length=255)
    report_description: Optional[str] = None
    report_parameters: Optional[Dict[str, Any]] = None
    report_filters: Optional[Dict[str, Any]] = None
    is_scheduled: bool = False
    schedule_frequency: Optional[str] = Field(None, max_length=20)
    schedule_time: Optional[str] = Field(None, max_length=10)
    schedule_day: Optional[str] = Field(None, max_length=20)
    output_format: str = Field(default='pdf', max_length=20)
    email_recipients: Optional[List[str]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseAdvancedReportingResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    report_template_id: Optional[int]
    report_instance_id: Optional[int]
    report_type: ReportType
    report_name: str
    report_description: Optional[str]
    report_parameters: Optional[Dict[str, Any]]
    report_filters: Optional[Dict[str, Any]]
    is_scheduled: bool
    schedule_frequency: Optional[str]
    schedule_time: Optional[str]
    schedule_day: Optional[str]
    next_run_date: Optional[datetime]
    report_status: str
    last_run_date: Optional[datetime]
    last_run_status: Optional[str]
    run_count: int
    success_count: int
    failure_count: int
    output_format: str
    output_path: Optional[str]
    output_size: Optional[int]
    email_recipients: Optional[List[str]]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Purchase Advanced Workflows
@router.post("/purchase-advanced-workflows", response_model=PurchaseAdvancedWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_advanced_workflow(
    workflow_data: PurchaseAdvancedWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_advanced_workflows"))
):
    """Create new purchase advanced workflow"""
    workflow = PurchaseAdvancedWorkflow(**workflow_data.dict())
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow

@router.get("/purchase-advanced-workflows", response_model=List[PurchaseAdvancedWorkflowResponse])
async def get_purchase_advanced_workflows(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    workflow_type: Optional[str] = Query(None),
    workflow_status: Optional[WorkflowStatus] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_advanced_workflows"))
):
    """Get all purchase advanced workflows"""
    query = db.query(PurchaseAdvancedWorkflow)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseAdvancedWorkflow.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseAdvancedWorkflow.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseAdvancedWorkflow.purchase_return_id == purchase_return_id)
    if workflow_type:
        query = query.filter(PurchaseAdvancedWorkflow.workflow_type == workflow_type)
    if workflow_status:
        query = query.filter(PurchaseAdvancedWorkflow.workflow_status == workflow_status)
    if priority:
        query = query.filter(PurchaseAdvancedWorkflow.priority == priority)
    
    return query.order_by(PurchaseAdvancedWorkflow.created_at.desc()).all()

@router.get("/purchase-advanced-workflows/{workflow_id}", response_model=PurchaseAdvancedWorkflowResponse)
async def get_purchase_advanced_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_advanced_workflows"))
):
    """Get specific purchase advanced workflow"""
    workflow = db.query(PurchaseAdvancedWorkflow).filter(PurchaseAdvancedWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase advanced workflow not found")
    return workflow

# Purchase Document Management
@router.post("/purchase-document-management", response_model=PurchaseDocumentManagementResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_document_management(
    document_data: PurchaseDocumentManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_document_management"))
):
    """Create new purchase document management record"""
    document = PurchaseDocumentManagement(**document_data.dict())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/purchase-document-management", response_model=List[PurchaseDocumentManagementResponse])
async def get_purchase_document_management(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    document_type: Optional[DocumentType] = Query(None),
    upload_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_document_management"))
):
    """Get all purchase document management records"""
    query = db.query(PurchaseDocumentManagement)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseDocumentManagement.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseDocumentManagement.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseDocumentManagement.purchase_return_id == purchase_return_id)
    if document_type:
        query = query.filter(PurchaseDocumentManagement.document_type == document_type)
    if upload_status:
        query = query.filter(PurchaseDocumentManagement.upload_status == upload_status)
    
    return query.order_by(PurchaseDocumentManagement.created_at.desc()).all()

# Purchase Advanced Reporting
@router.post("/purchase-advanced-reporting", response_model=PurchaseAdvancedReportingResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_advanced_reporting(
    reporting_data: PurchaseAdvancedReportingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_advanced_reporting"))
):
    """Create new purchase advanced reporting record"""
    reporting = PurchaseAdvancedReporting(**reporting_data.dict())
    db.add(reporting)
    db.commit()
    db.refresh(reporting)
    return reporting

@router.get("/purchase-advanced-reporting", response_model=List[PurchaseAdvancedReportingResponse])
async def get_purchase_advanced_reporting(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    report_type: Optional[ReportType] = Query(None),
    report_status: Optional[str] = Query(None),
    is_scheduled: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_advanced_reporting"))
):
    """Get all purchase advanced reporting records"""
    query = db.query(PurchaseAdvancedReporting)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseAdvancedReporting.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseAdvancedReporting.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseAdvancedReporting.purchase_return_id == purchase_return_id)
    if report_type:
        query = query.filter(PurchaseAdvancedReporting.report_type == report_type)
    if report_status:
        query = query.filter(PurchaseAdvancedReporting.report_status == report_status)
    if is_scheduled is not None:
        query = query.filter(PurchaseAdvancedReporting.is_scheduled == is_scheduled)
    
    return query.order_by(PurchaseAdvancedReporting.created_at.desc()).all()

# Purchase Advanced Features Statistics
@router.get("/purchase-advanced-features-statistics")
async def get_purchase_advanced_features_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_advanced_features"))
):
    """Get purchase advanced features statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_workflows": 35,
        "pending_workflows": 5,
        "completed_workflows": 28,
        "total_documents": 95,
        "total_reports": 20,
        "scheduled_reports": 12,
        "workflow_success_rate": 90.0,
        "document_upload_success_rate": 97.0,
        "report_success_rate": 95.0
    }

# Auto-create Advanced Workflows
@router.post("/auto-create-advanced-workflows/{purchase_invoice_id}")
async def auto_create_advanced_workflows(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_advanced_workflows"))
):
    """Auto-create advanced workflows for purchase invoice"""
    # This would contain the actual workflow creation logic
    # For now, returning a placeholder response
    return {
        "message": "Advanced workflows creation initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }

# Generate Advanced Reports
@router.post("/generate-advanced-reports/{purchase_invoice_id}")
async def generate_advanced_reports(
    purchase_invoice_id: int,
    report_type: str = Query(..., description="Report type to generate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_advanced_reporting"))
):
    """Generate advanced reports for purchase invoice"""
    # This would contain the actual report generation logic
    # For now, returning a placeholder response
    return {
        "message": "Advanced report generation initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "report_type": report_type,
        "status": "processing"
    }