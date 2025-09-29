# backend/app/api/endpoints/purchase/purchase_indian_localization.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.purchase.purchase_gst_integration import (
    PurchaseGST, PurchaseEInvoice, PurchaseEWaybill, PurchaseTDS, PurchaseTCS,
    PurchaseIndianBanking, PurchaseIndianGeography, GSTTaxType, PlaceOfSupplyType
)

router = APIRouter()

# --- Schemas ---
class PurchaseGSTCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    gst_slab_id: int = Field(..., gt=0)
    hsn_sac_code: Optional[str] = None
    place_of_supply: PlaceOfSupplyType
    supplier_state_code: Optional[str] = None
    recipient_state_code: Optional[str] = None
    taxable_amount: Decimal = Field(..., gt=0)
    cgst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    cgst_amount: Decimal = Field(default=0, ge=0)
    sgst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    sgst_amount: Decimal = Field(default=0, ge=0)
    igst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    igst_amount: Decimal = Field(default=0, ge=0)
    cess_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    cess_amount: Decimal = Field(default=0, ge=0)
    total_gst_amount: Decimal = Field(default=0, ge=0)
    reverse_charge_applicable: bool = False
    reverse_charge_amount: Decimal = Field(default=0, ge=0)
    reverse_charge_section: Optional[str] = None
    gst_in_voice: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseGSTResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    gst_slab_id: int
    hsn_sac_code: Optional[str]
    place_of_supply: PlaceOfSupplyType
    supplier_state_code: Optional[str]
    recipient_state_code: Optional[str]
    taxable_amount: Decimal
    cgst_rate: Optional[Decimal]
    cgst_amount: Decimal
    sgst_rate: Optional[Decimal]
    sgst_amount: Decimal
    igst_rate: Optional[Decimal]
    igst_amount: Decimal
    cess_rate: Optional[Decimal]
    cess_amount: Decimal
    total_gst_amount: Decimal
    reverse_charge_applicable: bool
    reverse_charge_amount: Decimal
    reverse_charge_section: Optional[str]
    gst_in_voice: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseEInvoiceCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    e_invoice_id: Optional[int] = None
    irn: Optional[str] = None
    qr_code: Optional[str] = None
    e_invoice_status: str = Field(default='pending', max_length=20)
    ack_no: Optional[str] = None
    ack_date: Optional[datetime] = None
    portal_upload_status: str = Field(default='pending', max_length=20)
    portal_upload_date: Optional[datetime] = None
    portal_response: Optional[Dict[str, Any]] = None
    generation_attempts: int = Field(default=0, ge=0)
    last_generation_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseEInvoiceResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    e_invoice_id: Optional[int]
    irn: Optional[str]
    qr_code: Optional[str]
    e_invoice_status: str
    ack_no: Optional[str]
    ack_date: Optional[datetime]
    portal_upload_status: str
    portal_upload_date: Optional[datetime]
    portal_response: Optional[Dict[str, Any]]
    generation_attempts: int
    last_generation_attempt: Optional[datetime]
    error_message: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseEWaybillCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    e_waybill_id: Optional[int] = None
    eway_bill_no: Optional[str] = None
    eway_bill_date: Optional[date] = None
    eway_bill_valid_upto: Optional[datetime] = None
    eway_bill_status: str = Field(default='pending', max_length=20)
    transport_mode: Optional[str] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_license: Optional[str] = None
    distance_km: Optional[Decimal] = None
    route_description: Optional[str] = None
    portal_upload_status: str = Field(default='pending', max_length=20)
    portal_upload_date: Optional[datetime] = None
    portal_response: Optional[Dict[str, Any]] = None
    generation_attempts: int = Field(default=0, ge=0)
    last_generation_attempt: Optional[datetime] = None
    error_message: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseEWaybillResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    e_waybill_id: Optional[int]
    eway_bill_no: Optional[str]
    eway_bill_date: Optional[date]
    eway_bill_valid_upto: Optional[datetime]
    eway_bill_status: str
    transport_mode: Optional[str]
    vehicle_number: Optional[str]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    driver_license: Optional[str]
    distance_km: Optional[Decimal]
    route_description: Optional[str]
    portal_upload_status: str
    portal_upload_date: Optional[datetime]
    portal_response: Optional[Dict[str, Any]]
    generation_attempts: int
    last_generation_attempt: Optional[datetime]
    error_message: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Purchase GST
@router.post("/purchase-gst", response_model=PurchaseGSTResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_gst(
    gst_data: PurchaseGSTCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_gst"))
):
    """Create new purchase GST record"""
    gst = PurchaseGST(**gst_data.dict())
    db.add(gst)
    db.commit()
    db.refresh(gst)
    return gst

@router.get("/purchase-gst", response_model=List[PurchaseGSTResponse])
async def get_purchase_gst(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    place_of_supply: Optional[PlaceOfSupplyType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_gst"))
):
    """Get all purchase GST records"""
    query = db.query(PurchaseGST)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseGST.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseGST.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseGST.purchase_return_id == purchase_return_id)
    if place_of_supply:
        query = query.filter(PurchaseGST.place_of_supply == place_of_supply)
    
    return query.order_by(PurchaseGST.created_at.desc()).all()

@router.get("/purchase-gst/{gst_id}", response_model=PurchaseGSTResponse)
async def get_purchase_gst_record(
    gst_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_gst"))
):
    """Get specific purchase GST record"""
    gst = db.query(PurchaseGST).filter(PurchaseGST.id == gst_id).first()
    if not gst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase GST record not found")
    return gst

# Purchase E-Invoice
@router.post("/purchase-e-invoice", response_model=PurchaseEInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_e_invoice(
    e_invoice_data: PurchaseEInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_e_invoice"))
):
    """Create new purchase E-invoice record"""
    e_invoice = PurchaseEInvoice(**e_invoice_data.dict())
    db.add(e_invoice)
    db.commit()
    db.refresh(e_invoice)
    return e_invoice

@router.get("/purchase-e-invoice", response_model=List[PurchaseEInvoiceResponse])
async def get_purchase_e_invoice(
    purchase_invoice_id: Optional[int] = Query(None),
    e_invoice_status: Optional[str] = Query(None),
    portal_upload_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_e_invoice"))
):
    """Get all purchase E-invoice records"""
    query = db.query(PurchaseEInvoice)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseEInvoice.purchase_invoice_id == purchase_invoice_id)
    if e_invoice_status:
        query = query.filter(PurchaseEInvoice.e_invoice_status == e_invoice_status)
    if portal_upload_status:
        query = query.filter(PurchaseEInvoice.portal_upload_status == portal_upload_status)
    
    return query.order_by(PurchaseEInvoice.created_at.desc()).all()

@router.post("/purchase-e-invoice/generate/{purchase_invoice_id}")
async def generate_purchase_e_invoice(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_e_invoice"))
):
    """Generate E-invoice for purchase invoice"""
    # This would contain the actual E-invoice generation logic
    # For now, returning a placeholder response
    return {
        "message": "E-invoice generation initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }

# Purchase E-Waybill
@router.post("/purchase-e-waybill", response_model=PurchaseEWaybillResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_e_waybill(
    e_waybill_data: PurchaseEWaybillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_e_waybill"))
):
    """Create new purchase E-waybill record"""
    e_waybill = PurchaseEWaybill(**e_waybill_data.dict())
    db.add(e_waybill)
    db.commit()
    db.refresh(e_waybill)
    return e_waybill

@router.get("/purchase-e-waybill", response_model=List[PurchaseEWaybillResponse])
async def get_purchase_e_waybill(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    eway_bill_status: Optional[str] = Query(None),
    transport_mode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_e_waybill"))
):
    """Get all purchase E-waybill records"""
    query = db.query(PurchaseEWaybill)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseEWaybill.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseEWaybill.purchase_order_id == purchase_order_id)
    if eway_bill_status:
        query = query.filter(PurchaseEWaybill.eway_bill_status == eway_bill_status)
    if transport_mode:
        query = query.filter(PurchaseEWaybill.transport_mode == transport_mode)
    
    return query.order_by(PurchaseEWaybill.created_at.desc()).all()

@router.post("/purchase-e-waybill/generate/{purchase_invoice_id}")
async def generate_purchase_e_waybill(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_e_waybill"))
):
    """Generate E-waybill for purchase invoice"""
    # This would contain the actual E-waybill generation logic
    # For now, returning a placeholder response
    return {
        "message": "E-waybill generation initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }

# Purchase Indian Localization Statistics
@router.get("/purchase-indian-localization-statistics")
async def get_purchase_indian_localization_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_indian_localization"))
):
    """Get purchase Indian localization statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_gst_paid": 12000.00,
        "total_e_invoices_received": 20,
        "total_e_waybills_received": 15,
        "pending_e_invoices": 2,
        "pending_e_waybills": 1,
        "gst_compliance_rate": 98.0,
        "e_invoice_success_rate": 95.0,
        "e_waybill_success_rate": 93.0
    }