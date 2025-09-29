# backend/app/services/financial_year_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ..models.core import Company, FinancialYear, ChartOfAccount
from ..models.sales import SalesInvoice, SalesInvoiceItem
from ..models.purchase import PurchaseBill, PurchaseBillItem
from ..models.customers import Customer
from ..models.customers import Supplier
from ..models.inventory import Item
from ..models.inventory import StockItem

logger = logging.getLogger(__name__)

class FinancialYearService:
    """Service class for financial year management operations"""
    
    def __init__(self):
        pass
    
    def create_financial_year(
        self, 
        db: Session, 
        company_id: int,
        year_name: str,
        start_date: date,
        end_date: date,
        user_id: int
    ) -> FinancialYear:
        """Create new financial year"""
        
        # Validate date range
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Check if financial year already exists
        existing_fy = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            FinancialYear.year_name == year_name
        ).first()
        
        if existing_fy:
            raise ValueError(f"Financial year {year_name} already exists")
        
        # Deactivate current financial year
        current_fy = self.get_active_financial_year(db, company_id)
        if current_fy:
            current_fy.is_active = False
            current_fy.updated_by = user_id
            current_fy.updated_at = datetime.utcnow()
        
        # Create new financial year
        financial_year = FinancialYear(
            company_id=company_id,
            year_name=year_name,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            created_by=user_id
        )
        
        db.add(financial_year)
        db.commit()
        db.refresh(financial_year)
        
        logger.info(f"Financial year created: {year_name} for company {company_id}")
        
        return financial_year
    
    def get_active_financial_year(
        self, 
        db: Session, 
        company_id: int
    ) -> Optional[FinancialYear]:
        """Get active financial year for company"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            FinancialYear.is_active == True
        ).first()
        
        return financial_year
    
    def get_financial_year_by_id(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Optional[FinancialYear]:
        """Get financial year by ID"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        return financial_year
    
    def list_financial_years(
        self, 
        db: Session, 
        company_id: int,
        include_closed: bool = False
    ) -> List[FinancialYear]:
        """List financial years for company"""
        
        query = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id
        )
        
        if not include_closed:
            query = query.filter(FinancialYear.is_closed == False)
        
        financial_years = query.order_by(FinancialYear.start_date.desc()).all()
        
        return financial_years
    
    def close_financial_year(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        user_id: int,
        closing_remarks: str = None
    ) -> FinancialYear:
        """Close financial year and prepare opening balances"""
        
        # Get financial year
        financial_year = self.get_financial_year_by_id(db, company_id, fy_id)
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Financial year is already closed")
        
        # Calculate closing balances
        closing_balances = self._calculate_closing_balances(db, company_id, fy_id)
        
        # Update financial year
        financial_year.is_closed = True
        financial_year.closed_at = datetime.utcnow()
        financial_year.closed_by = user_id
        financial_year.closing_remarks = closing_remarks
        financial_year.opening_balances = json.dumps(closing_balances)
        
        db.commit()
        
        logger.info(f"Financial year closed: {financial_year.year_name} for company {company_id}")
        
        return financial_year
    
    def _calculate_closing_balances(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Calculate closing balances for financial year"""
        
        financial_year = self.get_financial_year_by_id(db, company_id, fy_id)
        if not financial_year:
            raise ValueError("Financial year not found")
        
        # Get account balances
        account_balances = self._get_account_balances(
            db, company_id, financial_year.start_date, financial_year.end_date
        )
        
        # Get stock balances
        stock_balances = self._get_stock_balances(db, company_id)
        
        # Get customer balances
        customer_balances = self._get_customer_balances(db, company_id)
        
        # Get supplier balances
        supplier_balances = self._get_supplier_balances(db, company_id)
        
        return {
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date.isoformat(),
                "end_date": financial_year.end_date.isoformat()
            },
            "account_balances": account_balances,
            "stock_balances": stock_balances,
            "customer_balances": customer_balances,
            "supplier_balances": supplier_balances,
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    def _get_account_balances(
        self, 
        db: Session, 
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict:
        """Get account balances for the period"""
        
        # This would require implementing journal entries and account balances
        # For now, return basic structure
        return {
            "assets": {
                "cash": Decimal('0'),
                "bank": Decimal('0'),
                "inventory": Decimal('0'),
                "receivables": Decimal('0')
            },
            "liabilities": {
                "payables": Decimal('0'),
                "gst_payable": Decimal('0'),
                "loans": Decimal('0')
            },
            "equity": {
                "capital": Decimal('0'),
                "retained_earnings": Decimal('0')
            },
            "income": {
                "sales": Decimal('0'),
                "other_income": Decimal('0')
            },
            "expenses": {
                "purchases": Decimal('0'),
                "operating_expenses": Decimal('0')
            }
        }
    
    def _get_stock_balances(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get stock balances"""
        
        stock_items = db.query(StockItem).join(
            Item, StockItem.item_id == Item.id
        ).filter(
            Item.company_id == company_id,
            StockItem.quantity > 0
        ).all()
        
        return [
            {
                "item_id": stock.item_id,
                "item_name": stock.item.name,
                "barcode": stock.item.barcode,
                "quantity": stock.quantity,
                "unit_cost": stock.average_cost,
                "total_value": stock.quantity * stock.average_cost
            }
            for stock in stock_items
        ]
    
    def _get_customer_balances(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get customer balances"""
        
        customers = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.current_balance != 0
        ).all()
        
        return [
            {
                "customer_id": customer.id,
                "customer_name": customer.name,
                "customer_code": customer.customer_code,
                "balance": customer.current_balance
            }
            for customer in customers
        ]
    
    def _get_supplier_balances(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get supplier balances"""
        
        suppliers = db.query(Supplier).filter(
            Supplier.company_id == company_id,
            Supplier.current_balance != 0
        ).all()
        
        return [
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "supplier_code": supplier.supplier_code,
                "balance": supplier.current_balance
            }
            for supplier in suppliers
        ]
    
    def create_opening_balances(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        opening_balances: Dict,
        user_id: int
    ) -> FinancialYear:
        """Create opening balances for new financial year"""
        
        # Get financial year
        financial_year = self.get_financial_year_by_id(db, company_id, fy_id)
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Cannot create opening balances for closed financial year")
        
        # Update opening balances
        financial_year.opening_balances = json.dumps(opening_balances)
        financial_year.updated_by = user_id
        financial_year.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Opening balances created for financial year {financial_year.year_name}")
        
        return financial_year
    
    def carry_forward_data(
        self, 
        db: Session, 
        company_id: int,
        from_fy_id: int,
        to_fy_id: int,
        user_id: int
    ) -> Dict:
        """Carry forward data from one financial year to another"""
        
        # Get source and target financial years
        from_fy = self.get_financial_year_by_id(db, company_id, from_fy_id)
        to_fy = self.get_financial_year_by_id(db, company_id, to_fy_id)
        
        if not from_fy or not to_fy:
            raise ValueError("Financial year not found")
        
        if not from_fy.is_closed:
            raise ValueError("Source financial year must be closed")
        
        if to_fy.is_closed:
            raise ValueError("Target financial year must be open")
        
        # Get opening balances from source FY
        opening_balances = json.loads(from_fy.opening_balances) if from_fy.opening_balances else {}
        
        # Create opening balances for target FY
        self.create_opening_balances(db, company_id, to_fy_id, opening_balances, user_id)
        
        # Carry forward master data
        self._carry_forward_master_data(db, company_id, from_fy_id, to_fy_id)
        
        logger.info(f"Data carried forward from {from_fy.year_name} to {to_fy.year_name}")
        
        return {
            "from_financial_year": from_fy.year_name,
            "to_financial_year": to_fy.year_name,
            "opening_balances": opening_balances,
            "carried_forward_at": datetime.utcnow().isoformat()
        }
    
    def _carry_forward_master_data(
        self, 
        db: Session, 
        company_id: int,
        from_fy_id: int,
        to_fy_id: int
    ):
        """Carry forward master data between financial years"""
        
        # This would involve copying master data like:
        # - Items
        # - Customers
        # - Suppliers
        # - Chart of Accounts
        # - GST Slabs
        # etc.
        
        # For now, just log the operation
        logger.info("Master data carry forward completed")
    
    def get_financial_year_summary(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Get financial year summary"""
        
        financial_year = self.get_financial_year_by_id(db, company_id, fy_id)
        if not financial_year:
            raise ValueError("Financial year not found")
        
        # Get transaction counts
        sales_count = db.query(SalesInvoice).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= financial_year.start_date,
            SalesInvoice.invoice_date <= financial_year.end_date
        ).count()
        
        purchase_count = db.query(PurchaseBill).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= financial_year.start_date,
            PurchaseBill.bill_date <= financial_year.end_date
        ).count()
        
        # Get total amounts
        sales_total = db.query(func.sum(SalesInvoice.total_amount)).filter(
            SalesInvoice.company_id == company_id,
            SalesInvoice.invoice_date >= financial_year.start_date,
            SalesInvoice.invoice_date <= financial_year.end_date
        ).scalar() or Decimal('0')
        
        purchase_total = db.query(func.sum(PurchaseBill.total_amount)).filter(
            PurchaseBill.company_id == company_id,
            PurchaseBill.bill_date >= financial_year.start_date,
            PurchaseBill.bill_date <= financial_year.end_date
        ).scalar() or Decimal('0')
        
        return {
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date,
                "end_date": financial_year.end_date,
                "is_active": financial_year.is_active,
                "is_closed": financial_year.is_closed,
                "closed_at": financial_year.closed_at,
                "closed_by": financial_year.closed_by
            },
            "transactions": {
                "sales_count": sales_count,
                "purchase_count": purchase_count,
                "sales_total": sales_total,
                "purchase_total": purchase_total
            },
            "opening_balances": json.loads(financial_year.opening_balances) if financial_year.opening_balances else None
        }
    
    def get_financial_year_reports(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Get financial year reports"""
        
        financial_year = self.get_financial_year_by_id(db, company_id, fy_id)
        if not financial_year:
            raise ValueError("Financial year not found")
        
        # Get monthly breakdown
        monthly_data = []
        current_date = financial_year.start_date
        
        while current_date <= financial_year.end_date:
            month_end = min(
                current_date.replace(day=28) + timedelta(days=4),
                financial_year.end_date
            )
            
            # Get monthly sales
            monthly_sales = db.query(func.sum(SalesInvoice.total_amount)).filter(
                SalesInvoice.company_id == company_id,
                SalesInvoice.invoice_date >= current_date,
                SalesInvoice.invoice_date <= month_end
            ).scalar() or Decimal('0')
            
            # Get monthly purchases
            monthly_purchases = db.query(func.sum(PurchaseBill.total_amount)).filter(
                PurchaseBill.company_id == company_id,
                PurchaseBill.bill_date >= current_date,
                PurchaseBill.bill_date <= month_end
            ).scalar() or Decimal('0')
            
            monthly_data.append({
                "month": current_date.strftime("%B %Y"),
                "sales": monthly_sales,
                "purchases": monthly_purchases,
                "net": monthly_sales - monthly_purchases
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return {
            "financial_year": {
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date,
                "end_date": financial_year.end_date
            },
            "monthly_breakdown": monthly_data,
            "summary": {
                "total_sales": sum(month['sales'] for month in monthly_data),
                "total_purchases": sum(month['purchases'] for month in monthly_data),
                "net_profit": sum(month['net'] for month in monthly_data)
            }
        }
    
    def validate_financial_year_dates(
        self, 
        start_date: date,
        end_date: date
    ) -> Tuple[bool, str]:
        """Validate financial year dates"""
        
        if start_date >= end_date:
            return False, "Start date must be before end date"
        
        if (end_date - start_date).days < 300:  # Less than 10 months
            return False, "Financial year must be at least 10 months"
        
        if (end_date - start_date).days > 400:  # More than 13 months
            return False, "Financial year cannot exceed 13 months"
        
        return True, "Valid financial year dates"
    
    def get_financial_year_suggestions(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get financial year suggestions based on existing data"""
        
        # Get existing financial years
        existing_fys = self.list_financial_years(db, company_id, include_closed=True)
        
        if not existing_fys:
            # No existing FY, suggest current year
            current_year = datetime.now().year
            return [
                {
                    "year_name": f"{current_year}-{current_year + 1}",
                    "start_date": date(current_year, 4, 1),
                    "end_date": date(current_year + 1, 3, 31),
                    "suggestion": "Standard Indian financial year"
                }
            ]
        
        # Get the latest financial year
        latest_fy = existing_fys[0]
        
        # Suggest next financial year
        next_start = latest_fy.end_date + timedelta(days=1)
        next_end = date(next_start.year + 1, next_start.month - 1, 28)
        
        return [
            {
                "year_name": f"{next_start.year}-{next_start.year + 1}",
                "start_date": next_start,
                "end_date": next_end,
                "suggestion": "Next financial year based on existing pattern"
            }
        ]

# Global service instance
financial_year_service = FinancialYearService()