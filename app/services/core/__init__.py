# Core Services
from .company_service import CompanyService
from .settings_service import SettingsService
from .discount_management_service import DiscountManagementService
from .report_studio_service import ReportStudioService
from .gst_service import GSTService
from .gst_calculation_service import GSTCalculationService
from .gst_reports_service import GSTReportsService
from .gst_init_service import GSTInitService
from .backup_service import BackupService
from .excel_service import ExcelService
from .pdf_service import PDFService
from .performance_monitoring_service import PerformanceMonitoringService
from .system_integration_service import SystemIntegrationService
from .whatsapp_service import WhatsAppService

# Service instances
company_service = CompanyService()
settings_service = SettingsService()
discount_management_service = DiscountManagementService()
report_studio_service = ReportStudioService()
gst_service = GSTService()
gst_calculation_service = GSTCalculationService()
gst_reports_service = GSTReportsService()
gst_init_service = GSTInitService()
backup_service = BackupService()
excel_service = ExcelService()
pdf_service = PDFService()
performance_monitoring_service = PerformanceMonitoringService()
system_integration_service = SystemIntegrationService()
whatsapp_service = WhatsAppService()

__all__ = [
    "CompanyService",
    "SettingsService",
    "DiscountManagementService",
    "ReportStudioService", 
    "GSTService",
    "GSTCalculationService",
    "GSTReportsService",
    "GSTInitService",
    "BackupService",
    "ExcelService",
    "PDFService",
    "PerformanceMonitoringService",
    "SystemIntegrationService",
    "WhatsAppService",
    "company_service",
    "settings_service",
    "discount_management_service",
    "report_studio_service",
    "gst_service",
    "gst_calculation_service",
    "gst_reports_service",
    "gst_init_service",
    "backup_service",
    "excel_service",
    "pdf_service",
    "performance_monitoring_service",
    "system_integration_service",
    "whatsapp_service"
]