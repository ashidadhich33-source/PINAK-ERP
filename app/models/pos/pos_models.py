# backend/app/models/pos/pos_models.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.base import BaseModel
import enum

class POSSessionStatus(str, enum.Enum):
    """POS session status enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"
    LOCKED = "locked"

class POSPaymentMethod(str, enum.Enum):
    """POS payment method enumeration"""
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    UPI = "upi"
    DIGITAL_WALLET = "digital_wallet"
    NET_BANKING = "net_banking"
    CHEQUE = "cheque"
    GIFT_CARD = "gift_card"
    LOYALTY_POINTS = "loyalty_points"

class POSTransactionType(str, enum.Enum):
    """POS transaction type enumeration"""
    SALE = "sale"
    RETURN = "return"
    EXCHANGE = "exchange"
    REFUND = "refund"
    VOID = "void"
    DISCOUNT = "discount"

# Core POS Models
class POSSession(BaseModel):
    """POS session management"""
    __tablename__ = "pos_session"
    
    session_number = Column(String(100), unique=True, nullable=False)
    session_date = Column(Date, nullable=False)
    store_id = Column(Integer, ForeignKey('store.id'), nullable=False)
    cashier_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    opening_cash = Column(Numeric(12, 2), default=0)
    closing_cash = Column(Numeric(12, 2), nullable=True)
    expected_cash = Column(Numeric(12, 2), nullable=True)
    cash_difference = Column(Numeric(12, 2), nullable=True)
    total_sales = Column(Numeric(12, 2), default=0)
    total_transactions = Column(Integer, default=0)
    total_returns = Column(Numeric(12, 2), default=0)
    total_exchanges = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default='open')
    opened_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    store = relationship("Store")
    cashier = relationship("User")
    transactions = relationship("POSTransaction", back_populates="session")
    
    def __repr__(self):
        return f"<POSSession(number='{self.session_number}', cashier_id={self.cashier_id})>"

class POSTransaction(BaseModel):
    """POS transaction management"""
    __tablename__ = "pos_transaction"
    
    transaction_number = Column(String(100), unique=True, nullable=False)
    session_id = Column(Integer, ForeignKey('pos_session.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=True)
    transaction_type = Column(String(20), default='sale')
    transaction_date = Column(DateTime, default=func.now())
    
    # Transaction amounts
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    
    # Payment details
    payment_method = Column(String(20), nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_status = Column(String(20), default='completed')
    
    # GST details
    cgst_amount = Column(Numeric(10, 2), default=0)
    sgst_amount = Column(Numeric(10, 2), default=0)
    igst_amount = Column(Numeric(10, 2), default=0)
    total_gst_amount = Column(Numeric(10, 2), default=0)
    
    # Transaction status
    status = Column(String(20), default='completed')
    is_void = Column(Boolean, default=False)
    void_reason = Column(String(200), nullable=True)
    void_date = Column(DateTime, nullable=True)
    
    # Exchange/Return details
    original_transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=True)
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=True)
    return_id = Column(Integer, ForeignKey('sale_return.id'), nullable=True)
    
    # Relationships
    session = relationship("POSSession", back_populates="transactions")
    customer = relationship("Customer")
    original_transaction = relationship("POSTransaction", remote_side="POSTransaction.id")
    exchange = relationship("SalesExchange")
    return_record = relationship("SaleReturn")
    items = relationship("POSTransactionItem", back_populates="transaction")
    payments = relationship("POSPayment", back_populates="transaction")
    
    # Discount and CRM relationships
    discounts = relationship("POSTransactionDiscount", back_populates="transaction")
    customer_discounts = relationship("POSCustomerDiscount", back_populates="transaction")
    loyalty_transactions = relationship("POSLoyaltyTransaction", back_populates="transaction")
    discount_calculations = relationship("POSDiscountCalculation", back_populates="transaction")
    promotion_usage = relationship("POSPromotionUsage")
    discount_audit = relationship("POSDiscountAudit", back_populates="transaction")
    
    def __repr__(self):
        return f"<POSTransaction(number='{self.transaction_number}', amount={self.total_amount})>"

class POSTransactionItem(BaseModel):
    """Individual items in POS transaction"""
    __tablename__ = "pos_transaction_item"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    tax_rate = Column(Numeric(5, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(10, 2), nullable=False)
    
    # Serial/Batch tracking
    serial_numbers = Column(Text, nullable=True)  # JSON array
    batch_numbers = Column(Text, nullable=True)  # JSON array
    expiry_dates = Column(Text, nullable=True)  # JSON array
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="items")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    
    def __repr__(self):
        return f"<POSTransactionItem(item_id={self.item_id}, quantity={self.quantity})>"

class POSPayment(BaseModel):
    """POS payment processing"""
    __tablename__ = "pos_payment"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    payment_method = Column(String(20), nullable=False)
    payment_amount = Column(Numeric(12, 2), nullable=False)
    payment_reference = Column(String(100), nullable=True)
    payment_date = Column(DateTime, default=func.now())
    payment_status = Column(String(20), default='completed')
    
    # Card payment details
    card_number = Column(String(20), nullable=True)
    card_type = Column(String(20), nullable=True)
    card_holder_name = Column(String(100), nullable=True)
    authorization_code = Column(String(50), nullable=True)
    
    # UPI/Digital wallet details
    upi_id = Column(String(100), nullable=True)
    wallet_type = Column(String(20), nullable=True)
    wallet_transaction_id = Column(String(100), nullable=True)
    
    # Bank transfer details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    transaction_id_bank = Column(String(100), nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction", back_populates="payments")
    
    def __repr__(self):
        return f"<POSPayment(transaction_id={self.transaction_id}, amount={self.payment_amount})>"

# POS Store Management
class Store(BaseModel):
    """Store management for POS"""
    __tablename__ = "store"
    
    store_code = Column(String(50), unique=True, nullable=False)
    store_name = Column(String(200), nullable=False)
    store_address = Column(Text, nullable=True)
    store_city = Column(String(100), nullable=True)
    store_state = Column(String(100), nullable=True)
    store_pincode = Column(String(10), nullable=True)
    store_phone = Column(String(20), nullable=True)
    store_email = Column(String(100), nullable=True)
    
    # Store settings
    currency = Column(String(3), default='INR')
    timezone = Column(String(50), default='Asia/Kolkata')
    tax_number = Column(String(50), nullable=True)
    gst_number = Column(String(15), nullable=True)
    
    # Store status
    is_active = Column(Boolean, default=True)
    opening_time = Column(String(10), nullable=True)
    closing_time = Column(String(10), nullable=True)
    
    # Relationships
    sessions = relationship("POSSession")
    staff = relationship("StoreStaff")
    
    def __repr__(self):
        return f"<Store(code='{self.store_code}', name='{self.store_name}')>"

class StoreStaff(BaseModel):
    """Store staff management"""
    __tablename__ = "store_staff"
    
    store_id = Column(Integer, ForeignKey('store.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    role = Column(String(50), nullable=False)  # manager, cashier, supervisor
    is_active = Column(Boolean, default=True)
    assigned_date = Column(Date, default=func.now())
    
    # Relationships
    store = relationship("Store")
    user = relationship("User")
    
    def __repr__(self):
        return f"<StoreStaff(store_id={self.store_id}, user_id={self.user_id})>"

# POS Receipt Management
class POSReceipt(BaseModel):
    """POS receipt management"""
    __tablename__ = "pos_receipt"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    receipt_number = Column(String(100), unique=True, nullable=False)
    receipt_date = Column(DateTime, default=func.now())
    receipt_type = Column(String(20), default='sale')  # sale, return, exchange
    receipt_template = Column(String(50), default='standard')
    
    # Receipt content
    receipt_header = Column(Text, nullable=True)
    receipt_footer = Column(Text, nullable=True)
    receipt_content = Column(Text, nullable=True)
    
    # Receipt status
    is_printed = Column(Boolean, default=False)
    printed_at = Column(DateTime, nullable=True)
    print_count = Column(Integer, default=0)
    
    # Digital receipt
    digital_receipt_url = Column(String(500), nullable=True)
    qr_code = Column(Text, nullable=True)
    
    # Relationships
    transaction = relationship("POSTransaction")
    
    def __repr__(self):
        return f"<POSReceipt(number='{self.receipt_number}', transaction_id={self.transaction_id})>"

# POS Inventory Integration
class POSInventory(BaseModel):
    """POS inventory integration"""
    __tablename__ = "pos_inventory"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=False)
    quantity_sold = Column(Numeric(10, 2), nullable=False)
    quantity_returned = Column(Numeric(10, 2), default=0)
    stock_adjustment = Column(Boolean, default=True)
    adjustment_type = Column(String(20), default='decrease')  # decrease, increase
    serial_numbers = Column(Text, nullable=True)  # JSON array
    batch_numbers = Column(Text, nullable=True)  # JSON array
    expiry_dates = Column(Text, nullable=True)  # JSON array
    
    # Relationships
    transaction = relationship("POSTransaction")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    warehouse = relationship("Warehouse")
    
    def __repr__(self):
        return f"<POSInventory(transaction_id={self.transaction_id}, item_id={self.item_id})>"

# POS Analytics
class POSAnalytics(BaseModel):
    """POS analytics tracking"""
    __tablename__ = "pos_analytics"
    
    transaction_id = Column(Integer, ForeignKey('pos_transaction.id'), nullable=False)
    analytics_provider = Column(String(50), nullable=False)  # google_analytics, mixpanel, custom
    event_type = Column(String(50), nullable=False)  # sale, return, exchange, payment
    event_data = Column(Text, nullable=True)  # JSON data
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # POS specific analytics
    transaction_duration_seconds = Column(Integer, nullable=True)
    items_count = Column(Integer, nullable=True)
    payment_method_used = Column(String(20), nullable=True)
    customer_type = Column(String(20), nullable=True)  # new, returning, vip
    
    # Relationships
    transaction = relationship("POSTransaction")
    user = relationship("User")
    
    def __repr__(self):
        return f"<POSAnalytics(transaction_id={self.transaction_id}, provider='{self.analytics_provider}')>"