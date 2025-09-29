# backend/app/services/financial_year_management_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid

from ..models.financial_year_management import (
    FinancialYear, OpeningBalance, YearClosing, YearClosingItem, DataCarryForward,
    YearAnalytics, YearComparison, YearBackup, YearRestore, YearAudit, YearReport,
    YearConfiguration, YearPermission
)
from ..models.chart_of_accounts import ChartOfAccount

logger = logging.getLogger(__name__)

class FinancialYearManagementService:
    """Service class for financial year management"""
    
    def __init__(self):
        pass
    
    # Financial Year Management
    def create_financial_year(
        self, 
        db: Session, 
        company_id: int,
        year_name: str,
        year_code: str,
        start_date: date,
        end_date: date,
        notes: str = None,
        user_id: int = None
    ) -> FinancialYear:
        """Create financial year"""
        
        # Check if year code already exists
        existing_year = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            FinancialYear.year_code == year_code
        ).first()
        
        if existing_year:
            raise ValueError(f"Financial year code {year_code} already exists")
        
        # Validate date range
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Check for overlapping years
        overlapping_year = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            or_(
                and_(FinancialYear.start_date <= start_date, FinancialYear.end_date >= start_date),
                and_(FinancialYear.start_date <= end_date, FinancialYear.end_date >= end_date),
                and_(FinancialYear.start_date >= start_date, FinancialYear.end_date <= end_date)
            )
        ).first()
        
        if overlapping_year:
            raise ValueError(f"Financial year overlaps with existing year: {overlapping_year.year_name}")
        
        # Create financial year
        financial_year = FinancialYear(
            company_id=company_id,
            year_name=year_name,
            year_code=year_code,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
            created_by=user_id
        )
        
        db.add(financial_year)
        db.commit()
        db.refresh(financial_year)
        
        logger.info(f"Financial year created: {year_name}")
        
        return financial_year
    
    def get_financial_years(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None,
        is_closed: Optional[bool] = None,
        year_status: Optional[str] = None
    ) -> List[FinancialYear]:
        """Get financial years"""
        
        query = db.query(FinancialYear).filter(FinancialYear.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(FinancialYear.is_active == is_active)
        
        if is_closed is not None:
            query = query.filter(FinancialYear.is_closed == is_closed)
        
        if year_status:
            query = query.filter(FinancialYear.year_status == year_status)
        
        years = query.order_by(FinancialYear.start_date.desc()).all()
        
        return years
    
    def activate_financial_year(
        self, 
        db: Session, 
        company_id: int,
        year_id: int,
        user_id: int = None
    ) -> FinancialYear:
        """Activate financial year"""
        
        year = db.query(FinancialYear).filter(
            FinancialYear.id == year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not year:
            raise ValueError("Financial year not found")
        
        if year.is_closed:
            raise ValueError("Cannot activate closed financial year")
        
        # Deactivate other active years
        db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            FinancialYear.is_active == True
        ).update({"is_active": False})
        
        # Activate current year
        year.is_active = True
        year.year_status = 'active'
        year.updated_by = user_id
        year.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Financial year activated: {year.year_name}")
        
        return year
    
    def close_financial_year(
        self, 
        db: Session, 
        company_id: int,
        year_id: int,
        closing_type: str = 'full_closing',
        user_id: int = None
    ) -> YearClosing:
        """Close financial year"""
        
        year = db.query(FinancialYear).filter(
            FinancialYear.id == year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not year:
            raise ValueError("Financial year not found")
        
        if year.is_closed:
            raise ValueError("Financial year is already closed")
        
        if not year.is_active:
            raise ValueError("Only active financial year can be closed")
        
        # Create year closing record
        closing = YearClosing(
            company_id=company_id,
            financial_year_id=year_id,
            closing_type=closing_type,
            closing_status='in_progress',
            closed_by=user_id,
            created_by=user_id
        )
        
        db.add(closing)
        db.commit()
        db.refresh(closing)
        
        try:
            # Perform closing operations
            self._perform_year_closing(db, year, closing)
            
            # Update year status
            year.is_closed = True
            year.is_active = False
            year.year_status = 'closed'
            year.closing_date = datetime.utcnow()
            year.closed_by = user_id
            year.updated_by = user_id
            year.updated_at = datetime.utcnow()
            
            # Update closing status
            closing.closing_status = 'completed'
            closing.closing_date = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Financial year closed: {year.year_name}")
            
            return closing
            
        except Exception as e:
            # Update closing with error
            closing.closing_status = 'failed'
            closing.closing_errors = {"error": str(e)}
            db.commit()
            
            logger.error(f"Financial year closing failed: {str(e)}")
            raise ValueError(f"Financial year closing failed: {str(e)}")
    
    def _perform_year_closing(
        self, 
        db: Session, 
        year: FinancialYear, 
        closing: YearClosing
    ):
        """Perform year closing operations"""
        
        closing_data = {
            "closing_date": datetime.utcnow().isoformat(),
            "year_name": year.year_name,
            "year_code": year.year_code,
            "start_date": year.start_date.isoformat(),
            "end_date": year.end_date.isoformat()
        }
        
        # Close accounts
        self._close_accounts(db, year, closing)
        
        # Close transactions
        self._close_transactions(db, year, closing)
        
        # Close inventory
        self._close_inventory(db, year, closing)
        
        # Close customers
        self._close_customers(db, year, closing)
        
        # Close suppliers
        self._close_suppliers(db, year, closing)
        
        # Update closing data
        closing.closing_data = closing_data
    
    def _close_accounts(self, db: Session, year: FinancialYear, closing: YearClosing):
        """Close accounts for the year"""
        
        # Get all accounts
        accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == year.company_id
        ).all()
        
        for account in accounts:
            # Create closing item
            item = YearClosingItem(
                company_id=year.company_id,
                closing_id=closing.id,
                item_type='account',
                item_id=account.id,
                item_name=account.account_name,
                closing_status='completed',
                processed_date=datetime.utcnow(),
                created_by=closing.created_by
            )
            
            db.add(item)
    
    def _close_transactions(self, db: Session, year: FinancialYear, closing: YearClosing):
        """Close transactions for the year"""
        
        # This would close all transactions within the year
        # Implementation depends on your transaction model
        
        item = YearClosingItem(
            company_id=year.company_id,
            closing_id=closing.id,
            item_type='transaction',
            item_id=0,
            item_name='All Transactions',
            closing_status='completed',
            processed_date=datetime.utcnow(),
            created_by=closing.created_by
        )
        
        db.add(item)
    
    def _close_inventory(self, db: Session, year: FinancialYear, closing: YearClosing):
        """Close inventory for the year"""
        
        # This would close inventory for the year
        # Implementation depends on your inventory model
        
        item = YearClosingItem(
            company_id=year.company_id,
            closing_id=closing.id,
            item_type='inventory',
            item_id=0,
            item_name='All Inventory',
            closing_status='completed',
            processed_date=datetime.utcnow(),
            created_by=closing.created_by
        )
        
        db.add(item)
    
    def _close_customers(self, db: Session, year: FinancialYear, closing: YearClosing):
        """Close customers for the year"""
        
        # This would close customer data for the year
        # Implementation depends on your customer model
        
        item = YearClosingItem(
            company_id=year.company_id,
            closing_id=closing.id,
            item_type='customer',
            item_id=0,
            item_name='All Customers',
            closing_status='completed',
            processed_date=datetime.utcnow(),
            created_by=closing.created_by
        )
        
        db.add(item)
    
    def _close_suppliers(self, db: Session, year: FinancialYear, closing: YearClosing):
        """Close suppliers for the year"""
        
        # This would close supplier data for the year
        # Implementation depends on your supplier model
        
        item = YearClosingItem(
            company_id=year.company_id,
            closing_id=closing.id,
            item_type='supplier',
            item_id=0,
            item_name='All Suppliers',
            closing_status='completed',
            processed_date=datetime.utcnow(),
            created_by=closing.created_by
        )
        
        db.add(item)
    
    # Opening Balance Management
    def create_opening_balance(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int,
        account_id: int,
        debit_balance: Decimal = 0,
        credit_balance: Decimal = 0,
        balance_type: str = 'zero',
        notes: str = None,
        user_id: int = None
    ) -> OpeningBalance:
        """Create opening balance"""
        
        # Validate financial year
        year = db.query(FinancialYear).filter(
            FinancialYear.id == financial_year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not year:
            raise ValueError("Financial year not found")
        
        if year.is_closed:
            raise ValueError("Cannot add opening balance to closed financial year")
        
        # Validate account
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.id == account_id,
            ChartOfAccount.company_id == company_id
        ).first()
        
        if not account:
            raise ValueError("Account not found")
        
        # Check if opening balance already exists
        existing_balance = db.query(OpeningBalance).filter(
            OpeningBalance.financial_year_id == financial_year_id,
            OpeningBalance.account_id == account_id
        ).first()
        
        if existing_balance:
            raise ValueError("Opening balance already exists for this account")
        
        # Create opening balance
        opening_balance = OpeningBalance(
            company_id=company_id,
            financial_year_id=financial_year_id,
            account_id=account_id,
            debit_balance=debit_balance,
            credit_balance=credit_balance,
            balance_type=balance_type,
            notes=notes,
            created_by=user_id
        )
        
        db.add(opening_balance)
        db.commit()
        db.refresh(opening_balance)
        
        logger.info(f"Opening balance created: {account.account_name}")
        
        return opening_balance
    
    def get_opening_balances(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int,
        is_verified: Optional[bool] = None
    ) -> List[OpeningBalance]:
        """Get opening balances"""
        
        query = db.query(OpeningBalance).filter(
            OpeningBalance.company_id == company_id,
            OpeningBalance.financial_year_id == financial_year_id
        )
        
        if is_verified is not None:
            query = query.filter(OpeningBalance.is_verified == is_verified)
        
        balances = query.order_by(OpeningBalance.account_id).all()
        
        return balances
    
    def verify_opening_balance(
        self, 
        db: Session, 
        company_id: int,
        balance_id: int,
        user_id: int = None
    ) -> OpeningBalance:
        """Verify opening balance"""
        
        balance = db.query(OpeningBalance).filter(
            OpeningBalance.id == balance_id,
            OpeningBalance.company_id == company_id
        ).first()
        
        if not balance:
            raise ValueError("Opening balance not found")
        
        if balance.is_verified:
            raise ValueError("Opening balance is already verified")
        
        # Update balance
        balance.is_verified = True
        balance.verified_by = user_id
        balance.verified_date = datetime.utcnow()
        balance.updated_by = user_id
        balance.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Opening balance verified: {balance.account.account_name}")
        
        return balance
    
    # Data Carry Forward Management
    def create_data_carry_forward(
        self, 
        db: Session, 
        company_id: int,
        from_year_id: int,
        to_year_id: int,
        carry_forward_type: str,
        user_id: int = None
    ) -> DataCarryForward:
        """Create data carry forward"""
        
        # Validate years
        from_year = db.query(FinancialYear).filter(
            FinancialYear.id == from_year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not from_year:
            raise ValueError("From year not found")
        
        to_year = db.query(FinancialYear).filter(
            FinancialYear.id == to_year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not to_year:
            raise ValueError("To year not found")
        
        if not from_year.is_closed:
            raise ValueError("From year must be closed before carry forward")
        
        if to_year.is_closed:
            raise ValueError("To year must be active for carry forward")
        
        # Create carry forward record
        carry_forward = DataCarryForward(
            company_id=company_id,
            from_year_id=from_year_id,
            to_year_id=to_year_id,
            carry_forward_type=carry_forward_type,
            carry_forward_status='pending',
            processed_by=user_id,
            created_by=user_id
        )
        
        db.add(carry_forward)
        db.commit()
        db.refresh(carry_forward)
        
        try:
            # Perform carry forward
            self._perform_data_carry_forward(db, carry_forward)
            
            # Update status
            carry_forward.carry_forward_status = 'completed'
            carry_forward.processed_date = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Data carry forward completed: {carry_forward_type}")
            
            return carry_forward
            
        except Exception as e:
            # Update with error
            carry_forward.carry_forward_status = 'failed'
            carry_forward.carry_forward_errors = {"error": str(e)}
            db.commit()
            
            logger.error(f"Data carry forward failed: {str(e)}")
            raise ValueError(f"Data carry forward failed: {str(e)}")
    
    def _perform_data_carry_forward(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Perform data carry forward operations"""
        
        if carry_forward.carry_forward_type == 'opening_balances':
            self._carry_forward_opening_balances(db, carry_forward)
        elif carry_forward.carry_forward_type == 'inventory':
            self._carry_forward_inventory(db, carry_forward)
        elif carry_forward.carry_forward_type == 'customers':
            self._carry_forward_customers(db, carry_forward)
        elif carry_forward.carry_forward_type == 'suppliers':
            self._carry_forward_suppliers(db, carry_forward)
        elif carry_forward.carry_forward_type == 'items':
            self._carry_forward_items(db, carry_forward)
    
    def _carry_forward_opening_balances(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Carry forward opening balances"""
        
        # Get opening balances from previous year
        from_balances = db.query(OpeningBalance).filter(
            OpeningBalance.financial_year_id == carry_forward.from_year_id
        ).all()
        
        for balance in from_balances:
            # Create new opening balance for new year
            new_balance = OpeningBalance(
                company_id=carry_forward.company_id,
                financial_year_id=carry_forward.to_year_id,
                account_id=balance.account_id,
                debit_balance=balance.debit_balance,
                credit_balance=balance.credit_balance,
                balance_type=balance.balance_type,
                created_by=carry_forward.created_by
            )
            
            db.add(new_balance)
    
    def _carry_forward_inventory(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Carry forward inventory"""
        
        # This would carry forward inventory data
        # Implementation depends on your inventory model
        
        pass
    
    def _carry_forward_customers(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Carry forward customers"""
        
        # This would carry forward customer data
        # Implementation depends on your customer model
        
        pass
    
    def _carry_forward_suppliers(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Carry forward suppliers"""
        
        # This would carry forward supplier data
        # Implementation depends on your supplier model
        
        pass
    
    def _carry_forward_items(
        self, 
        db: Session, 
        carry_forward: DataCarryForward
    ):
        """Carry forward items"""
        
        # This would carry forward item data
        # Implementation depends on your item model
        
        pass
    
    # Year Analytics
    def get_year_analytics(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int,
        analytics_date: Optional[date] = None
    ) -> YearAnalytics:
        """Get year analytics"""
        
        # Get or create analytics record
        analytics = db.query(YearAnalytics).filter(
            YearAnalytics.financial_year_id == financial_year_id,
            YearAnalytics.analytics_date == (analytics_date or date.today())
        ).first()
        
        if not analytics:
            # Create new analytics record
            analytics = YearAnalytics(
                company_id=company_id,
                financial_year_id=financial_year_id,
                analytics_date=analytics_date or date.today(),
                created_by=1  # System user
            )
            
            db.add(analytics)
            db.commit()
            db.refresh(analytics)
        
        # Calculate analytics
        self._calculate_year_analytics(db, analytics)
        
        return analytics
    
    def _calculate_year_analytics(
        self, 
        db: Session, 
        analytics: YearAnalytics
    ):
        """Calculate year analytics"""
        
        # This would calculate various analytics
        # Implementation depends on your data models
        
        analytics.total_sales = 0
        analytics.total_purchases = 0
        analytics.total_expenses = 0
        analytics.total_income = 0
        analytics.net_profit = 0
        analytics.total_assets = 0
        analytics.total_liabilities = 0
        analytics.total_equity = 0
        analytics.cash_flow = 0
        analytics.inventory_value = 0
        analytics.customer_count = 0
        analytics.supplier_count = 0
        analytics.transaction_count = 0
        
        # Update analytics data
        analytics.analytics_data = {
            "calculated_date": datetime.utcnow().isoformat(),
            "year_id": analytics.financial_year_id,
            "analytics_date": analytics.analytics_date.isoformat()
        }
        
        db.commit()
    
    # Year Backup Management
    def create_year_backup(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int,
        backup_name: str,
        backup_type: str = 'full',
        user_id: int = None
    ) -> YearBackup:
        """Create year backup"""
        
        # Validate financial year
        year = db.query(FinancialYear).filter(
            FinancialYear.id == financial_year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not year:
            raise ValueError("Financial year not found")
        
        # Create backup record
        backup = YearBackup(
            company_id=company_id,
            financial_year_id=financial_year_id,
            backup_name=backup_name,
            backup_type=backup_type,
            backup_path=f"/backups/{year.year_code}_{backup_name}",
            backup_status='pending',
            backup_by=user_id,
            created_by=user_id
        )
        
        db.add(backup)
        db.commit()
        db.refresh(backup)
        
        try:
            # Perform backup
            self._perform_year_backup(db, backup)
            
            # Update backup status
            backup.backup_status = 'completed'
            backup.backup_size = 1024 * 1024  # 1MB placeholder
            backup.backup_data = {
                "backup_date": datetime.utcnow().isoformat(),
                "backup_type": backup_type,
                "year_name": year.year_name
            }
            
            db.commit()
            
            logger.info(f"Year backup created: {backup_name}")
            
            return backup
            
        except Exception as e:
            # Update backup with error
            backup.backup_status = 'failed'
            backup.backup_errors = {"error": str(e)}
            db.commit()
            
            logger.error(f"Year backup failed: {str(e)}")
            raise ValueError(f"Year backup failed: {str(e)}")
    
    def _perform_year_backup(
        self, 
        db: Session, 
        backup: YearBackup
    ):
        """Perform year backup"""
        
        # This would perform the actual backup
        # Implementation depends on your backup strategy
        
        pass
    
    # Year Report Generation
    def generate_year_report(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int,
        report_name: str,
        report_type: str,
        user_id: int = None
    ) -> YearReport:
        """Generate year report"""
        
        # Validate financial year
        year = db.query(FinancialYear).filter(
            FinancialYear.id == financial_year_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not year:
            raise ValueError("Financial year not found")
        
        # Create report record
        report = YearReport(
            company_id=company_id,
            financial_year_id=financial_year_id,
            report_name=report_name,
            report_type=report_type,
            report_data={},
            report_status='pending',
            generated_by=user_id,
            created_by=user_id
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        try:
            # Generate report data
            report_data = self._generate_year_report_data(db, year, report_type)
            
            # Update report
            report.report_data = report_data
            report.report_status = 'generated'
            report.generated_date = datetime.utcnow()
            report.report_file_path = f"/reports/{year.year_code}_{report_name}.pdf"
            report.report_file_size = 1024 * 1024  # 1MB placeholder
            
            db.commit()
            
            logger.info(f"Year report generated: {report_name}")
            
            return report
            
        except Exception as e:
            # Update report with error
            report.report_status = 'failed'
            report.report_data = {"error": str(e)}
            db.commit()
            
            logger.error(f"Year report generation failed: {str(e)}")
            raise ValueError(f"Year report generation failed: {str(e)}")
    
    def _generate_year_report_data(
        self, 
        db: Session, 
        year: FinancialYear, 
        report_type: str
    ) -> Dict:
        """Generate year report data"""
        
        # This would generate the actual report data
        # Implementation depends on your report requirements
        
        return {
            "report_type": report_type,
            "year_name": year.year_name,
            "year_code": year.year_code,
            "start_date": year.start_date.isoformat(),
            "end_date": year.end_date.isoformat(),
            "generated_date": datetime.utcnow().isoformat()
        }

# Global service instance
financial_year_management_service = FinancialYearManagementService()