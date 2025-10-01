# backend/app/services/core/gst_service.py
from decimal import Decimal
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class GSTService:
    """Service for GST calculations and management"""
    
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
    
    def get_gst_slabs(self, db: Session, company_id: int) -> List[Dict[str, Any]]:
        """Get GST slabs for a company"""
        try:
            # This would query the actual GST slabs from database
            # For now, return default GST slabs
            return [
                {
                    "id": 1,
                    "rate": 0.00,
                    "cgst_rate": 0.00,
                    "sgst_rate": 0.00,
                    "igst_rate": 0.00,
                    "description": "0% GST",
                    "is_active": True
                },
                {
                    "id": 2,
                    "rate": 5.00,
                    "cgst_rate": 2.50,
                    "sgst_rate": 2.50,
                    "igst_rate": 5.00,
                    "description": "5% GST",
                    "is_active": True
                },
                {
                    "id": 3,
                    "rate": 12.00,
                    "cgst_rate": 6.00,
                    "sgst_rate": 6.00,
                    "igst_rate": 12.00,
                    "description": "12% GST",
                    "is_active": True
                },
                {
                    "id": 4,
                    "rate": 18.00,
                    "cgst_rate": 9.00,
                    "sgst_rate": 9.00,
                    "igst_rate": 18.00,
                    "description": "18% GST",
                    "is_active": True
                },
                {
                    "id": 5,
                    "rate": 28.00,
                    "cgst_rate": 14.00,
                    "sgst_rate": 14.00,
                    "igst_rate": 28.00,
                    "description": "28% GST",
                    "is_active": True
                }
            ]
        except Exception as e:
            logger.error(f"Failed to get GST slabs: {e}")
            raise
    
    def create_gst_slab(self, db: Session, company_id: int, rate: Decimal, cgst_rate: Decimal, 
                       sgst_rate: Decimal, igst_rate: Decimal, description: str, created_by: int) -> Dict[str, Any]:
        """Create a new GST slab"""
        try:
            # This would create the actual GST slab in database
            # For now, return a sample response
            return {
                "id": 1,
                "rate": float(rate),
                "cgst_rate": float(cgst_rate),
                "sgst_rate": float(sgst_rate),
                "igst_rate": float(igst_rate),
                "description": description,
                "is_active": True
            }
        except Exception as e:
            logger.error(f"Failed to create GST slab: {e}")
            raise
    
    def get_gst_reports(self, db: Session, company_id: int, start_date: str, end_date: str, report_type: str) -> Dict[str, Any]:
        """Get GST reports"""
        try:
            # This would generate the actual GST reports
            # For now, return a sample response
            return {
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "total_sales": 100000.00,
                "total_gst": 18000.00,
                "cgst": 9000.00,
                "sgst": 9000.00,
                "igst": 0.00
            }
        except Exception as e:
            logger.error(f"Failed to get GST reports: {e}")
            raise
    
    def get_gst_returns(self, db: Session, company_id: int, return_period: str) -> Dict[str, Any]:
        """Get GST returns data"""
        try:
            # This would generate the actual GST returns data
            # For now, return a sample response
            return {
                "return_period": return_period,
                "total_sales": 100000.00,
                "total_purchases": 75000.00,
                "gst_payable": 18000.00,
                "gst_credit": 13500.00,
                "net_gst_payable": 4500.00
            }
        except Exception as e:
            logger.error(f"Failed to get GST returns: {e}")
            raise

# Create service instance
gst_service = GSTService()