# backend/app/services/double_entry_accounting_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid

from ..models.accounting import (
    JournalEntry, JournalEntryItem, AccountBalance, TrialBalance, TrialBalanceItem,
    BalanceSheet, BalanceSheetItem, ProfitLossStatement, ProfitLossItem,
    CashFlowStatement, CashFlowItem, AccountReconciliation, ReconciliationItem,
    AccountingPeriod, JournalEntryTemplate, AccountGroup
)
from ..models.core import ChartOfAccount
from ..models.financial_year import FinancialYear

logger = logging.getLogger(__name__)

class DoubleEntryAccountingService:
    """Service class for double entry accounting"""
    
    def __init__(self):
        pass
    
    # Journal Entry Management
    def create_journal_entry(
        self, 
        db: Session, 
        company_id: int,
        entry_date: date,
        narration: str = None,
        reference_number: str = None,
        reference_type: str = None,
        reference_id: int = None,
        notes: str = None,
        user_id: int = None
    ) -> JournalEntry:
        """Create journal entry"""
        
        # Generate entry number
        entry_number = f"JE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Create journal entry
        entry = JournalEntry(
            company_id=company_id,
            entry_number=entry_number,
            entry_date=entry_date,
            reference_number=reference_number,
            reference_type=reference_type,
            reference_id=reference_id,
            narration=narration,
            notes=notes,
            created_by=user_id
        )
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        logger.info(f"Journal entry created: {entry_number}")
        
        return entry
    
    def add_items_to_journal_entry(
        self, 
        db: Session, 
        company_id: int,
        entry_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[JournalEntryItem]:
        """Add items to journal entry"""
        
        entry_items = []
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for item_data in items:
            # Create entry item
            entry_item = JournalEntryItem(
                company_id=company_id,
                entry_id=entry_id,
                account_id=item_data['account_id'],
                debit_amount=item_data.get('debit_amount', 0),
                credit_amount=item_data.get('credit_amount', 0),
                description=item_data.get('description'),
                reference=item_data.get('reference'),
                created_by=user_id
            )
            
            db.add(entry_item)
            entry_items.append(entry_item)
            
            total_debit += entry_item.debit_amount
            total_credit += entry_item.credit_amount
        
        # Validate double entry principle
        if total_debit != total_credit:
            raise ValueError(f"Debit total ({total_debit}) must equal credit total ({total_credit})")
        
        # Update journal entry
        entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id
        ).first()
        
        if entry:
            entry.total_debit = total_debit
            entry.total_credit = total_credit
            entry.status = 'draft'
            db.commit()
        
        logger.info(f"Added {len(entry_items)} items to journal entry")
        
        return entry_items
    
    def post_journal_entry(
        self, 
        db: Session, 
        company_id: int,
        entry_id: int,
        user_id: int = None
    ) -> bool:
        """Post journal entry"""
        
        entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.company_id == company_id
        ).first()
        
        if not entry:
            return False
        
        if entry.status != 'draft':
            raise ValueError("Only draft entries can be posted")
        
        # Update account balances
        entry_items = db.query(JournalEntryItem).filter(
            JournalEntryItem.entry_id == entry_id
        ).all()
        
        for item in entry_items:
            # Get or create account balance
            account_balance = db.query(AccountBalance).filter(
                AccountBalance.account_id == item.account_id,
                AccountBalance.company_id == company_id
            ).first()
            
            if not account_balance:
                # Get current financial year
                current_fy = db.query(FinancialYear).filter(
                    FinancialYear.company_id == company_id,
                    FinancialYear.is_active == True
                ).first()
                
                if not current_fy:
                    raise ValueError("No active financial year found")
                
                account_balance = AccountBalance(
                    company_id=company_id,
                    account_id=item.account_id,
                    financial_year_id=current_fy.id,
                    created_by=user_id
                )
                db.add(account_balance)
            
            # Update balances
            account_balance.debit_total += item.debit_amount
            account_balance.credit_total += item.credit_amount
            account_balance.current_balance = account_balance.debit_total - account_balance.credit_total
            account_balance.last_updated = datetime.utcnow()
            account_balance.updated_by = user_id
        
        # Update entry status
        entry.status = 'posted'
        entry.updated_by = user_id
        entry.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Journal entry posted: {entry.entry_number}")
        
        return True
    
    def reverse_journal_entry(
        self, 
        db: Session, 
        company_id: int,
        entry_id: int,
        reversal_date: date,
        reversal_narration: str = None,
        user_id: int = None
    ) -> JournalEntry:
        """Reverse journal entry"""
        
        original_entry = db.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.company_id == company_id
        ).first()
        
        if not original_entry:
            raise ValueError("Journal entry not found")
        
        if original_entry.status != 'posted':
            raise ValueError("Only posted entries can be reversed")
        
        if original_entry.is_reversed:
            raise ValueError("Entry is already reversed")
        
        # Create reversal entry
        reversal_entry = JournalEntry(
            company_id=company_id,
            entry_number=f"REV-{original_entry.entry_number}",
            entry_date=reversal_date,
            reference_number=original_entry.reference_number,
            reference_type=original_entry.reference_type,
            reference_id=original_entry.reference_id,
            narration=reversal_narration or f"Reversal of {original_entry.entry_number}",
            status='draft',
            is_reversed=True,
            reversed_entry_id=entry_id,
            created_by=user_id
        )
        
        db.add(reversal_entry)
        db.commit()
        db.refresh(reversal_entry)
        
        # Create reversal items (opposite of original)
        original_items = db.query(JournalEntryItem).filter(
            JournalEntryItem.entry_id == entry_id
        ).all()
        
        for item in original_items:
            reversal_item = JournalEntryItem(
                company_id=company_id,
                entry_id=reversal_entry.id,
                account_id=item.account_id,
                debit_amount=item.credit_amount,  # Swap debit and credit
                credit_amount=item.debit_amount,
                description=f"Reversal of {item.description or ''}",
                reference=item.reference,
                created_by=user_id
            )
            
            db.add(reversal_item)
        
        # Update reversal entry totals
        reversal_entry.total_debit = original_entry.total_credit
        reversal_entry.total_credit = original_entry.total_debit
        reversal_entry.status = 'posted'
        
        # Mark original as reversed
        original_entry.is_reversed = True
        original_entry.updated_by = user_id
        original_entry.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Journal entry reversed: {original_entry.entry_number}")
        
        return reversal_entry
    
    # Trial Balance Management
    def generate_trial_balance(
        self, 
        db: Session, 
        company_id: int,
        balance_date: date,
        financial_year_id: int = None,
        user_id: int = None
    ) -> TrialBalance:
        """Generate trial balance"""
        
        # Get financial year
        if not financial_year_id:
            fy = db.query(FinancialYear).filter(
                FinancialYear.company_id == company_id,
                FinancialYear.is_active == True
            ).first()
            if not fy:
                raise ValueError("No active financial year found")
            financial_year_id = fy.id
        
        # Create trial balance
        trial_balance = TrialBalance(
            company_id=company_id,
            balance_date=balance_date,
            financial_year_id=financial_year_id,
            created_by=user_id
        )
        
        db.add(trial_balance)
        db.commit()
        db.refresh(trial_balance)
        
        # Get all accounts with balances
        accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.is_active == True
        ).all()
        
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for account in accounts:
            # Get account balance
            balance = db.query(AccountBalance).filter(
                AccountBalance.account_id == account.id,
                AccountBalance.financial_year_id == financial_year_id
            ).first()
            
            if balance and (balance.debit_total > 0 or balance.credit_total > 0):
                debit_balance = max(0, balance.current_balance) if balance.current_balance > 0 else 0
                credit_balance = max(0, -balance.current_balance) if balance.current_balance < 0 else 0
                
                # Create trial balance item
                balance_item = TrialBalanceItem(
                    company_id=company_id,
                    trial_balance_id=trial_balance.id,
                    account_id=account.id,
                    debit_balance=debit_balance,
                    credit_balance=credit_balance,
                    created_by=user_id
                )
                
                db.add(balance_item)
                
                total_debit += debit_balance
                total_credit += credit_balance
        
        # Update trial balance totals
        trial_balance.total_debit = total_debit
        trial_balance.total_credit = total_credit
        trial_balance.is_balanced = (total_debit == total_credit)
        
        db.commit()
        
        logger.info(f"Trial balance generated: {balance_date}")
        
        return trial_balance
    
    # Balance Sheet Management
    def generate_balance_sheet(
        self, 
        db: Session, 
        company_id: int,
        sheet_date: date,
        financial_year_id: int = None,
        user_id: int = None
    ) -> BalanceSheet:
        """Generate balance sheet"""
        
        # Get financial year
        if not financial_year_id:
            fy = db.query(FinancialYear).filter(
                FinancialYear.company_id == company_id,
                FinancialYear.is_active == True
            ).first()
            if not fy:
                raise ValueError("No active financial year found")
            financial_year_id = fy.id
        
        # Create balance sheet
        balance_sheet = BalanceSheet(
            company_id=company_id,
            sheet_date=sheet_date,
            financial_year_id=financial_year_id,
            created_by=user_id
        )
        
        db.add(balance_sheet)
        db.commit()
        db.refresh(balance_sheet)
        
        # Get accounts by type
        account_types = ['asset', 'liability', 'equity']
        total_assets = Decimal('0')
        total_liabilities = Decimal('0')
        total_equity = Decimal('0')
        
        for account_type in account_types:
            accounts = db.query(ChartOfAccount).filter(
                ChartOfAccount.company_id == company_id,
                ChartOfAccount.account_type == account_type,
                ChartOfAccount.is_active == True
            ).all()
            
            for account in accounts:
                # Get account balance
                balance = db.query(AccountBalance).filter(
                    AccountBalance.account_id == account.id,
                    AccountBalance.financial_year_id == financial_year_id
                ).first()
                
                if balance and balance.current_balance != 0:
                    amount = abs(balance.current_balance)
                    
                    # Create balance sheet item
                    sheet_item = BalanceSheetItem(
                        company_id=company_id,
                        balance_sheet_id=balance_sheet.id,
                        account_id=account.id,
                        account_type=account_type,
                        amount=amount,
                        created_by=user_id
                    )
                    
                    db.add(sheet_item)
                    
                    if account_type == 'asset':
                        total_assets += amount
                    elif account_type == 'liability':
                        total_liabilities += amount
                    elif account_type == 'equity':
                        total_equity += amount
        
        # Update balance sheet totals
        balance_sheet.total_assets = total_assets
        balance_sheet.total_liabilities = total_liabilities
        balance_sheet.total_equity = total_equity
        balance_sheet.is_balanced = (total_assets == total_liabilities + total_equity)
        
        db.commit()
        
        logger.info(f"Balance sheet generated: {sheet_date}")
        
        return balance_sheet
    
    # Profit & Loss Statement Management
    def generate_profit_loss_statement(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date,
        financial_year_id: int = None,
        user_id: int = None
    ) -> ProfitLossStatement:
        """Generate profit & loss statement"""
        
        # Get financial year
        if not financial_year_id:
            fy = db.query(FinancialYear).filter(
                FinancialYear.company_id == company_id,
                FinancialYear.is_active == True
            ).first()
            if not fy:
                raise ValueError("No active financial year found")
            financial_year_id = fy.id
        
        # Create profit & loss statement
        statement = ProfitLossStatement(
            company_id=company_id,
            statement_date=to_date,
            financial_year_id=financial_year_id,
            from_date=from_date,
            to_date=to_date,
            created_by=user_id
        )
        
        db.add(statement)
        db.commit()
        db.refresh(statement)
        
        # Get income and expense accounts
        account_types = ['income', 'expense']
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        
        for account_type in account_types:
            accounts = db.query(ChartOfAccount).filter(
                ChartOfAccount.company_id == company_id,
                ChartOfAccount.account_type == account_type,
                ChartOfAccount.is_active == True
            ).all()
            
            for account in accounts:
                # Get account balance for the period
                balance = db.query(AccountBalance).filter(
                    AccountBalance.account_id == account.id,
                    AccountBalance.financial_year_id == financial_year_id
                ).first()
                
                if balance and balance.current_balance != 0:
                    amount = abs(balance.current_balance)
                    
                    # Create statement item
                    statement_item = ProfitLossItem(
                        company_id=company_id,
                        statement_id=statement.id,
                        account_id=account.id,
                        account_type=account_type,
                        amount=amount,
                        created_by=user_id
                    )
                    
                    db.add(statement_item)
                    
                    if account_type == 'income':
                        total_income += amount
                    elif account_type == 'expense':
                        total_expenses += amount
        
        # Update statement totals
        statement.total_income = total_income
        statement.total_expenses = total_expenses
        statement.net_profit = total_income - total_expenses
        
        db.commit()
        
        logger.info(f"Profit & Loss statement generated: {from_date} to {to_date}")
        
        return statement
    
    # Cash Flow Statement Management
    def generate_cash_flow_statement(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date,
        financial_year_id: int = None,
        user_id: int = None
    ) -> CashFlowStatement:
        """Generate cash flow statement"""
        
        # Get financial year
        if not financial_year_id:
            fy = db.query(FinancialYear).filter(
                FinancialYear.company_id == company_id,
                FinancialYear.is_active == True
            ).first()
            if not fy:
                raise ValueError("No active financial year found")
            financial_year_id = fy.id
        
        # Create cash flow statement
        statement = CashFlowStatement(
            company_id=company_id,
            statement_date=to_date,
            financial_year_id=financial_year_id,
            from_date=from_date,
            to_date=to_date,
            created_by=user_id
        )
        
        db.add(statement)
        db.commit()
        db.refresh(statement)
        
        # Get cash accounts
        cash_accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'asset',
            ChartOfAccount.account_name.ilike('%cash%'),
            ChartOfAccount.is_active == True
        ).all()
        
        operating_cash_flow = Decimal('0')
        investing_cash_flow = Decimal('0')
        financing_cash_flow = Decimal('0')
        
        for account in cash_accounts:
            # Get account balance for the period
            balance = db.query(AccountBalance).filter(
                AccountBalance.account_id == account.id,
                AccountBalance.financial_year_id == financial_year_id
            ).first()
            
            if balance and balance.current_balance != 0:
                amount = balance.current_balance
                
                # Determine flow type based on account name
                flow_type = 'operating'
                if 'investment' in account.account_name.lower():
                    flow_type = 'investing'
                elif 'loan' in account.account_name.lower() or 'equity' in account.account_name.lower():
                    flow_type = 'financing'
                
                # Create cash flow item
                flow_item = CashFlowItem(
                    company_id=company_id,
                    statement_id=statement.id,
                    account_id=account.id,
                    flow_type=flow_type,
                    amount=amount,
                    created_by=user_id
                )
                
                db.add(flow_item)
                
                if flow_type == 'operating':
                    operating_cash_flow += amount
                elif flow_type == 'investing':
                    investing_cash_flow += amount
                elif flow_type == 'financing':
                    financing_cash_flow += amount
        
        # Update statement totals
        statement.operating_cash_flow = operating_cash_flow
        statement.investing_cash_flow = investing_cash_flow
        statement.financing_cash_flow = financing_cash_flow
        statement.net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
        
        db.commit()
        
        logger.info(f"Cash flow statement generated: {from_date} to {to_date}")
        
        return statement
    
    # Account Reconciliation Management
    def create_account_reconciliation(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        reconciliation_date: date,
        opening_balance: Decimal = 0,
        closing_balance: Decimal = 0,
        book_balance: Decimal = 0,
        bank_balance: Decimal = 0,
        notes: str = None,
        user_id: int = None
    ) -> AccountReconciliation:
        """Create account reconciliation"""
        
        # Calculate difference
        difference = book_balance - bank_balance
        
        # Create reconciliation
        reconciliation = AccountReconciliation(
            company_id=company_id,
            account_id=account_id,
            reconciliation_date=reconciliation_date,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            book_balance=book_balance,
            bank_balance=bank_balance,
            difference=difference,
            notes=notes,
            created_by=user_id
        )
        
        db.add(reconciliation)
        db.commit()
        db.refresh(reconciliation)
        
        logger.info(f"Account reconciliation created: {account_id}")
        
        return reconciliation
    
    def add_reconciliation_items(
        self, 
        db: Session, 
        company_id: int,
        reconciliation_id: int,
        items: List[Dict],
        user_id: int = None
    ) -> List[ReconciliationItem]:
        """Add items to account reconciliation"""
        
        reconciliation_items = []
        
        for item_data in items:
            # Create reconciliation item
            reconciliation_item = ReconciliationItem(
                company_id=company_id,
                reconciliation_id=reconciliation_id,
                transaction_id=item_data.get('transaction_id'),
                transaction_type=item_data.get('transaction_type'),
                transaction_date=item_data.get('transaction_date'),
                description=item_data.get('description'),
                book_amount=item_data.get('book_amount', 0),
                bank_amount=item_data.get('bank_amount', 0),
                difference=item_data.get('book_amount', 0) - item_data.get('bank_amount', 0),
                is_reconciled=item_data.get('is_reconciled', False),
                created_by=user_id
            )
            
            db.add(reconciliation_item)
            reconciliation_items.append(reconciliation_item)
        
        db.commit()
        
        logger.info(f"Added {len(reconciliation_items)} items to reconciliation")
        
        return reconciliation_items
    
    # Accounting Period Management
    def create_accounting_period(
        self, 
        db: Session, 
        company_id: int,
        period_name: str,
        period_type: str,
        start_date: date,
        end_date: date,
        financial_year_id: int,
        notes: str = None,
        user_id: int = None
    ) -> AccountingPeriod:
        """Create accounting period"""
        
        # Create period
        period = AccountingPeriod(
            company_id=company_id,
            period_name=period_name,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            financial_year_id=financial_year_id,
            notes=notes,
            created_by=user_id
        )
        
        db.add(period)
        db.commit()
        db.refresh(period)
        
        logger.info(f"Accounting period created: {period_name}")
        
        return period
    
    def close_accounting_period(
        self, 
        db: Session, 
        company_id: int,
        period_id: int,
        closing_date: date,
        user_id: int = None
    ) -> bool:
        """Close accounting period"""
        
        period = db.query(AccountingPeriod).filter(
            AccountingPeriod.id == period_id,
            AccountingPeriod.company_id == company_id
        ).first()
        
        if not period:
            return False
        
        if period.is_closed:
            raise ValueError("Period is already closed")
        
        # Close period
        period.is_closed = True
        period.closing_date = closing_date
        period.updated_by = user_id
        period.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Accounting period closed: {period.period_name}")
        
        return True
    
    # Financial Reports
    def get_financial_summary(
        self, 
        db: Session, 
        company_id: int,
        financial_year_id: int = None
    ) -> Dict:
        """Get financial summary"""
        
        # Get financial year
        if not financial_year_id:
            fy = db.query(FinancialYear).filter(
                FinancialYear.company_id == company_id,
                FinancialYear.is_active == True
            ).first()
            if not fy:
                raise ValueError("No active financial year found")
            financial_year_id = fy.id
        
        # Get account balances
        balances = db.query(AccountBalance).filter(
            AccountBalance.company_id == company_id,
            AccountBalance.financial_year_id == financial_year_id
        ).all()
        
        # Calculate totals by account type
        totals = {}
        for balance in balances:
            account = db.query(ChartOfAccount).filter(
                ChartOfAccount.id == balance.account_id
            ).first()
            
            if account:
                account_type = account.account_type
                if account_type not in totals:
                    totals[account_type] = Decimal('0')
                totals[account_type] += balance.current_balance
        
        return {
            "financial_year_id": financial_year_id,
            "account_totals": totals,
            "total_assets": totals.get('asset', 0),
            "total_liabilities": totals.get('liability', 0),
            "total_equity": totals.get('equity', 0),
            "total_income": totals.get('income', 0),
            "total_expenses": totals.get('expense', 0),
            "net_profit": totals.get('income', 0) - totals.get('expense', 0)
        }

# Global service instance
double_entry_accounting_service = DoubleEntryAccountingService()