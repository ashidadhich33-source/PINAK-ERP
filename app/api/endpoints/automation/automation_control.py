# backend/app/api/endpoints/automation/automation_control.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.automation.automation_control_service import AutomationControlService

router = APIRouter()

# Initialize service
automation_control_service = AutomationControlService()

# Pydantic schemas for Automation Control
class AutomationSettingsRequest(BaseModel):
    gst_automation: Optional[dict] = None
    banking_automation: Optional[dict] = None
    safety_controls: Optional[dict] = None

class AutomationApprovalRequest(BaseModel):
    approval_id: int
    approved: bool
    comments: Optional[str] = None

class AutomationSettingsResponse(BaseModel):
    company_id: int
    gst_automation: dict
    banking_automation: dict
    safety_controls: dict

class AutomationLogResponse(BaseModel):
    id: int
    automation_type: str
    action: str
    reference_id: Optional[int]
    status: str
    created_at: datetime
    details: dict

# Automation Control Endpoints
@router.get("/settings", response_model=AutomationSettingsResponse)
async def get_automation_settings(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.view")),
    db: Session = Depends(get_db)
):
    """Get automation settings for company"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get automation settings
        settings = automation_control_service.get_automation_settings(db, company_id)
        
        return AutomationSettingsResponse(
            company_id=settings['company_id'],
            gst_automation=settings['gst_automation'],
            banking_automation=settings['banking_automation'],
            safety_controls=settings['safety_controls']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get automation settings: {str(e)}"
        )

@router.put("/settings", response_model=AutomationSettingsResponse)
async def update_automation_settings(
    settings_data: AutomationSettingsRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.update")),
    db: Session = Depends(get_db)
):
    """Update automation settings with safety controls"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Update automation settings
        result = automation_control_service.update_automation_settings(db, company_id, settings_data.dict())
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['error']
            )
        
        return AutomationSettingsResponse(
            company_id=result['settings']['company_id'],
            gst_automation=result['settings']['gst_automation'],
            banking_automation=result['settings']['banking_automation'],
            safety_controls=result['settings']['safety_controls']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update automation settings: {str(e)}"
        )

@router.post("/gst/process")
async def process_gst_automation(
    return_data: dict,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.gst")),
    db: Session = Depends(get_db)
):
    """Process GST automation with safety controls"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Process GST automation
        result = automation_control_service.process_gst_automation(db, company_id, return_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process GST automation: {str(e)}"
        )

@router.post("/banking/process")
async def process_banking_automation(
    transaction_data: dict,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.banking")),
    db: Session = Depends(get_db)
):
    """Process banking automation with safety controls"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Process banking automation
        result = automation_control_service.process_banking_automation(db, company_id, transaction_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process banking automation: {str(e)}"
        )

@router.post("/approve", response_model=dict)
async def approve_automation_request(
    approval_data: AutomationApprovalRequest,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.approve")),
    db: Session = Depends(get_db)
):
    """Approve or reject automation request"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Approve automation request
        result = automation_control_service.approve_automation_request(
            db, company_id, approval_data.approval_id, 
            approval_data.approved, approval_data.comments
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve automation request: {str(e)}"
        )

@router.get("/logs", response_model=List[AutomationLogResponse])
async def get_automation_logs(
    company_id: int = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_permission("automation.logs")),
    db: Session = Depends(get_db)
):
    """Get automation logs for audit trail"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get automation logs
        logs = automation_control_service.get_automation_logs(db, company_id, limit)
        
        return [
            AutomationLogResponse(
                id=log['id'],
                automation_type=log['automation_type'],
                action=log['action'],
                reference_id=log['reference_id'],
                status=log['status'],
                created_at=log['created_at'],
                details=log['details']
            )
            for log in logs
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get automation logs: {str(e)}"
        )

@router.post("/rollback")
async def rollback_automation(
    log_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.rollback")),
    db: Session = Depends(get_db)
):
    """Rollback automation action"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Rollback automation
        result = automation_control_service.rollback_automation(db, company_id, log_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rollback automation: {str(e)}"
        )

@router.get("/status")
async def get_automation_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("automation.status")),
    db: Session = Depends(get_db)
):
    """Get automation status and capabilities"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get automation status
        return {
            "automation_status": {
                "gst_automation": "configurable",
                "banking_automation": "configurable",
                "safety_controls": "enabled",
                "approval_workflow": "enabled",
                "audit_trail": "enabled",
                "rollback_capability": "enabled"
            },
            "automation_features": [
                "Configurable automation settings",
                "Manual approval workflow",
                "Audit trail and logging",
                "Rollback capability",
                "Exception handling",
                "Safety controls"
            ],
            "safety_features": [
                "Manual approval required",
                "Audit trail enabled",
                "Rollback capability",
                "Exception handling",
                "Conservative defaults",
                "User control"
            ],
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get automation status: {str(e)}"
        )