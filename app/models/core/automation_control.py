"""
Automation Control Models
Provides configurable automation settings for all modules
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum


class AutomationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class AutomationTriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"


class AutomationActionType(str, enum.Enum):
    CREATE_RECORD = "create_record"
    UPDATE_RECORD = "update_record"
    DELETE_RECORD = "delete_record"
    SEND_NOTIFICATION = "send_notification"
    GENERATE_REPORT = "generate_report"
    EXECUTE_SCRIPT = "execute_script"
    CALL_API = "call_api"


class AutomationSetting(Base):
    """Automation settings for modules"""
    __tablename__ = "automation_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    setting_name = Column(String(100), nullable=False)
    setting_value = Column(Text)
    is_enabled = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    approval_workflow = Column(JSON)
    conditions = Column(JSON)
    exceptions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_settings")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])


class AutomationWorkflow(Base):
    """Automation workflows"""
    __tablename__ = "automation_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    module = Column(String(50), nullable=False, index=True)
    trigger_type = Column(Enum(AutomationTriggerType), nullable=False)
    trigger_conditions = Column(JSON)
    actions = Column(JSON, nullable=False)
    approval_required = Column(Boolean, default=False)
    approval_workflow = Column(JSON)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    conditions = Column(JSON)
    exceptions = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_workflows")
    created_by_user = relationship("User", foreign_keys=[created_by])
    rules = relationship("AutomationRule", back_populates="workflow")
    triggers = relationship("AutomationTrigger", back_populates="workflow")
    approvals = relationship("AutomationApproval", back_populates="workflow")


class AutomationRule(Base):
    """Automation rules"""
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rule_type = Column(String(50), nullable=False)
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_rules")
    workflow = relationship("AutomationWorkflow", back_populates="rules")
    created_by_user = relationship("User", foreign_keys=[created_by])


class AutomationTrigger(Base):
    """Automation triggers"""
    __tablename__ = "automation_triggers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    trigger_type = Column(Enum(AutomationTriggerType), nullable=False)
    trigger_conditions = Column(JSON)
    schedule = Column(JSON)
    event_source = Column(String(100))
    event_type = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_triggers")
    workflow = relationship("AutomationWorkflow", back_populates="triggers")
    created_by_user = relationship("User", foreign_keys=[created_by])


class AutomationAction(Base):
    """Automation actions"""
    __tablename__ = "automation_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    action_type = Column(Enum(AutomationActionType), nullable=False)
    action_data = Column(JSON, nullable=False)
    sequence = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_actions")
    workflow = relationship("AutomationWorkflow")
    created_by_user = relationship("User", foreign_keys=[created_by])


class AutomationCondition(Base):
    """Automation conditions"""
    __tablename__ = "automation_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    condition_type = Column(String(50), nullable=False)
    field = Column(String(100), nullable=False)
    operator = Column(String(20), nullable=False)
    value = Column(Text)
    logical_operator = Column(String(10), default="AND")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_conditions")
    workflow = relationship("AutomationWorkflow")
    created_by_user = relationship("User", foreign_keys=[created_by])


class AutomationApproval(Base):
    """Automation approvals"""
    __tablename__ = "automation_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey("automation_workflows.id"), nullable=False)
    workflow_name = Column(String(200), nullable=False)
    trigger_data = Column(JSON)
    status = Column(Enum(AutomationStatus), default=AutomationStatus.PENDING)
    requested_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    comments = Column(Text)
    execution_result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    
    # Relationships
    company = relationship("Company", back_populates="automation_approvals")
    workflow = relationship("AutomationWorkflow", back_populates="approvals")
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])


class AutomationLog(Base):
    """Automation execution logs"""
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    action = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(JSON)
    execution_time = Column(Float)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    company = relationship("Company", back_populates="automation_logs")
    created_by_user = relationship("User", foreign_keys=[created_by])
    exceptions = relationship("AutomationException", back_populates="log")
    rollbacks = relationship("AutomationRollback", back_populates="log")


class AutomationException(Base):
    """Automation exceptions"""
    __tablename__ = "automation_exceptions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    log_id = Column(Integer, ForeignKey("automation_logs.id"), nullable=False)
    exception_type = Column(String(100), nullable=False)
    exception_message = Column(Text)
    exception_data = Column(JSON)
    severity = Column(String(20), default="medium")
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="automation_exceptions")
    log = relationship("AutomationLog", back_populates="exceptions")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])


class AutomationRollback(Base):
    """Automation rollbacks"""
    __tablename__ = "automation_rollbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    automation_log_id = Column(Integer, ForeignKey("automation_logs.id"), nullable=False)
    rollback_reason = Column(Text, nullable=False)
    rollback_data = Column(JSON)
    rollback_actions = Column(JSON)
    status = Column(String(20), default="pending")
    execution_result = Column(JSON)
    executed_by = Column(Integer, ForeignKey("users.id"))
    executed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="automation_rollbacks")
    log = relationship("AutomationLog", back_populates="rollbacks")
    executed_by_user = relationship("User", foreign_keys=[executed_by])


class AutomationAudit(Base):
    """Automation audit trail"""
    __tablename__ = "automation_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    old_values = Column(JSON)
    new_values = Column(JSON)
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    company = relationship("Company", back_populates="automation_audits")
    changed_by_user = relationship("User", foreign_keys=[changed_by])