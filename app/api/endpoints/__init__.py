# backend/app/api/endpoints/__init__.py
from .auth import router as auth_router
from .setup import router as setup_router
from .items import router as items_router
from .customers import router as customers_router
from .suppliers import router as suppliers_router
from .staff import router as staff_router
# Removed basic sales router - using enhanced_sales instead
from .purchases import router as purchases_router
from .payments import router as payments_router
from .expenses import router as expenses_router
from .reports import router as reports_router
from .backup import router as backup_router
from .settings import router as settings_router
from .sale_returns import router as sale_returns_router
from .suppliers import router as suppliers_router
from .whatsapp import router as whatsapp_router

__all__ = [
    "auth_router",
    "setup_router",
    "items_router",
    "customers_router",
    "suppliers_router",
    "staff_router",
    # "sales_router", # Removed - using enhanced_sales instead
    "purchases_router",
    "payments_router",
    "expenses_router",
    "reports_router",
    "backup_router",
    "settings_router",
    "sale_returns_router",
    "whatsapp_router"
]