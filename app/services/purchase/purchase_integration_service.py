# backend/app/services/purchase/purchase_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseBill, PurchaseBillItem, PurchasePayment
from ...models.suppliers import Supplier
from ...models.inventory import Item, StockItem
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.core.discount_management import DiscountRule, DiscountCoupon
from ...models.pos.pos_models import POSTransaction
from ...models.core.payment import Payment

logger = logging.getLogger(__name__)

class PurchaseIntegrationService:
    """Service for purchase integration with all modules"""
    
    def __init__(self):
        self.purchase_cache = {}
        self.supplier_cache = {}
    
    def create_purchase_order_with_integrations(self, db: Session, order_data: Dict) -> Dict:
        """Create purchase order with full module integrations"""
        
        try:
            # Create purchase order
            purchase_order = PurchaseOrder(
                company_id=order_data['company_id'],
                order_number=order_data['order_number'],
                order_date=order_data['order_date'],
                supplier_id=order_data['supplier_id'],
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
            
            db.add(purchase_order)
            db.flush()
            
            # Create purchase order items
            order_items = []
            for item_data in order_data['items']:
                order_item = PurchaseOrderItem(
                    purchase_order_id=purchase_order.id,
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
            
            # 1. Supplier Integration
            supplier_result = self.integrate_with_supplier(db, purchase_order)
            integration_results['supplier'] = supplier_result
            
            # 2. Inventory Integration (reserve stock)
            inventory_result = self.integrate_with_inventory_reservation(db, purchase_order)
            integration_results['inventory'] = inventory_result
            
            # 3. Discount Integration
            discount_result = self.integrate_with_discounts(db, purchase_order, order_data.get('applied_discounts', []))
            integration_results['discounts'] = discount_result
            
            db.commit()
            
            return {
                'success': True,
                'purchase_order_id': purchase_order.id,
                'order_number': purchase_order.order_number,
                'integration_results': integration_results,
                'message': 'Purchase order created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating purchase order with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create purchase order: {str(e)}")
    
    def integrate_with_supplier(self, db: Session, purchase_order: PurchaseOrder) -> Dict:
        """Integrate purchase order with supplier module"""
        
        try:
            # Get supplier
            supplier = db.query(Supplier).filter(Supplier.id == purchase_order.supplier_id).first()
            if not supplier:
                return {'status': 'error', 'message': 'Supplier not found'}
            
            # Update supplier analytics
            supplier.total_purchases = (supplier.total_purchases or 0) + purchase_order.total_amount
            supplier.last_purchase_date = purchase_order.order_date
            
            # Update supplier rating if applicable
            if hasattr(supplier, 'rating'):
                # Calculate rating based on purchase frequency and amount
                new_rating = self.calculate_supplier_rating(db, supplier)
                if new_rating != supplier.rating:
                    supplier.rating = new_rating
            
            return {
                'status': 'success',
                'supplier_id': supplier.id,
                'supplier_name': supplier.name,
                'total_purchases': supplier.total_purchases,
                'rating': getattr(supplier, 'rating', 0)
            }
            
        except Exception as e:
            logger.error(f"Error integrating with supplier: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_inventory_reservation(self, db: Session, purchase_order: PurchaseOrder) -> Dict:
        """Integrate purchase order with inventory reservation"""
        
        try:
            # Get purchase order items
            order_items = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.purchase_order_id == purchase_order.id
            ).all()
            
            inventory_updates = []
            
            for item in order_items:
                # Check if item exists in inventory
                existing_item = db.query(Item).filter(Item.id == item.item_id).first()
                
                if not existing_item:
                    # Create new item if it doesn't exist
                    new_item = Item(
                        company_id=purchase_order.company_id,
                        name=f"Item from {purchase_order.supplier_id}",
                        item_code=f"ITEM-{item.item_id}",
                        cost_price=item.unit_price,
                        selling_price=item.unit_price * 1.2,  # 20% markup
                        minimum_stock_level=0
                    )
                    db.add(new_item)
                    db.flush()
                    item.item_id = new_item.id
                
                inventory_updates.append({
                    'item_id': item.item_id,
                    'quantity_ordered': item.quantity,
                    'unit_price': item.unit_price,
                    'total_price': item.total_price
                })
            
            return {
                'status': 'success',
                'inventory_updates': inventory_updates,
                'message': 'Inventory items prepared for purchase order'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with inventory reservation: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_discounts(self, db: Session, purchase_order: PurchaseOrder, applied_discounts: List[Dict]) -> Dict:
        """Integrate purchase order with discount module"""
        
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
                        discount_rule, purchase_order.subtotal
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
    
    def create_purchase_bill_with_integrations(self, db: Session, bill_data: Dict) -> Dict:
        """Create purchase bill with full module integrations"""
        
        try:
            # Create purchase bill
            purchase_bill = PurchaseBill(
                company_id=bill_data['company_id'],
                bill_number=bill_data['bill_number'],
                bill_date=bill_data['bill_date'],
                supplier_id=bill_data['supplier_id'],
                purchase_order_id=bill_data.get('purchase_order_id'),
                subtotal=bill_data['subtotal'],
                discount_amount=bill_data.get('discount_amount', 0),
                tax_amount=bill_data.get('tax_amount', 0),
                total_amount=bill_data['total_amount'],
                payment_status='pending',
                due_date=bill_data.get('due_date'),
                notes=bill_data.get('notes')
            )
            
            db.add(purchase_bill)
            db.flush()
            
            # Create bill items
            for item_data in bill_data['items']:
                bill_item = PurchaseBillItem(
                    purchase_bill_id=purchase_bill.id,
                    item_id=item_data['item_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                db.add(bill_item)
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_with_accounting(db, purchase_bill)
            integration_results['accounting'] = accounting_result
            
            # 2. Inventory Integration (add stock)
            inventory_result = self.integrate_with_inventory_addition(db, purchase_bill)
            integration_results['inventory'] = inventory_result
            
            # 3. Supplier Integration
            supplier_result = self.integrate_with_supplier_bill(db, purchase_bill)
            integration_results['supplier'] = supplier_result
            
            db.commit()
            
            return {
                'success': True,
                'purchase_bill_id': purchase_bill.id,
                'bill_number': purchase_bill.bill_number,
                'integration_results': integration_results,
                'message': 'Purchase bill created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating purchase bill with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create purchase bill: {str(e)}")
    
    def integrate_with_accounting(self, db: Session, purchase_bill: PurchaseBill) -> Dict:
        """Integrate purchase bill with accounting module"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=purchase_bill.company_id,
                entry_number=f"PURCH-{purchase_bill.bill_number}",
                entry_date=purchase_bill.bill_date,
                reference_type='purchase_bill',
                reference_id=purchase_bill.id,
                narration=f"Purchase bill {purchase_bill.bill_number}",
                total_debit=purchase_bill.total_amount,
                total_credit=purchase_bill.total_amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Inventory or Expense
            if purchase_bill.bill_type == 'goods':
                # If goods, debit inventory
                inventory_account = self.get_inventory_account(db, purchase_bill.company_id)
                journal_item_inventory = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=inventory_account.id,
                    debit_amount=purchase_bill.total_amount,
                    credit_amount=0,
                    description=f"Inventory purchase for bill {purchase_bill.bill_number}"
                )
                db.add(journal_item_inventory)
            else:
                # If services, debit expense
                expense_account = self.get_expense_account(db, purchase_bill.company_id)
                journal_item_expense = JournalEntryItem(
                    entry_id=journal_entry.id,
                    account_id=expense_account.id,
                    debit_amount=purchase_bill.total_amount,
                    credit_amount=0,
                    description=f"Expense for bill {purchase_bill.bill_number}"
                )
                db.add(journal_item_expense)
            
            # Credit: Accounts Payable
            ap_account = self.get_accounts_payable_account(db, purchase_bill.company_id)
            journal_item_ap = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=ap_account.id,
                debit_amount=0,
                credit_amount=purchase_bill.total_amount,
                description=f"Accounts payable for bill {purchase_bill.bill_number}"
            )
            db.add(journal_item_ap)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for purchase bill'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_inventory_addition(self, db: Session, purchase_bill: PurchaseBill) -> Dict:
        """Integrate purchase bill with inventory addition"""
        
        try:
            # Get bill items
            bill_items = db.query(PurchaseBillItem).filter(
                PurchaseBillItem.purchase_bill_id == purchase_bill.id
            ).all()
            
            stock_updates = []
            
            for item in bill_items:
                # Get or create stock item
                stock_item = db.query(StockItem).filter(
                    StockItem.item_id == item.item_id,
                    StockItem.location_id == purchase_bill.location_id
                ).first()
                
                if not stock_item:
                    # Create new stock item
                    stock_item = StockItem(
                        item_id=item.item_id,
                        location_id=purchase_bill.location_id,
                        quantity=0,
                        reserved_quantity=0,
                        available_quantity=0,
                        average_cost=0,
                        last_cost=0
                    )
                    db.add(stock_item)
                
                # Update stock quantities
                old_quantity = stock_item.quantity
                old_average_cost = stock_item.average_cost
                
                # Calculate new average cost
                total_cost = (old_quantity * old_average_cost) + (item.quantity * item.unit_price)
                total_quantity = old_quantity + item.quantity
                new_average_cost = total_cost / total_quantity if total_quantity > 0 else 0
                
                # Update stock item
                stock_item.quantity += item.quantity
                stock_item.available_quantity += item.quantity
                stock_item.average_cost = new_average_cost
                stock_item.last_cost = item.unit_price
                stock_item.update_available_quantity()
                
                # Update last movement
                stock_item.last_movement_date = datetime.utcnow()
                stock_item.last_movement_type = 'purchase'
                
                stock_updates.append({
                    'item_id': item.item_id,
                    'quantity_added': item.quantity,
                    'new_quantity': stock_item.quantity,
                    'new_average_cost': new_average_cost,
                    'new_available': stock_item.available_quantity
                })
            
            return {
                'status': 'success',
                'stock_updates': stock_updates,
                'message': 'Stock added for purchase bill'
            }
            
        except Exception as e:
            logger.error(f"Error integrating with inventory addition: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_with_supplier_bill(self, db: Session, purchase_bill: PurchaseBill) -> Dict:
        """Integrate purchase bill with supplier module"""
        
        try:
            # Get supplier
            supplier = db.query(Supplier).filter(Supplier.id == purchase_bill.supplier_id).first()
            if not supplier:
                return {'status': 'error', 'message': 'Supplier not found'}
            
            # Update supplier analytics
            supplier.total_purchases = (supplier.total_purchases or 0) + purchase_bill.total_amount
            supplier.last_purchase_date = purchase_bill.bill_date
            
            # Update supplier outstanding amount
            if hasattr(supplier, 'outstanding_amount'):
                supplier.outstanding_amount = (supplier.outstanding_amount or 0) + purchase_bill.total_amount
            
            return {
                'status': 'success',
                'supplier_id': supplier.id,
                'total_purchases': supplier.total_purchases,
                'outstanding_amount': getattr(supplier, 'outstanding_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error integrating with supplier bill: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_purchase_payment_with_integrations(self, db: Session, payment_data: Dict) -> Dict:
        """Process purchase payment with full module integrations"""
        
        try:
            # Create purchase payment
            purchase_payment = PurchasePayment(
                company_id=payment_data['company_id'],
                payment_number=payment_data['payment_number'],
                payment_date=payment_data['payment_date'],
                purchase_bill_id=payment_data['purchase_bill_id'],
                amount=payment_data['amount'],
                payment_method=payment_data['payment_method'],
                payment_reference=payment_data.get('payment_reference'),
                notes=payment_data.get('notes')
            )
            
            db.add(purchase_payment)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Accounting Integration
            accounting_result = self.integrate_payment_with_accounting(db, purchase_payment)
            integration_results['accounting'] = accounting_result
            
            # 2. Supplier Integration
            supplier_result = self.integrate_payment_with_supplier(db, purchase_payment)
            integration_results['supplier'] = supplier_result
            
            # 3. Update bill status
            bill_result = self.update_bill_payment_status(db, purchase_payment)
            integration_results['bill'] = bill_result
            
            db.commit()
            
            return {
                'success': True,
                'payment_id': purchase_payment.id,
                'payment_number': purchase_payment.payment_number,
                'integration_results': integration_results,
                'message': 'Purchase payment processed with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error processing purchase payment with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process purchase payment: {str(e)}")
    
    def integrate_payment_with_accounting(self, db: Session, purchase_payment: PurchasePayment) -> Dict:
        """Integrate purchase payment with accounting module"""
        
        try:
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=purchase_payment.company_id,
                entry_number=f"PURCH-PAY-{purchase_payment.payment_number}",
                entry_date=purchase_payment.payment_date,
                reference_type='purchase_payment',
                reference_id=purchase_payment.id,
                narration=f"Payment made for bill {purchase_payment.purchase_bill_id}",
                total_debit=purchase_payment.amount,
                total_credit=purchase_payment.amount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Accounts Payable
            ap_account = self.get_accounts_payable_account(db, purchase_payment.company_id)
            journal_item_ap = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=ap_account.id,
                debit_amount=purchase_payment.amount,
                credit_amount=0,
                description=f"Accounts payable cleared for payment {purchase_payment.payment_number}"
            )
            db.add(journal_item_ap)
            
            # Credit: Cash/Bank
            cash_account = self.get_cash_account(db, purchase_payment.company_id)
            journal_item_cash = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=cash_account.id,
                debit_amount=0,
                credit_amount=purchase_payment.amount,
                description=f"Cash paid for payment {purchase_payment.payment_number}"
            )
            db.add(journal_item_cash)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Journal entry created for purchase payment'
            }
            
        except Exception as e:
            logger.error(f"Error integrating payment with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_payment_with_supplier(self, db: Session, purchase_payment: PurchasePayment) -> Dict:
        """Integrate purchase payment with supplier module"""
        
        try:
            # Get purchase bill
            purchase_bill = db.query(PurchaseBill).filter(
                PurchaseBill.id == purchase_payment.purchase_bill_id
            ).first()
            
            if not purchase_bill:
                return {'status': 'error', 'message': 'Purchase bill not found'}
            
            # Get supplier
            supplier = db.query(Supplier).filter(Supplier.id == purchase_bill.supplier_id).first()
            if not supplier:
                return {'status': 'error', 'message': 'Supplier not found'}
            
            # Update supplier outstanding amount
            if hasattr(supplier, 'outstanding_amount'):
                supplier.outstanding_amount = max(0, (supplier.outstanding_amount or 0) - purchase_payment.amount)
            
            return {
                'status': 'success',
                'supplier_id': supplier.id,
                'outstanding_amount': getattr(supplier, 'outstanding_amount', 0)
            }
            
        except Exception as e:
            logger.error(f"Error integrating payment with supplier: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def update_bill_payment_status(self, db: Session, purchase_payment: PurchasePayment) -> Dict:
        """Update bill payment status"""
        
        try:
            # Get purchase bill
            purchase_bill = db.query(PurchaseBill).filter(
                PurchaseBill.id == purchase_payment.purchase_bill_id
            ).first()
            
            if not purchase_bill:
                return {'status': 'error', 'message': 'Purchase bill not found'}
            
            # Calculate total payments
            total_payments = db.query(func.sum(PurchasePayment.amount)).filter(
                PurchasePayment.purchase_bill_id == purchase_bill.id
            ).scalar() or 0
            
            # Update payment status
            if total_payments >= purchase_bill.total_amount:
                purchase_bill.payment_status = 'paid'
            elif total_payments > 0:
                purchase_bill.payment_status = 'partial'
            else:
                purchase_bill.payment_status = 'pending'
            
            return {
                'status': 'success',
                'payment_status': purchase_bill.payment_status,
                'total_payments': total_payments,
                'remaining_amount': purchase_bill.total_amount - total_payments
            }
            
        except Exception as e:
            logger.error(f"Error updating bill payment status: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_purchase_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive purchase analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get purchase data
            purchase_query = db.query(PurchaseOrder).filter(
                PurchaseOrder.company_id == company_id,
                PurchaseOrder.order_date >= from_date,
                PurchaseOrder.order_date <= to_date
            )
            
            purchase_orders = purchase_query.all()
            
            # Get bill data
            bill_query = db.query(PurchaseBill).filter(
                PurchaseBill.company_id == company_id,
                PurchaseBill.bill_date >= from_date,
                PurchaseBill.bill_date <= to_date
            )
            
            purchase_bills = bill_query.all()
            
            # Calculate metrics
            total_orders = len(purchase_orders)
            total_bills = len(purchase_bills)
            total_purchase_amount = sum(order.total_amount for order in purchase_orders)
            total_bill_amount = sum(bill.total_amount for bill in purchase_bills)
            average_order_value = total_purchase_amount / total_orders if total_orders > 0 else 0
            
            # Get supplier analytics
            supplier_analytics = self.get_supplier_purchase_analytics(db, company_id, from_date, to_date)
            
            # Get product analytics
            product_analytics = self.get_product_purchase_analytics(db, company_id, from_date, to_date)
            
            return {
                'total_orders': total_orders,
                'total_bills': total_bills,
                'total_purchase_amount': total_purchase_amount,
                'total_bill_amount': total_bill_amount,
                'average_order_value': average_order_value,
                'supplier_analytics': supplier_analytics,
                'product_analytics': product_analytics,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting purchase analytics: {str(e)}")
            return {
                'total_orders': 0,
                'total_bills': 0,
                'total_purchase_amount': 0,
                'total_bill_amount': 0,
                'average_order_value': 0,
                'supplier_analytics': {},
                'product_analytics': {},
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def get_supplier_purchase_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get supplier purchase analytics"""
        
        try:
            # Get top suppliers by purchases
            top_suppliers = db.query(
                Supplier.id,
                Supplier.name,
                func.sum(PurchaseOrder.total_amount).label('total_purchases')
            ).join(PurchaseOrder).filter(
                PurchaseOrder.company_id == company_id,
                PurchaseOrder.order_date >= from_date,
                PurchaseOrder.order_date <= to_date
            ).group_by(Supplier.id, Supplier.name).order_by(
                desc('total_purchases')
            ).limit(10).all()
            
            return {
                'top_suppliers': [
                    {
                        'supplier_id': supplier.id,
                        'supplier_name': supplier.name,
                        'total_purchases': supplier.total_purchases
                    }
                    for supplier in top_suppliers
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting supplier purchase analytics: {str(e)}")
            return {'top_suppliers': []}
    
    def get_product_purchase_analytics(self, db: Session, company_id: int, from_date: date, to_date: date) -> Dict:
        """Get product purchase analytics"""
        
        try:
            # Get top products by purchases
            top_products = db.query(
                Item.id,
                Item.name,
                func.sum(PurchaseOrderItem.quantity).label('total_quantity'),
                func.sum(PurchaseOrderItem.total_price).label('total_purchases')
            ).join(PurchaseOrderItem).join(PurchaseOrder).filter(
                PurchaseOrder.company_id == company_id,
                PurchaseOrder.order_date >= from_date,
                PurchaseOrder.order_date <= to_date
            ).group_by(Item.id, Item.name).order_by(
                desc('total_purchases')
            ).limit(10).all()
            
            return {
                'top_products': [
                    {
                        'item_id': product.id,
                        'item_name': product.name,
                        'total_quantity': product.total_quantity,
                        'total_purchases': product.total_purchases
                    }
                    for product in top_products
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting product purchase analytics: {str(e)}")
            return {'top_products': []}
    
    # Helper methods
    def calculate_supplier_rating(self, db: Session, supplier: Supplier) -> int:
        """Calculate supplier rating based on performance"""
        try:
            # Get supplier performance metrics
            total_purchases = supplier.total_purchases or 0
            purchase_frequency = self.get_supplier_purchase_frequency(db, supplier.id)
            
            # Calculate rating (1-5 stars)
            if total_purchases >= 100000 and purchase_frequency >= 10:
                return 5
            elif total_purchases >= 50000 and purchase_frequency >= 5:
                return 4
            elif total_purchases >= 10000 and purchase_frequency >= 2:
                return 3
            elif total_purchases >= 1000:
                return 2
            else:
                return 1
        except Exception as e:
            logger.error(f"Error calculating supplier rating: {str(e)}")
            return 1
    
    def get_supplier_purchase_frequency(self, db: Session, supplier_id: int) -> int:
        """Get supplier purchase frequency"""
        try:
            # Get purchase count in last 6 months
            six_months_ago = date.today() - timedelta(days=180)
            
            purchase_count = db.query(PurchaseOrder).filter(
                PurchaseOrder.supplier_id == supplier_id,
                PurchaseOrder.order_date >= six_months_ago
            ).count()
            
            return purchase_count
        except Exception as e:
            logger.error(f"Error getting supplier purchase frequency: {str(e)}")
            return 0
    
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
    
    def get_inventory_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get inventory account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%inventory%')
        ).first()
    
    def get_expense_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get expense account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'expense'
        ).first()
    
    def get_accounts_payable_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get accounts payable account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%accounts payable%')
        ).first()
    
    def get_cash_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get cash account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%cash%')
        ).first()