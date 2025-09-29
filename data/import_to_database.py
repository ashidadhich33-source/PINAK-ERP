#!/usr/bin/env python3
"""
Import Processed Geography Data to Database
This script imports the processed JSON data into the ERP database
"""

import json
import sys
import os
from pathlib import Path
import logging

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import get_db_session
from app.models.l10n_in import Country, IndianState, IndianCity, IndianPincode
from app.core.init_indian_geography import init_indian_geography_data

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_geography_data(db: Session, data_dir: str):
    """Import geography data from processed JSON files"""
    
    logger.info("🗄️ Starting geography data import...")
    
    # Load processed data
    states_file = Path(data_dir) / "processed" / "states.json"
    cities_file = Path(data_dir) / "processed" / "cities.json"
    pincodes_file = Path(data_dir) / "processed" / "pincodes.json"
    
    # Load states
    states_data = []
    if states_file.exists():
        with open(states_file, 'r', encoding='utf-8') as f:
            states_data = json.load(f)
        logger.info(f"Loaded {len(states_data)} states")
    else:
        logger.warning("States file not found, using default initialization")
        init_indian_geography_data(db)
        return
    
    # Load cities
    cities_data = []
    if cities_file.exists():
        with open(cities_file, 'r', encoding='utf-8') as f:
            cities_data = json.load(f)
        logger.info(f"Loaded {len(cities_data)} cities")
    
    # Load pincodes
    pincodes_data = []
    if pincodes_file.exists():
        with open(pincodes_file, 'r', encoding='utf-8') as f:
            pincodes_data = json.load(f)
        logger.info(f"Loaded {len(pincodes_data)} pincodes")
    
    # Get or create India country
    india = db.query(Country).filter(Country.country_code == "IND").first()
    if not india:
        india = Country(
            country_code="IND",
            country_name="India",
            country_name_local="भारत",
            currency_code="INR",
            currency_symbol="₹",
            phone_code="+91",
            is_active=True,
            is_default=True
        )
        db.add(india)
        db.commit()
        db.refresh(india)
        logger.info("Created India country record")
    
    # Import states
    state_mapping = {}
    for state_data in states_data:
        existing_state = db.query(IndianState).filter(
            IndianState.state_code == state_data["state_code"]
        ).first()
        
        if not existing_state:
            state = IndianState(
                state_code=state_data["state_code"],
                state_name=state_data["state_name"],
                state_type=state_data.get("state_type", "state"),
                region=state_data.get("region"),
                capital=state_data.get("capital"),
                gst_state_code=state_data.get("gst_state_code", state_data["state_code"]),
                gst_state_name=state_data.get("gst_state_name", state_data["state_name"]),
                country_id=india.id,
                is_active=state_data.get("is_active", True)
            )
            db.add(state)
            db.commit()
            db.refresh(state)
            logger.info(f"Created state: {state_data['state_name']}")
        else:
            state = existing_state
        
        state_mapping[state_data["state_code"]] = state.id
    
    # Import cities
    city_mapping = {}
    for city_data in cities_data:
        state_id = state_mapping.get(city_data["state_code"])
        if not state_id:
            logger.warning(f"State not found for city: {city_data['city_name']}")
            continue
        
        existing_city = db.query(IndianCity).filter(
            IndianCity.city_name == city_data["city_name"],
            IndianCity.state_id == state_id
        ).first()
        
        if not existing_city:
            city = IndianCity(
                city_name=city_data["city_name"],
                city_type=city_data.get("city_type", "city"),
                is_major_city=city_data.get("is_major_city", False),
                latitude=city_data.get("latitude"),
                longitude=city_data.get("longitude"),
                state_id=state_id,
                is_active=city_data.get("is_active", True)
            )
            db.add(city)
            db.commit()
            db.refresh(city)
            logger.info(f"Created city: {city_data['city_name']}")
        else:
            city = existing_city
        
        city_mapping[f"{city_data['city_name']}_{city_data['state_code']}"] = city.id
    
    # Import pincodes
    for pincode_data in pincodes_data:
        state_id = state_mapping.get(pincode_data["state_code"])
        if not state_id:
            logger.warning(f"State not found for pincode: {pincode_data['pincode']}")
            continue
        
        city_id = city_mapping.get(f"{pincode_data['city_name']}_{pincode_data['state_code']}")
        
        existing_pincode = db.query(IndianPincode).filter(
            IndianPincode.pincode == pincode_data["pincode"]
        ).first()
        
        if not existing_pincode:
            pincode = IndianPincode(
                pincode=pincode_data["pincode"],
                area_name=pincode_data["area_name"],
                area_type=pincode_data.get("area_type", "Post Office"),
                latitude=pincode_data.get("latitude"),
                longitude=pincode_data.get("longitude"),
                city_id=city_id,
                state_id=state_id,
                is_active=pincode_data.get("is_active", True)
            )
            db.add(pincode)
            db.commit()
            logger.info(f"Created pincode: {pincode_data['pincode']} - {pincode_data['area_name']}")
    
    logger.info("✅ Geography data import completed!")

def main():
    """Main import function"""
    logger.info("🚀 Starting geography data import to database...")
    
    try:
        with get_db_session() as db:
            data_dir = Path(__file__).parent
            import_geography_data(db, str(data_dir))
        
        logger.info("🎉 Database import completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database import failed: {e}")
        raise

if __name__ == "__main__":
    main()