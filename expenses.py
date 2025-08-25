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
from ...models import (
    ExpenseHead, Expense, PaymentMode, Sale, SalePayment,
    PurchaseBill, Staff, User
)
from ...services.excel_service import ExcelService
from ...core.security import get_current_user
from ...core.rbac import require_role
from ...schemas.expense_schema import (
    ExpenseHeadCreate, ExpenseHeadUpdate, ExpenseHeadResponse,
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseDetailResponse,
    ExpenseSummaryResponse, CashFlowResponse, BankReconciliationResponse,
    ExpenseImportResponse, ExpenseBulkApprovalRequest
)

router = APIRouter()

# =====================================
# Expense Head Management

@router.post("/heads", response_model=ExpenseHeadResponse)
async def create_expense_head(
    head_data: ExpenseHeadCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new expense head/category"""
    # Check if name already exists
    existing = db.query(ExpenseHead).filter(
        func.lower(ExpenseHead.name) == head_data.name.lower(),
        ExpenseHead.active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Expense head already exists")
    
    expense_head = ExpenseHead(
        id=str(uuid.uuid4()),
        name=head_data.name,
        description=head_data.description,
        category=head_data.category,
        budget_monthly=head_data.budget_monthly,
        requires_approval=head_data.requires_approval,
        active=True,
        created_at=datetime.utcnow(),
        created_by=current_user.id
    )
    
    db.add(expense_head)
    db.commit()
    db.refresh(expense_head)
    
    return expense_head

@router.get("/heads", response_model=List[ExpenseHeadResponse])
async def get_expense_heads(
    category: Optional[str] = None,
    active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all expense heads/categories"""
    query = db.query(ExpenseHead)
    
    if category:
        query = query.filter(ExpenseHead.category == category)
    
    if active is not None:
        query = query.filter(ExpenseHead.active == active)
    
    expense_heads = query.order_by(ExpenseHead.category, ExpenseHead.name).all()
    
    # Add current month expense for each head
    current_month_start = date.today().replace(day=1)
    
    result = []
    for head in expense_heads:
        current_expense = db.query(func.sum(Expense.amount)).filter(
            Expense.head_id == head.id,
            Expense.date >= current_month_start,
            Expense.status != 'cancelled'
        ).scalar() or Decimal('0')
        
        head_dict = {
            "id": head.id,
            "name": head.name,
            "description": head.description,
            "category": head.category,
            "budget_monthly": head.budget_monthly,
            "current_month_expense": current_expense,
            "budget_utilized": (current_expense / head.budget_monthly * 100).quantize(Decimal('0.01')) if head.budget_monthly else None,
            "requires_approval": head.requires_approval,
            "active": head.active,
            "created_at": head.created_at
        }
        result.append(head_dict)
    
    return result

@router.put("/heads/{head_id}", response_model=ExpenseHeadResponse)
async def update_expense_head(
    head_id: str,
    head_update: ExpenseHeadUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense head"""
    expense_head = db.query(ExpenseHead).filter(ExpenseHead.id == head_id).first()
    
    if not expense_head:
        raise HTTPException(status_code=404, detail="Expense head not found")
    
    # Check name uniqueness if being updated
    if head_update.name and head_update.name != expense_head.name:
        existing = db.query(ExpenseHead).filter(
            func.lower(ExpenseHead.name) == head_update.name.lower(),
            ExpenseHead.id != head_id,
            ExpenseHead.active == True
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Expense head name already exists")
    
    for field, value in head_update.dict(exclude_unset=True).items():
        setattr(expense_head, field, value)
    
    expense_head.updated_at = datetime.utcnow()
    expense_head.updated_by = current_user.id
    db.commit()
    db.refresh(expense_head)
    
    return expense_head

@router.delete("/heads/{head_id}")
async def delete_expense_head(
    head_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Soft delete expense head"""
    expense_head = db.query(ExpenseHead).filter(ExpenseHead.id == head_id).first()
    
    if not expense_head:
        raise HTTPException(status_code=404, detail="Expense head not found")
    
    # Check if there are expenses under this head
    expense_count = db.query(func.count(Expense.id)).filter(
        Expense.head_id == head_id
    ).scalar()
    
    if expense_count > 0:
        # Soft delete - just deactivate
        expense_head.active = False
        expense_head.updated_at = datetime.utcnow()
        expense_head.updated_by = current_user.id
        db.commit()
        return {"success": True, "message": f"Expense head deactivated (has {expense_count} expenses)"}
    else:
        # Hard delete if no expenses
        db.delete(expense_head)
        db.commit()
        return {"success": True, "message": "Expense head deleted permanently"}

# =====================================
# Expense Entry Management

@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new expense entry"""
    # Validate expense head
    expense_head = db.query(ExpenseHead).filter(
        ExpenseHead.id == expense_data.head_id,
        ExpenseHead.active == True
    ).first()
    
    if not expense_head:
        raise HTTPException(status_code=404, detail="Expense head not found or inactive")
    
    # Validate payment mode if provided
    if expense_data.payment_mode_id:
        payment_mode = db.query(PaymentMode).filter(
            PaymentMode.id == expense_data.payment_mode_id,
            PaymentMode.active == True
        ).first()
        if not payment_mode:
            raise HTTPException(status_code=404, detail="Payment mode not found or inactive")
    
    # Check if approval required
    status = 'pending' if expense_head.requires_approval else 'approved'
    
    expense = Expense(
        id=str(uuid.uuid4()),
        date=expense_data.date or date.today(),
        head_id=expense_data.head_id,
        amount=expense_data.amount,
        mode=expense_data.mode,
        payment_mode_id=expense_data.payment_mode_id,
        reference_no=expense_data.reference_no,
        vendor_name=expense_data.vendor_name,
        bill_no=expense_data.bill_no,
        description=expense_data.description,
        status=status,
        created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    # If auto-approved, set approval details
    if status == 'approved':
        expense.approved_by = current_user.id
        expense.approved_at = datetime.utcnow()
    
    db.add(expense)
    db.commit()
    db.refresh(expense)
    
    return expense

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = 0,
    limit: int = 100,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    head_id: Optional[str] = None,
    mode: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expenses with filters"""
    query = db.query(Expense)
    
    # Date filters
    if from_date:
        query = query.filter(Expense.date >= from_date)
    if to_date:
        query = query.filter(Expense.date <= to_date)
    
    # Other filters
    if head_id:
        query = query.filter(Expense.head_id == head_id)
    if mode:
        query = query.filter(Expense.mode == mode)
    if status:
        query = query.filter(Expense.status == status)
    
    expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseDetailResponse)
async def get_expense_details(
    expense_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed expense information"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Get head details
    head = expense.head
    
    # Get created by user
    created_user = db.query(User).filter(User.id == expense.created_by).first()
    
    # Get approved by user if applicable
    approved_user = None
    if expense.approved_by:
        approved_user = db.query(User).filter(User.id == expense.approved_by).first()
    
    return ExpenseDetailResponse(
        id=expense.id,
        date=expense.date,
        head_id=expense.head_id,
        head_name=head.name,
        head_category=head.category,
        amount=expense.amount,
        mode=expense.mode,
        payment_mode_id=expense.payment_mode_id,
        payment_mode_name=expense.payment_mode.name if expense.payment_mode else None,
        reference_no=expense.reference_no,
        vendor_name=expense.vendor_name,
        bill_no=expense.bill_no,
        description=expense.description,
        status=expense.status,
        created_by=expense.created_by,
        created_by_name=created_user.display_name if created_user else None,
        created_at=expense.created_at,
        approved_by=expense.approved_by,
        approved_by_name=approved_user.display_name if approved_user else None,
        approved_at=expense.approved_at,
        updated_at=expense.updated_at
    )

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense entry"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Check if expense is approved/cancelled
    if expense.status in ['approved', 'cancelled']:
        if current_user.role != 'admin':
            raise HTTPException(
                status_code=403,
                detail=f"Cannot modify {expense.status} expense"
            )
    
    # Update fields
    for field, value in expense_update.dict(exclude_unset=True).items():
        if field != 'status':  # Status change handled separately
            setattr(expense, field, value)
    
    expense.updated_at = datetime.utcnow()
    expense.updated_by = current_user.id
    db.commit()
    db.refresh(expense)
    
    return expense

@router.post("/{expense_id}/approve")
async def approve_expense(
    expense_id: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve a pending expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Expense is already {expense.status}")
    
    # Check authorization
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to approve expenses")
    
    expense.status = 'approved'
    expense.approved_by = current_user.id
    expense.approved_at = datetime.utcnow()
    expense.approval_notes = notes
    expense.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "message": "Expense approved successfully"}

@router.post("/{expense_id}/reject")
async def reject_expense(
    expense_id: str,
    reason: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reject a pending expense"""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    if expense.status != 'pending':
        raise HTTPException(status_code=400, detail=f"Expense is already {expense.status}")
    
    # Check authorization
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to reject expenses")
    
    expense.status = 'rejected'
    expense.approved_by = current_user.id  # Track who rejected
    expense.approved_at = datetime.utcnow()
    expense.approval_notes = f"Rejected: {reason}"
    expense.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"success": True, "message": "Expense rejected"}

@router.post("/bulk-approve")
async def bulk_approve_expenses(
    request: ExpenseBulkApprovalRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve multiple expenses at once"""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Not authorized to approve expenses")
    
    approved_count = 0
    errors = []
    
    for expense_id in request.expense_ids:
        expense = db.query(Expense).filter(Expense.id == expense_id).first()
        
        if not expense:
            errors.append(f"Expense {expense_id} not found")
            continue
        
        if expense.status != 'pending':
            errors.append(f"Expense {expense_id} is already {expense.status}")
            continue
        
        expense.status = 'approved'
        expense.approved_by = current_user.id
        expense.approved_at = datetime.utcnow()
        expense.approval_notes = request.notes
        expense.updated_at = datetime.utcnow()
        approved_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "approved_count": approved_count,
        "errors": errors
    }

# =====================================
# Cash Flow & Reconciliation

@router.get("/cashflow/summary")
async def get_cashflow_summary(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get cash flow summary (cash in hand calculation)"""
    # Default to current month
    if not from_date:
        from_date = date.today().replace(day=1)
    if not to_date:
        to_date = date.today()
    
    # Opening balance (would be from previous period closing)
    opening_balance = Decimal('0')  # In production, fetch from previous closing
    
    # Cash sales (POS cash payments)
    cash_sales = db.query(func.sum(SalePayment.amount)).join(
        PaymentMode
    ).filter(
        SalePayment.settlement_type == 'cash',
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date
    ).scalar() or Decimal('0')
    
    # Cash expenses
    cash_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.mode == 'cash',
        Expense.date >= from_date,
        Expense.date <= to_date,
        Expense.status == 'approved'
    ).scalar() or Decimal('0')
    
    # Cash purchases (if any)
    cash_purchases = db.query(func.sum(PurchaseBill.grand_total)).filter(
        PurchaseBill.payment_mode == 'cash',
        PurchaseBill.pb_date >= from_date,
        PurchaseBill.pb_date <= to_date
    ).scalar() or Decimal('0')
    
    # Calculate closing balance
    total_cash_in = opening_balance + cash_sales
    total_cash_out = cash_expenses + cash_purchases
    closing_balance = total_cash_in - total_cash_out
    
    # Daily breakdown
    daily_cashflow = []
    current = from_date
    while current <= to_date:
        day_sales = db.query(func.sum(SalePayment.amount)).join(
            Sale, PaymentMode
        ).filter(
            SalePayment.settlement_type == 'cash',
            func.date(Sale.bill_date) == current
        ).scalar() or Decimal('0')
        
        day_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.mode == 'cash',
            Expense.date == current,
            Expense.status == 'approved'
        ).scalar() or Decimal('0')
        
        daily_cashflow.append({
            "date": current,
            "cash_in": float(day_sales),
            "cash_out": float(day_expenses),
            "net": float(day_sales - day_expenses)
        })
        
        current += timedelta(days=1)
    
    return CashFlowResponse(
        period_start=from_date,
        period_end=to_date,
        opening_balance=opening_balance,
        cash_sales=cash_sales,
        cash_expenses=cash_expenses,
        cash_purchases=cash_purchases,
        total_cash_in=total_cash_in,
        total_cash_out=total_cash_out,
        closing_balance=closing_balance,
        daily_breakdown=daily_cashflow
    )

@router.get("/bank/reconciliation")
async def get_bank_reconciliation(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get bank reconciliation summary"""
    # Default to current month
    if not from_date:
        from_date = date.today().replace(day=1)
    if not to_date:
        to_date = date.today()
    
    # Bank collections from sales
    bank_collections = db.query(func.sum(SalePayment.amount)).join(
        PaymentMode
    ).filter(
        SalePayment.settlement_type == 'bank',
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date
    ).scalar() or Decimal('0')
    
    # Bank expenses
    bank_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.mode == 'bank',
        Expense.date >= from_date,
        Expense.date <= to_date,
        Expense.status == 'approved'
    ).scalar() or Decimal('0')
    
    # Supplier machine collections (off-bank)
    supplier_collections = db.query(func.sum(SalePayment.amount)).join(
        PaymentMode
    ).filter(
        SalePayment.settlement_type == 'supplier',
        Sale.bill_date >= from_date,
        Sale.bill_date <= to_date
    ).scalar() or Decimal('0')
    
    return BankReconciliationResponse(
        period_start=from_date,
        period_end=to_date,
        bank_collections=bank_collections,
        bank_expenses=bank_expenses,
        net_bank_balance=bank_collections - bank_expenses,
        supplier_collections=supplier_collections,
        total_card_collections=bank_collections + supplier_collections
    )

# =====================================
# Reports & Analytics

@router.get("/summary/by-category")
async def get_expense_summary_by_category(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense summary grouped by category"""
    # Default to current month
    if not from_date:
        from_date = date.today().replace(day=1)
    if not to_date:
        to_date = date.today()
    
    # Get expenses grouped by category
    category_expenses = db.query(
        ExpenseHead.category,
        func.count(Expense.id).label('count'),
        func.sum(Expense.amount).label('total')
    ).join(ExpenseHead).filter(
        Expense.date >= from_date,
        Expense.date <= to_date,
        Expense.status.in_(['approved', 'pending'])
    ).group_by(ExpenseHead.category).all()
    
    # Get head-wise breakdown
    head_expenses = db.query(
        ExpenseHead.name,
        ExpenseHead.category,
        ExpenseHead.budget_monthly,
        func.count(Expense.id).label('count'),
        func.sum(Expense.amount).label('total')
    ).join(ExpenseHead).filter(
        Expense.date >= from_date,
        Expense.date <= to_date,
        Expense.status.in_(['approved', 'pending'])
    ).group_by(ExpenseHead.id).all()
    
    categories = {}
    for cat in category_expenses:
        categories[cat.category] = {
            "category": cat.category,
            "count": cat.count,
            "total": float(cat.total),
            "heads": []
        }
    
    for head in head_expenses:
        if head.category in categories:
            categories[head.category]["heads"].append({
                "name": head.name,
                "budget": float(head.budget_monthly) if head.budget_monthly else None,
                "spent": float(head.total),
                "count": head.count,
                "utilization": (head.total / head.budget_monthly * 100).quantize(Decimal('0.01')) if head.budget_monthly else None
            })
    
    return {
        "period_start": from_date,
        "period_end": to_date,
        "categories": list(categories.values()),
        "total_expense": sum(cat["total"] for cat in categories.values())
    }

@router.get("/summary/trend")
async def get_expense_trend(
    months: int = 6,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get expense trend for last N months"""
    trends = []
    today = date.today()
    
    for i in range(months - 1, -1, -1):
        # Calculate month start and end
        month_date = today - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        
        if i == 0:
            month_end = today
        else:
            next_month = month_start + timedelta(days=32)
            month_end = (next_month.replace(day=1) - timedelta(days=1))
        
        # Get expenses for the month
        month_expense = db.query(func.sum(Expense.amount)).filter(
            Expense.date >= month_start,
            Expense.date <= month_end,
            Expense.status.in_(['approved', 'pending'])
        ).scalar() or Decimal('0')
        
        trends.append({
            "month": month_start.strftime("%B %Y"),
            "amount": float(month_expense)
        })
    
    return {"trend": trends}

# =====================================
# Import/Export

@router.post("/import", response_model=ExpenseImportResponse)
async def import_expenses(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Import expenses from Excel file"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    content = await file.read()
    
    try:
        df = pd.read_excel(io.BytesIO(content))
        df.columns = df.columns.str.strip().str.upper()
        
        required_columns = ['DATE', 'HEAD', 'AMOUNT']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Find expense head
                head_name = str(row['HEAD']).strip()
                expense_head = db.query(ExpenseHead).filter(
                    func.lower(ExpenseHead.name) == head_name.lower(),
                    ExpenseHead.active == True
                ).first()
                
                if not expense_head:
                    errors.append(f"Row {idx+2}: Expense head '{head_name}' not found")
                    continue
                
                # Parse date
                expense_date = pd.to_datetime(row['DATE']).date()
                
                # Create expense
                expense = Expense(
                    id=str(uuid.uuid4()),
                    date=expense_date,
                    head_id=expense_head.id,
                    amount=Decimal(str(row['AMOUNT'])),
                    mode=str(row.get('MODE', 'cash')).lower() if 'MODE' in row else 'cash',
                    vendor_name=str(row.get('VENDOR', '')).strip() if 'VENDOR' in row and pd.notna(row['VENDOR']) else None,
                    bill_no=str(row.get('BILL_NO', '')).strip() if 'BILL_NO' in row and pd.notna(row['BILL_NO']) else None,
                    description=str(row.get('DESCRIPTION', '')).strip() if 'DESCRIPTION' in row and pd.notna(row['DESCRIPTION']) else None,
                    status='approved' if not expense_head.requires_approval else 'pending',
                    created_by=current_user.id,
                    created_at=datetime.utcnow()
                )
                
                if expense.status == 'approved':
                    expense.approved_by = current_user.id
                    expense.approved_at = datetime.utcnow()
                
                db.add(expense)
                imported += 1
                
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
        
        db.commit()
        
        return ExpenseImportResponse(
            success=True,
            imported=imported,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.get("/export")
async def export_expenses(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export expenses to Excel"""
    # Default to current month
    if not from_date:
        from_date = date.today().replace(day=1)
    if not to_date:
        to_date = date.today()
    
    # Get expenses with joins
    expenses = db.query(Expense).filter(
        Expense.date >= from_date,
        Expense.date <= to_date
    ).order_by(Expense.date).all()
    
    # Prepare data for export
    export_data = []
    for expense in expenses:
        export_data.append({
            'Date': expense.date.strftime("%Y-%m-%d"),
            'Head': expense.head.name,
            'Category': expense.head.category,
            'Amount': float(expense.amount),
            'Mode': expense.mode,
            'Vendor': expense.vendor_name or '',
            'Bill No': expense.bill_no or '',
            'Reference': expense.reference_no or '',
            'Description': expense.description or '',
            'Status': expense.status,
            'Created By': expense.created_by_user.display_name if expense.created_by_user else '',
            'Approved By': expense.approved_by_user.display_name if expense.approved_by_user else ''
        })
    
    df = pd.DataFrame(export_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'Expenses_{from_date}_{to_date}', index=False)
        
        # Add summary sheet
        summary_df = df.groupby(['Category', 'Head']).agg({
            'Amount': 'sum'
        }).reset_index()
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=expenses_{from_date}_{to_date}.xlsx"
        }
    )

@router.get("/export/template")
async def export_expense_template():
    """Download Excel template for expense import"""
    columns = [
        'DATE', 'HEAD', 'AMOUNT', 'MODE', 'VENDOR',
        'BILL_NO', 'DESCRIPTION'
    ]
    
    sample_data = {
        'DATE': '2024-01-15',
        'HEAD': 'Tea & Snacks',
        'AMOUNT': '250.00',
        'MODE': 'cash',
        'VENDOR': 'Local Tea Shop',
        'BILL_NO': 'B123',
        'DESCRIPTION': 'Daily tea expenses'
    }
    
    df = pd.DataFrame([sample_data])
    
    # Add available heads as reference
    heads_df = pd.DataFrame({
        'Available Expense Heads': [
            'Tea & Snacks', 'Electricity', 'Rent', 'Salary',
            'Internet', 'Stationery', 'Maintenance', 'Transport'
        ]
    })
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Expense_Template', index=False)
        heads_df.to_excel(writer, sheet_name='Reference_Heads', index=False)
    
    output.seek(0)
    
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=expense_template_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )
