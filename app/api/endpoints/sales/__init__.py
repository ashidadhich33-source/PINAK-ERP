# Sales API Endpoints
from .enhanced_sales import router as enhanced_sales_router
from .sale_returns import router as sale_returns_router

__all__ = [
    "enhanced_sales_router",
    "sale_returns_router"
]