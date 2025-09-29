# backend/app/api/endpoints/l10n_in/indian_geography.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.l10n_in import Country, IndianState, IndianCity, IndianDistrict, IndianTaluka, IndianVillage, IndianPincode

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Schemas ---
class CountryResponse(BaseModel):
    id: int
    country_code: str
    country_name: str
    country_name_local: Optional[str] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    phone_code: Optional[str] = None
    is_active: bool
    is_default: bool
    
    class Config:
        orm_mode = True

class IndianStateResponse(BaseModel):
    id: int
    state_code: str
    state_name: str
    state_name_local: Optional[str] = None
    state_type: str
    gst_state_code: Optional[str] = None
    gst_state_name: Optional[str] = None
    region: Optional[str] = None
    capital: Optional[str] = None
    is_active: bool
    
    class Config:
        orm_mode = True

class IndianCityResponse(BaseModel):
    id: int
    city_name: str
    city_name_local: Optional[str] = None
    city_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pincode: Optional[str] = None
    area_code: Optional[str] = None
    is_active: bool
    is_major_city: bool
    state: IndianStateResponse
    
    class Config:
        orm_mode = True

class IndianDistrictResponse(BaseModel):
    id: int
    district_name: str
    district_name_local: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool
    state: IndianStateResponse
    
    class Config:
        orm_mode = True

class IndianTalukaResponse(BaseModel):
    id: int
    taluka_name: str
    taluka_name_local: Optional[str] = None
    is_active: bool
    district: IndianDistrictResponse
    
    class Config:
        orm_mode = True

class IndianVillageResponse(BaseModel):
    id: int
    village_name: str
    village_name_local: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool
    taluka: IndianTalukaResponse
    
    class Config:
        orm_mode = True

class IndianPincodeResponse(BaseModel):
    id: int
    pincode: str
    area_name: str
    area_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool
    city: Optional[IndianCityResponse] = None
    state: IndianStateResponse
    
    class Config:
        orm_mode = True

# --- Endpoints ---

# Countries
@router.get("/countries", response_model=List[CountryResponse], summary="Get all countries")
async def get_all_countries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves all countries.
    Requires 'view_geography' permission.
    """
    return db.query(Country).filter(Country.is_active == True).all()

@router.get("/countries/{country_id}", response_model=CountryResponse, summary="Get country by ID")
async def get_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves a specific country by ID.
    Requires 'view_geography' permission.
    """
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")
    return country

# Indian States
@router.get("/states", response_model=List[IndianStateResponse], summary="Get all Indian states")
async def get_all_indian_states(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves all Indian states and union territories.
    Requires 'view_geography' permission.
    """
    return db.query(IndianState).filter(IndianState.is_active == True).all()

@router.get("/states/{state_id}", response_model=IndianStateResponse, summary="Get Indian state by ID")
async def get_indian_state(
    state_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves a specific Indian state by ID.
    Requires 'view_geography' permission.
    """
    state = db.query(IndianState).filter(IndianState.id == state_id).first()
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indian state not found")
    return state

@router.get("/states/by-code/{state_code}", response_model=IndianStateResponse, summary="Get Indian state by code")
async def get_indian_state_by_code(
    state_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves an Indian state by its 2-digit code.
    Requires 'view_geography' permission.
    """
    state = db.query(IndianState).filter(IndianState.state_code == state_code).first()
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indian state not found")
    return state

# Indian Cities
@router.get("/cities", response_model=List[IndianCityResponse], summary="Get all Indian cities")
async def get_all_indian_cities(
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    is_major_city: Optional[bool] = Query(None, description="Filter by major cities only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves all Indian cities with optional filtering.
    Requires 'view_geography' permission.
    """
    query = db.query(IndianCity).filter(IndianCity.is_active == True)
    
    if state_id:
        query = query.filter(IndianCity.state_id == state_id)
    if is_major_city is not None:
        query = query.filter(IndianCity.is_major_city == is_major_city)
    
    return query.all()

@router.get("/cities/{city_id}", response_model=IndianCityResponse, summary="Get Indian city by ID")
async def get_indian_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves a specific Indian city by ID.
    Requires 'view_geography' permission.
    """
    city = db.query(IndianCity).filter(IndianCity.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indian city not found")
    return city

@router.get("/cities/search", response_model=List[IndianCityResponse], summary="Search Indian cities")
async def search_indian_cities(
    q: str = Query(..., description="Search query for city name"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Searches Indian cities by name.
    Requires 'view_geography' permission.
    """
    query = db.query(IndianCity).filter(
        IndianCity.is_active == True,
        IndianCity.city_name.ilike(f"%{q}%")
    )
    
    if state_id:
        query = query.filter(IndianCity.state_id == state_id)
    
    return query.limit(limit).all()

# Indian Districts
@router.get("/districts", response_model=List[IndianDistrictResponse], summary="Get all Indian districts")
async def get_all_indian_districts(
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves all Indian districts with optional state filtering.
    Requires 'view_geography' permission.
    """
    query = db.query(IndianDistrict).filter(IndianDistrict.is_active == True)
    
    if state_id:
        query = query.filter(IndianDistrict.state_id == state_id)
    
    return query.all()

# Indian Pincodes
@router.get("/pincodes", response_model=List[IndianPincodeResponse], summary="Get pincodes")
async def get_pincodes(
    pincode: Optional[str] = Query(None, description="Search by pincode"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    city_id: Optional[int] = Query(None, description="Filter by city ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves pincodes with optional filtering.
    Requires 'view_geography' permission.
    """
    query = db.query(IndianPincode).filter(IndianPincode.is_active == True)
    
    if pincode:
        query = query.filter(IndianPincode.pincode.ilike(f"%{pincode}%"))
    if state_id:
        query = query.filter(IndianPincode.state_id == state_id)
    if city_id:
        query = query.filter(IndianPincode.city_id == city_id)
    
    return query.limit(limit).all()

@router.get("/pincodes/{pincode_id}", response_model=IndianPincodeResponse, summary="Get pincode by ID")
async def get_pincode(
    pincode_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves a specific pincode by ID.
    Requires 'view_geography' permission.
    """
    pincode = db.query(IndianPincode).filter(IndianPincode.id == pincode_id).first()
    if not pincode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pincode not found")
    return pincode

# Geographic Hierarchy
@router.get("/geography/hierarchy", summary="Get geographic hierarchy")
async def get_geographic_hierarchy(
    country_id: Optional[int] = Query(None, description="Country ID"),
    state_id: Optional[int] = Query(None, description="State ID"),
    city_id: Optional[int] = Query(None, description="City ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Retrieves geographic hierarchy based on provided IDs.
    Requires 'view_geography' permission.
    """
    result = {}
    
    if country_id:
        country = db.query(Country).filter(Country.id == country_id).first()
        if country:
            result["country"] = CountryResponse.from_orm(country)
            result["states"] = [IndianStateResponse.from_orm(state) for state in country.states if state.is_active]
    
    if state_id:
        state = db.query(IndianState).filter(IndianState.id == state_id).first()
        if state:
            result["state"] = IndianStateResponse.from_orm(state)
            result["cities"] = [IndianCityResponse.from_orm(city) for city in state.cities if city.is_active]
            result["districts"] = [IndianDistrictResponse.from_orm(district) for district in state.districts if district.is_active]
    
    if city_id:
        city = db.query(IndianCity).filter(IndianCity.id == city_id).first()
        if city:
            result["city"] = IndianCityResponse.from_orm(city)
            result["pincodes"] = [IndianPincodeResponse.from_orm(pincode) for pincode in city.pincodes if pincode.is_active]
    
    return result