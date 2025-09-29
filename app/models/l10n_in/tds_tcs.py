# backend/app/models/l10n_in/tds_tcs.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from .base import BaseModel

class TDSType(PyEnum):
    """TDS Types"""
    TDS = "TDS"  # Tax Deducted at Source
    TCS = "TCS"  # Tax Collected at Source

class TDSStatus(PyEnum):
    """TDS/TCS Status"""
    DRAFT = "draft"
    GENERATED = "generated"
    UPLOADED = "uploaded"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class TDSRate(BaseModel):
    """TDS/TCS Rate Configuration"""
    __tablename__ = "tds_rate"
    
    # Basic Information
    section_code = Column(String(10), nullable=False)  # e.g., "194A", "194C"
    section_description = Column(Text, nullable=False)
    tds_type = Column(Enum(TDSType), nullable=False)
    
    # Rate Information
    rate = Column(Numeric(5, 2), nullable=False)  # TDS/TCS rate percentage
    threshold_amount = Column(Numeric(15, 2), nullable=True)  # Threshold amount
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Applicability
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_rates")
    
    def __repr__(self):
        return f"<TDSRate(section='{self.section_code}', rate={self.rate}%, type='{self.tds_type}')>"

class TDSDeduction(BaseModel):
    """TDS Deduction Record"""
    __tablename__ = "tds_deduction"
    
    # Basic Information
    deduction_date = Column(Date, nullable=False)
    section_code = Column(String(10), nullable=False)
    tds_type = Column(Enum(TDSType), nullable=False)
    
    # Party Information
    party_name = Column(String(200), nullable=False)
    party_pan = Column(String(10), nullable=True)
    party_gstin = Column(String(15), nullable=True)
    
    # Amount Information
    gross_amount = Column(Numeric(15, 2), nullable=False)
    tds_rate = Column(Numeric(5, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), nullable=False)
    net_amount = Column(Numeric(15, 2), nullable=False)
    
    # Certificate Information
    certificate_no = Column(String(50), nullable=True)
    certificate_date = Column(Date, nullable=True)
    
    # Status
    status = Column(Enum(TDSStatus), default=TDSStatus.DRAFT)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_deductions")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # Related Models
    sales_invoice_id = Column(Integer, ForeignKey('sales_invoice.id'), nullable=True)
    sales_invoice = relationship("SalesInvoice", back_populates="tds_deduction")
    
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=True)
    purchase_invoice = relationship("PurchaseInvoice", back_populates="tds_deduction")
    
    def __repr__(self):
        return f"<TDSDeduction(party='{self.party_name}', amount={self.tds_amount}, section='{self.section_code}')>"

class TDSReturn(BaseModel):
    """TDS Return Filing"""
    __tablename__ = "tds_return"
    
    # Return Information
    return_period = Column(String(7), nullable=False)  # e.g., "2024-25"
    quarter = Column(String(2), nullable=False)  # Q1, Q2, Q3, Q4
    return_type = Column(String(10), nullable=False)  # 24Q, 26Q, 27Q, etc.
    
    # Filing Information
    filing_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    acknowledgment_no = Column(String(50), nullable=True)
    acknowledgment_date = Column(Date, nullable=True)
    
    # Status
    status = Column(Enum(TDSStatus), default=TDSStatus.DRAFT)
    
    # JSON Data
    return_json = Column(JSON, nullable=True)  # Complete return JSON
    response_json = Column(JSON, nullable=True)  # Government response JSON
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(20), nullable=True)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_returns")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TDSReturn(period='{self.return_period}', quarter='{self.quarter}', type='{self.return_type}')>"

class TDSReturnItem(BaseModel):
    """TDS Return Item Details"""
    __tablename__ = "tds_return_item"
    
    # Party Information
    party_name = Column(String(200), nullable=False)
    party_pan = Column(String(10), nullable=False)
    party_gstin = Column(String(15), nullable=True)
    
    # Amount Information
    gross_amount = Column(Numeric(15, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), nullable=False)
    section_code = Column(String(10), nullable=False)
    
    # TDS Return Reference
    tds_return_id = Column(Integer, ForeignKey('tds_return.id'), nullable=False)
    tds_return = relationship("TDSReturn", back_populates="items")
    
    def __repr__(self):
        return f"<TDSReturnItem(party='{self.party_name}', pan='{self.party_pan}', amount={self.tds_amount})>"

class TDSCertificate(BaseModel):
    """TDS Certificate Generation"""
    __tablename__ = "tds_certificate"
    
    # Certificate Information
    certificate_no = Column(String(50), nullable=False, unique=True, index=True)
    certificate_type = Column(String(10), nullable=False)  # 16, 16A, 16B, 16C
    certificate_date = Column(Date, nullable=False)
    
    # Party Information
    party_name = Column(String(200), nullable=False)
    party_pan = Column(String(10), nullable=False)
    party_address = Column(Text, nullable=True)
    
    # Amount Information
    gross_amount = Column(Numeric(15, 2), nullable=False)
    tds_amount = Column(Numeric(15, 2), nullable=False)
    section_code = Column(String(10), nullable=False)
    
    # Status
    status = Column(Enum(TDSStatus), default=TDSStatus.DRAFT)
    
    # PDF Information
    pdf_path = Column(String(500), nullable=True)
    pdf_generated_date = Column(DateTime, nullable=True)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_certificates")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # Related Models
    tds_deduction_id = Column(Integer, ForeignKey('tds_deduction.id'), nullable=True)
    tds_deduction = relationship("TDSDeduction", back_populates="certificate")
    
    def __repr__(self):
        return f"<TDSCertificate(certificate_no='{self.certificate_no}', party='{self.party_name}')>"

class TDSReconciliation(BaseModel):
    """TDS Reconciliation"""
    __tablename__ = "tds_reconciliation"
    
    # Reconciliation Information
    reconciliation_period = Column(String(7), nullable=False)  # e.g., "2024-25"
    quarter = Column(String(2), nullable=False)  # Q1, Q2, Q3, Q4
    
    # Reconciliation Data
    total_deductions = Column(Numeric(15, 2), nullable=False)
    total_deposits = Column(Numeric(15, 2), nullable=False)
    difference_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    is_reconciled = Column(Boolean, default=False)
    reconciliation_date = Column(Date, nullable=True)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_reconciliations")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<TDSReconciliation(period='{self.reconciliation_period}', quarter='{self.quarter}')>"

# Add relationships
TDSReturn.items = relationship("TDSReturnItem", back_populates="tds_return", cascade="all, delete-orphan")
TDSDeduction.certificate = relationship("TDSCertificate", back_populates="tds_deduction", uselist=False)