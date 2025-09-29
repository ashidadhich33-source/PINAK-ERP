#!/usr/bin/env python3
"""
Process Pincode Data for Company, Customer, and Supplier Setup
This script processes the pincode Excel file and creates lookup APIs
"""

import pandas as pd
import json
import os
from pathlib import Path
import logging
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PincodeProcessor:
    """Process and manage pincode data for ERP system"""
    
    def __init__(self, excel_file_path: str):
        self.excel_file_path = excel_file_path
        self.data = None
        self.processed_data = {}
        
    def load_excel_data(self) -> bool:
        """Load data from Excel file"""
        try:
            if not os.path.exists(self.excel_file_path):
                logger.error(f"Excel file not found: {self.excel_file_path}")
                return False
                
            # Try different sheet names and formats
            sheet_names = ['Sheet1', 'Pincodes', 'Data', 'Details']
            df = None
            
            for sheet in sheet_names:
                try:
                    df = pd.read_excel(self.excel_file_path, sheet_name=sheet)
                    logger.info(f"Loaded data from sheet: {sheet}")
                    break
                except:
                    continue
            
            if df is None:
                # Try reading without sheet name
                df = pd.read_excel(self.excel_file_path)
                logger.info("Loaded data from default sheet")
            
            self.data = df
            logger.info(f"Successfully loaded {len(df)} records from Excel file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return False
    
    def analyze_data_structure(self) -> Dict:
        """Analyze the structure of the Excel data"""
        if self.data is None:
            return {}
        
        analysis = {
            "total_records": len(self.data),
            "columns": list(self.data.columns),
            "sample_data": self.data.head(3).to_dict('records'),
            "data_types": self.data.dtypes.to_dict(),
            "null_counts": self.data.isnull().sum().to_dict()
        }
        
        logger.info("📊 Data Structure Analysis:")
        logger.info(f"Total Records: {analysis['total_records']}")
        logger.info(f"Columns: {analysis['columns']}")
        logger.info(f"Data Types: {analysis['data_types']}")
        logger.info(f"Null Counts: {analysis['null_counts']}")
        
        return analysis
    
    def process_pincode_data(self) -> Dict:
        """Process pincode data for ERP system"""
        if self.data is None:
            return {}
        
        try:
            # Standardize column names (handle different naming conventions)
            column_mapping = {
                'pincode': ['pincode', 'pin_code', 'pin', 'postal_code', 'postalcode'],
                'area_name': ['area_name', 'area', 'locality', 'place', 'location'],
                'city_name': ['city_name', 'city', 'town', 'district'],
                'state_name': ['state_name', 'state', 'province'],
                'state_code': ['state_code', 'statecode', 'state_id'],
                'region': ['region', 'zone', 'division'],
                'latitude': ['latitude', 'lat', 'lat_coord'],
                'longitude': ['longitude', 'lng', 'lon', 'long', 'lng_coord']
            }
            
            # Map columns to standard names
            standardized_df = self.data.copy()
            for standard_name, possible_names in column_mapping.items():
                for col in self.data.columns:
                    if col.lower() in [name.lower() for name in possible_names]:
                        standardized_df[standard_name] = self.data[col]
                        break
            
            # Process the data
            processed_records = []
            for _, row in standardized_df.iterrows():
                record = {
                    "pincode": str(row.get('pincode', '')).strip(),
                    "area_name": str(row.get('area_name', '')).strip(),
                    "city_name": str(row.get('city_name', '')).strip(),
                    "state_name": str(row.get('state_name', '')).strip(),
                    "state_code": str(row.get('state_code', '')).strip(),
                    "region": str(row.get('region', '')).strip(),
                    "latitude": float(row.get('latitude', 0)) if pd.notna(row.get('latitude')) else None,
                    "longitude": float(row.get('longitude', 0)) if pd.notna(row.get('longitude')) else None,
                    "is_active": True
                }
                
                # Only add if pincode is valid
                if record["pincode"] and len(record["pincode"]) == 6 and record["pincode"].isdigit():
                    processed_records.append(record)
            
            # Create lookup structures
            self.processed_data = {
                "pincodes": processed_records,
                "pincode_lookup": {record["pincode"]: record for record in processed_records},
                "city_lookup": self._create_city_lookup(processed_records),
                "state_lookup": self._create_state_lookup(processed_records),
                "area_lookup": self._create_area_lookup(processed_records)
            }
            
            logger.info(f"✅ Processed {len(processed_records)} valid pincode records")
            return self.processed_data
            
        except Exception as e:
            logger.error(f"Error processing pincode data: {e}")
            return {}
    
    def _create_city_lookup(self, records: List[Dict]) -> Dict:
        """Create city-based lookup"""
        city_lookup = {}
        for record in records:
            city_key = f"{record['city_name']}_{record['state_name']}"
            if city_key not in city_lookup:
                city_lookup[city_key] = {
                    "city_name": record["city_name"],
                    "state_name": record["state_name"],
                    "state_code": record["state_code"],
                    "region": record["region"],
                    "pincodes": []
                }
            city_lookup[city_key]["pincodes"].append(record["pincode"])
        return city_lookup
    
    def _create_state_lookup(self, records: List[Dict]) -> Dict:
        """Create state-based lookup"""
        state_lookup = {}
        for record in records:
            state_key = record["state_name"]
            if state_key not in state_lookup:
                state_lookup[state_key] = {
                    "state_name": record["state_name"],
                    "state_code": record["state_code"],
                    "region": record["region"],
                    "cities": set(),
                    "pincodes": set()
                }
            state_lookup[state_key]["cities"].add(record["city_name"])
            state_lookup[state_key]["pincodes"].add(record["pincode"])
        
        # Convert sets to lists for JSON serialization
        for state_data in state_lookup.values():
            state_data["cities"] = list(state_data["cities"])
            state_data["pincodes"] = list(state_data["pincodes"])
        
        return state_lookup
    
    def _create_area_lookup(self, records: List[Dict]) -> Dict:
        """Create area-based lookup"""
        area_lookup = {}
        for record in records:
            area_key = f"{record['area_name']}_{record['city_name']}"
            if area_key not in area_lookup:
                area_lookup[area_key] = {
                    "area_name": record["area_name"],
                    "city_name": record["city_name"],
                    "state_name": record["state_name"],
                    "state_code": record["state_code"],
                    "pincode": record["pincode"],
                    "latitude": record["latitude"],
                    "longitude": record["longitude"]
                }
        return area_lookup
    
    def save_processed_data(self, output_dir: str) -> bool:
        """Save processed data to JSON files"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Save main pincode data
            with open(output_path / "pincodes.json", 'w', encoding='utf-8') as f:
                json.dump(self.processed_data["pincodes"], f, indent=2, ensure_ascii=False)
            
            # Save lookup data
            with open(output_path / "pincode_lookup.json", 'w', encoding='utf-8') as f:
                json.dump(self.processed_data["pincode_lookup"], f, indent=2, ensure_ascii=False)
            
            with open(output_path / "city_lookup.json", 'w', encoding='utf-8') as f:
                json.dump(self.processed_data["city_lookup"], f, indent=2, ensure_ascii=False)
            
            with open(output_path / "state_lookup.json", 'w', encoding='utf-8') as f:
                json.dump(self.processed_data["state_lookup"], f, indent=2, ensure_ascii=False)
            
            with open(output_path / "area_lookup.json", 'w', encoding='utf-8') as f:
                json.dump(self.processed_data["area_lookup"], f, indent=2, ensure_ascii=False)
            
            # Save combined data
            combined_data = {
                "metadata": {
                    "total_pincodes": len(self.processed_data["pincodes"]),
                    "total_cities": len(self.processed_data["city_lookup"]),
                    "total_states": len(self.processed_data["state_lookup"]),
                    "total_areas": len(self.processed_data["area_lookup"]),
                    "processed_at": pd.Timestamp.now().isoformat()
                },
                "data": self.processed_data
            }
            
            with open(output_path / "combined_pincode_data.json", 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Processed data saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            return False
    
    def generate_api_data(self) -> Dict:
        """Generate data structures for API endpoints"""
        api_data = {
            "search_endpoints": {
                "by_pincode": "GET /api/v1/pincodes/{pincode}",
                "by_city": "GET /api/v1/pincodes/city/{city_name}",
                "by_state": "GET /api/v1/pincodes/state/{state_name}",
                "by_area": "GET /api/v1/pincodes/area/{area_name}",
                "search": "GET /api/v1/pincodes/search?q={query}"
            },
            "lookup_endpoints": {
                "pincode_details": "GET /api/v1/pincodes/details/{pincode}",
                "city_pincodes": "GET /api/v1/pincodes/city/{city_name}/pincodes",
                "state_cities": "GET /api/v1/pincodes/state/{state_name}/cities",
                "nearby_pincodes": "GET /api/v1/pincodes/nearby?lat={lat}&lng={lng}&radius={km}"
            }
        }
        
        return api_data

def main():
    """Main processing function"""
    logger.info("🚀 Starting Pincode Data Processing...")
    
    # Look for the Excel file in common locations
    possible_locations = [
        "/workspace/pincode wise details.xlsx",
        "/workspace/pincode_wise_details.xlsx",
        "/workspace/data/pincode wise details.xlsx",
        "/workspace/data/geography/pincode wise details.xlsx"
    ]
    
    excel_file = None
    for location in possible_locations:
        if os.path.exists(location):
            excel_file = location
            break
    
    if not excel_file:
        logger.error("❌ Pincode Excel file not found!")
        logger.info("Please ensure the file is named 'pincode wise details.xlsx' and is in the workspace root")
        return False
    
    logger.info(f"📁 Found Excel file: {excel_file}")
    
    # Initialize processor
    processor = PincodeProcessor(excel_file)
    
    # Load and analyze data
    if not processor.load_excel_data():
        return False
    
    # Analyze data structure
    analysis = processor.analyze_data_structure()
    
    # Process data
    processed_data = processor.process_pincode_data()
    if not processed_data:
        return False
    
    # Save processed data
    output_dir = "/workspace/data/processed"
    if not processor.save_processed_data(output_dir):
        return False
    
    # Generate API data
    api_data = processor.generate_api_data()
    with open(f"{output_dir}/api_endpoints.json", 'w', encoding='utf-8') as f:
        json.dump(api_data, f, indent=2, ensure_ascii=False)
    
    logger.info("✅ Pincode data processing completed!")
    logger.info(f"📊 Processed {len(processed_data['pincodes'])} pincode records")
    logger.info(f"🏙️ Found {len(processed_data['city_lookup'])} cities")
    logger.info(f"🏛️ Found {len(processed_data['state_lookup'])} states")
    logger.info(f"📍 Found {len(processed_data['area_lookup'])} areas")
    
    return True

if __name__ == "__main__":
    main()