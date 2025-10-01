# backend/app/api/endpoints/ai_predictions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.ai.ai_models import AIPrediction
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class AIPredictionCreate(BaseModel):
    analytics_id: int
    prediction_type: str
    prediction_data: str
    confidence_score: Optional[Decimal] = None
    company_id: int

class AIPredictionResponse(BaseModel):
    id: int
    analytics_id: int
    prediction_type: str
    prediction_data: str
    confidence_score: Optional[Decimal]
    prediction_date: datetime
    status: str

    class Config:
        from_attributes = True

@router.post("/predictions", response_model=AIPredictionResponse)
async def create_ai_prediction(
    prediction_data: AIPredictionCreate,
    current_user: User = Depends(require_permission("ai.create")),
    db: Session = Depends(get_db)
):
    """Create a new AI prediction"""
    
    # Create AI prediction
    ai_prediction = AIPrediction(
        analytics_id=prediction_data.analytics_id,
        prediction_type=prediction_data.prediction_type,
        prediction_data=prediction_data.prediction_data,
        confidence_score=prediction_data.confidence_score,
        company_id=prediction_data.company_id,
        created_by=current_user.id
    )
    
    db.add(ai_prediction)
    db.commit()
    db.refresh(ai_prediction)
    
    return ai_prediction

@router.get("/predictions", response_model=List[AIPredictionResponse])
async def get_ai_predictions(
    company_id: int,
    prediction_type: Optional[str] = None,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get AI predictions for a company"""
    
    query = db.query(AIPrediction).filter(AIPrediction.company_id == company_id)
    
    if prediction_type:
        query = query.filter(AIPrediction.prediction_type == prediction_type)
    
    predictions = query.all()
    return predictions

@router.get("/predictions/{prediction_id}", response_model=AIPredictionResponse)
async def get_ai_prediction(
    prediction_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get a specific AI prediction"""
    
    prediction = db.query(AIPrediction).filter(AIPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="AI prediction not found")
    
    return prediction

@router.get("/demand-forecast")
async def get_demand_forecast(
    company_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get demand forecast"""
    
    # This would implement the actual demand forecast logic
    # For now, return a sample response
    return {
        "forecast": [
            {"item_id": 1, "item_name": "Product A", "demand_forecast": 1000, "confidence": 92.5},
            {"item_id": 2, "item_name": "Product B", "demand_forecast": 500, "confidence": 88.3}
        ]
    }