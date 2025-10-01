# backend/app/api/endpoints/customers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.customers.customer import Customer
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    company_id: int

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    gst_number: Optional[str]
    total_purchases: Decimal
    credit_limit: Decimal
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/customers", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(require_permission("customers.create")),
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    
    # Check if customer with same email already exists
    if customer_data.email:
        existing_customer = db.query(Customer).filter(
            Customer.email == customer_data.email,
            Customer.company_id == customer_data.company_id
        ).first()
        
        if existing_customer:
            raise HTTPException(
                status_code=400,
                detail="Customer with this email already exists"
            )
    
    # Create customer
    customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        phone=customer_data.phone,
        address=customer_data.address,
        gst_number=customer_data.gst_number,
        company_id=customer_data.company_id,
        created_by=current_user.id
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer

@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get customers for a company"""
    
    customers = db.query(Customer).filter(
        Customer.company_id == company_id
    ).offset(skip).limit(limit).all()
    
    return customers

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.view")),
    db: Session = Depends(get_db)
):
    """Get a specific customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerCreate,
    current_user: User = Depends(require_permission("customers.update")),
    db: Session = Depends(get_db)
):
    """Update a customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update customer fields
    customer.name = customer_data.name
    customer.email = customer_data.email
    customer.phone = customer_data.phone
    customer.address = customer_data.address
    customer.gst_number = customer_data.gst_number
    customer.updated_by = current_user.id
    
    db.commit()
    db.refresh(customer)
    
    return customer

@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customers.delete")),
    db: Session = Depends(get_db)
):
    """Delete a customer"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Soft delete
    customer.is_active = False
    customer.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Customer deleted successfully"}