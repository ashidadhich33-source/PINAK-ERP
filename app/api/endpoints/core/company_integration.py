# backend/app/api/endpoints/core/company_integration.py
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
from ...services.core.company_integration_service import CompanyIntegrationService

router = APIRouter()

# Initialize service
company_integration_service = CompanyIntegrationService()

# Pydantic schemas for Company Integration
class CompanyDataIsolationResponse(BaseModel):
    company: dict
    permissions: dict
    integrations: dict
    isolation_status: str

class CompanyAnalyticsResponse(BaseModel):
    inventory: dict
    sales: dict
    purchase: dict
    pos: dict
    customers: dict
    accounting: dict

class CompanySyncResponse(BaseModel):
    success: bool
    sync_results: dict
    timestamp: datetime

# Company Integration Endpoints
@router.get("/data-isolation", response_model=CompanyDataIsolationResponse)
async def get_company_data_isolation(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.view")),
    db: Session = Depends(get_db)
):
    """Get company data isolation settings and validate access"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company data isolation
        isolation_data = company_integration_service.get_company_data_isolation(db, company_id)
        
        return CompanyDataIsolationResponse(
            company=isolation_data['company'],
            permissions=isolation_data['permissions'],
            integrations=isolation_data['integrations'],
            isolation_status=isolation_data['isolation_status']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company data isolation: {str(e)}"
        )

@router.get("/analytics", response_model=CompanyAnalyticsResponse)
async def get_company_analytics(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.analytics")),
    db: Session = Depends(get_db)
):
    """Get company-level analytics and insights"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company analytics
        analytics = company_integration_service.get_company_analytics(db, company_id)
        
        return CompanyAnalyticsResponse(
            inventory=analytics.get('inventory', {}),
            sales=analytics.get('sales', {}),
            purchase=analytics.get('purchase', {}),
            pos=analytics.get('pos', {}),
            customers=analytics.get('customers', {}),
            accounting=analytics.get('accounting', {})
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company analytics: {str(e)}"
        )

@router.post("/sync", response_model=CompanySyncResponse)
async def sync_company_data(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.sync")),
    db: Session = Depends(get_db)
):
    """Sync company data across all modules"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Sync company data
        sync_result = company_integration_service.sync_company_data(db, company_id)
        
        return CompanySyncResponse(
            success=sync_result['success'],
            sync_results=sync_result.get('sync_results', {}),
            timestamp=sync_result['timestamp']
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync company data: {str(e)}"
        )

@router.get("/modules")
async def get_company_modules(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.view")),
    db: Session = Depends(get_db)
):
    """Get company-enabled modules"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company modules
        modules = company_integration_service.get_company_modules(db, company_id)
        
        return {
            "modules": modules,
            "total_modules": len(modules),
            "company_id": company_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company modules: {str(e)}"
        )

@router.get("/permissions")
async def get_company_permissions(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.view")),
    db: Session = Depends(get_db)
):
    """Get company-level permissions and access control"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company permissions
        permissions = company_integration_service.get_company_permissions(db, company_id)
        
        return permissions
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company permissions: {str(e)}"
        )

@router.get("/integrations")
async def get_company_integrations(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.view")),
    db: Session = Depends(get_db)
):
    """Get company-level integrations status"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company integrations
        integrations = company_integration_service.get_company_integrations(db, company_id)
        
        return integrations
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company integrations: {str(e)}"
        )

@router.get("/dashboard")
async def get_company_dashboard(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.dashboard")),
    db: Session = Depends(get_db)
):
    """Get company dashboard data"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company data isolation
        isolation_data = company_integration_service.get_company_data_isolation(db, company_id)
        
        # Get company analytics
        analytics = company_integration_service.get_company_analytics(db, company_id)
        
        # Get company integrations
        integrations = company_integration_service.get_company_integrations(db, company_id)
        
        return {
            "company": isolation_data['company'],
            "analytics": analytics,
            "integrations": integrations,
            "permissions": isolation_data['permissions'],
            "dashboard_updated": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company dashboard: {str(e)}"
        )

@router.get("/health")
async def get_company_health(
    company_id: int = Query(...),
    current_user: User = Depends(require_permission("company.view")),
    db: Session = Depends(get_db)
):
    """Get company system health status"""
    
    try:
        # Validate company access
        if not company_integration_service.validate_company_access(db, company_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Access denied to this company"
            )
        
        # Get company integrations
        integrations = company_integration_service.get_company_integrations(db, company_id)
        
        # Calculate health score
        total_modules = len(integrations)
        active_modules = len([m for m in integrations.values() if m.get('status') == 'active'])
        health_score = (active_modules / total_modules * 100) if total_modules > 0 else 0
        
        return {
            "company_id": company_id,
            "health_score": health_score,
            "total_modules": total_modules,
            "active_modules": active_modules,
            "inactive_modules": total_modules - active_modules,
            "status": "healthy" if health_score >= 80 else "warning" if health_score >= 60 else "critical",
            "last_checked": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get company health: {str(e)}"
        )