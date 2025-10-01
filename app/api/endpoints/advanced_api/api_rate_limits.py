# backend/app/api/endpoints/api_rate_limits.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.advanced_api.advanced_api_models import APIRateLimit
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class APIRateLimitResponse(BaseModel):
    id: int
    endpoint: str
    method: str
    rate_limit: int
    current_count: int
    window_start: datetime
    user_id: Optional[int]
    ip_address: Optional[str]

    class Config:
        from_attributes = True

@router.get("/rate-limits", response_model=List[APIRateLimitResponse])
async def get_api_rate_limits(
    company_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API rate limits for a company"""
    
    rate_limits = db.query(APIRateLimit).filter(
        APIRateLimit.company_id == company_id
    ).all()
    
    return rate_limits

@router.get("/rate-limits/{rate_limit_id}", response_model=APIRateLimitResponse)
async def get_api_rate_limit(
    rate_limit_id: int,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get a specific API rate limit"""
    
    rate_limit = db.query(APIRateLimit).filter(APIRateLimit.id == rate_limit_id).first()
    if not rate_limit:
        raise HTTPException(status_code=404, detail="API rate limit not found")
    
    return rate_limit

@router.post("/rate-limits")
async def create_api_rate_limit(
    endpoint: str,
    method: str,
    rate_limit: int,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    company_id: int = 1,
    current_user: User = Depends(require_permission("api.create")),
    db: Session = Depends(get_db)
):
    """Create a new API rate limit"""
    
    # Create API rate limit
    api_rate_limit = APIRateLimit(
        endpoint=endpoint,
        method=method,
        rate_limit=rate_limit,
        user_id=user_id,
        ip_address=ip_address,
        company_id=company_id,
        created_by=current_user.id
    )
    
    db.add(api_rate_limit)
    db.commit()
    db.refresh(api_rate_limit)
    
    return {"message": "API rate limit created successfully", "rate_limit_id": api_rate_limit.id}