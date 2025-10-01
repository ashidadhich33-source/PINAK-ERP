# Core API Endpoints
from .auth import router as auth_router
from .setup import router as setup_router
from .companies import router as companies_router
from .settings import router as settings_router
from .gst import router as gst_router
from .backup import router as backup_router
from .expenses import router as expenses_router
from .payments import router as payments_router
from .reports import router as reports_router
from .database_setup import router as database_setup_router

__all__ = [
    "auth_router",
    "setup_router",
    "companies_router",
    "settings_router",
    "gst_router",
    "backup_router",
    "expenses_router",
    "payments_router",
    "reports_router",
    "database_setup_router"
]