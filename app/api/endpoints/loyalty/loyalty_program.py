# backend/app/api/endpoints/loyalty_program.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.loyalty.loyalty_program import LoyaltyProgram, LoyaltyGrade
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class LoyaltyProgramCreate(BaseModel):
    name: str
    description: str
    points_per_rupee: Decimal
    redemption_rate: Decimal
    company_id: int

class LoyaltyProgramResponse(BaseModel):
    id: int
    name: str
    description: str
    points_per_rupee: Decimal
    redemption_rate: Decimal
    is_active: bool

    class Config:
        from_attributes = True

@router.post("/loyalty-programs", response_model=LoyaltyProgramResponse)
async def create_loyalty_program(
    program_data: LoyaltyProgramCreate,
    current_user: User = Depends(require_permission("loyalty.create")),
    db: Session = Depends(get_db)
):
    """Create a new loyalty program"""
    
    # Create loyalty program
    loyalty_program = LoyaltyProgram(
        name=program_data.name,
        description=program_data.description,
        points_per_rupee=program_data.points_per_rupee,
        redemption_rate=program_data.redemption_rate,
        company_id=program_data.company_id,
        created_by=current_user.id
    )
    
    db.add(loyalty_program)
    db.commit()
    db.refresh(loyalty_program)
    
    return loyalty_program

@router.get("/loyalty-programs", response_model=List[LoyaltyProgramResponse])
async def get_loyalty_programs(
    company_id: int,
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get loyalty programs for a company"""
    
    programs = db.query(LoyaltyProgram).filter(
        LoyaltyProgram.company_id == company_id
    ).all()
    
    return programs

@router.get("/loyalty-programs/{program_id}", response_model=LoyaltyProgramResponse)
async def get_loyalty_program(
    program_id: int,
    current_user: User = Depends(require_permission("loyalty.view")),
    db: Session = Depends(get_db)
):
    """Get a specific loyalty program"""
    
    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    
    return program

@router.put("/loyalty-programs/{program_id}", response_model=LoyaltyProgramResponse)
async def update_loyalty_program(
    program_id: int,
    program_data: LoyaltyProgramCreate,
    current_user: User = Depends(require_permission("loyalty.update")),
    db: Session = Depends(get_db)
):
    """Update a loyalty program"""
    
    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    
    # Update program fields
    program.name = program_data.name
    program.description = program_data.description
    program.points_per_rupee = program_data.points_per_rupee
    program.redemption_rate = program_data.redemption_rate
    program.updated_by = current_user.id
    
    db.commit()
    db.refresh(program)
    
    return program

@router.delete("/loyalty-programs/{program_id}")
async def delete_loyalty_program(
    program_id: int,
    current_user: User = Depends(require_permission("loyalty.delete")),
    db: Session = Depends(get_db)
):
    """Delete a loyalty program"""
    
    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Loyalty program not found")
    
    # Soft delete
    program.is_active = False
    program.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "Loyalty program deleted successfully"}