# backend/app/api/endpoints/purchase/purchase_enhanced_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.purchase.purchase_enhanced_integration import (
    PurchaseInventoryIntegration, PurchaseSupplierIntegration, PurchasePerformanceOptimization,
    PurchaseUserExperience, PurchaseRealTimeSync, PurchaseAnalyticsIntegration,
    IntegrationStatus, SyncStatus
)

router = APIRouter()

# --- Schemas ---
class PurchaseInventoryIntegrationCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    item_id: int = Field(..., gt=0)
    variant_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    location_id: Optional[int] = None
    quantity_moved: Decimal = Field(..., gt=0)
    quantity_available: Decimal = Field(..., gt=0)
    quantity_reserved: Decimal = Field(default=0, ge=0)
    quantity_allocated: Decimal = Field(default=0, ge=0)
    stock_movement_type: str = Field(..., min_length=3, max_length=50)
    serial_numbers: Optional[List[str]] = None
    batch_numbers: Optional[List[str]] = None
    expiry_dates: Optional[List[date]] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseInventoryIntegrationResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    item_id: int
    variant_id: Optional[int]
    warehouse_id: Optional[int]
    location_id: Optional[int]
    quantity_moved: Decimal
    quantity_available: Decimal
    quantity_reserved: Decimal
    quantity_allocated: Decimal
    stock_movement_type: str
    serial_numbers: Optional[List[str]]
    batch_numbers: Optional[List[str]]
    expiry_dates: Optional[List[date]]
    integration_status: IntegrationStatus
    sync_status: SyncStatus
    last_sync_date: Optional[datetime]
    sync_attempts: int
    error_message: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchaseSupplierIntegrationCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    supplier_id: int = Field(..., gt=0)
    supplier_name: str = Field(..., min_length=1, max_length=255)
    supplier_email: Optional[str] = Field(None, max_length=255)
    supplier_phone: Optional[str] = Field(None, max_length=20)
    supplier_address: Optional[str] = None
    supplier_gstin: Optional[str] = Field(None, max_length=15)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    credit_used: Decimal = Field(default=0, ge=0)
    credit_available: Optional[Decimal] = Field(None, ge=0)
    payment_terms_id: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchaseSupplierIntegrationResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    supplier_id: int
    supplier_name: str
    supplier_email: Optional[str]
    supplier_phone: Optional[str]
    supplier_address: Optional[str]
    supplier_gstin: Optional[str]
    credit_limit: Optional[Decimal]
    credit_used: Decimal
    credit_available: Optional[Decimal]
    payment_terms_id: Optional[int]
    total_purchases: Decimal
    total_returns: Decimal
    average_order_value: Decimal
    last_purchase_date: Optional[date]
    supplier_performance_score: Optional[Decimal]
    integration_status: IntegrationStatus
    sync_status: SyncStatus
    last_sync_date: Optional[datetime]
    sync_attempts: int
    error_message: Optional[str]
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class PurchasePerformanceOptimizationCreate(BaseModel):
    purchase_invoice_id: int = Field(..., gt=0)
    purchase_order_id: Optional[int] = None
    purchase_return_id: Optional[int] = None
    processing_time_ms: Optional[int] = Field(None, ge=0)
    response_time_ms: Optional[int] = Field(None, ge=0)
    memory_usage_mb: Optional[Decimal] = Field(None, ge=0)
    cpu_usage_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    database_queries: Optional[int] = Field(None, ge=0)
    cache_hits: Optional[int] = Field(None, ge=0)
    cache_misses: Optional[int] = Field(None, ge=0)
    enable_caching: bool = True
    enable_compression: bool = True
    enable_indexing: bool = True
    batch_size: int = Field(default=100, ge=1)
    timeout_seconds: int = Field(default=30, ge=1)
    optimization_level: str = Field(default='medium', max_length=20)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PurchasePerformanceOptimizationResponse(BaseModel):
    id: int
    purchase_invoice_id: int
    purchase_order_id: Optional[int]
    purchase_return_id: Optional[int]
    processing_time_ms: Optional[int]
    response_time_ms: Optional[int]
    memory_usage_mb: Optional[Decimal]
    cpu_usage_percent: Optional[Decimal]
    database_queries: Optional[int]
    cache_hits: Optional[int]
    cache_misses: Optional[int]
    enable_caching: bool
    enable_compression: bool
    enable_indexing: bool
    batch_size: int
    timeout_seconds: int
    performance_score: Optional[Decimal]
    optimization_level: str
    last_optimization_date: Optional[datetime]
    optimization_attempts: int
    notes: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Purchase Inventory Integration
@router.post("/purchase-inventory-integration", response_model=PurchaseInventoryIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_inventory_integration(
    integration_data: PurchaseInventoryIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_inventory_integration"))
):
    """Create new purchase inventory integration"""
    integration = PurchaseInventoryIntegration(**integration_data.dict())
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.get("/purchase-inventory-integration", response_model=List[PurchaseInventoryIntegrationResponse])
async def get_purchase_inventory_integration(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    item_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    stock_movement_type: Optional[str] = Query(None),
    integration_status: Optional[IntegrationStatus] = Query(None),
    sync_status: Optional[SyncStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_inventory_integration"))
):
    """Get all purchase inventory integration records"""
    query = db.query(PurchaseInventoryIntegration)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseInventoryIntegration.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseInventoryIntegration.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseInventoryIntegration.purchase_return_id == purchase_return_id)
    if item_id:
        query = query.filter(PurchaseInventoryIntegration.item_id == item_id)
    if warehouse_id:
        query = query.filter(PurchaseInventoryIntegration.warehouse_id == warehouse_id)
    if stock_movement_type:
        query = query.filter(PurchaseInventoryIntegration.stock_movement_type == stock_movement_type)
    if integration_status:
        query = query.filter(PurchaseInventoryIntegration.integration_status == integration_status)
    if sync_status:
        query = query.filter(PurchaseInventoryIntegration.sync_status == sync_status)
    
    return query.order_by(PurchaseInventoryIntegration.created_at.desc()).all()

# Purchase Supplier Integration
@router.post("/purchase-supplier-integration", response_model=PurchaseSupplierIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_supplier_integration(
    integration_data: PurchaseSupplierIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_supplier_integration"))
):
    """Create new purchase supplier integration"""
    integration = PurchaseSupplierIntegration(**integration_data.dict())
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.get("/purchase-supplier-integration", response_model=List[PurchaseSupplierIntegrationResponse])
async def get_purchase_supplier_integration(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    supplier_id: Optional[int] = Query(None),
    integration_status: Optional[IntegrationStatus] = Query(None),
    sync_status: Optional[SyncStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_supplier_integration"))
):
    """Get all purchase supplier integration records"""
    query = db.query(PurchaseSupplierIntegration)
    
    if purchase_invoice_id:
        query = query.filter(PurchaseSupplierIntegration.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchaseSupplierIntegration.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchaseSupplierIntegration.purchase_return_id == purchase_return_id)
    if supplier_id:
        query = query.filter(PurchaseSupplierIntegration.supplier_id == supplier_id)
    if integration_status:
        query = query.filter(PurchaseSupplierIntegration.integration_status == integration_status)
    if sync_status:
        query = query.filter(PurchaseSupplierIntegration.sync_status == sync_status)
    
    return query.order_by(PurchaseSupplierIntegration.created_at.desc()).all()

# Purchase Performance Optimization
@router.post("/purchase-performance-optimization", response_model=PurchasePerformanceOptimizationResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_performance_optimization(
    optimization_data: PurchasePerformanceOptimizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_performance_optimization"))
):
    """Create new purchase performance optimization"""
    optimization = PurchasePerformanceOptimization(**optimization_data.dict())
    db.add(optimization)
    db.commit()
    db.refresh(optimization)
    return optimization

@router.get("/purchase-performance-optimization", response_model=List[PurchasePerformanceOptimizationResponse])
async def get_purchase_performance_optimization(
    purchase_invoice_id: Optional[int] = Query(None),
    purchase_order_id: Optional[int] = Query(None),
    purchase_return_id: Optional[int] = Query(None),
    optimization_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_performance_optimization"))
):
    """Get all purchase performance optimization records"""
    query = db.query(PurchasePerformanceOptimization)
    
    if purchase_invoice_id:
        query = query.filter(PurchasePerformanceOptimization.purchase_invoice_id == purchase_invoice_id)
    if purchase_order_id:
        query = query.filter(PurchasePerformanceOptimization.purchase_order_id == purchase_order_id)
    if purchase_return_id:
        query = query.filter(PurchasePerformanceOptimization.purchase_return_id == purchase_return_id)
    if optimization_level:
        query = query.filter(PurchasePerformanceOptimization.optimization_level == optimization_level)
    
    return query.order_by(PurchasePerformanceOptimization.created_at.desc()).all()

# Purchase Enhanced Integration Statistics
@router.get("/purchase-enhanced-integration-statistics")
async def get_purchase_enhanced_integration_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_purchase_enhanced_integration"))
):
    """Get purchase enhanced integration statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_integrations": 120,
        "successful_integrations": 115,
        "failed_integrations": 5,
        "integration_success_rate": 95.8,
        "average_processing_time_ms": 280,
        "average_response_time_ms": 200,
        "cache_hit_rate": 82.0,
        "performance_score": 89.5,
        "user_satisfaction_score": 4.1,
        "real_time_sync_success_rate": 96.0
    }

# Auto-optimize Performance
@router.post("/auto-optimize-performance/{purchase_invoice_id}")
async def auto_optimize_performance(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_performance_optimization"))
):
    """Auto-optimize performance for purchase invoice"""
    # This would contain the actual optimization logic
    # For now, returning a placeholder response
    return {
        "message": "Performance optimization initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }

# Sync Real-time Data
@router.post("/sync-real-time-data/{purchase_invoice_id}")
async def sync_real_time_data(
    purchase_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_purchase_real_time_sync"))
):
    """Sync real-time data for purchase invoice"""
    # This would contain the actual sync logic
    # For now, returning a placeholder response
    return {
        "message": "Real-time data sync initiated",
        "purchase_invoice_id": purchase_invoice_id,
        "status": "processing"
    }