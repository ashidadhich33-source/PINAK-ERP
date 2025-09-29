# backend/app/api/endpoints/purchase/purchase_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, validator
from decimal import Decimal
from datetime import datetime, date
import json

from ...database import get_db
from ...models.company import Company
from ...models.user import User
from ...core.security import get_current_user, require_permission
from ...services.purchase.purchase_integration_service import PurchaseIntegrationService

router = APIRouter()

# Initialize service
purchase_integration_service = PurchaseIntegrationService()

# Pydantic schemas for Purchase Integration
class PurchaseOrderCreateRequest(BaseModel):
    company_id: int
    order_number: str
    order_date: date
    supplier_id: int
    staff_id: Optional[int] = None
    subtotal: Decimal
    discount_amount: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    total_amount: Decimal
    payment_terms: Optional[str] = None
    delivery_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[dict]
    applied_discounts: Optional[List[dict]] = []

class PurchaseBillCreateRequest(BaseModel):
    company_id: int
    bill_number: str
    bill_date: date
    supplier_id: int
    purchase_order_id: Optional[int] = None
    subtotal: Decimal
    discount_amount: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    total_amount: Decimal
    due_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[dict]

class PurchasePaymentCreateRequest(BaseModel):
    company_id: int
    payment_number: str
    payment_date: date
    purchase_bill_id: int
    amount: Decimal
    payment_method: str
    payment_reference: Optional[str] = None
    notes: Optional[str] = None

class PurchaseIntegrationResponse(BaseModel):
    success: bool
    purchase_order_id: Optional[int] = None
    purchase_bill_id: Optional[int] = None
    payment_id: Optional[int] = None
    order_number: Optional[str] = None
    bill_number: Optional[str] = None
    payment_number: Optional[str] = None
    integration_results: dict
    message: str

class PurchaseAnalyticsResponse(BaseModel):
    total_orders: int
    total_bills: int
    total_purchase_amount: Decimal
    total_bill_amount: Decimal
    average_order_value: Decimal
    supplier_analytics: dict
    product_analytics: dict
    period: dict

# Purchase Integration Endpoints
@router.post("/orders", response_model=PurchaseIntegrationResponse)
async def create_purchase_order_with_integrations(
    order_data: PurchaseOrderCreateRequest,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Create purchase order with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, order_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create purchase order with integrations
        result = purchase_integration_service.create_purchase_order_with_integrations(
            db, order_data.dict()
        )
        
        return PurchaseIntegrationResponse(
            success=result['success'],
            purchase_order_id=result['purchase_order_id'],
            order_number=result['order_number'],
            integration_results=result['integration_results'],
            message=result['message']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create purchase order: {str(e)}"
        )

@router.post("/bills", response_model=PurchaseIntegrationResponse)
async def create_purchase_bill_with_integrations(
    bill_data: PurchaseBillCreateRequest,
    current_user: User = Depends(require_permission("purchase.create")),
    db: Session = Depends(get_db)
):
    """Create purchase bill with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, bill_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create purchase bill with integrations
        result = purchase_integration_service.create_purchase_bill_with_integrations(
            db, bill_data.dict()
        )
        
        return PurchaseIntegrationResponse(
            success=result['success'],
            purchase_bill_id=result['purchase_bill_id'],
            bill_number=result['bill_number'],
            integration_results=result['integration_results'],
            message=result['message']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create purchase bill: {str(e)}"
        )

@router.post("/payments", response_model=PurchaseIntegrationResponse)
async def process_purchase_payment_with_integrations(
    payment_data: PurchasePaymentCreateRequest,
    current_user: User = Depends(require_permission("purchase.payment")),
    db: Session = Depends(get_db)
):
    """Process purchase payment with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, payment_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Process purchase payment with integrations
        result = purchase_integration_service.process_purchase_payment_with_integrations(
            db, payment_data.dict()
        )
        
        return PurchaseIntegrationResponse(
            success=result['success'],
            payment_id=result['payment_id'],
            payment_number=result['payment_number'],
            integration_results=result['integration_results'],
            message=result['message']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process purchase payment: {str(e)}"
        )

@router.get("/analytics", response_model=PurchaseAnalyticsResponse)
async def get_purchase_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive purchase analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get purchase analytics
        analytics = purchase_integration_service.get_purchase_analytics(db, company_id, from_date, to_date)
        
        return PurchaseAnalyticsResponse(
            total_orders=analytics['total_orders'],
            total_bills=analytics['total_bills'],
            total_purchase_amount=analytics['total_purchase_amount'],
            total_bill_amount=analytics['total_bill_amount'],
            average_order_value=analytics['average_order_value'],
            supplier_analytics=analytics['supplier_analytics'],
            product_analytics=analytics['product_analytics'],
            period=analytics['period']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get purchase analytics: {str(e)}"
        )

@router.get("/supplier-analytics")
async def get_supplier_purchase_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.analytics")),
    db: Session = Depends(get_db)
):
    """Get supplier purchase analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get supplier purchase analytics
        analytics = purchase_integration_service.get_supplier_purchase_analytics(db, company_id, from_date, to_date)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get supplier purchase analytics: {str(e)}"
        )

@router.get("/product-analytics")
async def get_product_purchase_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("purchase.analytics")),
    db: Session = Depends(get_db)
):
    """Get product purchase analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get product purchase analytics
        analytics = purchase_integration_service.get_product_purchase_analytics(db, company_id, from_date, to_date)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product purchase analytics: {str(e)}"
        )

@router.get("/integration-status")
async def get_purchase_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.view")),
    db: Session = Depends(get_db)
):
    """Get purchase integration status with other modules"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get integration status
        integrations = company_service.get_company_integrations(db, company_id)
        
        return {
            "purchase_integration": {
                "supplier_integration": integrations.get('suppliers', {}).get('status', 'unknown'),
                "inventory_integration": integrations.get('inventory', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "discount_integration": integrations.get('discounts', {}).get('status', 'unknown')
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get purchase integration status: {str(e)}"
        )

@router.get("/workflow-automation")
async def get_purchase_workflow_automation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("purchase.automation")),
    db: Session = Depends(get_db)
):
    """Get purchase workflow automation status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get workflow automation status
        return {
            "purchase_workflow_automation": {
                "order_to_bill": "enabled",
                "bill_to_payment": "enabled",
                "supplier_analytics": "enabled",
                "stock_updates": "enabled",
                "cost_updates": "enabled",
                "accounting_entries": "enabled"
            },
            "automation_rules": [
                "Auto-create journal entries for purchases",
                "Auto-update supplier analytics",
                "Auto-apply supplier discounts",
                "Auto-update stock levels",
                "Auto-update item costs",
                "Auto-send notifications"
            ],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get purchase workflow automation: {str(e)}"
        )