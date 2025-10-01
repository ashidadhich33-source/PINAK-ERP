# backend/app/api/endpoints/ai_analytics.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.ai.ai_models import AIAnalytics
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class AIAnalyticsCreate(BaseModel):
    analytics_name: str
    analytics_type: str
    data_source: str
    metrics: Optional[str] = None
    insights: Optional[str] = None
    accuracy: Optional[Decimal] = None
    company_id: int

class AIAnalyticsResponse(BaseModel):
    id: int
    analytics_name: str
    analytics_type: str
    data_source: str
    metrics: Optional[str]
    insights: Optional[str]
    accuracy: Optional[Decimal]
    status: str

    class Config:
        from_attributes = True

@router.post("/analytics", response_model=AIAnalyticsResponse)
async def create_ai_analytics(
    analytics_data: AIAnalyticsCreate,
    current_user: User = Depends(require_permission("ai.create")),
    db: Session = Depends(get_db)
):
    """Create a new AI analytics"""
    
    # Create AI analytics
    ai_analytics = AIAnalytics(
        analytics_name=analytics_data.analytics_name,
        analytics_type=analytics_data.analytics_type,
        data_source=analytics_data.data_source,
        metrics=analytics_data.metrics,
        insights=analytics_data.insights,
        accuracy=analytics_data.accuracy,
        company_id=analytics_data.company_id,
        created_by=current_user.id
    )
    
    db.add(ai_analytics)
    db.commit()
    db.refresh(ai_analytics)
    
    return ai_analytics

@router.get("/analytics", response_model=List[AIAnalyticsResponse])
async def get_ai_analytics(
    company_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get AI analytics for a company"""
    
    analytics = db.query(AIAnalytics).filter(
        AIAnalytics.company_id == company_id
    ).all()
    
    return analytics

@router.get("/analytics/{analytics_id}", response_model=AIAnalyticsResponse)
async def get_ai_analytics_by_id(
    analytics_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get a specific AI analytics"""
    
    analytics = db.query(AIAnalytics).filter(AIAnalytics.id == analytics_id).first()
    if not analytics:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    
    return analytics

@router.get("/predictive-analytics")
async def get_predictive_analytics(
    company_id: int,
    analytics_type: Optional[str] = None,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get predictive analytics"""
    
    query = db.query(AIAnalytics).filter(AIAnalytics.company_id == company_id)
    
    if analytics_type:
        query = query.filter(AIAnalytics.analytics_type == analytics_type)
    
    analytics = query.all()
    
    return {
        "analytics": [
            {
                "id": a.id,
                "name": a.analytics_name,
                "type": a.analytics_type,
                "accuracy": float(a.accuracy) if a.accuracy else None,
                "status": a.status
            }
            for a in analytics
        ]
    }

@router.get("/sales-forecast")
async def get_sales_forecast(
    company_id: int,
    period: str = "30d",
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get sales forecast"""
    
    # This would implement the actual sales forecast logic
    # For now, return a sample response
    return {
        "period": period,
        "forecast": [
            {"date": "2024-01-01", "predicted_sales": 10000.00},
            {"date": "2024-01-02", "predicted_sales": 12000.00},
            {"date": "2024-01-03", "predicted_sales": 15000.00}
        ],
        "confidence": 85.5
    }

@router.get("/inventory-predictions")
async def get_inventory_predictions(
    company_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get inventory predictions"""
    
    # This would implement the actual inventory prediction logic
    # For now, return a sample response
    return {
        "predictions": [
            {"item_id": 1, "item_name": "Product A", "predicted_demand": 100, "confidence": 90.5},
            {"item_id": 2, "item_name": "Product B", "predicted_demand": 50, "confidence": 85.2}
        ]
    }

@router.get("/customer-behavior")
async def get_customer_behavior_analysis(
    company_id: int,
    customer_id: Optional[int] = None,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get customer behavior analysis"""
    
    # This would implement the actual customer behavior analysis logic
    # For now, return a sample response
    return {
        "customer_id": customer_id,
        "behavior_insights": [
            {"insight": "High purchase frequency", "score": 95.5},
            {"insight": "Prefers premium products", "score": 88.2}
        ]
    }