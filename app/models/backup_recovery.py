# backend/app/models/backup_recovery.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from .base import BaseModel

class BackupType(PyEnum):
    """Backup Type"""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    MANUAL = "manual"
    SCHEDULED = "scheduled"

class BackupStatus(PyEnum):
    """Backup Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RecoveryStatus(PyEnum):
    """Recovery Status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BackupJob(BaseModel):
    """Backup Job Management"""
    __tablename__ = "backup_job"
    
    # Job Information
    job_name = Column(String(200), nullable=False)
    job_description = Column(Text, nullable=True)
    backup_type = Column(Enum(BackupType), nullable=False)
    
    # Backup Configuration
    backup_config = Column(JSON, nullable=False)
    include_tables = Column(JSON, nullable=True)  # Specific tables to backup
    exclude_tables = Column(JSON, nullable=True)  # Tables to exclude
    compression_enabled = Column(Boolean, default=True)
    encryption_enabled = Column(Boolean, default=False)
    
    # Storage Configuration
    storage_location = Column(String(500), nullable=False)
    storage_type = Column(String(50), nullable=False)  # local, s3, gcs, azure
    storage_config = Column(JSON, nullable=True)
    
    # Schedule Configuration
    is_scheduled = Column(Boolean, default=False)
    schedule_config = Column(JSON, nullable=True)
    cron_expression = Column(String(100), nullable=True)
    
    # Job Status
    status = Column(Enum(BackupStatus), default=BackupStatus.PENDING)
    is_active = Column(Boolean, default=True)
    
    # Execution Information
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    backup_records = relationship("BackupRecord", back_populates="backup_job")
    
    def __repr__(self):
        return f"<BackupJob(name='{self.job_name}', type='{self.backup_type}')>"

class BackupRecord(BaseModel):
    """Backup Record - Individual Backup Instances"""
    __tablename__ = "backup_record"
    
    # Backup Information
    backup_job_id = Column(Integer, ForeignKey('backup_job.id'), nullable=False)
    backup_name = Column(String(200), nullable=False)
    backup_description = Column(Text, nullable=True)
    
    # Backup Details
    backup_type = Column(Enum(BackupType), nullable=False)
    backup_size = Column(Integer, nullable=True)  # bytes
    backup_path = Column(String(500), nullable=False)
    backup_filename = Column(String(200), nullable=False)
    
    # Backup Status
    status = Column(Enum(BackupStatus), default=BackupStatus.PENDING)
    progress_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Execution Information
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # Backup Configuration
    compression_ratio = Column(Numeric(5, 2), nullable=True)
    encryption_key = Column(String(200), nullable=True)
    checksum = Column(String(200), nullable=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Metadata
    backup_metadata = Column(JSON, nullable=True)
    table_counts = Column(JSON, nullable=True)  # Record counts per table
    
    # Relationships
    backup_job = relationship("BackupJob", back_populates="backup_records")
    recovery_records = relationship("RecoveryRecord", back_populates="backup_record")
    
    def __repr__(self):
        return f"<BackupRecord(name='{self.backup_name}', status='{self.status}')>"

class RecoveryJob(BaseModel):
    """Recovery Job Management"""
    __tablename__ = "recovery_job"
    
    # Job Information
    job_name = Column(String(200), nullable=False)
    job_description = Column(Text, nullable=True)
    
    # Recovery Configuration
    recovery_config = Column(JSON, nullable=False)
    target_database = Column(String(100), nullable=False)
    recovery_mode = Column(String(50), nullable=False)  # full, partial, table_level
    
    # Recovery Status
    status = Column(Enum(RecoveryStatus), default=RecoveryStatus.PENDING)
    is_active = Column(Boolean, default=True)
    
    # Execution Information
    last_run_at = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    recovery_records = relationship("RecoveryRecord", back_populates="recovery_job")
    
    def __repr__(self):
        return f"<RecoveryJob(name='{self.job_name}', status='{self.status}')>"

class RecoveryRecord(BaseModel):
    """Recovery Record - Individual Recovery Instances"""
    __tablename__ = "recovery_record"
    
    # Recovery Information
    recovery_job_id = Column(Integer, ForeignKey('recovery_job.id'), nullable=False)
    backup_record_id = Column(Integer, ForeignKey('backup_record.id'), nullable=False)
    recovery_name = Column(String(200), nullable=False)
    recovery_description = Column(Text, nullable=True)
    
    # Recovery Details
    recovery_mode = Column(String(50), nullable=False)
    target_tables = Column(JSON, nullable=True)  # Specific tables to recover
    recovery_path = Column(String(500), nullable=True)
    
    # Recovery Status
    status = Column(Enum(RecoveryStatus), default=RecoveryStatus.PENDING)
    progress_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Execution Information
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # seconds
    
    # Recovery Results
    tables_recovered = Column(JSON, nullable=True)
    records_recovered = Column(Integer, nullable=True)
    recovery_metadata = Column(JSON, nullable=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Relationships
    recovery_job = relationship("RecoveryJob", back_populates="recovery_records")
    backup_record = relationship("BackupRecord", back_populates="recovery_records")
    
    def __repr__(self):
        return f"<RecoveryRecord(name='{self.recovery_name}', status='{self.status}')>"

class DisasterRecoveryPlan(BaseModel):
    """Disaster Recovery Plan"""
    __tablename__ = "disaster_recovery_plan"
    
    # Plan Information
    plan_name = Column(String(200), nullable=False)
    plan_description = Column(Text, nullable=True)
    plan_type = Column(String(50), nullable=False)  # rto, rpo, business_continuity
    
    # Plan Configuration
    plan_config = Column(JSON, nullable=False)
    recovery_time_objective = Column(Integer, nullable=True)  # minutes
    recovery_point_objective = Column(Integer, nullable=True)  # minutes
    
    # Backup Strategy
    backup_strategy = Column(JSON, nullable=True)
    backup_frequency = Column(String(50), nullable=True)  # hourly, daily, weekly
    retention_policy = Column(JSON, nullable=True)
    
    # Recovery Strategy
    recovery_strategy = Column(JSON, nullable=True)
    recovery_procedures = Column(JSON, nullable=True)
    escalation_procedures = Column(JSON, nullable=True)
    
    # Plan Status
    is_active = Column(Boolean, default=True)
    last_tested_at = Column(DateTime, nullable=True)
    next_test_at = Column(DateTime, nullable=True)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    plan_tests = relationship("DisasterRecoveryTest", back_populates="disaster_recovery_plan")
    
    def __repr__(self):
        return f"<DisasterRecoveryPlan(name='{self.plan_name}', type='{self.plan_type}')>"

class DisasterRecoveryTest(BaseModel):
    """Disaster Recovery Test"""
    __tablename__ = "disaster_recovery_test"
    
    # Test Information
    disaster_recovery_plan_id = Column(Integer, ForeignKey('disaster_recovery_plan.id'), nullable=False)
    test_name = Column(String(200), nullable=False)
    test_description = Column(Text, nullable=True)
    test_type = Column(String(50), nullable=False)  # tabletop, simulation, full_test
    
    # Test Configuration
    test_config = Column(JSON, nullable=False)
    test_scenarios = Column(JSON, nullable=True)
    test_environment = Column(String(100), nullable=True)
    
    # Test Status
    test_status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    test_started_at = Column(DateTime, nullable=True)
    test_completed_at = Column(DateTime, nullable=True)
    test_duration = Column(Integer, nullable=True)  # seconds
    
    # Test Results
    test_results = Column(JSON, nullable=True)
    test_metrics = Column(JSON, nullable=True)
    test_findings = Column(JSON, nullable=True)
    test_recommendations = Column(JSON, nullable=True)
    
    # Test Participants
    test_participants = Column(JSON, nullable=True)
    test_observers = Column(JSON, nullable=True)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    disaster_recovery_plan = relationship("DisasterRecoveryPlan", back_populates="plan_tests")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<DisasterRecoveryTest(name='{self.test_name}', status='{self.test_status}')>"

class BackupStorage(BaseModel):
    """Backup Storage Configuration"""
    __tablename__ = "backup_storage"
    
    # Storage Information
    storage_name = Column(String(200), nullable=False)
    storage_type = Column(String(50), nullable=False)  # local, s3, gcs, azure, ftp
    storage_description = Column(Text, nullable=True)
    
    # Storage Configuration
    storage_config = Column(JSON, nullable=False)
    connection_string = Column(String(500), nullable=True)
    credentials = Column(JSON, nullable=True)
    
    # Storage Settings
    max_storage_size = Column(Integer, nullable=True)  # bytes
    compression_enabled = Column(Boolean, default=True)
    encryption_enabled = Column(Boolean, default=False)
    
    # Storage Status
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Storage Metrics
    used_storage = Column(Integer, default=0)  # bytes
    available_storage = Column(Integer, nullable=True)  # bytes
    backup_count = Column(Integer, default=0)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<BackupStorage(name='{self.storage_name}', type='{self.storage_type}')>"

class BackupMonitoring(BaseModel):
    """Backup Monitoring and Alerts"""
    __tablename__ = "backup_monitoring"
    
    # Monitoring Information
    monitoring_name = Column(String(200), nullable=False)
    monitoring_type = Column(String(50), nullable=False)  # backup_failure, storage_full, recovery_failure
    
    # Monitoring Configuration
    monitoring_config = Column(JSON, nullable=False)
    alert_conditions = Column(JSON, nullable=True)
    alert_thresholds = Column(JSON, nullable=True)
    
    # Alert Configuration
    email_alerts = Column(Boolean, default=True)
    email_recipients = Column(JSON, nullable=True)
    whatsapp_alerts = Column(Boolean, default=False)
    whatsapp_recipients = Column(JSON, nullable=True)
    sms_alerts = Column(Boolean, default=False)
    sms_recipients = Column(JSON, nullable=True)
    
    # Monitoring Status
    is_active = Column(Boolean, default=True)
    last_alert_at = Column(DateTime, nullable=True)
    alert_count = Column(Integer, default=0)
    
    # Created Information
    created_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by])
    monitoring_logs = relationship("BackupMonitoringLog", back_populates="monitoring")
    
    def __repr__(self):
        return f"<BackupMonitoring(name='{self.monitoring_name}', type='{self.monitoring_type}')>"

class BackupMonitoringLog(BaseModel):
    """Backup Monitoring Logs"""
    __tablename__ = "backup_monitoring_log"
    
    # Monitoring Information
    monitoring_id = Column(Integer, ForeignKey('backup_monitoring.id'), nullable=False)
    
    # Log Information
    log_type = Column(String(50), nullable=False)  # info, warning, error, critical
    log_message = Column(Text, nullable=False)
    log_details = Column(JSON, nullable=True)
    
    # Alert Information
    alert_sent = Column(Boolean, default=False)
    alert_channels = Column(JSON, nullable=True)
    alert_recipients = Column(JSON, nullable=True)
    
    # Log Timestamps
    logged_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    monitoring = relationship("BackupMonitoring", back_populates="monitoring_logs")
    
    def __repr__(self):
        return f"<BackupMonitoringLog(type='{self.log_type}', message='{self.log_message[:50]}...')>"