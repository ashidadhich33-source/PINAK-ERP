# backend/app/services/chart_of_accounts_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.company import Company, ChartOfAccount
from ..models.sales import SalesInvoice, SalesInvoiceItem
from ..models.purchase import PurchaseBill, PurchaseBillItem

logger = logging.getLogger(__name__)

class ChartOfAccountsService:
    """Service class for chart of accounts management"""
    
    def __init__(self):
        pass
    
    def create_account(
        self, 
        db: Session, 
        company_id: int,
        account_code: str,
        account_name: str,
        account_type: str,
        parent_id: Optional[int] = None,
        gst_applicable: bool = False,
        user_id: int = None
    ) -> ChartOfAccount:
        """Create new chart of account"""
        
        # Validate account code uniqueness
        existing_account = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_code == account_code
        ).first()
        
        if existing_account:
            raise ValueError(f"Account code {account_code} already exists")
        
        # Validate parent account if provided
        if parent_id:
            parent_account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == parent_id,
                ChartOfAccount.company_id == company_id
            ).first()
            
            if not parent_account:
                raise ValueError("Parent account not found")
            
            if parent_account.account_type != account_type:
                raise ValueError("Parent and child accounts must have same type")
        
        # Create account
        account = ChartOfAccount(
            company_id=company_id,
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            parent_id=parent_id,
            gst_applicable=gst_applicable,
            created_by=user_id
        )
        
        db.add(account)
        db.commit()
        db.refresh(account)
        
        logger.info(f"Account created: {account_code} - {account_name}")
        
        return account
    
    def get_account_by_id(
        self, 
        db: Session, 
        company_id: int,
        account_id: int
    ) -> Optional[ChartOfAccount]:
        """Get account by ID"""
        
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.id == account_id,
            ChartOfAccount.company_id == company_id
        ).first()
        
        return account
    
    def get_account_by_code(
        self, 
        db: Session, 
        company_id: int,
        account_code: str
    ) -> Optional[ChartOfAccount]:
        """Get account by code"""
        
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_code == account_code
        ).first()
        
        return account
    
    def list_accounts(
        self, 
        db: Session, 
        company_id: int,
        account_type: Optional[str] = None,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[ChartOfAccount]:
        """List accounts for company"""
        
        query = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        )
        
        if account_type:
            query = query.filter(ChartOfAccount.account_type == account_type)
        
        if parent_id is not None:
            query = query.filter(ChartOfAccount.parent_id == parent_id)
        
        if is_active is not None:
            query = query.filter(ChartOfAccount.is_active == is_active)
        
        accounts = query.order_by(ChartOfAccount.account_code).all()
        
        return accounts
    
    def get_account_hierarchy(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get account hierarchy"""
        
        # Get all accounts
        accounts = self.list_accounts(db, company_id)
        
        # Build hierarchy
        hierarchy = {}
        root_accounts = []
        
        for account in accounts:
            if account.parent_id is None:
                root_accounts.append(account)
            else:
                if account.parent_id not in hierarchy:
                    hierarchy[account.parent_id] = []
                hierarchy[account.parent_id].append(account)
        
        # Build tree structure
        def build_tree(account):
            children = hierarchy.get(account.id, [])
            return {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "gst_applicable": account.gst_applicable,
                "is_active": account.is_active,
                "children": [build_tree(child) for child in children]
            }
        
        tree = [build_tree(account) for account in root_accounts]
        
        return {
            "hierarchy": tree,
            "total_accounts": len(accounts)
        }
    
    def update_account(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        account_data: Dict,
        user_id: int = None
    ) -> ChartOfAccount:
        """Update account"""
        
        account = self.get_account_by_id(db, company_id, account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Update account fields
        for field, value in account_data.items():
            if hasattr(account, field):
                setattr(account, field, value)
        
        account.updated_by = user_id
        account.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(account)
        
        logger.info(f"Account updated: {account.account_code}")
        
        return account
    
    def delete_account(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        user_id: int = None
    ) -> bool:
        """Delete account (soft delete)"""
        
        account = self.get_account_by_id(db, company_id, account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Check if account has children
        children = db.query(ChartOfAccount).filter(
            ChartOfAccount.parent_id == account_id,
            ChartOfAccount.company_id == company_id
        ).count()
        
        if children > 0:
            raise ValueError("Cannot delete account with child accounts")
        
        # Soft delete
        account.is_active = False
        account.updated_by = user_id
        account.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Account deleted: {account.account_code}")
        
        return True
    
    def create_indian_chart_of_accounts(
        self, 
        db: Session, 
        company_id: int,
        user_id: int = None
    ) -> List[ChartOfAccount]:
        """Create Indian chart of accounts"""
        
        # Check if accounts already exist
        existing_count = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        ).count()
        
        if existing_count > 0:
            logger.info("Chart of accounts already exists for company")
            return []
        
        # Indian Chart of Accounts structure
        indian_coa = [
            # Assets
            {"code": "1000", "name": "ASSETS", "type": "Asset", "parent": None},
            {"code": "1100", "name": "Current Assets", "type": "Asset", "parent": "1000"},
            {"code": "1110", "name": "Cash and Cash Equivalents", "type": "Asset", "parent": "1100"},
            {"code": "1111", "name": "Cash in Hand", "type": "Asset", "parent": "1110"},
            {"code": "1112", "name": "Bank Account", "type": "Asset", "parent": "1110"},
            {"code": "1120", "name": "Accounts Receivable", "type": "Asset", "parent": "1100"},
            {"code": "1121", "name": "Trade Receivables", "type": "Asset", "parent": "1120"},
            {"code": "1122", "name": "Other Receivables", "type": "Asset", "parent": "1120"},
            {"code": "1130", "name": "Inventory", "type": "Asset", "parent": "1100"},
            {"code": "1131", "name": "Raw Materials", "type": "Asset", "parent": "1130"},
            {"code": "1132", "name": "Finished Goods", "type": "Asset", "parent": "1130"},
            {"code": "1140", "name": "Prepaid Expenses", "type": "Asset", "parent": "1100"},
            {"code": "1200", "name": "Fixed Assets", "type": "Asset", "parent": "1000"},
            {"code": "1210", "name": "Property, Plant & Equipment", "type": "Asset", "parent": "1200"},
            {"code": "1211", "name": "Land", "type": "Asset", "parent": "1210"},
            {"code": "1212", "name": "Building", "type": "Asset", "parent": "1210"},
            {"code": "1213", "name": "Machinery", "type": "Asset", "parent": "1210"},
            {"code": "1220", "name": "Accumulated Depreciation", "type": "Asset", "parent": "1200"},
            
            # Liabilities
            {"code": "2000", "name": "LIABILITIES", "type": "Liability", "parent": None},
            {"code": "2100", "name": "Current Liabilities", "type": "Liability", "parent": "2000"},
            {"code": "2110", "name": "Accounts Payable", "type": "Liability", "parent": "2100"},
            {"code": "2111", "name": "Trade Payables", "type": "Liability", "parent": "2110"},
            {"code": "2112", "name": "Other Payables", "type": "Liability", "parent": "2110"},
            {"code": "2120", "name": "GST Payable", "type": "Liability", "parent": "2100", "gst_applicable": True},
            {"code": "2121", "name": "CGST Payable", "type": "Liability", "parent": "2120", "gst_applicable": True},
            {"code": "2122", "name": "SGST Payable", "type": "Liability", "parent": "2120", "gst_applicable": True},
            {"code": "2123", "name": "IGST Payable", "type": "Liability", "parent": "2120", "gst_applicable": True},
            {"code": "2130", "name": "Accrued Expenses", "type": "Liability", "parent": "2100"},
            {"code": "2200", "name": "Long-term Liabilities", "type": "Liability", "parent": "2000"},
            {"code": "2210", "name": "Loans Payable", "type": "Liability", "parent": "2200"},
            
            # Equity
            {"code": "3000", "name": "EQUITY", "type": "Equity", "parent": None},
            {"code": "3100", "name": "Share Capital", "type": "Equity", "parent": "3000"},
            {"code": "3200", "name": "Retained Earnings", "type": "Equity", "parent": "3000"},
            {"code": "3300", "name": "Current Year Profit/Loss", "type": "Equity", "parent": "3000"},
            
            # Income
            {"code": "4000", "name": "INCOME", "type": "Income", "parent": None},
            {"code": "4100", "name": "Sales Revenue", "type": "Income", "parent": "4000"},
            {"code": "4110", "name": "Product Sales", "type": "Income", "parent": "4100"},
            {"code": "4120", "name": "Service Revenue", "type": "Income", "parent": "4100"},
            {"code": "4200", "name": "Other Income", "type": "Income", "parent": "4000"},
            {"code": "4210", "name": "Interest Income", "type": "Income", "parent": "4200"},
            {"code": "4220", "name": "Rental Income", "type": "Income", "parent": "4200"},
            
            # Expenses
            {"code": "5000", "name": "EXPENSES", "type": "Expense", "parent": None},
            {"code": "5100", "name": "Cost of Goods Sold", "type": "Expense", "parent": "5000"},
            {"code": "5110", "name": "Raw Material Cost", "type": "Expense", "parent": "5100"},
            {"code": "5120", "name": "Direct Labor", "type": "Expense", "parent": "5100"},
            {"code": "5200", "name": "Operating Expenses", "type": "Expense", "parent": "5000"},
            {"code": "5210", "name": "Rent Expense", "type": "Expense", "parent": "5200"},
            {"code": "5220", "name": "Utilities", "type": "Expense", "parent": "5200"},
            {"code": "5230", "name": "Salaries", "type": "Expense", "parent": "5200"},
            {"code": "5240", "name": "Marketing", "type": "Expense", "parent": "5200"},
            {"code": "5300", "name": "Administrative Expenses", "type": "Expense", "parent": "5000"},
            {"code": "5310", "name": "Office Supplies", "type": "Expense", "parent": "5300"},
            {"code": "5320", "name": "Professional Fees", "type": "Expense", "parent": "5300"},
            {"code": "5400", "name": "Financial Expenses", "type": "Expense", "parent": "5000"},
            {"code": "5410", "name": "Interest Expense", "type": "Expense", "parent": "5400"},
            {"code": "5420", "name": "Bank Charges", "type": "Expense", "parent": "5400"}
        ]
        
        created_accounts = []
        
        # Create accounts in order
        for account_data in indian_coa:
            parent_id = None
            if account_data["parent"]:
                parent_account = db.query(ChartOfAccount).filter(
                    ChartOfAccount.company_id == company_id,
                    ChartOfAccount.account_code == account_data["parent"]
                ).first()
                if parent_account:
                    parent_id = parent_account.id
            
            account = ChartOfAccount(
                company_id=company_id,
                account_code=account_data["code"],
                account_name=account_data["name"],
                account_type=account_data["type"],
                parent_id=parent_id,
                gst_applicable=account_data.get("gst_applicable", False),
                created_by=user_id
            )
            
            db.add(account)
            created_accounts.append(account)
        
        db.commit()
        
        logger.info(f"Created {len(created_accounts)} accounts for Indian chart of accounts")
        
        return created_accounts
    
    def get_account_balance(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get account balance for period"""
        
        account = self.get_account_by_id(db, company_id, account_id)
        if not account:
            raise ValueError("Account not found")
        
        # This would require implementing journal entries
        # For now, return basic structure
        return {
            "account": {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type
            },
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "opening_balance": Decimal('0'),
            "debit_total": Decimal('0'),
            "credit_total": Decimal('0'),
            "closing_balance": Decimal('0'),
            "balance_type": "debit" if account.account_type in ["Asset", "Expense"] else "credit"
        }
    
    def get_trial_balance(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get trial balance for period"""
        
        accounts = self.list_accounts(db, company_id, is_active=True)
        
        trial_balance = []
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for account in accounts:
            balance = self.get_account_balance(db, company_id, account.id, from_date, to_date)
            
            trial_balance.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "debit_balance": balance["debit_total"],
                "credit_balance": balance["credit_total"],
                "closing_balance": balance["closing_balance"]
            })
            
            total_debit += balance["debit_total"]
            total_credit += balance["credit_total"]
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "trial_balance": trial_balance,
            "totals": {
                "total_debit": total_debit,
                "total_credit": total_credit,
                "difference": total_debit - total_credit,
                "is_balanced": total_debit == total_credit
            }
        }
    
    def get_balance_sheet(
        self, 
        db: Session, 
        company_id: int,
        as_on_date: date
    ) -> Dict:
        """Get balance sheet as on date"""
        
        # Get asset accounts
        asset_accounts = self.list_accounts(db, company_id, account_type="Asset", is_active=True)
        
        # Get liability accounts
        liability_accounts = self.list_accounts(db, company_id, account_type="Liability", is_active=True)
        
        # Get equity accounts
        equity_accounts = self.list_accounts(db, company_id, account_type="Equity", is_active=True)
        
        # Calculate balances
        assets = []
        liabilities = []
        equity = []
        
        total_assets = Decimal('0')
        total_liabilities = Decimal('0')
        total_equity = Decimal('0')
        
        for account in asset_accounts:
            balance = self.get_account_balance(db, company_id, account.id, None, as_on_date)
            assets.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "balance": balance["closing_balance"]
            })
            total_assets += balance["closing_balance"]
        
        for account in liability_accounts:
            balance = self.get_account_balance(db, company_id, account.id, None, as_on_date)
            liabilities.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "balance": balance["closing_balance"]
            })
            total_liabilities += balance["closing_balance"]
        
        for account in equity_accounts:
            balance = self.get_account_balance(db, company_id, account.id, None, as_on_date)
            equity.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "balance": balance["closing_balance"]
            })
            total_equity += balance["closing_balance"]
        
        return {
            "as_on_date": as_on_date,
            "assets": {
                "accounts": assets,
                "total": total_assets
            },
            "liabilities": {
                "accounts": liabilities,
                "total": total_liabilities
            },
            "equity": {
                "accounts": equity,
                "total": total_equity
            },
            "totals": {
                "total_assets": total_assets,
                "total_liabilities_equity": total_liabilities + total_equity,
                "is_balanced": total_assets == (total_liabilities + total_equity)
            }
        }
    
    def get_profit_loss(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Get profit and loss statement for period"""
        
        # Get income accounts
        income_accounts = self.list_accounts(db, company_id, account_type="Income", is_active=True)
        
        # Get expense accounts
        expense_accounts = self.list_accounts(db, company_id, account_type="Expense", is_active=True)
        
        # Calculate balances
        income = []
        expenses = []
        
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        
        for account in income_accounts:
            balance = self.get_account_balance(db, company_id, account.id, from_date, to_date)
            income.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "balance": balance["closing_balance"]
            })
            total_income += balance["closing_balance"]
        
        for account in expense_accounts:
            balance = self.get_account_balance(db, company_id, account.id, from_date, to_date)
            expenses.append({
                "account_code": account.account_code,
                "account_name": account.account_name,
                "balance": balance["closing_balance"]
            })
            total_expenses += balance["closing_balance"]
        
        net_profit = total_income - total_expenses
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "income": {
                "accounts": income,
                "total": total_income
            },
            "expenses": {
                "accounts": expenses,
                "total": total_expenses
            },
            "net_profit": net_profit,
            "net_profit_percentage": (net_profit / total_income * 100) if total_income > 0 else Decimal('0')
        }
    
    def export_chart_of_accounts_excel(
        self, 
        db: Session, 
        company_id: int
    ) -> bytes:
        """Export chart of accounts to Excel"""
        
        import pandas as pd
        import io
        
        accounts = self.list_accounts(db, company_id, is_active=True)
        
        # Prepare data for Excel
        excel_data = []
        
        for account in accounts:
            excel_data.append({
                "Account Code": account.account_code,
                "Account Name": account.account_name,
                "Account Type": account.account_type,
                "Parent Account": account.parent_id,
                "GST Applicable": account.gst_applicable,
                "Is Active": account.is_active,
                "Created At": account.created_at,
                "Updated At": account.updated_at
            })
        
        # Create Excel file
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df = pd.DataFrame(excel_data)
            df.to_excel(writer, sheet_name='Chart of Accounts', index=False)
        
        output.seek(0)
        return output.getvalue()

# Global service instance
chart_of_accounts_service = ChartOfAccountsService()