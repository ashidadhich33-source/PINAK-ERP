# backend/app/api/endpoints/customers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from decimal import Decimal
from datetime import date, datetime

from ...database import get_db
from ...models.customer import Customer, CustomerGroup
from ...models.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class CustomerResponse(BaseModel):
    id: int
    customer_code: str
    name: str
    display_name: Optional[str] = None
    customer_type: str
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    business_name: Optional[str] = None
    credit_limit: Decimal = 0
    payment_terms: Optional[str] = None
    current_balance: Decimal = 0
    discount_percent: Decimal = 0
    price_list: Optional[str] = None
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    gender: Optional[str] = None
    status: str = "active"
    is_loyalty_member: bool = False
    loyalty_card_number: Optional[str] = None
    first_sale_date: Optional[datetime] = None
    last_sale_date: Optional[datetime] = None
    total_sales_amount: Decimal = 0
    total_transactions: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerCreateRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    customer_type: str = "retail"
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    business_name: Optional[str] = None
    credit_limit: Decimal = 0
    payment_terms: Optional[str] = None
    opening_balance: Decimal = 0
    discount_percent: Decimal = 0
    price_list: Optional[str] = None
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    gender: Optional[str] = None
    is_loyalty_member: bool = False

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Customer name cannot be empty')
        return v.strip()

    @validator('mobile')
    def validate_mobile(cls, v):
        if v and len(v.strip()) > 0:
            # Basic mobile number validation
            mobile = v.strip().replace('+', '').replace('-', '').replace(' ', '')
            if not mobile.isdigit() or len(mobile) < 10:
                raise ValueError('Invalid mobile number')
            return mobile
        return v

    @validator('gst_number')
    def validate_gst(cls, v):
        if v and len(v.strip()) > 0:
            gst = v.strip().upper()
            if len(gst) != 15:
                raise ValueError('GST number must be 15 characters')
            return gst
        return v

class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    customer_type: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    business_name: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    discount_percent: Optional[Decimal] = None
    price_list: Optional[str] = None
    date_of_birth: Optional[date] = None
    anniversary_date: Optional[date] = None
    gender: Optional[str] = None
    status: Optional[str] = None
    is_loyalty_member: Optional[bool] = None

class CustomerGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    discount_percent: Decimal = 0
    price_list: Optional[str] = None
    credit_limit: Decimal = 0
    credit_days: int = 0

    class Config:
        from_attributes = True

class CustomerGroupCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    discount_percent: Decimal = 0
    price_list: Optional[str] = None
    credit_limit: Decimal = 0
    credit_days: int = 0

# Helper function to generate customer code
def generate_customer_code(db: Session, customer_type: str = "retail") -> str:
    """Generate unique customer code"""
    prefix = "C"
    if customer_type == "wholesale":
        prefix = "W"
    elif customer_type == "corporate":
        prefix = "CORP"
    
    # Get next number
    last_customer = db.query(Customer).filter(
        Customer.customer_code.like(f"{prefix}%")
    ).order_by(Customer.customer_code.desc()).first()
    
    if last_customer:
        try:
            last_num = int(last_customer.customer_code.replace(prefix, ""))
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}{next_num:06d}"

# Customer endpoints
@router.get("", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in name, mobile, or email"),
    customer_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    loyalty_members_only: bool = Query(False),
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customers with filtering and pagination"""
    
    query = db.query(Customer)
    
    # Apply filters
    if search:
        search_filter = or_(
            Customer.name.ilike(f"%{search}%"),
            Customer.mobile.ilike(f"%{search}%"),
            Customer.email.ilike(f"%{search}%"),
            Customer.customer_code.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)
    
    if status:
        query = query.filter(Customer.status == status)
    
    if loyalty_members_only:
        query = query.filter(Customer.is_loyalty_member == True)
    
    # Get customers
    customers = query.offset(skip).limit(limit).all()
    
    return [CustomerResponse.from_orm(customer) for customer in customers]

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customer by ID"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.from_orm(customer)

@router.get("/code/{customer_code}", response_model=CustomerResponse)
async def get_customer_by_code(
    customer_code: str,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customer by customer code"""
    
    customer = db.query(Customer).filter(Customer.customer_code == customer_code).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.from_orm(customer)

@router.get("/mobile/{mobile}", response_model=CustomerResponse)
async def get_customer_by_mobile(
    mobile: str,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customer by mobile number"""
    
    customer = db.query(Customer).filter(Customer.mobile == mobile).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerResponse.from_orm(customer)

@router.post("", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreateRequest,
    current_user: User = Depends(require_permission("customers.create")),
    db: Session = Depends(get_db)
):
    """Create new customer"""
    
    # Check if mobile number already exists (if provided)
    if customer_data.mobile:
        existing_mobile = db.query(Customer).filter(Customer.mobile == customer_data.mobile).first()
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this mobile number already exists"
            )
    
    # Check if email already exists (if provided)
    if customer_data.email:
        existing_email = db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists"
            )
    
    # Generate customer code
    customer_code = generate_customer_code(db, customer_data.customer_type)
    
    # Create customer
    customer_dict = customer_data.dict()
    customer_dict['customer_code'] = customer_code
    customer_dict['current_balance'] = customer_dict.pop('opening_balance', 0)
    customer_dict['created_by'] = current_user.id
    
    db_customer = Customer(**customer_dict)
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return CustomerResponse.from_orm(db_customer)

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdateRequest,
    current_user: User = Depends(require_permission("customers.edit")),
    db: Session = Depends(get_db)
):
    """Update customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check for duplicate mobile (if being updated)
    if customer_data.mobile and customer_data.mobile != customer.mobile:
        existing_mobile = db.query(Customer).filter(
            and_(Customer.mobile == customer_data.mobile, Customer.id != customer_id)
        ).first()
        if existing_mobile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this mobile number already exists"
            )
    
    # Check for duplicate email (if being updated)
    if customer_data.email and customer_data.email != customer.email:
        existing_email = db.query(Customer).filter(
            and_(Customer.email == customer_data.email, Customer.id != customer_id)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists"
            )
    
    # Update customer fields
    update_data = customer_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    customer.updated_by = current_user.id
    
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse.from_orm(customer)

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.delete")),
    db: Session = Depends(get_db)
):
    """Delete customer (soft delete)"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if customer has transactions
    if customer.total_transactions > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer with existing transactions. Set status to inactive instead."
        )
    
    # Check if customer has outstanding balance
    if customer.current_balance != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer with outstanding balance."
        )
    
    # Soft delete
    customer.status = 'inactive'
    customer.is_active = False
    customer.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Customer deleted successfully"}

@router.put("/{customer_id}/toggle-status")
async def toggle_customer_status(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.edit")),
    db: Session = Depends(get_db)
):
    """Activate/deactivate customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer.is_active = not customer.is_active
    customer.status = 'active' if customer.is_active else 'inactive'
    customer.updated_by = current_user.id
    
    db.commit()
    
    return {"message": f"Customer {'activated' if customer.is_active else 'deactivated'} successfully"}

@router.put("/{customer_id}/loyalty")
async def toggle_loyalty_membership(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.edit")),
    db: Session = Depends(get_db)
):
    """Toggle customer loyalty membership"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer.is_loyalty_member = not customer.is_loyalty_member
    
    # Generate loyalty card number if becoming a member
    if customer.is_loyalty_member and not customer.loyalty_card_number:
        card_count = db.query(Customer).filter(Customer.loyalty_card_number.isnot(None)).count()
        customer.loyalty_card_number = f"LC{card_count + 1:08d}"
    
    customer.updated_by = current_user.id
    db.commit()
    
    return {
        "message": f"Customer {'enrolled in' if customer.is_loyalty_member else 'removed from'} loyalty program",
        "loyalty_card_number": customer.loyalty_card_number
    }

@router.get("/{customer_id}/balance-summary")
async def get_customer_balance_summary(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customer balance and transaction summary"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Calculate additional metrics (would need proper queries with related tables)
    return {
        "customer_id": customer.id,
        "customer_name": customer.name,
        "current_balance": customer.current_balance,
        "credit_limit": customer.credit_limit,
        "available_credit": customer.credit_limit - customer.current_balance,
        "total_sales": customer.total_sales_amount,
        "total_transactions": customer.total_transactions,
        "last_transaction_date": customer.last_sale_date,
        "is_credit_limit_exceeded": customer.current_balance > customer.credit_limit
    }

# Customer Groups endpoints
@router.get("/groups", response_model=List[CustomerGroupResponse])
async def get_customer_groups(
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get all customer groups"""
    
    groups = db.query(CustomerGroup).filter(CustomerGroup.is_active == True).all()
    return [CustomerGroupResponse.from_orm(group) for group in groups]

@router.post("/groups", response_model=CustomerGroupResponse)
async def create_customer_group(
    group_data: CustomerGroupCreateRequest,
    current_user: User = Depends(require_permission("customers.create")),
    db: Session = Depends(get_db)
):
    """Create new customer group"""
    
    # Check if group name already exists
    existing = db.query(CustomerGroup).filter(CustomerGroup.name == group_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer group with this name already exists"
        )
    
    db_group = CustomerGroup(
        **group_data.dict(),
        created_by=current_user.id
    )
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return CustomerGroupResponse.from_orm(db_group)