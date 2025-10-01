from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class IndianGeographyService:
    def __init__(self):
        pass
    
    def get_states(self) -> Dict[str, Any]:
        try:
            return {"states": ["Maharashtra", "Gujarat", "Karnataka"], "status": "active"}
        except Exception as e:
            logger.error(f"Indian Geography service failed: {e}")
            return {"error": str(e)}

indian_geography_service = IndianGeographyService()
