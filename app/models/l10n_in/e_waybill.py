# backend/app/models/l10n_in/e_waybill.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from ..base import BaseModel

class EWaybillStatus(PyEnum):
    """E-waybill Status"""
    DRAFT = "draft"
    GENERATED = "generated"
    UPLOADED = "uploaded"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class EWaybillType(PyEnum):
    """E-waybill Types"""
    SUPPLY = "SUPPLY"  # Regular supply
    EXPORT = "EXPORT"  # Export
    IMPORT = "IMPORT"  # Import
    JOB_WORK = "JOB_WORK"  # Job work
    SKD = "SKD"  # SKD (Semi Knocked Down)
    CKD = "CKD"  # CKD (Completely Knocked Down)

class TransportationMode(PyEnum):
    """Transportation Modes"""
    ROAD = "ROAD"
    RAIL = "RAIL"
    AIR = "AIR"
    SHIP = "SHIP"

class EWaybill(BaseModel):
    """E-waybill Model for Indian GST Compliance"""
    __tablename__ = "e_waybill"
    
    # Basic Information
    eway_bill_no = Column(String(50), nullable=True, unique=True, index=True)
    eway_bill_date = Column(Date, nullable=False)
    eway_bill_type = Column(Enum(EWaybillType), nullable=False)
    
    # Validity Information
    valid_from = Column(DateTime, nullable=False)
    valid_upto = Column(DateTime, nullable=False)
    distance = Column(Numeric(8, 2), nullable=True)  # Distance in kilometers
    
    # Status
    status = Column(Enum(EWaybillStatus), default=EWaybillStatus.DRAFT)
    status_updated_at = Column(DateTime, nullable=True)
    
    # Government Portal Information
    ack_no = Column(String(100), nullable=True)  # Acknowledgment number
    ack_date = Column(DateTime, nullable=True)  # Acknowledgment date
    
    # JSON Data
    eway_bill_json = Column(JSON, nullable=True)  # Complete e-waybill JSON
    response_json = Column(JSON, nullable=True)  # Government response JSON
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_code = Column(String(20), nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Company and User Information
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="e_waybills")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    # Related Models
    sales_invoice_id = Column(Integer, ForeignKey('sales_invoice.id'), nullable=True)
    sales_invoice = relationship("SalesInvoice", back_populates="e_waybill")
    
    def __repr__(self):
        return f"<EWaybill(eway_bill_no='{self.eway_bill_no}', type='{self.eway_bill_type}', status='{self.status}')>"

class EWaybillItem(BaseModel):
    """E-waybill Item Details"""
    __tablename__ = "e_waybill_item"
    
    # Basic Information
    item_name = Column(String(200), nullable=False)
    item_description = Column(Text, nullable=True)
    hsn_code = Column(String(8), nullable=True)
    
    # Quantities
    quantity = Column(Numeric(10, 3), nullable=False)
    unit_of_measure = Column(String(10), nullable=True)  # NOS, KGS, LTR, etc.
    
    # Rates and Amounts
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
    
    # E-waybill Reference
    e_waybill_id = Column(Integer, ForeignKey('e_waybill.id'), nullable=False)
    e_waybill = relationship("EWaybill", back_populates="items")
    
    def __repr__(self):
        return f"<EWaybillItem(item_name='{self.item_name}', quantity={self.quantity}, amount={self.total_amount})>"

class EWaybillParty(BaseModel):
    """E-waybill Party Details (From/To)"""
    __tablename__ = "e_waybill_party"
    
    # Party Information
    party_type = Column(String(10), nullable=False)  # FROM, TO
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
    
    # E-waybill Reference
    e_waybill_id = Column(Integer, ForeignKey('e_waybill.id'), nullable=False)
    e_waybill = relationship("EWaybill", back_populates="parties")
    
    def __repr__(self):
        return f"<EWaybillParty(party_type='{self.party_type}', legal_name='{self.legal_name}')>"

class EWaybillTransport(BaseModel):
    """E-waybill Transportation Details"""
    __tablename__ = "e_waybill_transport"
    
    # Transportation Information
    transportation_mode = Column(Enum(TransportationMode), nullable=False)
    vehicle_number = Column(String(20), nullable=True)
    vehicle_type = Column(String(50), nullable=True)  # Truck, Lorry, etc.
    
    # Driver Information
    driver_name = Column(String(100), nullable=True)
    driver_phone = Column(String(20), nullable=True)
    driver_license_no = Column(String(50), nullable=True)
    
    # Transportation Details
    transporter_name = Column(String(200), nullable=True)
    transporter_gstin = Column(String(15), nullable=True)
    transporter_phone = Column(String(20), nullable=True)
    
    # Distance and Time
    distance = Column(Numeric(8, 2), nullable=True)  # Distance in kilometers
    transport_date = Column(Date, nullable=True)
    
    # E-waybill Reference
    e_waybill_id = Column(Integer, ForeignKey('e_waybill.id'), nullable=False)
    e_waybill = relationship("EWaybill", back_populates="transport")
    
    def __repr__(self):
        return f"<EWaybillTransport(mode='{self.transportation_mode}', vehicle='{self.vehicle_number}')>"

class EWaybillCancellation(BaseModel):
    """E-waybill Cancellation"""
    __tablename__ = "e_waybill_cancellation"
    
    # Cancellation Information
    eway_bill_no = Column(String(50), nullable=False, index=True)
    cancellation_reason = Column(String(10), nullable=False)  # 1-9 as per GST rules
    cancellation_remarks = Column(Text, nullable=True)
    
    # Status
    status = Column(Enum(EWaybillStatus), default=EWaybillStatus.DRAFT)
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
    company = relationship("Company", back_populates="e_waybill_cancellations")
    
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<EWaybillCancellation(eway_bill_no='{self.eway_bill_no}', reason='{self.cancellation_reason}')>"

# Add relationships to EWaybill
EWaybill.items = relationship("EWaybillItem", back_populates="e_waybill", cascade="all, delete-orphan")
EWaybill.parties = relationship("EWaybillParty", back_populates="e_waybill", cascade="all, delete-orphan")
EWaybill.transport = relationship("EWaybillTransport", back_populates="e_waybill", uselist=False, cascade="all, delete-orphan")