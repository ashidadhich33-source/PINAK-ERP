# backend/app/models/accounting/advanced_reporting.py
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import json

from ....database import get_db
from ...core.security import get_current_user, require_permission
from ....models.core import User, Company
from ....models.accounting.advanced_reporting import (
    ReportTemplate, ReportInstance, DashboardWidget, WidgetData,
    ScheduledReport, ReportRun, ReportCategory, ReportParameter,
    ReportFilter, ReportColumn, ReportAccess, ReportType, WidgetType, ExportFormat
)

router = APIRouter()

# --- Schemas ---
class ReportTemplateCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    report_type: ReportType
    category: Optional[str] = None
    template_data: Dict[str, Any]
    sql_query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[Dict[str, Any]] = None
    formatting: Optional[Dict[str, Any]] = None
    is_public: bool = False

class ReportTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    report_type: ReportType
    category: Optional[str]
    template_data: Dict[str, Any]
    sql_query: Optional[str]
    parameters: Optional[Dict[str, Any]]
    filters: Optional[Dict[str, Any]]
    columns: Optional[Dict[str, Any]]
    formatting: Optional[Dict[str, Any]]
    is_public: bool
    is_active: bool
    created_by: int
    version: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ReportInstanceCreate(BaseModel):
    template_id: int
    name: str = Field(..., min_length=3, max_length=100)
    parameters: Optional[Dict[str, Any]] = None
    filters_applied: Optional[Dict[str, Any]] = None

class ReportInstanceResponse(BaseModel):
    id: int
    template_id: int
    name: str
    parameters: Optional[Dict[str, Any]]
    filters_applied: Optional[Dict[str, Any]]
    generated_by: int
    generated_date: datetime
    status: str
    file_path: Optional[str]
    file_size: Optional[int]
    record_count: Optional[int]
    execution_time: Optional[float]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class DashboardWidgetCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    widget_type: WidgetType
    data_source: str = Field(..., min_length=3, max_length=100)
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    configuration: Dict[str, Any]
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)
    width: int = Field(default=4, ge=1, le=12)
    height: int = Field(default=3, ge=1, le=12)
    refresh_interval: int = Field(default=300, ge=60)
    is_public: bool = False

class DashboardWidgetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    widget_type: WidgetType
    data_source: str
    query: Optional[str]
    parameters: Optional[Dict[str, Any]]
    configuration: Dict[str, Any]
    position_x: int
    position_y: int
    width: int
    height: int
    refresh_interval: int
    is_public: bool
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ScheduledReportCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    template_id: int
    schedule_cron: str = Field(..., min_length=5, max_length=100)
    parameters: Optional[Dict[str, Any]] = None
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    export_format: ExportFormat = ExportFormat.PDF

class ScheduledReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template_id: int
    schedule_cron: str
    parameters: Optional[Dict[str, Any]]
    email_recipients: Optional[List[str]]
    email_subject: Optional[str]
    email_body: Optional[str]
    export_format: ExportFormat
    is_active: bool
    created_by: int
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    run_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Report Templates
@router.post("/report-templates", response_model=ReportTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_report_template(
    template_data: ReportTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_reports"))
):
    """Create new report template"""
    template = ReportTemplate(
        **template_data.dict(),
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    report_type: Optional[ReportType] = Query(None),
    category: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get all report templates"""
    query = db.query(ReportTemplate)
    
    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    if category:
        query = query.filter(ReportTemplate.category == category)
    if is_public is not None:
        query = query.filter(ReportTemplate.is_public == is_public)
    
    return query.filter(ReportTemplate.is_active == True).all()

@router.get("/report-templates/{template_id}", response_model=ReportTemplateResponse)
async def get_report_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get specific report template"""
    template = db.query(ReportTemplate).filter(ReportTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report template not found")
    return template

# Report Instances
@router.post("/report-instances", response_model=ReportInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_report_instance(
    instance_data: ReportInstanceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("generate_reports"))
):
    """Create new report instance"""
    # Check if template exists
    template = db.query(ReportTemplate).filter(ReportTemplate.id == instance_data.template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report template not found")
    
    instance = ReportInstance(
        **instance_data.dict(),
        generated_by=current_user.id,
        status="generating"
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    
    # Add background task to generate report
    background_tasks.add_task(generate_report_task, instance.id, db)
    
    return instance

@router.get("/report-instances", response_model=List[ReportInstanceResponse])
async def get_report_instances(
    template_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    generated_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get all report instances"""
    query = db.query(ReportInstance)
    
    if template_id:
        query = query.filter(ReportInstance.template_id == template_id)
    if status:
        query = query.filter(ReportInstance.status == status)
    if generated_by:
        query = query.filter(ReportInstance.generated_by == generated_by)
    
    return query.order_by(ReportInstance.generated_date.desc()).all()

@router.get("/report-instances/{instance_id}", response_model=ReportInstanceResponse)
async def get_report_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get specific report instance"""
    instance = db.query(ReportInstance).filter(ReportInstance.id == instance_id).first()
    if not instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report instance not found")
    return instance

# Dashboard Widgets
@router.post("/dashboard-widgets", response_model=DashboardWidgetResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard_widget(
    widget_data: DashboardWidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_dashboard"))
):
    """Create new dashboard widget"""
    widget = DashboardWidget(
        **widget_data.dict(),
        created_by=current_user.id
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return widget

@router.get("/dashboard-widgets", response_model=List[DashboardWidgetResponse])
async def get_dashboard_widgets(
    widget_type: Optional[WidgetType] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_dashboard"))
):
    """Get all dashboard widgets"""
    query = db.query(DashboardWidget)
    
    if widget_type:
        query = query.filter(DashboardWidget.widget_type == widget_type)
    if is_public is not None:
        query = query.filter(DashboardWidget.is_public == is_public)
    
    return query.filter(DashboardWidget.is_active == True).all()

@router.get("/dashboard-widgets/{widget_id}", response_model=DashboardWidgetResponse)
async def get_dashboard_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_dashboard"))
):
    """Get specific dashboard widget"""
    widget = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dashboard widget not found")
    return widget

# Scheduled Reports
@router.post("/scheduled-reports", response_model=ScheduledReportResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduled_report(
    report_data: ScheduledReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_scheduled_reports"))
):
    """Create new scheduled report"""
    # Check if template exists
    template = db.query(ReportTemplate).filter(ReportTemplate.id == report_data.template_id).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report template not found")
    
    scheduled_report = ScheduledReport(
        **report_data.dict(),
        created_by=current_user.id
    )
    db.add(scheduled_report)
    db.commit()
    db.refresh(scheduled_report)
    return scheduled_report

@router.get("/scheduled-reports", response_model=List[ScheduledReportResponse])
async def get_scheduled_reports(
    is_active: Optional[bool] = Query(None),
    created_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_scheduled_reports"))
):
    """Get all scheduled reports"""
    query = db.query(ScheduledReport)
    
    if is_active is not None:
        query = query.filter(ScheduledReport.is_active == is_active)
    if created_by:
        query = query.filter(ScheduledReport.created_by == created_by)
    
    return query.all()

@router.get("/scheduled-reports/{report_id}", response_model=ScheduledReportResponse)
async def get_scheduled_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_scheduled_reports"))
):
    """Get specific scheduled report"""
    report = db.query(ScheduledReport).filter(ScheduledReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled report not found")
    return report

# Report Categories
@router.get("/report-categories")
async def get_report_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get all report categories"""
    categories = db.query(ReportCategory).filter(ReportCategory.is_active == True).all()
    return [{"id": cat.id, "name": cat.name, "description": cat.description} for cat in categories]

# Report Statistics
@router.get("/report-statistics")
async def get_report_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_reports"))
):
    """Get report statistics"""
    query = db.query(ReportInstance)
    
    if date_from:
        query = query.filter(ReportInstance.generated_date >= date_from)
    if date_to:
        query = query.filter(ReportInstance.generated_date <= date_to)
    
    total_reports = query.count()
    completed_reports = query.filter(ReportInstance.status == "completed").count()
    failed_reports = query.filter(ReportInstance.status == "failed").count()
    generating_reports = query.filter(ReportInstance.status == "generating").count()
    
    return {
        "total_reports": total_reports,
        "completed_reports": completed_reports,
        "failed_reports": failed_reports,
        "generating_reports": generating_reports,
        "success_rate": (completed_reports / total_reports * 100) if total_reports > 0 else 0
    }

# Background task for report generation
async def generate_report_task(instance_id: int, db: Session):
    """Background task to generate report"""
    try:
        # This would contain the actual report generation logic
        # For now, just updating the status
        instance = db.query(ReportInstance).filter(ReportInstance.id == instance_id).first()
        if instance:
            instance.status = "completed"
            instance.file_path = f"/reports/{instance_id}.pdf"
            instance.file_size = 1024  # Placeholder
            instance.record_count = 100  # Placeholder
            instance.execution_time = 5.5  # Placeholder
            db.commit()
    except Exception as e:
        # Update status to failed
        instance = db.query(ReportInstance).filter(ReportInstance.id == instance_id).first()
        if instance:
            instance.status = "failed"
            instance.error_message = str(e)
            db.commit()