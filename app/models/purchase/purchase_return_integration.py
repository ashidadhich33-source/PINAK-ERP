# backend/app/models/purchase/purchase_return_integration.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import BaseModel
import enum

class ReturnStatus(str, enum.Enum):
    """Purchase return status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PROCESSED = "processed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ReturnType(str, enum.Enum):
    """Purchase return type enumeration"""
    DEFECTIVE = "defective"
    EXCESS = "excess"
    WRONG_ITEM = "wrong_item"
    DAMAGED = "damaged"
    QUALITY_ISSUE = "quality_issue"
    SPECIFICATION_MISMATCH = "specification_mismatch"
    EXPIRED = "expired"
    CUSTOMER_RETURN = "customer_return"

class ReturnReason(str, enum.Enum):
    """Purchase return reason enumeration"""
    DEFECTIVE_PRODUCT = "defective_product"
    WRONG_SPECIFICATION = "wrong_specification"
    DAMAGED_IN_TRANSIT = "damaged_in_transit"
    EXCESS_QUANTITY = "excess_quantity"
    QUALITY_ISSUE = "quality_issue"
    EXPIRED_PRODUCT = "expired_product"
    CUSTOMER_COMPLAINT = "customer_complaint"
    SUPPLIER_ERROR = "supplier_error"

# Phase 1: Accounting Integration Models
class PurchaseReturnAccounting(BaseModel):
    """Purchase return accounting integration"""
    __tablename__ = "purchase_return_accounting"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    debit_account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    credit_account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(12, 2), nullable=False)
    accounting_date = Column(Date, nullable=False)
    is_reversed = Column(Boolean, default=False)
    reversal_date = Column(Date, nullable=True)
    reversal_reason = Column(String(200), nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    journal_entry = relationship("JournalEntry")
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
    
    def __repr__(self):
        return f"<PurchaseReturnAccounting(return_id={self.return_id}, amount={self.amount})>"

class PurchaseReturnPayment(BaseModel):
    """Purchase return payment processing"""
    __tablename__ = "purchase_return_payment"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, bank_transfer, cheque, credit_note
    payment_reference = Column(String(100), nullable=True)
    payment_amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    cheque_number = Column(String(50), nullable=True)
    cheque_date = Column(Date, nullable=True)
    payment_status = Column(String(20), default='pending')  # pending, completed, failed, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    bank_account = relationship("BankAccount")
    
    def __repr__(self):
        return f"<PurchaseReturnPayment(return_id={self.return_id}, amount={self.payment_amount})>"

class PurchaseReturnAnalytic(BaseModel):
    """Purchase return analytic accounting"""
    __tablename__ = "purchase_return_analytic"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    analytic_plan_id = Column(Integer, ForeignKey('analytic_plan.id'), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)
    distribution_type = Column(String(50), default='amount')  # amount, percentage
    notes = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    analytic_account = relationship("AnalyticAccount")
    analytic_plan = relationship("AnalyticPlan")
    
    def __repr__(self):
        return f"<PurchaseReturnAnalytic(return_id={self.return_id}, amount={self.amount})>"

# Phase 2: Indian Localization Models
class PurchaseReturnGST(BaseModel):
    """Purchase return GST integration"""
    __tablename__ = "purchase_return_gst"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    gst_number = Column(String(15), nullable=True)
    place_of_supply = Column(String(100), nullable=True)
    place_of_supply_type = Column(String(20), default='intrastate')  # intrastate, interstate
    cgst_rate = Column(Numeric(5, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), default=0)
    igst_rate = Column(Numeric(5, 2), default=0)
    cess_rate = Column(Numeric(5, 2), default=0)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    cess_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    is_reverse_charge = Column(Boolean, default=False)
    reverse_charge_amount = Column(Numeric(10, 2), default=0)
    composition_scheme = Column(Boolean, default=False)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnGST(return_id={self.return_id}, gst_amount={self.total_gst_amount})>"

class PurchaseReturnEInvoice(BaseModel):
    """Purchase return E-invoice integration"""
    __tablename__ = "purchase_return_einvoice"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    irn = Column(String(100), nullable=True)
    ack_no = Column(String(100), nullable=True)
    ack_date = Column(DateTime, nullable=True)
    qr_code = Column(Text, nullable=True)
    e_invoice_status = Column(String(20), default='pending')  # pending, generated, cancelled
    gst_portal_status = Column(String(20), nullable=True)
    portal_upload_date = Column(DateTime, nullable=True)
    portal_response = Column(Text, nullable=True)
    cancellation_reason = Column(String(200), nullable=True)
    cancellation_date = Column(DateTime, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnEInvoice(return_id={self.return_id}, irn='{self.irn}')>"

class PurchaseReturnEWaybill(BaseModel):
    """Purchase return E-waybill integration"""
    __tablename__ = "purchase_return_ewaybill"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    eway_bill_no = Column(String(50), nullable=True)
    eway_bill_date = Column(DateTime, nullable=True)
    valid_upto = Column(DateTime, nullable=True)
    distance_km = Column(Numeric(8, 2), nullable=True)
    vehicle_number = Column(String(20), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_mobile = Column(String(15), nullable=True)
    transport_mode = Column(String(20), default='road')  # road, rail, air, ship
    eway_bill_status = Column(String(20), default='pending')  # pending, generated, cancelled
    cancellation_reason = Column(String(200), nullable=True)
    cancellation_date = Column(DateTime, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnEWaybill(return_id={self.return_id}, eway_no='{self.eway_bill_no}')>"

class PurchaseReturnTDS(BaseModel):
    """Purchase return TDS integration"""
    __tablename__ = "purchase_return_tds"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    tds_section = Column(String(10), nullable=True)
    tds_rate = Column(Numeric(5, 2), default=0)
    tds_amount = Column(Numeric(10, 2), default=0)
    tds_certificate_no = Column(String(50), nullable=True)
    tds_certificate_date = Column(Date, nullable=True)
    tds_deposit_date = Column(Date, nullable=True)
    tds_challan_no = Column(String(50), nullable=True)
    tds_return_filed = Column(Boolean, default=False)
    tds_return_date = Column(Date, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnTDS(return_id={self.return_id}, tds_amount={self.tds_amount})>"

class PurchaseReturnTCS(BaseModel):
    """Purchase return TCS integration"""
    __tablename__ = "purchase_return_tcs"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    tcs_section = Column(String(10), nullable=True)
    tcs_rate = Column(Numeric(5, 2), default=0)
    tcs_amount = Column(Numeric(10, 2), default=0)
    tcs_collection_date = Column(Date, nullable=True)
    tcs_challan_no = Column(String(50), nullable=True)
    tcs_return_filed = Column(Boolean, default=False)
    tcs_return_date = Column(Date, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnTCS(return_id={self.return_id}, tcs_amount={self.tcs_amount})>"

# Phase 3: Advanced Features Models
class PurchaseReturnWorkflow(BaseModel):
    """Purchase return workflow management"""
    __tablename__ = "purchase_return_workflow"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    workflow_type = Column(String(50), nullable=False)  # approval, notification, escalation
    workflow_step = Column(String(50), nullable=False)
    assigned_to = Column(Integer, ForeignKey('user.id'), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, rejected, escalated
    comments = Column(Text, nullable=True)
    priority = Column(String(10), default='medium')  # low, medium, high, urgent
    escalation_level = Column(Integer, default=0)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    assigned_user = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnWorkflow(return_id={self.return_id}, step='{self.workflow_step}')>"

class PurchaseReturnDocument(BaseModel):
    """Purchase return document management"""
    __tablename__ = "purchase_return_document"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    document_type = Column(String(50), nullable=False)  # return_note, receipt, invoice, quality_report
    document_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    upload_date = Column(DateTime, default=func.now())
    uploaded_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_encrypted = Column(Boolean, default=False)
    encryption_key = Column(String(100), nullable=True)
    version = Column(String(20), default='1.0')
    is_latest = Column(Boolean, default=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnDocument(return_id={self.return_id}, type='{self.document_type}')>"

class PurchaseReturnAudit(BaseModel):
    """Purchase return audit trail"""
    __tablename__ = "purchase_return_audit"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    action_type = Column(String(50), nullable=False)  # created, updated, approved, rejected, processed
    action_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    action_date = Column(DateTime, default=func.now())
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    comments = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    action_user = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnAudit(return_id={self.return_id}, action='{self.action_type}')>"

class PurchaseReturnNotification(BaseModel):
    """Purchase return notification management"""
    __tablename__ = "purchase_return_notification"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, push, whatsapp
    recipient_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    recipient_email = Column(String(100), nullable=True)
    recipient_phone = Column(String(15), nullable=True)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    sent_date = Column(DateTime, nullable=True)
    delivery_status = Column(String(20), default='pending')  # pending, sent, delivered, failed
    delivery_response = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    recipient = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnNotification(return_id={self.return_id}, type='{self.notification_type}')>"

# Phase 4: Enhanced Integration Models
class PurchaseReturnInventory(BaseModel):
    """Purchase return inventory integration"""
    __tablename__ = "purchase_return_inventory"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=False)
    quantity_returned = Column(Numeric(10, 2), nullable=False)
    quantity_received = Column(Numeric(10, 2), default=0)
    stock_adjustment = Column(Boolean, default=True)
    adjustment_type = Column(String(20), default='reduce')  # reduce, increase
    serial_numbers = Column(Text, nullable=True)  # JSON array of serial numbers
    batch_numbers = Column(Text, nullable=True)  # JSON array of batch numbers
    expiry_dates = Column(Text, nullable=True)  # JSON array of expiry dates
    quality_status = Column(String(20), default='good')  # good, defective, damaged, expired
    condition_notes = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    warehouse = relationship("Warehouse")
    
    def __repr__(self):
        return f"<PurchaseReturnInventory(return_id={self.return_id}, item_id={self.item_id})>"

class PurchaseReturnSupplier(BaseModel):
    """Purchase return supplier integration"""
    __tablename__ = "purchase_return_supplier"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    credit_note_issued = Column(Boolean, default=False)
    credit_note_number = Column(String(100), nullable=True)
    credit_note_date = Column(Date, nullable=True)
    credit_note_amount = Column(Numeric(12, 2), nullable=True)
    supplier_acknowledgment = Column(Boolean, default=False)
    acknowledgment_date = Column(DateTime, nullable=True)
    supplier_notes = Column(Text, nullable=True)
    return_authorization = Column(String(100), nullable=True)
    return_authorization_date = Column(Date, nullable=True)
    supplier_rating = Column(Integer, nullable=True)  # 1-5 rating
    feedback = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    supplier = relationship("Supplier")
    
    def __repr__(self):
        return f"<PurchaseReturnSupplier(return_id={self.return_id}, supplier_id={self.supplier_id})>"

class PurchaseReturnPerformance(BaseModel):
    """Purchase return performance optimization"""
    __tablename__ = "purchase_return_performance"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    processing_time_ms = Column(Integer, nullable=True)
    memory_usage_mb = Column(Integer, nullable=True)
    cpu_usage_percent = Column(Numeric(5, 2), nullable=True)
    database_queries = Column(Integer, nullable=True)
    cache_hit_rate = Column(Numeric(5, 2), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    throughput_per_second = Column(Numeric(10, 2), nullable=True)
    error_rate = Column(Numeric(5, 2), nullable=True)
    optimization_suggestions = Column(Text, nullable=True)
    performance_score = Column(Integer, nullable=True)  # 1-100 score
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnPerformance(return_id={self.return_id}, score={self.performance_score})>"

class PurchaseReturnUserExperience(BaseModel):
    """Purchase return user experience tracking"""
    __tablename__ = "purchase_return_user_experience"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    satisfaction_score = Column(Integer, nullable=True)  # 1-5 rating
    ease_of_use_score = Column(Integer, nullable=True)  # 1-5 rating
    interface_rating = Column(Integer, nullable=True)  # 1-5 rating
    responsiveness_rating = Column(Integer, nullable=True)  # 1-5 rating
    accessibility_score = Column(Integer, nullable=True)  # 1-5 rating
    completion_time_minutes = Column(Numeric(8, 2), nullable=True)
    error_count = Column(Integer, default=0)
    help_requests = Column(Integer, default=0)
    feedback = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    user = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnUserExperience(return_id={self.return_id}, user_id={self.user_id})>"

class PurchaseReturnSync(BaseModel):
    """Purchase return real-time synchronization"""
    __tablename__ = "purchase_return_sync"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    sync_type = Column(String(50), nullable=False)  # inventory, accounting, supplier, analytics
    sync_status = Column(String(20), default='pending')  # pending, syncing, completed, failed
    sync_start_time = Column(DateTime, nullable=True)
    sync_end_time = Column(DateTime, nullable=True)
    sync_duration_ms = Column(Integer, nullable=True)
    records_synced = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_sync_time = Column(DateTime, nullable=True)
    sync_frequency = Column(String(20), default='realtime')  # realtime, hourly, daily, weekly
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseReturnSync(return_id={self.return_id}, type='{self.sync_type}')>"

class PurchaseReturnAnalytics(BaseModel):
    """Purchase return analytics integration"""
    __tablename__ = "purchase_return_analytics"
    
    return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=False)
    analytics_provider = Column(String(50), nullable=False)  # google_analytics, mixpanel, custom
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text, nullable=True)  # JSON data
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    return_record = relationship("PurchaseReturn")
    user = relationship("User")
    
    def __repr__(self):
        return f"<PurchaseReturnAnalytics(return_id={self.return_id}, provider='{self.analytics_provider}')>"