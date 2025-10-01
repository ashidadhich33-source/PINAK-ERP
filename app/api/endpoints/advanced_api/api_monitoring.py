# backend/app/api/endpoints/api_monitoring.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.advanced_api.advanced_api_models import APIMonitoring
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class APIMonitoringResponse(BaseModel):
    id: int
    endpoint: str
    method: str
    response_time: Decimal
    status_code: int
    request_size: Optional[int]
    response_size: Optional[int]
    user_id: Optional[int]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/monitoring", response_model=List[APIMonitoringResponse])
async def get_api_monitoring(
    company_id: int,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API monitoring data for a company"""
    
    query = db.query(APIMonitoring).filter(APIMonitoring.company_id == company_id)
    
    if endpoint:
        query = query.filter(APIMonitoring.endpoint.like(f"%{endpoint}%"))
    
    if method:
        query = query.filter(APIMonitoring.method == method)
    
    if start_date:
        query = query.filter(APIMonitoring.created_at >= start_date)
    
    if end_date:
        query = query.filter(APIMonitoring.created_at <= end_date)
    
    monitoring_data = query.order_by(APIMonitoring.created_at.desc()).limit(1000).all()
    return monitoring_data

@router.get("/monitoring/stats")
async def get_api_monitoring_stats(
    company_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API monitoring statistics"""
    
    # Get basic stats
    total_requests = db.query(APIMonitoring).filter(
        APIMonitoring.company_id == company_id
    ).count()
    
    avg_response_time = db.query(APIMonitoring).filter(
        APIMonitoring.company_id == company_id
    ).with_entities(APIMonitoring.response_time).all()
    
    if avg_response_time:
        avg_time = sum([float(r[0]) for r in avg_response_time]) / len(avg_response_time)
    else:
        avg_time = 0
    
    # Get status code distribution
    status_codes = db.query(APIMonitoring).filter(
        APIMonitoring.company_id == company_id
    ).with_entities(APIMonitoring.status_code).all()
    
    status_distribution = {}
    for status_code in status_codes:
        code = status_code[0]
        status_distribution[code] = status_distribution.get(code, 0) + 1
    
    return {
        "total_requests": total_requests,
        "average_response_time": round(avg_time, 3),
        "status_code_distribution": status_distribution
    }

@router.get("/monitoring/endpoints")
async def get_api_endpoints(
    company_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API endpoints for a company"""
    
    endpoints = db.query(APIMonitoring).filter(
        APIMonitoring.company_id == company_id
    ).with_entities(APIMonitoring.endpoint, APIMonitoring.method).distinct().all()
    
    return [
        {"endpoint": endpoint, "method": method}
        for endpoint, method in endpoints
    ]