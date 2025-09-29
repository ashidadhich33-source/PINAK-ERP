# backend/app/api/endpoints/sales/sales_indian_localization.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.sales.sales_gst_integration import (
    SaleGST, SaleEInvoice, SaleEWaybill, SaleTDS, SaleTCS,
    SaleIndianBanking, SaleIndianGeography, GSTTaxType, PlaceOfSupplyType
)

router = APIRouter()

# --- Schemas ---
class SaleGSTCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleGSTResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

class SaleEInvoiceCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
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

class SaleEInvoiceResponse(BaseModel):
    id: int
    sale_invoice_id: int
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

class SaleEWaybillCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
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

class SaleEWaybillResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
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

# Sale GST
@router.post("/sale-gst", response_model=SaleGSTResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_gst(
    gst_data: SaleGSTCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_gst"))
):
    """Create new sale GST record"""
    gst = SaleGST(**gst_data.dict())
    db.add(gst)
    db.commit()
    db.refresh(gst)
    return gst

@router.get("/sale-gst", response_model=List[SaleGSTResponse])
async def get_sale_gst(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    place_of_supply: Optional[PlaceOfSupplyType] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_gst"))
):
    """Get all sale GST records"""
    query = db.query(SaleGST)
    
    if sale_invoice_id:
        query = query.filter(SaleGST.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleGST.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleGST.sale_return_id == sale_return_id)
    if place_of_supply:
        query = query.filter(SaleGST.place_of_supply == place_of_supply)
    
    return query.order_by(SaleGST.created_at.desc()).all()

@router.get("/sale-gst/{gst_id}", response_model=SaleGSTResponse)
async def get_sale_gst_record(
    gst_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_gst"))
):
    """Get specific sale GST record"""
    gst = db.query(SaleGST).filter(SaleGST.id == gst_id).first()
    if not gst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale GST record not found")
    return gst

# Sale E-Invoice
@router.post("/sale-e-invoice", response_model=SaleEInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_e_invoice(
    e_invoice_data: SaleEInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_e_invoice"))
):
    """Create new sale E-invoice record"""
    e_invoice = SaleEInvoice(**e_invoice_data.dict())
    db.add(e_invoice)
    db.commit()
    db.refresh(e_invoice)
    return e_invoice

@router.get("/sale-e-invoice", response_model=List[SaleEInvoiceResponse])
async def get_sale_e_invoice(
    sale_invoice_id: Optional[int] = Query(None),
    e_invoice_status: Optional[str] = Query(None),
    portal_upload_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_e_invoice"))
):
    """Get all sale E-invoice records"""
    query = db.query(SaleEInvoice)
    
    if sale_invoice_id:
        query = query.filter(SaleEInvoice.sale_invoice_id == sale_invoice_id)
    if e_invoice_status:
        query = query.filter(SaleEInvoice.e_invoice_status == e_invoice_status)
    if portal_upload_status:
        query = query.filter(SaleEInvoice.portal_upload_status == portal_upload_status)
    
    return query.order_by(SaleEInvoice.created_at.desc()).all()

@router.post("/sale-e-invoice/generate/{sale_invoice_id}")
async def generate_sale_e_invoice(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_e_invoice"))
):
    """Generate E-invoice for sale invoice"""
    # This would contain the actual E-invoice generation logic
    # For now, returning a placeholder response
    return {
        "message": "E-invoice generation initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }

# Sale E-Waybill
@router.post("/sale-e-waybill", response_model=SaleEWaybillResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_e_waybill(
    e_waybill_data: SaleEWaybillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_e_waybill"))
):
    """Create new sale E-waybill record"""
    e_waybill = SaleEWaybill(**e_waybill_data.dict())
    db.add(e_waybill)
    db.commit()
    db.refresh(e_waybill)
    return e_waybill

@router.get("/sale-e-waybill", response_model=List[SaleEWaybillResponse])
async def get_sale_e_waybill(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    eway_bill_status: Optional[str] = Query(None),
    transport_mode: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_e_waybill"))
):
    """Get all sale E-waybill records"""
    query = db.query(SaleEWaybill)
    
    if sale_invoice_id:
        query = query.filter(SaleEWaybill.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleEWaybill.sale_challan_id == sale_challan_id)
    if eway_bill_status:
        query = query.filter(SaleEWaybill.eway_bill_status == eway_bill_status)
    if transport_mode:
        query = query.filter(SaleEWaybill.transport_mode == transport_mode)
    
    return query.order_by(SaleEWaybill.created_at.desc()).all()

@router.post("/sale-e-waybill/generate/{sale_invoice_id}")
async def generate_sale_e_waybill(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_e_waybill"))
):
    """Generate E-waybill for sale invoice"""
    # This would contain the actual E-waybill generation logic
    # For now, returning a placeholder response
    return {
        "message": "E-waybill generation initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }

# Sales Indian Localization Statistics
@router.get("/sales-indian-localization-statistics")
async def get_sales_indian_localization_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_indian_localization"))
):
    """Get sales Indian localization statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_gst_collected": 15000.00,
        "total_e_invoices_generated": 25,
        "total_e_waybills_generated": 20,
        "pending_e_invoices": 3,
        "pending_e_waybills": 2,
        "gst_compliance_rate": 95.0,
        "e_invoice_success_rate": 92.0,
        "e_waybill_success_rate": 90.0
    }