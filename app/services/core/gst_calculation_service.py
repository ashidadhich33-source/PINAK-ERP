# backend/app/services/gst_calculation_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
import logging

from ..models.core import Company, GSTSlab
from ..models.sales import SalesInvoice, SalesInvoiceItem
from ..models.purchase import PurchaseBill, PurchaseBillItem

logger = logging.getLogger(__name__)

class GSTCalculationService:
    """Service class for GST calculations and compliance"""
    
    def __init__(self):
        self.round_off = Decimal('0.01')
    
    def calculate_gst(
        self, 
        db: Session, 
        company_id: int,
        amount: Decimal, 
        gst_rate: Decimal,
        gst_type: str = "cgst_sgst",  # cgst_sgst or igst
        state_code: str = None
    ) -> Dict[str, Decimal]:
        """
        Calculate GST for given amount and rate
        
        Args:
            db: Database session
            company_id: Company ID
            amount: Base amount (excluding GST)
            gst_rate: GST rate percentage
            gst_type: Type of GST (cgst_sgst or igst)
            state_code: State code for interstate transactions
        
        Returns:
            Dict with GST breakdown
        """
        
        # Get company state code if not provided
        if not state_code:
            company = db.query(Company).filter(Company.id == company_id).first()
            state_code = company.gst_state_code if company else None
        
        # Calculate GST amount
        gst_amount = (amount * gst_rate / 100).quantize(self.round_off, rounding=ROUND_HALF_UP)
        
        result = {
            "base_amount": amount,
            "gst_rate": gst_rate,
            "gst_amount": gst_amount,
            "total_amount": amount + gst_amount,
            "gst_type": gst_type
        }
        
        if gst_type == "cgst_sgst":
            # For intrastate transactions (CGST + SGST)
            cgst_rate = gst_rate / 2
            sgst_rate = gst_rate / 2
            cgst_amount = (amount * cgst_rate / 100).quantize(self.round_off, rounding=ROUND_HALF_UP)
            sgst_amount = (amount * sgst_rate / 100).quantize(self.round_off, rounding=ROUND_HALF_UP)
            
            result.update({
                "cgst_rate": cgst_rate,
                "sgst_rate": sgst_rate,
                "cgst_amount": cgst_amount,
                "sgst_amount": sgst_amount,
                "igst_rate": Decimal('0'),
                "igst_amount": Decimal('0')
            })
        else:
            # For interstate transactions (IGST)
            result.update({
                "cgst_rate": Decimal('0'),
                "sgst_rate": Decimal('0'),
                "cgst_amount": Decimal('0'),
                "sgst_amount": Decimal('0'),
                "igst_rate": gst_rate,
                "igst_amount": gst_amount
            })
        
        return result
    
    def calculate_invoice_gst(
        self, 
        db: Session, 
        company_id: int,
        invoice_items: List[Dict],
        customer_state_code: str = None
    ) -> Dict[str, Decimal]:
        """
        Calculate GST for entire invoice
        
        Args:
            db: Database session
            company_id: Company ID
            invoice_items: List of invoice items with amount and gst_rate
            customer_state_code: Customer's state code
        
        Returns:
            Dict with invoice GST breakdown
        """
        
        # Get company state code
        company = db.query(Company).filter(Company.id == company_id).first()
        company_state_code = company.gst_state_code if company else None
        
        # Determine GST type based on state codes
        is_interstate = (company_state_code != customer_state_code)
        gst_type = "igst" if is_interstate else "cgst_sgst"
        
        # Group items by GST rate
        gst_groups = {}
        for item in invoice_items:
            gst_rate = Decimal(str(item.get('gst_rate', 0)))
            if gst_rate not in gst_groups:
                gst_groups[gst_rate] = []
            gst_groups[gst_rate].append(item)
        
        # Calculate GST for each group
        total_base_amount = Decimal('0')
        total_gst_amount = Decimal('0')
        total_cgst_amount = Decimal('0')
        total_sgst_amount = Decimal('0')
        total_igst_amount = Decimal('0')
        
        gst_breakdown = []
        
        for gst_rate, items in gst_groups.items():
            group_amount = sum(Decimal(str(item.get('amount', 0))) for item in items)
            group_gst = self.calculate_gst(
                db, company_id, group_amount, gst_rate, gst_type, customer_state_code
            )
            
            gst_breakdown.append({
                "gst_rate": gst_rate,
                "base_amount": group_amount,
                "gst_amount": group_gst['gst_amount'],
                "cgst_amount": group_gst['cgst_amount'],
                "sgst_amount": group_gst['sgst_amount'],
                "igst_amount": group_gst['igst_amount']
            })
            
            total_base_amount += group_amount
            total_gst_amount += group_gst['gst_amount']
            total_cgst_amount += group_gst['cgst_amount']
            total_sgst_amount += group_gst['sgst_amount']
            total_igst_amount += group_gst['igst_amount']
        
        return {
            "gst_type": gst_type,
            "is_interstate": is_interstate,
            "total_base_amount": total_base_amount,
            "total_gst_amount": total_gst_amount,
            "total_cgst_amount": total_cgst_amount,
            "total_sgst_amount": total_sgst_amount,
            "total_igst_amount": total_igst_amount,
            "total_amount": total_base_amount + total_gst_amount,
            "gst_breakdown": gst_breakdown
        }
    
    def get_gst_slab_by_rate(
        self, 
        db: Session, 
        company_id: int, 
        gst_rate: Decimal,
        effective_date: date = None
    ) -> Optional[GSTSlab]:
        """Get GST slab by rate for company"""
        
        if effective_date is None:
            effective_date = date.today()
        
        gst_slab = db.query(GSTSlab).filter(
            GSTSlab.company_id == company_id,
            GSTSlab.rate == gst_rate,
            GSTSlab.effective_from <= effective_date,
            or_(
                GSTSlab.effective_to.is_(None),
                GSTSlab.effective_to >= effective_date
            ),
            GSTSlab.is_active == True
        ).first()
        
        return gst_slab
    
    def get_available_gst_rates(
        self, 
        db: Session, 
        company_id: int,
        effective_date: date = None
    ) -> List[Dict]:
        """Get all available GST rates for company"""
        
        if effective_date is None:
            effective_date = date.today()
        
        gst_slabs = db.query(GSTSlab).filter(
            GSTSlab.company_id == company_id,
            GSTSlab.effective_from <= effective_date,
            or_(
                GSTSlab.effective_to.is_(None),
                GSTSlab.effective_to >= effective_date
            ),
            GSTSlab.is_active == True
        ).order_by(GSTSlab.rate).all()
        
        return [
            {
                "id": slab.id,
                "rate": slab.rate,
                "cgst_rate": slab.cgst_rate,
                "sgst_rate": slab.sgst_rate,
                "igst_rate": slab.igst_rate,
                "description": slab.description,
                "is_default": slab.is_default
            }
            for slab in gst_slabs
        ]
    
    def calculate_gst_liability(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict[str, Decimal]:
        """Calculate GST liability for a period"""
        
        # Get sales GST
        sales_gst = db.query(
            func.sum(SalesInvoiceItem.cgst_amount).label('total_cgst'),
            func.sum(SalesInvoiceItem.sgst_amount).label('total_sgst'),
            func.sum(SalesInvoiceItem.igst_amount).label('total_igst')
        ).join(
            SalesInvoice, SalesInvoiceItem.invoice_id == SalesInvoice.id
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= from_date,
            SalesInvoice.invoice_date <= to_date,
            SalesInvoice.status != 'cancelled'
        ).first()
        
        # Get purchase GST (input credit)
        purchase_gst = db.query(
            func.sum(PurchaseBillItem.cgst_amount).label('total_cgst'),
            func.sum(PurchaseBillItem.sgst_amount).label('total_sgst'),
            func.sum(PurchaseBillItem.igst_amount).label('total_igst')
        ).join(
            PurchaseBill, PurchaseBillItem.bill_id == PurchaseBill.id
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= from_date,
            PurchaseBill.bill_date <= to_date,
            PurchaseBill.status != 'cancelled'
        ).first()
        
        # Calculate net GST liability
        sales_cgst = sales_gst.total_cgst or Decimal('0')
        sales_sgst = sales_gst.total_sgst or Decimal('0')
        sales_igst = sales_gst.total_igst or Decimal('0')
        
        purchase_cgst = purchase_gst.total_cgst or Decimal('0')
        purchase_sgst = purchase_gst.total_sgst or Decimal('0')
        purchase_igst = purchase_gst.total_igst or Decimal('0')
        
        net_cgst = sales_cgst - purchase_cgst
        net_sgst = sales_sgst - purchase_sgst
        net_igst = sales_igst - purchase_igst
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "sales_gst": {
                "cgst": sales_cgst,
                "sgst": sales_sgst,
                "igst": sales_igst,
                "total": sales_cgst + sales_sgst + sales_igst
            },
            "purchase_gst": {
                "cgst": purchase_cgst,
                "sgst": purchase_sgst,
                "igst": purchase_igst,
                "total": purchase_cgst + purchase_sgst + purchase_igst
            },
            "net_liability": {
                "cgst": net_cgst,
                "sgst": net_sgst,
                "igst": net_igst,
                "total": net_cgst + net_sgst + net_igst
            }
        }
    
    def generate_gst_return_data(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate GST return data (GSTR-1 format)"""
        
        # Get company details
        company = db.query(Company).filter(Company.id == company_id).first()
        
        # Get sales data
        sales_data = db.query(
            SalesInvoice.invoice_number,
            SalesInvoice.invoice_date,
            SalesInvoice.customer_gst,
            SalesInvoice.customer_name,
            func.sum(SalesInvoiceItem.line_total).label('total_amount'),
            func.sum(SalesInvoiceItem.cgst_amount).label('cgst_amount'),
            func.sum(SalesInvoiceItem.sgst_amount).label('sgst_amount'),
            func.sum(SalesInvoiceItem.igst_amount).label('igst_amount')
        ).join(
            SalesInvoiceItem, SalesInvoice.id == SalesInvoiceItem.invoice_id
        ).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= from_date,
            SalesInvoice.invoice_date <= to_date,
            SalesInvoice.status != 'cancelled'
        ).group_by(
            SalesInvoice.id
        ).all()
        
        # Get purchase data
        purchase_data = db.query(
            PurchaseBill.bill_number,
            PurchaseBill.bill_date,
            PurchaseBill.supplier_gst,
            PurchaseBill.supplier_name,
            func.sum(PurchaseBillItem.line_total).label('total_amount'),
            func.sum(PurchaseBillItem.cgst_amount).label('cgst_amount'),
            func.sum(PurchaseBillItem.sgst_amount).label('sgst_amount'),
            func.sum(PurchaseBillItem.igst_amount).label('igst_amount')
        ).join(
            PurchaseBillItem, PurchaseBill.id == PurchaseBillItem.bill_id
        ).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= from_date,
            PurchaseBill.bill_date <= to_date,
            PurchaseBill.status != 'cancelled'
        ).group_by(
            PurchaseBill.id
        ).all()
        
        return {
            "company_details": {
                "gst_number": company.gst_number,
                "company_name": company.name,
                "period": f"{from_date} to {to_date}"
            },
            "sales_data": [
                {
                    "invoice_number": sale.invoice_number,
                    "invoice_date": sale.invoice_date,
                    "customer_gst": sale.customer_gst,
                    "customer_name": sale.customer_name,
                    "total_amount": sale.total_amount,
                    "cgst_amount": sale.cgst_amount,
                    "sgst_amount": sale.sgst_amount,
                    "igst_amount": sale.igst_amount
                }
                for sale in sales_data
            ],
            "purchase_data": [
                {
                    "bill_number": purchase.bill_number,
                    "bill_date": purchase.bill_date,
                    "supplier_gst": purchase.supplier_gst,
                    "supplier_name": purchase.supplier_name,
                    "total_amount": purchase.total_amount,
                    "cgst_amount": purchase.cgst_amount,
                    "sgst_amount": purchase.sgst_amount,
                    "igst_amount": purchase.igst_amount
                }
                for purchase in purchase_data
            ]
        }
    
    def validate_gst_number(self, gst_number: str) -> bool:
        """Validate GST number format"""
        if not gst_number or len(gst_number) != 15:
            return False
        
        # GST number format: 2 digits state code + 10 digits PAN + 1 digit entity number + 1 digit Z + 1 digit checksum
        try:
            state_code = gst_number[:2]
            pan_number = gst_number[2:12]
            entity_number = gst_number[12:13]
            z_char = gst_number[13:14]
            checksum = gst_number[14:15]
            
            # Basic validation
            if not state_code.isdigit() or not pan_number.isalnum() or not entity_number.isdigit():
                return False
            
            if z_char != 'Z':
                return False
            
            # TODO: Add checksum validation
            return True
            
        except:
            return False
    
    def get_gst_state_codes(self) -> List[Dict]:
        """Get list of GST state codes"""
        return [
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

# Global service instance
gst_calculation_service = GSTCalculationService()