# backend/app/services/l10n_in/gst_service.py
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

from ...models.l10n_in import (
    GSTSlab, HSNCode, SACCode, GSTStateCode, PlaceOfSupply, 
    GSTRegistration, ReverseCharge, GSTTaxType, PlaceOfSupplyType
)
from ...models.core import Company
from ...models.sales import SalesInvoice, SalesInvoiceItem
from ...models.purchase import PurchaseInvoice, PurchaseInvoiceItem

logger = logging.getLogger(__name__)

class IndianGSTService:
    """Service for Indian GST compliance and calculations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_gst(
        self,
        db: Session,
        company_id: int,
        taxable_amount: Decimal,
        supplier_state_code: str,
        recipient_state_code: str,
        gst_rate: Decimal,
        hsn_code: Optional[str] = None,
        sac_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate GST based on place of supply and rates"""
        
        try:
            # Determine place of supply
            place_of_supply = self._determine_place_of_supply(
                db, company_id, supplier_state_code, recipient_state_code
            )
            
            # Calculate GST components
            if place_of_supply == PlaceOfSupplyType.INTRA_STATE:
                # Intra-state: CGST + SGST
                cgst_rate = gst_rate / 2
                sgst_rate = gst_rate / 2
                cgst_amount = (taxable_amount * cgst_rate) / 100
                sgst_amount = (taxable_amount * sgst_rate) / 100
                igst_amount = Decimal('0')
                
            elif place_of_supply == PlaceOfSupplyType.INTER_STATE:
                # Inter-state: IGST
                cgst_rate = Decimal('0')
                sgst_rate = Decimal('0')
                cgst_amount = Decimal('0')
                sgst_amount = Decimal('0')
                igst_amount = (taxable_amount * gst_rate) / 100
                
            else:
                # Export/Import: IGST
                cgst_rate = Decimal('0')
                sgst_rate = Decimal('0')
                cgst_amount = Decimal('0')
                sgst_amount = Decimal('0')
                igst_amount = (taxable_amount * gst_rate) / 100
            
            # Calculate CESS if applicable
            cess_rate, cess_amount = self._calculate_cess(
                db, company_id, hsn_code, sac_code, taxable_amount
            )
            
            total_gst_amount = cgst_amount + sgst_amount + igst_amount + cess_amount
            total_amount = taxable_amount + total_gst_amount
            
            return {
                "place_of_supply": place_of_supply.value,
                "gst_rate": gst_rate,
                "cgst_rate": cgst_rate,
                "cgst_amount": cgst_amount,
                "sgst_rate": sgst_rate,
                "sgst_amount": sgst_amount,
                "igst_rate": gst_rate if place_of_supply != PlaceOfSupplyType.INTRA_STATE else Decimal('0'),
                "igst_amount": igst_amount,
                "cess_rate": cess_rate,
                "cess_amount": cess_amount,
                "total_gst_amount": total_gst_amount,
                "taxable_amount": taxable_amount,
                "total_amount": total_amount
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating GST: {e}")
            raise
    
    def _determine_place_of_supply(
        self,
        db: Session,
        company_id: int,
        supplier_state_code: str,
        recipient_state_code: str
    ) -> PlaceOfSupplyType:
        """Determine place of supply based on state codes"""
        
        if supplier_state_code == recipient_state_code:
            return PlaceOfSupplyType.INTRA_STATE
        else:
            return PlaceOfSupplyType.INTER_STATE
    
    def _calculate_cess(
        self,
        db: Session,
        company_id: int,
        hsn_code: Optional[str],
        sac_code: Optional[str],
        taxable_amount: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Calculate CESS based on HSN/SAC codes"""
        
        cess_rate = Decimal('0')
        cess_amount = Decimal('0')
        
        if hsn_code:
            hsn_record = db.query(HSNCode).filter(
                HSNCode.code == hsn_code,
                HSNCode.company_id == company_id,
                HSNCode.is_active == True
            ).first()
            
            if hsn_record and hsn_record.cess_rate:
                cess_rate = hsn_record.cess_rate
                cess_amount = (taxable_amount * cess_rate) / 100
        
        elif sac_code:
            sac_record = db.query(SACCode).filter(
                SACCode.code == sac_code,
                SACCode.company_id == company_id,
                SACCode.is_active == True
            ).first()
            
            if sac_record and sac_record.cess_rate:
                cess_rate = sac_record.cess_rate
                cess_amount = (taxable_amount * cess_rate) / 100
        
        return cess_rate, cess_amount
    
    def get_gst_slabs(self, db: Session, company_id: int) -> List[Dict]:
        """Get all GST slabs for a company"""
        
        slabs = db.query(GSTSlab).filter(
            GSTSlab.company_id == company_id,
            GSTSlab.is_active == True
        ).all()
        
        return [
            {
                "id": slab.id,
                "name": slab.name,
                "tax_type": slab.tax_type.value,
                "rate": float(slab.rate),
                "cgst_rate": float(slab.cgst_rate) if slab.cgst_rate else None,
                "sgst_rate": float(slab.sgst_rate) if slab.sgst_rate else None,
                "igst_rate": float(slab.igst_rate) if slab.igst_rate else None,
                "cess_rate": float(slab.cess_rate) if slab.cess_rate else None,
                "description": slab.description
            }
            for slab in slabs
        ]
    
    def get_hsn_codes(self, db: Session, company_id: int, search_term: Optional[str] = None) -> List[Dict]:
        """Get HSN codes with optional search"""
        
        query = db.query(HSNCode).filter(
            HSNCode.company_id == company_id,
            HSNCode.is_active == True
        )
        
        if search_term:
            query = query.filter(
                HSNCode.code.ilike(f"%{search_term}%") |
                HSNCode.description.ilike(f"%{search_term}%")
            )
        
        hsn_codes = query.limit(100).all()
        
        return [
            {
                "id": hsn.id,
                "code": hsn.code,
                "description": hsn.description,
                "gst_rate": float(hsn.gst_rate) if hsn.gst_rate else None,
                "cess_rate": float(hsn.cess_rate) if hsn.cess_rate else None
            }
            for hsn in hsn_codes
        ]
    
    def get_sac_codes(self, db: Session, company_id: int, search_term: Optional[str] = None) -> List[Dict]:
        """Get SAC codes with optional search"""
        
        query = db.query(SACCode).filter(
            SACCode.company_id == company_id,
            SACCode.is_active == True
        )
        
        if search_term:
            query = query.filter(
                SACCode.code.ilike(f"%{search_term}%") |
                SACCode.description.ilike(f"%{search_term}%")
            )
        
        sac_codes = query.limit(100).all()
        
        return [
            {
                "id": sac.id,
                "code": sac.code,
                "description": sac.description,
                "category": sac.category,
                "gst_rate": float(sac.gst_rate) if sac.gst_rate else None,
                "cess_rate": float(sac.cess_rate) if sac.cess_rate else None
            }
            for sac in sac_codes
        ]
    
    def get_state_codes(self, db: Session) -> List[Dict]:
        """Get all GST state codes"""
        
        states = db.query(GSTStateCode).filter(
            GSTStateCode.is_active == True
        ).order_by(GSTStateCode.name).all()
        
        return [
            {
                "id": state.id,
                "code": state.code,
                "name": state.name,
                "state_type": state.state_type
            }
            for state in states
        ]
    
    def validate_gstin(self, gstin: str) -> Dict[str, Any]:
        """Validate GSTIN format"""
        
        if not gstin or len(gstin) != 15:
            return {"valid": False, "error": "GSTIN must be 15 characters long"}
        
        # GSTIN format: 2 digit state code + 10 digit PAN + 1 digit entity number + 1 digit Z + 1 digit checksum
        state_code = gstin[:2]
        pan = gstin[2:12]
        entity_number = gstin[12:13]
        z = gstin[13:14]
        checksum = gstin[14:15]
        
        # Basic validation
        if not state_code.isdigit():
            return {"valid": False, "error": "Invalid state code"}
        
        if not pan.isalnum():
            return {"valid": False, "error": "Invalid PAN format"}
        
        if entity_number != '1':
            return {"valid": False, "error": "Invalid entity number"}
        
        if z != 'Z':
            return {"valid": False, "error": "Invalid Z character"}
        
        return {"valid": True, "state_code": state_code, "pan": pan}
    
    def get_place_of_supply_rules(self, db: Session, company_id: int) -> List[Dict]:
        """Get place of supply rules"""
        
        rules = db.query(PlaceOfSupply).filter(
            PlaceOfSupply.company_id == company_id,
            PlaceOfSupply.is_active == True
        ).all()
        
        return [
            {
                "id": rule.id,
                "supplier_state_code": rule.supplier_state_code,
                "recipient_state_code": rule.recipient_state_code,
                "supply_type": rule.supply_type.value,
                "applies_cgst_sgst": rule.applies_cgst_sgst,
                "applies_igst": rule.applies_igst,
                "rule_description": rule.rule_description
            }
            for rule in rules
        ]
    
    def create_gst_slab(
        self,
        db: Session,
        company_id: int,
        name: str,
        tax_type: str,
        rate: Decimal,
        cgst_rate: Optional[Decimal] = None,
        sgst_rate: Optional[Decimal] = None,
        igst_rate: Optional[Decimal] = None,
        cess_rate: Optional[Decimal] = None,
        description: Optional[str] = None
    ) -> GSTSlab:
        """Create a new GST slab"""
        
        gst_slab = GSTSlab(
            name=name,
            tax_type=GSTTaxType(tax_type),
            rate=rate,
            cgst_rate=cgst_rate,
            sgst_rate=sgst_rate,
            igst_rate=igst_rate,
            cess_rate=cess_rate,
            description=description,
            company_id=company_id
        )
        
        db.add(gst_slab)
        db.commit()
        db.refresh(gst_slab)
        
        self.logger.info(f"Created GST slab: {name} with rate {rate}%")
        return gst_slab

# Service instance
indian_gst_service = IndianGSTService()