# backend/app/services/pos/pos_discount_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ...models.pos.pos_discount_integration import (
    POSTransactionDiscount, POSCustomerDiscount, POSLoyaltyTransaction,
    POSDiscountCalculation, POSPromotion, POSPromotionUsage,
    POSDiscountAnalytics, POSDiscountConfiguration, POSDiscountAudit
)
from ...models.core.discount_management import (
    DiscountRule, DiscountCoupon, DiscountTier, CustomerDiscount,
    DiscountApplication, CouponUsage
)
from ...models.customers import Customer
from ...models.inventory import Item
from ...models.loyalty import LoyaltyProgram

logger = logging.getLogger(__name__)

class POSDiscountService:
    """Service class for POS discount calculations and management"""
    
    def __init__(self):
        self.discount_cache = {}
        self.rule_engine = DiscountRuleEngine()
    
    def calculate_transaction_discounts(
        self, 
        db: Session, 
        transaction_data: Dict,
        customer_id: Optional[int] = None,
        store_id: Optional[int] = None
    ) -> Dict:
        """Calculate all applicable discounts for a POS transaction"""
        
        try:
            # Get base transaction data
            subtotal = transaction_data.get('subtotal', 0)
            items = transaction_data.get('items', [])
            
            # Initialize discount calculation
            calculation_result = {
                'subtotal': subtotal,
                'discounts': [],
                'total_discount': 0,
                'final_amount': subtotal,
                'customer_benefits': {},
                'loyalty_points': 0
            }
            
            # 1. Get customer information and benefits
            if customer_id:
                customer_benefits = self.get_customer_benefits(db, customer_id, subtotal)
                calculation_result['customer_benefits'] = customer_benefits
                
                # Add customer-specific discounts
                if customer_benefits.get('discounts'):
                    calculation_result['discounts'].extend(customer_benefits['discounts'])
            
            # 2. Get item-based discounts
            item_discounts = self.get_item_discounts(db, items, store_id)
            calculation_result['discounts'].extend(item_discounts)
            
            # 3. Get order-level discounts
            order_discounts = self.get_order_discounts(db, subtotal, store_id)
            calculation_result['discounts'].extend(order_discounts)
            
            # 4. Get available coupons
            available_coupons = self.get_available_coupons(db, customer_id, subtotal)
            calculation_result['available_coupons'] = available_coupons
            
            # 5. Get loyalty program benefits
            if customer_id:
                loyalty_benefits = self.get_loyalty_benefits(db, customer_id, subtotal)
                calculation_result['loyalty_points'] = loyalty_benefits.get('points_earned', 0)
                if loyalty_benefits.get('discounts'):
                    calculation_result['discounts'].extend(loyalty_benefits['discounts'])
            
            # 6. Apply discount priority and calculate final amounts
            final_calculation = self.apply_discount_priority(calculation_result)
            
            # 7. Save calculation history
            self.save_discount_calculation(db, transaction_data.get('transaction_id'), final_calculation)
            
            return final_calculation
            
        except Exception as e:
            logger.error(f"Error calculating transaction discounts: {str(e)}")
            raise ValueError(f"Failed to calculate discounts: {str(e)}")
    
    def get_customer_benefits(
        self, 
        db: Session, 
        customer_id: int, 
        order_amount: Decimal
    ) -> Dict:
        """Get customer-specific benefits and discounts"""
        
        try:
            # Get customer information
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return {}
            
            benefits = {
                'customer': customer,
                'discounts': [],
                'loyalty_points': 0,
                'customer_tier': None
            }
            
            # Get customer-specific discounts
            customer_discounts = db.query(CustomerDiscount).filter(
                CustomerDiscount.customer_id == customer_id,
                CustomerDiscount.is_active == True,
                CustomerDiscount.start_date <= date.today(),
                or_(
                    CustomerDiscount.end_date.is_(None),
                    CustomerDiscount.end_date >= date.today()
                )
            ).all()
            
            for discount in customer_discounts:
                if self.check_discount_conditions(discount, order_amount):
                    benefits['discounts'].append({
                        'type': 'customer_specific',
                        'name': f"Customer Discount - {discount.discount_type.name}",
                        'value': discount.discount_value,
                        'percentage': discount.discount_percentage,
                        'max_amount': discount.max_discount_amount,
                        'min_order': discount.min_order_amount
                    })
            
            # Get customer tier and benefits
            if hasattr(customer, 'customer_tier'):
                benefits['customer_tier'] = customer.customer_tier
                
                # Get tier-specific discounts
                tier_discounts = self.get_tier_discounts(db, customer.customer_tier, order_amount)
                benefits['discounts'].extend(tier_discounts)
            
            return benefits
            
        except Exception as e:
            logger.error(f"Error getting customer benefits: {str(e)}")
            return {}
    
    def get_item_discounts(
        self, 
        db: Session, 
        items: List[Dict], 
        store_id: Optional[int] = None
    ) -> List[Dict]:
        """Get item-based discounts"""
        
        discounts = []
        
        try:
            for item in items:
                item_id = item.get('item_id')
                quantity = item.get('quantity', 0)
                unit_price = item.get('unit_price', 0)
                
                # Get item-specific discount rules
                item_rules = db.query(DiscountRule).filter(
                    DiscountRule.rule_type == 'item',
                    DiscountRule.target_id == item_id,
                    DiscountRule.is_active == True,
                    DiscountRule.start_date <= date.today(),
                    or_(
                        DiscountRule.end_date.is_(None),
                        DiscountRule.end_date >= date.today()
                    )
                ).all()
                
                for rule in item_rules:
                    if self.check_rule_conditions(rule, quantity, unit_price):
                        discount_amount = self.calculate_discount_amount(rule, quantity * unit_price)
                        if discount_amount > 0:
                            discounts.append({
                                'type': 'item_rule',
                                'rule_id': rule.id,
                                'name': rule.rule_name,
                                'item_id': item_id,
                                'value': discount_amount,
                                'percentage': rule.discount_percentage,
                                'priority': rule.priority
                            })
                
                # Get quantity-based tier discounts
                tier_discounts = self.get_quantity_tier_discounts(db, item_id, quantity)
                discounts.extend(tier_discounts)
            
            return discounts
            
        except Exception as e:
            logger.error(f"Error getting item discounts: {str(e)}")
            return []
    
    def get_order_discounts(
        self, 
        db: Session, 
        order_amount: Decimal, 
        store_id: Optional[int] = None
    ) -> List[Dict]:
        """Get order-level discounts"""
        
        discounts = []
        
        try:
            # Get order amount-based discount rules
            order_rules = db.query(DiscountRule).filter(
                DiscountRule.rule_type == 'order',
                DiscountRule.is_active == True,
                DiscountRule.start_date <= date.today(),
                or_(
                    DiscountRule.end_date.is_(None),
                    DiscountRule.end_date >= date.today()
                )
            ).all()
            
            for rule in order_rules:
                if self.check_rule_conditions(rule, order_amount):
                    discount_amount = self.calculate_discount_amount(rule, order_amount)
                    if discount_amount > 0:
                        discounts.append({
                            'type': 'order_rule',
                            'rule_id': rule.id,
                            'name': rule.rule_name,
                            'value': discount_amount,
                            'percentage': rule.discount_percentage,
                            'priority': rule.priority
                        })
            
            return discounts
            
        except Exception as e:
            logger.error(f"Error getting order discounts: {str(e)}")
            return []
    
    def get_available_coupons(
        self, 
        db: Session, 
        customer_id: Optional[int], 
        order_amount: Decimal
    ) -> List[Dict]:
        """Get available coupons for the transaction"""
        
        coupons = []
        
        try:
            # Get active coupons
            query = db.query(DiscountCoupon).filter(
                DiscountCoupon.is_active == True,
                DiscountCoupon.start_date <= date.today(),
                or_(
                    DiscountCoupon.end_date.is_(None),
                    DiscountCoupon.end_date >= date.today()
                )
            )
            
            # Filter by customer if specified
            if customer_id:
                query = query.filter(
                    or_(
                        DiscountCoupon.customer_id.is_(None),
                        DiscountCoupon.customer_id == customer_id
                    )
                )
            
            # Filter by minimum order amount
            query = query.filter(
                or_(
                    DiscountCoupon.min_order_amount.is_(None),
                    DiscountCoupon.min_order_amount <= order_amount
                )
            )
            
            active_coupons = query.all()
            
            for coupon in active_coupons:
                # Check usage limits
                if coupon.max_usage_count and coupon.current_usage_count >= coupon.max_usage_count:
                    continue
                
                # Check if single-use and already used by customer
                if coupon.is_single_use and customer_id:
                    existing_usage = db.query(CouponUsage).filter(
                        CouponUsage.coupon_id == coupon.id,
                        CouponUsage.customer_id == customer_id
                    ).first()
                    if existing_usage:
                        continue
                
                coupons.append({
                    'id': coupon.id,
                    'code': coupon.coupon_code,
                    'name': coupon.coupon_name,
                    'description': coupon.description,
                    'value': coupon.discount_value,
                    'percentage': coupon.discount_percentage,
                    'max_amount': coupon.max_discount_amount,
                    'min_order': coupon.min_order_amount,
                    'usage_count': coupon.current_usage_count,
                    'max_usage': coupon.max_usage_count
                })
            
            return coupons
            
        except Exception as e:
            logger.error(f"Error getting available coupons: {str(e)}")
            return []
    
    def get_loyalty_benefits(
        self, 
        db: Session, 
        customer_id: int, 
        order_amount: Decimal
    ) -> Dict:
        """Get loyalty program benefits"""
        
        benefits = {
            'points_earned': 0,
            'points_redeemed': 0,
            'discounts': []
        }
        
        try:
            # Get customer's loyalty program
            loyalty_program = db.query(LoyaltyProgram).join(Customer).filter(
                Customer.id == customer_id
            ).first()
            
            if not loyalty_program:
                return benefits
            
            # Calculate points earned
            points_earned = int(order_amount * loyalty_program.points_per_rupee)
            benefits['points_earned'] = points_earned
            
            # Get loyalty-based discounts
            loyalty_discounts = self.get_loyalty_discounts(db, customer_id, order_amount)
            benefits['discounts'] = loyalty_discounts
            
            return benefits
            
        except Exception as e:
            logger.error(f"Error getting loyalty benefits: {str(e)}")
            return benefits
    
    def apply_discount_priority(self, calculation_result: Dict) -> Dict:
        """Apply discount priority and calculate final amounts"""
        
        try:
            discounts = calculation_result['discounts']
            subtotal = calculation_result['subtotal']
            
            # Sort discounts by priority (higher priority first)
            discounts.sort(key=lambda x: x.get('priority', 0), reverse=True)
            
            total_discount = 0
            remaining_amount = subtotal
            
            # Apply discounts in priority order
            for discount in discounts:
                if remaining_amount <= 0:
                    break
                
                discount_amount = min(discount['value'], remaining_amount)
                
                # Apply maximum discount limit if specified
                if discount.get('max_amount'):
                    discount_amount = min(discount_amount, discount['max_amount'])
                
                if discount_amount > 0:
                    total_discount += discount_amount
                    remaining_amount -= discount_amount
                    
                    # Mark discount as applied
                    discount['applied_amount'] = discount_amount
                    discount['is_applied'] = True
                else:
                    discount['applied_amount'] = 0
                    discount['is_applied'] = False
            
            # Calculate final amount
            final_amount = subtotal - total_discount
            
            # Update calculation result
            calculation_result['total_discount'] = total_discount
            calculation_result['final_amount'] = final_amount
            calculation_result['discounts'] = discounts
            
            return calculation_result
            
        except Exception as e:
            logger.error(f"Error applying discount priority: {str(e)}")
            return calculation_result
    
    def apply_coupon(
        self, 
        db: Session, 
        transaction_id: int,
        coupon_code: str,
        customer_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """Apply coupon to transaction"""
        
        try:
            # Get coupon
            coupon = db.query(DiscountCoupon).filter(
                DiscountCoupon.coupon_code == coupon_code,
                DiscountCoupon.is_active == True
            ).first()
            
            if not coupon:
                raise ValueError("Invalid coupon code")
            
            # Check coupon validity
            if not self.validate_coupon(coupon, customer_id):
                raise ValueError("Coupon is not valid for this transaction")
            
            # Get transaction
            transaction = db.query(POSTransaction).filter(
                POSTransaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise ValueError("Transaction not found")
            
            # Calculate discount amount
            discount_amount = self.calculate_coupon_discount(coupon, transaction.subtotal)
            
            # Create discount record
            discount = POSTransactionDiscount(
                transaction_id=transaction_id,
                discount_coupon_id=coupon.id,
                discount_type='coupon',
                discount_name=coupon.coupon_name,
                discount_value=discount_amount,
                discount_percentage=coupon.discount_percentage,
                applied_amount=discount_amount,
                priority=coupon.priority or 0,
                is_automatic=False,
                applied_by=user_id
            )
            
            db.add(discount)
            
            # Update coupon usage
            coupon.current_usage_count += 1
            db.commit()
            
            # Create coupon usage record
            usage = CouponUsage(
                coupon_id=coupon.id,
                customer_id=customer_id,
                transaction_type='sale',
                transaction_id=transaction_id,
                discount_amount=discount_amount,
                used_by=user_id
            )
            
            db.add(usage)
            db.commit()
            
            return {
                'success': True,
                'discount_amount': discount_amount,
                'coupon_name': coupon.coupon_name,
                'message': f"Coupon '{coupon_code}' applied successfully"
            }
            
        except Exception as e:
            logger.error(f"Error applying coupon: {str(e)}")
            raise ValueError(f"Failed to apply coupon: {str(e)}")
    
    def validate_coupon(
        self, 
        coupon: DiscountCoupon, 
        customer_id: Optional[int] = None
    ) -> bool:
        """Validate coupon for use"""
        
        # Check date validity
        if coupon.start_date > date.today():
            return False
        
        if coupon.end_date and coupon.end_date < date.today():
            return False
        
        # Check usage limits
        if coupon.max_usage_count and coupon.current_usage_count >= coupon.max_usage_count:
            return False
        
        # Check customer-specific coupons
        if coupon.customer_id and coupon.customer_id != customer_id:
            return False
        
        return True
    
    def calculate_coupon_discount(
        self, 
        coupon: DiscountCoupon, 
        order_amount: Decimal
    ) -> Decimal:
        """Calculate discount amount for coupon"""
        
        if coupon.discount_percentage:
            discount_amount = order_amount * (coupon.discount_percentage / 100)
        else:
            discount_amount = coupon.discount_value
        
        # Apply maximum discount limit
        if coupon.max_discount_amount:
            discount_amount = min(discount_amount, coupon.max_discount_amount)
        
        return discount_amount
    
    def save_discount_calculation(
        self, 
        db: Session, 
        transaction_id: int, 
        calculation_result: Dict
    ):
        """Save discount calculation history"""
        
        try:
            calculation = POSDiscountCalculation(
                transaction_id=transaction_id,
                calculation_step='final',
                subtotal=calculation_result['subtotal'],
                discount_amount=calculation_result['total_discount'],
                final_amount=calculation_result['final_amount'],
                calculation_data=calculation_result
            )
            
            db.add(calculation)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error saving discount calculation: {str(e)}")
    
    def check_rule_conditions(
        self, 
        rule: DiscountRule, 
        value: Decimal, 
        additional_value: Optional[Decimal] = None
    ) -> bool:
        """Check if rule conditions are met"""
        
        try:
            if rule.condition_type == 'quantity':
                return self.compare_values(value, rule.condition_value, rule.condition_operator)
            elif rule.condition_type == 'amount':
                return self.compare_values(value, rule.condition_value, rule.condition_operator)
            elif rule.condition_type == 'date':
                return rule.start_date <= date.today() and (not rule.end_date or rule.end_date >= date.today())
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {str(e)}")
            return False
    
    def compare_values(self, value1: Decimal, value2: Decimal, operator: str) -> bool:
        """Compare two values with given operator"""
        
        if operator == '>=':
            return value1 >= value2
        elif operator == '<=':
            return value1 <= value2
        elif operator == '>':
            return value1 > value2
        elif operator == '<':
            return value1 < value2
        elif operator == '=':
            return value1 == value2
        else:
            return False
    
    def calculate_discount_amount(self, rule: DiscountRule, amount: Decimal) -> Decimal:
        """Calculate discount amount for rule"""
        
        if rule.discount_percentage:
            discount_amount = amount * (rule.discount_percentage / 100)
        else:
            discount_amount = rule.discount_value
        
        # Apply maximum discount limit
        if rule.max_discount_amount:
            discount_amount = min(discount_amount, rule.max_discount_amount)
        
        return discount_amount

class DiscountRuleEngine:
    """Advanced discount rule engine"""
    
    def __init__(self):
        self.rule_cache = {}
    
    def evaluate_rules(self, transaction_data: Dict) -> List[Dict]:
        """Evaluate all applicable rules"""
        # Implementation for complex rule evaluation
        pass