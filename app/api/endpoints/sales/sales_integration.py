# backend/app/api/endpoints/sales/sales_integration.py
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
from ...services.sales.sales_integration_service import SalesIntegrationService

router = APIRouter()

# Initialize service
sales_integration_service = SalesIntegrationService()

# Pydantic schemas for Sales Integration
class SaleOrderCreateRequest(BaseModel):
    company_id: int
    order_number: str
    order_date: date
    customer_id: int
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

class SaleInvoiceCreateRequest(BaseModel):
    company_id: int
    invoice_number: str
    invoice_date: date
    customer_id: int
    sale_order_id: Optional[int] = None
    subtotal: Decimal
    discount_amount: Optional[Decimal] = 0
    tax_amount: Optional[Decimal] = 0
    total_amount: Decimal
    due_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[dict]

class SalePaymentCreateRequest(BaseModel):
    company_id: int
    payment_number: str
    payment_date: date
    sale_invoice_id: int
    amount: Decimal
    payment_method: str
    payment_reference: Optional[str] = None
    notes: Optional[str] = None

class SalesIntegrationResponse(BaseModel):
    success: bool
    sale_order_id: Optional[int] = None
    sale_invoice_id: Optional[int] = None
    payment_id: Optional[int] = None
    order_number: Optional[str] = None
    invoice_number: Optional[str] = None
    payment_number: Optional[str] = None
    integration_results: dict
    message: str

class SalesAnalyticsResponse(BaseModel):
    total_orders: int
    total_invoices: int
    total_sales_amount: Decimal
    total_invoice_amount: Decimal
    average_order_value: Decimal
    customer_analytics: dict
    product_analytics: dict
    period: dict

# Sales Integration Endpoints
@router.post("/orders", response_model=SalesIntegrationResponse)
async def create_sale_order_with_integrations(
    order_data: SaleOrderCreateRequest,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create sale order with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, order_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create sale order with integrations
        result = sales_integration_service.create_sale_order_with_integrations(
            db, order_data.dict()
        )
        
        return SalesIntegrationResponse(
            success=result['success'],
            sale_order_id=result['sale_order_id'],
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
            detail=f"Failed to create sale order: {str(e)}"
        )

@router.post("/invoices", response_model=SalesIntegrationResponse)
async def create_sale_invoice_with_integrations(
    invoice_data: SaleInvoiceCreateRequest,
    current_user: User = Depends(require_permission("sales.create")),
    db: Session = Depends(get_db)
):
    """Create sale invoice with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, invoice_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Create sale invoice with integrations
        result = sales_integration_service.create_sale_invoice_with_integrations(
            db, invoice_data.dict()
        )
        
        return SalesIntegrationResponse(
            success=result['success'],
            sale_invoice_id=result['sale_invoice_id'],
            invoice_number=result['invoice_number'],
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
            detail=f"Failed to create sale invoice: {str(e)}"
        )

@router.post("/payments", response_model=SalesIntegrationResponse)
async def process_sale_payment_with_integrations(
    payment_data: SalePaymentCreateRequest,
    current_user: User = Depends(require_permission("sales.payment")),
    db: Session = Depends(get_db)
):
    """Process sale payment with full module integrations"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, payment_data.company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Process sale payment with integrations
        result = sales_integration_service.process_sale_payment_with_integrations(
            db, payment_data.dict()
        )
        
        return SalesIntegrationResponse(
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
            detail=f"Failed to process sale payment: {str(e)}"
        )

@router.get("/analytics", response_model=SalesAnalyticsResponse)
async def get_sales_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive sales analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get sales analytics
        analytics = sales_integration_service.get_sales_analytics(db, company_id, from_date, to_date)
        
        return SalesAnalyticsResponse(
            total_orders=analytics['total_orders'],
            total_invoices=analytics['total_invoices'],
            total_sales_amount=analytics['total_sales_amount'],
            total_invoice_amount=analytics['total_invoice_amount'],
            average_order_value=analytics['average_order_value'],
            customer_analytics=analytics['customer_analytics'],
            product_analytics=analytics['product_analytics'],
            period=analytics['period']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales analytics: {str(e)}"
        )

@router.get("/customer-analytics")
async def get_customer_sales_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.analytics")),
    db: Session = Depends(get_db)
):
    """Get customer sales analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get customer sales analytics
        analytics = sales_integration_service.get_customer_sales_analytics(db, company_id, from_date, to_date)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get customer sales analytics: {str(e)}"
        )

@router.get("/product-analytics")
async def get_product_sales_analytics(
    company_id: int = Query(...),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    current_user: User = Depends(require_permission("sales.analytics")),
    db: Session = Depends(get_db)
):
    """Get product sales analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get product sales analytics
        analytics = sales_integration_service.get_product_sales_analytics(db, company_id, from_date, to_date)
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get product sales analytics: {str(e)}"
        )

@router.get("/integration-status")
async def get_sales_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.view")),
    db: Session = Depends(get_db)
):
    """Get sales integration status with other modules"""
    
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
            "sales_integration": {
                "customer_integration": integrations.get('customers', {}).get('status', 'unknown'),
                "inventory_integration": integrations.get('inventory', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "discount_integration": integrations.get('discounts', {}).get('status', 'unknown'),
                "loyalty_integration": integrations.get('loyalty', {}).get('status', 'unknown')
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales integration status: {str(e)}"
        )

@router.get("/workflow-automation")
async def get_sales_workflow_automation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("sales.automation")),
    db: Session = Depends(get_db)
):
    """Get sales workflow automation status"""
    
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
            "sales_workflow_automation": {
                "order_to_invoice": "enabled",
                "invoice_to_payment": "enabled",
                "customer_analytics": "enabled",
                "loyalty_points": "enabled",
                "discount_application": "enabled",
                "stock_updates": "enabled",
                "accounting_entries": "enabled"
            },
            "automation_rules": [
                "Auto-create journal entries for sales",
                "Auto-update customer analytics",
                "Auto-apply customer discounts",
                "Auto-earn loyalty points",
                "Auto-update stock levels",
                "Auto-send notifications"
            ],
            "last_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sales workflow automation: {str(e)}"
        )