from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract, case
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
import pandas as pd
import io
import uuid
import calendar

from ...database import get_db
from .staff import Staff, StaffTarget
from .user import User
from ..sales.enhanced_sales import Sale, SaleItem
from ..customers.customer import Customer
from ..sales.sales_return_integration import SaleReturn
from ...services.excel_service import ExcelService
from ...core.security import get_current_user
from ...core.rbac import require_role
from ...schemas.staff_schema import (
    StaffCreate, StaffUpdate, StaffResponse, StaffDetailResponse,
    StaffTargetCreate, StaffTargetUpdate, StaffTargetResponse,
    StaffPerformanceResponse, StaffCommissionResponse,
    StaffAttendanceCreate, StaffAttendanceResponse,
    StaffImportResponse
)

router = APIRouter()

@router.post("/", response_model=StaffResponse)
async def create_staff(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new staff member"""
    # Check if staff code already exists
    existing = db.query(Staff).filter(Staff.code == staff_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Staff code already exists")
    
    # Check if mobile already exists
    if staff_data.mobile:
        existing_mobile = db.query(Staff).filter(Staff.mobile == staff_data.mobile).first()
        if existing_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already registered")
    
    staff = Staff(
        id=str(uuid.uuid4()),
        code=staff_data.code,
        name=staff_data.name,
        mobile=staff_data.mobile,
        role=staff_data.role,
        email=staff_data.email,
        address=staff_data.address,
        joining_date=staff_data.joining_date or date.today(),
        basic_salary=staff_data.basic_salary,
        commission_enabled=staff_data.commission_enabled,
        active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(staff)
    
    # Create user account if requested
    if staff_data.create_user_account:
        from ...core.security import get_password_hash
        
        user = User(
            id=str(uuid.uuid4()),
            username=staff_data.code.lower(),
            display_name=staff_data.name,
            mobile=staff_data.mobile,
            email=staff_data.email,
            password_hash=get_password_hash(staff_data.user_password or "123456"),
            role=staff_data.user_role or "cashier",
            active=True
        )
        db.add(user)
        staff.user_id = user.id
    
    db.commit()
    db.refresh(staff)
    
    return staff

@router.get("/", response_model=List[StaffResponse])
async def get_staff_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[str] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all staff members with filters"""
    query = db.query(Staff)
    
    if search:
        query = query.filter(
            or_(
                Staff.code.ilike(f"%{search}%"),
                Staff.name.ilike(f"%{search}%"),
                Staff.mobile.contains(search)
            )
        )
    
    if role:
        query = query.filter(Staff.role == role)
    
    if active is not None:
        query = query.filter(Staff.active == active)
    
    staff_list = query.offset(skip).limit(limit).all()
    return staff_list

@router.get("/{staff_id}", response_model=StaffDetailResponse)
async def get_staff_details(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed staff information with performance metrics"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Get current month sales
    current_month_start = date.today().replace(day=1)
    current_month_sales = db.query(
        func.count(Sale.id).label('bill_count'),
        func.sum(Sale.final_payable).label('total_sales')
    ).filter(
        Sale.staff_id == staff_id,
        Sale.bill_date >= current_month_start
    ).first()
    
    # Get lifetime sales
    lifetime_sales = db.query(
        func.count(Sale.id).label('bill_count'),
        func.sum(Sale.final_payable).label('total_sales')
    ).filter(Sale.staff_id == staff_id).first()
    
    # Get current target
    current_target = db.query(StaffTarget).filter(
        StaffTarget.staff_id == staff_id,
        StaffTarget.period_start <= date.today(),
        StaffTarget.period_end >= date.today()
    ).first()
    
    # Calculate achievement percentage
    achievement_percentage = Decimal('0')
    if current_target and current_target.target_amount > 0:
        current_sales = current_month_sales.total_sales or Decimal('0')
        achievement_percentage = (current_sales / current_target.target_amount * 100).quantize(Decimal('0.01'))
    
    # Get recent sales
    recent_sales = db.query(Sale).filter(
        Sale.staff_id == staff_id
    ).order_by(Sale.bill_date.desc()).limit(10).all()
    
    recent_sales_list = []
    for sale in recent_sales:
        recent_sales_list.append({
            "bill_no": sale.bill_no,
            "bill_date": sale.bill_date,
            "customer_mobile": sale.customer_mobile,
            "amount": float(sale.final_payable)
        })
    
    # Get attendance for current month (if tracking)
    working_days = get_working_days_count(current_month_start, date.today())
    
    return StaffDetailResponse(
        id=staff.id,
        code=staff.code,
        name=staff.name,
        mobile=staff.mobile,
        role=staff.role,
        email=staff.email,
        address=staff.address,
        joining_date=staff.joining_date,
        basic_salary=staff.basic_salary,
        commission_enabled=staff.commission_enabled,
        active=staff.active,
        current_month_sales=current_month_sales.total_sales or Decimal('0'),
        current_month_bills=current_month_sales.bill_count or 0,
        lifetime_sales=lifetime_sales.total_sales or Decimal('0'),
        lifetime_bills=lifetime_sales.bill_count or 0,
        current_target=current_target.target_amount if current_target else None,
        achievement_percentage=achievement_percentage,
        working_days_current_month=working_days,
        recent_sales=recent_sales_list,
        created_at=staff.created_at
    )

@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: str,
    staff_update: StaffUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update staff information"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check code uniqueness if being updated
    if staff_update.code and staff_update.code != staff.code:
        existing = db.query(Staff).filter(
            Staff.code == staff_update.code,
            Staff.id != staff_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Staff code already exists")
    
    # Update fields
    for field, value in staff_update.dict(exclude_unset=True).items():
        if field not in ['create_user_account', 'user_password', 'user_role']:
            setattr(staff, field, value)
    
    staff.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(staff)
    
    return staff

@router.post("/{staff_id}/toggle-active")
async def toggle_staff_active(
    staff_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Toggle staff active status"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    staff.active = not staff.active
    staff.updated_at = datetime.utcnow()
    
    # Also deactivate user account if exists
    if staff.user_id:
        user = db.query(User).filter(User.id == staff.user_id).first()
        if user:
            user.active = staff.active
    
    db.commit()
    
    return {
        "success": True,
        "active": staff.active,
        "message": f"Staff {'activated' if staff.active else 'deactivated'} successfully"
    }

# =====================================
# Staff Targets & Incentives

@router.post("/targets", response_model=StaffTargetResponse)
async def create_staff_target(
    target_data: StaffTargetCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create target for staff member"""
    # Validate staff exists
    staff = db.query(Staff).filter(Staff.id == target_data.staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check for overlapping periods
    overlapping = db.query(StaffTarget).filter(
        StaffTarget.staff_id == target_data.staff_id,
        or_(
            and_(
                StaffTarget.period_start <= target_data.period_start,
                StaffTarget.period_end >= target_data.period_start
            ),
            and_(
                StaffTarget.period_start <= target_data.period_end,
                StaffTarget.period_end >= target_data.period_end
            )
        )
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Target period overlaps with existing target")
    
    target = StaffTarget(
        id=str(uuid.uuid4()),
        staff_id=target_data.staff_id,
        period_start=target_data.period_start,
        period_end=target_data.period_end,
        target_amount=target_data.target_amount,
        incentive_type=target_data.incentive_type,
        incentive_slabs=target_data.incentive_slabs,  # JSON field for multiple slabs
        min_achievement_for_incentive=target_data.min_achievement_for_incentive,
        created_at=datetime.utcnow()
    )
    
    db.add(target)
    db.commit()
    db.refresh(target)
    
    return target

@router.get("/targets")
async def get_targets(
    staff_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get staff targets"""
    query = db.query(StaffTarget)
    
    if staff_id:
        query = query.filter(StaffTarget.staff_id == staff_id)
    
    if active_only:
        today = date.today()
        query = query.filter(
            StaffTarget.period_start <= today,
            StaffTarget.period_end >= today
        )
    
    targets = query.all()
    
    result = []
    for target in targets:
        staff = target.staff
        
        # Calculate achievement
        sales = db.query(func.sum(Sale.final_payable)).filter(
            Sale.staff_id == target.staff_id,
            Sale.bill_date >= target.period_start,
            Sale.bill_date <= target.period_end
        ).scalar() or Decimal('0')
        
        achievement_percentage = Decimal('0')
        if target.target_amount > 0:
            achievement_percentage = (sales / target.target_amount * 100).quantize(Decimal('0.01'))
        
        result.append({
            "id": target.id,
            "staff_code": staff.code,
            "staff_name": staff.name,
            "period_start": target.period_start,
            "period_end": target.period_end,
            "target_amount": float(target.target_amount),
            "achieved_amount": float(sales),
            "achievement_percentage": float(achievement_percentage),
            "incentive_type": target.incentive_type,
            "incentive_slabs": target.incentive_slabs
        })
    
    return result

@router.put("/targets/{target_id}", response_model=StaffTargetResponse)
async def update_target(
    target_id: str,
    target_update: StaffTargetUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update staff target"""
    target = db.query(StaffTarget).filter(StaffTarget.id == target_id).first()
    
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Update fields
    for field, value in target_update.dict(exclude_unset=True).items():
        setattr(target, field, value)
    
    target.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(target)
    
    return target

# =====================================
# Performance & Commission Calculation

@router.get("/performance/{staff_id}")
async def get_staff_performance(
    staff_id: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed performance metrics for a staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Default to current month if dates not provided
    if not from_date:
        from_date = date.today().replace(day=1)
    if not to_date:
        to_date = date.today()
    
    # Get sales data
    sales_query = db.query(Sale).filter(
        Sale.staff_id == staff_id,
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date
    )
    
    total_sales = sales_query.with_entities(
        func.count(Sale.id).label('bill_count'),
        func.sum(Sale.final_payable).label('total_amount'),
        func.avg(Sale.final_payable).label('avg_bill_value')
    ).first()
    
    # Get daily breakdown
    daily_sales = sales_query.with_entities(
        func.date(Sale.bill_date).label('date'),
        func.count(Sale.id).label('bills'),
        func.sum(Sale.final_payable).label('amount')
    ).group_by(func.date(Sale.bill_date)).all()
    
    # Get category-wise sales
    category_sales = db.query(
        SaleItem.style_code,
        func.sum(SaleItem.qty).label('quantity'),
        func.sum(SaleItem.line_inclusive).label('amount')
    ).join(Sale).filter(
        Sale.staff_id == staff_id,
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date
    ).group_by(SaleItem.style_code).order_by(func.sum(SaleItem.line_inclusive).desc()).limit(10).all()
    
    # Get customer metrics
    unique_customers = sales_query.filter(
        Sale.customer_mobile.isnot(None)
    ).distinct(Sale.customer_mobile).count()
    
    repeat_customers = db.query(Sale.customer_mobile).filter(
        Sale.staff_id == staff_id,
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date,
        Sale.customer_mobile.isnot(None)
    ).group_by(Sale.customer_mobile).having(func.count(Sale.id) > 1).count()
    
    # Get returns handled
    returns = db.query(
        func.count(SaleReturn.id).label('return_count'),
        func.sum(SaleReturn.total_incl).label('return_amount')
    ).filter(
        SaleReturn.sr_date >= from_date,
        SaleReturn.sr_date <= to_date
    ).first()
    
    return {
        "staff_code": staff.code,
        "staff_name": staff.name,
        "period": {
            "from": from_date,
            "to": to_date
        },
        "sales_summary": {
            "total_bills": total_sales.bill_count or 0,
            "total_amount": float(total_sales.total_amount or 0),
            "average_bill_value": float(total_sales.avg_bill_value or 0)
        },
        "daily_performance": [
            {
                "date": day.date,
                "bills": day.bills,
                "amount": float(day.amount)
            } for day in daily_sales
        ],
        "top_products": [
            {
                "style_code": item.style_code,
                "quantity": item.quantity,
                "amount": float(item.amount)
            } for item in category_sales
        ],
        "customer_metrics": {
            "unique_customers": unique_customers,
            "repeat_customers": repeat_customers,
            "repeat_rate": round((repeat_customers / unique_customers * 100) if unique_customers > 0 else 0, 2)
        },
        "returns": {
            "count": returns.return_count or 0,
            "amount": float(returns.return_amount or 0)
        }
    }

@router.get("/commission/calculate")
async def calculate_commission(
    staff_id: Optional[str] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Calculate commission for staff members"""
    # Default to current month
    if not month:
        month = date.today().month
    if not year:
        year = date.today().year
    
    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get staff list
    query = db.query(Staff).filter(
        Staff.active == True,
        Staff.commission_enabled == True
    )
    
    if staff_id:
        query = query.filter(Staff.id == staff_id)
    
    staff_list = query.all()
    
    commission_details = []
    
    for staff in staff_list:
        # Get sales for the period
        sales = db.query(func.sum(Sale.final_payable)).filter(
            Sale.staff_id == staff.id,
            Sale.bill_date >= period_start,
            Sale.bill_date <= period_end
        ).scalar() or Decimal('0')
        
        # Get target for the period
        target = db.query(StaffTarget).filter(
            StaffTarget.staff_id == staff.id,
            StaffTarget.period_start <= period_start,
            StaffTarget.period_end >= period_end
        ).first()
        
        commission = Decimal('0')
        commission_rate = Decimal('0')
        achievement_percentage = Decimal('0')
        
        if target and target.target_amount > 0:
            achievement_percentage = (sales / target.target_amount * 100).quantize(Decimal('0.01'))
            
            # Check minimum achievement
            if achievement_percentage >= (target.min_achievement_for_incentive or 0):
                # Calculate commission based on slabs
                if target.incentive_slabs:
                    for slab in target.incentive_slabs:
                        if achievement_percentage >= slab['min'] and achievement_percentage <= slab['max']:
                            if target.incentive_type == 'percent':
                                commission_rate = Decimal(str(slab['rate']))
                                commission = (sales * commission_rate / 100).quantize(Decimal('0.01'))
                            else:  # flat
                                commission = Decimal(str(slab['amount']))
                            break
        
        commission_details.append({
            "staff_id": staff.id,
            "staff_code": staff.code,
            "staff_name": staff.name,
            "period": f"{calendar.month_name[month]} {year}",
            "sales_amount": float(sales),
            "target_amount": float(target.target_amount) if target else 0,
            "achievement_percentage": float(achievement_percentage),
            "commission_rate": float(commission_rate),
            "commission_amount": float(commission),
            "status": "eligible" if commission > 0 else "not_eligible"
        })
    
    total_commission = sum(c['commission_amount'] for c in commission_details)
    
    return {
        "period": f"{calendar.month_name[month]} {year}",
        "staff_count": len(commission_details),
        "total_commission": total_commission,
        "details": commission_details
    }

# =====================================
# Attendance Tracking (Optional)

@router.post("/attendance")
async def mark_attendance(
    attendance_data: StaffAttendanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark staff attendance"""
    # This is a simplified attendance system
    # In production, you might want a separate attendance table
    
    staff = db.query(Staff).filter(Staff.id == attendance_data.staff_id).first()
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Here you would save to an attendance table
    # For now, we'll just return success
    
    return {
        "success": True,
        "staff_code": staff.code,
        "date": attendance_data.date,
        "status": attendance_data.status,
        "check_in": attendance_data.check_in_time,
        "check_out": attendance_data.check_out_time
    }

# =====================================
# Import/Export

@router.post("/import", response_model=StaffImportResponse)
async def import_staff(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import staff from Excel file"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    content = await file.read()
    
    try:
        df = pd.read_excel(io.BytesIO(content))
        df.columns = df.columns.str.strip().str.upper()
        
        required_columns = ['CODE', 'NAME']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        imported = 0
        updated = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                code = str(row['CODE']).strip()
                name = str(row['NAME']).strip()
                
                existing = db.query(Staff).filter(Staff.code == code).first()
                
                if existing:
                    # Update existing staff
                    existing.name = name
                    if 'MOBILE' in row and pd.notna(row['MOBILE']):
                        existing.mobile = str(row['MOBILE']).strip()
                    if 'ROLE' in row and pd.notna(row['ROLE']):
                        existing.role = str(row['ROLE']).strip()
                    if 'EMAIL' in row and pd.notna(row['EMAIL']):
                        existing.email = str(row['EMAIL']).strip()
                    if 'BASIC_SALARY' in row and pd.notna(row['BASIC_SALARY']):
                        existing.basic_salary = Decimal(str(row['BASIC_SALARY']))
                    
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new staff
                    new_staff = Staff(
                        id=str(uuid.uuid4()),
                        code=code,
                        name=name,
                        mobile=str(row.get('MOBILE', '')).strip() if 'MOBILE' in row and pd.notna(row['MOBILE']) else None,
                        role=str(row.get('ROLE', 'Sales')).strip() if 'ROLE' in row and pd.notna(row['ROLE']) else 'Sales',
                        email=str(row.get('EMAIL', '')).strip() if 'EMAIL' in row and pd.notna(row['EMAIL']) else None,
                        basic_salary=Decimal(str(row['BASIC_SALARY'])) if 'BASIC_SALARY' in row and pd.notna(row['BASIC_SALARY']) else None,
                        joining_date=pd.to_datetime(row['JOINING_DATE']).date() if 'JOINING_DATE' in row and pd.notna(row['JOINING_DATE']) else date.today(),
                        commission_enabled='COMMISSION' in row and str(row['COMMISSION']).upper() == 'YES',
                        active=True
                    )
                    db.add(new_staff)
                    imported += 1
                    
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
        
        db.commit()
        
        return StaffImportResponse(
            success=True,
            imported=imported,
            updated=updated,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.get("/export/template")
async def export_staff_template():
    """Download Excel template for staff import"""
    columns = [
        'CODE', 'NAME', 'MOBILE', 'ROLE', 'EMAIL',
        'BASIC_SALARY', 'JOINING_DATE', 'COMMISSION'
    ]
    
    sample_data = {
        'CODE': 'EMP001',
        'NAME': 'John Doe',
        'MOBILE': '9876543210',
        'ROLE': 'Sales',
        'EMAIL': 'john@example.com',
        'BASIC_SALARY': '25000',
        'JOINING_DATE': '2024-01-15',
        'COMMISSION': 'YES'
    }
    
    df = pd.DataFrame([sample_data])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Staff', index=False)
    
    output.seek(0)
    
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=staff_template_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )

@router.get("/export/performance-report")
async def export_performance_report(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export staff performance report to Excel"""
    # Default to current month
    if not month:
        month = date.today().month
    if not year:
        year = date.today().year
    
    period_start = date(year, month, 1)
    period_end = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get all active staff
    staff_list = db.query(Staff).filter(Staff.active == True).all()
    
    report_data = []
    
    for staff in staff_list:
        # Get sales data
        sales = db.query(
            func.count(Sale.id).label('bills'),
            func.sum(Sale.final_payable).label('amount')
        ).filter(
            Sale.staff_id == staff.id,
            Sale.bill_date >= period_start,
            Sale.bill_date <= period_end
        ).first()
        
        # Get target
        target = db.query(StaffTarget).filter(
            StaffTarget.staff_id == staff.id,
            StaffTarget.period_start <= period_start,
            StaffTarget.period_end >= period_end
        ).first()
        
        achievement = Decimal('0')
        if target and target.target_amount > 0 and sales.amount:
            achievement = (sales.amount / target.target_amount * 100).quantize(Decimal('0.01'))
        
        report_data.append({
            'Staff Code': staff.code,
            'Staff Name': staff.name,
            'Role': staff.role,
            'Total Bills': sales.bills or 0,
            'Total Sales': float(sales.amount or 0),
            'Target': float(target.target_amount) if target else 0,
            'Achievement %': float(achievement),
            'Status': 'Active' if staff.active else 'Inactive'
        })
    
    df = pd.DataFrame(report_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'Performance_{calendar.month_name[month]}_{year}', index=False)
    
    output.seek(0)
    
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=staff_performance_{year}_{month:02d}.xlsx"
        }
    )

# Helper functions

def get_working_days_count(start_date: date, end_date: date) -> int:
    """Calculate working days between two dates (excluding Sundays)"""
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() != 6:  # Not Sunday
            days += 1
        current += timedelta(days=1)
    return days