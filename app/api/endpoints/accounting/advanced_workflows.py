# backend/app/api/endpoints/accounting/advanced_workflows.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import json

from ....database import get_db
from ...core.security import get_current_user, require_permission
from ....models.core import User, Company
from ....models.accounting.advanced_workflows import (
    ApprovalWorkflow, ApprovalStep, ApprovalRecord, ApprovalAction,
    EmailTemplate, EmailAutomation, DocumentAttachment, AuditTrail,
    WorkflowNotification, WorkflowStatus, ApprovalLevel, DocumentType
)

router = APIRouter()

# --- Schemas ---
class ApprovalWorkflowCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    document_type: DocumentType
    approval_level: ApprovalLevel = ApprovalLevel.SINGLE
    is_active: bool = True
    is_mandatory: bool = True
    auto_approve_amount: Optional[float] = None
    requires_justification: bool = False
    notification_settings: Optional[Dict[str, Any]] = None

class ApprovalWorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    document_type: DocumentType
    approval_level: ApprovalLevel
    is_active: bool
    is_mandatory: bool
    auto_approve_amount: Optional[float]
    requires_justification: bool
    notification_settings: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ApprovalStepCreate(BaseModel):
    workflow_id: int
    step_name: str = Field(..., min_length=3, max_length=100)
    step_order: int = Field(..., ge=1)
    approver_role: str = Field(..., min_length=3, max_length=100)
    approver_user_id: Optional[int] = None
    approver_group_id: Optional[int] = None
    is_mandatory: bool = True
    can_delegate: bool = False
    max_delegation_level: int = Field(default=1, ge=1)
    timeout_hours: Optional[int] = Field(None, ge=1)
    escalation_user_id: Optional[int] = None
    conditions: Optional[Dict[str, Any]] = None

class ApprovalStepResponse(BaseModel):
    id: int
    workflow_id: int
    step_name: str
    step_order: int
    approver_role: str
    approver_user_id: Optional[int]
    approver_group_id: Optional[int]
    is_mandatory: bool
    can_delegate: bool
    max_delegation_level: int
    timeout_hours: Optional[int]
    escalation_user_id: Optional[int]
    conditions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ApprovalRecordCreate(BaseModel):
    document_id: int = Field(..., ge=1)
    document_type: DocumentType
    workflow_id: int
    priority: str = Field(default="normal", regex="^(low|normal|high|urgent)$")
    due_date: Optional[datetime] = None
    comments: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ApprovalRecordResponse(BaseModel):
    id: int
    document_id: int
    document_type: DocumentType
    workflow_id: int
    current_step_id: Optional[int]
    status: WorkflowStatus
    initiated_by: int
    initiated_date: datetime
    completed_date: Optional[datetime]
    total_steps: int
    completed_steps: int
    priority: str
    due_date: Optional[datetime]
    comments: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ApprovalActionCreate(BaseModel):
    record_id: int
    step_id: int
    action_type: str = Field(..., regex="^(approve|reject|delegate|escalate|comment)$")
    comments: Optional[str] = None
    delegated_to: Optional[int] = None
    escalation_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ApprovalActionResponse(BaseModel):
    id: int
    record_id: int
    step_id: int
    action_type: str
    action_by: int
    action_date: datetime
    comments: Optional[str]
    delegated_to: Optional[int]
    escalation_reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Approval Workflows
@router.post("/approval-workflows", response_model=ApprovalWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_workflow(
    workflow_data: ApprovalWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_workflows"))
):
    """Create new approval workflow"""
    workflow = ApprovalWorkflow(**workflow_data.dict())
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow

@router.get("/approval-workflows", response_model=List[ApprovalWorkflowResponse])
async def get_approval_workflows(
    document_type: Optional[DocumentType] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get all approval workflows"""
    query = db.query(ApprovalWorkflow)
    
    if document_type:
        query = query.filter(ApprovalWorkflow.document_type == document_type)
    if is_active is not None:
        query = query.filter(ApprovalWorkflow.is_active == is_active)
    
    return query.all()

@router.get("/approval-workflows/{workflow_id}", response_model=ApprovalWorkflowResponse)
async def get_approval_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get specific approval workflow"""
    workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval workflow not found")
    return workflow

# Approval Steps
@router.post("/approval-steps", response_model=ApprovalStepResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_step(
    step_data: ApprovalStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_workflows"))
):
    """Create new approval step"""
    step = ApprovalStep(**step_data.dict())
    db.add(step)
    db.commit()
    db.refresh(step)
    return step

@router.get("/approval-steps", response_model=List[ApprovalStepResponse])
async def get_approval_steps(
    workflow_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get all approval steps"""
    query = db.query(ApprovalStep)
    
    if workflow_id:
        query = query.filter(ApprovalStep.workflow_id == workflow_id)
    
    return query.order_by(ApprovalStep.step_order).all()

# Approval Records
@router.post("/approval-records", response_model=ApprovalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_record(
    record_data: ApprovalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_workflows"))
):
    """Create new approval record"""
    # Get workflow and count steps
    workflow = db.query(ApprovalWorkflow).filter(ApprovalWorkflow.id == record_data.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    total_steps = db.query(ApprovalStep).filter(ApprovalStep.workflow_id == record_data.workflow_id).count()
    
    record = ApprovalRecord(
        **record_data.dict(),
        initiated_by=current_user.id,
        total_steps=total_steps
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.get("/approval-records", response_model=List[ApprovalRecordResponse])
async def get_approval_records(
    document_type: Optional[DocumentType] = Query(None),
    status: Optional[WorkflowStatus] = Query(None),
    initiated_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get all approval records"""
    query = db.query(ApprovalRecord)
    
    if document_type:
        query = query.filter(ApprovalRecord.document_type == document_type)
    if status:
        query = query.filter(ApprovalRecord.status == status)
    if initiated_by:
        query = query.filter(ApprovalRecord.initiated_by == initiated_by)
    
    return query.order_by(ApprovalRecord.created_at.desc()).all()

@router.get("/approval-records/{record_id}", response_model=ApprovalRecordResponse)
async def get_approval_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get specific approval record"""
    record = db.query(ApprovalRecord).filter(ApprovalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval record not found")
    return record

# Approval Actions
@router.post("/approval-actions", response_model=ApprovalActionResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_action(
    action_data: ApprovalActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_workflows"))
):
    """Create new approval action"""
    action = ApprovalAction(
        **action_data.dict(),
        action_by=current_user.id
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action

@router.get("/approval-actions", response_model=List[ApprovalActionResponse])
async def get_approval_actions(
    record_id: Optional[int] = Query(None),
    action_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get all approval actions"""
    query = db.query(ApprovalAction)
    
    if record_id:
        query = query.filter(ApprovalAction.record_id == record_id)
    if action_type:
        query = query.filter(ApprovalAction.action_type == action_type)
    
    return query.order_by(ApprovalAction.action_date.desc()).all()

# Workflow Statistics
@router.get("/workflow-statistics")
async def get_workflow_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get workflow statistics"""
    query = db.query(ApprovalRecord)
    
    if date_from:
        query = query.filter(ApprovalRecord.initiated_date >= date_from)
    if date_to:
        query = query.filter(ApprovalRecord.initiated_date <= date_to)
    
    total_records = query.count()
    pending_records = query.filter(ApprovalRecord.status == WorkflowStatus.PENDING).count()
    approved_records = query.filter(ApprovalRecord.status == WorkflowStatus.APPROVED).count()
    rejected_records = query.filter(ApprovalRecord.status == WorkflowStatus.REJECTED).count()
    
    return {
        "total_records": total_records,
        "pending_records": pending_records,
        "approved_records": approved_records,
        "rejected_records": rejected_records,
        "approval_rate": (approved_records / total_records * 100) if total_records > 0 else 0
    }

# My Pending Approvals
@router.get("/my-pending-approvals", response_model=List[ApprovalRecordResponse])
async def get_my_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get current user's pending approvals"""
    # This would need to be implemented based on user roles and workflow logic
    # For now, returning empty list as placeholder
    return []

# Workflow Dashboard
@router.get("/workflow-dashboard")
async def get_workflow_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_workflows"))
):
    """Get workflow dashboard data"""
    return {
        "message": "Workflow dashboard data",
        "status": "success"
    }