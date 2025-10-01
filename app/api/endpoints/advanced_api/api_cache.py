# backend/app/api/endpoints/api_cache.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.advanced_api.advanced_api_models import APICache
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class APICacheResponse(BaseModel):
    id: int
    cache_key: str
    cache_data: str
    cache_type: str
    expires_at: datetime
    hit_count: int
    miss_count: int

    class Config:
        from_attributes = True

@router.get("/cache", response_model=List[APICacheResponse])
async def get_api_cache(
    company_id: int,
    cache_type: Optional[str] = None,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API cache for a company"""
    
    query = db.query(APICache).filter(APICache.company_id == company_id)
    
    if cache_type:
        query = query.filter(APICache.cache_type == cache_type)
    
    cache_data = query.all()
    return cache_data

@router.get("/cache/{cache_key}")
async def get_api_cache_by_key(
    cache_key: str,
    current_user: User = Depends(require_permission("api.view")),
    db: Session = Depends(get_db)
):
    """Get API cache by key"""
    
    cache = db.query(APICache).filter(APICache.cache_key == cache_key).first()
    if not cache:
        raise HTTPException(status_code=404, detail="Cache not found")
    
    # Check if cache has expired
    if cache.expires_at < datetime.utcnow():
        # Delete expired cache
        db.delete(cache)
        db.commit()
        raise HTTPException(status_code=404, detail="Cache expired")
    
    # Update hit count
    cache.hit_count += 1
    db.commit()
    
    return {
        "cache_key": cache.cache_key,
        "cache_data": cache.cache_data,
        "cache_type": cache.cache_type,
        "expires_at": cache.expires_at,
        "hit_count": cache.hit_count
    }

@router.post("/cache")
async def create_api_cache(
    cache_key: str,
    cache_data: str,
    cache_type: str,
    expires_in_minutes: int = 60,
    company_id: int = 1,
    current_user: User = Depends(require_permission("api.create")),
    db: Session = Depends(get_db)
):
    """Create a new API cache"""
    
    # Check if cache already exists
    existing_cache = db.query(APICache).filter(APICache.cache_key == cache_key).first()
    if existing_cache:
        # Update existing cache
        existing_cache.cache_data = cache_data
        existing_cache.cache_type = cache_type
        existing_cache.expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        existing_cache.updated_by = current_user.id
        db.commit()
        return {"message": "Cache updated successfully"}
    
    # Create new cache
    api_cache = APICache(
        cache_key=cache_key,
        cache_data=cache_data,
        cache_type=cache_type,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        company_id=company_id,
        created_by=current_user.id
    )
    
    db.add(api_cache)
    db.commit()
    db.refresh(api_cache)
    
    return {"message": "Cache created successfully", "cache_id": api_cache.id}

@router.delete("/cache/{cache_key}")
async def delete_api_cache(
    cache_key: str,
    current_user: User = Depends(require_permission("api.delete")),
    db: Session = Depends(get_db)
):
    """Delete API cache"""
    
    cache = db.query(APICache).filter(APICache.cache_key == cache_key).first()
    if not cache:
        raise HTTPException(status_code=404, detail="Cache not found")
    
    db.delete(cache)
    db.commit()
    
    return {"message": "Cache deleted successfully"}