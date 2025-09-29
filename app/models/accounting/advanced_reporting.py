# backend/app/models/accounting/advanced_reporting.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Date, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from ..base import BaseModel

class ReportType(PyEnum):
    """Report type enumeration"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTIC = "analytic"
    CUSTOM = "custom"
    DASHBOARD = "dashboard"

class WidgetType(PyEnum):
    """Dashboard widget types"""
    CHART = "chart"
    TABLE = "table"
    KPI = "kpi"
    METRIC = "metric"
    GRAPH = "graph"
    GAUGE = "gauge"
    PIE = "pie"
    BAR = "bar"
    LINE = "line"

class ExportFormat(PyEnum):
    """Export format types"""
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    HTML = "html"

class ReportTemplate(BaseModel):
    """Report templates for custom reports"""
    __tablename__ = "report_template"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(Enum(ReportType), nullable=False)
    category = Column(String(100), nullable=True)  # Financial, Operational, etc.
    template_data = Column(JSON, nullable=False)  # Report structure and configuration
    sql_query = Column(Text, nullable=True)  # Custom SQL query
    parameters = Column(JSON, nullable=True)  # Report parameters
    filters = Column(JSON, nullable=True)  # Available filters
    columns = Column(JSON, nullable=True)  # Column definitions
    formatting = Column(JSON, nullable=True)  # Formatting rules
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    version = Column(String(20), default='1.0')
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    report_instances = relationship("ReportInstance", back_populates="template")
    
    def __repr__(self):
        return f"<ReportTemplate(name='{self.name}', type='{self.report_type}')>"

class ReportInstance(BaseModel):
    """Report instances (generated reports)"""
    __tablename__ = "report_instance"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=True)  # Parameters used for generation
    filters_applied = Column(JSON, nullable=True)  # Filters applied
    generated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    generated_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(20), default='generating')  # generating, completed, failed
    file_path = Column(String(500), nullable=True)  # Path to generated file
    file_size = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)  # Number of records in report
    execution_time = Column(Numeric(10, 3), nullable=True)  # Execution time in seconds
    error_message = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate", back_populates="report_instances")
    generated_by_user = relationship("User", foreign_keys=[generated_by])
    
    def __repr__(self):
        return f"<ReportInstance(name='{self.name}', status='{self.status}')>"

class DashboardWidget(BaseModel):
    """Dashboard widgets for KPIs"""
    __tablename__ = "dashboard_widget"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    widget_type = Column(Enum(WidgetType), nullable=False)
    data_source = Column(String(100), nullable=False)  # Table or query name
    query = Column(Text, nullable=True)  # Custom SQL query
    parameters = Column(JSON, nullable=True)  # Widget parameters
    configuration = Column(JSON, nullable=False)  # Widget configuration
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)
    refresh_interval = Column(Integer, default=300)  # Refresh interval in seconds
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    widget_data = relationship("WidgetData", back_populates="widget")
    
    def __repr__(self):
        return f"<DashboardWidget(name='{self.name}', type='{self.widget_type}')>"

class WidgetData(BaseModel):
    """Widget data cache"""
    __tablename__ = "widget_data"
    
    widget_id = Column(Integer, ForeignKey('dashboard_widget.id'), nullable=False)
    data = Column(JSON, nullable=False)  # Cached widget data
    generated_date = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    record_count = Column(Integer, nullable=True)
    
    # Relationships
    widget = relationship("DashboardWidget", back_populates="widget_data")
    
    def __repr__(self):
        return f"<WidgetData(widget_id={self.widget_id}, records={self.record_count})>"

class ScheduledReport(BaseModel):
    """Scheduled reports for automation"""
    __tablename__ = "scheduled_report"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    schedule_cron = Column(String(100), nullable=False)  # Cron expression
    parameters = Column(JSON, nullable=True)  # Default parameters
    email_recipients = Column(JSON, nullable=True)  # Email recipients
    email_subject = Column(String(200), nullable=True)
    email_body = Column(Text, nullable=True)
    export_format = Column(Enum(ExportFormat), default=ExportFormat.PDF)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Relationships
    template = relationship("ReportTemplate")
    created_by_user = relationship("User", foreign_keys=[created_by])
    report_runs = relationship("ReportRun", back_populates="scheduled_report")
    
    def __repr__(self):
        return f"<ScheduledReport(name='{self.name}', cron='{self.schedule_cron}')>"

class ReportRun(BaseModel):
    """Report run history"""
    __tablename__ = "report_run"
    
    scheduled_report_id = Column(Integer, ForeignKey('scheduled_report.id'), nullable=False)
    run_date = Column(DateTime, default=datetime.now, nullable=False)
    status = Column(String(20), default='running')  # running, completed, failed
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    record_count = Column(Integer, nullable=True)
    execution_time = Column(Numeric(10, 3), nullable=True)
    error_message = Column(Text, nullable=True)
    email_sent = Column(Boolean, default=False)
    email_recipients = Column(JSON, nullable=True)
    
    # Relationships
    scheduled_report = relationship("ScheduledReport", back_populates="report_runs")
    
    def __repr__(self):
        return f"<ReportRun(scheduled_id={self.scheduled_report_id}, status='{self.status}')>"

class ReportCategory(BaseModel):
    """Report categories for organization"""
    __tablename__ = "report_category"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('report_category.id'), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    parent = relationship("ReportCategory", remote_side=[BaseModel.id])
    children = relationship("ReportCategory", back_populates="parent")
    
    def __repr__(self):
        return f"<ReportCategory(name='{self.name}')>"

class ReportParameter(BaseModel):
    """Report parameters definition"""
    __tablename__ = "report_parameter"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    parameter_name = Column(String(100), nullable=False)
    parameter_type = Column(String(50), nullable=False)  # string, number, date, boolean, list
    default_value = Column(String(500), nullable=True)
    is_required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # For list parameters
    validation_rules = Column(JSON, nullable=True)  # Validation rules
    display_order = Column(Integer, default=0)
    
    # Relationships
    template = relationship("ReportTemplate")
    
    def __repr__(self):
        return f"<ReportParameter(name='{self.parameter_name}', type='{self.parameter_type}')>"

class ReportFilter(BaseModel):
    """Report filters definition"""
    __tablename__ = "report_filter"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    filter_name = Column(String(100), nullable=False)
    filter_type = Column(String(50), nullable=False)  # date_range, text, number, list
    field_name = Column(String(100), nullable=False)  # Database field name
    operator = Column(String(50), nullable=False)  # equals, contains, between, etc.
    default_value = Column(String(500), nullable=True)
    is_required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # For list filters
    display_order = Column(Integer, default=0)
    
    # Relationships
    template = relationship("ReportTemplate")
    
    def __repr__(self):
        return f"<ReportFilter(name='{self.filter_name}', type='{self.filter_type}')>"

class ReportColumn(BaseModel):
    """Report columns definition"""
    __tablename__ = "report_column"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    column_name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)  # string, number, date, currency
    field_name = Column(String(100), nullable=False)  # Database field name
    is_visible = Column(Boolean, default=True)
    is_sortable = Column(Boolean, default=True)
    is_groupable = Column(Boolean, default=False)
    width = Column(Integer, nullable=True)
    alignment = Column(String(20), default='left')  # left, center, right
    format_string = Column(String(100), nullable=True)  # Format string for numbers/dates
    display_order = Column(Integer, default=0)
    
    # Relationships
    template = relationship("ReportTemplate")
    
    def __repr__(self):
        return f"<ReportColumn(name='{self.column_name}', type='{self.data_type}')>"

class ReportAccess(BaseModel):
    """Report access control"""
    __tablename__ = "report_access"
    
    template_id = Column(Integer, ForeignKey('report_template.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    access_type = Column(String(20), nullable=False)  # view, edit, delete, admin
    granted_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    granted_date = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    template = relationship("ReportTemplate")
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    granted_by_user = relationship("User", foreign_keys=[granted_by])
    
    def __repr__(self):
        return f"<ReportAccess(template_id={self.template_id}, type='{self.access_type}')>"