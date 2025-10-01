# Accounting API Endpoints
from .double_entry_accounting import router as double_entry_accounting_router
from .chart_of_accounts import router as chart_of_accounts_router
from .financial_year_management import router as financial_year_management_router
from .banking import router as banking_router

__all__ = [
    "double_entry_accounting_router",
    "chart_of_accounts_router",
    "financial_year_management_router",
    "banking_router"
]