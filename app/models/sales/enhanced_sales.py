# backend/app/models/enhanced_sales.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class PlaceOfSupplyType(PyEnum):
    """Place of Supply Types for Indian GST"""
    INTRA_STATE = "intra_state"  # Within same state
    INTER_STATE = "inter_state"  # Between different states
    EXPORT = "export"  # Export of goods/services
    IMPORT = "import"  # Import of goods/services

class SaleChallan(BaseModel):
    """Sale challan management"""
    __tablename__ = "sale_challan"
    
    challan_number = Column(String(100), unique=True, nullable=False)
    challan_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    challan_type = Column(String(50), default='delivery')  # delivery, pickup, service
    delivery_address = Column(Text, nullable=True)
    delivery_date = Column(Date, nullable=True)
    delivery_time = Column(String(20), nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    total_quantity = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default='draft')  # draft, confirmed, delivered, cancelled
    notes = Column(Text, nullable=True)
    
    # Accounting Integration Fields
    journal_entry_created = Column(Boolean, default=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    payment_terms_id = Column(Integer, ForeignKey('payment_term.id'), nullable=True)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    staff = relationship("Staff")
    challan_items = relationship("SaleChallanItem", back_populates="challan_record")
    
    # Accounting Integration Relationships
    journal_entry = relationship("JournalEntry")
    payment_terms = relationship("PaymentTerm")
    analytic_account = relationship("AnalyticAccount")
    sale_journal_entries = relationship("SaleJournalEntry", foreign_keys="SaleJournalEntry.sale_challan_id")
    sale_payments = relationship("SalePayment", foreign_keys="SalePayment.sale_invoice_id")
    sale_analytics = relationship("SaleAnalytic", foreign_keys="SaleAnalytic.sale_challan_id")
    sale_workflows = relationship("SaleWorkflow", foreign_keys="SaleWorkflow.sale_challan_id")
    sale_documents = relationship("SaleDocument", foreign_keys="SaleDocument.sale_challan_id")
    sale_audit_trails = relationship("SaleAuditTrail", foreign_keys="SaleAuditTrail.sale_challan_id")
    
    def __repr__(self):
        return f"<SaleChallan(number='{self.challan_number}', customer_id={self.customer_id})>"

class SaleChallanItem(BaseModel):
    """Individual items in sale challan"""
    __tablename__ = "sale_challan_item"
    
    challan_id = Column(Integer, ForeignKey('sale_challan.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    delivered_quantity = Column(Numeric(10, 2), default=0)
    pending_quantity = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    challan_record = relationship("SaleChallan", back_populates="challan_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<SaleChallanItem(item_id={self.item_id}, quantity={self.quantity})>"

class BillSeries(BaseModel):
    """Bill series management for different document types"""
    __tablename__ = "bill_series"
    
    series_name = Column(String(100), nullable=False)
    series_code = Column(String(50), unique=True, nullable=False)
    document_type = Column(String(50), nullable=False)  # sale, purchase, sale_return, purchase_return
    prefix = Column(String(20), nullable=False)
    suffix = Column(String(20), nullable=True)
    starting_number = Column(Integer, default=1)
    current_number = Column(Integer, default=0)
    number_length = Column(Integer, default=6)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    bills = relationship("SaleBill", back_populates="bill_series")
    purchase_bills = relationship("PurchaseBill", back_populates="bill_series")
    
    def __repr__(self):
        return f"<BillSeries(name='{self.series_name}', code='{self.series_code}')>"
    
    def generate_number(self):
        """Generate next bill number"""
        self.current_number += 1
        number_str = str(self.current_number).zfill(self.number_length)
        return f"{self.prefix}{number_str}{self.suffix or ''}"

class PaymentMode(BaseModel):
    """Payment mode management"""
    __tablename__ = "payment_mode"
    
    mode_name = Column(String(100), nullable=False)
    mode_code = Column(String(50), unique=True, nullable=False)
    mode_type = Column(String(50), nullable=False)  # cash, card, bank_transfer, upi, wallet, cheque
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    requires_reference = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    minimum_amount = Column(Numeric(10, 2), nullable=True)
    maximum_amount = Column(Numeric(10, 2), nullable=True)
    processing_fee_percentage = Column(Numeric(5, 2), default=0)
    processing_fee_fixed = Column(Numeric(10, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    payments = relationship("Payment", back_populates="payment_mode")
    
    def __repr__(self):
        return f"<PaymentMode(name='{self.mode_name}', code='{self.mode_code}')>"

class Staff(BaseModel):
    """Staff management"""
    __tablename__ = "staff"
    
    employee_id = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    date_of_joining = Column(Date, nullable=False)
    date_of_leaving = Column(Date, nullable=True)
    designation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    salary = Column(Numeric(10, 2), nullable=True)
    commission_percentage = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    user = relationship("User")
    sales = relationship("SaleBill", back_populates="staff")
    challans = relationship("SaleChallan", back_populates="staff")
    targets = relationship("StaffTarget", back_populates="staff")
    
    def __repr__(self):
        return f"<Staff(name='{self.first_name} {self.last_name}', employee_id='{self.employee_id}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class StaffTarget(BaseModel):
    """Staff target management"""
    __tablename__ = "staff_target"
    
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    target_period = Column(String(20), nullable=False)  # daily, weekly, monthly, yearly
    target_date = Column(Date, nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    achieved_amount = Column(Numeric(12, 2), default=0)
    target_quantity = Column(Numeric(10, 2), nullable=True)
    achieved_quantity = Column(Numeric(10, 2), default=0)
    commission_rate = Column(Numeric(5, 2), default=0)
    bonus_amount = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default='active')  # active, achieved, failed
    notes = Column(Text, nullable=True)
    
    # Relationships
    staff = relationship("Staff", back_populates="targets")
    
    def __repr__(self):
        return f"<StaffTarget(staff_id={self.staff_id}, period='{self.target_period}')>"
    
    @property
    def achievement_percentage(self):
        if self.target_amount > 0:
            return (self.achieved_amount / self.target_amount) * 100
        return 0

class SaleReturn(BaseModel):
    """Sale return management"""
    __tablename__ = "sale_return"
    
    return_number = Column(String(100), unique=True, nullable=False)
    return_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    original_bill_id = Column(Integer, ForeignKey('sale_bill.id'), nullable=True)
    original_bill_number = Column(String(100), nullable=True)
    original_bill_date = Column(Date, nullable=True)
    return_reason = Column(String(200), nullable=True)
    return_type = Column(String(50), default='defective')  # defective, excess, wrong_item, damaged
    total_quantity = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default='draft')  # draft, confirmed, processed, cancelled
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    staff = relationship("Staff")
    original_bill = relationship("SaleBill")
    return_items = relationship("SaleReturnItem", back_populates="return_record")
    
    def __repr__(self):
        return f"<SaleReturn(number='{self.return_number}', customer_id={self.customer_id})>"

class SaleReturnItem(BaseModel):
    """Individual items in sale return"""
    __tablename__ = "sale_return_item"
    
    return_id = Column(Integer, ForeignKey('sale_return.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    original_bill_item_id = Column(Integer, ForeignKey('sale_bill_item.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), nullable=True)
    return_reason = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    return_record = relationship("SaleReturn", back_populates="return_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    original_bill_item = relationship("SaleBillItem")
    
    def __repr__(self):
        return f"<SaleReturnItem(item_id={self.item_id}, quantity={self.quantity})>"

class SaleOrder(BaseModel):
    """Sale order management"""
    __tablename__ = "sale_order"
    
    order_number = Column(String(100), unique=True, nullable=False)
    order_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    expected_delivery_date = Column(Date, nullable=True)
    order_status = Column(String(20), default='draft')  # draft, confirmed, partial, completed, cancelled
    total_quantity = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    staff = relationship("Staff")
    order_items = relationship("SaleOrderItem", back_populates="order_record")
    
    def __repr__(self):
        return f"<SaleOrder(number='{self.order_number}', customer_id={self.customer_id})>"

class SaleOrderItem(BaseModel):
    """Individual items in sale order"""
    __tablename__ = "sale_order_item"
    
    order_id = Column(Integer, ForeignKey('sale_order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    delivered_quantity = Column(Numeric(10, 2), default=0)
    pending_quantity = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    order_record = relationship("SaleOrder", back_populates="order_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<SaleOrderItem(item_id={self.item_id}, quantity={self.quantity})>"

class SaleInvoice(BaseModel):
    """Sale invoice management with Indian GST compliance"""
    __tablename__ = "sale_invoice"
    
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('sale_bill.id'), nullable=True)
    invoice_type = Column(String(50), default='regular')  # regular, credit_note, debit_note
    
    # Indian GST Compliance Fields
    gstin = Column(String(15), nullable=True)  # Customer GSTIN
    place_of_supply = Column(Enum(PlaceOfSupplyType), nullable=True)
    supplier_state_code = Column(String(2), nullable=True)
    recipient_state_code = Column(String(2), nullable=True)
    
    # Amount Fields
    subtotal_amount = Column(Numeric(12, 2), nullable=False)  # Amount before GST
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), default=0)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)  # Final amount including GST
    
    # E-invoice Fields
    irn = Column(String(64), nullable=True)  # Invoice Reference Number
    qr_code = Column(Text, nullable=True)  # QR code data
    e_invoice_status = Column(String(20), nullable=True)  # generated, uploaded, accepted, rejected
    
    # E-waybill Fields
    eway_bill_no = Column(String(50), nullable=True)
    eway_bill_date = Column(Date, nullable=True)
    eway_bill_valid_upto = Column(DateTime, nullable=True)
    
    # TDS Fields
    tds_applicable = Column(Boolean, default=False)
    tds_rate = Column(Numeric(5, 2), nullable=True)
    tds_amount = Column(Numeric(10, 2), default=0)
    tds_section = Column(String(10), nullable=True)
    
    # Status and Notes
    status = Column(String(20), default='draft')  # draft, confirmed, paid, cancelled
    notes = Column(Text, nullable=True)
    
    # Accounting Integration Fields
    journal_entry_created = Column(Boolean, default=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    payment_terms_id = Column(Integer, ForeignKey('payment_term.id'), nullable=True)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=True)
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    payment_method_id = Column(Integer, ForeignKey('payment_method.id'), nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    bill = relationship("SaleBill")
    invoice_items = relationship("SaleInvoiceItem", back_populates="invoice_record")
    
    # Accounting Integration Relationships
    journal_entry = relationship("JournalEntry")
    payment_terms = relationship("PaymentTerm")
    analytic_account = relationship("AnalyticAccount")
    bank_account = relationship("BankAccount")
    payment_method = relationship("PaymentMethod")
    sale_journal_entries = relationship("SaleJournalEntry", foreign_keys="SaleJournalEntry.sale_invoice_id")
    sale_payments = relationship("SalePayment", foreign_keys="SalePayment.sale_invoice_id")
    sale_analytics = relationship("SaleAnalytic", foreign_keys="SaleAnalytic.sale_invoice_id")
    sale_workflows = relationship("SaleWorkflow", foreign_keys="SaleWorkflow.sale_invoice_id")
    sale_documents = relationship("SaleDocument", foreign_keys="SaleDocument.sale_invoice_id")
    sale_audit_trails = relationship("SaleAuditTrail", foreign_keys="SaleAuditTrail.sale_invoice_id")
    
    # Indian Localization Integration Relationships
    sale_gst = relationship("SaleGST", foreign_keys="SaleGST.sale_invoice_id")
    sale_e_invoice = relationship("SaleEInvoice", foreign_keys="SaleEInvoice.sale_invoice_id")
    sale_e_waybill = relationship("SaleEWaybill", foreign_keys="SaleEWaybill.sale_invoice_id")
    sale_tds = relationship("SaleTDS", foreign_keys="SaleTDS.sale_invoice_id")
    sale_tcs = relationship("SaleTCS", foreign_keys="SaleTCS.sale_invoice_id")
    sale_indian_banking = relationship("SaleIndianBanking", foreign_keys="SaleIndianBanking.sale_invoice_id")
    sale_indian_geography = relationship("SaleIndianGeography", foreign_keys="SaleIndianGeography.sale_invoice_id")
    
    # Advanced Features Integration Relationships
    sale_advanced_workflows = relationship("SaleAdvancedWorkflow", foreign_keys="SaleAdvancedWorkflow.sale_invoice_id")
    sale_document_management = relationship("SaleDocumentManagement", foreign_keys="SaleDocumentManagement.sale_invoice_id")
    sale_advanced_reporting = relationship("SaleAdvancedReporting", foreign_keys="SaleAdvancedReporting.sale_invoice_id")
    sale_audit_trail_advanced = relationship("SaleAuditTrailAdvanced", foreign_keys="SaleAuditTrailAdvanced.sale_invoice_id")
    sale_notifications = relationship("SaleNotification", foreign_keys="SaleNotification.sale_invoice_id")
    sale_dashboards = relationship("SaleDashboard", foreign_keys="SaleDashboard.sale_invoice_id")
    
    # Enhanced Integration Relationships
    sale_inventory_integration = relationship("SaleInventoryIntegration", foreign_keys="SaleInventoryIntegration.sale_invoice_id")
    sale_customer_integration = relationship("SaleCustomerIntegration", foreign_keys="SaleCustomerIntegration.sale_invoice_id")
    sale_performance_optimization = relationship("SalePerformanceOptimization", foreign_keys="SalePerformanceOptimization.sale_invoice_id")
    sale_user_experience = relationship("SaleUserExperience", foreign_keys="SaleUserExperience.sale_invoice_id")
    sale_real_time_sync = relationship("SaleRealTimeSync", foreign_keys="SaleRealTimeSync.sale_invoice_id")
    sale_analytics_integration = relationship("SaleAnalyticsIntegration", foreign_keys="SaleAnalyticsIntegration.sale_invoice_id")
    
    def __repr__(self):
        return f"<SaleInvoice(number='{self.invoice_number}', customer_id={self.customer_id})>"

class SaleInvoiceItem(BaseModel):
    """Individual items in sale invoice with Indian GST compliance"""
    __tablename__ = "sale_invoice_item"
    
    invoice_id = Column(Integer, ForeignKey('sale_invoice.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    
    # Basic Item Information
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal_amount = Column(Numeric(10, 2), nullable=False)  # Amount before GST
    
    # HSN/SAC Information
    hsn_code = Column(String(8), nullable=True)
    sac_code = Column(String(6), nullable=True)
    
    # GST Information
    gst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(10, 2), nullable=True)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(10, 2), nullable=True)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(10, 2), nullable=True)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(10, 2), nullable=True)
    total_gst_amount = Column(Numeric(10, 2), nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)  # Final amount including GST
    
    # Unit of Measure
    unit_of_measure = Column(String(10), nullable=True)  # NOS, KGS, LTR, etc.
    
    # Relationships
    invoice_record = relationship("SaleInvoice", back_populates="invoice_items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<SaleInvoiceItem(item_id={self.item_id}, quantity={self.quantity})>"

class POSSession(BaseModel):
    """POS session management"""
    __tablename__ = "pos_session"
    
    session_number = Column(String(100), unique=True, nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    opening_cash = Column(Numeric(10, 2), default=0)
    closing_cash = Column(Numeric(10, 2), nullable=True)
    total_sales = Column(Numeric(12, 2), default=0)
    total_transactions = Column(Integer, default=0)
    status = Column(String(20), default='active')  # active, closed
    notes = Column(Text, nullable=True)
    
    # Relationships
    staff = relationship("Staff")
    transactions = relationship("SaleBill", back_populates="pos_session")
    
    def __repr__(self):
        return f"<POSSession(number='{self.session_number}', staff_id={self.staff_id})>"