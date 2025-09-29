# backend/app/services/compliance/indian_compliance_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.compliance.indian_compliance import (
    GSTRegistration, GSTReturn, GSTPayment, TDSReturn, TDSPayment,
    TCSReturn, TCSPayment, EInvoice, EWaybill, EInvoiceItem, EWaybillItem
)
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.purchase import PurchaseOrder, PurchaseBill, PurchasePayment
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.company import Company
from ...models.customers import Customer
from ...models.suppliers import Supplier

logger = logging.getLogger(__name__)

class IndianComplianceIntegrationService:
    """Service for Indian compliance integration with all modules"""
    
    def __init__(self):
        self.compliance_cache = {}
        self.gst_cache = {}
        self.tds_cache = {}
        self.tcs_cache = {}
    
    def create_gst_registration_with_integrations(self, db: Session, registration_data: Dict) -> Dict:
        """Create GST registration with full module integrations"""
        
        try:
            # Create GST registration
            gst_registration = GSTRegistration(
                company_id=registration_data['company_id'],
                gst_number=registration_data['gst_number'],
                registration_type=registration_data['registration_type'],
                registration_date=registration_data['registration_date'],
                business_name=registration_data['business_name'],
                business_address=registration_data['business_address'],
                business_type=registration_data['business_type'],
                pan_number=registration_data['pan_number'],
                aadhar_number=registration_data.get('aadhar_number'),
                mobile_number=registration_data.get('mobile_number'),
                email=registration_data.get('email'),
                state_code=registration_data['state_code'],
                is_active=registration_data.get('is_active', True)
            )
            
            db.add(gst_registration)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Company Integration
            company_result = self.integrate_gst_with_company(db, gst_registration)
            integration_results['company'] = company_result
            
            # 2. Accounting Integration
            accounting_result = self.integrate_gst_with_accounting(db, gst_registration)
            integration_results['accounting'] = accounting_result
            
            # 3. Sales Integration
            sales_result = self.integrate_gst_with_sales(db, gst_registration)
            integration_results['sales'] = sales_result
            
            # 4. Purchase Integration
            purchase_result = self.integrate_gst_with_purchase(db, gst_registration)
            integration_results['purchase'] = purchase_result
            
            db.commit()
            
            return {
                'success': True,
                'gst_registration_id': gst_registration.id,
                'gst_number': gst_registration.gst_number,
                'integration_results': integration_results,
                'message': 'GST registration created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating GST registration with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create GST registration: {str(e)}")
    
    def integrate_gst_with_company(self, db: Session, gst_registration: GSTRegistration) -> Dict:
        """Integrate GST registration with company module"""
        
        try:
            # Get company
            company = db.query(Company).filter(Company.id == gst_registration.company_id).first()
            if not company:
                return {'status': 'error', 'message': 'Company not found'}
            
            # Update company with GST details
            company.gst_number = gst_registration.gst_number
            company.pan_number = gst_registration.pan_number
            company.business_address = gst_registration.business_address
            company.state_code = gst_registration.state_code
            
            return {
                'status': 'success',
                'company_id': company.id,
                'gst_number': company.gst_number,
                'pan_number': company.pan_number
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST with company: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_gst_with_accounting(self, db: Session, gst_registration: GSTRegistration) -> Dict:
        """Integrate GST registration with accounting module"""
        
        try:
            # Create GST-related accounts
            gst_accounts = self.create_gst_accounts(db, gst_registration.company_id)
            
            return {
                'status': 'success',
                'gst_accounts_created': gst_accounts,
                'message': 'GST accounts created in chart of accounts'
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_gst_with_sales(self, db: Session, gst_registration: GSTRegistration) -> Dict:
        """Integrate GST registration with sales module"""
        
        try:
            # Update existing sales invoices with GST
            sales_invoices = db.query(SaleInvoice).filter(
                SaleInvoice.company_id == gst_registration.company_id,
                SaleInvoice.gst_number.is_(None)
            ).all()
            
            updated_count = 0
            for invoice in sales_invoices:
                invoice.gst_number = gst_registration.gst_number
                updated_count += 1
            
            return {
                'status': 'success',
                'invoices_updated': updated_count,
                'message': f'Updated {updated_count} sales invoices with GST number'
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST with sales: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_gst_with_purchase(self, db: Session, gst_registration: GSTRegistration) -> Dict:
        """Integrate GST registration with purchase module"""
        
        try:
            # Update existing purchase bills with GST
            purchase_bills = db.query(PurchaseBill).filter(
                PurchaseBill.company_id == gst_registration.company_id,
                PurchaseBill.gst_number.is_(None)
            ).all()
            
            updated_count = 0
            for bill in purchase_bills:
                bill.gst_number = gst_registration.gst_number
                updated_count += 1
            
            return {
                'status': 'success',
                'bills_updated': updated_count,
                'message': f'Updated {updated_count} purchase bills with GST number'
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST with purchase: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_gst_accounts(self, db: Session, company_id: int) -> List[Dict]:
        """Create GST-related accounts in chart of accounts"""
        
        try:
            gst_accounts = []
            
            # GST Input Tax Account
            gst_input_account = ChartOfAccount(
                company_id=company_id,
                account_name='GST Input Tax',
                account_code='GST-INPUT-001',
                account_type='asset',
                parent_account_id=None,
                is_active=True,
                description='GST input tax credit account'
            )
            db.add(gst_input_account)
            gst_accounts.append({'name': 'GST Input Tax', 'code': 'GST-INPUT-001'})
            
            # GST Output Tax Account
            gst_output_account = ChartOfAccount(
                company_id=company_id,
                account_name='GST Output Tax',
                account_code='GST-OUTPUT-001',
                account_type='liability',
                parent_account_id=None,
                is_active=True,
                description='GST output tax liability account'
            )
            db.add(gst_output_account)
            gst_accounts.append({'name': 'GST Output Tax', 'code': 'GST-OUTPUT-001'})
            
            # GST Payable Account
            gst_payable_account = ChartOfAccount(
                company_id=company_id,
                account_name='GST Payable',
                account_code='GST-PAYABLE-001',
                account_type='liability',
                parent_account_id=None,
                is_active=True,
                description='GST payable to government account'
            )
            db.add(gst_payable_account)
            gst_accounts.append({'name': 'GST Payable', 'code': 'GST-PAYABLE-001'})
            
            return gst_accounts
            
        except Exception as e:
            logger.error(f"Error creating GST accounts: {str(e)}")
            return []
    
    def process_gst_return_with_integrations(self, db: Session, return_data: Dict) -> Dict:
        """Process GST return with full module integrations"""
        
        try:
            # Create GST return
            gst_return = GSTReturn(
                company_id=return_data['company_id'],
                return_period=return_data['return_period'],
                return_type=return_data['return_type'],
                gst_number=return_data['gst_number'],
                filing_date=return_data['filing_date'],
                due_date=return_data['due_date'],
                status=return_data.get('status', 'draft'),
                total_sales=return_data.get('total_sales', 0),
                total_purchases=return_data.get('total_purchases', 0),
                output_tax=return_data.get('output_tax', 0),
                input_tax=return_data.get('input_tax', 0),
                net_tax=return_data.get('net_tax', 0),
                interest_amount=return_data.get('interest_amount', 0),
                penalty_amount=return_data.get('penalty_amount', 0),
                total_payable=return_data.get('total_payable', 0)
            )
            
            db.add(gst_return)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Sales Integration
            sales_result = self.integrate_gst_return_with_sales(db, gst_return)
            integration_results['sales'] = sales_result
            
            # 2. Purchase Integration
            purchase_result = self.integrate_gst_return_with_purchase(db, gst_return)
            integration_results['purchase'] = purchase_result
            
            # 3. Accounting Integration
            accounting_result = self.integrate_gst_return_with_accounting(db, gst_return)
            integration_results['accounting'] = accounting_result
            
            db.commit()
            
            return {
                'success': True,
                'gst_return_id': gst_return.id,
                'return_period': gst_return.return_period,
                'integration_results': integration_results,
                'message': 'GST return processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing GST return with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process GST return: {str(e)}")
    
    def integrate_gst_return_with_sales(self, db: Session, gst_return: GSTReturn) -> Dict:
        """Integrate GST return with sales module"""
        
        try:
            # Get sales data for the return period
            start_date = datetime.strptime(gst_return.return_period, '%Y-%m').date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            
            # Get sales invoices
            sales_invoices = db.query(SaleInvoice).filter(
                SaleInvoice.company_id == gst_return.company_id,
                SaleInvoice.invoice_date >= start_date,
                SaleInvoice.invoice_date <= end_date
            ).all()
            
            total_sales = sum(invoice.total_amount for invoice in sales_invoices)
            output_tax = sum(invoice.tax_amount for invoice in sales_invoices)
            
            return {
                'status': 'success',
                'invoices_count': len(sales_invoices),
                'total_sales': total_sales,
                'output_tax': output_tax
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST return with sales: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_gst_return_with_purchase(self, db: Session, gst_return: GSTReturn) -> Dict:
        """Integrate GST return with purchase module"""
        
        try:
            # Get purchase data for the return period
            start_date = datetime.strptime(gst_return.return_period, '%Y-%m').date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            
            # Get purchase bills
            purchase_bills = db.query(PurchaseBill).filter(
                PurchaseBill.company_id == gst_return.company_id,
                PurchaseBill.bill_date >= start_date,
                PurchaseBill.bill_date <= end_date
            ).all()
            
            total_purchases = sum(bill.total_amount for bill in purchase_bills)
            input_tax = sum(bill.tax_amount for bill in purchase_bills)
            
            return {
                'status': 'success',
                'bills_count': len(purchase_bills),
                'total_purchases': total_purchases,
                'input_tax': input_tax
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST return with purchase: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_gst_return_with_accounting(self, db: Session, gst_return: GSTReturn) -> Dict:
        """Integrate GST return with accounting module"""
        
        try:
            # Create journal entry for GST return
            journal_entry = JournalEntry(
                company_id=gst_return.company_id,
                entry_number=f"GST-RET-{gst_return.return_period}",
                entry_date=gst_return.filing_date,
                reference_type='gst_return',
                reference_id=gst_return.id,
                narration=f"GST return for period {gst_return.return_period}",
                total_debit=gst_return.total_payable,
                total_credit=gst_return.total_payable,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            if gst_return.net_tax > 0:
                # Debit: GST Payable
                gst_payable_account = self.get_gst_payable_account(db, gst_return.company_id)
                journal_item_payable = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=gst_payable_account.id,
                    debit_amount=gst_return.net_tax,
                    credit_amount=0,
                    description=f"GST payable for period {gst_return.return_period}"
                )
                db.add(journal_item_payable)
                
                # Credit: Cash/Bank
                cash_account = self.get_cash_account(db, gst_return.company_id)
                journal_item_cash = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=0,
                    credit_amount=gst_return.net_tax,
                    description=f"GST payment for period {gst_return.return_period}"
                )
                db.add(journal_item_cash)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for GST return'
            }
            
        except Exception as e:
            logger.error(f"Error integrating GST return with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_tds_return_with_integrations(self, db: Session, return_data: Dict) -> Dict:
        """Process TDS return with full module integrations"""
        
        try:
            # Create TDS return
            tds_return = TDSReturn(
                company_id=return_data['company_id'],
                return_period=return_data['return_period'],
                return_type=return_data['return_type'],
                pan_number=return_data['pan_number'],
                filing_date=return_data['filing_date'],
                due_date=return_data['due_date'],
                status=return_data.get('status', 'draft'),
                total_tds_deducted=return_data.get('total_tds_deducted', 0),
                total_tds_deposited=return_data.get('total_tds_deposited', 0),
                interest_amount=return_data.get('interest_amount', 0),
                penalty_amount=return_data.get('penalty_amount', 0),
                total_payable=return_data.get('total_payable', 0)
            )
            
            db.add(tds_return)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Purchase Integration
            purchase_result = self.integrate_tds_return_with_purchase(db, tds_return)
            integration_results['purchase'] = purchase_result
            
            # 2. Accounting Integration
            accounting_result = self.integrate_tds_return_with_accounting(db, tds_return)
            integration_results['accounting'] = accounting_result
            
            db.commit()
            
            return {
                'success': True,
                'tds_return_id': tds_return.id,
                'return_period': tds_return.return_period,
                'integration_results': integration_results,
                'message': 'TDS return processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing TDS return with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process TDS return: {str(e)}")
    
    def integrate_tds_return_with_purchase(self, db: Session, tds_return: TDSReturn) -> Dict:
        """Integrate TDS return with purchase module"""
        
        try:
            # Get purchase data for the return period
            start_date = datetime.strptime(tds_return.return_period, '%Y-%m').date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
            
            # Get purchase bills with TDS
            purchase_bills = db.query(PurchaseBill).filter(
                PurchaseBill.company_id == tds_return.company_id,
                PurchaseBill.bill_date >= start_date,
                PurchaseBill.bill_date <= end_date,
                PurchaseBill.tds_amount > 0
            ).all()
            
            total_tds_deducted = sum(bill.tds_amount for bill in purchase_bills)
            
            return {
                'status': 'success',
                'bills_count': len(purchase_bills),
                'total_tds_deducted': total_tds_deducted
            }
            
        except Exception as e:
            logger.error(f"Error integrating TDS return with purchase: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_tds_return_with_accounting(self, db: Session, tds_return: TDSReturn) -> Dict:
        """Integrate TDS return with accounting module"""
        
        try:
            # Create journal entry for TDS return
            journal_entry = JournalEntry(
                company_id=tds_return.company_id,
                entry_number=f"TDS-RET-{tds_return.return_period}",
                entry_date=tds_return.filing_date,
                reference_type='tds_return',
                reference_id=tds_return.id,
                narration=f"TDS return for period {tds_return.return_period}",
                total_debit=tds_return.total_payable,
                total_credit=tds_return.total_payable,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            if tds_return.total_payable > 0:
                # Debit: TDS Payable
                tds_payable_account = self.get_tds_payable_account(db, tds_return.company_id)
                journal_item_payable = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=tds_payable_account.id,
                    debit_amount=tds_return.total_payable,
                    credit_amount=0,
                    description=f"TDS payable for period {tds_return.return_period}"
                )
                db.add(journal_item_payable)
                
                # Credit: Cash/Bank
                cash_account = self.get_cash_account(db, tds_return.company_id)
                journal_item_cash = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=cash_account.id,
                    debit_amount=0,
                    credit_amount=tds_return.total_payable,
                    description=f"TDS payment for period {tds_return.return_period}"
                )
                db.add(journal_item_cash)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for TDS return'
            }
            
        except Exception as e:
            logger.error(f"Error integrating TDS return with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_e_invoice_with_integrations(self, db: Session, invoice_data: Dict) -> Dict:
        """Process E-invoice with full module integrations"""
        
        try:
            # Create E-invoice
            e_invoice = EInvoice(
                company_id=invoice_data['company_id'],
                invoice_id=invoice_data['invoice_id'],
                invoice_number=invoice_data['invoice_number'],
                invoice_date=invoice_data['invoice_date'],
                customer_id=invoice_data['customer_id'],
                customer_gst=invoice_data.get('customer_gst'),
                total_amount=invoice_data['total_amount'],
                tax_amount=invoice_data['tax_amount'],
                irn=invoice_data.get('irn'),
                qr_code=invoice_data.get('qr_code'),
                status=invoice_data.get('status', 'draft'),
                ack_number=invoice_data.get('ack_number'),
                ack_date=invoice_data.get('ack_date')
            )
            
            db.add(e_invoice)
            db.flush()
            
            # Create E-invoice items
            for item_data in invoice_data.get('items', []):
                e_invoice_item = EInvoiceItem(
                    e_invoice_id=e_invoice.id,
                    item_id=item_data['item_id'],
                    item_name=item_data['item_name'],
                    hsn_code=item_data.get('hsn_code'),
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    tax_rate=item_data.get('tax_rate', 0),
                    tax_amount=item_data.get('tax_amount', 0)
                )
                db.add(e_invoice_item)
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Sales Integration
            sales_result = self.integrate_e_invoice_with_sales(db, e_invoice)
            integration_results['sales'] = sales_result
            
            # 2. Customer Integration
            customer_result = self.integrate_e_invoice_with_customer(db, e_invoice)
            integration_results['customer'] = customer_result
            
            # 3. Accounting Integration
            accounting_result = self.integrate_e_invoice_with_accounting(db, e_invoice)
            integration_results['accounting'] = accounting_result
            
            db.commit()
            
            return {
                'success': True,
                'e_invoice_id': e_invoice.id,
                'invoice_number': e_invoice.invoice_number,
                'irn': e_invoice.irn,
                'integration_results': integration_results,
                'message': 'E-invoice processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing E-invoice with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process E-invoice: {str(e)}")
    
    def integrate_e_invoice_with_sales(self, db: Session, e_invoice: EInvoice) -> Dict:
        """Integrate E-invoice with sales module"""
        
        try:
            # Get corresponding sale invoice
            sale_invoice = db.query(SaleInvoice).filter(
                SaleInvoice.id == e_invoice.invoice_id
            ).first()
            
            if sale_invoice:
                # Update sale invoice with E-invoice details
                sale_invoice.irn = e_invoice.irn
                sale_invoice.qr_code = e_invoice.qr_code
                sale_invoice.e_invoice_status = e_invoice.status
                
                return {
                    'status': 'success',
                    'sale_invoice_id': sale_invoice.id,
                    'irn': e_invoice.irn,
                    'message': 'Sale invoice updated with E-invoice details'
                }
            
            return {'status': 'skipped', 'message': 'No corresponding sale invoice found'}
            
        except Exception as e:
            logger.error(f"Error integrating E-invoice with sales: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_e_invoice_with_customer(self, db: Session, e_invoice: EInvoice) -> Dict:
        """Integrate E-invoice with customer module"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == e_invoice.customer_id).first()
            
            if customer:
                # Update customer with GST number if available
                if e_invoice.customer_gst:
                    customer.gst_number = e_invoice.customer_gst
                
                return {
                    'status': 'success',
                    'customer_id': customer.id,
                    'customer_gst': e_invoice.customer_gst,
                    'message': 'Customer updated with GST details'
                }
            
            return {'status': 'error', 'message': 'Customer not found'}
            
        except Exception as e:
            logger.error(f"Error integrating E-invoice with customer: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_e_invoice_with_accounting(self, db: Session, e_invoice: EInvoice) -> Dict:
        """Integrate E-invoice with accounting module"""
        
        try:
            # Create journal entry for E-invoice
            journal_entry = JournalEntry(
                company_id=e_invoice.company_id,
                entry_number=f"E-INV-{e_invoice.invoice_number}",
                entry_date=e_invoice.invoice_date,
                reference_type='e_invoice',
                reference_id=e_invoice.id,
                narration=f"E-invoice {e_invoice.invoice_number}",
                total_debit=e_invoice.total_amount,
                total_credit=e_invoice.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Accounts Receivable
            ar_account = self.get_accounts_receivable_account(db, e_invoice.company_id)
            journal_item_ar = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=ar_account.id,
                debit_amount=e_invoice.total_amount,
                credit_amount=0,
                description=f"Accounts receivable for E-invoice {e_invoice.invoice_number}"
            )
            db.add(journal_item_ar)
            
            # Credit: Sales Revenue
            sales_account = self.get_sales_revenue_account(db, e_invoice.company_id)
            journal_item_sales = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=e_invoice.total_amount,
                description=f"Sales revenue for E-invoice {e_invoice.invoice_number}"
            )
            db.add(journal_item_sales)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for E-invoice'
            }
            
        except Exception as e:
            logger.error(f"Error integrating E-invoice with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_compliance_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive compliance analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get GST analytics
            gst_analytics = self.get_gst_analytics(db, company_id, from_date, to_date)
            
            # Get TDS analytics
            tds_analytics = self.get_tds_analytics(db, company_id, from_date, to_date)
            
            # Get TCS analytics
            tcs_analytics = self.get_tcs_analytics(db, company_id, from_date, to_date)
            
            # Get E-invoice analytics
            e_invoice_analytics = self.get_e_invoice_analytics(db, company_id, from_date, to_date)
            
            return {
                'gst_analytics': gst_analytics,
                'tds_analytics': tds_analytics,
                'tcs_analytics': tcs_analytics,
                'e_invoice_analytics': e_invoice_analytics,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance analytics: {str(e)}")
            return {
                'gst_analytics': {},
                'tds_analytics': {},
                'tcs_analytics': {},
                'e_invoice_analytics': {},
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def get_gst_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get GST analytics"""
        try:
            # Get GST returns
            gst_returns = db.query(GSTReturn).filter(
                GSTReturn.company_id == company_id,
                GSTReturn.filing_date >= from_date,
                GSTReturn.filing_date <= to_date
            ).all()
            
            total_returns = len(gst_returns)
            total_output_tax = sum(return_data.output_tax for return_data in gst_returns)
            total_input_tax = sum(return_data.input_tax for return_data in gst_returns)
            total_net_tax = sum(return_data.net_tax for return_data in gst_returns)
            
            return {
                'total_returns': total_returns,
                'total_output_tax': total_output_tax,
                'total_input_tax': total_input_tax,
                'total_net_tax': total_net_tax
            }
        except Exception as e:
            logger.error(f"Error getting GST analytics: {str(e)}")
            return {}
    
    def get_tds_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get TDS analytics"""
        try:
            # Get TDS returns
            tds_returns = db.query(TDSReturn).filter(
                TDSReturn.company_id == company_id,
                TDSReturn.filing_date >= from_date,
                TDSReturn.filing_date <= to_date
            ).all()
            
            total_returns = len(tds_returns)
            total_tds_deducted = sum(return_data.total_tds_deducted for return_data in tds_returns)
            total_tds_deposited = sum(return_data.total_tds_deposited for return_data in tds_returns)
            
            return {
                'total_returns': total_returns,
                'total_tds_deducted': total_tds_deducted,
                'total_tds_deposited': total_tds_deposited
            }
        except Exception as e:
            logger.error(f"Error getting TDS analytics: {str(e)}")
            return {}
    
    def get_tcs_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get TCS analytics"""
        try:
            # Get TCS returns
            tcs_returns = db.query(TCSReturn).filter(
                TCSReturn.company_id == company_id,
                TCSReturn.filing_date >= from_date,
                TCSReturn.filing_date <= to_date
            ).all()
            
            total_returns = len(tcs_returns)
            total_tcs_collected = sum(return_data.total_tcs_collected for return_data in tcs_returns)
            total_tcs_deposited = sum(return_data.total_tcs_deposited for return_data in tcs_returns)
            
            return {
                'total_returns': total_returns,
                'total_tcs_collected': total_tcs_collected,
                'total_tcs_deposited': total_tcs_deposited
            }
        except Exception as e:
            logger.error(f"Error getting TCS analytics: {str(e)}")
            return {}
    
    def get_e_invoice_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get E-invoice analytics"""
        try:
            # Get E-invoices
            e_invoices = db.query(EInvoice).filter(
                EInvoice.company_id == company_id,
                EInvoice.invoice_date >= from_date,
                EInvoice.invoice_date <= to_date
            ).all()
            
            total_invoices = len(e_invoices)
            total_amount = sum(invoice.total_amount for invoice in e_invoices)
            total_tax = sum(invoice.tax_amount for invoice in e_invoices)
            
            return {
                'total_invoices': total_invoices,
                'total_amount': total_amount,
                'total_tax': total_tax
            }
        except Exception as e:
            logger.error(f"Error getting E-invoice analytics: {str(e)}")
            return {}
    
    # Helper methods
    def get_gst_payable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get GST payable account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%gst payable%')
        ).first()
    
    def get_tds_payable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get TDS payable account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%tds payable%')
        ).first()
    
    def get_cash_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get cash account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%cash%')
        ).first()
    
    def get_accounts_receivable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get accounts receivable account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%accounts receivable%')
        ).first()
    
    def get_sales_revenue_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get sales revenue account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'revenue'
        ).first()