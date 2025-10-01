# backend/app/api/endpoints/suppliers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.customers.supplier import Supplier
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class SupplierCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    company_id: int

class SupplierResponse(BaseModel):
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

@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_permission("suppliers.create")),
    db: Session = Depends(get_db)
):
    """Create a new supplier"""
    
    # Check if supplier with same email already exists
    if supplier_data.email:
        existing_supplier = db.query(Supplier).filter(
            Supplier.email == supplier_data.email,
            Supplier.company_id == supplier_data.company_id
        ).first()
        
        if existing_supplier:
            raise HTTPException(
                status_code=400,
                detail="Supplier with this email already exists"
            )
    
    # Create supplier
    supplier = Supplier(
        name=supplier_data.name,
        email=supplier_data.email,
        phone=supplier_data.phone,
        address=supplier_data.address,
        gst_number=supplier_data.gst_number,
        company_id=supplier_data.company_id,
        created_by=current_user.id
    )
    
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    
    return supplier

@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get suppliers for a company"""
    
    suppliers = db.query(Supplier).filter(
        Supplier.company_id == company_id
    ).offset(skip).limit(limit).all()
    
    return suppliers

@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get a specific supplier"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    return supplier

@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierCreate,
    current_user: User = Depends(require_permission("suppliers.update")),
    db: Session = Depends(get_db)
):
    """Update a supplier"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Update supplier fields
    supplier.name = supplier_data.name
    supplier.email = supplier_data.email
    supplier.phone = supplier_data.phone
    supplier.address = supplier_data.address
    supplier.gst_number = supplier_data.gst_number
    supplier.updated_by = current_user.id
    
    db.commit()
    db.refresh(supplier)
    
    return supplier

@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.delete")),
    db: Session = Depends(get_db)
):
    """Delete a supplier"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Soft delete
    supplier.is_active = False
    supplier.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Supplier deleted successfully"}