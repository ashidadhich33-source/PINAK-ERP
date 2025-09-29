#!/usr/bin/env python3
"""
Process the uploaded pincode Excel file
This script will automatically detect and process your Excel file
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_excel_file():
    """Find the uploaded Excel file"""
    possible_names = [
        "pincode wise details.xlsx",
        "pincode_wise_details.xlsx", 
        "pincode-wise-details.xlsx",
        "pincode_details.xlsx",
        "pincodes.xlsx"
    ]
    
    # Check root directory
    for name in possible_names:
        file_path = Path(name)
        if file_path.exists():
            logger.info(f"✅ Found Excel file: {file_path}")
            return str(file_path)
    
    # Check data directory
    data_dir = Path("data")
    if data_dir.exists():
        for name in possible_names:
            file_path = data_dir / name
            if file_path.exists():
                logger.info(f"✅ Found Excel file: {file_path}")
                return str(file_path)
    
    logger.error("❌ Excel file not found!")
    logger.info("Please ensure your Excel file is named one of:")
    for name in possible_names:
        logger.info(f"  - {name}")
    
    return None

def process_excel_file():
    """Process the Excel file and set up the system"""
    logger.info("🚀 Starting Excel file processing...")
    
    # Find the Excel file
    excel_file = find_excel_file()
    if not excel_file:
        return False
    
    # Move to data directory if not already there
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    target_path = data_dir / "pincode wise details.xlsx"
    if not target_path.exists():
        import shutil
        shutil.copy2(excel_file, target_path)
        logger.info(f"📁 Copied Excel file to: {target_path}")
    
    # Run the processing script
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            "data/process_pincode_data.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Excel file processed successfully!")
            logger.info("📊 Processed data saved to data/processed/")
            return True
        else:
            logger.error(f"❌ Processing failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running processing script: {e}")
        return False

def setup_database_import():
    """Set up database import"""
    logger.info("🗄️ Setting up database import...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable,
            "data/import_to_database.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database import completed!")
            return True
        else:
            logger.error(f"❌ Database import failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running database import: {e}")
        return False

def main():
    """Main processing function"""
    logger.info("🎯 PINCODE EXCEL FILE PROCESSOR")
    logger.info("=" * 50)
    
    # Step 1: Find and process Excel file
    if not process_excel_file():
        logger.error("❌ Failed to process Excel file")
        return False
    
    # Step 2: Import to database
    logger.info("🔄 Importing processed data to database...")
    if not setup_database_import():
        logger.error("❌ Failed to import data to database")
        return False
    
    # Step 3: Verify setup
    logger.info("🔍 Verifying setup...")
    
    # Check if processed files exist
    processed_dir = Path("data/processed")
    required_files = [
        "pincodes.json",
        "pincode_lookup.json", 
        "city_lookup.json",
        "state_lookup.json",
        "area_lookup.json"
    ]
    
    all_files_exist = all((processed_dir / file).exists() for file in required_files)
    
    if all_files_exist:
        logger.info("✅ All processed files created successfully!")
        logger.info("🎉 PINCODE SYSTEM IS READY!")
        logger.info("")
        logger.info("📋 What's been set up:")
        logger.info("  ✅ Excel file processed")
        logger.info("  ✅ JSON data files created")
        logger.info("  ✅ Database import completed")
        logger.info("  ✅ API endpoints ready")
        logger.info("  ✅ Setup wizard enhanced")
        logger.info("")
        logger.info("🚀 Your ERP system now has complete pincode support!")
        logger.info("   - Company setup with pincode lookup")
        logger.info("   - Customer setup with pincode lookup") 
        logger.info("   - Supplier setup with pincode lookup")
        logger.info("   - Fast pincode search and validation")
        return True
    else:
        logger.error("❌ Some processed files are missing")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! Your pincode system is ready!")
        print("📱 You can now use the enhanced setup wizard with pincode lookup!")
    else:
        print("\n❌ FAILED! Please check the logs above for errors.")
        sys.exit(1)