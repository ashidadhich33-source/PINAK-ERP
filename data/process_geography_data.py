#!/usr/bin/env python3
"""
Process Indian Geography Data from Excel Files
This script processes Excel files and imports them into the database
"""

import pandas as pd
import json
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_states_data(excel_file: str) -> list:
    """Process states data from Excel file"""
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded {len(df)} states from {excel_file}")
        
        states = []
        for _, row in df.iterrows():
            state = {
                "state_code": str(row.get('state_code', '')).zfill(2),
                "state_name": str(row.get('state_name', '')).strip(),
                "state_type": str(row.get('state_type', 'state')).strip(),
                "region": str(row.get('region', '')).strip(),
                "capital": str(row.get('capital', '')).strip(),
                "gst_state_code": str(row.get('state_code', '')).zfill(2),
                "gst_state_name": str(row.get('state_name', '')).strip(),
                "is_active": True
            }
            states.append(state)
        
        return states
    except Exception as e:
        logger.error(f"Error processing states data: {e}")
        return []

def process_cities_data(excel_file: str) -> list:
    """Process cities data from Excel file"""
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded {len(df)} cities from {excel_file}")
        
        cities = []
        for _, row in df.iterrows():
            city = {
                "city_name": str(row.get('city_name', '')).strip(),
                "state_code": str(row.get('state_code', '')).zfill(2),
                "city_type": str(row.get('city_type', 'city')).strip(),
                "is_major_city": bool(row.get('is_major_city', False)),
                "latitude": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
                "longitude": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
                "is_active": True
            }
            cities.append(city)
        
        return cities
    except Exception as e:
        logger.error(f"Error processing cities data: {e}")
        return []

def process_pincodes_data(excel_file: str) -> list:
    """Process pincodes data from Excel file"""
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"Loaded {len(df)} pincodes from {excel_file}")
        
        pincodes = []
        for _, row in df.iterrows():
            pincode = {
                "pincode": str(row.get('pincode', '')).strip(),
                "area_name": str(row.get('area_name', '')).strip(),
                "city_name": str(row.get('city_name', '')).strip(),
                "state_code": str(row.get('state_code', '')).zfill(2),
                "area_type": str(row.get('area_type', 'Post Office')).strip(),
                "latitude": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
                "longitude": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
                "is_active": True
            }
            pincodes.append(pincode)
        
        return pincodes
    except Exception as e:
        logger.error(f"Error processing pincodes data: {e}")
        return []

def validate_data(states: list, cities: list, pincodes: list) -> dict:
    """Validate the processed data"""
    validation_results = {
        "states": {
            "count": len(states),
            "valid": 0,
            "invalid": 0,
            "errors": []
        },
        "cities": {
            "count": len(cities),
            "valid": 0,
            "invalid": 0,
            "errors": []
        },
        "pincodes": {
            "count": len(pincodes),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
    }
    
    # Validate states
    for state in states:
        if state.get('state_code') and state.get('state_name'):
            validation_results["states"]["valid"] += 1
        else:
            validation_results["states"]["invalid"] += 1
            validation_results["states"]["errors"].append(f"Invalid state: {state}")
    
    # Validate cities
    for city in cities:
        if city.get('city_name') and city.get('state_code'):
            validation_results["cities"]["valid"] += 1
        else:
            validation_results["cities"]["invalid"] += 1
            validation_results["cities"]["errors"].append(f"Invalid city: {city}")
    
    # Validate pincodes
    for pincode in pincodes:
        if pincode.get('pincode') and pincode.get('area_name'):
            validation_results["pincodes"]["valid"] += 1
        else:
            validation_results["pincodes"]["invalid"] += 1
            validation_results["pincodes"]["errors"].append(f"Invalid pincode: {pincode}")
    
    return validation_results

def save_processed_data(states: list, cities: list, pincodes: list, output_dir: str):
    """Save processed data to JSON files"""
    try:
        # Save states
        with open(f"{output_dir}/states.json", 'w', encoding='utf-8') as f:
            json.dump(states, f, indent=2, ensure_ascii=False)
        
        # Save cities
        with open(f"{output_dir}/cities.json", 'w', encoding='utf-8') as f:
            json.dump(cities, f, indent=2, ensure_ascii=False)
        
        # Save pincodes
        with open(f"{output_dir}/pincodes.json", 'w', encoding='utf-8') as f:
            json.dump(pincodes, f, indent=2, ensure_ascii=False)
        
        # Save combined data
        combined_data = {
            "states": states,
            "cities": cities,
            "pincodes": pincodes,
            "metadata": {
                "total_states": len(states),
                "total_cities": len(cities),
                "total_pincodes": len(pincodes),
                "processed_at": pd.Timestamp.now().isoformat()
            }
        }
        
        with open(f"{output_dir}/combined_geography.json", 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed data saved to {output_dir}")
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")

def main():
    """Main processing function"""
    logger.info("🚀 Starting Indian Geography Data Processing...")
    
    # Define paths
    data_dir = Path(__file__).parent
    geography_dir = data_dir / "geography"
    processed_dir = data_dir / "processed"
    
    # Ensure processed directory exists
    processed_dir.mkdir(exist_ok=True)
    
    # Process states
    states_file = geography_dir / "indian_states.xlsx"
    if states_file.exists():
        states = process_states_data(str(states_file))
    else:
        logger.warning(f"States file not found: {states_file}")
        states = []
    
    # Process cities
    cities_file = geography_dir / "indian_cities.xlsx"
    if cities_file.exists():
        cities = process_cities_data(str(cities_file))
    else:
        logger.warning(f"Cities file not found: {cities_file}")
        cities = []
    
    # Process pincodes
    pincodes_file = geography_dir / "indian_pincodes.xlsx"
    if pincodes_file.exists():
        pincodes = process_pincodes_data(str(pincodes_file))
    else:
        logger.warning(f"Pincodes file not found: {pincodes_file}")
        pincodes = []
    
    # Validate data
    validation_results = validate_data(states, cities, pincodes)
    
    # Print validation results
    logger.info("📊 Validation Results:")
    logger.info(f"States: {validation_results['states']['valid']}/{validation_results['states']['count']} valid")
    logger.info(f"Cities: {validation_results['cities']['valid']}/{validation_results['cities']['count']} valid")
    logger.info(f"Pincodes: {validation_results['pincodes']['valid']}/{validation_results['pincodes']['count']} valid")
    
    # Save processed data
    save_processed_data(states, cities, pincodes, str(processed_dir))
    
    # Save validation results
    with open(f"{processed_dir}/validation_results.json", 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)
    
    logger.info("✅ Data processing completed!")
    logger.info(f"📁 Processed files saved to: {processed_dir}")
    
    return {
        "states": len(states),
        "cities": len(cities),
        "pincodes": len(pincodes),
        "validation": validation_results
    }

if __name__ == "__main__":
    main()