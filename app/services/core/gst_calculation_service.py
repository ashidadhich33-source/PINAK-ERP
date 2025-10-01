# backend/app/services/core/gst_calculation_service.py
from decimal import Decimal
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class GSTCalculationService:
    """Service for GST calculations"""
    
    def __init__(self):
        pass
    
    def calculate_gst(self, amount: Decimal, tax_rate: Decimal, is_interstate: bool = False) -> Dict[str, Any]:
        """Calculate GST for a given amount"""
        try:
            if is_interstate:
                # Interstate - IGST
                igst_amount = (amount * tax_rate) / 100
                cgst_amount = Decimal('0')
                sgst_amount = Decimal('0')
            else:
                # Intrastate - CGST + SGST
                half_rate = tax_rate / 2
                cgst_amount = (amount * half_rate) / 100
                sgst_amount = (amount * half_rate) / 100
                igst_amount = Decimal('0')
            
            total_gst = cgst_amount + sgst_amount + igst_amount
            total_amount = amount + total_gst
            
            return {
                "base_amount": float(amount),
                "tax_rate": float(tax_rate),
                "is_interstate": is_interstate,
                "cgst_amount": float(cgst_amount),
                "sgst_amount": float(sgst_amount),
                "igst_amount": float(igst_amount),
                "total_gst": float(total_gst),
                "total_amount": float(total_amount)
            }
        except Exception as e:
            logger.error(f"GST calculation failed: {e}")
            raise

# Create service instance
gst_calculation_service = GSTCalculationService()