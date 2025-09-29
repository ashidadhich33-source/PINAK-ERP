# backend/app/models/sales/sales_exchange_integration.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.base import BaseModel
import enum

class ExchangeStatus(str, enum.Enum):
    """Sales exchange status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class ExchangeType(str, enum.Enum):
    """Sales exchange type enumeration"""
    SIZE_EXCHANGE = "size_exchange"
    COLOR_EXCHANGE = "color_exchange"
    MODEL_EXCHANGE = "model_exchange"
    DEFECTIVE_EXCHANGE = "defective_exchange"
    CUSTOMER_PREFERENCE = "customer_preference"
    UPGRADE_EXCHANGE = "upgrade_exchange"
    DOWNGRADE_EXCHANGE = "downgrade_exchange"

class ExchangeReason(str, enum.Enum):
    """Sales exchange reason enumeration"""
    WRONG_SIZE = "wrong_size"
    WRONG_COLOR = "wrong_color"
    WRONG_MODEL = "wrong_model"
    DEFECTIVE_PRODUCT = "defective_product"
    CUSTOMER_CHANGE_MIND = "customer_change_mind"
    BETTER_OPTION_AVAILABLE = "better_option_available"
    UPGRADE_DESIRED = "upgrade_desired"
    DOWNGRADE_DESIRED = "downgrade_desired"

# Core Exchange Models
class SalesExchange(BaseModel):
    """Sales exchange management for B2C retail"""
    __tablename__ = "sales_exchange"
    
    exchange_number = Column(String(100), unique=True, nullable=False)
    exchange_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.id'), nullable=True)
    original_bill_id = Column(Integer, ForeignKey('sale_bill.id'), nullable=False)
    original_bill_number = Column(String(100), nullable=False)
    original_bill_date = Column(Date, nullable=False)
    exchange_reason = Column(String(200), nullable=True)
    exchange_type = Column(String(50), default='size_exchange')
    exchange_notes = Column(Text, nullable=True)
    
    # Exchange amounts
    original_items_value = Column(Numeric(12, 2), default=0)
    new_items_value = Column(Numeric(12, 2), default=0)
    difference_amount = Column(Numeric(12, 2), default=0)  # Positive = customer pays more, Negative = store owes customer
    exchange_fee = Column(Numeric(10, 2), default=0)  # Optional exchange fee
    
    # GST calculations
    original_cgst_amount = Column(Numeric(10, 2), default=0)
    original_sgst_amount = Column(Numeric(10, 2), default=0)
    original_igst_amount = Column(Numeric(10, 2), default=0)
    original_total_gst_amount = Column(Numeric(10, 2), default=0)
    
    new_cgst_amount = Column(Numeric(10, 2), default=0)
    new_sgst_amount = Column(Numeric(10, 2), default=0)
    new_igst_amount = Column(Numeric(10, 2), default=0)
    new_total_gst_amount = Column(Numeric(10, 2), default=0)
    
    gst_difference = Column(Numeric(10, 2), default=0)
    net_difference = Column(Numeric(12, 2), default=0)
    
    status = Column(String(20), default='pending')
    processed_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    
    # Relationships
    customer = relationship("Customer")
    staff = relationship("Staff")
    original_bill = relationship("SaleBill")
    exchange_items = relationship("SalesExchangeItem", back_populates="exchange_record")
    new_bill = relationship("SaleBill", foreign_keys="SaleBill.exchange_id")
    
    def __repr__(self):
        return f"<SalesExchange(number='{self.exchange_number}', customer_id={self.customer_id})>"

class SalesExchangeItem(BaseModel):
    """Individual items in sales exchange"""
    __tablename__ = "sales_exchange_item"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    original_bill_item_id = Column(Integer, ForeignKey('sale_bill_item.id'), nullable=True)
    
    # Original item details
    original_quantity = Column(Numeric(10, 2), nullable=False)
    original_unit_price = Column(Numeric(10, 2), nullable=False)
    original_total_amount = Column(Numeric(10, 2), nullable=False)
    original_gst_rate = Column(Numeric(5, 2), nullable=True)
    original_cgst_amount = Column(Numeric(10, 2), nullable=True)
    original_sgst_amount = Column(Numeric(10, 2), nullable=True)
    original_igst_amount = Column(Numeric(10, 2), nullable=True)
    
    # New item details (if different item)
    new_item_id = Column(Integer, ForeignKey('item.id'), nullable=True)
    new_variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    new_quantity = Column(Numeric(10, 2), nullable=False)
    new_unit_price = Column(Numeric(10, 2), nullable=False)
    new_total_amount = Column(Numeric(10, 2), nullable=False)
    new_gst_rate = Column(Numeric(5, 2), nullable=True)
    new_cgst_amount = Column(Numeric(10, 2), nullable=True)
    new_sgst_amount = Column(Numeric(10, 2), nullable=True)
    new_igst_amount = Column(Numeric(10, 2), nullable=True)
    
    # Exchange calculations
    item_difference = Column(Numeric(10, 2), default=0)  # new_total - original_total
    exchange_reason = Column(String(200), nullable=True)
    condition_notes = Column(Text, nullable=True)
    
    # Relationships
    exchange_record = relationship("SalesExchange", back_populates="exchange_items")
    item = relationship("Item", foreign_keys=[item_id])
    variant = relationship("InventoryVariant", foreign_keys=[variant_id])
    new_item = relationship("Item", foreign_keys=[new_item_id])
    new_variant = relationship("InventoryVariant", foreign_keys=[new_variant_id])
    original_bill_item = relationship("SaleBillItem")
    
    def __repr__(self):
        return f"<SalesExchangeItem(item_id={self.item_id}, new_item_id={self.new_item_id})>"

# Exchange Workflow Models
class SalesExchangeWorkflow(BaseModel):
    """Sales exchange workflow management"""
    __tablename__ = "sales_exchange_workflow"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    workflow_step = Column(String(50), nullable=False)  # approval, processing, completion
    assigned_to = Column(Integer, ForeignKey('user.id'), nullable=True)
    assigned_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # pending, completed, rejected
    comments = Column(Text, nullable=True)
    priority = Column(String(10), default='medium')  # low, medium, high, urgent
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    assigned_user = relationship("User")
    
    def __repr__(self):
        return f"<SalesExchangeWorkflow(exchange_id={self.exchange_id}, step='{self.workflow_step}')>"

class SalesExchangeDocument(BaseModel):
    """Sales exchange document management"""
    __tablename__ = "sales_exchange_document"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    document_type = Column(String(50), nullable=False)  # exchange_form, receipt, invoice, photo
    document_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)
    upload_date = Column(DateTime, default=func.now())
    uploaded_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_encrypted = Column(Boolean, default=False)
    version = Column(String(20), default='1.0')
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<SalesExchangeDocument(exchange_id={self.exchange_id}, type='{self.document_type}')>"

# Exchange Inventory Models
class SalesExchangeInventory(BaseModel):
    """Sales exchange inventory integration"""
    __tablename__ = "sales_exchange_inventory"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=False)
    
    # Original item inventory
    original_quantity_returned = Column(Numeric(10, 2), nullable=False)
    original_serial_numbers = Column(Text, nullable=True)  # JSON array
    original_batch_numbers = Column(Text, nullable=True)  # JSON array
    original_expiry_dates = Column(Text, nullable=True)  # JSON array
    original_condition = Column(String(20), default='good')  # good, defective, damaged
    
    # New item inventory
    new_item_id = Column(Integer, ForeignKey('item.id'), nullable=True)
    new_variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    new_quantity_issued = Column(Numeric(10, 2), nullable=False)
    new_serial_numbers = Column(Text, nullable=True)  # JSON array
    new_batch_numbers = Column(Text, nullable=True)  # JSON array
    new_expiry_dates = Column(Text, nullable=True)  # JSON array
    
    # Stock adjustments
    original_stock_adjustment = Column(Boolean, default=True)
    new_stock_adjustment = Column(Boolean, default=True)
    adjustment_type_original = Column(String(20), default='increase')  # increase stock
    adjustment_type_new = Column(String(20), default='decrease')  # decrease stock
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    item = relationship("Item", foreign_keys=[item_id])
    variant = relationship("InventoryVariant", foreign_keys=[variant_id])
    new_item = relationship("Item", foreign_keys=[new_item_id])
    new_variant = relationship("InventoryVariant", foreign_keys=[new_variant_id])
    warehouse = relationship("Warehouse")
    
    def __repr__(self):
        return f"<SalesExchangeInventory(exchange_id={self.exchange_id}, item_id={self.item_id})>"

# Exchange Accounting Models
class SalesExchangeAccounting(BaseModel):
    """Sales exchange accounting integration"""
    __tablename__ = "sales_exchange_accounting"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    journal_entry_id = Column(Integer, ForeignKey('journal_entry.id'), nullable=True)
    debit_account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    credit_account_id = Column(Integer, ForeignKey('account.id'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0)
    net_amount = Column(Numeric(12, 2), nullable=False)
    accounting_date = Column(Date, nullable=False)
    exchange_type = Column(String(20), default='exchange')  # exchange, adjustment
    notes = Column(Text, nullable=True)
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    journal_entry = relationship("JournalEntry")
    debit_account = relationship("Account", foreign_keys=[debit_account_id])
    credit_account = relationship("Account", foreign_keys=[credit_account_id])
    
    def __repr__(self):
        return f"<SalesExchangeAccounting(exchange_id={self.exchange_id}, amount={self.amount})>"

# Exchange GST Models
class SalesExchangeGST(BaseModel):
    """Sales exchange GST integration"""
    __tablename__ = "sales_exchange_gst"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    gst_number = Column(String(15), nullable=True)
    place_of_supply = Column(String(100), nullable=True)
    place_of_supply_type = Column(String(20), default='intrastate')
    
    # Original GST
    original_cgst_rate = Column(Numeric(5, 2), default=0)
    original_sgst_rate = Column(Numeric(5, 2), default=0)
    original_igst_rate = Column(Numeric(5, 2), default=0)
    original_cess_rate = Column(Numeric(5, 2), default=0)
    
    # New GST
    new_cgst_rate = Column(Numeric(5, 2), default=0)
    new_sgst_rate = Column(Numeric(5, 2), default=0)
    new_igst_rate = Column(Numeric(5, 2), default=0)
    new_cess_rate = Column(Numeric(5, 2), default=0)
    
    # GST differences
    cgst_difference = Column(Numeric(10, 2), default=0)
    sgst_difference = Column(Numeric(10, 2), default=0)
    igst_difference = Column(Numeric(10, 2), default=0)
    cess_difference = Column(Numeric(10, 2), default=0)
    total_gst_difference = Column(Numeric(10, 2), default=0)
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    
    def __repr__(self):
        return f"<SalesExchangeGST(exchange_id={self.exchange_id}, gst_difference={self.total_gst_difference})>"

# Exchange Customer Models
class SalesExchangeCustomer(BaseModel):
    """Sales exchange customer integration"""
    __tablename__ = "sales_exchange_customer"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    
    # Customer exchange preferences
    exchange_policy_accepted = Column(Boolean, default=False)
    exchange_policy_date = Column(DateTime, nullable=True)
    customer_signature = Column(Text, nullable=True)  # Digital signature
    
    # Customer satisfaction
    customer_satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating
    customer_feedback = Column(Text, nullable=True)
    would_recommend = Column(Boolean, nullable=True)
    
    # Exchange history
    total_exchanges = Column(Integer, default=0)
    exchange_frequency = Column(String(20), default='first_time')  # first_time, frequent, regular
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    customer = relationship("Customer")
    
    def __repr__(self):
        return f"<SalesExchangeCustomer(exchange_id={self.exchange_id}, customer_id={self.customer_id})>"

# Exchange Analytics Models
class SalesExchangeAnalytics(BaseModel):
    """Sales exchange analytics integration"""
    __tablename__ = "sales_exchange_analytics"
    
    exchange_id = Column(Integer, ForeignKey('sales_exchange.id'), nullable=False)
    analytics_provider = Column(String(50), nullable=False)  # google_analytics, mixpanel, custom
    event_type = Column(String(50), nullable=False)  # exchange_initiated, exchange_completed, exchange_cancelled
    event_data = Column(Text, nullable=True)  # JSON data
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    session_id = Column(String(100), nullable=True)
    page_url = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    # Exchange specific analytics
    exchange_duration_minutes = Column(Numeric(8, 2), nullable=True)
    staff_efficiency_score = Column(Integer, nullable=True)  # 1-100
    customer_satisfaction_score = Column(Integer, nullable=True)  # 1-100
    
    # Relationships
    exchange_record = relationship("SalesExchange")
    user = relationship("User")
    
    def __repr__(self):
        return f"<SalesExchangeAnalytics(exchange_id={self.exchange_id}, provider='{self.analytics_provider}')>"