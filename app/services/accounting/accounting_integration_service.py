# backend/app/services/accounting/accounting_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount, AccountBalance
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.purchase import PurchaseOrder, PurchaseBill, PurchasePayment
from ...models.pos.pos_models import POSTransaction, POSPayment
from ...models.inventory import Item, StockItem
from ...models.banking import BankAccount, BankTransaction
from ...models.core.payment import Payment

logger = logging.getLogger(__name__)

class AccountingIntegrationService:
    """Service for accounting integration with all modules"""
    
    def __init__(self):
        self.journal_cache = {}
        self.account_cache = {}
    
    def create_sales_journal_entry(self, db: Session, sale_invoice_id: int) -> Dict:
        """Create journal entry for sales invoice"""
        
        try:
            # Get sale invoice
            sale_invoice = db.query(SaleInvoice).filter(SaleInvoice.id == sale_invoice_id).first()
            if not sale_invoice:
                raise ValueError("Sale invoice not found")
            
            # Get sale invoice items
            invoice_items = db.query(SaleInvoiceItem).filter(SaleInvoiceItem.sale_invoice_id == sale_invoice_id).all()
            
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=sale_invoice.company_id,
                entry_number=f"SALE-{sale_invoice.invoice_number}",
                entry_date=sale_invoice.invoice_date,
                reference_type='sale_invoice',
                reference_id=sale_invoice_id,
                narration=f"Sales invoice {sale_invoice.invoice_number}",
                total_debit=sale_invoice.total_amount,
                total_credit=sale_invoice.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            journal_items = []
            
            # Debit: Accounts Receivable or Cash/Bank
            if sale_invoice.payment_status == 'paid':
                # If paid, debit cash/bank account
                cash_account = self.get_cash_account(db, sale_invoice.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=sale_invoice.total_amount,
                    credit_amount=0,
                    description=f"Cash received for invoice {sale_invoice.invoice_number}"
                ))
            else:
                # If not paid, debit accounts receivable
                ar_account = self.get_accounts_receivable_account(db, sale_invoice.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=ar_account.id,
                    debit_amount=sale_invoice.total_amount,
                    credit_amount=0,
                    description=f"Accounts receivable for invoice {sale_invoice.invoice_number}"
                ))
            
            # Credit: Sales Revenue
            sales_account = self.get_sales_account(db, sale_invoice.company_id)
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=sale_invoice.total_amount,
                description=f"Sales revenue for invoice {sale_invoice.invoice_number}"
            ))
            
            # Add journal items
            for item in journal_items:
                db.add(item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'sale_invoice_id': sale_invoice_id,
                'message': 'Sales journal entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating sales journal entry: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create sales journal entry: {str(e)}")
    
    def create_purchase_journal_entry(self, db: Session, purchase_bill_id: int) -> Dict:
        """Create journal entry for purchase bill"""
        
        try:
            # Get purchase bill
            purchase_bill = db.query(PurchaseBill).filter(PurchaseBill.id == purchase_bill_id).first()
            if not purchase_bill:
                raise ValueError("Purchase bill not found")
            
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=purchase_bill.company_id,
                entry_number=f"PURCH-{purchase_bill.bill_number}",
                entry_date=purchase_bill.bill_date,
                reference_type='purchase_bill',
                reference_id=purchase_bill_id,
                narration=f"Purchase bill {purchase_bill.bill_number}",
                total_debit=purchase_bill.total_amount,
                total_credit=purchase_bill.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            journal_items = []
            
            # Debit: Inventory or Expense
            if purchase_bill.bill_type == 'goods':
                # If goods, debit inventory
                inventory_account = self.get_inventory_account(db, purchase_bill.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=inventory_account.id,
                    debit_amount=purchase_bill.total_amount,
                    credit_amount=0,
                    description=f"Inventory purchase for bill {purchase_bill.bill_number}"
                ))
            else:
                # If services, debit expense
                expense_account = self.get_expense_account(db, purchase_bill.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=expense_account.id,
                    debit_amount=purchase_bill.total_amount,
                    credit_amount=0,
                    description=f"Expense for bill {purchase_bill.bill_number}"
                ))
            
            # Credit: Accounts Payable or Cash/Bank
            if purchase_bill.payment_status == 'paid':
                # If paid, credit cash/bank account
                cash_account = self.get_cash_account(db, purchase_bill.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=0,
                    credit_amount=purchase_bill.total_amount,
                    description=f"Cash paid for bill {purchase_bill.bill_number}"
                ))
            else:
                # If not paid, credit accounts payable
                ap_account = self.get_accounts_payable_account(db, purchase_bill.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=ap_account.id,
                    debit_amount=0,
                    credit_amount=purchase_bill.total_amount,
                    description=f"Accounts payable for bill {purchase_bill.bill_number}"
                ))
            
            # Add journal items
            for item in journal_items:
                db.add(item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'purchase_bill_id': purchase_bill_id,
                'message': 'Purchase journal entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating purchase journal entry: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create purchase journal entry: {str(e)}")
    
    def create_pos_journal_entry(self, db: Session, pos_transaction_id: int) -> Dict:
        """Create journal entry for POS transaction"""
        
        try:
            # Get POS transaction
            pos_transaction = db.query(POSTransaction).filter(POSTransaction.id == pos_transaction_id).first()
            if not pos_transaction:
                raise ValueError("POS transaction not found")
            
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=pos_transaction.company_id,
                entry_number=f"POS-{pos_transaction.transaction_number}",
                entry_date=pos_transaction.transaction_date,
                reference_type='pos_transaction',
                reference_id=pos_transaction_id,
                narration=f"POS transaction {pos_transaction.transaction_number}",
                total_debit=pos_transaction.total_amount,
                total_credit=pos_transaction.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            journal_items = []
            
            # Debit: Cash/Bank account
            cash_account = self.get_cash_account(db, pos_transaction.company_id)
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=pos_transaction.total_amount,
                credit_amount=0,
                description=f"Cash received for POS transaction {pos_transaction.transaction_number}"
            ))
            
            # Credit: Sales Revenue
            sales_account = self.get_sales_account(db, pos_transaction.company_id)
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=pos_transaction.total_amount,
                description=f"Sales revenue for POS transaction {pos_transaction.transaction_number}"
            ))
            
            # Add journal items
            for item in journal_items:
                db.add(item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'pos_transaction_id': pos_transaction_id,
                'message': 'POS journal entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating POS journal entry: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create POS journal entry: {str(e)}")
    
    def create_inventory_valuation_entry(self, db: Session, valuation_data: Dict) -> Dict:
        """Create journal entry for inventory valuation"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=valuation_data['company_id'],
                entry_number=f"INV-VAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                entry_date=valuation_data['valuation_date'],
                reference_type='inventory_valuation',
                reference_id=valuation_data['valuation_id'],
                narration=f"Inventory valuation as on {valuation_data['valuation_date']}",
                total_debit=valuation_data['total_value'],
                total_credit=valuation_data['total_value'],
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            journal_items = []
            
            # Debit: Inventory Asset
            inventory_account = self.get_inventory_account(db, valuation_data['company_id'])
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=inventory_account.id,
                debit_amount=valuation_data['total_value'],
                credit_amount=0,
                description=f"Inventory valuation as on {valuation_data['valuation_date']}"
            ))
            
            # Credit: Inventory Valuation Reserve
            valuation_reserve_account = self.get_inventory_valuation_reserve_account(db, valuation_data['company_id'])
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=valuation_reserve_account.id,
                debit_amount=0,
                credit_amount=valuation_data['total_value'],
                description=f"Inventory valuation reserve as on {valuation_data['valuation_date']}"
            ))
            
            # Add journal items
            for item in journal_items:
                db.add(item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'message': 'Inventory valuation journal entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating inventory valuation entry: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create inventory valuation entry: {str(e)}")
    
    def create_payment_journal_entry(self, db: Session, payment_id: int, payment_type: str) -> Dict:
        """Create journal entry for payment"""
        
        try:
            if payment_type == 'sale_payment':
                # Get sale payment
                payment = db.query(SalePayment).filter(SalePayment.id == payment_id).first()
                if not payment:
                    raise ValueError("Sale payment not found")
                
                # Create journal entry
                journal_entry = JournalEntry(
                    company_id=payment.company_id,
                    entry_number=f"SALE-PAY-{payment.payment_number}",
                    entry_date=payment.payment_date,
                    reference_type='sale_payment',
                    reference_id=payment_id,
                    narration=f"Payment received for invoice {payment.sale_invoice_id}",
                    total_debit=payment.amount,
                    total_credit=payment.amount,
                    status='posted'
                )
                
            elif payment_type == 'purchase_payment':
                # Get purchase payment
                payment = db.query(PurchasePayment).filter(PurchasePayment.id == payment_id).first()
                if not payment:
                    raise ValueError("Purchase payment not found")
                
                # Create journal entry
                journal_entry = JournalEntry(
                    company_id=payment.company_id,
                    entry_number=f"PURCH-PAY-{payment.payment_number}",
                    entry_date=payment.payment_date,
                    reference_type='purchase_payment',
                    reference_id=payment_id,
                    narration=f"Payment made for bill {payment.purchase_bill_id}",
                    total_debit=payment.amount,
                    total_credit=payment.amount,
                    status='posted'
                )
                
            elif payment_type == 'pos_payment':
                # Get POS payment
                payment = db.query(POSPayment).filter(POSPayment.id == payment_id).first()
                if not payment:
                    raise ValueError("POS payment not found")
                
                # Create journal entry
                journal_entry = JournalEntry(
                    company_id=payment.company_id,
                    entry_number=f"POS-PAY-{payment.payment_number}",
                    entry_date=payment.payment_date,
                    reference_type='pos_payment',
                    reference_id=payment_id,
                    narration=f"POS payment for transaction {payment.transaction_id}",
                    total_debit=payment.amount,
                    total_credit=payment.amount,
                    status='posted'
                )
            
            else:
                raise ValueError("Invalid payment type")
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            journal_items = []
            
            # Debit: Cash/Bank account
            cash_account = self.get_cash_account(db, payment.company_id)
            journal_items.append(JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=payment.amount,
                credit_amount=0,
                description=f"Payment received/made for {payment_type}"
            ))
            
            # Credit: Accounts Receivable/Payable
            if payment_type == 'sale_payment':
                ar_account = self.get_accounts_receivable_account(db, payment.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=ar_account.id,
                    debit_amount=0,
                    credit_amount=payment.amount,
                    description=f"Accounts receivable cleared for {payment_type}"
                ))
            elif payment_type == 'purchase_payment':
                ap_account = self.get_accounts_payable_account(db, payment.company_id)
                journal_items.append(JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=ap_account.id,
                    debit_amount=0,
                    credit_amount=payment.amount,
                    description=f"Accounts payable cleared for {payment_type}"
                ))
            
            # Add journal items
            for item in journal_items:
                db.add(item)
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'payment_id': payment_id,
                'message': f'{payment_type} journal entry created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating payment journal entry: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create payment journal entry: {str(e)}")
    
    def update_account_balances(self, db: Session, company_id: int) -> Dict:
        """Update account balances for all accounts"""
        
        try:
            # Get all accounts for company
            accounts = db.query(ChartOfAccount).filter(ChartOfAccount.company_id == company_id).all()
            
            updated_accounts = []
            
            for account in accounts:
                # Calculate current balance
                debit_total = db.query(func.sum(JournalEntryItem.debit_amount)).join(JournalEntry).filter(
                    JournalEntryItem.account_id == account.id,
                    JournalEntry.company_id == company_id,
                    JournalEntry.status == 'posted'
                ).scalar() or 0
                
                credit_total = db.query(func.sum(JournalEntryItem.credit_amount)).join(JournalEntry).filter(
                    JournalEntryItem.account_id == account.id,
                    JournalEntry.company_id == company_id,
                    JournalEntry.status == 'posted'
                ).scalar() or 0
                
                # Calculate balance
                if account.account_type in ['asset', 'expense']:
                    balance = debit_total - credit_total
                else:
                    balance = credit_total - debit_total
                
                # Update or create account balance
                account_balance = db.query(AccountBalance).filter(
                    AccountBalance.account_id == account.id,
                    AccountBalance.company_id == company_id
                ).first()
                
                if account_balance:
                    account_balance.current_balance = balance
                    account_balance.last_updated = datetime.utcnow()
                else:
                    account_balance = AccountBalance(
                        account_id=account.id,
                        company_id=company_id,
                        current_balance=balance,
                        last_updated=datetime.utcnow()
                    )
                    db.add(account_balance)
                
                updated_accounts.append({
                    'account_id': account.id,
                    'account_name': account.account_name,
                    'account_type': account.account_type,
                    'balance': balance
                })
            
            db.commit()
            
            return {
                'success': True,
                'updated_accounts': len(updated_accounts),
                'accounts': updated_accounts,
                'message': 'Account balances updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating account balances: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update account balances: {str(e)}")
    
    def get_financial_summary(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get financial summary for company"""
        
        try:
            if not from_date:
                from_date = date.today().replace(day=1)  # First day of current month
            if not to_date:
                to_date = date.today()
            
            # Get revenue
            revenue = db.query(func.sum(JournalEntryItem.credit_amount)).join(JournalEntry).join(ChartOfAccount).filter(
                ChartOfAccount.account_type == 'revenue',
                ChartOfAccount.company_id == company_id,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                JournalEntry.status == 'posted'
            ).scalar() or 0
            
            # Get expenses
            expenses = db.query(func.sum(JournalEntryItem.debit_amount)).join(JournalEntry).join(ChartOfAccount).filter(
                ChartOfAccount.account_type == 'expense',
                ChartOfAccount.company_id == company_id,
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date,
                JournalEntry.status == 'posted'
            ).scalar() or 0
            
            # Get assets
            assets = db.query(func.sum(AccountBalance.current_balance)).join(ChartOfAccount).filter(
                ChartOfAccount.account_type == 'asset',
                ChartOfAccount.company_id == company_id
            ).scalar() or 0
            
            # Get liabilities
            liabilities = db.query(func.sum(AccountBalance.current_balance)).join(ChartOfAccount).filter(
                ChartOfAccount.account_type == 'liability',
                ChartOfAccount.company_id == company_id
            ).scalar() or 0
            
            # Get equity
            equity = db.query(func.sum(AccountBalance.current_balance)).join(ChartOfAccount).filter(
                ChartOfAccount.account_type == 'equity',
                ChartOfAccount.company_id == company_id
            ).scalar() or 0
            
            # Calculate profit/loss
            profit_loss = revenue - expenses
            
            return {
                'revenue': revenue,
                'expenses': expenses,
                'profit_loss': profit_loss,
                'assets': assets,
                'liabilities': liabilities,
                'equity': equity,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                },
                'summary_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting financial summary: {str(e)}")
            return {
                'revenue': 0,
                'expenses': 0,
                'profit_loss': 0,
                'assets': 0,
                'liabilities': 0,
                'equity': 0,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                },
                'summary_date': datetime.utcnow()
            }
    
    # Helper methods for getting accounts
    def get_cash_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get cash account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%cash%')
        ).first()
    
    def get_sales_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get sales revenue account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'revenue'
        ).first()
    
    def get_inventory_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get inventory account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%inventory%')
        ).first()
    
    def get_expense_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get expense account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'expense'
        ).first()
    
    def get_accounts_receivable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get accounts receivable account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%accounts receivable%')
        ).first()
    
    def get_accounts_payable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get accounts payable account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%accounts payable%')
        ).first()
    
    def get_inventory_valuation_reserve_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get inventory valuation reserve account for company"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%inventory valuation%')
        ).first()