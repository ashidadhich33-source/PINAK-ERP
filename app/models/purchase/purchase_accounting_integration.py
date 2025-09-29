# backend/app/models/purchase/purchase_accounting_integration.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class JournalEntryStatus(PyEnum):
    """Journal Entry Status"""
    PENDING = "pending"
    CREATED = "created"
    POSTED = "posted"
    CANCELLED = "cancelled"

class PaymentStatus(PyEnum):
    """Payment Status"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PurchaseJournalEntry(BaseModel):
    """Link Purchases to Journal Entries"""
    __tablename__ = "purchase_journal_entry"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Journal Entry Reference
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=False)
    
    # Integration Details
    entry_type = Column(String(50), nullable=False)  # invoice, order, return, payment, receipt
    entry_status = Column(Enum(JournalEntryStatus), default=JournalEntryStatus.PENDING)
    total_amount = Column(Numeric(15, 2), nullable=False)
    tax_amount = Column(Numeric(15, 2), default=0)
    discount_amount = Column(Numeric(15, 2), default=0)
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Accounting Details
    debit_account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=True)  # Purchase account
    credit_account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=True)  # Supplier account
    tax_account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=True)  # Tax account
    
    # Additional Information
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional integration data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    journal_entry = relationship("JournalEntry")
    debit_account = relationship("ChartOfAccount", foreign_keys=[debit_account_id])
    credit_account = relationship("ChartOfAccount", foreign_keys=[credit_account_id])
    tax_account = relationship("ChartOfAccount", foreign_keys=[tax_account_id])
    
    def __repr__(self):
        return f"<PurchaseJournalEntry(purchase_id={self.purchase_invoice_id}, journal_id={self.journal_entry_id})>"

class PurchasePayment(BaseModel):
    """Link Purchases to Payments"""
    __tablename__ = "purchase_payment"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    
    # Payment Reference
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    payment_method_id = Column(Integer, ForeignKey('payment_method.id'), nullable=True)
    
    # Payment Details
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_reference = Column(String(100), nullable=True)
    payment_notes = Column(Text, nullable=True)
    
    # Payment Terms
    due_date = Column(Date, nullable=True)
    discount_days = Column(Integer, nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    discount_amount = Column(Numeric(15, 2), default=0)
    
    # Additional Information
    metadata = Column(JSON, nullable=True)  # Additional payment data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    payment = relationship("Payment")
    bank_account = relationship("BankAccount")
    payment_method = relationship("PaymentMethod")
    
    def __repr__(self):
        return f"<PurchasePayment(purchase_id={self.purchase_invoice_id}, amount={self.payment_amount})>"

class PurchaseAnalytic(BaseModel):
    """Link Purchases to Analytic Accounting"""
    __tablename__ = "purchase_analytic"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Analytic Reference
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    
    # Analytic Details
    amount = Column(Numeric(15, 2), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)  # If percentage-based distribution
    distribution_method = Column(String(50), nullable=True)  # manual, percentage, equal, weighted
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional analytic data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    analytic_account = relationship("AnalyticAccount")
    
    def __repr__(self):
        return f"<PurchaseAnalytic(purchase_id={self.purchase_invoice_id}, analytic_id={self.analytic_account_id})>"

class PurchaseWorkflow(BaseModel):
    """Link Purchases to Workflows"""
    __tablename__ = "purchase_workflow"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Workflow Reference
    approval_record_id = Column(Integer, ForeignKey('approval_record.id'), nullable=True)
    workflow_id = Column(Integer, ForeignKey('approval_workflow.id'), nullable=True)
    
    # Workflow Details
    workflow_type = Column(String(50), nullable=False)  # approval, notification, automation
    workflow_status = Column(String(50), default='pending')  # pending, approved, rejected, completed
    initiated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    initiated_date = Column(DateTime, default=datetime.now, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    
    # Additional Information
    workflow_data = Column(JSON, nullable=True)  # Workflow-specific data
    notes = Column(Text, nullable=True)
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    approval_record = relationship("ApprovalRecord")
    workflow = relationship("ApprovalWorkflow")
    initiated_by_user = relationship("User", foreign_keys=[initiated_by])
    
    def __repr__(self):
        return f"<PurchaseWorkflow(purchase_id={self.purchase_invoice_id}, type='{self.workflow_type}')>"

class PurchaseDocument(BaseModel):
    """Link Purchases to Document Management"""
    __tablename__ = "purchase_document"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Document Reference
    document_attachment_id = Column(Integer, ForeignKey('document_attachment.id'), nullable=False)
    
    # Document Details
    document_type = Column(String(50), nullable=False)  # invoice, order, receipt, contract, other
    document_name = Column(String(255), nullable=False)
    document_description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Additional Information
    metadata = Column(JSON, nullable=True)  # Additional document data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    document_attachment = relationship("DocumentAttachment")
    
    def __repr__(self):
        return f"<PurchaseDocument(purchase_id={self.purchase_invoice_id}, type='{self.document_type}')>"

class PurchaseAuditTrail(BaseModel):
    """Link Purchases to Audit Trails"""
    __tablename__ = "purchase_audit_trail"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Audit Reference
    audit_trail_id = Column(Integer, ForeignKey('audit_trail.id'), nullable=False)
    
    # Audit Details
    action_type = Column(String(50), nullable=False)  # create, update, delete, approve, reject
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    changed_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    changed_date = Column(DateTime, default=datetime.now, nullable=False)
    
    # Additional Information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    reason = Column(Text, nullable=True)
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    audit_trail = relationship("AuditTrail")
    changed_by_user = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<PurchaseAuditTrail(purchase_id={self.purchase_invoice_id}, action='{self.action_type}')>"