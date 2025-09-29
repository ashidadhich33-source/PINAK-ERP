# backend/app/models/accounting/analytic.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class AnalyticAccountType(PyEnum):
    """Analytic account types"""
    COST_CENTER = "cost_center"
    PROJECT = "project"
    DEPARTMENT = "department"
    PRODUCT = "product"
    CUSTOMER = "customer"
    SUPPLIER = "supplier"
    LOCATION = "location"
    ACTIVITY = "activity"

class DistributionMethod(PyEnum):
    """Distribution methods"""
    MANUAL = "manual"
    PERCENTAGE = "percentage"
    EQUAL = "equal"
    WEIGHTED = "weighted"
    FORMULA = "formula"

class AnalyticAccount(BaseModel):
    """Analytic accounts for cost center tracking"""
    __tablename__ = "analytic_account"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    account_type = Column(Enum(AnalyticAccountType), nullable=False)
    parent_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=True)
    level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    is_leaf = Column(Boolean, default=True)  # Cannot have children
    manager_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    budget_amount = Column(Numeric(15, 2), nullable=True)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance_amount = Column(Numeric(15, 2), default=0)
    color = Column(String(7), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)  # Icon name
    metadata = Column(JSON, nullable=True)  # Additional account data
    
    # Relationships
    parent = relationship("AnalyticAccount", remote_side=[BaseModel.id])
    children = relationship("AnalyticAccount", back_populates="parent")
    manager = relationship("User", foreign_keys=[manager_id])
    analytic_lines = relationship("AnalyticLine", back_populates="analytic_account")
    distributions = relationship("AnalyticDistribution", back_populates="analytic_account")
    
    def __repr__(self):
        return f"<AnalyticAccount(name='{self.name}', type='{self.account_type}')>"

class AnalyticLine(BaseModel):
    """Analytic lines for cost tracking"""
    __tablename__ = "analytic_line"
    
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    move_line_id = Column(Integer, ForeignKey('journal_entry_item.id'), nullable=True)
    invoice_id = Column(Integer, ForeignKey('invoice.id'), nullable=True)
    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_amount = Column(Numeric(15, 2), nullable=True)  # Amount in original currency
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=True)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=True)
    unit_amount = Column(Numeric(15, 2), nullable=True)
    unit_of_measure = Column(String(50), nullable=True)
    is_debit = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    analytic_account = relationship("AnalyticAccount", back_populates="analytic_lines")
    move_line = relationship("JournalEntryItem")
    invoice = relationship("Invoice")
    bill = relationship("Bill")
    payment = relationship("Payment")
    currency = relationship("Currency")
    partner = relationship("Partner")
    product = relationship("Product")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<AnalyticLine(account='{self.analytic_account.name}', amount={self.amount})>"

class AnalyticPlan(BaseModel):
    """Analytic plans for cost structure"""
    __tablename__ = "analytic_plan"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    company = relationship("Company")
    created_by_user = relationship("User", foreign_keys=[created_by])
    plan_accounts = relationship("AnalyticPlanAccount", back_populates="plan")
    
    def __repr__(self):
        return f"<AnalyticPlan(name='{self.name}', code='{self.code}')>"

class AnalyticPlanAccount(BaseModel):
    """Analytic plan accounts"""
    __tablename__ = "analytic_plan_account"
    
    plan_id = Column(Integer, ForeignKey('analytic_plan.id'), nullable=False)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    is_mandatory = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    plan = relationship("AnalyticPlan", back_populates="plan_accounts")
    analytic_account = relationship("AnalyticAccount")
    
    def __repr__(self):
        return f"<AnalyticPlanAccount(plan='{self.plan.name}', account='{self.analytic_account.name}')>"

class AnalyticDistribution(BaseModel):
    """Analytic distribution models"""
    __tablename__ = "analytic_distribution"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    distribution_method = Column(Enum(DistributionMethod), nullable=False)
    percentage = Column(Numeric(5, 2), nullable=True)  # For percentage method
    amount = Column(Numeric(15, 2), nullable=True)  # For fixed amount method
    formula = Column(Text, nullable=True)  # For formula method
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    conditions = Column(JSON, nullable=True)  # Conditional distribution logic
    
    # Relationships
    account = relationship("ChartOfAccount")
    analytic_account = relationship("AnalyticAccount", back_populates="distributions")
    
    def __repr__(self):
        return f"<AnalyticDistribution(name='{self.name}', method='{self.distribution_method}')>"

class AnalyticBudget(BaseModel):
    """Analytic budgets"""
    __tablename__ = "analytic_budget"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    analytic_account_id = Column(Integer, ForeignKey('analytic_account.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    budget_period = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance_amount = Column(Numeric(15, 2), default=0)
    variance_percentage = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    analytic_account = relationship("AnalyticAccount")
    account = relationship("ChartOfAccount")
    created_by_user = relationship("User", foreign_keys=[created_by])
    budget_lines = relationship("AnalyticBudgetLine", back_populates="budget")
    
    def __repr__(self):
        return f"<AnalyticBudget(name='{self.name}', amount={self.budget_amount})>"

class AnalyticBudgetLine(BaseModel):
    """Analytic budget line items"""
    __tablename__ = "analytic_budget_line"
    
    budget_id = Column(Integer, ForeignKey('analytic_budget.id'), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    budget_amount = Column(Numeric(15, 2), nullable=False)
    actual_amount = Column(Numeric(15, 2), default=0)
    variance_amount = Column(Numeric(15, 2), default=0)
    variance_percentage = Column(Numeric(5, 2), default=0)
    
    # Relationships
    budget = relationship("AnalyticBudget", back_populates="budget_lines")
    
    def __repr__(self):
        return f"<AnalyticBudgetLine(period='{self.period_start}', amount={self.budget_amount})>"

class AnalyticReport(BaseModel):
    """Analytic reports"""
    __tablename__ = "analytic_report"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # cost_center, project, department
    analytic_account_ids = Column(JSON, nullable=True)  # Selected analytic accounts
    account_ids = Column(JSON, nullable=True)  # Selected chart accounts
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    group_by = Column(String(50), nullable=True)  # account, partner, product, period
    sort_by = Column(String(50), nullable=True)  # amount, name, date
    sort_order = Column(String(10), default='asc')  # asc, desc
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<AnalyticReport(name='{self.name}', type='{self.report_type}')>"

class AnalyticTag(BaseModel):
    """Analytic tags for categorization"""
    __tablename__ = "analytic_tag"
    
    name = Column(String(100), nullable=False)
    color = Column(String(7), nullable=True)  # Hex color code
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tag_lines = relationship("AnalyticTagLine", back_populates="tag")
    
    def __repr__(self):
        return f"<AnalyticTag(name='{self.name}')>"

class AnalyticTagLine(BaseModel):
    """Analytic tag line items"""
    __tablename__ = "analytic_tag_line"
    
    tag_id = Column(Integer, ForeignKey('analytic_tag.id'), nullable=False)
    analytic_line_id = Column(Integer, ForeignKey('analytic_line.id'), nullable=False)
    
    # Relationships
    tag = relationship("AnalyticTag", back_populates="tag_lines")
    analytic_line = relationship("AnalyticLine")
    
    def __repr__(self):
        return f"<AnalyticTagLine(tag='{self.tag.name}', line_id={self.analytic_line_id})>"