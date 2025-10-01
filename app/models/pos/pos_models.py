# backend/app/models/pos/pos_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel

class POSSession(BaseModel):
    """POS Session model for managing POS sessions"""
    __tablename__ = "pos_session"
    
    session_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default='active')  # active, closed, suspended
    opening_cash = Column(Numeric(10, 2), default=0)
    closing_cash = Column(Numeric(10, 2), nullable=True)
    total_sales = Column(Numeric(10, 2), default=0)
    total_transactions = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="pos_sessions")
    staff = relationship("Staff", back_populates="pos_sessions")
    transactions = relationship("POSTransaction", back_populates="session")
    payments = relationship("POSPayment", back_populates="session")
    receipts = relationship("POSReceipt", back_populates="session")
    
    def __repr__(self):
        return f"<POSSession(session_name='{self.session_name}', status='{self.status}')>"

class POSTransaction(BaseModel):
    """POS Transaction model for managing POS transactions"""
    __tablename__ = "pos_transaction"
    
    transaction_number = Column(String(50), nullable=False, unique=True)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('pos_session.id'), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default='pending')  # pending, paid, refunded
    status = Column(String(20), default='active')  # active, cancelled, refunded
    notes = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="pos_transactions")
    staff = relationship("Staff", back_populates="pos_transactions")
    session = relationship("POSSession", back_populates="transactions")
    company = relationship("Company", back_populates="pos_transactions")
    payments = relationship("POSPayment", back_populates="transaction")
    receipts = relationship("POSReceipt", back_populates="transaction")
    discounts = relationship("POSDiscount", back_populates="transaction")
    
    def __repr__(self):
        return f"<POSTransaction(transaction_number='{self.transaction_number}', total_amount={self.total_amount})>"

class POSPayment(BaseModel):
    """POS Payment model for managing POS payments"""
    __tablename__ = "pos_payment"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('pos_session.id'), nullable=False)
    payment_method = Column(String(50), nullable=False)  # cash, card, upi, etc.
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    reference_number = Column(String(100), nullable=True)
    status = Column(String(20), default='completed')  # completed, pending, failed
    notes = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="payments")
    session = relationship("POSSession", back_populates="payments")
    company = relationship("Company", back_populates="pos_payments")
    
    def __repr__(self):
        return f"<POSPayment(payment_method='{self.payment_method}', amount={self.amount})>"

class POSReceipt(BaseModel):
    """POS Receipt model for managing POS receipts"""
    __tablename__ = "pos_receipt"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('pos_session.id'), nullable=False)
    receipt_number = Column(String(50), nullable=False, unique=True)
    receipt_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    receipt_type = Column(String(20), default='sale')  # sale, refund, exchange
    total_amount = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    discount_amount = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default='printed')  # printed, reprint, void
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="receipts")
    session = relationship("POSSession", back_populates="receipts")
    company = relationship("Company", back_populates="pos_receipts")
    
    def __repr__(self):
        return f"<POSReceipt(receipt_number='{self.receipt_number}', total_amount={self.total_amount})>"

class POSDiscount(BaseModel):
    """POS Discount model for managing POS discounts"""
    __tablename__ = "pos_discount"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    discount_type = Column(String(50), nullable=False)  # percentage, fixed, item
    discount_value = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(200), nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="discounts")
    company = relationship("Company", back_populates="pos_discounts")
    
    def __repr__(self):
        return f"<POSDiscount(discount_type='{self.discount_type}', discount_amount={self.discount_amount})>"

class POSStaff(BaseModel):
    """POS Staff model for managing POS staff"""
    __tablename__ = "pos_staff"
    
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=False)
    pos_access = Column(Boolean, default=True)
    can_void_transactions = Column(Boolean, default=False)
    can_apply_discounts = Column(Boolean, default=True)
    can_manage_sessions = Column(Boolean, default=False)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    staff = relationship("Staff", back_populates="pos_staff")
    company = relationship("Company", back_populates="pos_staff")
    
    def __repr__(self):
        return f"<POSStaff(staff_id={self.staff_id}, pos_access={self.pos_access})>"

class POSShift(BaseModel):
    """POS Shift model for managing POS shifts"""
    __tablename__ = "pos_shift"
    
    shift_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default='active')  # active, completed, cancelled
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="pos_shifts")
    
    def __repr__(self):
        return f"<POSShift(shift_name='{self.shift_name}', status='{self.status}')>"