# backend/app/models/purchase/purchase_advanced_features_integration.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..base import BaseModel

class WorkflowStatus(PyEnum):
    """Workflow Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DocumentType(PyEnum):
    """Document Type"""
    INVOICE = "invoice"
    ORDER = "order"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    QUOTATION = "quotation"
    BILL = "bill"
    RETURN = "return"
    OTHER = "other"

class ReportType(PyEnum):
    """Report Type"""
    PURCHASE_REPORT = "purchase_report"
    GST_REPORT = "gst_report"
    PAYMENT_REPORT = "payment_report"
    SUPPLIER_REPORT = "supplier_report"
    PRODUCT_REPORT = "product_report"
    CUSTOM = "custom"

class PurchaseAdvancedWorkflow(BaseModel):
    """Link Purchases to Advanced Workflows"""
    __tablename__ = "purchase_advanced_workflow"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Workflow Reference
    approval_workflow_id = Column(Integer, ForeignKey('approval_workflow.id'), nullable=False)
    approval_record_id = Column(Integer, ForeignKey('approval_record.id'), nullable=True)
    
    # Workflow Details
    workflow_type = Column(String(50), nullable=False)  # approval, notification, automation, escalation
    workflow_status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    initiated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    initiated_date = Column(DateTime, default=datetime.now, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Workflow Configuration
    auto_approve = Column(Boolean, default=False)
    require_approval = Column(Boolean, default=True)
    approval_levels = Column(Integer, default=1)
    current_level = Column(Integer, default=1)
    escalation_enabled = Column(Boolean, default=False)
    escalation_days = Column(Integer, nullable=True)
    
    # Additional Information
    workflow_data = Column(JSON, nullable=True)  # Workflow-specific data
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional workflow data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    approval_workflow = relationship("ApprovalWorkflow")
    approval_record = relationship("ApprovalRecord")
    initiated_by_user = relationship("User", foreign_keys=[initiated_by])
    
    def __repr__(self):
        return f"<PurchaseAdvancedWorkflow(purchase_id={self.purchase_invoice_id}, type='{self.workflow_type}')>"

class PurchaseDocumentManagement(BaseModel):
    """Link Purchases to Document Management"""
    __tablename__ = "purchase_document_management"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Document Reference
    document_attachment_id = Column(Integer, ForeignKey('document_attachment.id'), nullable=False)
    
    # Document Details
    document_type = Column(Enum(DocumentType), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_extension = Column(String(10), nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Document Properties
    is_required = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    version = Column(String(20), default='1.0')
    checksum = Column(String(64), nullable=True)  # File integrity check
    
    # Document Status
    upload_status = Column(String(20), default='pending')  # pending, uploaded, failed, processing
    upload_date = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Additional Information
    tags = Column(JSON, nullable=True)  # Document tags
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional document data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    document_attachment = relationship("DocumentAttachment")
    
    def __repr__(self):
        return f"<PurchaseDocumentManagement(purchase_id={self.purchase_invoice_id}, type='{self.document_type}')>"

class PurchaseAdvancedReporting(BaseModel):
    """Link Purchases to Advanced Reporting"""
    __tablename__ = "purchase_advanced_reporting"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Report Reference
    report_template_id = Column(Integer, ForeignKey('report_template.id'), nullable=True)
    report_instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=True)
    
    # Report Details
    report_type = Column(Enum(ReportType), nullable=False)
    report_name = Column(String(255), nullable=False)
    report_description = Column(Text, nullable=True)
    report_parameters = Column(JSON, nullable=True)  # Report parameters
    report_filters = Column(JSON, nullable=True)  # Report filters
    
    # Report Configuration
    is_scheduled = Column(Boolean, default=False)
    schedule_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, quarterly, yearly
    schedule_time = Column(String(10), nullable=True)  # HH:MM format
    schedule_day = Column(String(20), nullable=True)  # For weekly/monthly schedules
    next_run_date = Column(DateTime, nullable=True)
    
    # Report Status
    report_status = Column(String(20), default='pending')  # pending, running, completed, failed
    last_run_date = Column(DateTime, nullable=True)
    last_run_status = Column(String(20), nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Report Output
    output_format = Column(String(20), default='pdf')  # pdf, excel, csv, json, xml
    output_path = Column(String(500), nullable=True)
    output_size = Column(Integer, nullable=True)
    email_recipients = Column(JSON, nullable=True)  # Email recipients
    
    # Additional Information
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional report data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    report_template = relationship("ReportTemplate")
    report_instance = relationship("ReportInstance")
    
    def __repr__(self):
        return f"<PurchaseAdvancedReporting(purchase_id={self.purchase_invoice_id}, type='{self.report_type}')>"

class PurchaseAuditTrailAdvanced(BaseModel):
    """Link Purchases to Advanced Audit Trails"""
    __tablename__ = "purchase_audit_trail_advanced"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Audit Reference
    audit_trail_id = Column(Integer, ForeignKey('audit_trail.id'), nullable=False)
    
    # Audit Details
    action_type = Column(String(50), nullable=False)  # create, update, delete, approve, reject, view, export, print
    action_category = Column(String(50), nullable=True)  # data_change, workflow, document, report, system
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_fields = Column(JSON, nullable=True)  # List of changed fields
    
    # User and Session Information
    changed_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    changed_date = Column(DateTime, default=datetime.now, nullable=False)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional Context
    reason = Column(Text, nullable=True)
    approval_required = Column(Boolean, default=False)
    approval_status = Column(String(20), nullable=True)  # pending, approved, rejected
    approval_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # System Information
    module_name = Column(String(50), nullable=True)
    feature_name = Column(String(50), nullable=True)
    business_rule = Column(String(100), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional audit data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    audit_trail = relationship("AuditTrail")
    changed_by_user = relationship("User", foreign_keys=[changed_by])
    approval_by_user = relationship("User", foreign_keys=[approval_by])
    
    def __repr__(self):
        return f"<PurchaseAuditTrailAdvanced(purchase_id={self.purchase_invoice_id}, action='{self.action_type}')>"

class PurchaseNotification(BaseModel):
    """Link Purchases to Notifications"""
    __tablename__ = "purchase_notification"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Notification Reference
    workflow_notification_id = Column(Integer, ForeignKey('workflow_notification.id'), nullable=True)
    
    # Notification Details
    notification_type = Column(String(50), nullable=False)  # email, sms, push, in_app, webhook
    notification_subject = Column(String(255), nullable=True)
    notification_message = Column(Text, nullable=False)
    notification_priority = Column(String(20), default='medium')  # low, medium, high, urgent
    
    # Recipients
    recipient_user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_roles = Column(JSON, nullable=True)  # List of roles to notify
    
    # Notification Status
    notification_status = Column(String(20), default='pending')  # pending, sent, delivered, failed, read
    sent_date = Column(DateTime, nullable=True)
    delivered_date = Column(DateTime, nullable=True)
    read_date = Column(DateTime, nullable=True)
    
    # Delivery Information
    delivery_attempts = Column(Integer, default=0)
    delivery_status = Column(String(20), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional notification data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    workflow_notification = relationship("WorkflowNotification")
    recipient_user = relationship("User", foreign_keys=[recipient_user_id])
    
    def __repr__(self):
        return f"<PurchaseNotification(purchase_id={self.purchase_invoice_id}, type='{self.notification_type}')>"

class PurchaseDashboard(BaseModel):
    """Link Purchases to Dashboard Widgets"""
    __tablename__ = "purchase_dashboard"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Dashboard Reference
    dashboard_widget_id = Column(Integer, ForeignKey('dashboard_widget.id'), nullable=False)
    
    # Widget Details
    widget_type = Column(String(50), nullable=False)  # chart, table, metric, kpi, gauge, map
    widget_title = Column(String(255), nullable=False)
    widget_description = Column(Text, nullable=True)
    widget_config = Column(JSON, nullable=True)  # Widget configuration
    widget_data = Column(JSON, nullable=True)  # Widget data
    
    # Widget Position and Size
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    
    # Widget Status
    is_visible = Column(Boolean, default=True)
    is_refreshable = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=300)  # Seconds
    last_refresh = Column(DateTime, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    model_metadata = Column(JSON, nullable=True)  # Additional widget data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    dashboard_widget = relationship("DashboardWidget")
    
    def __repr__(self):
        return f"<PurchaseDashboard(purchase_id={self.purchase_invoice_id}, widget='{self.widget_title}')>"