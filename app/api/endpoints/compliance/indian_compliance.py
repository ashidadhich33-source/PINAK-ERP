# backend/app/api/endpoints/compliance/indian_compliance.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from ....database import get_db
from ....models.core import User
from ....models.compliance.indian_compliance import (
    GSTRegistration, GSTReturn, GSTPayment, GSTFiling,
    TDSReturn, TDSPayment, TDSFiling,
    TCSReturn, TCSPayment, TCSFiling,
    EInvoice, EWaybill, EInvoiceItem, EWaybillItem,
    ComplianceSettings, ComplianceLog, ComplianceAlert
)
from ....core.security import get_current_user, require_permission
from ....schemas.compliance_schema import (
    GSTRegistrationCreate, GSTRegistrationResponse,
    GSTReturnCreate, GSTReturnResponse,
    GSTPaymentCreate, GSTPaymentResponse,
    TDSReturnCreate, TDSReturnResponse,
    TCSReturnCreate, TCSReturnResponse,
    EInvoiceCreate, EInvoiceResponse,
    EWaybillCreate, EWaybillResponse,
    ComplianceSettingsCreate, ComplianceSettingsResponse,
    ComplianceAlertResponse, ComplianceLogResponse,
    ComplianceDashboardResponse
)

router = APIRouter()

# GST Registration Endpoints
@router.post("/gst/registrations", response_model=GSTRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_registration(
    registration_data: GSTRegistrationCreate,
    current_user: User = Depends(require_permission("compliance.gst.create")),
    db: Session = Depends(get_db)
):
    """Create GST registration"""
    
    # Check if GST number already exists
    existing_gst = db.query(GSTRegistration).filter(
        GSTRegistration.gst_number == registration_data.gst_number
    ).first()
    if existing_gst:
        raise HTTPException(
            status_code=400,
            detail="GST number already exists"
        )
    
    # Create GST registration
    gst_registration = GSTRegistration(
        company_id=current_user.company_id,
        **registration_data.dict()
    )
    
    db.add(gst_registration)
    db.commit()
    db.refresh(gst_registration)
    
    return gst_registration

@router.get("/gst/registrations", response_model=List[GSTRegistrationResponse])
async def get_gst_registrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_permission("compliance.gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST registrations"""
    
    query = db.query(GSTRegistration).filter(
        GSTRegistration.company_id == current_user.company_id
    )
    
    if is_active is not None:
        query = query.filter(GSTRegistration.is_active == is_active)
    
    registrations = query.offset(skip).limit(limit).all()
    return registrations

@router.get("/gst/registrations/{registration_id}", response_model=GSTRegistrationResponse)
async def get_gst_registration(
    registration_id: int,
    current_user: User = Depends(require_permission("compliance.gst.view")),
    db: Session = Depends(get_db)
):
    """Get specific GST registration"""
    
    registration = db.query(GSTRegistration).filter(
        GSTRegistration.id == registration_id,
        GSTRegistration.company_id == current_user.company_id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=404,
            detail="GST registration not found"
        )
    
    return registration

# GST Return Endpoints
@router.post("/gst/returns", response_model=GSTReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_return(
    return_data: GSTReturnCreate,
    current_user: User = Depends(require_permission("compliance.gst.create")),
    db: Session = Depends(get_db)
):
    """Create GST return"""
    
    # Check if GST registration exists
    gst_registration = db.query(GSTRegistration).filter(
        GSTRegistration.id == return_data.gst_registration_id,
        GSTRegistration.company_id == current_user.company_id
    ).first()
    
    if not gst_registration:
        raise HTTPException(
            status_code=404,
            detail="GST registration not found"
        )
    
    # Create GST return
    gst_return = GSTReturn(
        company_id=current_user.company_id,
        **return_data.dict()
    )
    
    db.add(gst_return)
    db.commit()
    db.refresh(gst_return)
    
    return gst_return

@router.get("/gst/returns", response_model=List[GSTReturnResponse])
async def get_gst_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    return_period: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST returns"""
    
    query = db.query(GSTReturn).filter(
        GSTReturn.company_id == current_user.company_id
    )
    
    if return_period:
        query = query.filter(GSTReturn.return_period == return_period)
    if return_type:
        query = query.filter(GSTReturn.return_type == return_type)
    if status:
        query = query.filter(GSTReturn.status == status)
    
    returns = query.offset(skip).limit(limit).all()
    return returns

@router.get("/gst/returns/{return_id}", response_model=GSTReturnResponse)
async def get_gst_return(
    return_id: int,
    current_user: User = Depends(require_permission("compliance.gst.view")),
    db: Session = Depends(get_db)
):
    """Get specific GST return"""
    
    gst_return = db.query(GSTReturn).filter(
        GSTReturn.id == return_id,
        GSTReturn.company_id == current_user.company_id
    ).first()
    
    if not gst_return:
        raise HTTPException(
            status_code=404,
            detail="GST return not found"
        )
    
    return gst_return

# GST Payment Endpoints
@router.post("/gst/payments", response_model=GSTPaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_payment(
    payment_data: GSTPaymentCreate,
    current_user: User = Depends(require_permission("compliance.gst.create")),
    db: Session = Depends(get_db)
):
    """Create GST payment"""
    
    # Check if GST registration exists
    gst_registration = db.query(GSTRegistration).filter(
        GSTRegistration.id == payment_data.gst_registration_id,
        GSTRegistration.company_id == current_user.company_id
    ).first()
    
    if not gst_registration:
        raise HTTPException(
            status_code=404,
            detail="GST registration not found"
        )
    
    # Create GST payment
    gst_payment = GSTPayment(
        company_id=current_user.company_id,
        **payment_data.dict()
    )
    
    db.add(gst_payment)
    db.commit()
    db.refresh(gst_payment)
    
    return gst_payment

@router.get("/gst/payments", response_model=List[GSTPaymentResponse])
async def get_gst_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    gst_registration_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.gst.view")),
    db: Session = Depends(get_db)
):
    """Get GST payments"""
    
    query = db.query(GSTPayment).filter(
        GSTPayment.company_id == current_user.company_id
    )
    
    if gst_registration_id:
        query = query.filter(GSTPayment.gst_registration_id == gst_registration_id)
    if status:
        query = query.filter(GSTPayment.status == status)
    
    payments = query.offset(skip).limit(limit).all()
    return payments

# TDS Return Endpoints
@router.post("/tds/returns", response_model=TDSReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_return(
    return_data: TDSReturnCreate,
    current_user: User = Depends(require_permission("compliance.tds.create")),
    db: Session = Depends(get_db)
):
    """Create TDS return"""
    
    # Create TDS return
    tds_return = TDSReturn(
        company_id=current_user.company_id,
        **return_data.dict()
    )
    
    db.add(tds_return)
    db.commit()
    db.refresh(tds_return)
    
    return tds_return

@router.get("/tds/returns", response_model=List[TDSReturnResponse])
async def get_tds_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    return_period: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.tds.view")),
    db: Session = Depends(get_db)
):
    """Get TDS returns"""
    
    query = db.query(TDSReturn).filter(
        TDSReturn.company_id == current_user.company_id
    )
    
    if return_period:
        query = query.filter(TDSReturn.return_period == return_period)
    if return_type:
        query = query.filter(TDSReturn.return_type == return_type)
    if status:
        query = query.filter(TDSReturn.status == status)
    
    returns = query.offset(skip).limit(limit).all()
    return returns

# TCS Return Endpoints
@router.post("/tcs/returns", response_model=TCSReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_tcs_return(
    return_data: TCSReturnCreate,
    current_user: User = Depends(require_permission("compliance.tcs.create")),
    db: Session = Depends(get_db)
):
    """Create TCS return"""
    
    # Create TCS return
    tcs_return = TCSReturn(
        company_id=current_user.company_id,
        **return_data.dict()
    )
    
    db.add(tcs_return)
    db.commit()
    db.refresh(tcs_return)
    
    return tcs_return

@router.get("/tcs/returns", response_model=List[TCSReturnResponse])
async def get_tcs_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    return_period: Optional[str] = Query(None),
    return_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.tcs.view")),
    db: Session = Depends(get_db)
):
    """Get TCS returns"""
    
    query = db.query(TCSReturn).filter(
        TCSReturn.company_id == current_user.company_id
    )
    
    if return_period:
        query = query.filter(TCSReturn.return_period == return_period)
    if return_type:
        query = query.filter(TCSReturn.return_type == return_type)
    if status:
        query = query.filter(TCSReturn.status == status)
    
    returns = query.offset(skip).limit(limit).all()
    return returns

# E-Invoice Endpoints
@router.post("/e-invoices", response_model=EInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_e_invoice(
    invoice_data: EInvoiceCreate,
    current_user: User = Depends(require_permission("compliance.e_invoice.create")),
    db: Session = Depends(get_db)
):
    """Create E-Invoice"""
    
    # Create E-Invoice
    e_invoice = EInvoice(
        company_id=current_user.company_id,
        **invoice_data.dict()
    )
    
    db.add(e_invoice)
    db.flush()  # Get the ID
    
    # Create E-Invoice items
    for item_data in invoice_data.items:
        e_invoice_item = EInvoiceItem(
            e_invoice_id=e_invoice.id,
            **item_data.dict()
        )
        db.add(e_invoice_item)
    
    db.commit()
    db.refresh(e_invoice)
    
    return e_invoice

@router.get("/e-invoices", response_model=List[EInvoiceResponse])
async def get_e_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.e_invoice.view")),
    db: Session = Depends(get_db)
):
    """Get E-Invoices"""
    
    query = db.query(EInvoice).filter(
        EInvoice.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(EInvoice.status == status)
    
    invoices = query.offset(skip).limit(limit).all()
    return invoices

# E-Waybill Endpoints
@router.post("/e-waybills", response_model=EWaybillResponse, status_code=status.HTTP_201_CREATED)
async def create_e_waybill(
    waybill_data: EWaybillCreate,
    current_user: User = Depends(require_permission("compliance.e_waybill.create")),
    db: Session = Depends(get_db)
):
    """Create E-Waybill"""
    
    # Create E-Waybill
    e_waybill = EWaybill(
        company_id=current_user.company_id,
        **waybill_data.dict()
    )
    
    db.add(e_waybill)
    db.flush()  # Get the ID
    
    # Create E-Waybill items
    for item_data in waybill_data.items:
        e_waybill_item = EWaybillItem(
            e_waybill_id=e_waybill.id,
            **item_data.dict()
        )
        db.add(e_waybill_item)
    
    db.commit()
    db.refresh(e_waybill)
    
    return e_waybill

@router.get("/e-waybills", response_model=List[EWaybillResponse])
async def get_e_waybills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.e_waybill.view")),
    db: Session = Depends(get_db)
):
    """Get E-Waybills"""
    
    query = db.query(EWaybill).filter(
        EWaybill.company_id == current_user.company_id
    )
    
    if status:
        query = query.filter(EWaybill.status == status)
    
    waybills = query.offset(skip).limit(limit).all()
    return waybills

# Compliance Settings Endpoints
@router.get("/settings", response_model=ComplianceSettingsResponse)
async def get_compliance_settings(
    current_user: User = Depends(require_permission("compliance.settings.view")),
    db: Session = Depends(get_db)
):
    """Get compliance settings"""
    
    settings = db.query(ComplianceSettings).filter(
        ComplianceSettings.company_id == current_user.company_id
    ).first()
    
    if not settings:
        # Create default settings
        settings = ComplianceSettings(
            company_id=current_user.company_id
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

@router.put("/settings", response_model=ComplianceSettingsResponse)
async def update_compliance_settings(
    settings_data: ComplianceSettingsCreate,
    current_user: User = Depends(require_permission("compliance.settings.update")),
    db: Session = Depends(get_db)
):
    """Update compliance settings"""
    
    settings = db.query(ComplianceSettings).filter(
        ComplianceSettings.company_id == current_user.company_id
    ).first()
    
    if not settings:
        settings = ComplianceSettings(
            company_id=current_user.company_id,
            **settings_data.dict()
        )
        db.add(settings)
    else:
        for field, value in settings_data.dict().items():
            setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings

# Compliance Alerts Endpoints
@router.get("/alerts", response_model=List[ComplianceAlertResponse])
async def get_compliance_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    compliance_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_permission("compliance.alerts.view")),
    db: Session = Depends(get_db)
):
    """Get compliance alerts"""
    
    query = db.query(ComplianceAlert).filter(
        ComplianceAlert.company_id == current_user.company_id
    )
    
    if compliance_type:
        query = query.filter(ComplianceAlert.compliance_type == compliance_type)
    if priority:
        query = query.filter(ComplianceAlert.priority == priority)
    if status:
        query = query.filter(ComplianceAlert.status == status)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts

# Compliance Dashboard
@router.get("/dashboard", response_model=ComplianceDashboardResponse)
async def get_compliance_dashboard(
    current_user: User = Depends(require_permission("compliance.dashboard.view")),
    db: Session = Depends(get_db)
):
    """Get compliance dashboard"""
    
    # This would contain the actual dashboard logic
    # For now, returning placeholder data
    return ComplianceDashboardResponse(
        company_id=current_user.company_id,
        gst_summary={
            "total_returns": 12,
            "pending_returns": 2,
            "total_payments": 8,
            "pending_payments": 1
        },
        tds_summary={
            "total_returns": 6,
            "pending_returns": 1,
            "total_payments": 5,
            "pending_payments": 0
        },
        tcs_summary={
            "total_returns": 3,
            "pending_returns": 0,
            "total_payments": 3,
            "pending_payments": 0
        },
        e_invoice_summary={
            "total_invoices": 150,
            "generated_invoices": 145,
            "pending_invoices": 5
        },
        e_waybill_summary={
            "total_waybills": 120,
            "active_waybills": 115,
            "expired_waybills": 5
        },
        active_alerts=[],
        upcoming_due_dates=[],
        recent_activities=[]
    )