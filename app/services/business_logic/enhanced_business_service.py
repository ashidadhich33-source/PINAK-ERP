# backend/app/services/business_logic/enhanced_business_service.py
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from ...models.sales import SaleInvoice, SaleChallan, SaleOrder
from ...models.purchase import PurchaseInvoice, PurchaseOrder
from ...models.inventory import Item, StockMovement
from ...models.customers import Customer
from ...models.suppliers import Supplier
from ...models.accounting import JournalEntry, Account
from ...schemas.enhanced_validation import BusinessRuleValidator

logger = logging.getLogger(__name__)

class EnhancedBusinessService:
    """Enhanced business logic service with modular functions"""
    
    def __init__(self):
        self.calculation_service = CalculationService()
        self.validation_service = ValidationService()
        self.workflow_service = WorkflowService()
        self.notification_service = NotificationService()
        self.analytics_service = AnalyticsService()
    
    # Sales Business Logic
    def process_sale_workflow(self, sale_data: Dict, db: Session) -> Dict:
        """Process complete sales workflow with all business rules"""
        try:
            # 1. Validate business rules
            validation_result = self.validation_service.validate_sale_creation(sale_data, db)
            if not validation_result['valid']:
                return {'success': False, 'errors': validation_result['errors']}
            
            # 2. Calculate totals
            totals = self.calculation_service.calculate_sale_totals(sale_data['items'])
            
            # 3. Apply business rules
            totals = self.validation_service.apply_sale_business_rules(totals, sale_data, db)
            
            # 4. Create database records
            sale_record = self._create_sale_record(sale_data, totals, db)
            
            # 5. Update inventory
            inventory_result = self._update_inventory_for_sale(sale_data['items'], db)
            if not inventory_result['success']:
                db.rollback()
                return {'success': False, 'error': 'Inventory update failed'}
            
            # 6. Create accounting entries
            accounting_result = self._create_sale_accounting_entries(sale_record, totals, db)
            if not accounting_result['success']:
                db.rollback()
                return {'success': False, 'error': 'Accounting entry creation failed'}
            
            # 7. Send notifications
            self.notification_service.send_sale_notifications(sale_record)
            
            # 8. Update analytics
            self.analytics_service.update_sales_analytics(sale_record)
            
            db.commit()
            
            return {
                'success': True,
                'sale_id': sale_record.id,
                'totals': totals,
                'message': 'Sale processed successfully'
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in sale workflow: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def calculate_sale_totals(self, items: List[Dict]) -> Dict:
        """Calculate comprehensive sale totals"""
        return self.calculation_service.calculate_sale_totals(items)
    
    def apply_sale_discounts(self, totals: Dict, discount_rules: List[Dict]) -> Dict:
        """Apply discount rules to sale totals"""
        return self.calculation_service.apply_sale_discounts(totals, discount_rules)
    
    def calculate_sale_taxes(self, subtotal: Decimal, tax_config: Dict) -> Decimal:
        """Calculate taxes based on configuration"""
        return self.calculation_service.calculate_sale_taxes(subtotal, tax_config)
    
    def validate_sale_business_rules(self, sale_data: Dict, db: Session) -> bool:
        """Validate all business rules for sale"""
        return self.validation_service.validate_sale_business_rules(sale_data, db)
    
    def process_sale_payment(self, payment_data: Dict, db: Session) -> Dict:
        """Process payment for sale"""
        return self.workflow_service.process_sale_payment(payment_data, db)
    
    def send_sale_notifications(self, sale_id: int, notification_type: str) -> bool:
        """Send notifications for sale events"""
        return self.notification_service.send_sale_notifications(sale_id, notification_type)
    
    def update_sale_analytics(self, sale_data: Dict) -> bool:
        """Update sales analytics"""
        return self.analytics_service.update_sales_analytics(sale_data)
    
    # Purchase Business Logic
    def process_purchase_workflow(self, purchase_data: Dict, db: Session) -> Dict:
        """Process complete purchase workflow"""
        try:
            # 1. Validate business rules
            validation_result = self.validation_service.validate_purchase_creation(purchase_data, db)
            if not validation_result['valid']:
                return {'success': False, 'errors': validation_result['errors']}
            
            # 2. Calculate totals
            totals = self.calculation_service.calculate_purchase_totals(purchase_data['items'])
            
            # 3. Apply business rules
            totals = self.validation_service.apply_purchase_business_rules(totals, purchase_data, db)
            
            # 4. Create database records
            purchase_record = self._create_purchase_record(purchase_data, totals, db)
            
            # 5. Update inventory
            inventory_result = self._update_inventory_for_purchase(purchase_data['items'], db)
            if not inventory_result['success']:
                db.rollback()
                return {'success': False, 'error': 'Inventory update failed'}
            
            # 6. Create accounting entries
            accounting_result = self._create_purchase_accounting_entries(purchase_record, totals, db)
            if not accounting_result['success']:
                db.rollback()
                return {'success': False, 'error': 'Accounting entry creation failed'}
            
            # 7. Send notifications
            self.notification_service.send_purchase_notifications(purchase_record)
            
            # 8. Update analytics
            self.analytics_service.update_purchase_analytics(purchase_record)
            
            db.commit()
            
            return {
                'success': True,
                'purchase_id': purchase_record.id,
                'totals': totals,
                'message': 'Purchase processed successfully'
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in purchase workflow: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Inventory Business Logic
    def process_inventory_adjustment(self, adjustment_data: Dict, db: Session) -> Dict:
        """Process inventory adjustment with business rules"""
        try:
            # 1. Validate adjustment
            if not self.validation_service.validate_inventory_adjustment(adjustment_data, db):
                return {'success': False, 'error': 'Invalid inventory adjustment'}
            
            # 2. Create stock movement
            stock_movement = self._create_stock_movement(adjustment_data, db)
            
            # 3. Update item quantity
            self._update_item_quantity(adjustment_data['item_id'], adjustment_data['quantity'], db)
            
            # 4. Check reorder levels
            reorder_result = self._check_reorder_levels(adjustment_data['item_id'], db)
            
            # 5. Send notifications if needed
            if reorder_result['needs_reorder']:
                self.notification_service.send_reorder_notification(adjustment_data['item_id'])
            
            db.commit()
            
            return {
                'success': True,
                'stock_movement_id': stock_movement.id,
                'reorder_check': reorder_result,
                'message': 'Inventory adjustment processed successfully'
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in inventory adjustment: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Accounting Business Logic
    def process_accounting_entry(self, entry_data: Dict, db: Session) -> Dict:
        """Process accounting entry with business rules"""
        try:
            # 1. Validate accounting entry
            if not self.validation_service.validate_accounting_entry(entry_data, db):
                return {'success': False, 'error': 'Invalid accounting entry'}
            
            # 2. Check debit-credit balance
            if not self.calculation_service.check_debit_credit_balance(entry_data['line_items']):
                return {'success': False, 'error': 'Debit and credit amounts must be equal'}
            
            # 3. Create journal entry
            journal_entry = self._create_journal_entry(entry_data, db)
            
            # 4. Update account balances
            self._update_account_balances(entry_data['line_items'], db)
            
            # 5. Check account limits
            limit_check = self._check_account_limits(entry_data['line_items'], db)
            if not limit_check['valid']:
                db.rollback()
                return {'success': False, 'error': limit_check['error']}
            
            db.commit()
            
            return {
                'success': True,
                'journal_entry_id': journal_entry.id,
                'message': 'Accounting entry processed successfully'
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in accounting entry: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Helper Methods
    def _create_sale_record(self, sale_data: Dict, totals: Dict, db: Session):
        """Create sale record in database"""
        # Implementation for creating sale record
        pass
    
    def _update_inventory_for_sale(self, items: List[Dict], db: Session) -> Dict:
        """Update inventory for sale"""
        try:
            for item in items:
                # Update item quantity
                db.query(Item).filter(Item.id == item['item_id']).update({
                    'quantity': Item.quantity - item['quantity']
                })
                
                # Create stock movement
                stock_movement = StockMovement(
                    item_id=item['item_id'],
                    quantity=-item['quantity'],  # Negative for sale
                    movement_type='sale',
                    reference_id=sale_data.get('sale_id'),
                    created_at=datetime.utcnow()
                )
                db.add(stock_movement)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_sale_accounting_entries(self, sale_record, totals: Dict, db: Session) -> Dict:
        """Create accounting entries for sale"""
        try:
            # Create journal entry for sale
            journal_entry = JournalEntry(
                entry_date=datetime.utcnow(),
                description=f"Sale - {sale_record.invoice_number}",
                total_amount=totals['total_amount']
            )
            db.add(journal_entry)
            db.flush()
            
            # Create debit entry (Customer Receivable)
            debit_entry = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=self._get_account_id('Accounts Receivable', db),
                debit_amount=totals['total_amount'],
                credit_amount=0
            )
            db.add(debit_entry)
            
            # Create credit entry (Sales Revenue)
            credit_entry = JournalEntryLine(
                journal_entry_id=journal_entry.id,
                account_id=self._get_account_id('Sales Revenue', db),
                debit_amount=0,
                credit_amount=totals['subtotal']
            )
            db.add(credit_entry)
            
            # Create credit entry (Tax Payable)
            if totals['tax_amount'] > 0:
                tax_entry = JournalEntryLine(
                    journal_entry_id=journal_entry.id,
                    account_id=self._get_account_id('Tax Payable', db),
                    debit_amount=0,
                    credit_amount=totals['tax_amount']
                )
                db.add(tax_entry)
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

class CalculationService:
    """Service for all calculation operations"""
    
    def calculate_sale_totals(self, items: List[Dict]) -> Dict:
        """Calculate comprehensive sale totals"""
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        tax_amount = subtotal * Decimal('0.18')  # 18% GST
        total_amount = subtotal + tax_amount
        
        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'item_count': len(items)
        }
    
    def apply_sale_discounts(self, totals: Dict, discount_rules: List[Dict]) -> Dict:
        """Apply discount rules to sale totals"""
        discount_amount = Decimal('0')
        
        for rule in discount_rules:
            if rule['type'] == 'percentage':
                if totals['subtotal'] >= rule['min_amount']:
                    discount_amount += totals['subtotal'] * (rule['discount_percent'] / 100)
            elif rule['type'] == 'fixed':
                if totals['subtotal'] >= rule['min_amount']:
                    discount_amount += rule['discount_amount']
        
        totals['discount_amount'] = discount_amount
        totals['total_amount'] = totals['subtotal'] + totals['tax_amount'] - discount_amount
        
        return totals
    
    def calculate_sale_taxes(self, subtotal: Decimal, tax_config: Dict) -> Decimal:
        """Calculate taxes based on configuration"""
        tax_rate = tax_config.get('tax_rate', Decimal('0.18'))
        return subtotal * tax_rate
    
    def calculate_purchase_totals(self, items: List[Dict]) -> Dict:
        """Calculate comprehensive purchase totals"""
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        tax_amount = subtotal * Decimal('0.18')  # 18% GST
        total_amount = subtotal + tax_amount
        
        return {
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'item_count': len(items)
        }
    
    def check_debit_credit_balance(self, line_items: List[Dict]) -> bool:
        """Check if debit and credit amounts are equal"""
        total_debit = sum(item['debit_amount'] for item in line_items)
        total_credit = sum(item['credit_amount'] for item in line_items)
        return total_debit == total_credit

class ValidationService:
    """Service for all validation operations"""
    
    def validate_sale_creation(self, sale_data: Dict, db: Session) -> Dict:
        """Validate sale creation with all business rules"""
        errors = []
        
        # Check customer exists
        customer = db.query(Customer).filter(Customer.id == sale_data['customer_id']).first()
        if not customer:
            errors.append('Customer not found')
        
        # Check credit limit
        if customer and customer.credit_limit:
            outstanding = db.query(func.sum(SaleInvoice.total_amount)).filter(
                SaleInvoice.customer_id == sale_data['customer_id'],
                SaleInvoice.payment_status == 'pending'
            ).scalar() or 0
            
            if outstanding + sale_data.get('total_amount', 0) > customer.credit_limit:
                errors.append('Credit limit exceeded')
        
        # Check inventory availability
        for item in sale_data.get('items', []):
            item_stock = db.query(Item).filter(Item.id == item['item_id']).first()
            if not item_stock or item_stock.quantity < item['quantity']:
                errors.append(f'Insufficient inventory for item {item["item_id"]}')
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def apply_sale_business_rules(self, totals: Dict, sale_data: Dict, db: Session) -> Dict:
        """Apply business rules to sale totals"""
        # Apply customer-specific discounts
        customer = db.query(Customer).filter(Customer.id == sale_data['customer_id']).first()
        if customer and customer.discount_percent:
            totals['discount_amount'] = totals['subtotal'] * (customer.discount_percent / 100)
            totals['total_amount'] = totals['subtotal'] + totals['tax_amount'] - totals['discount_amount']
        
        return totals
    
    def validate_purchase_creation(self, purchase_data: Dict, db: Session) -> Dict:
        """Validate purchase creation with all business rules"""
        errors = []
        
        # Check supplier exists
        supplier = db.query(Supplier).filter(Supplier.id == purchase_data['supplier_id']).first()
        if not supplier:
            errors.append('Supplier not found')
        
        # Check supplier credit limit
        if supplier and supplier.credit_limit:
            outstanding = db.query(func.sum(PurchaseInvoice.total_amount)).filter(
                PurchaseInvoice.supplier_id == purchase_data['supplier_id'],
                PurchaseInvoice.payment_status == 'pending'
            ).scalar() or 0
            
            if outstanding + purchase_data.get('total_amount', 0) > supplier.credit_limit:
                errors.append('Supplier credit limit exceeded')
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def apply_purchase_business_rules(self, totals: Dict, purchase_data: Dict, db: Session) -> Dict:
        """Apply business rules to purchase totals"""
        # Apply supplier-specific discounts
        supplier = db.query(Supplier).filter(Supplier.id == purchase_data['supplier_id']).first()
        if supplier and supplier.discount_percent:
            totals['discount_amount'] = totals['subtotal'] * (supplier.discount_percent / 100)
            totals['total_amount'] = totals['subtotal'] + totals['tax_amount'] - totals['discount_amount']
        
        return totals
    
    def validate_inventory_adjustment(self, adjustment_data: Dict, db: Session) -> bool:
        """Validate inventory adjustment"""
        # Check if item exists
        item = db.query(Item).filter(Item.id == adjustment_data['item_id']).first()
        if not item:
            return False
        
        # Check if adjustment is within reasonable limits
        if abs(adjustment_data['quantity']) > item.quantity * 2:
            return False
        
        return True
    
    def validate_accounting_entry(self, entry_data: Dict, db: Session) -> bool:
        """Validate accounting entry"""
        # Check if all accounts exist
        for line_item in entry_data['line_items']:
            account = db.query(Account).filter(Account.id == line_item['account_id']).first()
            if not account:
                return False
        
        return True

class WorkflowService:
    """Service for workflow management"""
    
    def process_sale_payment(self, payment_data: Dict, db: Session) -> Dict:
        """Process payment for sale"""
        try:
            # Update payment status
            sale = db.query(SaleInvoice).filter(SaleInvoice.id == payment_data['sale_id']).first()
            if not sale:
                return {'success': False, 'error': 'Sale not found'}
            
            sale.payment_status = 'paid'
            sale.payment_date = datetime.utcnow()
            sale.payment_method = payment_data['payment_method']
            
            # Create payment accounting entry
            self._create_payment_accounting_entry(sale, payment_data, db)
            
            return {'success': True, 'message': 'Payment processed successfully'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_payment_accounting_entry(self, sale, payment_data: Dict, db: Session):
        """Create accounting entry for payment"""
        # Implementation for payment accounting entry
        pass

class NotificationService:
    """Service for notifications"""
    
    def send_sale_notifications(self, sale_record):
        """Send notifications for sale events"""
        # Implementation for sale notifications
        pass
    
    def send_purchase_notifications(self, purchase_record):
        """Send notifications for purchase events"""
        # Implementation for purchase notifications
        pass
    
    def send_reorder_notification(self, item_id: int):
        """Send reorder notification"""
        # Implementation for reorder notifications
        pass

class AnalyticsService:
    """Service for analytics"""
    
    def update_sales_analytics(self, sale_data: Dict):
        """Update sales analytics"""
        # Implementation for sales analytics
        pass
    
    def update_purchase_analytics(self, purchase_data: Dict):
        """Update purchase analytics"""
        # Implementation for purchase analytics
        pass

# Initialize the enhanced business service
enhanced_business_service = EnhancedBusinessService()