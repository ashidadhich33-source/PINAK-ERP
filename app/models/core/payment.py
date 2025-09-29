# backend/app/models/payment.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

# PaymentMethod moved to accounting/banking.py for enhanced functionality

class Payment(BaseModel):
    __tablename__ = "payment"
    
    # Document Information
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Transaction Details
    payment_type = Column(String(20), nullable=False)  # received, paid
    amount = Column(Numeric(12, 2), nullable=False)
    
    # Reference Information
    reference_type = Column(String(30), nullable=True)  # sales_invoice, purchase_invoice
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String(50), nullable=True)
    
    # Party Information
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=True)
    party_name = Column(String(200), nullable=False)  # Denormalized
    
    # Payment Method Details
    payment_method_id = Column(Integer, ForeignKey('payment_method.id'), nullable=False)
    payment_method_name = Column(String(50), nullable=False)  # Denormalized
    
    # Transaction Details
    transaction_reference = Column(String(100), nullable=True)  # Cheque number, UPI ref, etc.
    bank_name = Column(String(100), nullable=True)
    branch_name = Column(String(100), nullable=True)
    cheque_date = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default='completed')  # completed, pending, bounced, cancelled
    
    # Additional Information
    remarks = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    supplier = relationship("Supplier")
    payment_method = relationship("PaymentMethod")
    sales_invoice = relationship("SalesInvoice", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(number='{self.payment_number}', amount={self.amount})>"