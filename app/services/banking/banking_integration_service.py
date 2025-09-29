# backend/app/services/banking/banking_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.banking import (
    BankAccount, BankTransaction, BankReconciliation, BankStatement,
    BankTransfer, BankPayment, BankReceipt, BankLoan, BankLoanEMI
)
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.purchase import PurchaseOrder, PurchaseBill, PurchasePayment
from ...models.pos.pos_models import POSTransaction, POSPayment
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.company import Company
from ...models.customers import Customer
from ...models.suppliers import Supplier

logger = logging.getLogger(__name__)

class BankingIntegrationService:
    """Service for banking integration with all modules"""
    
    def __init__(self):
        self.banking_cache = {}
        self.account_cache = {}
        self.transaction_cache = {}
    
    def create_bank_account_with_integrations(self, db: Session, account_data: Dict) -> Dict:
        """Create bank account with full module integrations"""
        
        try:
            # Create bank account
            bank_account = BankAccount(
                company_id=account_data['company_id'],
                account_name=account_data['account_name'],
                account_number=account_data['account_number'],
                bank_name=account_data['bank_name'],
                bank_code=account_data.get('bank_code'),
                branch_name=account_data.get('branch_name'),
                branch_code=account_data.get('branch_code'),
                ifsc_code=account_data.get('ifsc_code'),
                account_type=account_data['account_type'],
                currency=account_data.get('currency', 'INR'),
                opening_balance=account_data.get('opening_balance', 0),
                current_balance=account_data.get('opening_balance', 0),
                is_active=account_data.get('is_active', True)
            )
            
            db.add(bank_account)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_bank_account_with_accounting(db, bank_account)
            integration_results['accounting'] = accounting_result
            
            # 2. Company Integration
            company_result = self.integrate_bank_account_with_company(db, bank_account)
            integration_results['company'] = company_result
            
            db.commit()
            
            return {
                'success': True,
                'bank_account_id': bank_account.id,
                'account_name': bank_account.account_name,
                'account_number': bank_account.account_number,
                'integration_results': integration_results,
                'message': 'Bank account created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating bank account with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create bank account: {str(e)}")
    
    def integrate_bank_account_with_accounting(self, db: Session, bank_account: BankAccount) -> Dict:
        """Integrate bank account with accounting module"""
        
        try:
            # Create bank account in chart of accounts
            chart_account = ChartOfAccount(
                company_id=bank_account.company_id,
                account_name=f"Bank - {bank_account.account_name}",
                account_code=f"BANK-{bank_account.id:06d}",
                account_type='asset',
                parent_account_id=None,
                is_active=True,
                description=f"Bank account {bank_account.account_name} - {bank_account.account_number}"
            )
            
            db.add(chart_account)
            
            # Create opening balance journal entry if applicable
            if bank_account.opening_balance != 0:
                opening_entry = JournalEntry(
                    company_id=bank_account.company_id,
                    entry_number=f"BANK-OPEN-{bank_account.id}",
                    entry_date=date.today(),
                    reference_type='bank_account',
                    reference_id=bank_account.id,
                    narration=f"Opening balance for bank account {bank_account.account_name}",
                    total_debit=abs(bank_account.opening_balance),
                    total_credit=abs(bank_account.opening_balance),
                    status='posted'
                )
                
                db.add(opening_entry)
                db.flush()
                
                # Create journal entry items
                if bank_account.opening_balance > 0:
                    # Debit: Bank Account
                    journal_item_bank = JournalEntryItem(
                        entry_id=opening_entry.id,
                        account_id=chart_account.id,
                        debit_amount=bank_account.opening_balance,
                        credit_amount=0,
                        description=f"Opening balance for {bank_account.account_name}"
                    )
                    db.add(journal_item_bank)
                    
                    # Credit: Capital Account
                    capital_account = self.get_capital_account(db, bank_account.company_id)
                    journal_item_capital = JournalEntryItem(
                        entry_id=opening_entry.id,
                        account_id=capital_account.id,
                        debit_amount=0,
                        credit_amount=bank_account.opening_balance,
                        description=f"Opening balance for {bank_account.account_name}"
                    )
                    db.add(journal_item_capital)
                else:
                    # Credit: Bank Account
                    journal_item_bank = JournalEntryItem(
                        entry_id=opening_entry.id,
                        account_id=chart_account.id,
                        debit_amount=0,
                        credit_amount=abs(bank_account.opening_balance),
                        description=f"Opening balance for {bank_account.account_name}"
                    )
                    db.add(journal_item_bank)
                    
                    # Debit: Capital Account
                    capital_account = self.get_capital_account(db, bank_account.company_id)
                    journal_item_capital = JournalEntryItem(
                        entry_id=opening_entry.id,
                        account_id=capital_account.id,
                        debit_amount=abs(bank_account.opening_balance),
                        credit_amount=0,
                        description=f"Opening balance for {bank_account.account_name}"
                    )
                    db.add(journal_item_capital)
            
            return {
                'status': 'success',
                'chart_account_id': chart_account.id,
                'account_name': chart_account.account_name,
                'opening_balance_entry': opening_entry.id if bank_account.opening_balance != 0 else None,
                'message': 'Bank account integrated with accounting'
            }
            
        except Exception as e:
            logger.error(f"Error integrating bank account with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_bank_account_with_company(self, db: Session, bank_account: BankAccount) -> Dict:
        """Integrate bank account with company module"""
        
        try:
            # Get company
            company = db.query(Company).filter(Company.id == bank_account.company_id).first()
            if not company:
                return {'status': 'error', 'message': 'Company not found'}
            
            # Update company with bank details
            company.bank_accounts = (company.bank_accounts or []) + [bank_account.id]
            
            return {
                'status': 'success',
                'company_id': company.id,
                'bank_account_id': bank_account.id,
                'message': 'Bank account integrated with company'
            }
            
        except Exception as e:
            logger.error(f"Error integrating bank account with company: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_bank_transaction_with_integrations(self, db: Session, transaction_data: Dict) -> Dict:
        """Process bank transaction with full module integrations"""
        
        try:
            # Create bank transaction
            bank_transaction = BankTransaction(
                company_id=transaction_data['company_id'],
                bank_account_id=transaction_data['bank_account_id'],
                transaction_date=transaction_data['transaction_date'],
                transaction_type=transaction_data['transaction_type'],
                amount=transaction_data['amount'],
                balance_after=transaction_data['balance_after'],
                reference_number=transaction_data.get('reference_number'),
                description=transaction_data.get('description'),
                category=transaction_data.get('category'),
                subcategory=transaction_data.get('subcategory'),
                is_reconciled=transaction_data.get('is_reconciled', False)
            )
            
            db.add(bank_transaction)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_bank_transaction_with_accounting(db, bank_transaction)
            integration_results['accounting'] = accounting_result
            
            # 2. Sales Integration
            sales_result = self.integrate_bank_transaction_with_sales(db, bank_transaction)
            integration_results['sales'] = sales_result
            
            # 3. Purchase Integration
            purchase_result = self.integrate_bank_transaction_with_purchase(db, bank_transaction)
            integration_results['purchase'] = purchase_result
            
            # 4. POS Integration
            pos_result = self.integrate_bank_transaction_with_pos(db, bank_transaction)
            integration_results['pos'] = pos_result
            
            db.commit()
            
            return {
                'success': True,
                'transaction_id': bank_transaction.id,
                'transaction_type': bank_transaction.transaction_type,
                'amount': bank_transaction.amount,
                'integration_results': integration_results,
                'message': 'Bank transaction processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing bank transaction with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process bank transaction: {str(e)}")
    
    def integrate_bank_transaction_with_accounting(self, db: Session, bank_transaction: BankTransaction) -> Dict:
        """Integrate bank transaction with accounting module"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=bank_transaction.company_id,
                entry_number=f"BANK-TXN-{bank_transaction.id}",
                entry_date=bank_transaction.transaction_date,
                reference_type='bank_transaction',
                reference_id=bank_transaction.id,
                narration=f"Bank transaction {bank_transaction.transaction_type} - {bank_transaction.description}",
                total_debit=bank_transaction.amount,
                total_credit=bank_transaction.amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            if bank_transaction.transaction_type == 'credit':
                # Debit: Bank Account
                bank_account = self.get_bank_chart_account(db, bank_transaction.bank_account_id)
                journal_item_bank = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=bank_account.id,
                    debit_amount=bank_transaction.amount,
                    credit_amount=0,
                    description=f"Bank credit - {bank_transaction.description}"
                )
                db.add(journal_item_bank)
                
                # Credit: Income Account
                income_account = self.get_income_account(db, bank_transaction.company_id)
                journal_item_income = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=income_account.id,
                    debit_amount=0,
                    credit_amount=bank_transaction.amount,
                    description=f"Bank credit - {bank_transaction.description}"
                )
                db.add(journal_item_income)
            
            elif bank_transaction.transaction_type == 'debit':
                # Debit: Expense Account
                expense_account = self.get_expense_account(db, bank_transaction.company_id)
                journal_item_expense = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=expense_account.id,
                    debit_amount=bank_transaction.amount,
                    credit_amount=0,
                    description=f"Bank debit - {bank_transaction.description}"
                )
                db.add(journal_item_expense)
                
                # Credit: Bank Account
                bank_account = self.get_bank_chart_account(db, bank_transaction.bank_account_id)
                journal_item_bank = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=bank_account.id,
                    debit_amount=0,
                    credit_amount=bank_transaction.amount,
                    description=f"Bank debit - {bank_transaction.description}"
                )
                db.add(journal_item_bank)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for bank transaction'
            }
            
        except Exception as e:
            logger.error(f"Error integrating bank transaction with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_bank_transaction_with_sales(self, db: Session, bank_transaction: BankTransaction) -> Dict:
        """Integrate bank transaction with sales module"""
        
        try:
            # Check if transaction is related to sales
            if bank_transaction.transaction_type == 'credit' and bank_transaction.category == 'sales':
                # Find matching sale payment
                sale_payment = db.query(SalePayment).filter(
                    SalePayment.payment_reference == bank_transaction.reference_number
                ).first()
                
                if sale_payment:
                    # Update sale payment with bank transaction
                    sale_payment.bank_transaction_id = bank_transaction.id
                    sale_payment.payment_status = 'confirmed'
                    
                    return {
                        'status': 'success',
                        'sale_payment_id': sale_payment.id,
                        'message': 'Sale payment updated with bank transaction'
                    }
            
            return {'status': 'skipped', 'message': 'No sales integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating bank transaction with sales: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_bank_transaction_with_purchase(self, db: Session, bank_transaction: BankTransaction) -> Dict:
        """Integrate bank transaction with purchase module"""
        
        try:
            # Check if transaction is related to purchases
            if bank_transaction.transaction_type == 'debit' and bank_transaction.category == 'purchase':
                # Find matching purchase payment
                purchase_payment = db.query(PurchasePayment).filter(
                    PurchasePayment.payment_reference == bank_transaction.reference_number
                ).first()
                
                if purchase_payment:
                    # Update purchase payment with bank transaction
                    purchase_payment.bank_transaction_id = bank_transaction.id
                    purchase_payment.payment_status = 'confirmed'
                    
                    return {
                        'status': 'success',
                        'purchase_payment_id': purchase_payment.id,
                        'message': 'Purchase payment updated with bank transaction'
                    }
            
            return {'status': 'skipped', 'message': 'No purchase integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating bank transaction with purchase: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_bank_transaction_with_pos(self, db: Session, bank_transaction: BankTransaction) -> Dict:
        """Integrate bank transaction with POS module"""
        
        try:
            # Check if transaction is related to POS
            if bank_transaction.transaction_type == 'credit' and bank_transaction.category == 'pos':
                # Find matching POS payment
                pos_payment = db.query(POSPayment).filter(
                    POSPayment.payment_reference == bank_transaction.reference_number
                ).first()
                
                if pos_payment:
                    # Update POS payment with bank transaction
                    pos_payment.bank_transaction_id = bank_transaction.id
                    pos_payment.payment_status = 'confirmed'
                    
                    return {
                        'status': 'success',
                        'pos_payment_id': pos_payment.id,
                        'message': 'POS payment updated with bank transaction'
                    }
            
            return {'status': 'skipped', 'message': 'No POS integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating bank transaction with POS: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_bank_reconciliation_with_integrations(self, db: Session, reconciliation_data: Dict) -> Dict:
        """Process bank reconciliation with full module integrations"""
        
        try:
            # Create bank reconciliation
            bank_reconciliation = BankReconciliation(
                company_id=reconciliation_data['company_id'],
                bank_account_id=reconciliation_data['bank_account_id'],
                reconciliation_date=reconciliation_data['reconciliation_date'],
                opening_balance=reconciliation_data['opening_balance'],
                closing_balance=reconciliation_data['closing_balance'],
                total_debits=reconciliation_data.get('total_debits', 0),
                total_credits=reconciliation_data.get('total_credits', 0),
                difference_amount=reconciliation_data.get('difference_amount', 0),
                status=reconciliation_data.get('status', 'draft')
            )
            
            db.add(bank_reconciliation)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_reconciliation_with_accounting(db, bank_reconciliation)
            integration_results['accounting'] = accounting_result
            
            # 2. Transaction Integration
            transaction_result = self.integrate_reconciliation_with_transactions(db, bank_reconciliation)
            integration_results['transactions'] = transaction_result
            
            db.commit()
            
            return {
                'success': True,
                'reconciliation_id': bank_reconciliation.id,
                'reconciliation_date': bank_reconciliation.reconciliation_date,
                'integration_results': integration_results,
                'message': 'Bank reconciliation processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing bank reconciliation with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process bank reconciliation: {str(e)}")
    
    def integrate_reconciliation_with_accounting(self, db: Session, bank_reconciliation: BankReconciliation) -> Dict:
        """Integrate bank reconciliation with accounting module"""
        
        try:
            # Create journal entry for reconciliation
            journal_entry = JournalEntry(
                company_id=bank_reconciliation.company_id,
                entry_number=f"BANK-REC-{bank_reconciliation.id}",
                entry_date=bank_reconciliation.reconciliation_date,
                reference_type='bank_reconciliation',
                reference_id=bank_reconciliation.id,
                narration=f"Bank reconciliation for {bank_reconciliation.reconciliation_date}",
                total_debit=bank_reconciliation.difference_amount,
                total_credit=bank_reconciliation.difference_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            if bank_reconciliation.difference_amount != 0:
                # Debit: Bank Account
                bank_account = self.get_bank_chart_account(db, bank_reconciliation.bank_account_id)
                journal_item_bank = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=bank_account.id,
                    debit_amount=bank_reconciliation.difference_amount,
                    credit_amount=0,
                    description=f"Bank reconciliation adjustment"
                )
                db.add(journal_item_bank)
                
                # Credit: Bank Reconciliation Account
                reconciliation_account = self.get_reconciliation_account(db, bank_reconciliation.company_id)
                journal_item_reconciliation = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=reconciliation_account.id,
                    debit_amount=0,
                    credit_amount=bank_reconciliation.difference_amount,
                    description=f"Bank reconciliation adjustment"
                )
                db.add(journal_item_reconciliation)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for bank reconciliation'
            }
            
        except Exception as e:
            logger.error(f"Error integrating reconciliation with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_reconciliation_with_transactions(self, db: Session, bank_reconciliation: BankReconciliation) -> Dict:
        """Integrate bank reconciliation with transactions"""
        
        try:
            # Get unreconciled transactions
            unreconciled_transactions = db.query(BankTransaction).filter(
                BankTransaction.bank_account_id == bank_reconciliation.bank_account_id,
                BankTransaction.is_reconciled == False
            ).all()
            
            # Mark transactions as reconciled
            reconciled_count = 0
            for transaction in unreconciled_transactions:
                transaction.is_reconciled = True
                transaction.reconciliation_id = bank_reconciliation.id
                reconciled_count += 1
            
            return {
                'status': 'success',
                'reconciled_transactions': reconciled_count,
                'message': f'{reconciled_count} transactions marked as reconciled'
            }
            
        except Exception as e:
            logger.error(f"Error integrating reconciliation with transactions: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_banking_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive banking analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get bank accounts
            bank_accounts = db.query(BankAccount).filter(
                BankAccount.company_id == company_id,
                BankAccount.is_active == True
            ).all()
            
            # Get bank transactions
            bank_transactions = db.query(BankTransaction).filter(
                BankTransaction.company_id == company_id,
                BankTransaction.transaction_date >= from_date,
                BankTransaction.transaction_date <= to_date
            ).all()
            
            # Calculate metrics
            total_accounts = len(bank_accounts)
            total_transactions = len(bank_transactions)
            total_credits = sum(t.amount for t in bank_transactions if t.transaction_type == 'credit')
            total_debits = sum(t.amount for t in bank_transactions if t.transaction_type == 'debit')
            net_flow = total_credits - total_debits
            
            # Get account-wise analytics
            account_analytics = []
            for account in bank_accounts:
                account_transactions = [t for t in bank_transactions if t.bank_account_id == account.id]
                account_credits = sum(t.amount for t in account_transactions if t.transaction_type == 'credit')
                account_debits = sum(t.amount for t in account_transactions if t.transaction_type == 'debit')
                
                account_analytics.append({
                    'account_id': account.id,
                    'account_name': account.account_name,
                    'account_number': account.account_number,
                    'current_balance': account.current_balance,
                    'total_credits': account_credits,
                    'total_debits': account_debits,
                    'net_flow': account_credits - account_debits,
                    'transaction_count': len(account_transactions)
                })
            
            return {
                'total_accounts': total_accounts,
                'total_transactions': total_transactions,
                'total_credits': total_credits,
                'total_debits': total_debits,
                'net_flow': net_flow,
                'account_analytics': account_analytics,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting banking analytics: {str(e)}")
            return {
                'total_accounts': 0,
                'total_transactions': 0,
                'total_credits': 0,
                'total_debits': 0,
                'net_flow': 0,
                'account_analytics': [],
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    # Helper methods
    def get_capital_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get capital account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'equity'
        ).first()
    
    def get_bank_chart_account(self, db: Session, bank_account_id: int) -> ChartOfAccount:
        """Get bank chart account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.account_name.ilike(f'%bank%{bank_account_id}%')
        ).first()
    
    def get_income_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get income account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'revenue'
        ).first()
    
    def get_expense_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get expense account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'expense'
        ).first()
    
    def get_reconciliation_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get reconciliation account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%reconciliation%')
        ).first()