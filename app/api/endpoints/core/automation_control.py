"""
Automation Control API Endpoints
API endpoints for automation control
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.services.core.automation_control_service import AutomationControlService
from app.schemas.core.automation_control_schema import (
    AutomationSettingCreate,
    AutomationSettingUpdate,
    AutomationWorkflowCreate,
    AutomationRuleCreate,
    AutomationTriggerCreate,
    AutomationActionCreate,
    AutomationConditionCreate,
    AutomationApprovalCreate,
    AutomationExceptionCreate,
    AutomationRollbackCreate,
    AutomationSettingsResponse,
    AutomationWorkflowResponse,
    AutomationApprovalsResponse,
    AutomationLogsResponse,
    AutomationAnalyticsResponse,
    AutomationRollbackResponse,
    AutomationIntegrationStatusResponse,
    AutomationWorkflowAutomationResponse
)

router = APIRouter(prefix="/automation", tags=["Automation Control"])


@router.get("/settings", response_model=AutomationSettingsResponse)
async def get_automation_settings(
    company_id: int = Query(..., description="Company ID"),
    module: Optional[str] = Query(None, description="Module name"),
    db: Session = Depends(get_db)
):
    """Get automation settings for company and module"""
    service = AutomationControlService()
    result = service.get_automation_settings(db, company_id, module)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/settings", response_model=AutomationWorkflowResponse)
async def update_automation_setting(
    company_id: int,
    setting_data: AutomationSettingCreate,
    db: Session = Depends(get_db)
):
    """Update automation setting"""
    service = AutomationControlService()
    result = service.update_automation_setting(db, company_id, setting_data.dict())
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.put("/settings/{setting_id}", response_model=AutomationWorkflowResponse)
async def update_automation_setting_by_id(
    setting_id: int = Path(..., description="Setting ID"),
    setting_data: AutomationSettingUpdate,
    db: Session = Depends(get_db)
):
    """Update automation setting by ID"""
    service = AutomationControlService()
    result = service.update_automation_setting(db, setting_id, setting_data.dict())
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/workflows", response_model=AutomationWorkflowResponse)
async def create_automation_workflow(
    company_id: int,
    workflow_data: AutomationWorkflowCreate,
    db: Session = Depends(get_db)
):
    """Create automation workflow"""
    service = AutomationControlService()
    result = service.create_automation_workflow(db, company_id, workflow_data.dict())
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/workflows/{workflow_id}/execute", response_model=AutomationWorkflowResponse)
async def execute_automation_workflow(
    company_id: int,
    workflow_id: int = Path(..., description="Workflow ID"),
    trigger_data: dict = None,
    db: Session = Depends(get_db)
):
    """Execute automation workflow"""
    service = AutomationControlService()
    result = service.execute_automation_workflow(db, company_id, workflow_id, trigger_data or {})
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.get("/approvals", response_model=AutomationApprovalsResponse)
async def get_automation_approvals(
    company_id: int = Query(..., description="Company ID"),
    status: Optional[str] = Query(None, description="Approval status"),
    db: Session = Depends(get_db)
):
    """Get automation approvals"""
    service = AutomationControlService()
    result = service.get_automation_approvals(db, company_id, status)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/approvals/{approval_id}/approve", response_model=AutomationWorkflowResponse)
async def approve_automation_request(
    company_id: int,
    approval_id: int = Path(..., description="Approval ID"),
    approved_by: int = Query(..., description="Approved by user ID"),
    comments: Optional[str] = Query(None, description="Comments"),
    db: Session = Depends(get_db)
):
    """Approve automation request"""
    service = AutomationControlService()
    result = service.approve_automation_request(db, company_id, approval_id, approved_by, comments)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.get("/logs", response_model=AutomationLogsResponse)
async def get_automation_logs(
    company_id: int = Query(..., description="Company ID"),
    module: Optional[str] = Query(None, description="Module name"),
    limit: int = Query(100, description="Limit"),
    db: Session = Depends(get_db)
):
    """Get automation logs"""
    service = AutomationControlService()
    result = service.get_automation_logs(db, company_id, module, limit)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.post("/rollback/{log_id}", response_model=AutomationRollbackResponse)
async def rollback_automation(
    company_id: int,
    log_id: int = Path(..., description="Log ID"),
    rollback_data: AutomationRollbackCreate,
    db: Session = Depends(get_db)
):
    """Rollback automation execution"""
    service = AutomationControlService()
    result = service.rollback_automation(db, company_id, log_id, rollback_data.dict())
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.get("/analytics", response_model=AutomationAnalyticsResponse)
async def get_automation_analytics(
    company_id: int = Query(..., description="Company ID"),
    from_date: Optional[date] = Query(None, description="From date"),
    to_date: Optional[date] = Query(None, description="To date"),
    db: Session = Depends(get_db)
):
    """Get automation analytics"""
    service = AutomationControlService()
    result = service.get_automation_analytics(db, company_id, from_date, to_date)
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result


@router.get("/integration-status", response_model=AutomationIntegrationStatusResponse)
async def get_automation_integration_status(
    company_id: int = Query(..., description="Company ID"),
    db: Session = Depends(get_db)
):
    """Get automation integration status"""
    service = AutomationControlService()
    
    # Get automation settings for all modules
    settings_result = service.get_automation_settings(db, company_id)
    
    if not settings_result['success']:
        raise HTTPException(status_code=400, detail=settings_result['message'])
    
    # Calculate integration status
    modules = ['gst', 'banking', 'accounting', 'inventory', 'sales', 'purchase', 'pos', 'reports']
    integration_status = {}
    
    for module in modules:
        module_settings = settings_result['data'].get(module, {})
        enabled_count = sum(1 for setting in module_settings.values() if setting.get('is_enabled', False))
        total_count = len(module_settings)
        
        integration_status[module] = {
            'enabled_automations': enabled_count,
            'total_automations': total_count,
            'integration_percentage': round((enabled_count / total_count * 100) if total_count > 0 else 0, 2),
            'is_fully_integrated': enabled_count == total_count and total_count > 0
        }
    
    return {
        'success': True,
        'data': {
            'modules': integration_status,
            'overall_integration': round(sum(status['integration_percentage'] for status in integration_status.values()) / len(modules), 2),
            'fully_integrated_modules': [module for module, status in integration_status.items() if status['is_fully_integrated']],
            'partially_integrated_modules': [module for module, status in integration_status.items() if not status['is_fully_integrated'] and status['integration_percentage'] > 0]
        },
        'message': 'Retrieved automation integration status'
    }


@router.get("/workflow-automation", response_model=AutomationWorkflowAutomationResponse)
async def get_automation_workflow_automation(
    company_id: int = Query(..., description="Company ID"),
    db: Session = Depends(get_db)
):
    """Get automation workflow automation settings"""
    service = AutomationControlService()
    
    # Get automation settings
    settings_result = service.get_automation_settings(db, company_id)
    
    if not settings_result['success']:
        raise HTTPException(status_code=400, detail=settings_result['message'])
    
    # Get automation analytics
    analytics_result = service.get_automation_analytics(db, company_id)
    
    if not analytics_result['success']:
        analytics_data = {'total_executions': 0, 'success_rate': 0}
    else:
        analytics_data = analytics_result['data']
    
    # Calculate workflow automation status
    workflow_automation = {
        'automation_enabled': any(
            any(setting.get('is_enabled', False) for setting in module_settings.values())
            for module_settings in settings_result['data'].values()
        ),
        'approval_required': any(
            any(setting.get('requires_approval', False) for setting in module_settings.values())
            for module_settings in settings_result['data'].values()
        ),
        'total_automations': sum(len(module_settings) for module_settings in settings_result['data'].values()),
        'enabled_automations': sum(
            sum(1 for setting in module_settings.values() if setting.get('is_enabled', False))
            for module_settings in settings_result['data'].values()
        ),
        'execution_stats': analytics_data,
        'modules_with_automation': [
            module for module, settings in settings_result['data'].items()
            if any(setting.get('is_enabled', False) for setting in settings.values())
        ]
    }
    
    return {
        'success': True,
        'data': workflow_automation,
        'message': 'Retrieved automation workflow automation settings'
    }