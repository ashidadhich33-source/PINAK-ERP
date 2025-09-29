# backend/app/api/endpoints/sales/sales_enhanced_integration.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.sales.sales_enhanced_integration import (
    SaleInventoryIntegration, SaleCustomerIntegration, SalePerformanceOptimization,
    SaleUserExperience, SaleRealTimeSync, SaleAnalyticsIntegration,
    IntegrationStatus, SyncStatus
)

router = APIRouter()

# --- Schemas ---
class SaleInventoryIntegrationCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SaleInventoryIntegrationResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

class SaleCustomerIntegrationCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
    customer_id: int = Field(..., gt=0)
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_address: Optional[str] = None
    customer_gstin: Optional[str] = Field(None, max_length=15)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    credit_used: Decimal = Field(default=0, ge=0)
    credit_available: Optional[Decimal] = Field(None, ge=0)
    payment_terms_id: Optional[int] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SaleCustomerIntegrationResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
    customer_id: int
    customer_name: str
    customer_email: Optional[str]
    customer_phone: Optional[str]
    customer_address: Optional[str]
    customer_gstin: Optional[str]
    credit_limit: Optional[Decimal]
    credit_used: Decimal
    credit_available: Optional[Decimal]
    payment_terms_id: Optional[int]
    total_sales: Decimal
    total_returns: Decimal
    average_order_value: Decimal
    last_purchase_date: Optional[date]
    customer_lifetime_value: Decimal
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

class SalePerformanceOptimizationCreate(BaseModel):
    sale_invoice_id: int = Field(..., gt=0)
    sale_challan_id: Optional[int] = None
    sale_return_id: Optional[int] = None
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

class SalePerformanceOptimizationResponse(BaseModel):
    id: int
    sale_invoice_id: int
    sale_challan_id: Optional[int]
    sale_return_id: Optional[int]
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

# Sale Inventory Integration
@router.post("/sale-inventory-integration", response_model=SaleInventoryIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_inventory_integration(
    integration_data: SaleInventoryIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_inventory_integration"))
):
    """Create new sale inventory integration"""
    integration = SaleInventoryIntegration(**integration_data.dict())
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.get("/sale-inventory-integration", response_model=List[SaleInventoryIntegrationResponse])
async def get_sale_inventory_integration(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    item_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    stock_movement_type: Optional[str] = Query(None),
    integration_status: Optional[IntegrationStatus] = Query(None),
    sync_status: Optional[SyncStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_inventory_integration"))
):
    """Get all sale inventory integration records"""
    query = db.query(SaleInventoryIntegration)
    
    if sale_invoice_id:
        query = query.filter(SaleInventoryIntegration.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleInventoryIntegration.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleInventoryIntegration.sale_return_id == sale_return_id)
    if item_id:
        query = query.filter(SaleInventoryIntegration.item_id == item_id)
    if warehouse_id:
        query = query.filter(SaleInventoryIntegration.warehouse_id == warehouse_id)
    if stock_movement_type:
        query = query.filter(SaleInventoryIntegration.stock_movement_type == stock_movement_type)
    if integration_status:
        query = query.filter(SaleInventoryIntegration.integration_status == integration_status)
    if sync_status:
        query = query.filter(SaleInventoryIntegration.sync_status == sync_status)
    
    return query.order_by(SaleInventoryIntegration.created_at.desc()).all()

# Sale Customer Integration
@router.post("/sale-customer-integration", response_model=SaleCustomerIntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_customer_integration(
    integration_data: SaleCustomerIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_customer_integration"))
):
    """Create new sale customer integration"""
    integration = SaleCustomerIntegration(**integration_data.dict())
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

@router.get("/sale-customer-integration", response_model=List[SaleCustomerIntegrationResponse])
async def get_sale_customer_integration(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    integration_status: Optional[IntegrationStatus] = Query(None),
    sync_status: Optional[SyncStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_customer_integration"))
):
    """Get all sale customer integration records"""
    query = db.query(SaleCustomerIntegration)
    
    if sale_invoice_id:
        query = query.filter(SaleCustomerIntegration.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SaleCustomerIntegration.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SaleCustomerIntegration.sale_return_id == sale_return_id)
    if customer_id:
        query = query.filter(SaleCustomerIntegration.customer_id == customer_id)
    if integration_status:
        query = query.filter(SaleCustomerIntegration.integration_status == integration_status)
    if sync_status:
        query = query.filter(SaleCustomerIntegration.sync_status == sync_status)
    
    return query.order_by(SaleCustomerIntegration.created_at.desc()).all()

# Sale Performance Optimization
@router.post("/sale-performance-optimization", response_model=SalePerformanceOptimizationResponse, status_code=status.HTTP_201_CREATED)
async def create_sale_performance_optimization(
    optimization_data: SalePerformanceOptimizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_performance_optimization"))
):
    """Create new sale performance optimization"""
    optimization = SalePerformanceOptimization(**optimization_data.dict())
    db.add(optimization)
    db.commit()
    db.refresh(optimization)
    return optimization

@router.get("/sale-performance-optimization", response_model=List[SalePerformanceOptimizationResponse])
async def get_sale_performance_optimization(
    sale_invoice_id: Optional[int] = Query(None),
    sale_challan_id: Optional[int] = Query(None),
    sale_return_id: Optional[int] = Query(None),
    optimization_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_performance_optimization"))
):
    """Get all sale performance optimization records"""
    query = db.query(SalePerformanceOptimization)
    
    if sale_invoice_id:
        query = query.filter(SalePerformanceOptimization.sale_invoice_id == sale_invoice_id)
    if sale_challan_id:
        query = query.filter(SalePerformanceOptimization.sale_challan_id == sale_challan_id)
    if sale_return_id:
        query = query.filter(SalePerformanceOptimization.sale_return_id == sale_return_id)
    if optimization_level:
        query = query.filter(SalePerformanceOptimization.optimization_level == optimization_level)
    
    return query.order_by(SalePerformanceOptimization.created_at.desc()).all()

# Sale Enhanced Integration Statistics
@router.get("/sales-enhanced-integration-statistics")
async def get_sales_enhanced_integration_statistics(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_sales_enhanced_integration"))
):
    """Get sales enhanced integration statistics"""
    # This would contain the actual statistics logic
    # For now, returning placeholder data
    return {
        "total_integrations": 150,
        "successful_integrations": 145,
        "failed_integrations": 5,
        "integration_success_rate": 96.7,
        "average_processing_time_ms": 250,
        "average_response_time_ms": 180,
        "cache_hit_rate": 85.0,
        "performance_score": 92.5,
        "user_satisfaction_score": 4.3,
        "real_time_sync_success_rate": 98.0
    }

# Auto-optimize Performance
@router.post("/auto-optimize-performance/{sale_invoice_id}")
async def auto_optimize_performance(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_performance_optimization"))
):
    """Auto-optimize performance for sale invoice"""
    # This would contain the actual optimization logic
    # For now, returning a placeholder response
    return {
        "message": "Performance optimization initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }

# Sync Real-time Data
@router.post("/sync-real-time-data/{sale_invoice_id}")
async def sync_real_time_data(
    sale_invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("manage_sales_real_time_sync"))
):
    """Sync real-time data for sale invoice"""
    # This would contain the actual sync logic
    # For now, returning a placeholder response
    return {
        "message": "Real-time data sync initiated",
        "sale_invoice_id": sale_invoice_id,
        "status": "processing"
    }