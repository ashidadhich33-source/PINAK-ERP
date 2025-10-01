from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class CompanyService:
    def __init__(self):
        pass
    
    def get_company(self, company_id: int) -> Dict[str, Any]:
        try:
            return {"id": company_id, "name": "Sample Company", "status": "active"}
        except Exception as e:
            logger.error(f"Company service failed: {e}")
            return {"error": str(e)}

company_service = CompanyService()
