from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self):
        pass
    
    def get_stock(self, item_id: int) -> Dict[str, Any]:
        try:
            return {"item_id": item_id, "quantity": 100, "status": "in_stock"}
        except Exception as e:
            logger.error(f"Stock service failed: {e}")
            return {"error": str(e)}

stock_service = StockService()
