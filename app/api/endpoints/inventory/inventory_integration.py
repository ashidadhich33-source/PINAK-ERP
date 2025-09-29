# backend/app/api/endpoints/inventory/inventory_integration.py
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
from ...services.inventory.inventory_integration_service import InventoryIntegrationService

router = APIRouter()

# Initialize service
inventory_integration_service = InventoryIntegrationService()

# Pydantic schemas for Inventory Integration
class StockUpdateResponse(BaseModel):
    success: bool
    sale_order_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    pos_transaction_id: Optional[int] = None
    stock_updates: List[dict]
    message: str

class ItemAvailabilityResponse(BaseModel):
    available: bool
    quantity: Decimal
    reserved: Decimal
    available_quantity: Decimal
    item_name: str
    unit_price: Decimal
    minimum_stock: Decimal
    is_low_stock: bool
    message: Optional[str] = None

class LowStockResponse(BaseModel):
    items: List[dict]
    total_items: int
    critical_items: int
    warning_items: int

class InventoryValuationResponse(BaseModel):
    total_value: Decimal
    total_quantity: Decimal
    items_count: int
    items: List[dict]
    valuation_date: datetime

class ItemSalesHistoryResponse(BaseModel):
    item_id: int
    sales_quantity: Decimal
    sales_amount: Decimal
    pos_quantity: Decimal
    pos_amount: Decimal
    total_quantity: Decimal
    total_amount: Decimal
    period: dict

# Inventory Integration Endpoints
@router.post("/stock/update-sale", response_model=StockUpdateResponse)
async def update_stock_on_sale(
    sale_order_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.stock")),
    db: Session = Depends(get_db)
):
    """Update stock when sale order is created/confirmed"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Update stock
        result = inventory_integration_service.update_stock_on_sale(db, sale_order_id)
        
        return StockUpdateResponse(
            success=result['success'],
            sale_order_id=result['sale_order_id'],
            stock_updates=result['stock_updates'],
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
            detail=f"Failed to update stock on sale: {str(e)}"
        )

@router.post("/stock/update-purchase", response_model=StockUpdateResponse)
async def update_stock_on_purchase(
    purchase_order_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.stock")),
    db: Session = Depends(get_db)
):
    """Update stock when purchase order is received"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Update stock
        result = inventory_integration_service.update_stock_on_purchase(db, purchase_order_id)
        
        return StockUpdateResponse(
            success=result['success'],
            purchase_order_id=result['purchase_order_id'],
            stock_updates=result['stock_updates'],
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
            detail=f"Failed to update stock on purchase: {str(e)}"
        )

@router.post("/stock/update-pos", response_model=StockUpdateResponse)
async def update_stock_on_pos_transaction(
    pos_transaction_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.stock")),
    db: Session = Depends(get_db)
):
    """Update stock when POS transaction is completed"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Update stock
        result = inventory_integration_service.update_stock_on_pos_transaction(db, pos_transaction_id)
        
        return StockUpdateResponse(
            success=result['success'],
            pos_transaction_id=result['pos_transaction_id'],
            stock_updates=result['stock_updates'],
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
            detail=f"Failed to update stock on POS transaction: {str(e)}"
        )

@router.get("/availability/{item_id}", response_model=ItemAvailabilityResponse)
async def get_item_availability(
    item_id: int,
    location_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get item availability for sales/POS"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get item availability
        availability = inventory_integration_service.get_item_availability(db, item_id, location_id)
        
        return ItemAvailabilityResponse(
            available=availability['available'],
            quantity=availability['quantity'],
            reserved=availability['reserved'],
            available_quantity=availability['available_quantity'],
            item_name=availability['item_name'],
            unit_price=availability['unit_price'],
            minimum_stock=availability['minimum_stock'],
            is_low_stock=availability['is_low_stock'],
            message=availability.get('message')
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get item availability: {str(e)}"
        )

@router.get("/low-stock", response_model=LowStockResponse)
async def get_low_stock_items(
    company_id: int = Query(...),
    location_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get low stock items for alerts"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get low stock items
        low_stock_items = inventory_integration_service.get_low_stock_items(db, company_id, location_id)
        
        critical_items = len([item for item in low_stock_items if item.get('is_critical', False)])
        warning_items = len(low_stock_items) - critical_items
        
        return LowStockResponse(
            items=low_stock_items,
            total_items=len(low_stock_items),
            critical_items=critical_items,
            warning_items=warning_items
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get low stock items: {str(e)}"
        )

@router.post("/cost/update-purchase")
async def update_item_cost_from_purchase(
    purchase_bill_id: int = Query(...),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.cost")),
    db: Session = Depends(get_db)
):
    """Update item cost from purchase bill"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Update item cost
        result = inventory_integration_service.update_item_cost_from_purchase(db, purchase_bill_id)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update item cost: {str(e)}"
        )

@router.get("/valuation", response_model=InventoryValuationResponse)
async def get_inventory_valuation(
    company_id: int = Query(...),
    location_id: Optional[int] = Query(None),
    current_user: User = Depends(require_permission("inventory.valuation")),
    db: Session = Depends(get_db)
):
    """Get inventory valuation for accounting"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get inventory valuation
        valuation = inventory_integration_service.get_inventory_valuation(db, company_id, location_id)
        
        return InventoryValuationResponse(
            total_value=valuation['total_value'],
            total_quantity=valuation['total_quantity'],
            items_count=valuation['items_count'],
            items=valuation['items'],
            valuation_date=valuation['valuation_date']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory valuation: {str(e)}"
        )

@router.get("/sales-history/{item_id}", response_model=ItemSalesHistoryResponse)
async def get_item_sales_history(
    item_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.analytics")),
    db: Session = Depends(get_db)
):
    """Get item sales history for analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get item sales history
        history = inventory_integration_service.get_item_sales_history(db, item_id, from_date, to_date)
        
        return ItemSalesHistoryResponse(
            item_id=history['item_id'],
            sales_quantity=history['sales_quantity'],
            sales_amount=history['sales_amount'],
            pos_quantity=history['pos_quantity'],
            pos_amount=history['pos_amount'],
            total_quantity=history['total_quantity'],
            total_amount=history['total_amount'],
            period=history['period']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get item sales history: {str(e)}"
        )

@router.get("/purchase-history/{item_id}")
async def get_item_purchase_history(
    item_id: int,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.analytics")),
    db: Session = Depends(get_db)
):
    """Get item purchase history for analytics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get item purchase history
        history = inventory_integration_service.get_item_purchase_history(db, item_id, from_date, to_date)
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get item purchase history: {str(e)}"
        )

@router.post("/adjustment")
async def create_inventory_adjustment(
    adjustment_data: dict,
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.adjustment")),
    db: Session = Depends(get_db)
):
    """Create inventory adjustment entry"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Add company_id to adjustment data
        adjustment_data['company_id'] = company_id
        
        # Create inventory adjustment
        result = inventory_integration_service.create_inventory_adjustment(db, adjustment_data)
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create inventory adjustment: {str(e)}"
        )

@router.get("/integration-status")
async def get_inventory_integration_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("inventory.view")),
    db: Session = Depends(get_db)
):
    """Get inventory integration status with other modules"""
    
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
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        integrations = company_service.get_company_integrations(db, company_id)
        
        return {
            "inventory_integration": {
                "sales_integration": integrations.get('sales', {}).get('status', 'unknown'),
                "purchase_integration": integrations.get('purchase', {}).get('status', 'unknown'),
                "pos_integration": integrations.get('pos', {}).get('status', 'unknown'),
                "accounting_integration": integrations.get('accounting', {}).get('status', 'unknown'),
                "customer_integration": integrations.get('customers', {}).get('status', 'unknown')
            },
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get inventory integration status: {str(e)}"
        )