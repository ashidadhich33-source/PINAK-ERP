"""
Automation Control Schemas
Pydantic schemas for automation control
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, date
from enum import Enum


class AutomationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class AutomationTriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"


class AutomationActionType(str, Enum):
    CREATE_RECORD = "create_record"
    UPDATE_RECORD = "update_record"
    DELETE_RECORD = "delete_record"
    SEND_NOTIFICATION = "send_notification"
    GENERATE_REPORT = "generate_report"
    EXECUTE_SCRIPT = "execute_script"
    CALL_API = "call_api"


# Base schemas
class AutomationSettingBase(BaseModel):
    module: str = Field(..., description="Module name")
    setting_name: str = Field(..., description="Setting name")
    setting_value: Optional[str] = Field(None, description="Setting value")
    is_enabled: bool = Field(True, description="Is setting enabled")
    requires_approval: bool = Field(False, description="Requires approval")
    approval_workflow: Optional[Dict] = Field(None, description="Approval workflow")
    conditions: Optional[Dict] = Field(None, description="Conditions")
    exceptions: Optional[Dict] = Field(None, description="Exceptions")


class AutomationSettingCreate(AutomationSettingBase):
    pass


class AutomationSettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    is_enabled: Optional[bool] = None
    requires_approval: Optional[bool] = None
    approval_workflow: Optional[Dict] = None
    conditions: Optional[Dict] = None
    exceptions: Optional[Dict] = None


class AutomationSettingResponse(AutomationSettingBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationWorkflowBase(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    module: str = Field(..., description="Module name")
    trigger_type: AutomationTriggerType = Field(..., description="Trigger type")
    trigger_conditions: Optional[Dict] = Field(None, description="Trigger conditions")
    actions: Dict = Field(..., description="Workflow actions")
    approval_required: bool = Field(False, description="Requires approval")
    approval_workflow: Optional[Dict] = Field(None, description="Approval workflow")
    priority: int = Field(1, description="Priority")
    conditions: Optional[Dict] = Field(None, description="Conditions")
    exceptions: Optional[Dict] = Field(None, description="Exceptions")


class AutomationWorkflowCreate(AutomationWorkflowBase):
    pass


class AutomationWorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_conditions: Optional[Dict] = None
    actions: Optional[Dict] = None
    approval_required: Optional[bool] = None
    approval_workflow: Optional[Dict] = None
    priority: Optional[int] = None
    conditions: Optional[Dict] = None
    exceptions: Optional[Dict] = None
    is_active: Optional[bool] = None


class AutomationWorkflowResponse(AutomationWorkflowBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationRuleBase(BaseModel):
    workflow_id: int = Field(..., description="Workflow ID")
    name: str = Field(..., description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    rule_type: str = Field(..., description="Rule type")
    conditions: Dict = Field(..., description="Rule conditions")
    actions: Dict = Field(..., description="Rule actions")
    priority: int = Field(1, description="Priority")


class AutomationRuleCreate(AutomationRuleBase):
    pass


class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rule_type: Optional[str] = None
    conditions: Optional[Dict] = None
    actions: Optional[Dict] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class AutomationRuleResponse(AutomationRuleBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationTriggerBase(BaseModel):
    workflow_id: int = Field(..., description="Workflow ID")
    name: str = Field(..., description="Trigger name")
    description: Optional[str] = Field(None, description="Trigger description")
    trigger_type: AutomationTriggerType = Field(..., description="Trigger type")
    trigger_conditions: Optional[Dict] = Field(None, description="Trigger conditions")
    schedule: Optional[Dict] = Field(None, description="Schedule")
    event_source: Optional[str] = Field(None, description="Event source")
    event_type: Optional[str] = Field(None, description="Event type")


class AutomationTriggerCreate(AutomationTriggerBase):
    pass


class AutomationTriggerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[AutomationTriggerType] = None
    trigger_conditions: Optional[Dict] = None
    schedule: Optional[Dict] = None
    event_source: Optional[str] = None
    event_type: Optional[str] = None
    is_active: Optional[bool] = None


class AutomationTriggerResponse(AutomationTriggerBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationActionBase(BaseModel):
    workflow_id: int = Field(..., description="Workflow ID")
    name: str = Field(..., description="Action name")
    description: Optional[str] = Field(None, description="Action description")
    action_type: AutomationActionType = Field(..., description="Action type")
    action_data: Dict = Field(..., description="Action data")
    sequence: int = Field(1, description="Sequence")


class AutomationActionCreate(AutomationActionBase):
    pass


class AutomationActionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[AutomationActionType] = None
    action_data: Optional[Dict] = None
    sequence: Optional[int] = None
    is_active: Optional[bool] = None


class AutomationActionResponse(AutomationActionBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationConditionBase(BaseModel):
    workflow_id: int = Field(..., description="Workflow ID")
    name: str = Field(..., description="Condition name")
    description: Optional[str] = Field(None, description="Condition description")
    condition_type: str = Field(..., description="Condition type")
    field: str = Field(..., description="Field name")
    operator: str = Field(..., description="Operator")
    value: Optional[str] = Field(None, description="Value")
    logical_operator: str = Field("AND", description="Logical operator")


class AutomationConditionCreate(AutomationConditionBase):
    pass


class AutomationConditionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_type: Optional[str] = None
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    logical_operator: Optional[str] = None
    is_active: Optional[bool] = None


class AutomationConditionResponse(AutomationConditionBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationApprovalBase(BaseModel):
    workflow_id: int = Field(..., description="Workflow ID")
    workflow_name: str = Field(..., description="Workflow name")
    trigger_data: Optional[Dict] = Field(None, description="Trigger data")
    status: AutomationStatus = Field(AutomationStatus.PENDING, description="Status")
    requested_by: Optional[int] = Field(None, description="Requested by")
    approved_by: Optional[int] = Field(None, description="Approved by")
    comments: Optional[str] = Field(None, description="Comments")


class AutomationApprovalCreate(AutomationApprovalBase):
    pass


class AutomationApprovalUpdate(BaseModel):
    status: Optional[AutomationStatus] = None
    approved_by: Optional[int] = None
    comments: Optional[str] = None
    execution_result: Optional[Dict] = None


class AutomationApprovalResponse(AutomationApprovalBase):
    id: int
    company_id: int
    created_at: datetime
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AutomationLogBase(BaseModel):
    module: str = Field(..., description="Module name")
    action: str = Field(..., description="Action name")
    status: str = Field(..., description="Status")
    details: Optional[Dict] = Field(None, description="Details")
    execution_time: Optional[float] = Field(None, description="Execution time")
    error_message: Optional[str] = Field(None, description="Error message")


class AutomationLogCreate(AutomationLogBase):
    pass


class AutomationLogResponse(AutomationLogBase):
    id: int
    company_id: int
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True


class AutomationExceptionBase(BaseModel):
    log_id: int = Field(..., description="Log ID")
    exception_type: str = Field(..., description="Exception type")
    exception_message: Optional[str] = Field(None, description="Exception message")
    exception_data: Optional[Dict] = Field(None, description="Exception data")
    severity: str = Field("medium", description="Severity")
    is_resolved: bool = Field(False, description="Is resolved")
    resolved_by: Optional[int] = Field(None, description="Resolved by")
    resolved_at: Optional[datetime] = Field(None, description="Resolved at")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


class AutomationExceptionCreate(AutomationExceptionBase):
    pass


class AutomationExceptionUpdate(BaseModel):
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    exception_data: Optional[Dict] = None
    severity: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class AutomationExceptionResponse(AutomationExceptionBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AutomationRollbackBase(BaseModel):
    automation_log_id: int = Field(..., description="Automation log ID")
    rollback_reason: str = Field(..., description="Rollback reason")
    rollback_data: Optional[Dict] = Field(None, description="Rollback data")
    rollback_actions: Optional[Dict] = Field(None, description="Rollback actions")
    status: str = Field("pending", description="Status")
    execution_result: Optional[Dict] = Field(None, description="Execution result")
    executed_by: Optional[int] = Field(None, description="Executed by")
    executed_at: Optional[datetime] = Field(None, description="Executed at")


class AutomationRollbackCreate(AutomationRollbackBase):
    pass


class AutomationRollbackUpdate(BaseModel):
    rollback_reason: Optional[str] = None
    rollback_data: Optional[Dict] = None
    rollback_actions: Optional[Dict] = None
    status: Optional[str] = None
    execution_result: Optional[Dict] = None
    executed_by: Optional[int] = None
    executed_at: Optional[datetime] = None


class AutomationRollbackResponse(AutomationRollbackBase):
    id: int
    company_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AutomationAuditBase(BaseModel):
    entity_type: str = Field(..., description="Entity type")
    entity_id: int = Field(..., description="Entity ID")
    action: str = Field(..., description="Action")
    old_values: Optional[Dict] = Field(None, description="Old values")
    new_values: Optional[Dict] = Field(None, description="New values")
    changed_by: Optional[int] = Field(None, description="Changed by")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")


class AutomationAuditResponse(AutomationAuditBase):
    id: int
    company_id: int
    changed_at: datetime
    
    class Config:
        from_attributes = True


# Response schemas
class AutomationSettingsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


class AutomationWorkflowResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


class AutomationApprovalsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str


class AutomationLogsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str


class AutomationAnalyticsResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


class AutomationRollbackResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


class AutomationIntegrationStatusResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


class AutomationWorkflowAutomationResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str