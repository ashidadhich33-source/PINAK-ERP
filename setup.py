from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...database import get_db
from ...models import Company, BillSeries, PaymentMode, ExpenseHead, LoyaltyGrade
from ...core.security import get_current_user
from ...core.rbac import require_role

router = APIRouter()

@router.post("/company")
async def create_company(
    name: str,
    gstin: str = None,
    mobile: str = None,
    address: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create company setup"""
    company = Company(
        id=str(uuid.uuid4()),
        name=name,
        gstin=gstin,
        mobile=mobile,
        address=address
    )
    
    db.add(company)
    
    # Update user's company
    current_user.company_id = company.id
    
    # Create default bill series
    series = [
        BillSeries(
            id=str(uuid.uuid4()),
            code="SALE",
            description="Sale Bills",
            prefix="S",
            next_no=1,
            width=5,
            fy="2024-25",
            default_tax_region="local",
            active=True
        ),
        BillSeries(
            id=str(uuid.uuid4()),
            code="SR",
            description="Sale Returns",
            prefix="SR",
            next_no=1,
            width=5,
            fy="2024-25",
            default_tax_region="local",
            active=True
        ),
        BillSeries(
            id=str(uuid.uuid4()),
            code="PB",
            description="Purchase Bills",
            prefix="PB",
            next_no=1,
            width=5,
            fy="2024-25",
            default_tax_region="local",
            active=True
        ),
        BillSeries(
            id=str(uuid.uuid4()),
            code="PR",
            description="Purchase Returns",
            prefix="PR",
            next_no=1,
            width=5,
            fy="2024-25",
            default_tax_region="local",
            active=True
        )
    ]
    
    for s in series:
        db.add(s)
    
    # Create default payment modes
    payment_modes = [
        PaymentMode(
            id=str(uuid.uuid4()),
            name="Cash",
            settlement_type="cash",
            active=True
        ),
        PaymentMode(
            id=str(uuid.uuid4()),
            name="Card",
            settlement_type="bank",
            active=True
        ),
        PaymentMode(
            id=str(uuid.uuid4()),
            name="UPI",
            settlement_type="bank",
            active=True
        )
    ]
    
    for pm in payment_modes:
        db.add(pm)
    
    # Create default loyalty grades
    loyalty_grades = [
        LoyaltyGrade(
            id=str(uuid.uuid4()),
            name="Silver",
            amount_from=0,
            amount_to=10000,
            earn_pct=1.0
        ),
        LoyaltyGrade(
            id=str(uuid.uuid4()),
            name="Gold",
            amount_from=10001,
            amount_to=20000,
            earn_pct=1.5
        ),
        LoyaltyGrade(
            id=str(uuid.uuid4()),
            name="Platinum",
            amount_from=20001,
            amount_to=999999999,
            earn_pct=2.0
        )
    ]
    
    for lg in loyalty_grades:
        db.add(lg)
    
    db.commit()
    
    return {
        "message": "Company setup completed",
        "company_id": company.id
    }

@router.get("/company")
async def get_company(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get company details"""
    if not current_user.company_id:
        raise HTTPException(status_code=404, detail="No company setup found")
    
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    return company

@router.put("/company")
async def update_company(
    name: str = None,
    gstin: str = None,
    mobile: str = None,
    address: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update company details"""
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if name:
        company.name = name
    if gstin:
        company.gstin = gstin
    if mobile:
        company.mobile = mobile
    if address:
        company.address = address
    
    db.commit()
    return {"message": "Company updated successfully"}