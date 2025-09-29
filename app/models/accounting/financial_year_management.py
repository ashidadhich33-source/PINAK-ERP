# backend/app/models/financial_year_management.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class FinancialYear(BaseModel):
    """Financial year management"""
    __tablename__ = "financial_year"
    
    year_name = Column(String(100), nullable=False)
    year_code = Column(String(20), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    closing_date = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    opening_balance_entered = Column(Boolean, default=False)
    year_status = Column(String(20), default='draft')  # draft, active, closed, archived
    notes = Column(Text, nullable=True)
    
    # Relationships
    closed_by_user = relationship("User", foreign_keys=[closed_by])
    opening_balances = relationship("OpeningBalance", back_populates="financial_year")
    year_closing = relationship("YearClosing", back_populates="financial_year")
    year_analytics = relationship("YearAnalytics", back_populates="financial_year")
    
    def __repr__(self):
        return f"<FinancialYear(name='{self.year_name}', code='{self.year_code}')>"

class OpeningBalance(BaseModel):
    """Opening balance management"""
    __tablename__ = "opening_balance"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    debit_balance = Column(Numeric(15, 2), default=0)
    credit_balance = Column(Numeric(15, 2), default=0)
    balance_type = Column(String(20), nullable=False)  # debit, credit, zero
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="opening_balances")
    account = relationship("ChartOfAccount")
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<OpeningBalance(year_id={self.financial_year_id}, account_id={self.account_id})>"

class YearClosing(BaseModel):
    """Year closing management"""
    __tablename__ = "year_closing"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    closing_type = Column(String(50), nullable=False)  # full_closing, partial_closing, trial_closing
    closing_date = Column(DateTime, default=datetime.utcnow)
    closing_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    closing_data = Column(JSON, nullable=True)  # Closing data and statistics
    closing_errors = Column(JSON, nullable=True)  # Closing errors and warnings
    closing_notes = Column(Text, nullable=True)
    closed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="year_closing")
    closed_by_user = relationship("User", foreign_keys=[closed_by])
    closing_items = relationship("YearClosingItem", back_populates="year_closing")
    
    def __repr__(self):
        return f"<YearClosing(year_id={self.financial_year_id}, type='{self.closing_type}')>"

class YearClosingItem(BaseModel):
    """Year closing item management"""
    __tablename__ = "year_closing_item"
    
    closing_id = Column(Integer, ForeignKey('year_closing.id'), nullable=False)
    item_type = Column(String(50), nullable=False)  # account, transaction, inventory, customer, supplier
    item_id = Column(Integer, nullable=False)
    item_name = Column(String(200), nullable=False)
    closing_status = Column(String(20), default='pending')  # pending, completed, failed, skipped
    closing_data = Column(JSON, nullable=True)
    closing_errors = Column(JSON, nullable=True)
    processed_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    year_closing = relationship("YearClosing", back_populates="closing_items")
    
    def __repr__(self):
        return f"<YearClosingItem(closing_id={self.closing_id}, type='{self.item_type}')>"

class DataCarryForward(BaseModel):
    """Data carry forward management"""
    __tablename__ = "data_carry_forward"
    
    from_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    to_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    carry_forward_type = Column(String(50), nullable=False)  # opening_balances, inventory, customers, suppliers, items
    carry_forward_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    carry_forward_data = Column(JSON, nullable=True)
    carry_forward_errors = Column(JSON, nullable=True)
    processed_date = Column(DateTime, nullable=True)
    processed_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    from_year = relationship("FinancialYear", foreign_keys=[from_year_id])
    to_year = relationship("FinancialYear", foreign_keys=[to_year_id])
    processed_by_user = relationship("User", foreign_keys=[processed_by])
    
    def __repr__(self):
        return f"<DataCarryForward(from_year={self.from_year_id}, to_year={self.to_year_id})>"

class YearAnalytics(BaseModel):
    """Financial year analytics"""
    __tablename__ = "year_analytics"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    analytics_date = Column(Date, nullable=False)
    total_sales = Column(Numeric(15, 2), default=0)
    total_purchases = Column(Numeric(15, 2), default=0)
    total_expenses = Column(Numeric(15, 2), default=0)
    total_income = Column(Numeric(15, 2), default=0)
    net_profit = Column(Numeric(15, 2), default=0)
    total_assets = Column(Numeric(15, 2), default=0)
    total_liabilities = Column(Numeric(15, 2), default=0)
    total_equity = Column(Numeric(15, 2), default=0)
    cash_flow = Column(Numeric(15, 2), default=0)
    inventory_value = Column(Numeric(15, 2), default=0)
    customer_count = Column(Integer, default=0)
    supplier_count = Column(Integer, default=0)
    transaction_count = Column(Integer, default=0)
    analytics_data = Column(JSON, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear", back_populates="year_analytics")
    
    def __repr__(self):
        return f"<YearAnalytics(year_id={self.financial_year_id}, date='{self.analytics_date}')>"

class YearComparison(BaseModel):
    """Year comparison management"""
    __tablename__ = "year_comparison"
    
    current_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    previous_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    comparison_type = Column(String(50), nullable=False)  # financial, operational, growth
    comparison_data = Column(JSON, nullable=False)
    growth_percentage = Column(Numeric(5, 2), nullable=True)
    comparison_notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    current_year = relationship("FinancialYear", foreign_keys=[current_year_id])
    previous_year = relationship("FinancialYear", foreign_keys=[previous_year_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<YearComparison(current={self.current_year_id}, previous={self.previous_year_id})>"

class YearBackup(BaseModel):
    """Year backup management"""
    __tablename__ = "year_backup"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    backup_name = Column(String(200), nullable=False)
    backup_type = Column(String(50), nullable=False)  # full, partial, data_only, structure_only
    backup_path = Column(String(500), nullable=False)
    backup_size = Column(Integer, nullable=True)
    backup_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    backup_data = Column(JSON, nullable=True)
    backup_errors = Column(JSON, nullable=True)
    backup_date = Column(DateTime, default=datetime.utcnow)
    backup_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    backup_by_user = relationship("User", foreign_keys=[backup_by])
    
    def __repr__(self):
        return f"<YearBackup(year_id={self.financial_year_id}, name='{self.backup_name}')>"

class YearRestore(BaseModel):
    """Year restore management"""
    __tablename__ = "year_restore"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    backup_id = Column(Integer, ForeignKey('year_backup.id'), nullable=False)
    restore_name = Column(String(200), nullable=False)
    restore_type = Column(String(50), nullable=False)  # full, partial, data_only, structure_only
    restore_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    restore_data = Column(JSON, nullable=True)
    restore_errors = Column(JSON, nullable=True)
    restore_date = Column(DateTime, default=datetime.utcnow)
    restored_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    backup = relationship("YearBackup")
    restored_by_user = relationship("User", foreign_keys=[restored_by])
    
    def __repr__(self):
        return f"<YearRestore(year_id={self.financial_year_id}, backup_id={self.backup_id})>"

class YearAudit(BaseModel):
    """Year audit management"""
    __tablename__ = "year_audit"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    audit_type = Column(String(50), nullable=False)  # internal, external, compliance, financial
    audit_date = Column(DateTime, default=datetime.utcnow)
    audit_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    audit_data = Column(JSON, nullable=True)
    audit_findings = Column(JSON, nullable=True)
    audit_recommendations = Column(JSON, nullable=True)
    audit_notes = Column(Text, nullable=True)
    audited_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    audited_by_user = relationship("User", foreign_keys=[audited_by])
    
    def __repr__(self):
        return f"<YearAudit(year_id={self.financial_year_id}, type='{self.audit_type}')>"

class YearReport(BaseModel):
    """Year report management"""
    __tablename__ = "year_report"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # financial, operational, compliance, summary
    report_data = Column(JSON, nullable=False)
    report_file_path = Column(String(500), nullable=True)
    report_file_size = Column(Integer, nullable=True)
    report_status = Column(String(20), default='pending')  # pending, generated, failed
    generated_date = Column(DateTime, nullable=True)
    generated_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    generated_by_user = relationship("User", foreign_keys=[generated_by])
    
    def __repr__(self):
        return f"<YearReport(year_id={self.financial_year_id}, name='{self.report_name}')>"

class YearConfiguration(BaseModel):
    """Year configuration management"""
    __tablename__ = "year_configuration"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    
    def __repr__(self):
        return f"<YearConfiguration(year_id={self.financial_year_id}, key='{self.config_key}')>"

class YearPermission(BaseModel):
    """Year permission management"""
    __tablename__ = "year_permission"
    
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    permission_type = Column(String(50), nullable=False)  # view, edit, close, archive, restore
    is_granted = Column(Boolean, default=True)
    granted_date = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<YearPermission(year_id={self.financial_year_id}, type='{self.permission_type}')>"