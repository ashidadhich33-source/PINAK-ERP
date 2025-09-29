# backend/app/core/init_indian_geography.py
"""
Initialize Indian Geography Data
This script populates the database with Indian states, cities, and pincodes
"""

from sqlalchemy.orm import Session
from ..models.l10n_in import Country, IndianState, IndianCity, IndianDistrict, IndianPincode
import logging

logger = logging.getLogger(__name__)

def init_indian_geography_data(db: Session):
    """Initialize Indian geography data"""
    
    logger.info("Initializing Indian Geography Data...")
    
    # Create India country record
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
    
    # Indian States and Union Territories
    indian_states = [
        # States
        {"code": "01", "name": "Jammu and Kashmir", "type": "state", "region": "North", "capital": "Srinagar"},
        {"code": "02", "name": "Himachal Pradesh", "type": "state", "region": "North", "capital": "Shimla"},
        {"code": "03", "name": "Punjab", "type": "state", "region": "North", "capital": "Chandigarh"},
        {"code": "04", "name": "Chandigarh", "type": "union_territory", "region": "North", "capital": "Chandigarh"},
        {"code": "05", "name": "Uttarakhand", "type": "state", "region": "North", "capital": "Dehradun"},
        {"code": "06", "name": "Haryana", "type": "state", "region": "North", "capital": "Chandigarh"},
        {"code": "07", "name": "Delhi", "type": "union_territory", "region": "North", "capital": "New Delhi"},
        {"code": "08", "name": "Rajasthan", "type": "state", "region": "North", "capital": "Jaipur"},
        {"code": "09", "name": "Uttar Pradesh", "type": "state", "region": "North", "capital": "Lucknow"},
        {"code": "10", "name": "Bihar", "type": "state", "region": "East", "capital": "Patna"},
        {"code": "11", "name": "Sikkim", "type": "state", "region": "Northeast", "capital": "Gangtok"},
        {"code": "12", "name": "Arunachal Pradesh", "type": "state", "region": "Northeast", "capital": "Itanagar"},
        {"code": "13", "name": "Nagaland", "type": "state", "region": "Northeast", "capital": "Kohima"},
        {"code": "14", "name": "Manipur", "type": "state", "region": "Northeast", "capital": "Imphal"},
        {"code": "15", "name": "Mizoram", "type": "state", "region": "Northeast", "capital": "Aizawl"},
        {"code": "16", "name": "Tripura", "type": "state", "region": "Northeast", "capital": "Agartala"},
        {"code": "17", "name": "Meghalaya", "type": "state", "region": "Northeast", "capital": "Shillong"},
        {"code": "18", "name": "Assam", "type": "state", "region": "Northeast", "capital": "Dispur"},
        {"code": "19", "name": "West Bengal", "type": "state", "region": "East", "capital": "Kolkata"},
        {"code": "20", "name": "Jharkhand", "type": "state", "region": "East", "capital": "Ranchi"},
        {"code": "21", "name": "Odisha", "type": "state", "region": "East", "capital": "Bhubaneswar"},
        {"code": "22", "name": "Chhattisgarh", "type": "state", "region": "Central", "capital": "Raipur"},
        {"code": "23", "name": "Madhya Pradesh", "type": "state", "region": "Central", "capital": "Bhopal"},
        {"code": "24", "name": "Gujarat", "type": "state", "region": "West", "capital": "Gandhinagar"},
        {"code": "25", "name": "Daman and Diu", "type": "union_territory", "region": "West", "capital": "Daman"},
        {"code": "26", "name": "Dadra and Nagar Haveli", "type": "union_territory", "region": "West", "capital": "Silvassa"},
        {"code": "27", "name": "Maharashtra", "type": "state", "region": "West", "capital": "Mumbai"},
        {"code": "28", "name": "Andhra Pradesh", "type": "state", "region": "South", "capital": "Amaravati"},
        {"code": "29", "name": "Karnataka", "type": "state", "region": "South", "capital": "Bangalore"},
        {"code": "30", "name": "Goa", "type": "state", "region": "West", "capital": "Panaji"},
        {"code": "31", "name": "Lakshadweep", "type": "union_territory", "region": "South", "capital": "Kavaratti"},
        {"code": "32", "name": "Kerala", "type": "state", "region": "South", "capital": "Thiruvananthapuram"},
        {"code": "33", "name": "Tamil Nadu", "type": "state", "region": "South", "capital": "Chennai"},
        {"code": "34", "name": "Puducherry", "type": "union_territory", "region": "South", "capital": "Puducherry"},
        {"code": "35", "name": "Andaman and Nicobar Islands", "type": "union_territory", "region": "South", "capital": "Port Blair"},
        {"code": "36", "name": "Telangana", "type": "state", "region": "South", "capital": "Hyderabad"},
        {"code": "37", "name": "Ladakh", "type": "union_territory", "region": "North", "capital": "Leh"},
    ]
    
    # Create states
    for state_data in indian_states:
        existing_state = db.query(IndianState).filter(IndianState.state_code == state_data["code"]).first()
        if not existing_state:
            state = IndianState(
                state_code=state_data["code"],
                state_name=state_data["name"],
                state_type=state_data["type"],
                region=state_data["region"],
                capital=state_data["capital"],
                gst_state_code=state_data["code"],
                gst_state_name=state_data["name"],
                country_id=india.id,
                is_active=True
            )
            db.add(state)
            db.commit()
            db.refresh(state)
            logger.info(f"Created state: {state_data['name']}")
    
    # Major Indian Cities
    major_cities = [
        # Maharashtra
        {"name": "Mumbai", "state_code": "27", "type": "metro", "is_major": True},
        {"name": "Pune", "state_code": "27", "type": "city", "is_major": True},
        {"name": "Nagpur", "state_code": "27", "type": "city", "is_major": True},
        {"name": "Nashik", "state_code": "27", "type": "city", "is_major": True},
        {"name": "Aurangabad", "state_code": "27", "type": "city", "is_major": False},
        
        # Delhi
        {"name": "New Delhi", "state_code": "07", "type": "metro", "is_major": True},
        {"name": "Delhi", "state_code": "07", "type": "metro", "is_major": True},
        
        # Karnataka
        {"name": "Bangalore", "state_code": "29", "type": "metro", "is_major": True},
        {"name": "Mysore", "state_code": "29", "type": "city", "is_major": True},
        {"name": "Hubli", "state_code": "29", "type": "city", "is_major": False},
        
        # Tamil Nadu
        {"name": "Chennai", "state_code": "33", "type": "metro", "is_major": True},
        {"name": "Coimbatore", "state_code": "33", "type": "city", "is_major": True},
        {"name": "Madurai", "state_code": "33", "type": "city", "is_major": True},
        
        # West Bengal
        {"name": "Kolkata", "state_code": "19", "type": "metro", "is_major": True},
        {"name": "Howrah", "state_code": "19", "type": "city", "is_major": True},
        
        # Gujarat
        {"name": "Ahmedabad", "state_code": "24", "type": "metro", "is_major": True},
        {"name": "Surat", "state_code": "24", "type": "city", "is_major": True},
        {"name": "Vadodara", "state_code": "24", "type": "city", "is_major": True},
        
        # Rajasthan
        {"name": "Jaipur", "state_code": "08", "type": "city", "is_major": True},
        {"name": "Jodhpur", "state_code": "08", "type": "city", "is_major": True},
        {"name": "Udaipur", "state_code": "08", "type": "city", "is_major": True},
        
        # Uttar Pradesh
        {"name": "Lucknow", "state_code": "09", "type": "city", "is_major": True},
        {"name": "Kanpur", "state_code": "09", "type": "city", "is_major": True},
        {"name": "Agra", "state_code": "09", "type": "city", "is_major": True},
        {"name": "Varanasi", "state_code": "09", "type": "city", "is_major": True},
        
        # Andhra Pradesh
        {"name": "Hyderabad", "state_code": "28", "type": "metro", "is_major": True},
        {"name": "Visakhapatnam", "state_code": "28", "type": "city", "is_major": True},
        
        # Telangana
        {"name": "Hyderabad", "state_code": "36", "type": "metro", "is_major": True},
        
        # Kerala
        {"name": "Thiruvananthapuram", "state_code": "32", "type": "city", "is_major": True},
        {"name": "Kochi", "state_code": "32", "type": "city", "is_major": True},
        {"name": "Kozhikode", "state_code": "32", "type": "city", "is_major": True},
        
        # Punjab
        {"name": "Chandigarh", "state_code": "03", "type": "city", "is_major": True},
        {"name": "Ludhiana", "state_code": "03", "type": "city", "is_major": True},
        {"name": "Amritsar", "state_code": "03", "type": "city", "is_major": True},
        
        # Haryana
        {"name": "Gurgaon", "state_code": "06", "type": "city", "is_major": True},
        {"name": "Faridabad", "state_code": "06", "type": "city", "is_major": True},
        
        # Madhya Pradesh
        {"name": "Bhopal", "state_code": "23", "type": "city", "is_major": True},
        {"name": "Indore", "state_code": "23", "type": "city", "is_major": True},
        {"name": "Gwalior", "state_code": "23", "type": "city", "is_major": True},
        
        # Odisha
        {"name": "Bhubaneswar", "state_code": "21", "type": "city", "is_major": True},
        {"name": "Cuttack", "state_code": "21", "type": "city", "is_major": True},
        
        # Bihar
        {"name": "Patna", "state_code": "10", "type": "city", "is_major": True},
        {"name": "Gaya", "state_code": "10", "type": "city", "is_major": False},
        
        # Jharkhand
        {"name": "Ranchi", "state_code": "20", "type": "city", "is_major": True},
        {"name": "Jamshedpur", "state_code": "20", "type": "city", "is_major": True},
        
        # Assam
        {"name": "Guwahati", "state_code": "18", "type": "city", "is_major": True},
        {"name": "Dibrugarh", "state_code": "18", "type": "city", "is_major": False},
        
        # Goa
        {"name": "Panaji", "state_code": "30", "type": "city", "is_major": True},
        {"name": "Margao", "state_code": "30", "type": "city", "is_major": False},
    ]
    
    # Create cities
    for city_data in major_cities:
        state = db.query(IndianState).filter(IndianState.state_code == city_data["state_code"]).first()
        if state:
            existing_city = db.query(IndianCity).filter(
                IndianCity.city_name == city_data["name"],
                IndianCity.state_id == state.id
            ).first()
            if not existing_city:
                city = IndianCity(
                    city_name=city_data["name"],
                    city_type=city_data["type"],
                    is_major_city=city_data["is_major"],
                    state_id=state.id,
                    is_active=True
                )
                db.add(city)
                db.commit()
                db.refresh(city)
                logger.info(f"Created city: {city_data['name']} in {state.state_name}")
    
    # Sample Pincodes for major cities
    sample_pincodes = [
        # Mumbai
        {"pincode": "400001", "area": "Fort", "city": "Mumbai", "state_code": "27"},
        {"pincode": "400002", "area": "Marine Lines", "city": "Mumbai", "state_code": "27"},
        {"pincode": "400003", "area": "Ballard Estate", "city": "Mumbai", "state_code": "27"},
        {"pincode": "400004", "area": "Cuffe Parade", "city": "Mumbai", "state_code": "27"},
        {"pincode": "400005", "area": "Worli", "city": "Mumbai", "state_code": "27"},
        
        # Delhi
        {"pincode": "110001", "area": "Connaught Place", "city": "New Delhi", "state_code": "07"},
        {"pincode": "110002", "area": "New Delhi", "city": "New Delhi", "state_code": "07"},
        {"pincode": "110003", "area": "India Gate", "city": "New Delhi", "state_code": "07"},
        
        # Bangalore
        {"pincode": "560001", "area": "Bangalore", "city": "Bangalore", "state_code": "29"},
        {"pincode": "560002", "area": "Bangalore", "city": "Bangalore", "state_code": "29"},
        {"pincode": "560003", "area": "Bangalore", "city": "Bangalore", "state_code": "29"},
        
        # Chennai
        {"pincode": "600001", "area": "Chennai", "city": "Chennai", "state_code": "33"},
        {"pincode": "600002", "area": "Chennai", "city": "Chennai", "state_code": "33"},
        {"pincode": "600003", "area": "Chennai", "city": "Chennai", "state_code": "33"},
        
        # Kolkata
        {"pincode": "700001", "area": "Kolkata", "city": "Kolkata", "state_code": "19"},
        {"pincode": "700002", "area": "Kolkata", "city": "Kolkata", "state_code": "19"},
        {"pincode": "700003", "area": "Kolkata", "city": "Kolkata", "state_code": "19"},
        
        # Ahmedabad
        {"pincode": "380001", "area": "Ahmedabad", "city": "Ahmedabad", "state_code": "24"},
        {"pincode": "380002", "area": "Ahmedabad", "city": "Ahmedabad", "state_code": "24"},
        {"pincode": "380003", "area": "Ahmedabad", "city": "Ahmedabad", "state_code": "24"},
    ]
    
    # Create pincodes
    for pincode_data in sample_pincodes:
        state = db.query(IndianState).filter(IndianState.state_code == pincode_data["state_code"]).first()
        city = db.query(IndianCity).filter(
            IndianCity.city_name == pincode_data["city"],
            IndianCity.state_id == state.id
        ).first()
        
        if state and city:
            existing_pincode = db.query(IndianPincode).filter(IndianPincode.pincode == pincode_data["pincode"]).first()
            if not existing_pincode:
                pincode = IndianPincode(
                    pincode=pincode_data["pincode"],
                    area_name=pincode_data["area"],
                    area_type="Post Office",
                    city_id=city.id,
                    state_id=state.id,
                    is_active=True
                )
                db.add(pincode)
                db.commit()
                logger.info(f"Created pincode: {pincode_data['pincode']} for {pincode_data['area']}")
    
    logger.info("Indian Geography Data initialization completed!")
    return True