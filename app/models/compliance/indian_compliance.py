# backend/app/models/compliance/indian_compliance.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Decimal, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from decimal import Decimal

from ..base import BaseModel

# GST Registration Model
class GSTRegistration(BaseModel):
    """GST Registration details for companies"""
    __tablename__ = "gst_registrations"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    gst_number = Column(String(15), unique=True, nullable=False)
    registration_type = Column(String(20), nullable=False)  # regular, composition, casual, non-resident
    registration_date = Column(Date, nullable=False)
    business_name = Column(String(200), nullable=False)
    business_address = Column(Text, nullable=False)
    business_type = Column(String(50), nullable=False)  # manufacturer, trader, service provider
    pan_number = Column(String(10), nullable=False)
    aadhar_number = Column(String(12), nullable=True)
    mobile_number = Column(String(10), nullable=True)
    email = Column(String(100), nullable=True)
    state_code = Column(String(2), nullable=False)
    is_active = Column(Boolean, default=True)
    suspension_date = Column(Date, nullable=True)
    cancellation_date = Column(Date, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="gst_registrations")
    gst_returns = relationship("GSTReturn", back_populates="gst_registration")
    gst_payments = relationship("GSTPayment", back_populates="gst_registration")

# GST Return Model
class GSTReturn(BaseModel):
    """GST Return filing details"""
    __tablename__ = "gst_returns"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    gst_registration_id = Column(Integer, ForeignKey("gst_registrations.id"), nullable=False)
    return_period = Column(String(7), nullable=False)  # YYYY-MM format
    return_type = Column(String(10), nullable=False)  # GSTR-1, GSTR-3B, GSTR-9, etc.
    gst_number = Column(String(15), nullable=False)
    filing_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft")  # draft, filed, accepted, rejected
    
    # Financial details
    total_sales = Column(Decimal(15, 2), default=0)
    total_purchases = Column(Decimal(15, 2), default=0)
    output_tax = Column(Decimal(15, 2), default=0)
    input_tax = Column(Decimal(15, 2), default=0)
    net_tax = Column(Decimal(15, 2), default=0)
    interest_amount = Column(Decimal(15, 2), default=0)
    penalty_amount = Column(Decimal(15, 2), default=0)
    total_payable = Column(Decimal(15, 2), default=0)
    
    # Filing details
    acknowledgment_number = Column(String(20), nullable=True)
    filing_reference = Column(String(50), nullable=True)
    filed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    filed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="gst_returns")
    gst_registration = relationship("GSTRegistration", back_populates="gst_returns")
    gst_payments = relationship("GSTPayment", back_populates="gst_return")

# GST Payment Model
class GSTPayment(BaseModel):
    """GST Payment details"""
    __tablename__ = "gst_payments"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    gst_registration_id = Column(Integer, ForeignKey("gst_registrations.id"), nullable=False)
    gst_return_id = Column(Integer, ForeignKey("gst_returns.id"), nullable=True)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Decimal(15, 2), nullable=False)
    payment_mode = Column(String(20), nullable=False)  # online, offline, challan
    payment_reference = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, failed
    
    # Relationships
    company = relationship("Company", back_populates="gst_payments")
    gst_registration = relationship("GSTRegistration", back_populates="gst_payments")
    gst_return = relationship("GSTReturn", back_populates="gst_payments")

# GST Filing Model
class GSTFiling(BaseModel):
    """GST Filing tracking"""
    __tablename__ = "gst_filings"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    gst_return_id = Column(Integer, ForeignKey("gst_returns.id"), nullable=False)
    filing_type = Column(String(20), nullable=False)  # original, revised, late
    filing_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    error_details = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    company = relationship("Company")
    gst_return = relationship("GSTReturn")

# TDS Return Model
class TDSReturn(BaseModel):
    """TDS Return filing details"""
    __tablename__ = "tds_returns"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    return_period = Column(String(7), nullable=False)  # YYYY-MM format
    return_type = Column(String(10), nullable=False)  # 24Q, 26Q, 27Q, etc.
    pan_number = Column(String(10), nullable=False)
    filing_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft")
    
    # Financial details
    total_tds_deducted = Column(Decimal(15, 2), default=0)
    total_tds_deposited = Column(Decimal(15, 2), default=0)
    interest_amount = Column(Decimal(15, 2), default=0)
    penalty_amount = Column(Decimal(15, 2), default=0)
    total_payable = Column(Decimal(15, 2), default=0)
    
    # Filing details
    acknowledgment_number = Column(String(20), nullable=True)
    filed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    filed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="tds_returns")
    tds_payments = relationship("TDSPayment", back_populates="tds_return")

# TDS Payment Model
class TDSPayment(BaseModel):
    """TDS Payment details"""
    __tablename__ = "tds_payments"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tds_return_id = Column(Integer, ForeignKey("tds_returns.id"), nullable=True)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Decimal(15, 2), nullable=False)
    payment_mode = Column(String(20), nullable=False)
    payment_reference = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")
    
    # Relationships
    company = relationship("Company", back_populates="tds_payments")
    tds_return = relationship("TDSReturn", back_populates="tds_payments")

# TDS Filing Model
class TDSFiling(BaseModel):
    """TDS Filing tracking"""
    __tablename__ = "tds_filings"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tds_return_id = Column(Integer, ForeignKey("tds_returns.id"), nullable=False)
    filing_type = Column(String(20), nullable=False)
    filing_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    error_details = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company")
    tds_return = relationship("TDSReturn")

# TCS Return Model
class TCSReturn(BaseModel):
    """TCS Return filing details"""
    __tablename__ = "tcs_returns"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    return_period = Column(String(7), nullable=False)
    return_type = Column(String(10), nullable=False)
    pan_number = Column(String(10), nullable=False)
    filing_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="draft")
    
    # Financial details
    total_tcs_collected = Column(Decimal(15, 2), default=0)
    total_tcs_deposited = Column(Decimal(15, 2), default=0)
    interest_amount = Column(Decimal(15, 2), default=0)
    penalty_amount = Column(Decimal(15, 2), default=0)
    total_payable = Column(Decimal(15, 2), default=0)
    
    # Filing details
    acknowledgment_number = Column(String(20), nullable=True)
    filed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    filed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="tcs_returns")
    tcs_payments = relationship("TCSPayment", back_populates="tcs_return")

# TCS Payment Model
class TCSPayment(BaseModel):
    """TCS Payment details"""
    __tablename__ = "tcs_payments"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tcs_return_id = Column(Integer, ForeignKey("tcs_returns.id"), nullable=True)
    payment_date = Column(Date, nullable=False)
    payment_amount = Column(Decimal(15, 2), nullable=False)
    payment_mode = Column(String(20), nullable=False)
    payment_reference = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")
    
    # Relationships
    company = relationship("Company", back_populates="tcs_payments")
    tcs_return = relationship("TCSReturn", back_populates="tcs_payments")

# TCS Filing Model
class TCSFiling(BaseModel):
    """TCS Filing tracking"""
    __tablename__ = "tcs_filings"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    tcs_return_id = Column(Integer, ForeignKey("tcs_returns.id"), nullable=False)
    filing_type = Column(String(20), nullable=False)
    filing_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")
    error_details = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company")
    tcs_return = relationship("TCSReturn")

# E-Invoice Model
class EInvoice(BaseModel):
    """E-Invoice details"""
    __tablename__ = "e_invoices"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    invoice_id = Column(Integer, nullable=False)  # Reference to sales invoice
    invoice_number = Column(String(50), nullable=False)
    invoice_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_gst = Column(String(15), nullable=True)
    total_amount = Column(Decimal(15, 2), nullable=False)
    tax_amount = Column(Decimal(15, 2), nullable=False)
    
    # E-Invoice specific fields
    irn = Column(String(64), nullable=True)  # Invoice Registration Number
    qr_code = Column(Text, nullable=True)
    status = Column(String(20), default="draft")  # draft, generated, uploaded, accepted, rejected
    ack_number = Column(String(50), nullable=True)
    ack_date = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="e_invoices")
    customer = relationship("Customer")
    e_invoice_items = relationship("EInvoiceItem", back_populates="e_invoice")

# E-Invoice Item Model
class EInvoiceItem(BaseModel):
    """E-Invoice line items"""
    __tablename__ = "e_invoice_items"
    
    e_invoice_id = Column(Integer, ForeignKey("e_invoices.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    item_name = Column(String(200), nullable=False)
    hsn_code = Column(String(8), nullable=True)
    quantity = Column(Decimal(10, 3), nullable=False)
    unit_price = Column(Decimal(15, 2), nullable=False)
    total_price = Column(Decimal(15, 2), nullable=False)
    tax_rate = Column(Decimal(5, 2), default=0)
    tax_amount = Column(Decimal(15, 2), default=0)
    
    # Relationships
    e_invoice = relationship("EInvoice", back_populates="e_invoice_items")
    item = relationship("Item")

# E-Waybill Model
class EWaybill(BaseModel):
    """E-Waybill details"""
    __tablename__ = "e_waybills"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    waybill_number = Column(String(50), nullable=False)
    waybill_date = Column(Date, nullable=False)
    invoice_id = Column(Integer, nullable=True)  # Reference to sales invoice
    invoice_number = Column(String(50), nullable=True)
    invoice_date = Column(Date, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_gst = Column(String(15), nullable=True)
    total_amount = Column(Decimal(15, 2), nullable=False)
    
    # E-Waybill specific fields
    ewb_number = Column(String(12), nullable=True)  # E-Waybill Number
    status = Column(String(20), default="draft")  # draft, generated, active, expired, cancelled
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    distance = Column(Integer, nullable=True)  # Distance in kilometers
    transport_mode = Column(String(20), nullable=True)  # road, rail, air, ship
    vehicle_number = Column(String(20), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_mobile = Column(String(10), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="e_waybills")
    customer = relationship("Customer")
    e_waybill_items = relationship("EWaybillItem", back_populates="e_waybill")

# E-Waybill Item Model
class EWaybillItem(BaseModel):
    """E-Waybill line items"""
    __tablename__ = "e_waybill_items"
    
    e_waybill_id = Column(Integer, ForeignKey("e_waybills.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    item_name = Column(String(200), nullable=False)
    hsn_code = Column(String(8), nullable=True)
    quantity = Column(Decimal(10, 3), nullable=False)
    unit_price = Column(Decimal(15, 2), nullable=False)
    total_price = Column(Decimal(15, 2), nullable=False)
    
    # Relationships
    e_waybill = relationship("EWaybill", back_populates="e_waybill_items")
    item = relationship("Item")

# Compliance Settings Model
class ComplianceSettings(BaseModel):
    """Compliance settings for companies"""
    __tablename__ = "compliance_settings"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, unique=True)
    
    # GST Settings
    gst_auto_filing = Column(Boolean, default=False)
    gst_auto_payment = Column(Boolean, default=False)
    gst_notification_days = Column(Integer, default=7)
    
    # TDS Settings
    tds_auto_filing = Column(Boolean, default=False)
    tds_auto_payment = Column(Boolean, default=False)
    tds_notification_days = Column(Integer, default=7)
    
    # TCS Settings
    tcs_auto_filing = Column(Boolean, default=False)
    tcs_auto_payment = Column(Boolean, default=False)
    tcs_notification_days = Column(Integer, default=7)
    
    # E-Invoice Settings
    e_invoice_auto_generation = Column(Boolean, default=False)
    e_invoice_threshold = Column(Decimal(15, 2), default=50000)
    
    # E-Waybill Settings
    e_waybill_auto_generation = Column(Boolean, default=False)
    e_waybill_threshold = Column(Decimal(15, 2), default=50000)
    
    # Relationships
    company = relationship("Company", back_populates="compliance_settings")

# Compliance Log Model
class ComplianceLog(BaseModel):
    """Compliance activity log"""
    __tablename__ = "compliance_logs"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    compliance_type = Column(String(20), nullable=False)  # gst, tds, tcs, e_invoice, e_waybill
    action = Column(String(50), nullable=False)  # filed, paid, generated, etc.
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)  # success, failed, pending
    message = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="compliance_logs")

# Compliance Alert Model
class ComplianceAlert(BaseModel):
    """Compliance alerts and notifications"""
    __tablename__ = "compliance_alerts"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    alert_type = Column(String(20), nullable=False)  # due_date, filing, payment, error
    compliance_type = Column(String(20), nullable=False)  # gst, tds, tcs, e_invoice, e_waybill
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    due_date = Column(Date, nullable=True)
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="compliance_alerts")
    acknowledged_user = relationship("User")