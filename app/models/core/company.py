# backend/app/models/company.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from ..base import BaseModel

class Company(BaseModel):
    """Company/Organization model for multi-tenant support"""
    __tablename__ = "company"
    
    # Basic Information
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    legal_name = Column(String(200), nullable=True)
    
    # Contact Information
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Address Information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default='India')
    postal_code = Column(String(10), nullable=True)
    
    # Geographic References (for Indian localization)
    country_id = Column(Integer, ForeignKey('country.id'), nullable=True)
    state_id = Column(Integer, ForeignKey('indian_state.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('indian_city.id'), nullable=True)
    district_id = Column(Integer, ForeignKey('indian_district.id'), nullable=True)
    taluka_id = Column(Integer, ForeignKey('indian_taluka.id'), nullable=True)
    village_id = Column(Integer, ForeignKey('indian_village.id'), nullable=True)
    pincode_id = Column(Integer, ForeignKey('indian_pincode.id'), nullable=True)
    
    # Business Information
    gst_number = Column(String(15), nullable=True, unique=True)
    pan_number = Column(String(10), nullable=True, unique=True)
    cin_number = Column(String(21), nullable=True)
    business_type = Column(String(50), nullable=True)  # Private Limited, Partnership, etc.
    
    # Financial Year Settings
    financial_year_start = Column(Date, nullable=False, default=date(2024, 4, 1))
    financial_year_end = Column(Date, nullable=False, default=date(2025, 3, 31))
    current_financial_year = Column(String(10), nullable=False, default='2024-25')
    
    # Currency Settings
    currency_code = Column(String(3), default='INR')
    currency_symbol = Column(String(5), default='₹')
    decimal_places = Column(Integer, default=2)
    
    # GST Settings
    gst_registration_type = Column(String(20), default='regular')  # regular, composition, unregistered
    gst_state_code = Column(String(2), nullable=True)
    
    # System Settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Logo and Branding
    logo_path = Column(String(500), nullable=True)
    theme_color = Column(String(7), default='#007bff')  # Hex color
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("UserCompany", back_populates="company")
    financial_years = relationship("FinancialYear", back_populates="company")
    gst_slabs = relationship("GSTSlab", back_populates="company")
    chart_of_accounts = relationship("ChartOfAccount", back_populates="company")
    items = relationship("Item", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    suppliers = relationship("Supplier", back_populates="company")
    
    # Automation relationships
    automation_settings = relationship("AutomationSetting", back_populates="company")
    automation_workflows = relationship("AutomationWorkflow", back_populates="company")
    automation_rules = relationship("AutomationRule", back_populates="company")
    automation_triggers = relationship("AutomationTrigger", back_populates="company")
    automation_actions = relationship("AutomationAction", back_populates="company")
    automation_conditions = relationship("AutomationCondition", back_populates="company")
    automation_approvals = relationship("AutomationApproval", back_populates="company")
    automation_logs = relationship("AutomationLog", back_populates="company")
    automation_exceptions = relationship("AutomationException", back_populates="company")
    automation_rollbacks = relationship("AutomationRollback", back_populates="company")
    automation_audits = relationship("AutomationAudit", back_populates="company")
    
    # Geographic Relationships
    country_ref = relationship("Country", foreign_keys=[country_id])
    state_ref = relationship("IndianState", foreign_keys=[state_id])
    city_ref = relationship("IndianCity", foreign_keys=[city_id])
    district_ref = relationship("IndianDistrict", foreign_keys=[district_id])
    taluka_ref = relationship("IndianTaluka", foreign_keys=[taluka_id])
    village_ref = relationship("IndianVillage", foreign_keys=[village_id])
    pincode_ref = relationship("IndianPincode", foreign_keys=[pincode_id])
    
    def __repr__(self):
        return f"<Company(name='{self.name}', gst='{self.gst_number}')>"

class UserCompany(BaseModel):
    """User-Company association for multi-tenant access"""
    __tablename__ = "user_company"
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Access Control
    role = Column(String(20), default='user')  # admin, manager, user, viewer
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Permissions (JSON field for granular permissions)
    permissions = Column(Text, nullable=True)  # JSON string
    
    # Access Information
    last_accessed = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="companies")
    company = relationship("Company", back_populates="users")
    
    def __repr__(self):
        return f"<UserCompany(user_id={self.user_id}, company_id={self.company_id}, role='{self.role}')>"

class FinancialYear(BaseModel):
    """Financial Year management per company"""
    __tablename__ = "financial_year"
    
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Financial Year Information
    year_name = Column(String(20), nullable=False)  # 2024-25
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Opening Balances
    opening_balances = Column(Text, nullable=True)  # JSON string
    
    # Closing Information
    closing_remarks = Column(Text, nullable=True)
    next_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="financial_years")
    closed_by_user = relationship("User", foreign_keys=[closed_by])
    next_year = relationship("FinancialYear", remote_side=[BaseModel.id])
    
    def __repr__(self):
        return f"<FinancialYear(company_id={self.company_id}, year='{self.year_name}')>"

class GSTSlab(BaseModel):
    """Dynamic GST slab management per company"""
    __tablename__ = "gst_slab"
    
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # GST Information
    rate = Column(Numeric(5, 2), nullable=False)  # 18.00
    cgst_rate = Column(Numeric(5, 2), nullable=False)  # 9.00
    sgst_rate = Column(Numeric(5, 2), nullable=False)  # 9.00
    igst_rate = Column(Numeric(5, 2), nullable=False)  # 18.00
    
    # Validity Period
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Additional Information
    description = Column(String(200), nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="gst_slabs")
    
    def __repr__(self):
        return f"<GSTSlab(company_id={self.company_id}, rate={self.rate}%)>"

class ChartOfAccount(BaseModel):
    """Chart of Accounts per company"""
    __tablename__ = "chart_of_account"
    
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Account Information
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(20), nullable=False)  # asset, liability, income, expense, equity
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=True)
    level = Column(Integer, default=1)
    
    # Account Properties
    balance_type = Column(String(10), nullable=False)  # debit, credit
    is_gst_applicable = Column(Boolean, default=False)
    gst_slab_id = Column(Integer, ForeignKey('gst_slab.id'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system_account = Column(Boolean, default=False)
    
    # Additional Information
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="chart_of_accounts")
    parent = relationship("ChartOfAccount", remote_side=[BaseModel.id])
    gst_slab = relationship("GSTSlab")
    
    def __repr__(self):
        return f"<ChartOfAccount(company_id={self.company_id}, code='{self.account_code}', name='{self.account_name}')>"