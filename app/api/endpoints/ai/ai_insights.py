# backend/app/api/endpoints/ai_insights.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.ai.ai_models import AIInsight, AIRecommendation
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class AIInsightResponse(BaseModel):
    id: int
    insight_name: str
    insight_type: str
    insight_data: str
    insight_score: Optional[Decimal]
    insight_date: datetime
    status: str

    class Config:
        from_attributes = True

class AIRecommendationResponse(BaseModel):
    id: int
    recommendation_name: str
    recommendation_type: str
    recommendation_data: str
    recommendation_score: Optional[Decimal]
    recommendation_date: datetime
    status: str

    class Config:
        from_attributes = True

@router.get("/insights", response_model=List[AIInsightResponse])
async def get_ai_insights(
    company_id: int,
    insight_type: Optional[str] = None,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get AI insights for a company"""
    
    query = db.query(AIInsight).filter(AIInsight.company_id == company_id)
    
    if insight_type:
        query = query.filter(AIInsight.insight_type == insight_type)
    
    insights = query.all()
    return insights

@router.get("/insights/{insight_id}", response_model=AIInsightResponse)
async def get_ai_insight(
    insight_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get a specific AI insight"""
    
    insight = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="AI insight not found")
    
    return insight

@router.get("/recommendations", response_model=List[AIRecommendationResponse])
async def get_ai_recommendations(
    company_id: int,
    recommendation_type: Optional[str] = None,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get AI recommendations for a company"""
    
    query = db.query(AIRecommendation).filter(AIRecommendation.company_id == company_id)
    
    if recommendation_type:
        query = query.filter(AIRecommendation.recommendation_type == recommendation_type)
    
    recommendations = query.all()
    return recommendations

@router.get("/recommendations/{recommendation_id}", response_model=AIRecommendationResponse)
async def get_ai_recommendation(
    recommendation_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get a specific AI recommendation"""
    
    recommendation = db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="AI recommendation not found")
    
    return recommendation

@router.put("/recommendations/{recommendation_id}/implement")
async def implement_ai_recommendation(
    recommendation_id: int,
    current_user: User = Depends(require_permission("ai.update")),
    db: Session = Depends(get_db)
):
    """Implement an AI recommendation"""
    
    recommendation = db.query(AIRecommendation).filter(AIRecommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="AI recommendation not found")
    
    # Update recommendation status
    recommendation.status = "implemented"
    recommendation.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "AI recommendation implemented successfully"}