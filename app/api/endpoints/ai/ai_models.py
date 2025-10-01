# backend/app/api/endpoints/ai_models.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.ai.ai_models import AIModel
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class AIModelCreate(BaseModel):
    model_name: str
    model_type: str
    model_version: str
    model_path: Optional[str] = None
    model_parameters: Optional[str] = None
    training_data: Optional[str] = None
    performance_metrics: Optional[str] = None
    company_id: int

class AIModelResponse(BaseModel):
    id: int
    model_name: str
    model_type: str
    model_version: str
    model_path: Optional[str]
    model_parameters: Optional[str]
    training_data: Optional[str]
    performance_metrics: Optional[str]
    status: str

    class Config:
        from_attributes = True

@router.post("/models", response_model=AIModelResponse)
async def create_ai_model(
    model_data: AIModelCreate,
    current_user: User = Depends(require_permission("ai.create")),
    db: Session = Depends(get_db)
):
    """Create a new AI model"""
    
    # Create AI model
    ai_model = AIModel(
        model_name=model_data.model_name,
        model_type=model_data.model_type,
        model_version=model_data.model_version,
        model_path=model_data.model_path,
        model_parameters=model_data.model_parameters,
        training_data=model_data.training_data,
        performance_metrics=model_data.performance_metrics,
        company_id=model_data.company_id,
        created_by=current_user.id
    )
    
    db.add(ai_model)
    db.commit()
    db.refresh(ai_model)
    
    return ai_model

@router.get("/models", response_model=List[AIModelResponse])
async def get_ai_models(
    company_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get AI models for a company"""
    
    models = db.query(AIModel).filter(
        AIModel.company_id == company_id
    ).all()
    
    return models

@router.get("/models/{model_id}", response_model=AIModelResponse)
async def get_ai_model(
    model_id: int,
    current_user: User = Depends(require_permission("ai.view")),
    db: Session = Depends(get_db)
):
    """Get a specific AI model"""
    
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    return model

@router.put("/models/{model_id}/train")
async def train_ai_model(
    model_id: int,
    training_data: str,
    current_user: User = Depends(require_permission("ai.update")),
    db: Session = Depends(get_db)
):
    """Train an AI model"""
    
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="AI model not found")
    
    # Update model status to training
    model.status = "training"
    model.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "AI model training initiated"}