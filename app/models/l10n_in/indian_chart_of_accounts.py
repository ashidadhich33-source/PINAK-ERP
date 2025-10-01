# backend/app/models/l10n_in/indian_chart_of_accounts.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from ..base import BaseModel

class AccountType(PyEnum):
    """Indian Chart of Accounts - Account Types"""
    ASSETS = "Assets"
    LIABILITIES = "Liabilities"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSES = "Expenses"

class AccountSubType(PyEnum):
    """Indian Chart of Accounts - Account Sub Types"""
    # Assets
    CURRENT_ASSETS = "Current Assets"
    FIXED_ASSETS = "Fixed Assets"
    INVESTMENTS = "Investments"
    LOANS_ADVANCES = "Loans & Advances"
    
    # Liabilities
    CURRENT_LIABILITIES = "Current Liabilities"
    LONG_TERM_LIABILITIES = "Long Term Liabilities"
    PROVISIONS = "Provisions"
    
    # Equity
    SHARE_CAPITAL = "Share Capital"
    RESERVES_SURPLUS = "Reserves & Surplus"
    
    # Income
    SALES = "Sales"
    OTHER_INCOME = "Other Income"
    
    # Expenses
    PURCHASES = "Purchases"
    DIRECT_EXPENSES = "Direct Expenses"
    INDIRECT_EXPENSES = "Indirect Expenses"

class IndianChartOfAccount(BaseModel):
    """Indian Chart of Accounts - Standard Format"""
    __tablename__ = "indian_chart_of_account"
    
    # Basic Information
    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_sub_type = Column(Enum(AccountSubType), nullable=True)
    
    # Hierarchy
    parent_account_id = Column(Integer, ForeignKey('indian_chart_of_account.id'), nullable=True)
    parent_account = relationship("IndianChartOfAccount", remote_side=[id], back_populates="child_accounts")
    child_accounts = relationship("IndianChartOfAccount", back_populates="parent_account")
    
    # Account Properties
    is_group = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # GST Information
    gst_applicable = Column(Boolean, default=False)
    gst_rate = Column(Numeric(5, 2), nullable=True)
    hsn_code = Column(String(8), nullable=True)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="indian_chart_of_accounts")
    
    def __repr__(self):
        return f"<IndianChartOfAccount(code='{self.account_code}', name='{self.account_name}', type='{self.account_type}')>"

class ScheduleVIAccount(BaseModel):
    """Schedule VI Chart of Accounts - MCA Revised Format"""
    __tablename__ = "schedule_vi_account"
    
    # Basic Information
    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    schedule_vi_category = Column(String(100), nullable=False)  # Balance Sheet, P&L categories
    
    # Schedule VI Classification
    balance_sheet_side = Column(String(20), nullable=True)  # Assets, Liabilities
    p_l_side = Column(String(20), nullable=True)  # Income, Expenses
    
    # Hierarchy
    parent_account_id = Column(Integer, ForeignKey('schedule_vi_account.id'), nullable=True)
    parent_account = relationship("ScheduleVIAccount", remote_side=[id], back_populates="child_accounts")
    child_accounts = relationship("ScheduleVIAccount", back_populates="parent_account")
    
    # Account Properties
    is_group = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="schedule_vi_accounts")
    
    def __repr__(self):
        return f"<ScheduleVIAccount(code='{self.account_code}', name='{self.account_name}', category='{self.schedule_vi_category}')>"

class GSTAccount(BaseModel):
    """GST-specific Accounts"""
    __tablename__ = "gst_account"
    
    # Basic Information
    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    
    # GST Information
    gst_type = Column(String(20), nullable=False)  # CGST, SGST, IGST, CESS
    gst_rate = Column(Numeric(5, 2), nullable=True)
    state_code = Column(String(2), nullable=True)
    
    # Account Properties
    is_input_tax = Column(Boolean, default=False)
    is_output_tax = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="gst_accounts")
    
    def __repr__(self):
        return f"<GSTAccount(code='{self.account_code}', name='{self.account_name}', type='{self.gst_type}')>"

class TDSAccount(BaseModel):
    """TDS-specific Accounts"""
    __tablename__ = "tds_account"
    
    # Basic Information
    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    
    # TDS Information
    tds_type = Column(String(20), nullable=False)  # TDS, TCS
    section_code = Column(String(10), nullable=False)
    tds_rate = Column(Numeric(5, 2), nullable=True)
    
    # Account Properties
    is_active = Column(Boolean, default=True)
    
    # Balance Information
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="tds_accounts")
    
    def __repr__(self):
        return f"<TDSAccount(code='{self.account_code}', name='{self.account_name}', type='{self.tds_type}')>"

class IndustryChartOfAccount(BaseModel):
    """Industry-specific Chart of Accounts"""
    __tablename__ = "industry_chart_of_account"
    
    # Basic Information
    industry_name = Column(String(100), nullable=False)
    industry_code = Column(String(10), nullable=False)
    account_code = Column(String(20), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    
    # Industry Classification
    industry_type = Column(String(50), nullable=False)  # Manufacturing, Trading, Service, etc.
    account_type = Column(Enum(AccountType), nullable=False)
    account_sub_type = Column(Enum(AccountSubType), nullable=True)
    
    # Account Properties
    is_group = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="industry_chart_of_accounts")
    
    def __repr__(self):
        return f"<IndustryChartOfAccount(industry='{self.industry_name}', code='{self.account_code}', name='{self.account_name}')>"

class AccountTemplate(BaseModel):
    """Chart of Accounts Template"""
    __tablename__ = "account_template"
    
    # Template Information
    template_name = Column(String(100), nullable=False)
    template_description = Column(Text, nullable=True)
    template_type = Column(String(20), nullable=False)  # standard, schedule_vi, industry_specific
    
    # Template Properties
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="account_templates")
    
    def __repr__(self):
        return f"<AccountTemplate(name='{self.template_name}', type='{self.template_type}')>"

class AccountTemplateItem(BaseModel):
    """Chart of Accounts Template Items"""
    __tablename__ = "account_template_item"
    
    # Template Item Information
    account_code = Column(String(20), nullable=False)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    account_sub_type = Column(Enum(AccountSubType), nullable=True)
    
    # Hierarchy
    parent_account_code = Column(String(20), nullable=True)
    level = Column(Integer, default=1)
    
    # Account Properties
    is_group = Column(Boolean, default=False)
    is_system = Column(Boolean, default=False)
    
    # Template Reference
    template_id = Column(Integer, ForeignKey('account_template.id'), nullable=False)
    template = relationship("AccountTemplate", back_populates="items")
    
    def __repr__(self):
        return f"<AccountTemplateItem(code='{self.account_code}', name='{self.account_name}', template='{self.template_id}')>"

# Add relationships to AccountTemplate
AccountTemplate.items = relationship("AccountTemplateItem", back_populates="template", cascade="all, delete-orphan")