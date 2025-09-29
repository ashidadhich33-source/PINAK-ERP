# backend/app/services/company_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.core import Company, UserCompany, FinancialYear, GSTSlab, ChartOfAccount
from ..models.core import User

logger = logging.getLogger(__name__)

class CompanyService:
    """Service class for company management operations"""
    
    def __init__(self):
        pass
    
    def create_company(self, db: Session, company_data: dict, user_id: int) -> Company:
        """Create a new company with default setup"""
        
        # Create company
        company = Company(
            **company_data,
            created_by=user_id
        )
        
        db.add(company)
        db.commit()
        db.refresh(company)
        
        # Create user-company association
        user_company = UserCompany(
            user_id=user_id,
            company_id=company.id,
            role="admin",
            is_active=True,
            is_default=True
        )
        
        db.add(user_company)
        
        # Create default financial year
        financial_year = FinancialYear(
            company_id=company.id,
            year_name=company.current_financial_year,
            start_date=company.financial_year_start,
            end_date=company.financial_year_end,
            is_active=True,
            created_by=user_id
        )
        
        db.add(financial_year)
        
        # Create default GST slabs
        self._create_default_gst_slabs(db, company.id, user_id)
        
        # Create default chart of accounts
        self._create_default_chart_of_accounts(db, company.id, user_id)
        
        db.commit()
        
        logger.info(f"Company created: {company.name} (ID: {company.id})")
        
        return company
    
    def _create_default_gst_slabs(self, db: Session, company_id: int, user_id: int):
        """Create default GST slabs for company"""
        
        default_slabs = [
            {
                "rate": Decimal('0.00'),
                "cgst_rate": Decimal('0.00'),
                "sgst_rate": Decimal('0.00'),
                "igst_rate": Decimal('0.00'),
                "description": "0% GST",
                "is_default": True
            },
            {
                "rate": Decimal('5.00'),
                "cgst_rate": Decimal('2.50'),
                "sgst_rate": Decimal('2.50'),
                "igst_rate": Decimal('5.00'),
                "description": "5% GST"
            },
            {
                "rate": Decimal('12.00'),
                "cgst_rate": Decimal('6.00'),
                "sgst_rate": Decimal('6.00'),
                "igst_rate": Decimal('12.00'),
                "description": "12% GST"
            },
            {
                "rate": Decimal('18.00'),
                "cgst_rate": Decimal('9.00'),
                "sgst_rate": Decimal('9.00'),
                "igst_rate": Decimal('18.00'),
                "description": "18% GST",
                "is_default": True
            },
            {
                "rate": Decimal('28.00'),
                "cgst_rate": Decimal('14.00'),
                "sgst_rate": Decimal('14.00'),
                "igst_rate": Decimal('28.00'),
                "description": "28% GST"
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
    
    def _create_default_chart_of_accounts(self, db: Session, company_id: int, user_id: int):
        """Create default chart of accounts for company"""
        
        # Indian Chart of Accounts structure
        accounts = [
            # Assets
            {"code": "1000", "name": "ASSETS", "type": "asset", "balance_type": "debit", "level": 1},
            {"code": "1100", "name": "Current Assets", "type": "asset", "balance_type": "debit", "level": 2, "parent_code": "1000"},
            {"code": "1110", "name": "Cash and Bank", "type": "asset", "balance_type": "debit", "level": 3, "parent_code": "1100"},
            {"code": "1111", "name": "Cash in Hand", "type": "asset", "balance_type": "debit", "level": 4, "parent_code": "1110"},
            {"code": "1112", "name": "Bank Account", "type": "asset", "balance_type": "debit", "level": 4, "parent_code": "1110"},
            {"code": "1120", "name": "Accounts Receivable", "type": "asset", "balance_type": "debit", "level": 3, "parent_code": "1100"},
            {"code": "1130", "name": "Inventory", "type": "asset", "balance_type": "debit", "level": 3, "parent_code": "1100"},
            {"code": "1140", "name": "GST Input Credit", "type": "asset", "balance_type": "debit", "level": 3, "parent_code": "1100", "is_gst_applicable": True},
            
            # Liabilities
            {"code": "2000", "name": "LIABILITIES", "type": "liability", "balance_type": "credit", "level": 1},
            {"code": "2100", "name": "Current Liabilities", "type": "liability", "balance_type": "credit", "level": 2, "parent_code": "2000"},
            {"code": "2110", "name": "Accounts Payable", "type": "liability", "balance_type": "credit", "level": 3, "parent_code": "2100"},
            {"code": "2120", "name": "GST Payable", "type": "liability", "balance_type": "credit", "level": 3, "parent_code": "2100", "is_gst_applicable": True},
            {"code": "2130", "name": "TDS Payable", "type": "liability", "balance_type": "credit", "level": 3, "parent_code": "2100"},
            
            # Equity
            {"code": "3000", "name": "EQUITY", "type": "equity", "balance_type": "credit", "level": 1},
            {"code": "3100", "name": "Owner's Equity", "type": "equity", "balance_type": "credit", "level": 2, "parent_code": "3000"},
            {"code": "3110", "name": "Capital", "type": "equity", "balance_type": "credit", "level": 3, "parent_code": "3100"},
            {"code": "3120", "name": "Retained Earnings", "type": "equity", "balance_type": "credit", "level": 3, "parent_code": "3100"},
            
            # Income
            {"code": "4000", "name": "INCOME", "type": "income", "balance_type": "credit", "level": 1},
            {"code": "4100", "name": "Sales Revenue", "type": "income", "balance_type": "credit", "level": 2, "parent_code": "4000"},
            {"code": "4110", "name": "Product Sales", "type": "income", "balance_type": "credit", "level": 3, "parent_code": "4100"},
            {"code": "4120", "name": "Service Revenue", "type": "income", "balance_type": "credit", "level": 3, "parent_code": "4100"},
            {"code": "4200", "name": "Other Income", "type": "income", "balance_type": "credit", "level": 2, "parent_code": "4000"},
            
            # Expenses
            {"code": "5000", "name": "EXPENSES", "type": "expense", "balance_type": "debit", "level": 1},
            {"code": "5100", "name": "Cost of Goods Sold", "type": "expense", "balance_type": "debit", "level": 2, "parent_code": "5000"},
            {"code": "5110", "name": "Purchase of Goods", "type": "expense", "balance_type": "debit", "level": 3, "parent_code": "5100"},
            {"code": "5200", "name": "Operating Expenses", "type": "expense", "balance_type": "debit", "level": 2, "parent_code": "5000"},
            {"code": "5210", "name": "Rent", "type": "expense", "balance_type": "debit", "level": 3, "parent_code": "5200"},
            {"code": "5220", "name": "Salaries", "type": "expense", "balance_type": "debit", "level": 3, "parent_code": "5200"},
            {"code": "5230", "name": "Utilities", "type": "expense", "balance_type": "debit", "level": 3, "parent_code": "5200"},
        ]
        
        # Create accounts with proper hierarchy
        account_map = {}
        
        for account_data in accounts:
            parent_id = None
            if "parent_code" in account_data:
                parent_id = account_map.get(account_data["parent_code"])
            
            account = ChartOfAccount(
                company_id=company_id,
                account_code=account_data["code"],
                account_name=account_data["name"],
                account_type=account_data["type"],
                balance_type=account_data["balance_type"],
                level=account_data["level"],
                parent_id=parent_id,
                is_gst_applicable=account_data.get("is_gst_applicable", False),
                is_system_account=True,
                created_by=user_id
            )
            
            db.add(account)
            db.flush()  # Get the ID
            
            account_map[account_data["code"]] = account.id
    
    def get_user_companies(self, db: Session, user_id: int) -> List[Company]:
        """Get all companies accessible to user"""
        
        user_companies = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.is_active == True
        ).all()
        
        company_ids = [uc.company_id for uc in user_companies]
        
        if not company_ids:
            return []
        
        companies = db.query(Company).filter(
            Company.id.in_(company_ids),
            Company.is_active == True
        ).all()
        
        return companies
    
    def get_company_by_id(self, db: Session, company_id: int, user_id: int) -> Optional[Company]:
        """Get company by ID if user has access"""
        
        # Check if user has access to this company
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id,
            UserCompany.is_active == True
        ).first()
        
        if not user_company:
            return None
        
        company = db.query(Company).filter(
            Company.id == company_id,
            Company.is_active == True
        ).first()
        
        return company
    
    def add_user_to_company(self, db: Session, company_id: int, user_id: int, role: str = "user", permissions: dict = None) -> UserCompany:
        """Add user to company"""
        
        # Check if user is already associated
        existing = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id
        ).first()
        
        if existing:
            raise ValueError("User is already associated with this company")
        
        user_company = UserCompany(
            user_id=user_id,
            company_id=company_id,
            role=role,
            is_active=True,
            permissions=json.dumps(permissions) if permissions else None
        )
        
        db.add(user_company)
        db.commit()
        db.refresh(user_company)
        
        return user_company
    
    def remove_user_from_company(self, db: Session, company_id: int, user_id: int):
        """Remove user from company"""
        
        user_company = db.query(UserCompany).filter(
            UserCompany.user_id == user_id,
            UserCompany.company_id == company_id
        ).first()
        
        if user_company:
            user_company.is_active = False
            db.commit()
    
    def get_company_users(self, db: Session, company_id: int) -> List[UserCompany]:
        """Get all users associated with company"""
        
        user_companies = db.query(UserCompany).filter(
            UserCompany.company_id == company_id
        ).all()
        
        return user_companies
    
    def get_active_financial_year(self, db: Session, company_id: int) -> Optional[FinancialYear]:
        """Get active financial year for company"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.company_id == company_id,
            FinancialYear.is_active == True
        ).first()
        
        return financial_year
    
    def create_financial_year(self, db: Session, company_id: int, year_name: str, start_date: date, end_date: date, user_id: int) -> FinancialYear:
        """Create new financial year"""
        
        # Deactivate current financial year
        current_fy = self.get_active_financial_year(db, company_id)
        if current_fy:
            current_fy.is_active = False
        
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
        
        return financial_year
    
    def close_financial_year(self, db: Session, company_id: int, user_id: int, closing_remarks: str = None) -> FinancialYear:
        """Close current financial year"""
        
        financial_year = self.get_active_financial_year(db, company_id)
        if not financial_year:
            raise ValueError("No active financial year found")
        
        financial_year.is_closed = True
        financial_year.closed_at = datetime.utcnow()
        financial_year.closed_by = user_id
        financial_year.closing_remarks = closing_remarks
        
        db.commit()
        
        return financial_year
    
    def get_gst_slabs(self, db: Session, company_id: int, effective_date: date = None) -> List[GSTSlab]:
        """Get GST slabs for company"""
        
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
        ).all()
        
        return gst_slabs
    
    def get_chart_of_accounts(self, db: Session, company_id: int, account_type: str = None) -> List[ChartOfAccount]:
        """Get chart of accounts for company"""
        
        query = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.is_active == True
        )
        
        if account_type:
            query = query.filter(ChartOfAccount.account_type == account_type)
        
        accounts = query.order_by(ChartOfAccount.account_code).all()
        
        return accounts

# Global service instance
company_service = CompanyService()