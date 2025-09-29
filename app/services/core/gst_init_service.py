# backend/app/services/gst_init_service.py
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from decimal import Decimal
import logging

from ..models.core import GSTStateCode
from ..models.core import GSTSlab

logger = logging.getLogger(__name__)

class GSTInitService:
    """Service class for GST system initialization"""
    
    def __init__(self):
        pass
    
    def initialize_gst_state_codes(self, db: Session):
        """Initialize GST state codes in database"""
        
        # Check if state codes already exist
        existing_count = db.query(GSTStateCode).count()
        if existing_count > 0:
            logger.info("GST state codes already initialized")
            return
        
        state_codes = [
            {"code": "01", "name": "Jammu and Kashmir"},
            {"code": "02", "name": "Himachal Pradesh"},
            {"code": "03", "name": "Punjab"},
            {"code": "04", "name": "Chandigarh"},
            {"code": "05", "name": "Uttarakhand"},
            {"code": "06", "name": "Haryana"},
            {"code": "07", "name": "Delhi"},
            {"code": "08", "name": "Rajasthan"},
            {"code": "09", "name": "Uttar Pradesh"},
            {"code": "10", "name": "Bihar"},
            {"code": "11", "name": "Sikkim"},
            {"code": "12", "name": "Arunachal Pradesh"},
            {"code": "13", "name": "Nagaland"},
            {"code": "14", "name": "Manipur"},
            {"code": "15", "name": "Mizoram"},
            {"code": "16", "name": "Tripura"},
            {"code": "17", "name": "Meghalaya"},
            {"code": "18", "name": "Assam"},
            {"code": "19", "name": "West Bengal"},
            {"code": "20", "name": "Jharkhand"},
            {"code": "21", "name": "Odisha"},
            {"code": "22", "name": "Chhattisgarh"},
            {"code": "23", "name": "Madhya Pradesh"},
            {"code": "24", "name": "Gujarat"},
            {"code": "25", "name": "Daman and Diu"},
            {"code": "26", "name": "Dadra and Nagar Haveli"},
            {"code": "27", "name": "Maharashtra"},
            {"code": "28", "name": "Andhra Pradesh"},
            {"code": "29", "name": "Karnataka"},
            {"code": "30", "name": "Goa"},
            {"code": "31", "name": "Lakshadweep"},
            {"code": "32", "name": "Kerala"},
            {"code": "33", "name": "Tamil Nadu"},
            {"code": "34", "name": "Puducherry"},
            {"code": "35", "name": "Andaman and Nicobar Islands"},
            {"code": "36", "name": "Telangana"},
            {"code": "37", "name": "Andhra Pradesh (New)"}
        ]
        
        for state_data in state_codes:
            state_code = GSTStateCode(
                code=state_data["code"],
                name=state_data["name"],
                is_active=True
            )
            db.add(state_code)
        
        db.commit()
        logger.info("GST state codes initialized successfully")
    
    def create_default_gst_slabs_for_company(
        self, 
        db: Session, 
        company_id: int, 
        user_id: int
    ):
        """Create default GST slabs for a company"""
        
        # Check if GST slabs already exist for this company
        existing_slabs = db.query(GSTSlab).filter(
            GSTSlab.company_id == company_id
        ).count()
        
        if existing_slabs > 0:
            logger.info(f"GST slabs already exist for company {company_id}")
            return
        
        default_slabs = [
            {
                "rate": Decimal('0.00'),
                "cgst_rate": Decimal('0.00'),
                "sgst_rate": Decimal('0.00'),
                "igst_rate": Decimal('0.00'),
                "description": "0% GST - Exempted",
                "is_default": True
            },
            {
                "rate": Decimal('5.00'),
                "cgst_rate": Decimal('2.50'),
                "sgst_rate": Decimal('2.50'),
                "igst_rate": Decimal('5.00'),
                "description": "5% GST - Essential items",
                "is_default": False
            },
            {
                "rate": Decimal('12.00'),
                "cgst_rate": Decimal('6.00'),
                "sgst_rate": Decimal('6.00'),
                "igst_rate": Decimal('12.00'),
                "description": "12% GST - Standard rate",
                "is_default": False
            },
            {
                "rate": Decimal('18.00'),
                "cgst_rate": Decimal('9.00'),
                "sgst_rate": Decimal('9.00'),
                "igst_rate": Decimal('18.00'),
                "description": "18% GST - Standard rate",
                "is_default": True
            },
            {
                "rate": Decimal('28.00'),
                "cgst_rate": Decimal('14.00'),
                "sgst_rate": Decimal('14.00'),
                "igst_rate": Decimal('28.00'),
                "description": "28% GST - Luxury items",
                "is_default": False
            }
        ]
        
        for slab_data in default_slabs:
            gst_slab = GSTSlab(
                company_id=company_id,
                effective_from=date.today(),
                **slab_data,
                created_by=user_id
            )
            db.add(gst_slab)
        
        db.commit()
        logger.info(f"Default GST slabs created for company {company_id}")
    
    def update_gst_slabs_for_rate_change(
        self, 
        db: Session, 
        company_id: int,
        old_rate: Decimal,
        new_rate: Decimal,
        effective_date: date,
        user_id: int
    ):
        """Update GST slabs when rates change"""
        
        # Deactivate old slabs
        old_slabs = db.query(GSTSlab).filter(
            GSTSlab.company_id == company_id,
            GSTSlab.rate == old_rate,
            GSTSlab.is_active == True
        ).all()
        
        for slab in old_slabs:
            slab.effective_to = effective_date
            slab.is_active = False
            slab.updated_by = user_id
        
        # Create new slabs
        new_slab = GSTSlab(
            company_id=company_id,
            rate=new_rate,
            cgst_rate=new_rate / 2,
            sgst_rate=new_rate / 2,
            igst_rate=new_rate,
            effective_from=effective_date,
            description=f"{new_rate}% GST - Updated rate",
            created_by=user_id
        )
        
        db.add(new_slab)
        db.commit()
        
        logger.info(f"GST slabs updated for company {company_id}: {old_rate}% -> {new_rate}%")
    
    def get_gst_compliance_checklist(self) -> List[Dict]:
        """Get GST compliance checklist"""
        
        return [
            {
                "item": "GST Registration",
                "description": "Ensure GST registration is valid and active",
                "mandatory": True,
                "frequency": "Annual"
            },
            {
                "item": "GST Returns Filing",
                "description": "File GSTR-1, GSTR-3B, and GSTR-9 on time",
                "mandatory": True,
                "frequency": "Monthly/Annual"
            },
            {
                "item": "GST Payment",
                "description": "Pay GST liability within due dates",
                "mandatory": True,
                "frequency": "Monthly"
            },
            {
                "item": "E-Invoicing",
                "description": "Generate e-invoices for B2B transactions above threshold",
                "mandatory": True,
                "frequency": "Per Transaction"
            },
            {
                "item": "E-Way Bill",
                "description": "Generate e-way bills for goods movement above threshold",
                "mandatory": True,
                "frequency": "Per Movement"
            },
            {
                "item": "GST Reconciliation",
                "description": "Reconcile books with GST returns",
                "mandatory": True,
                "frequency": "Monthly"
            },
            {
                "item": "GST Audit",
                "description": "Conduct GST audit if turnover exceeds threshold",
                "mandatory": True,
                "frequency": "Annual"
            },
            {
                "item": "Documentation",
                "description": "Maintain proper GST documentation and records",
                "mandatory": True,
                "frequency": "Continuous"
            }
        ]
    
    def get_gst_filing_due_dates(self, month: int, year: int) -> List[Dict]:
        """Get GST filing due dates for a month"""
        
        due_dates = [
            {
                "form": "GSTR-1",
                "description": "Outward supplies return",
                "due_date": f"{year}-{month:02d}-11",
                "late_fee": "₹200 per day (max ₹10,000)",
                "mandatory": True
            },
            {
                "form": "GSTR-3B",
                "description": "Monthly summary return",
                "due_date": f"{year}-{month:02d}-20",
                "late_fee": "₹200 per day (max ₹10,000)",
                "mandatory": True
            },
            {
                "form": "GSTR-2A",
                "description": "Auto-populated purchase return",
                "due_date": f"{year}-{month:02d}-15",
                "late_fee": "N/A",
                "mandatory": False
            },
            {
                "form": "GSTR-2B",
                "description": "Static purchase return",
                "due_date": f"{year}-{month:02d}-14",
                "late_fee": "N/A",
                "mandatory": False
            }
        ]
        
        return due_dates

# Global service instance
gst_init_service = GSTInitService()