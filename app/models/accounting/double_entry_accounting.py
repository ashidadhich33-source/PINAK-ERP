# backend/app/models/double_entry_accounting.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..base import BaseModel

class JournalEntry(BaseModel):
    """Journal entry management"""
    __tablename__ = "journal_entry"
    
    entry_number = Column(String(100), unique=True, nullable=False)
    entry_date = Column(Date, nullable=False)
    reference_number = Column(String(100), nullable=True)
    reference_type = Column(String(50), nullable=True)  # sale, purchase, payment, receipt, adjustment
    reference_id = Column(Integer, nullable=True)
    narration = Column(Text, nullable=True)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='draft')  # draft, posted, cancelled
    is_reversed = Column(Boolean, default=False)
    reversed_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    reversed_entry = relationship("JournalEntry", remote_side=[BaseModel.id])
    entry_items = relationship("JournalEntryItem", back_populates="journal_entry")
    
    def __repr__(self):
        return f"<JournalEntry(number='{self.entry_number}', date='{self.entry_date}')>"

class JournalEntryItem(BaseModel):
    """Individual items in journal entry"""
    __tablename__ = "journal_entry_item"
    
    entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    debit_amount = Column(Numeric(15, 2), default=0)
    credit_amount = Column(Numeric(15, 2), default=0)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="entry_items")
    account = relationship("ChartOfAccount")
    
    def __repr__(self):
        return f"<JournalEntryItem(account_id={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"

class AccountBalance(BaseModel):
    """Account balance tracking"""
    __tablename__ = "account_balance"
    
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    debit_total = Column(Numeric(15, 2), default=0)
    credit_total = Column(Numeric(15, 2), default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("ChartOfAccount")
    financial_year = relationship("FinancialYear")
    
    def __repr__(self):
        return f"<AccountBalance(account_id={self.account_id}, balance={self.current_balance})>"

class TrialBalance(BaseModel):
    """Trial balance management"""
    __tablename__ = "trial_balance"
    
    balance_date = Column(Date, nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    is_balanced = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    balance_items = relationship("TrialBalanceItem", back_populates="trial_balance")
    
    def __repr__(self):
        return f"<TrialBalance(date='{self.balance_date}', balanced={self.is_balanced})>"

class TrialBalanceItem(BaseModel):
    """Individual items in trial balance"""
    __tablename__ = "trial_balance_item"
    
    trial_balance_id = Column(Integer, ForeignKey('trial_balance.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    debit_balance = Column(Numeric(15, 2), default=0)
    credit_balance = Column(Numeric(15, 2), default=0)
    
    # Relationships
    trial_balance = relationship("TrialBalance", back_populates="balance_items")
    account = relationship("ChartOfAccount")
    
    def __repr__(self):
        return f"<TrialBalanceItem(account_id={self.account_id}, debit={self.debit_balance}, credit={self.credit_balance})>"

class BalanceSheet(BaseModel):
    """Balance sheet management"""
    __tablename__ = "balance_sheet"
    
    sheet_date = Column(Date, nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    total_assets = Column(Numeric(15, 2), default=0)
    total_liabilities = Column(Numeric(15, 2), default=0)
    total_equity = Column(Numeric(15, 2), default=0)
    is_balanced = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    sheet_items = relationship("BalanceSheetItem", back_populates="balance_sheet")
    
    def __repr__(self):
        return f"<BalanceSheet(date='{self.sheet_date}', balanced={self.is_balanced})>"

class BalanceSheetItem(BaseModel):
    """Individual items in balance sheet"""
    __tablename__ = "balance_sheet_item"
    
    balance_sheet_id = Column(Integer, ForeignKey('balance_sheet.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    account_type = Column(String(50), nullable=False)  # asset, liability, equity
    amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    balance_sheet = relationship("BalanceSheet", back_populates="sheet_items")
    account = relationship("ChartOfAccount")
    
    def __repr__(self):
        return f"<BalanceSheetItem(account_id={self.account_id}, type='{self.account_type}', amount={self.amount})>"

class ProfitLossStatement(BaseModel):
    """Profit & Loss statement management"""
    __tablename__ = "profit_loss_statement"
    
    statement_date = Column(Date, nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    total_income = Column(Numeric(15, 2), default=0)
    total_expenses = Column(Numeric(15, 2), default=0)
    net_profit = Column(Numeric(15, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    statement_items = relationship("ProfitLossItem", back_populates="profit_loss_statement")
    
    def __repr__(self):
        return f"<ProfitLossStatement(date='{self.statement_date}', profit={self.net_profit})>"

class ProfitLossItem(BaseModel):
    """Individual items in profit & loss statement"""
    __tablename__ = "profit_loss_item"
    
    statement_id = Column(Integer, ForeignKey('profit_loss_statement.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    account_type = Column(String(50), nullable=False)  # income, expense
    amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    profit_loss_statement = relationship("ProfitLossStatement", back_populates="statement_items")
    account = relationship("ChartOfAccount")
    
    def __repr__(self):
        return f"<ProfitLossItem(account_id={self.account_id}, type='{self.account_type}', amount={self.amount})>"

class CashFlowStatement(BaseModel):
    """Cash flow statement management"""
    __tablename__ = "cash_flow_statement"
    
    statement_date = Column(Date, nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    operating_cash_flow = Column(Numeric(15, 2), default=0)
    investing_cash_flow = Column(Numeric(15, 2), default=0)
    financing_cash_flow = Column(Numeric(15, 2), default=0)
    net_cash_flow = Column(Numeric(15, 2), default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    cash_flow_items = relationship("CashFlowItem", back_populates="cash_flow_statement")
    
    def __repr__(self):
        return f"<CashFlowStatement(date='{self.statement_date}', net_flow={self.net_cash_flow})>"

class CashFlowItem(BaseModel):
    """Individual items in cash flow statement"""
    __tablename__ = "cash_flow_item"
    
    statement_id = Column(Integer, ForeignKey('cash_flow_statement.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    flow_type = Column(String(50), nullable=False)  # operating, investing, financing
    amount = Column(Numeric(15, 2), default=0)
    
    # Relationships
    cash_flow_statement = relationship("CashFlowStatement", back_populates="cash_flow_items")
    account = relationship("ChartOfAccount")
    
    def __repr__(self):
        return f"<CashFlowItem(account_id={self.account_id}, type='{self.flow_type}', amount={self.amount})>"

class AccountReconciliation(BaseModel):
    """Account reconciliation management"""
    __tablename__ = "account_reconciliation"
    
    account_id = Column(Integer, ForeignKey('chart_of_account.id'), nullable=False)
    reconciliation_date = Column(Date, nullable=False)
    opening_balance = Column(Numeric(15, 2), default=0)
    closing_balance = Column(Numeric(15, 2), default=0)
    book_balance = Column(Numeric(15, 2), default=0)
    bank_balance = Column(Numeric(15, 2), default=0)
    difference = Column(Numeric(15, 2), default=0)
    status = Column(String(20), default='pending')  # pending, reconciled, disputed
    notes = Column(Text, nullable=True)
    
    # Relationships
    account = relationship("ChartOfAccount")
    reconciliation_items = relationship("ReconciliationItem", back_populates="reconciliation")
    
    def __repr__(self):
        return f"<AccountReconciliation(account_id={self.account_id}, status='{self.status}')>"

class ReconciliationItem(BaseModel):
    """Individual items in account reconciliation"""
    __tablename__ = "reconciliation_item"
    
    reconciliation_id = Column(Integer, ForeignKey('account_reconciliation.id'), nullable=False)
    transaction_id = Column(Integer, nullable=True)
    transaction_type = Column(String(50), nullable=True)
    transaction_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    book_amount = Column(Numeric(15, 2), default=0)
    bank_amount = Column(Numeric(15, 2), default=0)
    difference = Column(Numeric(15, 2), default=0)
    is_reconciled = Column(Boolean, default=False)
    
    # Relationships
    reconciliation = relationship("AccountReconciliation", back_populates="reconciliation_items")
    
    def __repr__(self):
        return f"<ReconciliationItem(transaction_id={self.transaction_id}, reconciled={self.is_reconciled})>"

class AccountingPeriod(BaseModel):
    """Accounting period management"""
    __tablename__ = "accounting_period"
    
    period_name = Column(String(100), nullable=False)
    period_type = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    financial_year_id = Column(Integer, ForeignKey('financial_year.id'), nullable=False)
    is_closed = Column(Boolean, default=False)
    closing_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    financial_year = relationship("FinancialYear")
    
    def __repr__(self):
        return f"<AccountingPeriod(name='{self.period_name}', type='{self.period_type}')>"

class JournalEntryTemplate(BaseModel):
    """Journal entry template management"""
    __tablename__ = "journal_entry_template"
    
    template_name = Column(String(100), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    template_data = Column(JSON, nullable=False)  # Store template structure
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<JournalEntryTemplate(name='{self.template_name}', code='{self.template_code}')>"

class AccountGroup(BaseModel):
    """Account group management"""
    __tablename__ = "account_group"
    
    group_name = Column(String(100), nullable=False)
    group_code = Column(String(50), unique=True, nullable=False)
    group_type = Column(String(50), nullable=False)  # asset, liability, equity, income, expense
    parent_group_id = Column(Integer, ForeignKey('account_group.id'), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    parent_group = relationship("AccountGroup", remote_side=[BaseModel.id])
    child_groups = relationship("AccountGroup", back_populates="parent_group")
    accounts = relationship("ChartOfAccount", back_populates="account_group")
    
    def __repr__(self):
        return f"<AccountGroup(name='{self.group_name}', type='{self.group_type}')>"