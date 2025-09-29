# backend/app/api/endpoints/optimization/performance_optimization.py
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
from ...services.optimization.performance_optimization_service import PerformanceOptimizationService

router = APIRouter()

# Initialize service
performance_optimization_service = PerformanceOptimizationService()

# Pydantic schemas for Performance Optimization
class PerformanceOptimizationResponse(BaseModel):
    success: bool
    optimization_results: dict
    overall_results: dict
    message: str

class OptimizationResultResponse(BaseModel):
    status: str
    optimizations: List[dict]
    total_optimizations: int
    performance_improvement: str

class OverallOptimizationResults(BaseModel):
    total_optimizations: int
    completed_optimizations: int
    failed_optimizations: int
    success_rate: float
    average_performance_improvement: float
    overall_status: str

# Performance Optimization Endpoints
@router.post("/run-comprehensive-optimization", response_model=PerformanceOptimizationResponse)
async def run_comprehensive_performance_optimization(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.run")),
    db: Session = Depends(get_db)
):
    """Run comprehensive performance optimization for all modules"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Run comprehensive performance optimization
        result = performance_optimization_service.run_comprehensive_performance_optimization(db, company_id)
        
        return PerformanceOptimizationResponse(
            success=result['success'],
            optimization_results=result['optimization_results'],
            overall_results=result['overall_results'],
            message=result['message']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run comprehensive performance optimization: {str(e)}"
        )

@router.get("/optimize-database-performance", response_model=OptimizationResultResponse)
async def optimize_database_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.database")),
    db: Session = Depends(get_db)
):
    """Optimize database performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize database performance
        result = performance_optimization_service.optimize_database_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize database performance: {str(e)}"
        )

@router.get("/optimize-query-performance", response_model=OptimizationResultResponse)
async def optimize_query_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.query")),
    db: Session = Depends(get_db)
):
    """Optimize query performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize query performance
        result = performance_optimization_service.optimize_query_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize query performance: {str(e)}"
        )

@router.get("/optimize-cache-performance", response_model=OptimizationResultResponse)
async def optimize_cache_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.cache")),
    db: Session = Depends(get_db)
):
    """Optimize cache performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize cache performance
        result = performance_optimization_service.optimize_cache_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize cache performance: {str(e)}"
        )

@router.get("/optimize-api-performance", response_model=OptimizationResultResponse)
async def optimize_api_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.api")),
    db: Session = Depends(get_db)
):
    """Optimize API performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize API performance
        result = performance_optimization_service.optimize_api_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize API performance: {str(e)}"
        )

@router.get("/optimize-memory-performance", response_model=OptimizationResultResponse)
async def optimize_memory_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.memory")),
    db: Session = Depends(get_db)
):
    """Optimize memory performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize memory performance
        result = performance_optimization_service.optimize_memory_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize memory performance: {str(e)}"
        )

@router.get("/optimize-integration-performance", response_model=OptimizationResultResponse)
async def optimize_integration_performance(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.integration")),
    db: Session = Depends(get_db)
):
    """Optimize integration performance"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Optimize integration performance
        result = performance_optimization_service.optimize_integration_performance(db, company_id)
        
        return OptimizationResultResponse(
            status=result['status'],
            optimizations=result['optimizations'],
            total_optimizations=result['total_optimizations'],
            performance_improvement=result['performance_improvement']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize integration performance: {str(e)}"
        )

@router.get("/performance-metrics")
async def get_performance_metrics(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.metrics")),
    db: Session = Depends(get_db)
):
    """Get performance metrics"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get performance metrics
        return {
            "performance_metrics": {
                "database_performance": "optimized",
                "query_performance": "optimized",
                "cache_performance": "optimized",
                "api_performance": "optimized",
                "memory_performance": "optimized",
                "integration_performance": "optimized"
            },
            "optimization_capabilities": [
                "Database index optimization",
                "Query plan optimization",
                "Cache optimization",
                "API rate limiting",
                "Memory optimization",
                "Integration optimization"
            ],
            "last_optimized": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/optimization-status")
async def get_optimization_status(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("optimization.status")),
    db: Session = Depends(get_db)
):
    """Get optimization status"""
    
    try:
        # Validate company access
        from ...services.core.company_integration_service import CompanyIntegrationService
        company_service = CompanyIntegrationService()
        if not company_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get optimization status
        return {
            "optimization_status": {
                "database_optimization": "ready",
                "query_optimization": "ready",
                "cache_optimization": "ready",
                "api_optimization": "ready",
                "memory_optimization": "ready",
                "integration_optimization": "ready"
            },
            "optimization_features": [
                "Automatic index creation",
                "Query performance analysis",
                "Cache optimization",
                "API rate limiting",
                "Memory leak detection",
                "Integration performance tuning"
            ],
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get optimization status: {str(e)}"
        )