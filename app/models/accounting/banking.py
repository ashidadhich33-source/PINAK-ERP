# backend/app/models/accounting/banking.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..base import BaseModel

class BankAccountType(PyEnum):
    """Bank account types"""
    CURRENT = "current"
    SAVINGS = "savings"
    CASH_CREDIT = "cash_credit"
    OVERDRAFT = "overdraft"
    LOAN = "loan"
    FIXED_DEPOSIT = "fixed_deposit"
    RECURRING_DEPOSIT = "recurring_deposit"

class PaymentMethodType(PyEnum):
    """Payment method types"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    DEMAND_DRAFT = "demand_draft"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    DIGITAL_WALLET = "digital_wallet"
    NEFT = "neft"
    RTGS = "rtgs"
    IMPS = "imps"

class StatementStatus(PyEnum):
    """Bank statement status"""
    DRAFT = "draft"
    IMPORTED = "imported"
    RECONCILED = "reconciled"
    CLOSED = "closed"

class ReconciliationStatus(PyEnum):
    """Reconciliation status"""
    UNRECONCILED = "unreconciled"
    PARTIALLY_RECONCILED = "partially_reconciled"
    FULLY_RECONCILED = "fully_reconciled"

class BankAccount(BaseModel):
    """Bank account management"""
    __tablename__ = "bank_account"
    
    account_name = Column(String(100), nullable=False)
    account_number = Column(String(50), nullable=False)
    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(20), nullable=True)  # Bank code or SWIFT code
    account_type = Column(Enum(BankAccountType), nullable=False)
    currency_code = Column(String(3), default='INR', nullable=False)
    opening_balance = Column(Numeric(15, 2), default=0)
    current_balance = Column(Numeric(15, 2), default=0)
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    ifsc_code = Column(String(11), nullable=True)
    micr_code = Column(String(9), nullable=True)
    branch_name = Column(String(100), nullable=True)
    branch_address = Column(Text, nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    bank_statements = relationship("BankStatement", back_populates="bank_account")
    payments = relationship("Payment", back_populates="bank_account")
    
    def __repr__(self):
        return f"<BankAccount(name='{self.account_name}', number='{self.account_number}')>"

class BankStatement(BaseModel):
    """Bank statement management"""
    __tablename__ = "bank_statement"
    
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    statement_date = Column(Date, nullable=False)
    balance_start = Column(Numeric(15, 2), default=0)
    balance_end = Column(Numeric(15, 2), default=0)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    total_entries = Column(Integer, default=0)
    status = Column(Enum(StatementStatus), default=StatementStatus.DRAFT)
    imported_date = Column(DateTime, nullable=True)
    imported_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    bank_account = relationship("BankAccount", back_populates="bank_statements")
    imported_by_user = relationship("User", foreign_keys=[imported_by])
    statement_lines = relationship("BankStatementLine", back_populates="statement")
    
    def __repr__(self):
        return f"<BankStatement(date='{self.statement_date}', balance={self.balance_end})>"

class BankStatementLine(BaseModel):
    """Bank statement lines"""
    __tablename__ = "bank_statement_line"
    
    statement_id = Column(Integer, ForeignKey('bank_statement.id'), nullable=False)
    line_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    partner_id = Column(Integer, ForeignKey('partner.id'), nullable=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)
    is_reconciled = Column(Boolean, default=False)
    reconciled_amount = Column(Numeric(15, 2), default=0)
    reconciliation_date = Column(DateTime, nullable=True)
    reconciled_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    statement = relationship("BankStatement", back_populates="statement_lines")
    partner = relationship("Partner")
    payment = relationship("Payment")
    reconciled_by_user = relationship("User", foreign_keys=[reconciled_by])
    
    def __repr__(self):
        return f"<BankStatementLine(amount={self.amount}, description='{self.description}')>"

class PaymentMethod(BaseModel):
    """Payment methods"""
    __tablename__ = "payment_method"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    payment_type = Column(Enum(PaymentMethodType), nullable=False)
    is_active = Column(Boolean, default=True)
    requires_bank_account = Column(Boolean, default=False)
    requires_reference = Column(Boolean, default=False)
    processing_fee = Column(Numeric(10, 2), default=0)
    processing_fee_type = Column(String(20), default='fixed')  # fixed, percentage
    description = Column(Text, nullable=True)
    configuration = Column(JSON, nullable=True)  # Method-specific configuration
    
    # Relationships
    payments = relationship("Payment", back_populates="payment_method")
    
    def __repr__(self):
        return f"<PaymentMethod(name='{self.name}', type='{self.payment_type}')>"

class PaymentTerm(BaseModel):
    """Payment terms"""
    __tablename__ = "payment_term"
    
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    days = Column(Integer, nullable=False)
    discount_days = Column(Integer, nullable=True)
    discount_percentage = Column(Numeric(5, 2), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="payment_term")
    bills = relationship("Bill", back_populates="payment_term")
    
    def __repr__(self):
        return f"<PaymentTerm(name='{self.name}', days={self.days})>"

class CashRounding(BaseModel):
    """Cash rounding rules"""
    __tablename__ = "cash_rounding"
    
    name = Column(String(100), nullable=False)
    rounding_method = Column(String(50), nullable=False)  # up, down, half_up, half_down
    rounding_precision = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    payments = relationship("Payment", back_populates="cash_rounding")
    
    def __repr__(self):
        return f"<CashRounding(name='{self.name}', method='{self.rounding_method}')>"

class BankReconciliation(BaseModel):
    """Bank reconciliation records"""
    __tablename__ = "bank_reconciliation"
    
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    statement_id = Column(Integer, ForeignKey('bank_statement.id'), nullable=True)
    reconciliation_date = Column(Date, nullable=False)
    balance_start = Column(Numeric(15, 2), default=0)
    balance_end = Column(Numeric(15, 2), default=0)
    total_reconciled = Column(Numeric(15, 2), default=0)
    unreconciled_amount = Column(Numeric(15, 2), default=0)
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.UNRECONCILED)
    reconciled_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    reconciled_date = Column(DateTime, default=datetime.now, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    bank_account = relationship("BankAccount")
    statement = relationship("BankStatement")
    reconciled_by_user = relationship("User", foreign_keys=[reconciled_by])
    reconciliation_lines = relationship("ReconciliationLine", back_populates="reconciliation")
    
    def __repr__(self):
        return f"<BankReconciliation(date='{self.reconciliation_date}', status='{self.status}')>"

class ReconciliationLine(BaseModel):
    """Reconciliation line items"""
    __tablename__ = "reconciliation_line"
    
    reconciliation_id = Column(Integer, ForeignKey('bank_reconciliation.id'), nullable=False)
    statement_line_id = Column(Integer, ForeignKey('bank_statement_line.id'), nullable=True)
    payment_id = Column(Integer, ForeignKey('payment.id'), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    reconciled_amount = Column(Numeric(15, 2), default=0)
    is_fully_reconciled = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    reconciliation = relationship("BankReconciliation", back_populates="reconciliation_lines")
    statement_line = relationship("BankStatementLine")
    payment = relationship("Payment")
    
    def __repr__(self):
        return f"<ReconciliationLine(amount={self.amount}, reconciled={self.reconciled_amount})>"

class BankImportTemplate(BaseModel):
    """Bank import templates"""
    __tablename__ = "bank_import_template"
    
    name = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=False)
    file_format = Column(String(50), nullable=False)  # csv, excel, ofx, qif
    template_config = Column(JSON, nullable=False)  # Column mappings and configuration
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_date = Column(DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<BankImportTemplate(name='{self.name}', bank='{self.bank_name}')>"

class BankImportLog(BaseModel):
    """Bank import logs"""
    __tablename__ = "bank_import_log"
    
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('bank_import_template.id'), nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    import_date = Column(DateTime, default=datetime.now, nullable=False)
    imported_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    total_lines = Column(Integer, default=0)
    imported_lines = Column(Integer, default=0)
    error_lines = Column(Integer, default=0)
    status = Column(String(20), default='processing')  # processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Relationships
    bank_account = relationship("BankAccount")
    template = relationship("BankImportTemplate")
    imported_by_user = relationship("User", foreign_keys=[imported_by])
    
    def __repr__(self):
        return f"<BankImportLog(file='{self.file_name}', status='{self.status}')>"