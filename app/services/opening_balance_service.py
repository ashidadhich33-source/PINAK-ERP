# backend/app/services/opening_balance_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.company import Company, FinancialYear, ChartOfAccount
from ..models.customer import Customer
from ..models.supplier import Supplier
from ..models.item import Item
from ..models.stock import StockItem

logger = logging.getLogger(__name__)

class OpeningBalanceService:
    """Service class for opening balance management"""
    
    def __init__(self):
        pass
    
    def create_opening_balance_entry(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        account_id: int,
        debit_amount: Decimal = Decimal('0'),
        credit_amount: Decimal = Decimal('0'),
        user_id: int = None
    ) -> Dict:
        """Create opening balance entry for an account"""
        
        # Validate financial year
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Cannot create opening balances for closed financial year")
        
        # Validate account
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.id == account_id,
            ChartOfAccount.company_id == company_id
        ).first()
        
        if not account:
            raise ValueError("Account not found")
        
        # Validate amounts
        if debit_amount < 0 or credit_amount < 0:
            raise ValueError("Amounts cannot be negative")
        
        if debit_amount > 0 and credit_amount > 0:
            raise ValueError("Cannot have both debit and credit amounts")
        
        # Create opening balance entry
        opening_balance = {
            "account_id": account_id,
            "account_code": account.account_code,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "debit_amount": debit_amount,
            "credit_amount": credit_amount,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": user_id
        }
        
        # Update financial year opening balances
        current_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        if "account_balances" not in current_balances:
            current_balances["account_balances"] = {}
        
        current_balances["account_balances"][str(account_id)] = opening_balance
        
        financial_year.opening_balances = json.dumps(current_balances)
        financial_year.updated_by = user_id
        financial_year.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Opening balance created for account {account.account_name}")
        
        return opening_balance
    
    def get_opening_balances(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Get opening balances for financial year"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        opening_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        return opening_balances
    
    def update_opening_balance(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        account_id: int,
        debit_amount: Decimal = Decimal('0'),
        credit_amount: Decimal = Decimal('0'),
        user_id: int = None
    ) -> Dict:
        """Update opening balance for an account"""
        
        # Validate financial year
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Cannot update opening balances for closed financial year")
        
        # Get current opening balances
        current_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        if "account_balances" not in current_balances:
            current_balances["account_balances"] = {}
        
        # Update account balance
        current_balances["account_balances"][str(account_id)] = {
            "account_id": account_id,
            "debit_amount": debit_amount,
            "credit_amount": credit_amount,
            "updated_at": datetime.utcnow().isoformat(),
            "updated_by": user_id
        }
        
        financial_year.opening_balances = json.dumps(current_balances)
        financial_year.updated_by = user_id
        financial_year.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Opening balance updated for account {account_id}")
        
        return current_balances["account_balances"][str(account_id)]
    
    def delete_opening_balance(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        account_id: int,
        user_id: int = None
    ) -> bool:
        """Delete opening balance for an account"""
        
        # Validate financial year
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Cannot delete opening balances for closed financial year")
        
        # Get current opening balances
        current_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        if "account_balances" in current_balances and str(account_id) in current_balances["account_balances"]:
            del current_balances["account_balances"][str(account_id)]
            
            financial_year.opening_balances = json.dumps(current_balances)
            financial_year.updated_by = user_id
            financial_year.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Opening balance deleted for account {account_id}")
            return True
        
        return False
    
    def validate_opening_balances(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Validate opening balances for financial year"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        opening_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        # Get account balances
        account_balances = opening_balances.get("account_balances", {})
        
        # Calculate totals
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for account_id, balance in account_balances.items():
            total_debit += Decimal(str(balance.get('debit_amount', 0)))
            total_credit += Decimal(str(balance.get('credit_amount', 0)))
        
        # Check if debits equal credits
        is_balanced = total_debit == total_credit
        
        # Get account details
        account_details = []
        for account_id, balance in account_balances.items():
            account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == int(account_id),
                ChartOfAccount.company_id == company_id
            ).first()
            
            if account:
                account_details.append({
                    "account_id": account.id,
                    "account_code": account.account_code,
                    "account_name": account.account_name,
                    "account_type": account.account_type,
                    "debit_amount": balance.get('debit_amount', 0),
                    "credit_amount": balance.get('credit_amount', 0)
                })
        
        return {
            "is_balanced": is_balanced,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "difference": total_debit - total_credit,
            "account_count": len(account_balances),
            "account_details": account_details,
            "validation_message": "Opening balances are balanced" if is_balanced else "Opening balances are not balanced"
        }
    
    def create_opening_balances_bulk(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        opening_balances: List[Dict],
        user_id: int = None
    ) -> Dict:
        """Create multiple opening balance entries"""
        
        # Validate financial year
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        if financial_year.is_closed:
            raise ValueError("Cannot create opening balances for closed financial year")
        
        # Get current opening balances
        current_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        if "account_balances" not in current_balances:
            current_balances["account_balances"] = {}
        
        created_balances = []
        
        for balance_data in opening_balances:
            account_id = balance_data.get('account_id')
            debit_amount = Decimal(str(balance_data.get('debit_amount', 0)))
            credit_amount = Decimal(str(balance_data.get('credit_amount', 0)))
            
            # Validate account
            account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == account_id,
                ChartOfAccount.company_id == company_id
            ).first()
            
            if not account:
                continue
            
            # Create balance entry
            balance_entry = {
                "account_id": account_id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type,
                "debit_amount": debit_amount,
                "credit_amount": credit_amount,
                "created_at": datetime.utcnow().isoformat(),
                "created_by": user_id
            }
            
            current_balances["account_balances"][str(account_id)] = balance_entry
            created_balances.append(balance_entry)
        
        # Update financial year
        financial_year.opening_balances = json.dumps(current_balances)
        financial_year.updated_by = user_id
        financial_year.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Created {len(created_balances)} opening balance entries")
        
        return {
            "created_count": len(created_balances),
            "balances": created_balances
        }
    
    def get_opening_balance_summary(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Get opening balance summary"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        opening_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        
        # Get account balances
        account_balances = opening_balances.get("account_balances", {})
        
        # Calculate totals by account type
        totals_by_type = {}
        
        for account_id, balance in account_balances.items():
            account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == int(account_id),
                ChartOfAccount.company_id == company_id
            ).first()
            
            if account:
                account_type = account.account_type
                if account_type not in totals_by_type:
                    totals_by_type[account_type] = {
                        "debit_total": Decimal('0'),
                        "credit_total": Decimal('0'),
                        "account_count": 0
                    }
                
                totals_by_type[account_type]["debit_total"] += Decimal(str(balance.get('debit_amount', 0)))
                totals_by_type[account_type]["credit_total"] += Decimal(str(balance.get('credit_amount', 0)))
                totals_by_type[account_type]["account_count"] += 1
        
        # Calculate grand totals
        grand_debit = sum(totals_by_type[acc_type]["debit_total"] for acc_type in totals_by_type)
        grand_credit = sum(totals_by_type[acc_type]["credit_total"] for acc_type in totals_by_type)
        
        return {
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date,
                "end_date": financial_year.end_date
            },
            "totals_by_type": totals_by_type,
            "grand_totals": {
                "total_debit": grand_debit,
                "total_credit": grand_credit,
                "difference": grand_debit - grand_credit,
                "is_balanced": grand_debit == grand_credit
            },
            "summary": {
                "total_accounts": len(account_balances),
                "account_types": list(totals_by_type.keys())
            }
        }
    
    def export_opening_balances_excel(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> bytes:
        """Export opening balances to Excel"""
        
        import pandas as pd
        import io
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        opening_balances = json.loads(financial_year.opening_balances) if financial_year.opening_balances else {}
        account_balances = opening_balances.get("account_balances", {})
        
        # Prepare data for Excel
        excel_data = []
        
        for account_id, balance in account_balances.items():
            account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == int(account_id),
                ChartOfAccount.company_id == company_id
            ).first()
            
            if account:
                excel_data.append({
                    "Account Code": account.account_code,
                    "Account Name": account.account_name,
                    "Account Type": account.account_type,
                    "Debit Amount": balance.get('debit_amount', 0),
                    "Credit Amount": balance.get('credit_amount', 0)
                })
        
        # Create Excel file
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df = pd.DataFrame(excel_data)
            df.to_excel(writer, sheet_name='Opening Balances', index=False)
        
        output.seek(0)
        return output.getvalue()

# Global service instance
opening_balance_service = OpeningBalanceService()