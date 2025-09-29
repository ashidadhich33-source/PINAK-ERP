# backend/app/models/purchase/purchase_enhanced_integration.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class IntegrationStatus(PyEnum):
    """Integration Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SyncStatus(PyEnum):
    """Sync Status"""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    ERROR = "error"

class PurchaseInventoryIntegration(BaseModel):
    """Link Purchases to Inventory Management"""
    __tablename__ = "purchase_inventory_integration"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Inventory References
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    variant_id = Column(Integer, ForeignKey('inventory_variant.id'), nullable=True)
    warehouse_id = Column(Integer, ForeignKey('warehouse.id'), nullable=True)
    location_id = Column(Integer, ForeignKey('warehouse_location.id'), nullable=True)
    
    # Stock Movement Details
    quantity_moved = Column(Numeric(15, 2), nullable=False)
    quantity_available = Column(Numeric(15, 2), nullable=False)
    quantity_reserved = Column(Numeric(15, 2), default=0)
    quantity_allocated = Column(Numeric(15, 2), default=0)
    stock_movement_type = Column(String(50), nullable=False)  # purchase, return, adjustment, transfer
    
    # Serial/Batch Tracking
    serial_numbers = Column(JSON, nullable=True)  # List of serial numbers
    batch_numbers = Column(JSON, nullable=True)  # List of batch numbers
    expiry_dates = Column(JSON, nullable=True)  # List of expiry dates
    
    # Integration Status
    integration_status = Column(Enum(IntegrationStatus), default=IntegrationStatus.PENDING)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    last_sync_date = Column(DateTime, nullable=True)
    sync_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional inventory data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    item = relationship("Item")
    variant = relationship("InventoryVariant")
    warehouse = relationship("Warehouse")
    location = relationship("WarehouseLocation")
    
    def __repr__(self):
        return f"<PurchaseInventoryIntegration(purchase_id={self.purchase_invoice_id}, item_id={self.item_id})>"

class PurchaseSupplierIntegration(BaseModel):
    """Link Purchases to Supplier Management"""
    __tablename__ = "purchase_supplier_integration"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Supplier Reference
    supplier_id = Column(Integer, ForeignKey('supplier.id'), nullable=False)
    
    # Supplier Details
    supplier_name = Column(String(255), nullable=False)
    supplier_email = Column(String(255), nullable=True)
    supplier_phone = Column(String(20), nullable=True)
    supplier_address = Column(Text, nullable=True)
    supplier_gstin = Column(String(15), nullable=True)
    
    # Credit Management
    credit_limit = Column(Numeric(15, 2), nullable=True)
    credit_used = Column(Numeric(15, 2), default=0)
    credit_available = Column(Numeric(15, 2), nullable=True)
    payment_terms_id = Column(Integer, ForeignKey('payment_term.id'), nullable=True)
    
    # Supplier Analytics
    total_purchases = Column(Numeric(15, 2), default=0)
    total_returns = Column(Numeric(15, 2), default=0)
    average_order_value = Column(Numeric(15, 2), default=0)
    last_purchase_date = Column(Date, nullable=True)
    supplier_performance_score = Column(Numeric(5, 2), nullable=True)  # Performance score out of 100
    
    # Integration Status
    integration_status = Column(Enum(IntegrationStatus), default=IntegrationStatus.PENDING)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    last_sync_date = Column(DateTime, nullable=True)
    sync_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional supplier data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    supplier = relationship("Supplier")
    payment_terms = relationship("PaymentTerm")
    
    def __repr__(self):
        return f"<PurchaseSupplierIntegration(purchase_id={self.purchase_invoice_id}, supplier_id={self.supplier_id})>"

class PurchasePerformanceOptimization(BaseModel):
    """Link Purchases to Performance Optimization"""
    __tablename__ = "purchase_performance_optimization"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Performance Metrics
    processing_time_ms = Column(Integer, nullable=True)  # Processing time in milliseconds
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    memory_usage_mb = Column(Numeric(10, 2), nullable=True)  # Memory usage in MB
    cpu_usage_percent = Column(Numeric(5, 2), nullable=True)  # CPU usage percentage
    database_queries = Column(Integer, nullable=True)  # Number of database queries
    cache_hits = Column(Integer, nullable=True)  # Number of cache hits
    cache_misses = Column(Integer, nullable=True)  # Number of cache misses
    
    # Optimization Settings
    enable_caching = Column(Boolean, default=True)
    enable_compression = Column(Boolean, default=True)
    enable_indexing = Column(Boolean, default=True)
    batch_size = Column(Integer, default=100)
    timeout_seconds = Column(Integer, default=30)
    
    # Performance Status
    performance_score = Column(Numeric(5, 2), nullable=True)  # Performance score out of 100
    optimization_level = Column(String(20), default='medium')  # low, medium, high, maximum
    last_optimization_date = Column(DateTime, nullable=True)
    optimization_attempts = Column(Integer, default=0)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional performance data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchasePerformanceOptimization(purchase_id={self.purchase_invoice_id}, score={self.performance_score})>"

class PurchaseUserExperience(BaseModel):
    """Link Purchases to User Experience Enhancement"""
    __tablename__ = "purchase_user_experience"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # User Experience Metrics
    user_satisfaction_score = Column(Numeric(3, 2), nullable=True)  # Score out of 5
    ease_of_use_score = Column(Numeric(3, 2), nullable=True)  # Score out of 5
    interface_responsiveness = Column(Numeric(3, 2), nullable=True)  # Score out of 5
    feature_completeness = Column(Numeric(3, 2), nullable=True)  # Score out of 5
    error_rate = Column(Numeric(5, 2), nullable=True)  # Error rate percentage
    
    # User Interaction Data
    time_to_complete = Column(Integer, nullable=True)  # Time in seconds
    clicks_required = Column(Integer, nullable=True)  # Number of clicks
    form_abandonment_rate = Column(Numeric(5, 2), nullable=True)  # Abandonment rate percentage
    help_requests = Column(Integer, default=0)  # Number of help requests
    user_feedback = Column(Text, nullable=True)  # User feedback text
    
    # UI/UX Enhancements
    custom_theme = Column(String(50), nullable=True)  # Custom theme name
    layout_preference = Column(String(50), nullable=True)  # Layout preference
    font_size = Column(String(20), nullable=True)  # Font size preference
    color_scheme = Column(String(50), nullable=True)  # Color scheme preference
    accessibility_features = Column(JSON, nullable=True)  # Accessibility features
    
    # Experience Status
    experience_score = Column(Numeric(5, 2), nullable=True)  # Overall experience score
    improvement_suggestions = Column(Text, nullable=True)  # Improvement suggestions
    last_improvement_date = Column(DateTime, nullable=True)
    improvement_attempts = Column(Integer, default=0)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional UX data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseUserExperience(purchase_id={self.purchase_invoice_id}, score={self.experience_score})>"

class PurchaseRealTimeSync(BaseModel):
    """Link Purchases to Real-time Synchronization"""
    __tablename__ = "purchase_real_time_sync"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Sync Configuration
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(20), default='real_time')  # real_time, immediate, scheduled
    sync_interval_seconds = Column(Integer, default=0)  # For scheduled sync
    sync_priority = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Sync Status
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)
    last_sync_date = Column(DateTime, nullable=True)
    next_sync_date = Column(DateTime, nullable=True)
    sync_attempts = Column(Integer, default=0)
    sync_success_count = Column(Integer, default=0)
    sync_failure_count = Column(Integer, default=0)
    
    # Sync Data
    sync_data = Column(JSON, nullable=True)  # Data to sync
    sync_metadata = Column(JSON, nullable=True)  # Sync metadata
    conflict_resolution = Column(String(50), default='auto')  # auto, manual, priority
    
    # Error Handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_interval_seconds = Column(Integer, default=60)
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional sync data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseRealTimeSync(purchase_id={self.purchase_invoice_id}, status='{self.sync_status}')>"

class PurchaseAnalyticsIntegration(BaseModel):
    """Link Purchases to Analytics Integration"""
    __tablename__ = "purchase_analytics_integration"
    
    # Purchase Reference
    purchase_invoice_id = Column(Integer, ForeignKey('purchase_invoice.id'), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey('purchase_order.id'), nullable=True)
    purchase_return_id = Column(Integer, ForeignKey('purchase_return.id'), nullable=True)
    
    # Analytics Configuration
    analytics_enabled = Column(Boolean, default=True)
    tracking_enabled = Column(Boolean, default=True)
    analytics_provider = Column(String(50), nullable=True)  # google_analytics, mixpanel, custom
    tracking_id = Column(String(100), nullable=True)  # Analytics tracking ID
    
    # Analytics Data
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    session_duration = Column(Integer, nullable=True)  # Session duration in seconds
    bounce_rate = Column(Numeric(5, 2), nullable=True)  # Bounce rate percentage
    conversion_rate = Column(Numeric(5, 2), nullable=True)  # Conversion rate percentage
    
    # User Behavior
    user_actions = Column(JSON, nullable=True)  # User action tracking
    user_path = Column(JSON, nullable=True)  # User navigation path
    user_segments = Column(JSON, nullable=True)  # User segmentation data
    user_preferences = Column(JSON, nullable=True)  # User preferences
    
    # Performance Analytics
    load_time = Column(Integer, nullable=True)  # Page load time in milliseconds
    render_time = Column(Integer, nullable=True)  # Render time in milliseconds
    api_response_time = Column(Integer, nullable=True)  # API response time in milliseconds
    error_rate = Column(Numeric(5, 2), nullable=True)  # Error rate percentage
    
    # Additional Information
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional analytics data
    
    # Relationships
    purchase_invoice = relationship("PurchaseInvoice")
    purchase_order = relationship("PurchaseOrder")
    purchase_return = relationship("PurchaseReturn")
    
    def __repr__(self):
        return f"<PurchaseAnalyticsIntegration(purchase_id={self.purchase_invoice_id}, provider='{self.analytics_provider}')>"