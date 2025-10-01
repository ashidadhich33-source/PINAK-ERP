# backend/app/models/advanced_api/advanced_api_models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel

class APIMonitoring(BaseModel):
    """API Monitoring model for managing API monitoring"""
    __tablename__ = "api_monitoring"
    
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    response_time = Column(Numeric(10, 3), nullable=False)  # in milliseconds
    status_code = Column(Integer, nullable=False)
    request_size = Column(Integer, nullable=True)  # in bytes
    response_size = Column(Integer, nullable=True)  # in bytes
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_monitoring")
    company = relationship("Company", back_populates="api_monitoring")
    
    def __repr__(self):
        return f"<APIMonitoring(endpoint='{self.endpoint}', response_time={self.response_time})>"

class APILog(BaseModel):
    """API Log model for managing API logs"""
    __tablename__ = "api_log"
    
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(Text, nullable=True)  # JSON request data
    response_data = Column(Text, nullable=True)  # JSON response data
    status_code = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Numeric(10, 3), nullable=False)  # in milliseconds
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_logs")
    company = relationship("Company", back_populates="api_logs")
    
    def __repr__(self):
        return f"<APILog(endpoint='{self.endpoint}', status_code={self.status_code})>"

class APIRateLimit(BaseModel):
    """API Rate Limit model for managing API rate limits"""
    __tablename__ = "api_rate_limit"
    
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    rate_limit = Column(Integer, nullable=False)  # requests per minute
    current_count = Column(Integer, default=0)
    window_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_rate_limits")
    company = relationship("Company", back_populates="api_rate_limits")
    
    def __repr__(self):
        return f"<APIRateLimit(endpoint='{self.endpoint}', rate_limit={self.rate_limit})>"

class APICache(BaseModel):
    """API Cache model for managing API cache"""
    __tablename__ = "api_cache"
    
    cache_key = Column(String(255), nullable=False, unique=True)
    cache_data = Column(Text, nullable=False)  # JSON cached data
    cache_type = Column(String(50), nullable=False)  # response, query, session
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)
    miss_count = Column(Integer, default=0)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="api_cache")
    
    def __repr__(self):
        return f"<APICache(cache_key='{self.cache_key}', cache_type='{self.cache_type}')>"

class APIBatch(BaseModel):
    """API Batch model for managing API batches"""
    __tablename__ = "api_batch"
    
    batch_name = Column(String(100), nullable=False)
    batch_type = Column(String(50), nullable=False)  # import, export, sync, etc.
    batch_data = Column(Text, nullable=False)  # JSON batch data
    batch_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="api_batches")
    
    def __repr__(self):
        return f"<APIBatch(batch_name='{self.batch_name}', batch_status='{self.batch_status}')>"

class APIQueue(BaseModel):
    """API Queue model for managing API queues"""
    __tablename__ = "api_queue"
    
    queue_name = Column(String(100), nullable=False)
    queue_type = Column(String(50), nullable=False)  # email, sms, notification, etc.
    queue_data = Column(Text, nullable=False)  # JSON queue data
    queue_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    priority = Column(Integer, default=0)  # 0 = normal, 1 = high, 2 = urgent
    scheduled_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    company_id = Column(Integer, ForeignKey('company.id'), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="api_queues")
    
    def __repr__(self):
        return f"<APIQueue(queue_name='{self.queue_name}', queue_status='{self.queue_status}')>"