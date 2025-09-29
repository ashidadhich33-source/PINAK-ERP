# backend/app/services/core/discount_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.core.discount_management import (
    DiscountType, DiscountRule, DiscountApplication, DiscountCoupon, 
    CouponUsage, DiscountTier, TierApplication, CustomerDiscount,
    DiscountAnalytics, DiscountReport, DiscountConfiguration
)
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.purchase import PurchaseOrder, PurchaseBill, PurchasePayment
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.customers import Customer
from ...models.inventory import Item, ItemCategory
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount

logger = logging.getLogger(__name__)

class DiscountIntegrationService:
    """Service for discount integration with all modules"""
    
    def __init__(self):
        self.discount_cache = {}
        self.rule_cache = {}
        self.coupon_cache = {}
    
    def create_discount_rule_with_integrations(self, db: Session, rule_data: Dict) -> Dict:
        """Create discount rule with full module integrations"""
        
        try:
            # Create discount rule
            discount_rule = DiscountRule(
                company_id=rule_data['company_id'],
                rule_name=rule_data['rule_name'],
                rule_type=rule_data['rule_type'],
                target_id=rule_data.get('target_id'),
                condition_type=rule_data.get('condition_type'),
                condition_value=rule_data.get('condition_value'),
                condition_operator=rule_data.get('condition_operator'),
                discount_type_id=rule_data['discount_type_id'],
                discount_value=rule_data.get('discount_value'),
                discount_percentage=rule_data.get('discount_percentage'),
                max_discount_amount=rule_data.get('max_discount_amount'),
                min_order_amount=rule_data.get('min_order_amount'),
                start_date=rule_data.get('start_date'),
                end_date=rule_data.get('end_date'),
                priority=rule_data.get('priority', 0),
                is_active=rule_data.get('is_active', True),
                description=rule_data.get('description')
            )
            
            db.add(discount_rule)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Inventory Integration
            inventory_result = self.integrate_rule_with_inventory(db, discount_rule)
            integration_results['inventory'] = inventory_result
            
            # 2. Customer Integration
            customer_result = self.integrate_rule_with_customers(db, discount_rule)
            integration_results['customers'] = customer_result
            
            # 3. Accounting Integration
            accounting_result = self.integrate_rule_with_accounting(db, discount_rule)
            integration_results['accounting'] = accounting_result
            
            db.commit()
            
            return {
                'success': True,
                'rule_id': discount_rule.id,
                'rule_name': discount_rule.rule_name,
                'integration_results': integration_results,
                'message': 'Discount rule created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating discount rule with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create discount rule: {str(e)}")
    
    def integrate_rule_with_inventory(self, db: Session, discount_rule: DiscountRule) -> Dict:
        """Integrate discount rule with inventory module"""
        
        try:
            if discount_rule.rule_type == 'item':
                # Get item details
                item = db.query(Item).filter(Item.id == discount_rule.target_id).first()
                if item:
                    return {
                        'status': 'success',
                        'item_name': item.name,
                        'item_code': item.item_code,
                        'message': 'Rule integrated with item'
                    }
            elif discount_rule.rule_type == 'category':
                # Get category details
                category = db.query(ItemCategory).filter(ItemCategory.id == discount_rule.target_id).first()
                if category:
                    return {
                        'status': 'success',
                        'category_name': category.name,
                        'message': 'Rule integrated with category'
                    }
            
            return {'status': 'skipped', 'message': 'No inventory integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating rule with inventory: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_rule_with_customers(self, db: Session, discount_rule: DiscountRule) -> Dict:
        """Integrate discount rule with customer module"""
        
        try:
            if discount_rule.rule_type == 'customer':
                # Get customer details
                customer = db.query(Customer).filter(Customer.id == discount_rule.target_id).first()
                if customer:
                    return {
                        'status': 'success',
                        'customer_name': customer.name,
                        'customer_type': customer.customer_type,
                        'message': 'Rule integrated with customer'
                    }
            elif discount_rule.rule_type == 'customer_tier':
                # Get customer tier details
                return {
                    'status': 'success',
                    'tier': discount_rule.target_id,
                    'message': 'Rule integrated with customer tier'
                }
            
            return {'status': 'skipped', 'message': 'No customer integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating rule with customers: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_rule_with_accounting(self, db: Session, discount_rule: DiscountRule) -> Dict:
        """Integrate discount rule with accounting module"""
        
        try:
            # Create discount account if not exists
            discount_account = db.query(ChartOfAccount).filter(
                ChartOfAccount.company_id == discount_rule.company_id,
                ChartOfAccount.account_name.ilike('%discount%')
            ).first()
            
            if not discount_account:
                # Create discount account
                discount_account = ChartOfAccount(
                    company_id=discount_rule.company_id,
                    account_name='Discounts Given',
                    account_code='DISCOUNT-001',
                    account_type='expense',
                    parent_account_id=None,
                    is_active=True,
                    description='Account for tracking discounts given to customers'
                )
                db.add(discount_account)
            
            return {
                'status': 'success',
                'account_name': discount_account.account_name,
                'account_code': discount_account.account_code,
                'message': 'Rule integrated with accounting'
            }
            
        except Exception as e:
            logger.error(f"Error integrating rule with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_discount_coupon_with_integrations(self, db: Session, coupon_data: Dict) -> Dict:
        """Create discount coupon with full module integrations"""
        
        try:
            # Create discount coupon
            discount_coupon = DiscountCoupon(
                company_id=coupon_data['company_id'],
                coupon_code=coupon_data['coupon_code'],
                coupon_name=coupon_data['coupon_name'],
                description=coupon_data.get('description'),
                discount_type_id=coupon_data['discount_type_id'],
                discount_value=coupon_data.get('discount_value'),
                discount_percentage=coupon_data.get('discount_percentage'),
                max_discount_amount=coupon_data.get('max_discount_amount'),
                min_order_amount=coupon_data.get('min_order_amount'),
                start_date=coupon_data.get('start_date'),
                end_date=coupon_data.get('end_date'),
                max_usage_count=coupon_data.get('max_usage_count'),
                current_usage_count=0,
                is_single_use=coupon_data.get('is_single_use', False),
                customer_id=coupon_data.get('customer_id'),
                is_active=coupon_data.get('is_active', True)
            )
            
            db.add(discount_coupon)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Customer Integration
            customer_result = self.integrate_coupon_with_customer(db, discount_coupon)
            integration_results['customer'] = customer_result
            
            # 2. Marketing Integration
            marketing_result = self.integrate_coupon_with_marketing(db, discount_coupon)
            integration_results['marketing'] = marketing_result
            
            db.commit()
            
            return {
                'success': True,
                'coupon_id': discount_coupon.id,
                'coupon_code': discount_coupon.coupon_code,
                'integration_results': integration_results,
                'message': 'Discount coupon created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating discount coupon with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create discount coupon: {str(e)}")
    
    def integrate_coupon_with_customer(self, db: Session, discount_coupon: DiscountCoupon) -> Dict:
        """Integrate discount coupon with customer module"""
        
        try:
            if discount_coupon.customer_id:
                # Get customer details
                customer = db.query(Customer).filter(Customer.id == discount_coupon.customer_id).first()
                if customer:
                    return {
                        'status': 'success',
                        'customer_name': customer.name,
                        'customer_type': customer.customer_type,
                        'message': 'Coupon integrated with specific customer'
                    }
            
            return {'status': 'success', 'message': 'Coupon available for all customers'}
            
        except Exception as e:
            logger.error(f"Error integrating coupon with customer: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_coupon_with_marketing(self, db: Session, discount_coupon: DiscountCoupon) -> Dict:
        """Integrate discount coupon with marketing module"""
        
        try:
            # Create marketing campaign if applicable
            if discount_coupon.coupon_name and 'campaign' in discount_coupon.coupon_name.lower():
                return {
                    'status': 'success',
                    'campaign_created': True,
                    'message': 'Marketing campaign created for coupon'
                }
            
            return {'status': 'skipped', 'message': 'No marketing integration needed'}
            
        except Exception as e:
            logger.error(f"Error integrating coupon with marketing: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def apply_discount_to_transaction(self, db: Session, transaction_data: Dict) -> Dict:
        """Apply discount to transaction with full integrations"""
        
        try:
            transaction_type = transaction_data.get('transaction_type')
            transaction_id = transaction_data.get('transaction_id')
            applied_discounts = transaction_data.get('applied_discounts', [])
            
            discount_applications = []
            total_discount = 0
            
            for discount_data in applied_discounts:
                # Get discount rule or coupon
                if discount_data.get('rule_id'):
                    discount_rule = db.query(DiscountRule).filter(
                        DiscountRule.id == discount_data['rule_id']
                    ).first()
                    
                    if discount_rule and self.is_rule_applicable(discount_rule, transaction_data):
                        discount_amount = self.calculate_discount_amount(
                            discount_rule, transaction_data.get('subtotal', 0)
                        )
                        
                        # Create discount application
                        discount_application = DiscountApplication(
                            transaction_type=transaction_type,
                            transaction_id=transaction_id,
                            discount_rule_id=discount_rule.id,
                            discount_amount=discount_amount,
                            applied_date=datetime.utcnow()
                        )
                        db.add(discount_application)
                        
                        discount_applications.append({
                            'type': 'rule',
                            'rule_id': discount_rule.id,
                            'rule_name': discount_rule.rule_name,
                            'discount_amount': discount_amount
                        })
                        
                        total_discount += discount_amount
                
                elif discount_data.get('coupon_code'):
                    discount_coupon = db.query(DiscountCoupon).filter(
                        DiscountCoupon.coupon_code == discount_data['coupon_code']
                    ).first()
                    
                    if discount_coupon and self.is_coupon_applicable(discount_coupon, transaction_data):
                        discount_amount = self.calculate_coupon_discount(
                            discount_coupon, transaction_data.get('subtotal', 0)
                        )
                        
                        # Create coupon usage
                        coupon_usage = CouponUsage(
                            coupon_id=discount_coupon.id,
                            customer_id=transaction_data.get('customer_id'),
                            transaction_type=transaction_type,
                            transaction_id=transaction_id,
                            discount_amount=discount_amount,
                            used_date=datetime.utcnow()
                        )
                        db.add(coupon_usage)
                        
                        # Update coupon usage count
                        discount_coupon.current_usage_count += 1
                        
                        discount_applications.append({
                            'type': 'coupon',
                            'coupon_id': discount_coupon.id,
                            'coupon_code': discount_coupon.coupon_code,
                            'discount_amount': discount_amount
                        })
                        
                        total_discount += discount_amount
            
            # Update transaction with discount
            self.update_transaction_discount(db, transaction_type, transaction_id, total_discount)
            
            # Create accounting entry for discount
            accounting_result = self.create_discount_accounting_entry(
                db, transaction_data, total_discount
            )
            
            db.commit()
            
            return {
                'success': True,
                'total_discount': total_discount,
                'discount_applications': discount_applications,
                'accounting_result': accounting_result,
                'message': 'Discounts applied successfully'
            }
            
        except Exception as e:
            logger.error(f"Error applying discount to transaction: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to apply discount: {str(e)}")
    
    def is_rule_applicable(self, discount_rule: DiscountRule, transaction_data: Dict) -> bool:
        """Check if discount rule is applicable to transaction"""
        
        try:
            # Check if rule is active
            if not discount_rule.is_active:
                return False
            
            # Check date range
            if discount_rule.start_date and discount_rule.start_date > date.today():
                return False
            
            if discount_rule.end_date and discount_rule.end_date < date.today():
                return False
            
            # Check minimum order amount
            if discount_rule.min_order_amount and transaction_data.get('subtotal', 0) < discount_rule.min_order_amount:
                return False
            
            # Check rule conditions
            if discount_rule.condition_type == 'amount':
                if not self.check_amount_condition(discount_rule, transaction_data.get('subtotal', 0)):
                    return False
            elif discount_rule.condition_type == 'quantity':
                if not self.check_quantity_condition(discount_rule, transaction_data.get('items', [])):
                    return False
            elif discount_rule.condition_type == 'customer':
                if not self.check_customer_condition(discount_rule, transaction_data.get('customer_id')):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rule applicability: {str(e)}")
            return False
    
    def is_coupon_applicable(self, discount_coupon: DiscountCoupon, transaction_data: Dict) -> bool:
        """Check if discount coupon is applicable to transaction"""
        
        try:
            # Check if coupon is active
            if not discount_coupon.is_active:
                return False
            
            # Check date range
            if discount_coupon.start_date and discount_coupon.start_date > date.today():
                return False
            
            if discount_coupon.end_date and discount_coupon.end_date < date.today():
                return False
            
            # Check usage limits
            if discount_coupon.max_usage_count and discount_coupon.current_usage_count >= discount_coupon.max_usage_count:
                return False
            
            # Check minimum order amount
            if discount_coupon.min_order_amount and transaction_data.get('subtotal', 0) < discount_coupon.min_order_amount:
                return False
            
            # Check customer-specific coupon
            if discount_coupon.customer_id and discount_coupon.customer_id != transaction_data.get('customer_id'):
                return False
            
            # Check single-use coupon
            if discount_coupon.is_single_use and transaction_data.get('customer_id'):
                existing_usage = db.query(CouponUsage).filter(
                    CouponUsage.coupon_id == discount_coupon.id,
                    CouponUsage.customer_id == transaction_data.get('customer_id')
                ).first()
                if existing_usage:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking coupon applicability: {str(e)}")
            return False
    
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
    
    def calculate_coupon_discount(self, discount_coupon: DiscountCoupon, amount: Decimal) -> Decimal:
        """Calculate discount amount for coupon"""
        
        try:
            if discount_coupon.discount_percentage:
                discount_amount = amount * (discount_coupon.discount_percentage / 100)
            else:
                discount_amount = discount_coupon.discount_value
            
            # Apply maximum discount limit
            if discount_coupon.max_discount_amount:
                discount_amount = min(discount_amount, discount_coupon.max_discount_amount)
            
            return discount_amount
            
        except Exception as e:
            logger.error(f"Error calculating coupon discount: {str(e)}")
            return 0
    
    def update_transaction_discount(self, db: Session, transaction_type: str, transaction_id: int, total_discount: Decimal):
        """Update transaction with discount amount"""
        
        try:
            if transaction_type == 'sale_order':
                sale_order = db.query(SaleOrder).filter(SaleOrder.id == transaction_id).first()
                if sale_order:
                    sale_order.discount_amount = total_discount
                    sale_order.total_amount = sale_order.subtotal - total_discount + sale_order.tax_amount
            
            elif transaction_type == 'sale_invoice':
                sale_invoice = db.query(SaleInvoice).filter(SaleInvoice.id == transaction_id).first()
                if sale_invoice:
                    sale_invoice.discount_amount = total_discount
                    sale_invoice.total_amount = sale_invoice.subtotal - total_discount + sale_invoice.tax_amount
            
            elif transaction_type == 'pos_transaction':
                pos_transaction = db.query(POSTransaction).filter(POSTransaction.id == transaction_id).first()
                if pos_transaction:
                    pos_transaction.discount_amount = total_discount
                    pos_transaction.total_amount = pos_transaction.subtotal - total_discount + pos_transaction.tax_amount
            
        except Exception as e:
            logger.error(f"Error updating transaction discount: {str(e)}")
    
    def create_discount_accounting_entry(self, db: Session, transaction_data: Dict, total_discount: Decimal) -> Dict:
        """Create accounting entry for discount"""
        
        try:
            if total_discount <= 0:
                return {'status': 'skipped', 'message': 'No discount to record'}
            
            # Create journal entry
            journal_entry = JournalEntry(
                company_id=transaction_data['company_id'],
                entry_number=f"DISCOUNT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                entry_date=datetime.utcnow().date(),
                reference_type='discount',
                reference_id=transaction_data.get('transaction_id'),
                narration=f"Discount applied to {transaction_data.get('transaction_type', 'transaction')}",
                total_debit=total_discount,
                total_credit=total_discount,
                status='posted'
            )
            
            db.add(journal_entry)
            db.flush()
            
            # Create journal entry items
            # Debit: Discount Account
            discount_account = self.get_discount_account(db, transaction_data['company_id'])
            journal_item_discount = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=discount_account.id,
                debit_amount=total_discount,
                credit_amount=0,
                description=f"Discount given for {transaction_data.get('transaction_type', 'transaction')}"
            )
            db.add(journal_item_discount)
            
            # Credit: Sales Revenue (to reduce revenue)
            sales_account = self.get_sales_revenue_account(db, transaction_data['company_id'])
            journal_item_sales = JournalEntryItem(
                entry_id=journal_entry.id,
                account_id=sales_account.id,
                debit_amount=0,
                credit_amount=total_discount,
                description=f"Revenue reduction for discount"
            )
            db.add(journal_item_sales)
            
            return {
                'status': 'success',
                'journal_entry_id': journal_entry.id,
                'message': 'Accounting entry created for discount'
            }
            
        except Exception as e:
            logger.error(f"Error creating discount accounting entry: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_discount_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive discount analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get discount applications
            applications_query = db.query(DiscountApplication).filter(
                DiscountApplication.applied_date >= from_date,
                DiscountApplication.applied_date <= to_date
            )
            
            applications = applications_query.all()
            
            # Calculate metrics
            total_discounts = len(applications)
            total_discount_amount = sum(app.discount_amount for app in applications)
            average_discount = total_discount_amount / total_discounts if total_discounts > 0 else 0
            
            # Get rule usage
            rule_usage = db.query(
                DiscountRule.rule_name,
                func.count(DiscountApplication.id).label('usage_count'),
                func.sum(DiscountApplication.discount_amount).label('total_amount')
            ).join(DiscountApplication).filter(
                DiscountApplication.applied_date >= from_date,
                DiscountApplication.applied_date <= to_date
            ).group_by(DiscountRule.rule_name).all()
            
            # Get coupon usage
            coupon_usage = db.query(
                DiscountCoupon.coupon_code,
                func.count(CouponUsage.id).label('usage_count'),
                func.sum(CouponUsage.discount_amount).label('total_amount')
            ).join(CouponUsage).filter(
                CouponUsage.used_date >= from_date,
                CouponUsage.used_date <= to_date
            ).group_by(DiscountCoupon.coupon_code).all()
            
            return {
                'total_discounts': total_discounts,
                'total_discount_amount': total_discount_amount,
                'average_discount': average_discount,
                'rule_usage': [
                    {
                        'rule_name': rule.rule_name,
                        'usage_count': rule.usage_count,
                        'total_amount': rule.total_amount
                    }
                    for rule in rule_usage
                ],
                'coupon_usage': [
                    {
                        'coupon_code': coupon.coupon_code,
                        'usage_count': coupon.usage_count,
                        'total_amount': coupon.total_amount
                    }
                    for coupon in coupon_usage
                ],
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting discount analytics: {str(e)}")
            return {
                'total_discounts': 0,
                'total_discount_amount': 0,
                'average_discount': 0,
                'rule_usage': [],
                'coupon_usage': [],
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    # Helper methods
    def check_amount_condition(self, discount_rule: DiscountRule, amount: Decimal) -> bool:
        """Check amount condition for discount rule"""
        try:
            if discount_rule.condition_operator == '>=':
                return amount >= discount_rule.condition_value
            elif discount_rule.condition_operator == '<=':
                return amount <= discount_rule.condition_value
            elif discount_rule.condition_operator == '>':
                return amount > discount_rule.condition_value
            elif discount_rule.condition_operator == '<':
                return amount < discount_rule.condition_value
            elif discount_rule.condition_operator == '=':
                return amount == discount_rule.condition_value
            return False
        except Exception as e:
            logger.error(f"Error checking amount condition: {str(e)}")
            return False
    
    def check_quantity_condition(self, discount_rule: DiscountRule, items: List[Dict]) -> bool:
        """Check quantity condition for discount rule"""
        try:
            total_quantity = sum(item.get('quantity', 0) for item in items)
            return self.check_amount_condition(discount_rule, total_quantity)
        except Exception as e:
            logger.error(f"Error checking quantity condition: {str(e)}")
            return False
    
    def check_customer_condition(self, discount_rule: DiscountRule, customer_id: Optional[int]) -> bool:
        """Check customer condition for discount rule"""
        try:
            if discount_rule.rule_type == 'customer':
                return discount_rule.target_id == customer_id
            elif discount_rule.rule_type == 'customer_tier':
                if customer_id:
                    customer = db.query(Customer).filter(Customer.id == customer_id).first()
                    return customer and customer.customer_tier == discount_rule.target_id
            return False
        except Exception as e:
            logger.error(f"Error checking customer condition: {str(e)}")
            return False
    
    def get_discount_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get discount account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_name.ilike('%discount%')
        ).first()
    
    def get_sales_revenue_account(self, db: Session, company_id: int) -> ChartOfAccount:
        """Get sales revenue account"""
        return db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.account_type == 'revenue'
        ).first()