from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, date, time

class StaffBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    mobile: Optional[str] = Field(None, regex="^[0-9]{10}$")
    role: str = Field(default="Sales")
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    joining_date: Optional[date] = None
    basic_salary: Optional[Decimal] = Field(None, ge=0)
    commission_enabled: bool = False

class StaffCreate(StaffBase):
    create_user_account: bool = False
    user_password: Optional[str] = None
    user_role: Optional[str] = "cashier"

class StaffUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    mobile: Optional[str] = None
    role: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    basic_salary: Optional[Decimal] = None
    commission_enabled: Optional[bool] = None
    active: Optional[bool] = None

class StaffResponse(BaseModel):
    id: str
    code: str
    name: str
    mobile: Optional[str]
    role: str
    email: Optional[str]
    joining_date: Optional[date]
    basic_salary: Optional[Decimal]
    commission_enabled: bool
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StaffDetailResponse(StaffResponse):
    current_month_sales: Decimal
    current_month_bills: int
    lifetime_sales: Decimal
    lifetime_bills: int
    current_target: Optional[Decimal]
    achievement_percentage: Decimal
    working_days_current_month: int
    recent_sales: List[Dict[str, Any]]

class StaffTargetCreate(BaseModel):
    staff_id: str
    period_start: date
    period_end: date
    target_amount: Decimal = Field(..., gt=0)
    incentive_type: str = Field(..., regex="^(percent|flat)$")
    incentive_slabs: List[Dict[str, Any]]  # [{"min": 0, "max": 50, "rate": 1}, ...]
    min_achievement_for_incentive: Optional[Decimal] = Field(default=80, ge=0, le=100)
    
    @validator('period_end')
    def validate_period(cls, v, values):
        if 'period_start' in values and v < values['period_start']:
            raise ValueError('period_end must be after period_start')
        return v

class StaffTargetUpdate(BaseModel):
    target_amount: Optional[Decimal] = None
    incentive_type: Optional[str] = None
    incentive_slabs: Optional[List[Dict[str, Any]]] = None
    min_achievement_for_incentive: Optional[Decimal] = None

class StaffTargetResponse(BaseModel):
    id: str
    staff_id: str
    period_start: date
    period_end: date
    target_amount: Decimal
    incentive_type: str
    incentive_slabs: List[Dict[str, Any]]
    min_achievement_for_incentive: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StaffPerformanceResponse(BaseModel):
    staff_code: str
    staff_name: str
    period: Dict[str, date]
    sales_summary: Dict[str, Any]
    daily_performance: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    customer_metrics: Dict[str, Any]
    returns: Dict[str, Any]

class StaffCommissionResponse(BaseModel):
    period: str
    staff_count: int
    total_commission: float
    details: List[Dict[str, Any]]

class StaffAttendanceCreate(BaseModel):
    staff_id: str
    date: date
    status: str = Field(..., regex="^(present|absent|half_day|leave|holiday)$")
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    notes: Optional[str] = None

class StaffAttendanceResponse(BaseModel):
    id: str
    staff_id: str
    date: date
    status: str
    check_in_time: Optional[time]
    check_out_time: Optional[time]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class StaffImportResponse(BaseModel):
    success: bool
    imported: int
    updated: int
    errors: List[str]