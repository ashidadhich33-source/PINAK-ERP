# backend/app/models/optimization/performance_models.py
from sqlalchemy import Column, Integer, String, DateTime, Date, Decimal, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, date
from decimal import Decimal

from ..base import BaseModel

# Performance Metric Model
class PerformanceMetric(BaseModel):
    """Performance metrics tracking"""
    __tablename__ = "performance_metrics"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)  # response_time, throughput, error_rate, etc.
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=False)  # ms, requests/sec, %, etc.
    timestamp = Column(DateTime, default=func.now())
    module = Column(String(50), nullable=True)  # sales, purchase, inventory, etc.
    endpoint = Column(String(200), nullable=True)  # API endpoint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="performance_metrics")
    user = relationship("User")

# Performance Alert Model
class PerformanceAlert(BaseModel):
    """Performance alerts and thresholds"""
    __tablename__ = "performance_alerts"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # threshold_exceeded, anomaly_detected, etc.
    metric_type = Column(String(50), nullable=False)
    metric_name = Column(String(100), nullable=False)
    threshold_value = Column(Float, nullable=False)
    actual_value = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    message = Column(Text, nullable=False)
    triggered_at = Column(DateTime, default=func.now())
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="performance_alerts")
    acknowledged_user = relationship("User")

# Performance Report Model
class PerformanceReport(BaseModel):
    """Performance reports and analytics"""
    __tablename__ = "performance_reports"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, custom
    report_name = Column(String(200), nullable=False)
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=func.now())
    
    # Report data
    summary_data = Column(JSON, nullable=True)
    detailed_data = Column(JSON, nullable=True)
    recommendations = Column(Text, nullable=True)
    status = Column(String(20), default="generated")  # generated, reviewed, archived
    
    # Relationships
    company = relationship("Company", back_populates="performance_reports")
    generated_user = relationship("User")

# System Resource Model
class SystemResource(BaseModel):
    """System resource usage tracking"""
    __tablename__ = "system_resources"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # cpu, memory, disk, network
    resource_name = Column(String(100), nullable=False)
    usage_percentage = Column(Float, nullable=False)
    usage_value = Column(Float, nullable=False)
    usage_unit = Column(String(20), nullable=False)  # %, MB, GB, etc.
    total_capacity = Column(Float, nullable=True)
    available_capacity = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    server_name = Column(String(100), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="system_resources")

# Database Query Model
class DatabaseQuery(BaseModel):
    """Database query performance tracking"""
    __tablename__ = "database_queries"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    query_hash = Column(String(64), nullable=False)  # Hash of the query
    query_text = Column(Text, nullable=False)
    execution_time = Column(Float, nullable=False)  # in milliseconds
    rows_returned = Column(Integer, nullable=True)
    rows_examined = Column(Integer, nullable=True)
    query_type = Column(String(20), nullable=False)  # SELECT, INSERT, UPDATE, DELETE
    table_name = Column(String(100), nullable=True)
    index_used = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="database_queries")
    user = relationship("User")

# API Performance Model
class APIPerformance(BaseModel):
    """API performance tracking"""
    __tablename__ = "api_performance"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    response_time = Column(Float, nullable=False)  # in milliseconds
    status_code = Column(Integer, nullable=False)
    request_size = Column(Integer, nullable=True)  # in bytes
    response_size = Column(Integer, nullable=True)  # in bytes
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="api_performance")
    user = relationship("User")

# Cache Performance Model
class CachePerformance(BaseModel):
    """Cache performance tracking"""
    __tablename__ = "cache_performance"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    cache_type = Column(String(50), nullable=False)  # redis, memory, database
    cache_key = Column(String(200), nullable=False)
    operation = Column(String(20), nullable=False)  # get, set, delete, hit, miss
    response_time = Column(Float, nullable=False)  # in milliseconds
    cache_size = Column(Integer, nullable=True)  # in bytes
    hit_rate = Column(Float, nullable=True)  # percentage
    miss_rate = Column(Float, nullable=True)  # percentage
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="cache_performance")
    user = relationship("User")

# Integration Performance Model
class IntegrationPerformance(BaseModel):
    """Integration performance tracking"""
    __tablename__ = "integration_performance"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    integration_type = Column(String(50), nullable=False)  # api, webhook, file_upload, etc.
    integration_name = Column(String(100), nullable=False)
    external_service = Column(String(100), nullable=True)
    operation = Column(String(50), nullable=False)  # sync, async, batch, etc.
    response_time = Column(Float, nullable=False)  # in milliseconds
    status = Column(String(20), nullable=False)  # success, failed, timeout
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="integration_performance")
    user = relationship("User")

# Optimization Log Model
class OptimizationLog(BaseModel):
    """Optimization activities log"""
    __tablename__ = "optimization_logs"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    optimization_type = Column(String(50), nullable=False)  # database, cache, api, integration
    action = Column(String(100), nullable=False)  # index_created, cache_cleared, etc.
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)  # success, failed, in_progress
    performance_improvement = Column(Float, nullable=True)  # percentage improvement
    before_value = Column(Float, nullable=True)
    after_value = Column(Float, nullable=True)
    executed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, default=func.now())
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="optimization_logs")
    executed_user = relationship("User")