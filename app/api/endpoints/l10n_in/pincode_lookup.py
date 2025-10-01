# backend/app/api/endpoints/pincode_lookup.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date

from ...database import get_db
from ...models.l10n_in.indian_geography import IndianPincode, IndianState, IndianCity, IndianDistrict, IndianTaluka, IndianVillage
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class PincodeResponse(BaseModel):
    id: int
    pincode: str
    state_name: str
    city_name: str
    district_name: str
    taluka_name: str
    village_name: str
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/pincode/{pincode}", response_model=PincodeResponse)
async def get_pincode_details(
    pincode: str,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Get pincode details"""
    
    pincode_record = db.query(IndianPincode).filter(
        IndianPincode.pincode == pincode,
        IndianPincode.is_active == True
    ).first()
    
    if not pincode_record:
        raise HTTPException(status_code=404, detail="Pincode not found")
    
    # Get related geography data
    state = db.query(IndianState).filter(IndianState.id == pincode_record.state_id).first()
    city = db.query(IndianCity).filter(IndianCity.id == pincode_record.city_id).first()
    district = db.query(IndianDistrict).filter(IndianDistrict.id == pincode_record.district_id).first()
    taluka = db.query(IndianTaluka).filter(IndianTaluka.id == pincode_record.taluka_id).first()
    village = db.query(IndianVillage).filter(IndianVillage.id == pincode_record.village_id).first()
    
    return PincodeResponse(
        id=pincode_record.id,
        pincode=pincode_record.pincode,
        state_name=state.name if state else "",
        city_name=city.name if city else "",
        district_name=district.name if district else "",
        taluka_name=taluka.name if taluka else "",
        village_name=village.name if village else "",
        is_active=pincode_record.is_active
    )

@router.get("/pincode/search", response_model=List[PincodeResponse])
async def search_pincodes(
    query: str,
    limit: int = 10,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Search pincodes by query"""
    
    pincodes = db.query(IndianPincode).filter(
        IndianPincode.pincode.like(f"%{query}%"),
        IndianPincode.is_active == True
    ).limit(limit).all()
    
    results = []
    for pincode in pincodes:
        # Get related geography data
        state = db.query(IndianState).filter(IndianState.id == pincode.state_id).first()
        city = db.query(IndianCity).filter(IndianCity.id == pincode.city_id).first()
        district = db.query(IndianDistrict).filter(IndianDistrict.id == pincode.district_id).first()
        taluka = db.query(IndianTaluka).filter(IndianTaluka.id == pincode.taluka_id).first()
        village = db.query(IndianVillage).filter(IndianVillage.id == pincode.village_id).first()
        
        results.append(PincodeResponse(
            id=pincode.id,
            pincode=pincode.pincode,
            state_name=state.name if state else "",
            city_name=city.name if city else "",
            district_name=district.name if district else "",
            taluka_name=taluka.name if taluka else "",
            village_name=village.name if village else "",
            is_active=pincode.is_active
        ))
    
    return results

@router.get("/pincode/validate/{pincode}")
async def validate_pincode(
    pincode: str,
    current_user: User = Depends(require_permission("geography.view")),
    db: Session = Depends(get_db)
):
    """Validate if pincode exists"""
    
    pincode_record = db.query(IndianPincode).filter(
        IndianPincode.pincode == pincode,
        IndianPincode.is_active == True
    ).first()
    
    return {
        "pincode": pincode,
        "exists": pincode_record is not None,
        "valid": pincode_record is not None
    }