# backend/app/api/endpoints/indian_geography.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from ...database import get_db
from ...models.l10n_in.indian_geography import IndianState, IndianCity, IndianDistrict, IndianTaluka, IndianVillage, IndianPincode
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class StateResponse(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool

    class Config:
        from_attributes = True

class CityResponse(BaseModel):
    id: int
    name: str
    state_id: int
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/states", response_model=List[StateResponse])
async def get_states(
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get all Indian states"""
    
    states = db.query(IndianState).filter(IndianState.is_active == True).all()
    return states

@router.get("/states/{state_id}/cities", response_model=List[CityResponse])
async def get_cities_by_state(
    state_id: int,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get cities by state"""
    
    cities = db.query(IndianCity).filter(
        IndianCity.state_id == state_id,
        IndianCity.is_active == True
    ).all()
    
    return cities

@router.get("/cities/{city_id}/districts", response_model=List[dict])
async def get_districts_by_city(
    city_id: int,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get districts by city"""
    
    districts = db.query(IndianDistrict).filter(
        IndianDistrict.city_id == city_id,
        IndianDistrict.is_active == True
    ).all()
    
    return [
        {
            "id": district.id,
            "name": district.name,
            "city_id": district.city_id,
            "is_active": district.is_active
        }
        for district in districts
    ]

@router.get("/districts/{district_id}/talukas", response_model=List[dict])
async def get_talukas_by_district(
    district_id: int,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get talukas by district"""
    
    talukas = db.query(IndianTaluka).filter(
        IndianTaluka.district_id == district_id,
        IndianTaluka.is_active == True
    ).all()
    
    return [
        {
            "id": taluka.id,
            "name": taluka.name,
            "district_id": taluka.district_id,
            "is_active": taluka.is_active
        }
        for taluka in talukas
    ]

@router.get("/talukas/{taluka_id}/villages", response_model=List[dict])
async def get_villages_by_taluka(
    taluka_id: int,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get villages by taluka"""
    
    villages = db.query(IndianVillage).filter(
        IndianVillage.taluka_id == taluka_id,
        IndianVillage.is_active == True
    ).all()
    
    return [
        {
            "id": village.id,
            "name": village.name,
            "taluka_id": village.taluka_id,
            "is_active": village.is_active
        }
        for village in villages
    ]