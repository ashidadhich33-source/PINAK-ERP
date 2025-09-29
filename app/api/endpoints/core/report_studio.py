# backend/app/api/endpoints/report_studio.py
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
from ...services.report_studio_service import report_studio_service

router = APIRouter()

# Pydantic schemas for Report Category
class ReportCategoryCreateRequest(BaseModel):
    category_name: str
    category_code: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    display_order: int = 0
    icon: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

class ReportCategoryResponse(BaseModel):
    id: int
    company_id: int
    category_name: str
    category_code: str
    description: Optional[str] = None
    parent_category_id: Optional[int] = None
    display_order: int
    is_active: bool
    icon: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Report Template
class ReportTemplateCreateRequest(BaseModel):
    template_name: str
    template_code: str
    category_id: int
    report_type: str
    data_source: str
    query_sql: Optional[str] = None
    template_config: Optional[dict] = None
    parameters: Optional[dict] = None
    filters: Optional[dict] = None
    columns: Optional[dict] = None
    chart_config: Optional[dict] = None
    layout_config: Optional[dict] = None
    is_public: bool = False
    is_system: bool = False
    version: str = '1.0'
    notes: Optional[str] = None

class ReportTemplateResponse(BaseModel):
    id: int
    company_id: int
    template_name: str
    template_code: str
    category_id: int
    description: Optional[str] = None
    report_type: str
    data_source: str
    query_sql: Optional[str] = None
    template_config: dict
    parameters: Optional[dict] = None
    filters: Optional[dict] = None
    columns: Optional[dict] = None
    chart_config: Optional[dict] = None
    layout_config: Optional[dict] = None
    is_public: bool
    is_system: bool
    is_active: bool
    version: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Report Instance
class ReportInstanceCreateRequest(BaseModel):
    template_id: int
    instance_name: str
    instance_code: Optional[str] = None
    parameters: Optional[dict] = None
    filters: Optional[dict] = None
    notes: Optional[str] = None

class ReportInstanceResponse(BaseModel):
    id: int
    company_id: int
    template_id: int
    instance_name: str
    instance_code: str
    parameters: Optional[dict] = None
    filters: Optional[dict] = None
    data: Optional[dict] = None
    status: str
    generated_date: Optional[datetime] = None
    file_path: Optional[str] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    execution_time: Optional[float] = None
    row_count: Optional[int] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Report View
class ReportViewCreateRequest(BaseModel):
    instance_id: int
    view_name: str
    view_type: str
    view_config: dict
    chart_type: Optional[str] = None
    chart_config: Optional[dict] = None
    filters: Optional[dict] = None
    sorting: Optional[dict] = None
    grouping: Optional[dict] = None
    aggregation: Optional[dict] = None
    display_order: int = 0
    is_default: bool = False
    notes: Optional[str] = None

class ReportViewResponse(BaseModel):
    id: int
    company_id: int
    instance_id: int
    view_name: str
    view_type: str
    view_config: dict
    chart_type: Optional[str] = None
    chart_config: Optional[dict] = None
    filters: Optional[dict] = None
    sorting: Optional[dict] = None
    grouping: Optional[dict] = None
    aggregation: Optional[dict] = None
    display_order: int
    is_default: bool
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Pydantic schemas for Report Schedule
class ReportScheduleCreateRequest(BaseModel):
    template_id: int
    schedule_name: str
    schedule_type: str
    cron_expression: Optional[str] = None
    schedule_time: Optional[str] = None
    schedule_date: Optional[date] = None
    parameters: Optional[dict] = None
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    file_format: str = 'pdf'
    notes: Optional[str] = None

class ReportScheduleResponse(BaseModel):
    id: int
    company_id: int
    template_id: int
    schedule_name: str
    schedule_type: str
    cron_expression: Optional[str] = None
    schedule_time: Optional[str] = None
    schedule_date: Optional[date] = None
    parameters: Optional[dict] = None
    email_recipients: Optional[List[str]] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    file_format: str
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int
    success_count: int
    failure_count: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Report Category Endpoints
@router.post("/report-categories", response_model=ReportCategoryResponse)
async def create_report_category(
    category_data: ReportCategoryCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Create report category"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        category = report_studio_service.create_report_category(
            db=db,
            company_id=company_id,
            category_name=category_data.category_name,
            category_code=category_data.category_code,
            description=category_data.description,
            parent_category_id=category_data.parent_category_id,
            display_order=category_data.display_order,
            icon=category_data.icon,
            color=category_data.color,
            notes=category_data.notes,
            user_id=current_user.id
        )
        
        return category
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report category: {str(e)}"
        )

@router.get("/report-categories", response_model=List[ReportCategoryResponse])
async def get_report_categories(
    company_id: int = Query(...),
    parent_category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("report.view")),
    db: Session = Depends(get_db)
):
    """Get report categories"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    categories = report_studio_service.get_report_categories(
        db=db,
        company_id=company_id,
        parent_category_id=parent_category_id,
        is_active=is_active
    )
    
    return categories

# Report Template Endpoints
@router.post("/report-templates", response_model=ReportTemplateResponse)
async def create_report_template(
    template_data: ReportTemplateCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Create report template"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        template = report_studio_service.create_report_template(
            db=db,
            company_id=company_id,
            template_name=template_data.template_name,
            template_code=template_data.template_code,
            category_id=template_data.category_id,
            report_type=template_data.report_type,
            data_source=template_data.data_source,
            query_sql=template_data.query_sql,
            template_config=template_data.template_config,
            parameters=template_data.parameters,
            filters=template_data.filters,
            columns=template_data.columns,
            chart_config=template_data.chart_config,
            layout_config=template_data.layout_config,
            is_public=template_data.is_public,
            is_system=template_data.is_system,
            version=template_data.version,
            notes=template_data.notes,
            user_id=current_user.id
        )
        
        return template
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report template: {str(e)}"
        )

@router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def get_report_templates(
    company_id: int = Query(...),
    category_id: Optional[int] = Query(None),
    report_type: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    is_system: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("report.view")),
    db: Session = Depends(get_db)
):
    """Get report templates"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    templates = report_studio_service.get_report_templates(
        db=db,
        company_id=company_id,
        category_id=category_id,
        report_type=report_type,
        is_public=is_public,
        is_system=is_system,
        is_active=is_active
    )
    
    return templates

# Report Instance Endpoints
@router.post("/report-instances", response_model=ReportInstanceResponse)
async def create_report_instance(
    instance_data: ReportInstanceCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Create report instance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        instance = report_studio_service.create_report_instance(
            db=db,
            company_id=company_id,
            template_id=instance_data.template_id,
            instance_name=instance_data.instance_name,
            instance_code=instance_data.instance_code,
            parameters=instance_data.parameters,
            filters=instance_data.filters,
            notes=instance_data.notes,
            user_id=current_user.id
        )
        
        return instance
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report instance: {str(e)}"
        )

@router.post("/report-instances/{instance_id}/generate", response_model=ReportInstanceResponse)
async def generate_report_instance(
    instance_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Generate report instance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        instance = report_studio_service.generate_report_instance(
            db=db,
            company_id=company_id,
            instance_id=instance_id,
            user_id=current_user.id
        )
        
        return instance
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report instance: {str(e)}"
        )

# Report View Endpoints
@router.post("/report-views", response_model=ReportViewResponse)
async def create_report_view(
    view_data: ReportViewCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Create report view"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        view = report_studio_service.create_report_view(
            db=db,
            company_id=company_id,
            instance_id=view_data.instance_id,
            view_name=view_data.view_name,
            view_type=view_data.view_type,
            view_config=view_data.view_config,
            chart_type=view_data.chart_type,
            chart_config=view_data.chart_config,
            filters=view_data.filters,
            sorting=view_data.sorting,
            grouping=view_data.grouping,
            aggregation=view_data.aggregation,
            display_order=view_data.display_order,
            is_default=view_data.is_default,
            notes=view_data.notes,
            user_id=current_user.id
        )
        
        return view
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report view: {str(e)}"
        )

# Report Schedule Endpoints
@router.post("/report-schedules", response_model=ReportScheduleResponse)
async def create_report_schedule(
    schedule_data: ReportScheduleCreateRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Create report schedule"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        schedule = report_studio_service.create_report_schedule(
            db=db,
            company_id=company_id,
            template_id=schedule_data.template_id,
            schedule_name=schedule_data.schedule_name,
            schedule_type=schedule_data.schedule_type,
            cron_expression=schedule_data.cron_expression,
            schedule_time=schedule_data.schedule_time,
            schedule_date=schedule_data.schedule_date,
            parameters=schedule_data.parameters,
            email_recipients=schedule_data.email_recipients,
            email_subject=schedule_data.email_subject,
            email_body=schedule_data.email_body,
            file_format=schedule_data.file_format,
            notes=schedule_data.notes,
            user_id=current_user.id
        )
        
        return schedule
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report schedule: {str(e)}"
        )

@router.post("/report-schedules/{schedule_id}/execute")
async def execute_report_schedule(
    schedule_id: int,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Execute report schedule"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        log = report_studio_service.execute_report_schedule(
            db=db,
            company_id=company_id,
            schedule_id=schedule_id,
            user_id=current_user.id
        )
        
        return {
            "message": "Report schedule executed successfully",
            "log_id": log.id,
            "status": log.status,
            "execution_time": log.execution_time
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute report schedule: {str(e)}"
        )

# Report Export Endpoints
@router.post("/report-instances/{instance_id}/export")
async def export_report_instance(
    instance_id: int,
    export_format: str = Query(...),
    export_config: Optional[dict] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("report.manage")),
    db: Session = Depends(get_db)
):
    """Export report instance"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    try:
        export = report_studio_service.export_report_instance(
            db=db,
            company_id=company_id,
            instance_id=instance_id,
            export_format=export_format,
            export_config=export_config,
            user_id=current_user.id
        )
        
        return {
            "message": "Report exported successfully",
            "export_id": export.id,
            "file_path": export.file_path,
            "file_size": export.file_size,
            "export_format": export.export_format
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export report: {str(e)}"
        )

# Report Analytics Endpoints
@router.get("/analytics")
async def get_report_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    template_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("report.view")),
    db: Session = Depends(get_db)
):
    """Get report analytics"""
    
    # Check if user has access to company
    from ...services.company_service import company_service
    company = company_service.get_company_by_id(db, company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this company"
        )
    
    analytics = report_studio_service.get_report_analytics(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date,
        template_id=template_id
    )
    
    return analytics