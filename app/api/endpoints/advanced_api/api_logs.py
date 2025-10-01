# backend/app/api/endpoints/api_logs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.advanced_api.advanced_api_models import APILog
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class APILogResponse(BaseModel):
    id: int
    endpoint: str
    method: str
    request_data: Optional[str]
    response_data: Optional[str]
    status_code: int
    error_message: Optional[str]
    execution_time: Decimal
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/logs", response_model=List[APILogResponse])
async def get_api_logs(
    company_id: int,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API logs for a company"""
    
    query = db.query(APILog).filter(APILog.company_id == company_id)
    
    if endpoint:
        query = query.filter(APILog.endpoint.like(f"%{endpoint}%"))
    
    if method:
        query = query.filter(APILog.method == method)
    
    if status_code:
        query = query.filter(APILog.status_code == status_code)
    
    if start_date:
        query = query.filter(APILog.created_at >= start_date)
    
    if end_date:
        query = query.filter(APILog.created_at <= end_date)
    
    logs = query.order_by(APILog.created_at.desc()).limit(1000).all()
    return logs

@router.get("/logs/{log_id}", response_model=APILogResponse)
async def get_api_log(
    log_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get a specific API log"""
    
    log = db.query(APILog).filter(APILog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="API log not found")
    
    return log

@router.get("/logs/errors")
async def get_api_errors(
    company_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API errors for a company"""
    
    errors = db.query(APILog).filter(
        APILog.company_id == company_id,
        APILog.status_code >= 400
    ).order_by(APILog.created_at.desc()).limit(100).all()
    
    return [
        {
            "id": error.id,
            "endpoint": error.endpoint,
            "method": error.method,
            "status_code": error.status_code,
            "error_message": error.error_message,
            "created_at": error.created_at
        }
        for error in errors
    ]