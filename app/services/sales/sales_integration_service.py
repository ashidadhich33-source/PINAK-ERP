# backend/app/services/sales/sales_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.sales import SaleOrder, SaleOrderItem, SaleInvoice, SaleInvoiceItem, SalePayment
from ...models.customers import Customer
from ...models.inventory import Item, StockItem
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.core.discount_management import DiscountRule, DiscountCoupon, CustomerDiscount
from ...models.loyalty import LoyaltyTransaction, LoyaltyProgram
from ...models.pos.pos_models import POSTransaction
from ...models.core.payment import Payment

logger = logging.getLogger(__name__)

class SalesIntegrationService:
    """Service for sales integration with all modules"""
    
    def __init__(self):
        self.sales_cache = {}
        self.customer_cache = {}
    
    def create_sale_order_with_integrations(self, db: Session, order_data: Dict) -> Dict:
        """Create sale order with full module integrations"""
        
        try:
            # Create sale order
            sale_order = SaleOrder(
                company_id=order_data['company_id'],
                order_number=order_data['order_number'],
                order_date=order_data['order_date'],
                customer_id=order_data['customer_id'],
                staff_id=order_data.get('staff_id'),
                subtotal=order_data['subtotal'],
                discount_amount=order_data.get('discount_amount', 0),
                tax_amount=order_data.get('tax_amount', 0),
                total_amount=order_data['total_amount'],
                status='draft',
                payment_terms=order_data.get('payment_terms'),
                delivery_date=order_data.get('delivery_date'),
                notes=order_data.get('notes')
            )
            
            db.add(sale_order)
            db.flush()
            
            # Create sale order items
            order_items = []
            for item_data in order_data['items']:
                order_item = SaleOrderItem(
                    sale_order_id=sale_order.id,
                    item_id=item_data['item_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    discount_percentage=item_data.get('discount_percentage', 0),
                    discount_amount=item_data.get('discount_amount', 0)
                )
                db.add(order_item)
                order_items.append(order_item)
            
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Customer Integration
            customer_result = self.integrate_with_customer(db, sale_order)
            integration_results['customer'] = customer_result
            
            # 2. Inventory Integration
            inventory_result = self.integrate_with_inventory(db, sale_order)
            integration_results['inventory'] = inventory_result
            
            # 3. Discount Integration
            discount_result = self.integrate_with_discounts(db, sale_order, order_data.get('applied_discounts', []))
            integration_results['discounts'] = discount_result
            
            # 4. Loyalty Integration
            loyalty_result = self.integrate_with_loyalty(db, sale_order)
            integration_results['loyalty'] = loyalty_result
            
            db.commit()
            
            return {
                'success': True,
                'sale_order_id': sale_order.id,
                'order_number': sale_order.order_number,
                'integration_results': integration_results,
                'message': 'Sale order created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating sale order with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create sale order: {str(e)}")
    
    def integrate_with_customer(self, db: Session, sale_order: SaleOrder) -> Dict:
        """Integrate sale order with customer module"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == sale_order.customer_id).first()
            if not customer:
                return {'status': 'error', 'message': 'Customer not found'}
            
            # Update customer analytics
            customer.total_purchases = (customer.total_purchases or 0) + sale_order.total_amount
            customer.last_purchase_date = sale_order.order_date
            
            # Update customer tier if applicable
            if hasattr(customer, 'customer_tier'):
                new_tier = self.calculate_customer_tier(db, customer)
                if new_tier != customer.customer_tier:
                    customer.customer_tier = new_tier
            
            return {
                'status': 'success',
                'customer_id': customer.id,
                'customer_name': customer.name,
                'total_purchases': customer.total_purchases,
                'customer_tier': getattr(customer, 'customer_tier', 'regular')
            }
            
        except Exception as e:
            logger.error(f"Error integrating with customer: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_inventory(self, db: Session, sale_order: SaleOrder) -> Dict:
        """Integrate sale order with inventory module"""
        
        try:
            # Get sale order items
            order_items = db.query(SaleOrderItem).filter(SaleOrderItem.sale_order_id == sale_order.id).all()
            
            stock_updates = []
            
            for item in order_items:
                # Check stock availability
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == sale_order.location_id
                ).first()
                
                if stock_item:
                    # Reserve stock
                    stock_item.reserved_quantity += item.quantity
                    stock_item.update_available_quantity()
                    
                    stock_updates.append({
                        'item_id': item.item_id,
                        'quantity_reserved': item.quantity,
                        'new_reserved': stock_item.reserved_quantity,
                        'new_available': stock_item.available_quantity
                    })
            
            return {
                'status': 'success',
                'stock_updates': stock_updates,
                'message': 'Stock reserved for sale order'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with inventory: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_discounts(self, db: Session, sale_order: SaleOrder, applied_discounts: List[Dict]) -> Dict:
        """Integrate sale order with discount module"""
        
        try:
            discount_applications = []
            
            for discount_data in applied_discounts:
                # Get discount rule
                discount_rule = db.query(DiscountRule).filter(
                    DiscountRule.id == discount_data['discount_id']
                ).first()
                
                if discount_rule:
                    # Apply discount
                    discount_amount = self.calculate_discount_amount(
                        discount_rule, sale_order.subtotal
                    )
                    
                    discount_applications.append({
                        'discount_id': discount_rule.id,
                        'discount_name': discount_rule.rule_name,
                        'discount_amount': discount_amount,
                        'discount_type': discount_rule.rule_type
                    })
            
            return {
                'status': 'success',
                'applied_discounts': discount_applications,
                'total_discount': sum(d['discount_amount'] for d in discount_applications)
            }
            
        except Exception as e:
            logger.error(f"Error integrating with discounts: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_loyalty(self, db: Session, sale_order: SaleOrder) -> Dict:
        """Integrate sale order with loyalty module"""
        
        try:
            # Get customer loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == sale_order.company_id
            ).first()
            
            if not loyalty_program:
                return {'status': 'skipped', 'message': 'No loyalty program found'}
            
            # Calculate points earned
            points_earned = int(sale_order.total_amount * loyalty_program.points_per_rupee)
            
            if points_earned > 0:
                # Create loyalty transaction
                loyalty_transaction = LoyaltyTransaction(
                    customer_id=sale_order.customer_id,
                    transaction_type='earned',
                    points=points_earned,
                    reference_type='sale',
                    reference_id=sale_order.id,
                    reference_number=sale_order.order_number,
                    description=f"Points earned for sale order {sale_order.order_number}"
                )
                
                db.add(loyalty_transaction)
            
            return {
                'status': 'success',
                'points_earned': points_earned,
                'loyalty_program': loyalty_program.program_name
            }
            
        except Exception as e:
            logger.error(f"Error integrating with loyalty: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_sale_invoice_with_integrations(self, db: Session, invoice_data: Dict) -> Dict:
        """Create sale invoice with full module integrations"""
        
        try:
            # Create sale invoice
            sale_invoice = SaleInvoice(
                company_id=invoice_data['company_id'],
                invoice_number=invoice_data['invoice_number'],
                invoice_date=invoice_data['invoice_date'],
                customer_id=invoice_data['customer_id'],
                sale_order_id=invoice_data.get('sale_order_id'),
                subtotal=invoice_data['subtotal'],
                discount_amount=invoice_data.get('discount_amount', 0),
                tax_amount=invoice_data.get('tax_amount', 0),
                total_amount=invoice_data['total_amount'],
                payment_status='pending',
                due_date=invoice_data.get('due_date'),
                notes=invoice_data.get('notes')
            )
            
            db.add(sale_invoice)
            db.flush()
            
            # Create invoice items
            for item_data in invoice_data['items']:
                invoice_item = SaleInvoiceItem(
                    sale_invoice_id=sale_invoice.id,
                    item_id=item_data['item_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                db.add(invoice_item)
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_with_accounting(db, sale_invoice)
            integration_results['accounting'] = accounting_result
            
            # 2. Inventory Integration (reduce stock)
            inventory_result = self.integrate_with_inventory_reduction(db, sale_invoice)
            integration_results['inventory'] = inventory_result
            
            # 3. Customer Integration
            customer_result = self.integrate_with_customer_invoice(db, sale_invoice)
            integration_results['customer'] = customer_result
            
            db.commit()
            
            return {
                'success': True,
                'sale_invoice_id': sale_invoice.id,
                'invoice_number': sale_invoice.invoice_number,
                'integration_results': integration_results,
                'message': 'Sale invoice created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating sale invoice with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create sale invoice: {str(e)}")
    
    def integrate_with_accounting(self, db: Session, sale_invoice: SaleInvoice) -> Dict:
        """Integrate sale invoice with accounting module"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=sale_invoice.company_id,
                entry_number=f"SALE-{sale_invoice.invoice_number}",
                entry_date=sale_invoice.invoice_date,
                reference_type='sale_invoice',
                reference_id=sale_invoice.id,
                narration=f"Sales invoice {sale_invoice.invoice_number}",
                total_debit=sale_invoice.total_amount,
                total_credit=sale_invoice.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Accounts Receivable
            ar_account = self.get_accounts_receivable_account(db, sale_invoice.company_id)
            journal_item_ar = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=ar_account.id,
                debit_amount=sale_invoice.total_amount,
                credit_amount=0,
                description=f"Accounts receivable for invoice {sale_invoice.invoice_number}"
            )
            db.add(journal_item_ar)
            
            # Credit: Sales Revenue
            sales_account = self.get_sales_revenue_account(db, sale_invoice.company_id)
            journal_item_sales = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=sale_invoice.total_amount,
                description=f"Sales revenue for invoice {sale_invoice.invoice_number}"
            )
            db.add(journal_item_sales)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for sale invoice'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_inventory_reduction(self, db: Session, sale_invoice: SaleInvoice) -> Dict:
        """Integrate sale invoice with inventory reduction"""
        
        try:
            # Get invoice items
            invoice_items = db.query(SaleInvoiceItem).filter(
                SaleInvoiceItem.sale_invoice_id == sale_invoice.id
            ).all()
            
            stock_updates = []
            
            for item in invoice_items:
                # Get stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == sale_invoice.location_id
                ).first()
                
                if stock_item:
                    # Reduce stock
                    stock_item.quantity -= item.quantity
                    stock_item.reserved_quantity -= item.quantity
                    stock_item.update_available_quantity()
                    
                    # Update last movement
                    stock_item.last_movement_date = datetime.utcnow()
                    stock_item.last_movement_type = 'sale'
                    
                    stock_updates.append({
                        'item_id': item.item_id,
                        'quantity_reduced': item.quantity,
                        'new_quantity': stock_item.quantity,
                        'new_available': stock_item.available_quantity
                    })
            
            return {
                'status': 'success',
                'stock_updates': stock_updates,
                'message': 'Stock reduced for sale invoice'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with inventory reduction: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_customer_invoice(self, db: Session, sale_invoice: SaleInvoice) -> Dict:
        """Integrate sale invoice with customer module"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == sale_invoice.customer_id).first()
            if not customer:
                return {'status': 'error', 'message': 'Customer not found'}
            
            # Update customer analytics
            customer.total_purchases = (customer.total_purchases or 0) + sale_invoice.total_amount
            customer.last_purchase_date = sale_invoice.invoice_date
            
            # Update customer credit limit if applicable
            if hasattr(customer, 'credit_limit'):
                customer.outstanding_amount = (customer.outstanding_amount or 0) + sale_invoice.total_amount
            
            return {
                'status': 'success',
                'customer_id': customer.id,
                'total_purchases': customer.total_purchases,
                'outstanding_amount': getattr(customer, 'outstanding_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error integrating with customer invoice: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_sale_payment_with_integrations(self, db: Session, payment_data: Dict) -> Dict:
        """Process sale payment with full module integrations"""
        
        try:
            # Create sale payment
            sale_payment = SalePayment(
                company_id=payment_data['company_id'],
                payment_number=payment_data['payment_number'],
                payment_date=payment_data['payment_date'],
                sale_invoice_id=payment_data['sale_invoice_id'],
                amount=payment_data['amount'],
                payment_method=payment_data['payment_method'],
                payment_reference=payment_data.get('payment_reference'),
                notes=payment_data.get('notes')
            )
            
            db.add(sale_payment)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_payment_with_accounting(db, sale_payment)
            integration_results['accounting'] = accounting_result
            
            # 2. Customer Integration
            customer_result = self.integrate_payment_with_customer(db, sale_payment)
            integration_results['customer'] = customer_result
            
            # 3. Update invoice status
            invoice_result = self.update_invoice_payment_status(db, sale_payment)
            integration_results['invoice'] = invoice_result
            
            db.commit()
            
            return {
                'success': True,
                'payment_id': sale_payment.id,
                'payment_number': sale_payment.payment_number,
                'integration_results': integration_results,
                'message': 'Sale payment processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing sale payment with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process sale payment: {str(e)}")
    
    def integrate_payment_with_accounting(self, db: Session, sale_payment: SalePayment) -> Dict:
        """Integrate sale payment with accounting module"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=sale_payment.company_id,
                entry_number=f"SALE-PAY-{sale_payment.payment_number}",
                entry_date=sale_payment.payment_date,
                reference_type='sale_payment',
                reference_id=sale_payment.id,
                narration=f"Payment received for invoice {sale_payment.sale_invoice_id}",
                total_debit=sale_payment.amount,
                total_credit=sale_payment.amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Cash/Bank
            cash_account = self.get_cash_account(db, sale_payment.company_id)
            journal_item_cash = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=sale_payment.amount,
                credit_amount=0,
                description=f"Cash received for payment {sale_payment.payment_number}"
            )
            db.add(journal_item_cash)
            
            # Credit: Accounts Receivable
            ar_account = self.get_accounts_receivable_account(db, sale_payment.company_id)
            journal_item_ar = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=ar_account.id,
                debit_amount=0,
                credit_amount=sale_payment.amount,
                description=f"Accounts receivable cleared for payment {sale_payment.payment_number}"
            )
            db.add(journal_item_ar)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for sale payment'
            }
            
        except Exception as e:
            logger.error(f"Error integrating payment with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_payment_with_customer(self, db: Session, sale_payment: SalePayment) -> Dict:
        """Integrate sale payment with customer module"""
        
        try:
            # Get sale invoice
            sale_invoice = db.query(SaleInvoice).filter(
                SaleInvoice.id == sale_payment.sale_invoice_id
            ).first()
            
            if not sale_invoice:
                return {'status': 'error', 'message': 'Sale invoice not found'}
            
            # Get customer
            customer = db.query(Customer).filter(Customer.id == sale_invoice.customer_id).first()
            if not customer:
                return {'status': 'error', 'message': 'Customer not found'}
            
            # Update customer outstanding amount
            if hasattr(customer, 'outstanding_amount'):
                customer.outstanding_amount = max(0, (customer.outstanding_amount or 0) - sale_payment.amount)
            
            return {
                'status': 'success',
                'customer_id': customer.id,
                'outstanding_amount': getattr(customer, 'outstanding_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error integrating payment with customer: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def update_invoice_payment_status(self, db: Session, sale_payment: SalePayment) -> Dict:
        """Update invoice payment status"""
        
        try:
            # Get sale invoice
            sale_invoice = db.query(SaleInvoice).filter(
                SaleInvoice.id == sale_payment.sale_invoice_id
            ).first()
            
            if not sale_invoice:
                return {'status': 'error', 'message': 'Sale invoice not found'}
            
            # Calculate total payments
            total_payments = db.query(func.sum(SalePayment.amount)).filter(
                SalePayment.sale_invoice_id == sale_invoice.id
            ).scalar() or 0
            
            # Update payment status
            if total_payments >= sale_invoice.total_amount:
                sale_invoice.payment_status = 'paid'
            elif total_payments > 0:
                sale_invoice.payment_status = 'partial'
            else:
                sale_invoice.payment_status = 'pending'
            
            return {
                'status': 'success',
                'payment_status': sale_invoice.payment_status,
                'total_payments': total_payments,
                'remaining_amount': sale_invoice.total_amount - total_payments
            }
            
        except Exception as e:
            logger.error(f"Error updating invoice payment status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_sales_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive sales analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get sales data
            sales_query = db.query(SaleOrder).filter(
                SaleOrder.company_id == company_id,
                SaleOrder.order_date >= from_date,
                SaleOrder.order_date <= to_date
            )
            
            sales_orders = sales_query.all()
            
            # Get invoice data
            invoice_query = db.query(SaleInvoice).filter(
                SaleInvoice.company_id == company_id,
                SaleInvoice.invoice_date >= from_date,
                SaleInvoice.invoice_date <= to_date
            )
            
            sale_invoices = invoice_query.all()
            
            # Calculate metrics
            total_orders = len(sales_orders)
            total_invoices = len(sale_invoices)
            total_sales_amount = sum(order.total_amount for order in sales_orders)
            total_invoice_amount = sum(invoice.total_amount for invoice in sale_invoices)
            average_order_value = total_sales_amount / total_orders if total_orders > 0 else 0
            
            # Get customer analytics
            customer_analytics = self.get_customer_sales_analytics(db, company_id, from_date, to_date)
            
            # Get product analytics
            product_analytics = self.get_product_sales_analytics(db, company_id, from_date, to_date)
            
            return {
                'total_orders': total_orders,
                'total_invoices': total_invoices,
                'total_sales_amount': total_sales_amount,
                'total_invoice_amount': total_invoice_amount,
                'average_order_value': average_order_value,
                'customer_analytics': customer_analytics,
                'product_analytics': product_analytics,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting sales analytics: {str(e)}")
            return {
                'total_orders': 0,
                'total_invoices': 0,
                'total_sales_amount': 0,
                'total_invoice_amount': 0,
                'average_order_value': 0,
                'customer_analytics': {},
                'product_analytics': {},
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def get_customer_sales_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get customer sales analytics"""
        
        try:
            # Get top customers by sales
            top_customers = db.query(
                Customer.id,
                Customer.name,
                func.sum(SaleOrder.total_amount).label('total_sales')
            ).join(SaleOrder).filter(
                SaleOrder.company_id == company_id,
                SaleOrder.order_date >= from_date,
                SaleOrder.order_date <= to_date
            ).group_by(Customer.id, Customer.name).order_by(
                desc('total_sales')
            ).limit(10).all()
            
            return {
                'top_customers': [
                    {
                        'customer_id': customer.id,
                        'customer_name': customer.name,
                        'total_sales': customer.total_sales
                    }
                    for customer in top_customers
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting customer sales analytics: {str(e)}")
            return {'top_customers': []}
    
    def get_product_sales_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get product sales analytics"""
        
        try:
            # Get top products by sales
            top_products = db.query(
                Item.id,
                Item.name,
                func.sum(SaleOrderItem.quantity).label('total_quantity'),
                func.sum(SaleOrderItem.total_price).label('total_sales')
            ).join(SaleOrderItem).join(SaleOrder).filter(
                SaleOrder.company_id == company_id,
                SaleOrder.order_date >= from_date,
                SaleOrder.order_date <= to_date
            ).group_by(Item.id, Item.name).order_by(
                desc('total_sales')
            ).limit(10).all()
            
            return {
                'top_products': [
                    {
                        'item_id': product.id,
                        'item_name': product.name,
                        'total_quantity': product.total_quantity,
                        'total_sales': product.total_sales
                    }
                    for product in top_products
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting product sales analytics: {str(e)}")
            return {'top_products': []}
    
    # Helper methods
    def calculate_customer_tier(self, db: Session, customer: Customer) -> str:
        """Calculate customer tier based on total purchases"""
        try:
            total_purchases = customer.total_purchases or 0
            
            if total_purchases >= 100000:
                return 'platinum'
            elif total_purchases >= 50000:
                return 'gold'
            elif total_purchases >= 10000:
                return 'silver'
            else:
                return 'bronze'
        except Exception as e:
            logger.error(f"Error calculating customer tier: {str(e)}")
            return 'bronze'
    
    def calculate_discount_amount(self, discount_rule: DiscountRule, amount: Decimal) -> Decimal:
        """Calculate discount amount for rule"""
        try:
            if discount_rule.discount_percentage:
                discount_amount = amount * (discount_rule.discount_percentage / 100)
            else:
                discount_amount = discount_rule.discount_value
            
            # Apply maximum discount limit
            if discount_rule.max_discount_amount:
                discount_amount = min(discount_amount, discount_rule.max_discount_amount)
            
            return discount_amount
        except Exception as e:
            logger.error(f"Error calculating discount amount: {str(e)}")
            return 0
    
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
    
    def get_cash_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get cash account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%cash%')
        ).first()