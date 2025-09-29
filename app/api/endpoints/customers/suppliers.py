# backend/app/api/endpoints/suppliers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from decimal import Decimal
from datetime import datetime

from ...database import get_db
from ...models.customer import Supplier, SupplierGroup
from ...models.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class SupplierResponse(BaseModel):
    id: int
    supplier_code: str
    name: str
    display_name: Optional[str] = None
    supplier_type: str
    contact_person: Optional[str] = None
    mobile: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    business_license: Optional[str] = None
    credit_days: int = 0
    payment_terms: Optional[str] = None
    current_balance: Decimal = 0
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None
    status: str = "active"
    rating: Optional[int] = None
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    total_purchase_amount: Decimal = 0
    total_orders: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SupplierCreateRequest(BaseModel):
    name: str
    display_name: Optional[str] = None
    supplier_type: str = "vendor"
    contact_person: Optional[str] = None
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
    business_license: Optional[str] = None
    credit_days: int = 0
    payment_terms: Optional[str] = None
    opening_balance: Decimal = 0
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None
    rating: Optional[int] = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Supplier name cannot be empty')
        return v.strip()

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v

    @validator('gst_number')
    def validate_gst(cls, v):
        if v and len(v.strip()) > 0:
            gst = v.strip().upper()
            if len(gst) != 15:
                raise ValueError('GST number must be 15 characters')
            return gst
        return v

    @validator('ifsc_code')
    def validate_ifsc(cls, v):
        if v and len(v.strip()) > 0:
            ifsc = v.strip().upper()
            if len(ifsc) != 11:
                raise ValueError('IFSC code must be 11 characters')
            return ifsc
        return v

class SupplierUpdateRequest(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    supplier_type: Optional[str] = None
    contact_person: Optional[str] = None
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
    business_license: Optional[str] = None
    credit_days: Optional[int] = None
    payment_terms: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    bank_branch: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = None

class SupplierGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_days: int = 0

    class Config:
        from_attributes = True

class SupplierGroupCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_days: int = 0

# Helper function to generate supplier code
def generate_supplier_code(db: Session, supplier_type: str = "vendor") -> str:
    """Generate unique supplier code"""
    prefix = "S"
    if supplier_type == "manufacturer":
        prefix = "MFG"
    elif supplier_type == "distributor":
        prefix = "DIST"
    
    # Get next number
    last_supplier = db.query(Supplier).filter(
        Supplier.supplier_code.like(f"{prefix}%")
    ).order_by(Supplier.supplier_code.desc()).first()
    
    if last_supplier:
        try:
            last_num = int(last_supplier.supplier_code.replace(prefix, ""))
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}{next_num:06d}"

# Supplier endpoints
@router.get("", response_model=List[SupplierResponse])
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search in name, mobile, or email"),
    supplier_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get suppliers with filtering and pagination"""
    
    query = db.query(Supplier)
    
    # Apply filters
    if search:
        search_filter = or_(
            Supplier.name.ilike(f"%{search}%"),
            Supplier.mobile.ilike(f"%{search}%"),
            Supplier.email.ilike(f"%{search}%"),
            Supplier.supplier_code.ilike(f"%{search}%"),
            Supplier.contact_person.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if supplier_type:
        query = query.filter(Supplier.supplier_type == supplier_type)
    
    if status:
        query = query.filter(Supplier.status == status)
    
    # Get suppliers
    suppliers = query.offset(skip).limit(limit).all()
    
    return [SupplierResponse.from_orm(supplier) for supplier in suppliers]

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get supplier by ID"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return SupplierResponse.from_orm(supplier)

@router.get("/code/{supplier_code}", response_model=SupplierResponse)
async def get_supplier_by_code(
    supplier_code: str,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get supplier by supplier code"""
    
    supplier = db.query(Supplier).filter(Supplier.supplier_code == supplier_code).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return SupplierResponse.from_orm(supplier)

@router.post("", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreateRequest,
    current_user: User = Depends(require_permission("suppliers.create")),
    db: Session = Depends(get_db)
):
    """Create new supplier"""
    
    # Check if email already exists (if provided)
    if supplier_data.email:
        existing_email = db.query(Supplier).filter(Supplier.email == supplier_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier with this email already exists"
            )
    
    # Check if GST number already exists (if provided)
    if supplier_data.gst_number:
        existing_gst = db.query(Supplier).filter(Supplier.gst_number == supplier_data.gst_number).first()
        if existing_gst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier with this GST number already exists"
            )
    
    # Generate supplier code
    supplier_code = generate_supplier_code(db, supplier_data.supplier_type)
    
    # Create supplier
    supplier_dict = supplier_data.dict()
    supplier_dict['supplier_code'] = supplier_code
    supplier_dict['current_balance'] = supplier_dict.pop('opening_balance', 0)
    supplier_dict['created_by'] = current_user.id
    
    db_supplier = Supplier(**supplier_dict)
    
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    
    return SupplierResponse.from_orm(db_supplier)

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdateRequest,
    current_user: User = Depends(require_permission("suppliers.edit")),
    db: Session = Depends(get_db)
):
    """Update supplier"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Check for duplicate email (if being updated)
    if supplier_data.email and supplier_data.email != supplier.email:
        existing_email = db.query(Supplier).filter(
            and_(Supplier.email == supplier_data.email, Supplier.id != supplier_id)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier with this email already exists"
            )
    
    # Check for duplicate GST number (if being updated)
    if supplier_data.gst_number and supplier_data.gst_number != supplier.gst_number:
        existing_gst = db.query(Supplier).filter(
            and_(Supplier.gst_number == supplier_data.gst_number, Supplier.id != supplier_id)
        ).first()
        if existing_gst:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier with this GST number already exists"
            )
    
    # Update supplier fields
    update_data = supplier_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    
    supplier.updated_by = current_user.id
    
    db.commit()
    db.refresh(supplier)
    
    return SupplierResponse.from_orm(supplier)

@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.delete")),
    db: Session = Depends(get_db)
):
    """Delete supplier (soft delete)"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Check if supplier has transactions
    if supplier.total_orders > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete supplier with existing transactions. Set status to inactive instead."
        )
    
    # Check if supplier has outstanding balance
    if supplier.current_balance != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete supplier with outstanding balance."
        )
    
    # Soft delete
    supplier.status = 'inactive'
    supplier.is_active = False
    supplier.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Supplier deleted successfully"}

@router.put("/{supplier_id}/toggle-status")
async def toggle_supplier_status(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.edit")),
    db: Session = Depends(get_db)
):
    """Activate/deactivate supplier"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    supplier.is_active = not supplier.is_active
    supplier.status = 'active' if supplier.is_active else 'inactive'
    supplier.updated_by = current_user.id
    
    db.commit()
    
    return {"message": f"Supplier {'activated' if supplier.is_active else 'deactivated'} successfully"}

@router.put("/{supplier_id}/rating")
async def update_supplier_rating(
    supplier_id: int,
    rating: int = Query(..., ge=1, le=5, description="Rating between 1-5"),
    current_user: User = Depends(require_permission("suppliers.edit")),
    db: Session = Depends(get_db)
):
    """Update supplier rating"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    supplier.rating = rating
    supplier.updated_by = current_user.id
    
    db.commit()
    
    return {"message": f"Supplier rating updated to {rating} stars"}

@router.get("/{supplier_id}/balance-summary")
async def get_supplier_balance_summary(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get supplier balance and transaction summary"""
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return {
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "current_balance": supplier.current_balance,
        "credit_days": supplier.credit_days,
        "payment_terms": supplier.payment_terms,
        "total_purchases": supplier.total_purchase_amount,
        "total_orders": supplier.total_orders,
        "last_transaction_date": supplier.last_purchase_date,
        "rating": supplier.rating
    }

@router.get("/{supplier_id}/items")
async def get_supplier_items(
    supplier_id: int,
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get items preferentially supplied by this supplier"""
    
    from ...models.item import Item
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Get items where this supplier is preferred
    items = db.query(Item).filter(
        and_(Item.preferred_supplier_id == supplier_id, Item.status == 'active')
    ).all()
    
    return {
        "supplier_id": supplier_id,
        "supplier_name": supplier.name,
        "items": [
            {
                "id": item.id,
                "barcode": item.barcode,
                "name": item.name,
                "supplier_item_code": item.supplier_item_code,
                "purchase_rate": item.purchase_rate
            }
            for item in items
        ],
        "total_items": len(items)
    }

# Supplier Groups endpoints
@router.get("/groups", response_model=List[SupplierGroupResponse])
async def get_supplier_groups(
    current_user: User = Depends(require_permission("suppliers.view")),
    db: Session = Depends(get_db)
):
    """Get all supplier groups"""
    
    groups = db.query(SupplierGroup).filter(SupplierGroup.is_active == True).all()
    return [SupplierGroupResponse.from_orm(group) for group in groups]

@router.post("/groups", response_model=SupplierGroupResponse)
async def create_supplier_group(
    group_data: SupplierGroupCreateRequest,
    current_user: User = Depends(require_permission("suppliers.create")),
    db: Session = Depends(get_db)
):
    """Create new supplier group"""
    
    # Check if group name already exists
    existing = db.query(SupplierGroup).filter(SupplierGroup.name == group_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier group with this name already exists"
        )
    
    db_group = SupplierGroup(
        **group_data.dict(),
        created_by=current_user.id
    )
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return SupplierGroupResponse.from_orm(db_group)