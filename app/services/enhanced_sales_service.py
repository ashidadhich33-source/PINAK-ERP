# backend/app/services/enhanced_sales_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid

from ..models.enhanced_sales import (
    SaleChallan, SaleChallanItem, BillSeries, PaymentMode, Staff, StaffTarget,
    SaleReturn, SaleReturnItem, SaleOrder, SaleOrderItem, SaleInvoice, SaleInvoiceItem, POSSession
)
from ..models.item import Item
from ..models.customer import Customer
from ..models.stock import StockItem, StockLocation
from ..models.sale import SaleBill, SaleBillItem

logger = logging.getLogger(__name__)

class EnhancedSalesService:
    """Service class for enhanced sales management"""
    
    def __init__(self):
        pass
    
    # Sale Challan Management
    def create_sale_challan(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        challan_date: date,
        challan_type: str = 'delivery',
        staff_id: Optional[int] = None,
        delivery_address: str = None,
        delivery_date: date = None,
        delivery_time: str = None,
        contact_person: str = None,
        contact_phone: str = None,
        notes: str = None,
        user_id: int = None
    ) -> SaleChallan:
        """Create sale challan"""
        
        # Generate challan number
        challan_number = f"CHL-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Create challan
        challan = SaleChallan(
            company_id=company_id,
            challan_number=challan_number,
            challan_date=challan_date,
            customer_id=customer_id,
            staff_id=staff_id,
            challan_type=challan_type,
            delivery_address=delivery_address,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            contact_person=contact_person,
            contact_phone=contact_phone,
            notes=notes,
            created_by=user_id
        )
        
        db.add(challan)
        db.commit()
        db.refresh(challan)
        
        logger.info(f"Sale challan created: {challan_number}")
        
        return challan
    
    def add_items_to_challan(
        self, 
        db: Session, 
        company_id: int,
        challan_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[SaleChallanItem]:
        """Add items to sale challan"""
        
        challan_items = []
        total_quantity = Decimal('0')
        total_amount = Decimal('0')
        
        for item_data in items:
            # Create challan item
            challan_item = SaleChallanItem(
                company_id=company_id,
                challan_id=challan_id,
                item_id=item_data['item_id'],
                variant_id=item_data.get('variant_id'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_amount=item_data['quantity'] * item_data['unit_price'],
                pending_quantity=item_data['quantity'],
                notes=item_data.get('notes'),
                created_by=user_id
            )
            
            db.add(challan_item)
            challan_items.append(challan_item)
            
            total_quantity += item_data['quantity']
            total_amount += challan_item.total_amount
        
        # Update challan record
        challan = db.query(SaleChallan).filter(
            SaleChallan.id == challan_id
        ).first()
        
        if challan:
            challan.total_quantity = total_quantity
            challan.total_amount = total_amount
            challan.status = 'confirmed'
            db.commit()
        
        logger.info(f"Added {len(challan_items)} items to sale challan")
        
        return challan_items
    
    def deliver_challan_items(
        self, 
        db: Session, 
        company_id: int,
        challan_id: int,
        item_deliveries: List[Dict],
        user_id: int = None
    ) -> bool:
        """Deliver challan items"""
        
        challan = db.query(SaleChallan).filter(
            SaleChallan.id == challan_id,
            SaleChallan.company_id == company_id
        ).first()
        
        if not challan:
            return False
        
        for delivery in item_deliveries:
            challan_item = db.query(SaleChallanItem).filter(
                SaleChallanItem.id == delivery['item_id'],
                SaleChallanItem.challan_id == challan_id
            ).first()
            
            if challan_item:
                challan_item.delivered_quantity += delivery['delivered_quantity']
                challan_item.pending_quantity -= delivery['delivered_quantity']
        
        # Check if all items are delivered
        all_delivered = all(
            item.pending_quantity == 0 
            for item in db.query(SaleChallanItem).filter(
                SaleChallanItem.challan_id == challan_id
            ).all()
        )
        
        if all_delivered:
            challan.status = 'delivered'
        else:
            challan.status = 'partial'
        
        challan.updated_by = user_id
        challan.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Challan items delivered: {challan.challan_number}")
        
        return True
    
    # Bill Series Management
    def create_bill_series(
        self, 
        db: Session, 
        company_id: int,
        series_name: str,
        series_code: str,
        document_type: str,
        prefix: str,
        suffix: str = None,
        starting_number: int = 1,
        number_length: int = 6,
        is_default: bool = False,
        notes: str = None,
        user_id: int = None
    ) -> BillSeries:
        """Create bill series"""
        
        # Check if series code already exists
        existing_series = db.query(BillSeries).filter(
            BillSeries.company_id == company_id,
            BillSeries.series_code == series_code
        ).first()
        
        if existing_series:
            raise ValueError(f"Bill series code {series_code} already exists")
        
        # If setting as default, unset other default series for this document type
        if is_default:
            db.query(BillSeries).filter(
                BillSeries.company_id == company_id,
                BillSeries.document_type == document_type,
                BillSeries.is_default == True
            ).update({"is_default": False})
        
        # Create bill series
        bill_series = BillSeries(
            company_id=company_id,
            series_name=series_name,
            series_code=series_code,
            document_type=document_type,
            prefix=prefix,
            suffix=suffix,
            starting_number=starting_number,
            current_number=starting_number - 1,
            number_length=number_length,
            is_default=is_default,
            notes=notes,
            created_by=user_id
        )
        
        db.add(bill_series)
        db.commit()
        db.refresh(bill_series)
        
        logger.info(f"Bill series created: {series_name}")
        
        return bill_series
    
    def get_bill_series(
        self, 
        db: Session, 
        company_id: int,
        document_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[BillSeries]:
        """Get bill series"""
        
        query = db.query(BillSeries).filter(BillSeries.company_id == company_id)
        
        if document_type:
            query = query.filter(BillSeries.document_type == document_type)
        
        if is_active is not None:
            query = query.filter(BillSeries.is_active == is_active)
        
        series = query.order_by(BillSeries.series_name).all()
        
        return series
    
    def generate_bill_number(
        self, 
        db: Session, 
        company_id: int,
        document_type: str
    ) -> str:
        """Generate next bill number"""
        
        # Get default series for document type
        series = db.query(BillSeries).filter(
            BillSeries.company_id == company_id,
            BillSeries.document_type == document_type,
            BillSeries.is_default == True,
            BillSeries.is_active == True
        ).first()
        
        if not series:
            # Get any active series for document type
            series = db.query(BillSeries).filter(
                BillSeries.company_id == company_id,
                BillSeries.document_type == document_type,
                BillSeries.is_active == True
            ).first()
        
        if not series:
            raise ValueError(f"No bill series found for document type: {document_type}")
        
        # Generate bill number
        bill_number = series.generate_number()
        
        # Update current number
        series.current_number += 1
        db.commit()
        
        logger.info(f"Generated bill number: {bill_number}")
        
        return bill_number
    
    # Payment Mode Management
    def create_payment_mode(
        self, 
        db: Session, 
        company_id: int,
        mode_name: str,
        mode_code: str,
        mode_type: str,
        is_default: bool = False,
        requires_reference: bool = False,
        requires_approval: bool = False,
        minimum_amount: Decimal = None,
        maximum_amount: Decimal = None,
        processing_fee_percentage: Decimal = 0,
        processing_fee_fixed: Decimal = 0,
        notes: str = None,
        user_id: int = None
    ) -> PaymentMode:
        """Create payment mode"""
        
        # Check if mode code already exists
        existing_mode = db.query(PaymentMode).filter(
            PaymentMode.company_id == company_id,
            PaymentMode.mode_code == mode_code
        ).first()
        
        if existing_mode:
            raise ValueError(f"Payment mode code {mode_code} already exists")
        
        # If setting as default, unset other default modes
        if is_default:
            db.query(PaymentMode).filter(
                PaymentMode.company_id == company_id,
                PaymentMode.is_default == True
            ).update({"is_default": False})
        
        # Create payment mode
        payment_mode = PaymentMode(
            company_id=company_id,
            mode_name=mode_name,
            mode_code=mode_code,
            mode_type=mode_type,
            is_default=is_default,
            requires_reference=requires_reference,
            requires_approval=requires_approval,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            processing_fee_percentage=processing_fee_percentage,
            processing_fee_fixed=processing_fee_fixed,
            notes=notes,
            created_by=user_id
        )
        
        db.add(payment_mode)
        db.commit()
        db.refresh(payment_mode)
        
        logger.info(f"Payment mode created: {mode_name}")
        
        return payment_mode
    
    def get_payment_modes(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None
    ) -> List[PaymentMode]:
        """Get payment modes"""
        
        query = db.query(PaymentMode).filter(PaymentMode.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(PaymentMode.is_active == is_active)
        
        modes = query.order_by(PaymentMode.mode_name).all()
        
        return modes
    
    # Staff Management
    def create_staff(
        self, 
        db: Session, 
        company_id: int,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str = None,
        phone: str = None,
        address: str = None,
        date_of_birth: date = None,
        date_of_joining: date = None,
        designation: str = None,
        department: str = None,
        salary: Decimal = None,
        commission_percentage: Decimal = 0,
        user_id: int = None
    ) -> Staff:
        """Create staff member"""
        
        # Check if employee ID already exists
        existing_staff = db.query(Staff).filter(
            Staff.company_id == company_id,
            Staff.employee_id == employee_id
        ).first()
        
        if existing_staff:
            raise ValueError(f"Employee ID {employee_id} already exists")
        
        # Create staff
        staff = Staff(
            company_id=company_id,
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
            date_of_joining=date_of_joining,
            designation=designation,
            department=department,
            salary=salary,
            commission_percentage=commission_percentage,
            created_by=user_id
        )
        
        db.add(staff)
        db.commit()
        db.refresh(staff)
        
        logger.info(f"Staff created: {staff.full_name}")
        
        return staff
    
    def get_staff(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None,
        department: Optional[str] = None
    ) -> List[Staff]:
        """Get staff members"""
        
        query = db.query(Staff).filter(Staff.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(Staff.is_active == is_active)
        
        if department:
            query = query.filter(Staff.department == department)
        
        staff = query.order_by(Staff.first_name, Staff.last_name).all()
        
        return staff
    
    def create_staff_target(
        self, 
        db: Session, 
        company_id: int,
        staff_id: int,
        target_period: str,
        target_date: date,
        target_amount: Decimal,
        target_quantity: Decimal = None,
        commission_rate: Decimal = 0,
        bonus_amount: Decimal = 0,
        notes: str = None,
        user_id: int = None
    ) -> StaffTarget:
        """Create staff target"""
        
        # Create target
        target = StaffTarget(
            company_id=company_id,
            staff_id=staff_id,
            target_period=target_period,
            target_date=target_date,
            target_amount=target_amount,
            target_quantity=target_quantity,
            commission_rate=commission_rate,
            bonus_amount=bonus_amount,
            notes=notes,
            created_by=user_id
        )
        
        db.add(target)
        db.commit()
        db.refresh(target)
        
        logger.info(f"Staff target created: {target_period}")
        
        return target
    
    def update_staff_target_achievement(
        self, 
        db: Session, 
        company_id: int,
        staff_id: int,
        target_date: date,
        achieved_amount: Decimal,
        achieved_quantity: Decimal = None
    ) -> bool:
        """Update staff target achievement"""
        
        target = db.query(StaffTarget).filter(
            StaffTarget.company_id == company_id,
            StaffTarget.staff_id == staff_id,
            StaffTarget.target_date == target_date
        ).first()
        
        if not target:
            return False
        
        target.achieved_amount = achieved_amount
        if achieved_quantity is not None:
            target.achieved_quantity = achieved_quantity
        
        # Update status based on achievement
        if target.achieved_amount >= target.target_amount:
            target.status = 'achieved'
        else:
            target.status = 'failed'
        
        target.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Staff target achievement updated: {target.achievement_percentage}%")
        
        return True
    
    # Sale Return Management
    def create_sale_return(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        return_date: date,
        return_reason: str = None,
        return_type: str = 'defective',
        original_bill_id: int = None,
        staff_id: int = None,
        notes: str = None,
        user_id: int = None
    ) -> SaleReturn:
        """Create sale return"""
        
        # Generate return number
        return_number = f"SR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Get original bill details if provided
        original_bill = None
        if original_bill_id:
            original_bill = db.query(SaleBill).filter(
                SaleBill.id == original_bill_id,
                SaleBill.company_id == company_id
            ).first()
        
        # Create return
        sale_return = SaleReturn(
            company_id=company_id,
            return_number=return_number,
            return_date=return_date,
            customer_id=customer_id,
            staff_id=staff_id,
            original_bill_id=original_bill_id,
            original_bill_number=original_bill.bill_number if original_bill else None,
            original_bill_date=original_bill.bill_date if original_bill else None,
            return_reason=return_reason,
            return_type=return_type,
            notes=notes,
            created_by=user_id
        )
        
        db.add(sale_return)
        db.commit()
        db.refresh(sale_return)
        
        logger.info(f"Sale return created: {return_number}")
        
        return sale_return
    
    def add_items_to_sale_return(
        self, 
        db: Session, 
        company_id: int,
        return_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[SaleReturnItem]:
        """Add items to sale return"""
        
        return_items = []
        total_quantity = Decimal('0')
        total_amount = Decimal('0')
        total_cgst = Decimal('0')
        total_sgst = Decimal('0')
        total_igst = Decimal('0')
        
        for item_data in items:
            # Calculate GST amounts
            cgst_amount = Decimal('0')
            sgst_amount = Decimal('0')
            igst_amount = Decimal('0')
            
            if item_data.get('gst_rate'):
                gst_amount = (item_data['total_amount'] * item_data['gst_rate'] / 100)
                cgst_amount = gst_amount / 2
                sgst_amount = gst_amount / 2
                igst_amount = gst_amount
            
            # Create return item
            return_item = SaleReturnItem(
                company_id=company_id,
                return_id=return_id,
                item_id=item_data['item_id'],
                variant_id=item_data.get('variant_id'),
                original_bill_item_id=item_data.get('original_bill_item_id'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_amount=item_data['total_amount'],
                gst_rate=item_data.get('gst_rate'),
                cgst_amount=cgst_amount,
                sgst_amount=sgst_amount,
                igst_amount=igst_amount,
                return_reason=item_data.get('return_reason'),
                notes=item_data.get('notes'),
                created_by=user_id
            )
            
            db.add(return_item)
            return_items.append(return_item)
            
            total_quantity += item_data['quantity']
            total_amount += item_data['total_amount']
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_igst += igst_amount
        
        # Update return record
        return_record = db.query(SaleReturn).filter(
            SaleReturn.id == return_id
        ).first()
        
        if return_record:
            return_record.total_quantity = total_quantity
            return_record.total_amount = total_amount
            return_record.cgst_amount = total_cgst
            return_record.sgst_amount = total_sgst
            return_record.igst_amount = total_igst
            return_record.total_gst_amount = total_cgst + total_sgst + total_igst
            return_record.net_amount = total_amount + return_record.total_gst_amount
            return_record.status = 'confirmed'
            db.commit()
        
        logger.info(f"Added {len(return_items)} items to sale return")
        
        return return_items
    
    def process_sale_return(
        self, 
        db: Session, 
        company_id: int,
        return_id: int,
        user_id: int = None
    ) -> bool:
        """Process sale return and update stock"""
        
        return_record = db.query(SaleReturn).filter(
            SaleReturn.id == return_id,
            SaleReturn.company_id == company_id
        ).first()
        
        if not return_record:
            return False
        
        return_items = db.query(SaleReturnItem).filter(
            SaleReturnItem.return_id == return_id
        ).all()
        
        for item in return_items:
            # Update stock (increase quantity)
            stock_item = db.query(StockItem).filter(
                StockItem.item_id == item.item_id,
                StockItem.company_id == company_id
            ).first()
            
            if stock_item:
                stock_item.quantity += item.quantity
                stock_item.updated_by = user_id
                stock_item.updated_at = datetime.utcnow()
        
        # Update return status
        return_record.status = 'processed'
        return_record.updated_by = user_id
        return_record.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Sale return processed: {return_record.return_number}")
        
        return True
    
    # POS Session Management
    def start_pos_session(
        self, 
        db: Session, 
        company_id: int,
        staff_id: int,
        opening_cash: Decimal = 0,
        notes: str = None,
        user_id: int = None
    ) -> POSSession:
        """Start POS session"""
        
        # Check if staff has active session
        active_session = db.query(POSSession).filter(
            POSSession.company_id == company_id,
            POSSession.staff_id == staff_id,
            POSSession.status == 'active'
        ).first()
        
        if active_session:
            raise ValueError("Staff already has an active POS session")
        
        # Generate session number
        session_number = f"POS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{staff_id}"
        
        # Create session
        session = POSSession(
            company_id=company_id,
            session_number=session_number,
            staff_id=staff_id,
            start_time=datetime.utcnow(),
            opening_cash=opening_cash,
            notes=notes,
            created_by=user_id
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info(f"POS session started: {session_number}")
        
        return session
    
    def close_pos_session(
        self, 
        db: Session, 
        company_id: int,
        session_id: int,
        closing_cash: Decimal,
        notes: str = None,
        user_id: int = None
    ) -> bool:
        """Close POS session"""
        
        session = db.query(POSSession).filter(
            POSSession.id == session_id,
            POSSession.company_id == company_id,
            POSSession.status == 'active'
        ).first()
        
        if not session:
            return False
        
        # Calculate session totals
        session.end_time = datetime.utcnow()
        session.closing_cash = closing_cash
        session.status = 'closed'
        session.notes = notes
        session.updated_by = user_id
        session.updated_at = datetime.utcnow()
        
        # Calculate total sales and transactions
        sales = db.query(SaleBill).filter(
            SaleBill.pos_session_id == session_id,
            SaleBill.status != 'cancelled'
        ).all()
        
        session.total_sales = sum(sale.total_amount for sale in sales)
        session.total_transactions = len(sales)
        
        db.commit()
        
        logger.info(f"POS session closed: {session.session_number}")
        
        return True
    
    # Sales Analytics
    def get_sales_analytics(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        staff_id: Optional[int] = None
    ) -> Dict:
        """Get sales analytics"""
        
        # Get sales bills
        query = db.query(SaleBill).filter(
            SaleBill.company_id == company_id,
            SaleBill.status != 'cancelled'
        )
        
        if from_date:
            query = query.filter(SaleBill.bill_date >= from_date)
        
        if to_date:
            query = query.filter(SaleBill.bill_date <= to_date)
        
        if staff_id:
            query = query.filter(SaleBill.staff_id == staff_id)
        
        bills = query.all()
        
        # Calculate analytics
        total_bills = len(bills)
        total_amount = sum(bill.total_amount for bill in bills)
        total_gst = sum(bill.cgst_amount + bill.sgst_amount + bill.igst_amount for bill in bills)
        
        # Get top customers
        customer_analytics = db.query(
            SaleBill.customer_id,
            func.count(SaleBill.id).label('bill_count'),
            func.sum(SaleBill.total_amount).label('total_amount')
        ).filter(
            SaleBill.company_id == company_id,
            SaleBill.status != 'cancelled'
        ).group_by(SaleBill.customer_id).all()
        
        # Get staff performance
        staff_analytics = db.query(
            SaleBill.staff_id,
            func.count(SaleBill.id).label('bill_count'),
            func.sum(SaleBill.total_amount).label('total_amount')
        ).filter(
            SaleBill.company_id == company_id,
            SaleBill.status != 'cancelled'
        ).group_by(SaleBill.staff_id).all()
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "summary": {
                "total_bills": total_bills,
                "total_amount": total_amount,
                "total_gst": total_gst,
                "average_bill_amount": total_amount / total_bills if total_bills > 0 else 0
            },
            "customer_analytics": [
                {
                    "customer_id": customer.customer_id,
                    "bill_count": customer.bill_count,
                    "total_amount": customer.total_amount
                }
                for customer in customer_analytics
            ],
            "staff_analytics": [
                {
                    "staff_id": staff.staff_id,
                    "bill_count": staff.bill_count,
                    "total_amount": staff.total_amount
                }
                for staff in staff_analytics
            ]
        }

# Global service instance
enhanced_sales_service = EnhancedSalesService()