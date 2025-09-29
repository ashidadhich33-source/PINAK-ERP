# backend/app/models/l10n_in/e_invoicing.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from .base import BaseModel

class EInvoiceStatus(PyEnum):
    """E-invoice Status"""
    DRAFT = "draft"
    GENERATED = "generated"
    UPLOADED = "uploaded"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class EInvoiceType(PyEnum):
    """E-invoice Types"""
    B2B = "B2B"  # Business to Business
    B2C = "B2C"  # Business to Consumer
    B2CL = "B2CL"  # Business to Consumer Large
    EXPORT = "EXPORT"  # Export
    SEZ = "SEZ"  # Special Economic Zone
    DEEMED_EXPORT = "DEEMED_EXPORT"  # Deemed Export

class EInvoice(BaseModel):
    """E-invoice Model for Indian GST Compliance"""
    __tablename__ = "e_invoice"
    
    # Basic Information
    invoice_number = Column(String(50), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    invoice_type = Column(Enum(EInvoiceType), nullable=False)
    
    # IRN Information
    irn = Column(String(64), nullable=True, unique=True, index=True)  # Invoice Reference Number
    irn_generated_date = Column(DateTime, nullable=True)
    irn_expiry_date = Column(DateTime, nullable=True)
    
    # QR Code
    qr_code = Column(Text, nullable=True)  # QR code data
    qr_code_image = Column(Text, nullable=True)  # Base64 encoded QR code image
    
    # Status
    status = Column(Enum(EInvoiceStatus), default=EInvoiceStatus.DRAFT)
    status_updated_at = Column(DateTime, nullable=True)
    
    # Government Portal Information
    ack_no = Column(String(100), nullable=True)  # Acknowledgment number
    ack_date = Column(DateTime, nullable=True)  # Acknowledgment date
    eway_bill_no = Column(String(50), nullable=True)  # E-waybill number
    
    # JSON Data
    invoice_json = Column(JSON, nullable=True)  # Complete invoice JSON
    response_json = Column(JSON, nullable=True)  # Government response JSON
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(20), nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="e_invoices")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # Related Models
    sales_invoice_id = Column(Integer, ForeignKey('sales_invoice.id'), nullable=True)
    sales_invoice = relationship("SalesInvoice", back_populates="e_invoice")
    
    def __repr__(self):
        return f"<EInvoice(invoice_number='{self.invoice_number}', irn='{self.irn}', status='{self.status}')>"

class EInvoiceItem(BaseModel):
    """E-invoice Item Details"""
    __tablename__ = "e_invoice_item"
    
    # Basic Information
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    hsn_code = Column(String(8), nullable=True)
    sac_code = Column(String(6), nullable=True)
    
    # Quantities
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_of_measure = Column(String(10), nullable=True)  # NOS, KGS, LTR, etc.
    
    # Rates and Amounts
    unit_price = Column(Numeric(15, 2), nullable=False)
    taxable_amount = Column(Numeric(15, 2), nullable=False)
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    cgst_amount = Column(Numeric(15, 2), nullable=True)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_amount = Column(Numeric(15, 2), nullable=True)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    igst_amount = Column(Numeric(15, 2), nullable=True)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    cess_amount = Column(Numeric(15, 2), nullable=True)
    total_amount = Column(Numeric(15, 2), nullable=False)
    
    # E-invoice Reference
    e_invoice_id = Column(Integer, ForeignKey('e_invoice.id'), nullable=False)
    e_invoice = relationship("EInvoice", back_populates="items")
    
    def __repr__(self):
        return f"<EInvoiceItem(item_name='{self.item_name}', quantity={self.quantity}, amount={self.total_amount})>"

class EInvoiceParty(BaseModel):
    """E-invoice Party Details (Buyer/Seller)"""
    __tablename__ = "e_invoice_party"
    
    # Party Information
    party_type = Column(String(10), nullable=False)  # SELLER, BUYER, SHIP_TO, PAY_TO
    legal_name = Column(String(200), nullable=False)
    trade_name = Column(String(200), nullable=True)
    
    # GST Information
    gstin = Column(String(15), nullable=True)
    registration_type = Column(String(20), nullable=True)  # REGULAR, COMPOSITION, etc.
    
    # Address Information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    country = Column(String(100), default='India')
    
    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # E-invoice Reference
    e_invoice_id = Column(Integer, ForeignKey('e_invoice.id'), nullable=False)
    e_invoice = relationship("EInvoice", back_populates="parties")
    
    def __repr__(self):
        return f"<EInvoiceParty(party_type='{self.party_type}', legal_name='{self.legal_name}')>"

class GSPConfiguration(BaseModel):
    """GSP (GST Suvidha Provider) Configuration"""
    __tablename__ = "gsp_configuration"
    
    # GSP Information
    gsp_name = Column(String(100), nullable=False)  # e.g., "Tera Software Limited"
    gsp_username = Column(String(100), nullable=False)
    gsp_password = Column(String(200), nullable=False)  # Encrypted
    gsp_api_url = Column(String(500), nullable=False)
    
    # Authentication
    client_id = Column(String(100), nullable=True)
    client_secret = Column(String(200), nullable=True)  # Encrypted
    access_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_sandbox = Column(Boolean, default=True)  # Sandbox or Production
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="gsp_configurations")
    
    def __repr__(self):
        return f"<GSPConfiguration(gsp_name='{self.gsp_name}', is_active={self.is_active})>"

class EInvoiceCancellation(BaseModel):
    """E-invoice Cancellation"""
    __tablename__ = "e_invoice_cancellation"
    
    # Cancellation Information
    irn = Column(String(64), nullable=False, index=True)
    cancellation_reason = Column(String(10), nullable=False)  # 1-9 as per GST rules
    cancellation_remarks = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(EInvoiceStatus), default=EInvoiceStatus.DRAFT)
    cancelled_date = Column(DateTime, nullable=True)
    
    # Government Response
    cancel_ack_no = Column(String(100), nullable=True)
    cancel_ack_date = Column(DateTime, nullable=True)
    response_json = Column(JSON, nullable=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(20), nullable=True)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="e_invoice_cancellations")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<EInvoiceCancellation(irn='{self.irn}', reason='{self.cancellation_reason}')>"

# Add relationships to EInvoice
EInvoice.items = relationship("EInvoiceItem", back_populates="e_invoice", cascade="all, delete-orphan")
EInvoice.parties = relationship("EInvoiceParty", back_populates="e_invoice", cascade="all, delete-orphan")