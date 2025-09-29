# Customer API Endpoints
from .customers import router as customers_router
from .suppliers import router as suppliers_router

__all__ = [
    "customers_router",
    "suppliers_router"
]