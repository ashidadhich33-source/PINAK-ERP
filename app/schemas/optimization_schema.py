# backend/app/schemas/optimization_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Enums
class MetricType(str, Enum):
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_USAGE = "network_usage"
    CACHE_HIT_RATE = "cache_hit_rate"
    DATABASE_QUERY_TIME = "database_query_time"
    API_RESPONSE_TIME = "api_response_time"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class ResourceType(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"

class QueryType(str, Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class CacheType(str, Enum):
    REDIS = "redis"
    MEMORY = "memory"
    DATABASE = "database"

class IntegrationType(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    FILE_UPLOAD = "file_upload"
    EMAIL = "email"
    SMS = "sms"

# Performance Metric Schemas
class PerformanceMetricCreate(BaseModel):
    metric_type: MetricType
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float = Field(..., ge=0)
    metric_unit: str = Field(..., min_length=1, max_length=20)
    module: Optional[str] = Field(None, max_length=50)
    endpoint: Optional[str] = Field(None, max_length=200)
    session_id: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class PerformanceMetricResponse(BaseModel):
    id: int
    company_id: int
    metric_type: str
    metric_name: str
    metric_value: float
    metric_unit: str
    timestamp: datetime
    module: Optional[str]
    endpoint: Optional[str]
    user_id: Optional[int]
    session_id: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Performance Alert Schemas
class PerformanceAlertCreate(BaseModel):
    alert_type: str = Field(..., min_length=1, max_length=50)
    metric_type: MetricType
    metric_name: str = Field(..., min_length=1, max_length=100)
    threshold_value: float = Field(..., ge=0)
    actual_value: float = Field(..., ge=0)
    severity: AlertSeverity
    message: str = Field(..., min_length=1)
    additional_data: Optional[Dict[str, Any]] = None

class PerformanceAlertResponse(BaseModel):
    id: int
    company_id: int
    alert_type: str
    metric_type: str
    metric_name: str
    threshold_value: float
    actual_value: float
    severity: str
    status: str
    message: str
    triggered_at: datetime
    acknowledged_by: Optional[int]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PerformanceAlertUpdate(BaseModel):
    status: Optional[str] = None
    acknowledged_by: Optional[int] = None
    resolved_at: Optional[datetime] = None

# Performance Report Schemas
class PerformanceReportCreate(BaseModel):
    report_type: ReportType
    report_name: str = Field(..., min_length=1, max_length=200)
    report_period_start: datetime
    report_period_end: datetime
    summary_data: Optional[Dict[str, Any]] = None
    detailed_data: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None

class PerformanceReportResponse(BaseModel):
    id: int
    company_id: int
    report_type: str
    report_name: str
    report_period_start: datetime
    report_period_end: datetime
    generated_by: int
    generated_at: datetime
    summary_data: Optional[Dict[str, Any]]
    detailed_data: Optional[Dict[str, Any]]
    recommendations: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# System Resource Schemas
class SystemResourceCreate(BaseModel):
    resource_type: ResourceType
    resource_name: str = Field(..., min_length=1, max_length=100)
    usage_percentage: float = Field(..., ge=0, le=100)
    usage_value: float = Field(..., ge=0)
    usage_unit: str = Field(..., min_length=1, max_length=20)
    total_capacity: Optional[float] = Field(None, ge=0)
    available_capacity: Optional[float] = Field(None, ge=0)
    server_name: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class SystemResourceResponse(BaseModel):
    id: int
    company_id: int
    resource_type: str
    resource_name: str
    usage_percentage: float
    usage_value: float
    usage_unit: str
    total_capacity: Optional[float]
    available_capacity: Optional[float]
    timestamp: datetime
    server_name: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Database Query Schemas
class DatabaseQueryCreate(BaseModel):
    query_hash: str = Field(..., min_length=1, max_length=64)
    query_text: str = Field(..., min_length=1)
    execution_time: float = Field(..., ge=0)
    rows_returned: Optional[int] = Field(None, ge=0)
    rows_examined: Optional[int] = Field(None, ge=0)
    query_type: QueryType
    table_name: Optional[str] = Field(None, max_length=100)
    index_used: Optional[str] = Field(None, max_length=100)
    session_id: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class DatabaseQueryResponse(BaseModel):
    id: int
    company_id: int
    query_hash: str
    query_text: str
    execution_time: float
    rows_returned: Optional[int]
    rows_examined: Optional[int]
    query_type: str
    table_name: Optional[str]
    index_used: Optional[str]
    timestamp: datetime
    user_id: Optional[int]
    session_id: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# API Performance Schemas
class APIPerformanceCreate(BaseModel):
    endpoint: str = Field(..., min_length=1, max_length=200)
    method: str = Field(..., regex="^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$")
    response_time: float = Field(..., ge=0)
    status_code: int = Field(..., ge=100, le=599)
    request_size: Optional[int] = Field(None, ge=0)
    response_size: Optional[int] = Field(None, ge=0)
    session_id: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    additional_data: Optional[Dict[str, Any]] = None

class APIPerformanceResponse(BaseModel):
    id: int
    company_id: int
    endpoint: str
    method: str
    response_time: float
    status_code: int
    request_size: Optional[int]
    response_size: Optional[int]
    timestamp: datetime
    user_id: Optional[int]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Cache Performance Schemas
class CachePerformanceCreate(BaseModel):
    cache_type: CacheType
    cache_key: str = Field(..., min_length=1, max_length=200)
    operation: str = Field(..., regex="^(get|set|delete|hit|miss)$")
    response_time: float = Field(..., ge=0)
    cache_size: Optional[int] = Field(None, ge=0)
    hit_rate: Optional[float] = Field(None, ge=0, le=100)
    miss_rate: Optional[float] = Field(None, ge=0, le=100)
    session_id: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class CachePerformanceResponse(BaseModel):
    id: int
    company_id: int
    cache_type: str
    cache_key: str
    operation: str
    response_time: float
    cache_size: Optional[int]
    hit_rate: Optional[float]
    miss_rate: Optional[float]
    timestamp: datetime
    user_id: Optional[int]
    session_id: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Integration Performance Schemas
class IntegrationPerformanceCreate(BaseModel):
    integration_type: IntegrationType
    integration_name: str = Field(..., min_length=1, max_length=100)
    external_service: Optional[str] = Field(None, max_length=100)
    operation: str = Field(..., min_length=1, max_length=50)
    response_time: float = Field(..., ge=0)
    status: str = Field(..., regex="^(success|failed|timeout)$")
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    session_id: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None

class IntegrationPerformanceResponse(BaseModel):
    id: int
    company_id: int
    integration_type: str
    integration_name: str
    external_service: Optional[str]
    operation: str
    response_time: float
    status: str
    error_message: Optional[str]
    retry_count: int
    timestamp: datetime
    user_id: Optional[int]
    session_id: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Optimization Log Schemas
class OptimizationLogCreate(BaseModel):
    optimization_type: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    status: str = Field(..., regex="^(success|failed|in_progress)$")
    performance_improvement: Optional[float] = Field(None, ge=0)
    before_value: Optional[float] = None
    after_value: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

class OptimizationLogResponse(BaseModel):
    id: int
    company_id: int
    optimization_type: str
    action: str
    description: str
    status: str
    performance_improvement: Optional[float]
    before_value: Optional[float]
    after_value: Optional[float]
    executed_by: Optional[int]
    executed_at: datetime
    additional_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Performance Dashboard Schemas
class PerformanceDashboardResponse(BaseModel):
    company_id: int
    system_overview: Dict[str, Any]
    performance_metrics: List[PerformanceMetricResponse]
    active_alerts: List[PerformanceAlertResponse]
    recent_optimizations: List[OptimizationLogResponse]
    resource_usage: List[SystemResourceResponse]
    slow_queries: List[DatabaseQueryResponse]
    api_performance: List[APIPerformanceResponse]
    cache_performance: List[CachePerformanceResponse]
    integration_performance: List[IntegrationPerformanceResponse]
    
    class Config:
        from_attributes = True

# Performance Analytics Schemas
class PerformanceAnalyticsResponse(BaseModel):
    company_id: int
    period_start: datetime
    period_end: datetime
    total_requests: int
    average_response_time: float
    error_rate: float
    throughput: float
    resource_utilization: Dict[str, Any]
    performance_trends: Dict[str, Any]
    recommendations: List[str]
    
    class Config:
        from_attributes = True