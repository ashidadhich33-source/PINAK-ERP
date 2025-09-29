# backend/app/models/report_studio.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class ReportCategory(BaseModel):
    """Report category management"""
    __tablename__ = "report_category"
    
    category_name = Column(String(100), nullable=False)
    category_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_category_id = Column(Integer, ForeignKey('report_category.id'), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    notes = Column(Text, nullable=True)
    
    # Relationships
    parent_category = relationship("ReportCategory", remote_side=[BaseModel.id])
    child_categories = relationship("ReportCategory", back_populates="parent_category")
    reports = relationship("ReportTemplate", back_populates="category")
    
    def __repr__(self):
        return f"<ReportCategory(name='{self.category_name}', code='{self.category_code}')>"

# ReportTemplate moved to accounting/advanced_reporting.py for enhanced functionality

class ReportInstance(BaseModel):
    """Report instance management"""
    __tablename__ = "report_instance"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    instance_name = Column(String(200), nullable=False)
    instance_code = Column(String(100), unique=True, nullable=False)
    parameters = Column(JSON, nullable=True)  # Instance parameters
    filters = Column(JSON, nullable=True)  # Instance filters
    data = Column(JSON, nullable=True)  # Report data
    status = Column(String(20), default='draft')  # draft, generated, failed, scheduled
    generated_date = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(20), nullable=True)  # pdf, excel, csv, json
    file_size = Column(Integer, nullable=True)
    execution_time = Column(Numeric(10, 3), nullable=True)  # in seconds
    row_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="report_instances")
    report_views = relationship("ReportView", back_populates="report_instance")
    
    def __repr__(self):
        return f"<ReportInstance(name='{self.instance_name}', status='{self.status}')>"

class ReportView(BaseModel):
    """Report view management"""
    __tablename__ = "report_view"
    
    instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=False)
    view_name = Column(String(200), nullable=False)
    view_type = Column(String(50), nullable=False)  # table, chart, dashboard, summary
    view_config = Column(JSON, nullable=False)  # View configuration
    chart_type = Column(String(50), nullable=True)  # bar, line, pie, scatter, etc.
    chart_config = Column(JSON, nullable=True)  # Chart configuration
    filters = Column(JSON, nullable=True)  # View filters
    sorting = Column(JSON, nullable=True)  # Sorting configuration
    grouping = Column(JSON, nullable=True)  # Grouping configuration
    aggregation = Column(JSON, nullable=True)  # Aggregation configuration
    display_order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    report_instance = relationship("ReportInstance", back_populates="report_views")
    
    def __repr__(self):
        return f"<ReportView(name='{self.view_name}', type='{self.view_type}')>"

class ReportSchedule(BaseModel):
    """Report schedule management"""
    __tablename__ = "report_schedule"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    schedule_name = Column(String(200), nullable=False)
    schedule_type = Column(String(50), nullable=False)  # daily, weekly, monthly, yearly, custom
    cron_expression = Column(String(100), nullable=True)
    schedule_time = Column(String(20), nullable=True)  # HH:MM format
    schedule_date = Column(Date, nullable=True)
    parameters = Column(JSON, nullable=True)  # Schedule parameters
    email_recipients = Column(JSON, nullable=True)  # Email recipients
    email_subject = Column(String(200), nullable=True)
    email_body = Column(Text, nullable=True)
    file_format = Column(String(20), default='pdf')
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="report_schedules")
    schedule_logs = relationship("ReportScheduleLog", back_populates="schedule")
    
    def __repr__(self):
        return f"<ReportSchedule(name='{self.schedule_name}', type='{self.schedule_type}')>"

class ReportScheduleLog(BaseModel):
    """Report schedule execution log"""
    __tablename__ = "report_schedule_log"
    
    schedule_id = Column(Integer, ForeignKey('report_schedule.id'), nullable=False)
    execution_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), nullable=False)  # success, failed, running
    execution_time = Column(Numeric(10, 3), nullable=True)  # in seconds
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    email_sent = Column(Boolean, default=False)
    email_recipients = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    schedule = relationship("ReportSchedule", back_populates="schedule_logs")
    
    def __repr__(self):
        return f"<ReportScheduleLog(schedule_id={self.schedule_id}, status='{self.status}')>"

class ReportBuilder(BaseModel):
    """Report builder configuration"""
    __tablename__ = "report_builder"
    
    builder_name = Column(String(200), nullable=False)
    builder_code = Column(String(100), unique=True, nullable=False)
    builder_type = Column(String(50), nullable=False)  # visual, sql, api
    data_sources = Column(JSON, nullable=False)  # Available data sources
    field_mappings = Column(JSON, nullable=True)  # Field mappings
    validation_rules = Column(JSON, nullable=True)  # Validation rules
    builder_config = Column(JSON, nullable=False)  # Builder configuration
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default='1.0')
    notes = Column(Text, nullable=True)
    
    # Relationships
    builder_templates = relationship("ReportTemplate", back_populates="builder")
    
    def __repr__(self):
        return f"<ReportBuilder(name='{self.builder_name}', type='{self.builder_type}')>"

class ReportDashboard(BaseModel):
    """Report dashboard management"""
    __tablename__ = "report_dashboard"
    
    dashboard_name = Column(String(200), nullable=False)
    dashboard_code = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    layout_config = Column(JSON, nullable=False)  # Dashboard layout
    widgets = Column(JSON, nullable=True)  # Dashboard widgets
    filters = Column(JSON, nullable=True)  # Dashboard filters
    refresh_interval = Column(Integer, default=300)  # in seconds
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    dashboard_views = relationship("ReportView", back_populates="dashboard")
    
    def __repr__(self):
        return f"<ReportDashboard(name='{self.dashboard_name}', code='{self.dashboard_code}')>"

class ReportWidget(BaseModel):
    """Report widget management"""
    __tablename__ = "report_widget"
    
    widget_name = Column(String(200), nullable=False)
    widget_code = Column(String(100), unique=True, nullable=False)
    widget_type = Column(String(50), nullable=False)  # chart, table, metric, gauge, map
    data_source = Column(String(100), nullable=False)
    query_sql = Column(Text, nullable=True)
    widget_config = Column(JSON, nullable=False)  # Widget configuration
    chart_config = Column(JSON, nullable=True)  # Chart configuration
    position = Column(JSON, nullable=True)  # Widget position
    size = Column(JSON, nullable=True)  # Widget size
    filters = Column(JSON, nullable=True)  # Widget filters
    refresh_interval = Column(Integer, default=300)  # in seconds
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    widget_instances = relationship("ReportInstance", back_populates="widget")
    
    def __repr__(self):
        return f"<ReportWidget(name='{self.widget_name}', type='{self.widget_type}')>"

class ReportExport(BaseModel):
    """Report export management"""
    __tablename__ = "report_export"
    
    instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=False)
    export_name = Column(String(200), nullable=False)
    export_format = Column(String(20), nullable=False)  # pdf, excel, csv, json, xml
    export_config = Column(JSON, nullable=True)  # Export configuration
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    export_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    report_instance = relationship("ReportInstance")
    
    def __repr__(self):
        return f"<ReportExport(name='{self.export_name}', format='{self.export_format}')>"

class ReportAnalytics(BaseModel):
    """Report analytics tracking"""
    __tablename__ = "report_analytics"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=True)
    instance_id = Column(Integer, ForeignKey('report_instance.id'), nullable=True)
    analytics_date = Column(Date, nullable=False)
    view_count = Column(Integer, default=0)
    export_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    average_execution_time = Column(Numeric(10, 3), nullable=True)
    success_rate = Column(Numeric(5, 2), nullable=True)
    error_count = Column(Integer, default=0)
    
    # Relationships
    template = relationship("ReportTemplate")
    instance = relationship("ReportInstance")
    
    def __repr__(self):
        return f"<ReportAnalytics(date='{self.analytics_date}', views={self.view_count})>"

class ReportPermission(BaseModel):
    """Report permission management"""
    __tablename__ = "report_permission"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    permission_type = Column(String(50), nullable=False)  # view, edit, delete, schedule
    is_granted = Column(Boolean, default=True)
    granted_date = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(Integer, ForeignKey('user.id'), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<ReportPermission(template_id={self.template_id}, type='{self.permission_type}')>"

class ReportCache(BaseModel):
    """Report cache management"""
    __tablename__ = "report_cache"
    
    cache_key = Column(String(200), unique=True, nullable=False)
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    parameters = Column(JSON, nullable=True)
    cache_data = Column(JSON, nullable=False)
    cache_size = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)
    hit_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate")
    
    def __repr__(self):
        return f"<ReportCache(key='{self.cache_key}', size={self.cache_size})>"