from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date

class ReportPeriod(BaseModel):
    from_date: date
    to_date: date

class SaleReportResponse(BaseModel):
    period: ReportPeriod
    total_records: int
    total_sales: Decimal
    total_returns: Decimal
    net_sales: Decimal
    data: List[Dict[str, Any]]

class PurchaseReportResponse(BaseModel):
    period: ReportPeriod
    total_purchases: Decimal
    total_returns: Decimal
    net_purchases: Decimal

class StockReportResponse(BaseModel):
    total_items: int
    total_quantity: int
    total_stock_value: Decimal
    total_retail_value: Decimal
    items: List[Dict[str, Any]]

class CustomerReportResponse(BaseModel):
    period: ReportPeriod
    top_customers: List[Dict[str, Any]]
    inactive_customers: int
    new_customers: int
    loyalty_distribution: List[Dict[str, Any]]

class StaffPerformanceReportResponse(BaseModel):
    period: ReportPeriod
    staff_count: int
    total_sales: Decimal
    performance: List[Dict[str, Any]]

class GST_ReportResponse(BaseModel):
    period: ReportPeriod
    output_tax: Dict[str, float]
    input_tax: Dict[str, float]
    net_payable: Dict[str, float]
    hsn_summary: List[Dict[str, Any]]

class ProfitLossReportResponse(BaseModel):
    period: ReportPeriod
    revenue: Dict[str, float]
    costs: Dict[str, float]
    expenses: List[Dict[str, float]]
    total_expenses: float
    net_profit: float
    net_margin: float

class DashboardMetricsResponse(BaseModel):
    today: Dict[str, Any]
    month: Dict[str, Any]
    inventory: Dict[str, Any]
    customers: Dict[str, Any]
    pending: Dict[str, Any]
    top_selling_today: List[Dict[str, Any]]