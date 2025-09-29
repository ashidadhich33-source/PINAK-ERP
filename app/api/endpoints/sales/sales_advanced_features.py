# backend/app/api/endpoints/sales/sales_advanced_features.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.sales.sales_advanced_features_integration import (
    SaleAdvancedWorkflow, SaleDocumentManagement, SaleAdvancedReporting,
    SaleAuditTrailAdvanced, SaleNotification, SaleDashboard,
    WorkflowStatus, DocumentType, ReportType
)

router = APIRouter()

# --- Schemas ---
class SaleAdvancedWorkflowCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleAdvancedWorkflowResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

class SaleDocumentManagementCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleDocumentManagementResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

class SaleAdvancedReportingCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleAdvancedReportingResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

# Sale Advanced Workflows
@router.post("/sale-advanced-workflows", response_model=SaleAdvancedWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_advanced_workflow(
    workflow_data: SaleAdvancedWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_advanced_workflows"))
):
    """Create new sale advanced workflow"""
    workflow = SaleAdvancedWorkflow(**workflow_data.dict())
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow

@router.get("/sale-advanced-workflows", response_model=List[SaleAdvancedWorkflowResponse])
async def get_sale_advanced_workflows(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    workflow_type: Optional[str] = Query(None),
    workflow_status: Optional[WorkflowStatus] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_advanced_workflows"))
):
    """Get all sale advanced workflows"""
    query = db.query(SaleAdvancedWorkflow)
    
    if sale_invoice_id:
        query = query.filter(SaleAdvancedWorkflow.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleAdvancedWorkflow.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleAdvancedWorkflow.sale_return_id == sale_return_id)
    if workflow_type:
        query = query.filter(SaleAdvancedWorkflow.workflow_type == workflow_type)
    if workflow_status:
        query = query.filter(SaleAdvancedWorkflow.workflow_status == workflow_status)
    if priority:
        query = query.filter(SaleAdvancedWorkflow.priority == priority)
    
    return query.order_by(SaleAdvancedWorkflow.created_at.desc()).all()

@router.get("/sale-advanced-workflows/{workflow_id}", response_model=SaleAdvancedWorkflowResponse)
async def get_sale_advanced_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_advanced_workflows"))
):
    """Get specific sale advanced workflow"""
    workflow = db.query(SaleAdvancedWorkflow).filter(SaleAdvancedWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale advanced workflow not found")
    return workflow

# Sale Document Management
@router.post("/sale-document-management", response_model=SaleDocumentManagementResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_document_management(
    document_data: SaleDocumentManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_document_management"))
):
    """Create new sale document management record"""
    document = SaleDocumentManagement(**document_data.dict())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

@router.get("/sale-document-management", response_model=List[SaleDocumentManagementResponse])
async def get_sale_document_management(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    document_type: Optional[DocumentType] = Query(None),
    upload_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_document_management"))
):
    """Get all sale document management records"""
    query = db.query(SaleDocumentManagement)
    
    if sale_invoice_id:
        query = query.filter(SaleDocumentManagement.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleDocumentManagement.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleDocumentManagement.sale_return_id == sale_return_id)
    if document_type:
        query = query.filter(SaleDocumentManagement.document_type == document_type)
    if upload_status:
        query = query.filter(SaleDocumentManagement.upload_status == upload_status)
    
    return query.order_by(SaleDocumentManagement.created_at.desc()).all()

# Sale Advanced Reporting
@router.post("/sale-advanced-reporting", response_model=SaleAdvancedReportingResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_advanced_reporting(
    reporting_data: SaleAdvancedReportingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_advanced_reporting"))
):
    """Create new sale advanced reporting record"""
    reporting = SaleAdvancedReporting(**reporting_data.dict())
    db.add(reporting)
    db.commit()
    db.refresh(reporting)
    return reporting

@router.get("/sale-advanced-reporting", response_model=List[SaleAdvancedReportingResponse])
async def get_sale_advanced_reporting(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    report_type: Optional[ReportType] = Query(None),
    report_status: Optional[str] = Query(None),
    is_scheduled: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_advanced_reporting"))
):
    """Get all sale advanced reporting records"""
    query = db.query(SaleAdvancedReporting)
    
    if sale_invoice_id:
        query = query.filter(SaleAdvancedReporting.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleAdvancedReporting.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleAdvancedReporting.sale_return_id == sale_return_id)
    if report_type:
        query = query.filter(SaleAdvancedReporting.report_type == report_type)
    if report_status:
        query = query.filter(SaleAdvancedReporting.report_status == report_status)
    if is_scheduled is not None:
        query = query.filter(SaleAdvancedReporting.is_scheduled == is_scheduled)
    
    return query.order_by(SaleAdvancedReporting.created_at.desc()).all()

# Sale Advanced Features Statistics
@router.get("/sales-advanced-features-statistics")
async def get_sales_advanced_features_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_advanced_features"))
):
    """Get sales advanced features statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_workflows": 45,
        "pending_workflows": 8,
        "completed_workflows": 35,
        "total_documents": 120,
        "total_reports": 25,
        "scheduled_reports": 15,
        "workflow_success_rate": 87.5,
        "document_upload_success_rate": 95.0,
        "report_success_rate": 92.0
    }

# Auto-create Advanced Workflows
@router.post("/auto-create-advanced-workflows/{sale_invoice_id}")
async def auto_create_advanced_workflows(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_advanced_workflows"))
):
    """Auto-create advanced workflows for sale invoice"""
    # This would contain the actual workflow creation logic
    # For now, returning a placeholder response
    return {
        "message": "Advanced workflows creation initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }

# Generate Advanced Reports
@router.post("/generate-advanced-reports/{sale_invoice_id}")
async def generate_advanced_reports(
    sale_invoice_id: int,
    report_type: str = Query(..., description="Report type to generate"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_advanced_reporting"))
):
    """Generate advanced reports for sale invoice"""
    # This would contain the actual report generation logic
    # For now, returning a placeholder response
    return {
        "message": "Advanced report generation initiated",
        "sale_invoice_id": sale_invoice_id,
        "report_type": report_type,
        "status": "processing"
    }