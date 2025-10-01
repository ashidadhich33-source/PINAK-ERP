from sqlalchemy import Column, String, Numeric, ForeignKey, DateTime, Date, Boolean, Text
from sqlalchemy.orm import relationship
from ..base import BaseModel
from datetime import datetime

class ExpenseHead(BaseModel):
    __tablename__ = "expense_heads"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    budget_monthly = Column(Numeric(12, 2))
    requires_approval = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(36))
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(36))
    
    # Relationships
    expenses = relationship("Expense", back_populates="head")

class Expense(BaseModel):
    __tablename__ = "expenses"
    
    id = Column(String(36), primary_key=True)
    date = Column(Date, nullable=False)
    head_id = Column(String(36), ForeignKey("expense_heads.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    mode = Column(String(20))  # cash, bank, online
    payment_mode_id = Column(String(36), ForeignKey("payment_modes.id"))
    reference_no = Column(String(50))
    vendor_name = Column(String(255))
    bill_no = Column(String(50))
    description = Column(Text)
    status = Column(String(20), default='pending')  # pending, approved, rejected, cancelled
    created_by = Column(String(36))
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(String(36))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    updated_by = Column(String(36))
    
    # Relationships
    head = relationship("ExpenseHead", back_populates="expenses")
    payment_mode = relationship("PaymentMode")
    created_by_user = relationship("User", foreign_keys=[created_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])