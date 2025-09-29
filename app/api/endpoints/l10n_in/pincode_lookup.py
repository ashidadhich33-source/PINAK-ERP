# backend/app/api/endpoints/l10n_in/pincode_lookup.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path
import logging

from ...database import get_db
from ...core.security import get_current_user, require_permission
from ...models.core import User, Company
from ...models.l10n_in import IndianPincode, IndianCity, IndianState

router = APIRouter()
logger = logging.getLogger(__name__)

# Load processed pincode data
PINCODE_DATA = None
PINCODE_LOOKUP = None
CITY_LOOKUP = None
STATE_LOOKUP = None
AREA_LOOKUP = None

def load_pincode_data():
    """Load processed pincode data from JSON files"""
    global PINCODE_DATA, PINCODE_LOOKUP, CITY_LOOKUP, STATE_LOOKUP, AREA_LOOKUP
    
    try:
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
        
        # Load pincode data
        pincodes_file = data_dir / "pincodes.json"
        if pincodes_file.exists():
            with open(pincodes_file, 'r', encoding='utf-8') as f:
                PINCODE_DATA = json.load(f)
        
        # Load lookup data
        lookup_file = data_dir / "pincode_lookup.json"
        if lookup_file.exists():
            with open(lookup_file, 'r', encoding='utf-8') as f:
                PINCODE_LOOKUP = json.load(f)
        
        city_lookup_file = data_dir / "city_lookup.json"
        if city_lookup_file.exists():
            with open(city_lookup_file, 'r', encoding='utf-8') as f:
                CITY_LOOKUP = json.load(f)
        
        state_lookup_file = data_dir / "state_lookup.json"
        if state_lookup_file.exists():
            with open(state_lookup_file, 'r', encoding='utf-8') as f:
                STATE_LOOKUP = json.load(f)
        
        area_lookup_file = data_dir / "area_lookup.json"
        if area_lookup_file.exists():
            with open(area_lookup_file, 'r', encoding='utf-8') as f:
                AREA_LOOKUP = json.load(f)
        
        logger.info("✅ Pincode data loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading pincode data: {e}")

# Initialize data on module load
load_pincode_data()

# --- Schemas ---
class PincodeResponse(BaseModel):
    pincode: str
    area_name: str
    city_name: str
    state_name: str
    state_code: str
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True

class CityResponse(BaseModel):
    city_name: str
    state_name: str
    state_code: str
    region: Optional[str] = None
    pincodes: List[str]
    total_pincodes: int

class StateResponse(BaseModel):
    state_name: str
    state_code: str
    region: Optional[str] = None
    cities: List[str]
    pincodes: List[str]
    total_cities: int
    total_pincodes: int

class AreaResponse(BaseModel):
    area_name: str
    city_name: str
    state_name: str
    state_code: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PincodeSearchResponse(BaseModel):
    query: str
    results: List[PincodeResponse]
    total_results: int
    search_type: str

# --- Endpoints ---

@router.get("/pincodes/{pincode}", response_model=PincodeResponse, summary="Get pincode details")
async def get_pincode_details(
    pincode: str,
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Get detailed information for a specific pincode.
    Requires 'view_geography' permission.
    """
    if not PINCODE_LOOKUP:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Pincode data not loaded")
    
    # Clean pincode (remove spaces, ensure 6 digits)
    clean_pincode = pincode.strip().zfill(6)
    
    if clean_pincode not in PINCODE_LOOKUP:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pincode {pincode} not found")
    
    return PincodeResponse(**PINCODE_LOOKUP[clean_pincode])

@router.get("/pincodes/city/{city_name}", response_model=CityResponse, summary="Get city pincodes")
async def get_city_pincodes(
    city_name: str,
    state_name: Optional[str] = Query(None, description="Filter by state name"),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Get all pincodes for a specific city.
    Requires 'view_geography' permission.
    """
    if not CITY_LOOKUP:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="City data not loaded")
    
    # Search for city (case insensitive)
    city_key = None
    for key, data in CITY_LOOKUP.items():
        if city_name.lower() in data["city_name"].lower():
            if not state_name or state_name.lower() in data["state_name"].lower():
                city_key = key
                break
    
    if not city_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"City {city_name} not found")
    
    city_data = CITY_LOOKUP[city_key]
    return CityResponse(
        city_name=city_data["city_name"],
        state_name=city_data["state_name"],
        state_code=city_data["state_code"],
        region=city_data.get("region"),
        pincodes=city_data["pincodes"],
        total_pincodes=len(city_data["pincodes"])
    )

@router.get("/pincodes/state/{state_name}", response_model=StateResponse, summary="Get state cities and pincodes")
async def get_state_data(
    state_name: str,
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Get all cities and pincodes for a specific state.
    Requires 'view_geography' permission.
    """
    if not STATE_LOOKUP:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="State data not loaded")
    
    # Search for state (case insensitive)
    state_key = None
    for key, data in STATE_LOOKUP.items():
        if state_name.lower() in data["state_name"].lower():
            state_key = key
            break
    
    if not state_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"State {state_name} not found")
    
    state_data = STATE_LOOKUP[state_key]
    return StateResponse(
        state_name=state_data["state_name"],
        state_code=state_data["state_code"],
        region=state_data.get("region"),
        cities=state_data["cities"],
        pincodes=state_data["pincodes"],
        total_cities=len(state_data["cities"]),
        total_pincodes=len(state_data["pincodes"])
    )

@router.get("/pincodes/search", response_model=PincodeSearchResponse, summary="Search pincodes")
async def search_pincodes(
    q: str = Query(..., description="Search query (pincode, area, city, state)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    search_type: str = Query("all", description="Search type: all, pincode, area, city, state"),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Search pincodes by various criteria.
    Requires 'view_geography' permission.
    """
    if not PINCODE_DATA:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Pincode data not loaded")
    
    results = []
    query_lower = q.lower()
    
    for pincode_data in PINCODE_DATA:
        match = False
        
        if search_type in ["all", "pincode"] and query_lower in pincode_data["pincode"]:
            match = True
        elif search_type in ["all", "area"] and query_lower in pincode_data["area_name"].lower():
            match = True
        elif search_type in ["all", "city"] and query_lower in pincode_data["city_name"].lower():
            match = True
        elif search_type in ["all", "state"] and query_lower in pincode_data["state_name"].lower():
            match = True
        
        if match:
            results.append(PincodeResponse(**pincode_data))
            if len(results) >= limit:
                break
    
    return PincodeSearchResponse(
        query=q,
        results=results,
        total_results=len(results),
        search_type=search_type
    )

@router.get("/pincodes/area/{area_name}", response_model=List[AreaResponse], summary="Get area details")
async def get_area_details(
    area_name: str,
    city_name: Optional[str] = Query(None, description="Filter by city name"),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Get details for a specific area.
    Requires 'view_geography' permission.
    """
    if not AREA_LOOKUP:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Area data not loaded")
    
    results = []
    for key, data in AREA_LOOKUP.items():
        if area_name.lower() in data["area_name"].lower():
            if not city_name or city_name.lower() in data["city_name"].lower():
                results.append(AreaResponse(**data))
    
    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Area {area_name} not found")
    
    return results

@router.get("/pincodes/nearby", response_model=List[PincodeResponse], summary="Find nearby pincodes")
async def find_nearby_pincodes(
    latitude: float = Query(..., description="Latitude coordinate"),
    longitude: float = Query(..., description="Longitude coordinate"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Find pincodes near a specific location.
    Requires 'view_geography' permission.
    """
    if not PINCODE_DATA:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Pincode data not loaded")
    
    # Simple distance calculation (for production, use proper geospatial queries)
    def calculate_distance(lat1, lon1, lat2, lon2):
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')
        
        # Haversine formula (simplified)
        import math
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    nearby_pincodes = []
    for pincode_data in PINCODE_DATA:
        if pincode_data.get("latitude") and pincode_data.get("longitude"):
            distance = calculate_distance(
                latitude, longitude,
                pincode_data["latitude"], pincode_data["longitude"]
            )
            if distance <= radius_km:
                nearby_pincodes.append((distance, PincodeResponse(**pincode_data)))
    
    # Sort by distance and limit results
    nearby_pincodes.sort(key=lambda x: x[0])
    results = [pincode for _, pincode in nearby_pincodes[:limit]]
    
    return results

@router.get("/pincodes/stats", summary="Get pincode statistics")
async def get_pincode_statistics(
    current_user: User = Depends(require_permission("view_geography"))
):
    """
    Get statistics about the pincode database.
    Requires 'view_geography' permission.
    """
    if not PINCODE_DATA:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Pincode data not loaded")
    
    stats = {
        "total_pincodes": len(PINCODE_DATA),
        "total_cities": len(CITY_LOOKUP) if CITY_LOOKUP else 0,
        "total_states": len(STATE_LOOKUP) if STATE_LOOKUP else 0,
        "total_areas": len(AREA_LOOKUP) if AREA_LOOKUP else 0,
        "data_loaded": True,
        "last_updated": "Unknown"  # Could be added to metadata
    }
    
    return stats

@router.post("/pincodes/reload", summary="Reload pincode data")
async def reload_pincode_data(
    current_user: User = Depends(require_permission("manage_geography"))
):
    """
    Reload pincode data from JSON files.
    Requires 'manage_geography' permission.
    """
    try:
        load_pincode_data()
        return {"message": "Pincode data reloaded successfully", "status": "success"}
    except Exception as e:
        logger.error(f"Error reloading pincode data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to reload data: {e}")