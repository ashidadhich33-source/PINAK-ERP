# backend/app/models/l10n_in/gst_tax_structure.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from ..base import BaseModel

class GSTTaxType(PyEnum):
    """GST Tax Types"""
    CGST = "CGST"  # Central GST
    SGST = "SGST"  # State GST
    IGST = "IGST"  # Integrated GST
    CESS = "CESS"  # Cess
    UTGST = "UTGST"  # Union Territory GST

class GSTRegistrationType(PyEnum):
    """GST Registration Types"""
    REGULAR = "regular"
    COMPOSITION = "composition"
    UNREGISTERED = "unregistered"
    CASUAL = "casual"
    NON_RESIDENT = "non_resident"

class PlaceOfSupplyType(PyEnum):
    """Place of Supply Types"""
    INTRA_STATE = "intra_state"  # Within same state
    INTER_STATE = "inter_state"  # Between different states
    EXPORT = "export"  # Export of goods/services
    IMPORT = "import"  # Import of goods/services

class GSTSlab(BaseModel):
    """GST Tax Slabs and Rates"""
    __tablename__ = "gst_tax_slab"
    
    # Basic Information
    name = Column(String(100), nullable=False)  # e.g., "GST 18%"
    tax_type = Column(Enum(GSTTaxType), nullable=False)
    rate = Column(Numeric(5, 2), nullable=False)  # Tax rate percentage
    cgst_rate = Column(Numeric(5, 2), nullable=True)  # CGST rate
    sgst_rate = Column(Numeric(5, 2), nullable=True)  # SGST rate
    igst_rate = Column(Numeric(5, 2), nullable=True)  # IGST rate
    cess_rate = Column(Numeric(5, 2), nullable=True)  # CESS rate
    
    # Applicability
    is_active = Column(Boolean, default=True)
    effective_from = Column(Date, nullable=False, default=date.today)
    effective_to = Column(Date, nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="gst_slabs")
    
    def __repr__(self):
        return f"<GSTSlab(name='{self.name}', rate={self.rate}%)>"

class HSNCode(BaseModel):
    """HSN (Harmonized System of Nomenclature) Codes"""
    __tablename__ = "gst_hsn_code"
    
    # HSN Code Information
    code = Column(String(8), nullable=False, unique=True, index=True)  # 4, 6, or 8 digit HSN code
    description = Column(Text, nullable=False)
    chapter = Column(String(2), nullable=True)  # First 2 digits
    heading = Column(String(4), nullable=True)  # First 4 digits
    sub_heading = Column(String(6), nullable=True)  # First 6 digits
    
    # GST Information
    gst_rate = Column(Numeric(5, 2), nullable=True)  # Standard GST rate
    cess_rate = Column(Numeric(5, 2), nullable=True)  # CESS rate if applicable
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="hsn_codes")
    
    def __repr__(self):
        return f"<HSNCode(code='{self.code}', description='{self.description[:50]}...')>"

class SACCode(BaseModel):
    """SAC (Service Accounting Code) Codes"""
    __tablename__ = "sac_code"
    
    # SAC Code Information
    code = Column(String(6), nullable=False, unique=True, index=True)  # 6 digit SAC code
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # Service category
    
    # GST Information
    gst_rate = Column(Numeric(5, 2), nullable=True)  # Standard GST rate
    cess_rate = Column(Numeric(5, 2), nullable=True)  # CESS rate if applicable
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="sac_codes")
    
    def __repr__(self):
        return f"<SACCode(code='{self.code}', description='{self.description[:50]}...')>"

class GSTStateCode(BaseModel):
    """GST State Codes for Indian States and Union Territories"""
    __tablename__ = "gst_tax_state_code"
    
    # State Information
    code = Column(String(2), nullable=False, unique=True, index=True)  # 2 digit state code
    name = Column(String(100), nullable=False)
    state_type = Column(String(20), default='state')  # state, union_territory
    
    # GST Information
    gst_state_code = Column(String(2), nullable=True)  # GST state code
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<GSTStateCode(code='{self.code}', name='{self.name}')>"

class PlaceOfSupply(BaseModel):
    """Place of Supply Rules for GST"""
    __tablename__ = "place_of_supply"
    
    # Supply Information
    supplier_state_code = Column(String(2), nullable=False)
    recipient_state_code = Column(String(2), nullable=False)
    supply_type = Column(Enum(PlaceOfSupplyType), nullable=False)
    
    # Tax Application
    applies_cgst_sgst = Column(Boolean, default=False)  # Intra-state: CGST + SGST
    applies_igst = Column(Boolean, default=False)  # Inter-state: IGST
    
    # Rules
    rule_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="place_of_supply_rules")
    
    def __repr__(self):
        return f"<PlaceOfSupply(supplier='{self.supplier_state_code}', recipient='{self.recipient_state_code}', type='{self.supply_type}')>"

class GSTRegistration(BaseModel):
    """GST Registration Details"""
    __tablename__ = "gst_registration"
    
    # Registration Information
    gstin = Column(String(15), nullable=False, unique=True, index=True)  # 15 character GSTIN
    registration_type = Column(Enum(GSTRegistrationType), nullable=False)
    registration_date = Column(Date, nullable=False)
    
    # Business Details
    legal_name = Column(String(200), nullable=False)
    trade_name = Column(String(200), nullable=True)
    business_type = Column(String(50), nullable=True)  # Private Limited, Partnership, etc.
    
    # Address Information
    principal_place_of_business = Column(Text, nullable=False)
    state_code = Column(String(2), nullable=False)
    
    # Contact Information
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_date = Column(Date, nullable=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="gst_registrations")
    
    def __repr__(self):
        return f"<GSTRegistration(gstin='{self.gstin}', type='{self.registration_type}')>"

class ReverseCharge(BaseModel):
    """Reverse Charge Mechanism"""
    __tablename__ = "reverse_charge"
    
    # Reverse Charge Information
    description = Column(Text, nullable=False)
    applicable_from = Column(Date, nullable=False)
    applicable_to = Column(Date, nullable=True)
    
    # Tax Details
    cgst_rate = Column(Numeric(5, 2), nullable=True)
    sgst_rate = Column(Numeric(5, 2), nullable=True)
    igst_rate = Column(Numeric(5, 2), nullable=True)
    cess_rate = Column(Numeric(5, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="reverse_charge_rules")
    
    def __repr__(self):
        return f"<ReverseCharge(description='{self.description[:50]}...')>"