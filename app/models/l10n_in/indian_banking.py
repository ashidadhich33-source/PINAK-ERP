# backend/app/models/l10n_in/indian_banking.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from enum import Enum as PyEnum
from ..base import BaseModel

class PaymentMethodType(PyEnum):
    """Indian Payment Method Types"""
    CASH = "cash"
    CHEQUE = "cheque"
    NEFT = "neft"
    RTGS = "rtgs"
    UPI = "upi"
    CARD = "card"
    WALLET = "wallet"
    DD = "dd"  # Demand Draft
    ONLINE = "online"

class UPIProvider(PyEnum):
    """UPI Provider Types"""
    PHONEPE = "phonepe"
    PAYTM = "paytm"
    GOOGLE_PAY = "google_pay"
    BHIM = "bhim"
    AMAZON_PAY = "amazon_pay"
    WHATSAPP_PAY = "whatsapp_pay"
    OTHER = "other"

class BankAccount(BaseModel):
    """Indian Bank Account Model"""
    __tablename__ = "indian_bank_account"
    
    # Basic Information
    account_holder_name = Column(String(200), nullable=False)
    account_number = Column(String(50), nullable=False, index=True)
    ifsc_code = Column(String(11), nullable=False, index=True)
    
    # Bank Information
    bank_name = Column(String(200), nullable=False)
    bank_branch = Column(String(200), nullable=True)
    bank_address = Column(Text, nullable=True)
    
    # Account Type
    account_type = Column(String(20), nullable=False)  # savings, current, fixed, recurring
    is_primary = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="bank_accounts")
    
    def __repr__(self):
        return f"<BankAccount(account_number='{self.account_number}', bank='{self.bank_name}')>"

class UPIAccount(BaseModel):
    """UPI Account Model"""
    __tablename__ = "upi_account"
    
    # UPI Information
    upi_id = Column(String(100), nullable=False, unique=True, index=True)
    upi_provider = Column(Enum(UPIProvider), nullable=False)
    upi_name = Column(String(100), nullable=True)
    
    # Bank Account Link
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    bank_account = relationship("BankAccount", back_populates="upi_accounts")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="upi_accounts")
    
    def __repr__(self):
        return f"<UPIAccount(upi_id='{self.upi_id}', provider='{self.upi_provider}')>"

class DigitalWallet(BaseModel):
    """Digital Wallet Model"""
    __tablename__ = "digital_wallet"
    
    # Wallet Information
    wallet_name = Column(String(100), nullable=False)
    wallet_provider = Column(Enum(UPIProvider), nullable=False)
    wallet_id = Column(String(100), nullable=False)
    wallet_phone = Column(String(15), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="digital_wallets")
    
    def __repr__(self):
        return f"<DigitalWallet(wallet_name='{self.wallet_name}', provider='{self.wallet_provider}')>"

class ChequeBook(BaseModel):
    """Cheque Book Model"""
    __tablename__ = "cheque_book"
    
    # Cheque Book Information
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    bank_account = relationship("BankAccount", back_populates="cheque_books")
    
    # Cheque Details
    cheque_book_no = Column(String(50), nullable=False)
    start_cheque_no = Column(String(20), nullable=False)
    end_cheque_no = Column(String(20), nullable=False)
    total_cheques = Column(Integer, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    issued_date = Column(Date, nullable=False)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="cheque_books")
    
    def __repr__(self):
        return f"<ChequeBook(book_no='{self.cheque_book_no}', bank_account='{self.bank_account_id}')>"

class Cheque(BaseModel):
    """Cheque Model"""
    __tablename__ = "cheque"
    
    # Cheque Information
    cheque_number = Column(String(20), nullable=False, index=True)
    cheque_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Party Information
    payee_name = Column(String(200), nullable=False)
    payee_address = Column(Text, nullable=True)
    
    # Bank Information
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    bank_account = relationship("BankAccount", back_populates="cheques")
    
    cheque_book_id = Column(Integer, ForeignKey('cheque_book.id'), nullable=True)
    cheque_book = relationship("ChequeBook", back_populates="cheques")
    
    # Status
    status = Column(String(20), default='issued')  # issued, presented, cleared, bounced, cancelled
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="cheques")
    
    def __repr__(self):
        return f"<Cheque(cheque_no='{self.cheque_number}', amount={self.amount}, payee='{self.payee_name}')>"

class NEFTRTGS(BaseModel):
    """NEFT/RTGS Transaction Model"""
    __tablename__ = "neft_rtgs"
    
    # Transaction Information
    transaction_type = Column(String(4), nullable=False)  # NEFT, RTGS
    transaction_id = Column(String(50), nullable=False, unique=True, index=True)
    transaction_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Bank Information
    from_bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    from_bank_account = relationship("BankAccount", foreign_keys=[from_bank_account_id])
    
    to_bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=True)
    to_bank_account = relationship("BankAccount", foreign_keys=[to_bank_account_id])
    
    # Party Information
    beneficiary_name = Column(String(200), nullable=False)
    beneficiary_account = Column(String(50), nullable=False)
    beneficiary_ifsc = Column(String(11), nullable=False)
    
    # Status
    status = Column(String(20), default='pending')  # pending, processed, failed, cancelled
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="neft_rtgs")
    
    def __repr__(self):
        return f"<NEFTRTGS(type='{self.transaction_type}', amount={self.amount}, status='{self.status}')>"

class PaymentGateway(BaseModel):
    """Payment Gateway Model"""
    __tablename__ = "payment_gateway"
    
    # Gateway Information
    gateway_name = Column(String(100), nullable=False)
    gateway_provider = Column(String(100), nullable=False)  # Razorpay, PayU, etc.
    gateway_id = Column(String(100), nullable=False)
    gateway_key = Column(String(200), nullable=False)  # Encrypted
    gateway_secret = Column(String(200), nullable=False)  # Encrypted
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_sandbox = Column(Boolean, default=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="payment_gateways")
    
    def __repr__(self):
        return f"<PaymentGateway(gateway_name='{self.gateway_name}', provider='{self.gateway_provider}')>"

class BankReconciliation(BaseModel):
    """Bank Reconciliation Model"""
    __tablename__ = "indian_bank_reconciliation"
    
    # Reconciliation Information
    bank_account_id = Column(Integer, ForeignKey('bank_account.id'), nullable=False)
    bank_account = relationship("BankAccount", back_populates="reconciliations")
    
    reconciliation_date = Column(Date, nullable=False)
    opening_balance = Column(Numeric(15, 2), nullable=False)
    closing_balance = Column(Numeric(15, 2), nullable=False)
    
    # Reconciliation Data
    total_debits = Column(Numeric(15, 2), nullable=False)
    total_credits = Column(Numeric(15, 2), nullable=False)
    difference_amount = Column(Numeric(15, 2), nullable=False)
    
    # Status
    is_reconciled = Column(Boolean, default=False)
    reconciliation_notes = Column(Text, nullable=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    company = relationship("Company", back_populates="bank_reconciliations")
    
    def __repr__(self):
        return f"<BankReconciliation(bank_account='{self.bank_account_id}', date='{self.reconciliation_date}')>"

# Add relationships to BankAccount
BankAccount.upi_accounts = relationship("UPIAccount", back_populates="bank_account", cascade="all, delete-orphan")
BankAccount.cheque_books = relationship("ChequeBook", back_populates="bank_account", cascade="all, delete-orphan")
BankAccount.cheques = relationship("Cheque", back_populates="bank_account", cascade="all, delete-orphan")
BankAccount.reconciliations = relationship("BankReconciliation", back_populates="bank_account", cascade="all, delete-orphan")

# Add relationships to ChequeBook
ChequeBook.cheques = relationship("Cheque", back_populates="cheque_book", cascade="all, delete-orphan")