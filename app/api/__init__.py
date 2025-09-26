# backend/app/api/__init__.py
from .endpoints import auth, setup, items, sales, purchases, reports, customers, suppliers, backup, expenses, staff, settings, payments

__all__ = [
    "auth",
    "setup",
    "items",
    "sales",
    "purchases",
    "reports",
    "customers",
    "suppliers",
    "backup",
    "expenses",
    "staff",
    "settings",
    "payments"
]