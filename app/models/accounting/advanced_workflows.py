# backend/app/models/accounting/advanced_workflows.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class WorkflowStatus(PyEnum):
    """Workflow status types"""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class ApprovalLevel(PyEnum):
    """Approval level types"""
    SINGLE = "single"
    MULTI_LEVEL = "multi_level"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"

class DocumentType(PyEnum):
    """Document types for workflows"""
    JOURNAL_ENTRY = "journal_entry"
    PAYMENT = "payment"
    INVOICE = "invoice"
    BILL = "bill"
    EXPENSE = "expense"
    PURCHASE_ORDER = "purchase_order"
    SALES_ORDER = "sales_order"
    BANK_STATEMENT = "bank_statement"
    CUSTOM = "custom"

class ApprovalWorkflow(BaseModel):
    """Approval workflows for accounting documents"""
    __tablename__ = "approval_workflow"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    approval_level = Column(Enum(ApprovalLevel), default=ApprovalLevel.SINGLE, nullable=False)
    is_active = Column(Boolean, default=True)
    is_mandatory = Column(Boolean, default=True)
    auto_approve_amount = Column(Numeric(15, 2), nullable=True)  # Auto-approve below this amount
    requires_justification = Column(Boolean, default=False)
    notification_settings = Column(JSON, nullable=True)  # Email, SMS, in-app notifications
    
    # Relationships
    approval_steps = relationship("ApprovalStep", back_populates="workflow", cascade="all, delete-orphan")
    approval_records = relationship("ApprovalRecord", back_populates="workflow")
    
    def __repr__(self):
        return f"<ApprovalWorkflow(name='{self.name}', type='{self.document_type}')>"

class ApprovalStep(BaseModel):
    """Individual steps in approval workflow"""
    __tablename__ = "approval_step"
    
    workflow_id = Column(Integer, ForeignKey('approval_workflow.id'), nullable=False)
    step_name = Column(String(100), nullable=False)
    step_order = Column(Integer, nullable=False)
    approver_role = Column(String(100), nullable=False)  # Role-based approval
    approver_user_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # Specific user approval
    approver_group_id = Column(Integer, ForeignKey('user_group.id'), nullable=True)  # Group-based approval
    is_mandatory = Column(Boolean, default=True)
    can_delegate = Column(Boolean, default=False)
    max_delegation_level = Column(Integer, default=1)
    timeout_hours = Column(Integer, nullable=True)  # Auto-escalation timeout
    escalation_user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    conditions = Column(JSON, nullable=True)  # Conditional approval logic
    
    # Relationships
    workflow = relationship("ApprovalWorkflow", back_populates="approval_steps")
    approver_user = relationship("User", foreign_keys=[approver_user_id])
    escalation_user = relationship("User", foreign_keys=[escalation_user_id])
    approval_actions = relationship("ApprovalAction", back_populates="step")
    
    def __repr__(self):
        return f"<ApprovalStep(name='{self.step_name}', order={self.step_order})>"

class ApprovalRecord(BaseModel):
    """Approval records for documents"""
    __tablename__ = "approval_record"
    
    document_id = Column(Integer, nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    workflow_id = Column(Integer, ForeignKey('approval_workflow.id'), nullable=False)
    current_step_id = Column(Integer, ForeignKey('approval_step.id'), nullable=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)
    initiated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    initiated_date = Column(DateTime, default=datetime.now, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    priority = Column(String(20), default='normal')  # low, normal, high, urgent
    due_date = Column(DateTime, nullable=True)
    comments = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional workflow data
    
    # Relationships
    workflow = relationship("ApprovalWorkflow", back_populates="approval_records")
    current_step = relationship("ApprovalStep", foreign_keys=[current_step_id])
    initiated_by_user = relationship("User", foreign_keys=[initiated_by])
    approval_actions = relationship("ApprovalAction", back_populates="record")
    
    def __repr__(self):
        return f"<ApprovalRecord(document_id={self.document_id}, status='{self.status}')>"

class ApprovalAction(BaseModel):
    """Individual approval actions"""
    __tablename__ = "approval_action"
    
    record_id = Column(Integer, ForeignKey('approval_record.id'), nullable=False)
    step_id = Column(Integer, ForeignKey('approval_step.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # approve, reject, delegate, escalate, comment
    action_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    action_date = Column(DateTime, default=datetime.now, nullable=False)
    comments = Column(Text, nullable=True)
    delegated_to = Column(Integer, ForeignKey('user.id'), nullable=True)
    escalation_reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional action data
    
    # Relationships
    record = relationship("ApprovalRecord", back_populates="approval_actions")
    step = relationship("ApprovalStep", back_populates="approval_actions")
    action_by_user = relationship("User", foreign_keys=[action_by])
    delegated_to_user = relationship("User", foreign_keys=[delegated_to])
    
    def __repr__(self):
        return f"<ApprovalAction(type='{self.action_type}', by={self.action_by})>"

class EmailTemplate(BaseModel):
    """Email templates for automation"""
    __tablename__ = "email_template"
    
    name = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    template_type = Column(String(50), nullable=False)  # approval, rejection, reminder, notification
    workflow_id = Column(Integer, ForeignKey('approval_workflow.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    variables = Column(JSON, nullable=True)  # Available template variables
    
    # Relationships
    workflow = relationship("ApprovalWorkflow")
    email_automations = relationship("EmailAutomation", back_populates="template")
    
    def __repr__(self):
        return f"<EmailTemplate(name='{self.name}', type='{self.template_type}')>"

class EmailAutomation(BaseModel):
    """Email automation rules"""
    __tablename__ = "email_automation"
    
    name = Column(String(100), nullable=False)
    trigger_event = Column(String(100), nullable=False)  # workflow_started, step_completed, overdue, etc.
    template_id = Column(Integer, ForeignKey('email_template.id'), nullable=False)
    recipient_type = Column(String(50), nullable=False)  # initiator, approver, manager, custom
    recipient_emails = Column(JSON, nullable=True)  # Custom recipient emails
    conditions = Column(JSON, nullable=True)  # Conditional sending
    delay_minutes = Column(Integer, default=0)  # Delay before sending
    is_active = Column(Boolean, default=True)
    
    # Relationships
    template = relationship("EmailTemplate", back_populates="email_automations")
    
    def __repr__(self):
        return f"<EmailAutomation(name='{self.name}', trigger='{self.trigger_event}')>"

class DocumentAttachment(BaseModel):
    """Document attachments"""
    __tablename__ = "document_attachment"
    
    document_id = Column(Integer, nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    uploaded_date = Column(DateTime, default=datetime.now, nullable=False)
    is_public = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # File tags for organization
    
    # Relationships
    uploaded_by_user = relationship("User", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<DocumentAttachment(name='{self.file_name}', type='{self.document_type}')>"

class AuditTrail(BaseModel):
    """Complete audit trail for all transactions"""
    __tablename__ = "audit_trail"
    
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete, approve, reject
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    changed_date = Column(DateTime, default=datetime.now, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional audit data
    
    # Relationships
    changed_by_user = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<AuditTrail(table='{self.table_name}', action='{self.action}')>"

class WorkflowNotification(BaseModel):
    """Workflow notifications"""
    __tablename__ = "workflow_notification"
    
    record_id = Column(Integer, ForeignKey('approval_record.id'), nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, in_app, push
    recipient_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    sent_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(20), default='sent')  # sent, delivered, failed, bounced
    delivery_attempts = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    record = relationship("ApprovalRecord")
    recipient = relationship("User", foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f"<WorkflowNotification(type='{self.notification_type}', status='{self.status}')>"