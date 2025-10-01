# backend/app/services/core/excel_service.py
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ExcelService:
    """Service for Excel operations"""
    
    def __init__(self):
        pass
    
    def read_excel(self, file_path: str) -> Dict[str, Any]:
        """Read Excel file"""
        try:
            df = pd.read_excel(file_path)
            return {
                "success": True,
                "data": df.to_dict('records'),
                "columns": df.columns.tolist(),
                "rows": len(df)
            }
        except Exception as e:
            logger.error(f"Excel read failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def write_excel(self, data: List[Dict], file_path: str) -> Dict[str, Any]:
        """Write data to Excel file"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            return {
                "success": True,
                "file_path": file_path,
                "rows": len(df)
            }
        except Exception as e:
            logger.error(f"Excel write failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Create service instance
excel_service = ExcelService()