# backend/app/api/endpoints/accounting/analytic.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ....database import get_db
from ...core.security import get_current_user, require_permission
from ....models.core import User, Company
from ....models.accounting.analytic import (
    AnalyticAccount, AnalyticLine, AnalyticPlan, AnalyticPlanAccount,
    AnalyticDistribution, AnalyticBudget, AnalyticBudgetLine,
    AnalyticReport, AnalyticTag, AnalyticTagLine, AnalyticAccountType,
    DistributionMethod
)

router = APIRouter()

# --- Schemas ---
class AnalyticAccountCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    account_type: AnalyticAccountType
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    budget_amount: Optional[Decimal] = None
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AnalyticAccountResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    account_type: AnalyticAccountType
    parent_id: Optional[int]
    level: int
    is_active: bool
    is_leaf: bool
    manager_id: Optional[int]
    budget_amount: Optional[Decimal]
    actual_amount: Decimal
    variance_amount: Decimal
    color: Optional[str]
    icon: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AnalyticLineCreate(BaseModel):
    analytic_account_id: int
    move_line_id: Optional[int] = None
    invoice_id: Optional[int] = None
    bill_id: Optional[int] = None
    payment_id: Optional[int] = None
    amount: Decimal
    currency_amount: Optional[Decimal] = None
    currency_id: Optional[int] = None
    date: date
    description: Optional[str] = None
    reference: Optional[str] = None
    partner_id: Optional[int] = None
    product_id: Optional[int] = None
    unit_amount: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    is_debit: bool = True

class AnalyticLineResponse(BaseModel):
    id: int
    analytic_account_id: int
    move_line_id: Optional[int]
    invoice_id: Optional[int]
    bill_id: Optional[int]
    payment_id: Optional[int]
    amount: Decimal
    currency_amount: Optional[Decimal]
    currency_id: Optional[int]
    date: date
    description: Optional[str]
    reference: Optional[str]
    partner_id: Optional[int]
    product_id: Optional[int]
    unit_amount: Optional[Decimal]
    unit_of_measure: Optional[str]
    is_debit: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AnalyticPlanCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    is_default: bool = False

class AnalyticPlanResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    is_active: bool
    is_default: bool
    company_id: int
    created_by: int
    created_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AnalyticDistributionCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    account_id: int
    analytic_account_id: int
    distribution_method: DistributionMethod
    percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    amount: Optional[Decimal] = Field(None, ge=0)
    formula: Optional[str] = None
    is_default: bool = False
    conditions: Optional[Dict[str, Any]] = None

class AnalyticDistributionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    account_id: int
    analytic_account_id: int
    distribution_method: DistributionMethod
    percentage: Optional[Decimal]
    amount: Optional[Decimal]
    formula: Optional[str]
    is_active: bool
    is_default: bool
    conditions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AnalyticBudgetCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    analytic_account_id: int
    account_id: int
    budget_period: str = Field(..., regex="^(monthly|quarterly|yearly)$")
    start_date: date
    end_date: date
    budget_amount: Decimal = Field(..., gt=0)

class AnalyticBudgetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    analytic_account_id: int
    account_id: int
    budget_period: str
    start_date: date
    end_date: date
    budget_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percentage: Decimal
    is_active: bool
    created_by: int
    created_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class AnalyticReportCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    report_type: str = Field(..., regex="^(cost_center|project|department|product|customer|supplier|location|activity)$")
    analytic_account_ids: Optional[List[int]] = None
    account_ids: Optional[List[int]] = None
    date_from: date
    date_to: date
    group_by: Optional[str] = Field(None, regex="^(account|partner|product|period)$")
    sort_by: Optional[str] = Field(None, regex="^(amount|name|date)$")
    sort_order: str = Field(default="asc", regex="^(asc|desc)$")

class AnalyticReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    report_type: str
    analytic_account_ids: Optional[List[int]]
    account_ids: Optional[List[int]]
    date_from: date
    date_to: date
    group_by: Optional[str]
    sort_by: Optional[str]
    sort_order: str
    is_active: bool
    created_by: int
    created_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Analytic Accounts
@router.post("/analytic-accounts", response_model=AnalyticAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_account(
    account_data: AnalyticAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic account"""
    account = AnalyticAccount(**account_data.dict())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.get("/analytic-accounts", response_model=List[AnalyticAccountResponse])
async def get_analytic_accounts(
    account_type: Optional[AnalyticAccountType] = Query(None),
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_leaf: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic accounts"""
    query = db.query(AnalyticAccount)
    
    if account_type:
        query = query.filter(AnalyticAccount.account_type == account_type)
    if parent_id is not None:
        query = query.filter(AnalyticAccount.parent_id == parent_id)
    if is_active is not None:
        query = query.filter(AnalyticAccount.is_active == is_active)
    if is_leaf is not None:
        query = query.filter(AnalyticAccount.is_leaf == is_leaf)
    
    return query.order_by(AnalyticAccount.name).all()

@router.get("/analytic-accounts/{account_id}", response_model=AnalyticAccountResponse)
async def get_analytic_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get specific analytic account"""
    account = db.query(AnalyticAccount).filter(AnalyticAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytic account not found")
    return account

# Analytic Lines
@router.post("/analytic-lines", response_model=AnalyticLineResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_line(
    line_data: AnalyticLineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic line"""
    line = AnalyticLine(
        **line_data.dict(),
        created_by=current_user.id
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return line

@router.get("/analytic-lines", response_model=List[AnalyticLineResponse])
async def get_analytic_lines(
    analytic_account_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    is_debit: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic lines"""
    query = db.query(AnalyticLine)
    
    if analytic_account_id:
        query = query.filter(AnalyticLine.analytic_account_id == analytic_account_id)
    if date_from:
        query = query.filter(AnalyticLine.date >= date_from)
    if date_to:
        query = query.filter(AnalyticLine.date <= date_to)
    if is_debit is not None:
        query = query.filter(AnalyticLine.is_debit == is_debit)
    
    return query.order_by(AnalyticLine.date.desc()).all()

# Analytic Plans
@router.post("/analytic-plans", response_model=AnalyticPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_plan(
    plan_data: AnalyticPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic plan"""
    plan = AnalyticPlan(
        **plan_data.dict(),
        company_id=current_user.company_id,
        created_by=current_user.id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.get("/analytic-plans", response_model=List[AnalyticPlanResponse])
async def get_analytic_plans(
    is_active: Optional[bool] = Query(None),
    is_default: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic plans"""
    query = db.query(AnalyticPlan)
    
    if is_active is not None:
        query = query.filter(AnalyticPlan.is_active == is_active)
    if is_default is not None:
        query = query.filter(AnalyticPlan.is_default == is_default)
    
    return query.all()

# Analytic Distributions
@router.post("/analytic-distributions", response_model=AnalyticDistributionResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_distribution(
    distribution_data: AnalyticDistributionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic distribution"""
    distribution = AnalyticDistribution(**distribution_data.dict())
    db.add(distribution)
    db.commit()
    db.refresh(distribution)
    return distribution

@router.get("/analytic-distributions", response_model=List[AnalyticDistributionResponse])
async def get_analytic_distributions(
    account_id: Optional[int] = Query(None),
    analytic_account_id: Optional[int] = Query(None),
    distribution_method: Optional[DistributionMethod] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic distributions"""
    query = db.query(AnalyticDistribution)
    
    if account_id:
        query = query.filter(AnalyticDistribution.account_id == account_id)
    if analytic_account_id:
        query = query.filter(AnalyticDistribution.analytic_account_id == analytic_account_id)
    if distribution_method:
        query = query.filter(AnalyticDistribution.distribution_method == distribution_method)
    if is_active is not None:
        query = query.filter(AnalyticDistribution.is_active == is_active)
    
    return query.all()

# Analytic Budgets
@router.post("/analytic-budgets", response_model=AnalyticBudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_budget(
    budget_data: AnalyticBudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic budget"""
    budget = AnalyticBudget(
        **budget_data.dict(),
        created_by=current_user.id
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

@router.get("/analytic-budgets", response_model=List[AnalyticBudgetResponse])
async def get_analytic_budgets(
    analytic_account_id: Optional[int] = Query(None),
    account_id: Optional[int] = Query(None),
    budget_period: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic budgets"""
    query = db.query(AnalyticBudget)
    
    if analytic_account_id:
        query = query.filter(AnalyticBudget.analytic_account_id == analytic_account_id)
    if account_id:
        query = query.filter(AnalyticBudget.account_id == account_id)
    if budget_period:
        query = query.filter(AnalyticBudget.budget_period == budget_period)
    if is_active is not None:
        query = query.filter(AnalyticBudget.is_active == is_active)
    
    return query.all()

# Analytic Reports
@router.post("/analytic-reports", response_model=AnalyticReportResponse, status_code=status.HTTP_201_CREATED)
async def create_analytic_report(
    report_data: AnalyticReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_analytic"))
):
    """Create new analytic report"""
    report = AnalyticReport(
        **report_data.dict(),
        created_by=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/analytic-reports", response_model=List[AnalyticReportResponse])
async def get_analytic_reports(
    report_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    created_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get all analytic reports"""
    query = db.query(AnalyticReport)
    
    if report_type:
        query = query.filter(AnalyticReport.report_type == report_type)
    if is_active is not None:
        query = query.filter(AnalyticReport.is_active == is_active)
    if created_by:
        query = query.filter(AnalyticReport.created_by == created_by)
    
    return query.all()

# Analytic Statistics
@router.get("/analytic-statistics")
async def get_analytic_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    analytic_account_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get analytic statistics"""
    # This would contain the actual statistics logic
    # For now, just returning placeholder data
    return {
        "total_accounts": 15,
        "active_accounts": 12,
        "total_lines": 1250,
        "total_budget": 500000.00,
        "total_actual": 450000.00,
        "variance_amount": 50000.00,
        "variance_percentage": 10.0
    }

# Analytic Dashboard
@router.get("/analytic-dashboard")
async def get_analytic_dashboard(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytic"))
):
    """Get analytic dashboard data"""
    # This would contain the actual dashboard logic
    # For now, just returning placeholder data
    return {
        "message": "Analytic dashboard data",
        "status": "success",
        "data": {
            "cost_centers": 5,
            "projects": 8,
            "departments": 3,
            "total_budget": 500000.00,
            "total_actual": 450000.00
        }
    }