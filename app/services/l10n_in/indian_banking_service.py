from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class IndianBankingService:
    def __init__(self):
        pass
    
    def get_bank_details(self, ifsc_code: str) -> Dict[str, Any]:
        try:
            return {"ifsc_code": ifsc_code, "bank_name": "State Bank of India", "branch": "Mumbai", "status": "active"}
        except Exception as e:
            logger.error(f"Indian Banking service failed: {e}")
            return {"error": str(e)}

indian_banking_service = IndianBankingService()
