# backend/app/models/advanced_reporting.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class ReportType(PyEnum):
    """Report Type"""
    TABLE = "table"
    CHART = "chart"
    DASHBOARD = "dashboard"
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPARATIVE = "comparative"
    TREND = "trend"

class ChartType(PyEnum):
    """Chart Type"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"

class ReportStatus(PyEnum):
    """Report Status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"

class ReportBuilder(BaseModel):
    """Advanced Report Builder"""
    __tablename__ = "report_builder"
    
    # Report Information
    report_name = Column(String(200), nullable=False)
    report_description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    report_category = Column(String(100), nullable=True)
    
    # Report Configuration
    report_config = Column(JSON, nullable=False)
    data_source = Column(String(100), nullable=False)  # table name or query
    sql_query = Column(Text, nullable=True)
    
    # Visual Configuration
    chart_type = Column(Enum(ChartType), nullable=True)
    chart_config = Column(JSON, nullable=True)
    layout_config = Column(JSON, nullable=True)
    
    # Filter Configuration
    filter_config = Column(JSON, nullable=True)
    parameter_config = Column(JSON, nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Report Status
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    report_instances = relationship("ReportInstance", back_populates="report_builder")
    report_schedules = relationship("ReportSchedule", back_populates="report_builder")
    
    def __repr__(self):
        return f"<ReportBuilder(name='{self.report_name}', type='{self.report_type}')>"

class ReportInstance(BaseModel):
    """Report Instance - Generated Reports"""
    __tablename__ = "report_instance"
    
    # Report Information
    report_builder_id = Column(Integer, ForeignKey('report_builder.id'), nullable=False)
    instance_name = Column(String(200), nullable=False)
    instance_description = Column(Text, nullable=True)
    
    # Report Data
    report_data = Column(JSON, nullable=False)
    report_metadata = Column(JSON, nullable=True)
    report_summary = Column(JSON, nullable=True)
    
    # Generation Information
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    generation_duration = Column(Integer, nullable=True)  # seconds
    
    # Filter Parameters
    filter_parameters = Column(JSON, nullable=True)
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    
    # Export Information
    export_formats = Column(JSON, nullable=True)  # ["pdf", "excel", "csv"]
    export_paths = Column(JSON, nullable=True)
    
    # Access Information
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Relationships
    report_builder = relationship("ReportBuilder", back_populates="report_instances")
    generated_by_user = relationship("User", foreign_keys=[generated_by])
    
    def __repr__(self):
        return f"<ReportInstance(name='{self.instance_name}', generated_at='{self.generated_at}')>"

class ReportSchedule(BaseModel):
    """Report Scheduling"""
    __tablename__ = "report_schedule"
    
    # Schedule Information
    report_builder_id = Column(Integer, ForeignKey('report_builder.id'), nullable=False)
    schedule_name = Column(String(200), nullable=False)
    schedule_description = Column(Text, nullable=True)
    
    # Schedule Configuration
    schedule_type = Column(String(20), nullable=False)  # daily, weekly, monthly, custom
    schedule_config = Column(JSON, nullable=False)
    cron_expression = Column(String(100), nullable=True)
    
    # Schedule Status
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    
    # Notification Configuration
    email_notification = Column(Boolean, default=False)
    email_recipients = Column(JSON, nullable=True)
    whatsapp_notification = Column(Boolean, default=False)
    whatsapp_recipients = Column(JSON, nullable=True)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    report_builder = relationship("ReportBuilder", back_populates="report_schedules")
    created_by_user = relationship("User", foreign_keys=[created_by])
    schedule_logs = relationship("ReportScheduleLog", back_populates="schedule")
    
    def __repr__(self):
        return f"<ReportSchedule(name='{self.schedule_name}', type='{self.schedule_type}')>"

class ReportScheduleLog(BaseModel):
    """Report Schedule Execution Logs"""
    __tablename__ = "report_schedule_log"
    
    # Schedule Information
    schedule_id = Column(Integer, ForeignKey('report_schedule.id'), nullable=False)
    
    # Execution Information
    execution_started_at = Column(DateTime, default=datetime.utcnow)
    execution_completed_at = Column(DateTime, nullable=True)
    execution_duration = Column(Integer, nullable=True)  # seconds
    
    # Execution Status
    execution_status = Column(String(20), nullable=False)  # success, failed, cancelled
    error_message = Column(Text, nullable=True)
    
    # Report Generation
    report_instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=True)
    report_generated = Column(Boolean, default=False)
    
    # Notification Status
    email_sent = Column(Boolean, default=False)
    whatsapp_sent = Column(Boolean, default=False)
    
    # Relationships
    schedule = relationship("ReportSchedule", back_populates="schedule_logs")
    report_instance = relationship("ReportInstance")
    
    def __repr__(self):
        return f"<ReportScheduleLog(schedule_id={self.schedule_id}, status='{self.execution_status}')>"

class ReportDashboard(BaseModel):
    """Report Dashboard Configuration"""
    __tablename__ = "report_dashboard"
    
    # Dashboard Information
    dashboard_name = Column(String(200), nullable=False)
    dashboard_description = Column(Text, nullable=True)
    dashboard_type = Column(String(50), nullable=False)  # sales, inventory, financial, operational
    
    # Dashboard Configuration
    dashboard_config = Column(JSON, nullable=False)
    layout_config = Column(JSON, nullable=True)
    theme_config = Column(JSON, nullable=True)
    
    # Widget Configuration
    widgets = Column(JSON, nullable=True)
    widget_positions = Column(JSON, nullable=True)
    
    # Access Control
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Dashboard Status
    status = Column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ReportDashboard(name='{self.dashboard_name}', type='{self.dashboard_type}')>"

class ReportWidget(BaseModel):
    """Report Widget Configuration"""
    __tablename__ = "report_widget"
    
    # Widget Information
    widget_name = Column(String(200), nullable=False)
    widget_type = Column(String(50), nullable=False)  # chart, table, metric, kpi
    widget_description = Column(Text, nullable=True)
    
    # Widget Configuration
    widget_config = Column(JSON, nullable=False)
    data_source = Column(String(100), nullable=False)
    sql_query = Column(Text, nullable=True)
    
    # Visual Configuration
    chart_type = Column(Enum(ChartType), nullable=True)
    chart_config = Column(JSON, nullable=True)
    display_config = Column(JSON, nullable=True)
    
    # Filter Configuration
    filter_config = Column(JSON, nullable=True)
    parameter_config = Column(JSON, nullable=True)
    
    # Widget Status
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ReportWidget(name='{self.widget_name}', type='{self.widget_type}')>"

class ReportExport(BaseModel):
    """Report Export Configuration"""
    __tablename__ = "report_export"
    
    # Export Information
    report_instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=False)
    export_format = Column(String(20), nullable=False)  # pdf, excel, csv, json
    export_config = Column(JSON, nullable=True)
    
    # Export Status
    export_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    export_path = Column(String(500), nullable=True)
    export_size = Column(Integer, nullable=True)  # bytes
    
    # Export Information
    exported_at = Column(DateTime, nullable=True)
    exported_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    download_count = Column(Integer, default=0)
    
    # Relationships
    report_instance = relationship("ReportInstance")
    exported_by_user = relationship("User", foreign_keys=[exported_by])
    
    def __repr__(self):
        return f"<ReportExport(format='{self.export_format}', status='{self.export_status}')>"

class ReportAnalytics(BaseModel):
    """Report Analytics and Usage Tracking"""
    __tablename__ = "report_analytics"
    
    # Analytics Information
    report_builder_id = Column(Integer, ForeignKey('report_builder.id'), nullable=True)
    report_instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=True)
    dashboard_id = Column(Integer, ForeignKey('report_dashboard.id'), nullable=True)
    
    # Usage Metrics
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Performance Metrics
    generation_time = Column(Integer, nullable=True)  # seconds
    data_size = Column(Integer, nullable=True)  # bytes
    query_execution_time = Column(Integer, nullable=True)  # seconds
    
    # User Metrics
    unique_users = Column(Integer, default=0)
    user_engagement = Column(JSON, nullable=True)
    
    # Date Range
    analytics_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    report_builder = relationship("ReportBuilder")
    report_instance = relationship("ReportInstance")
    dashboard = relationship("ReportDashboard")
    
    def __repr__(self):
        return f"<ReportAnalytics(date='{self.analytics_date}', views={self.view_count})>"

class ReportPermission(BaseModel):
    """Report Access Permissions"""
    __tablename__ = "report_permission"
    
    # Permission Information
    report_builder_id = Column(Integer, ForeignKey('report_builder.id'), nullable=True)
    dashboard_id = Column(Integer, ForeignKey('report_dashboard.id'), nullable=True)
    
    # User/Role Information
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    
    # Permission Types
    can_view = Column(Boolean, default=False)
    can_edit = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_share = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)
    can_schedule = Column(Boolean, default=False)
    
    # Relationships
    report_builder = relationship("ReportBuilder")
    dashboard = relationship("ReportDashboard")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    
    def __repr__(self):
        return f"<ReportPermission(user_id={self.user_id}, can_view={self.can_view})>"

class ReportCache(BaseModel):
    """Report Data Caching"""
    __tablename__ = "report_cache"
    
    # Cache Information
    cache_key = Column(String(200), unique=True, nullable=False, index=True)
    report_builder_id = Column(Integer, ForeignKey('report_builder.id'), nullable=False)
    
    # Cache Data
    cached_data = Column(JSON, nullable=False)
    cache_metadata = Column(JSON, nullable=True)
    
    # Cache Configuration
    cache_ttl = Column(Integer, default=3600)  # seconds
    cache_size = Column(Integer, nullable=True)  # bytes
    
    # Cache Status
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, nullable=True)
    access_count = Column(Integer, default=0)
    
    # Relationships
    report_builder = relationship("ReportBuilder")
    
    def __repr__(self):
        return f"<ReportCache(key='{self.cache_key}', valid={self.is_valid})>"