# backend/app/services/customers/customer_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.customers import Customer
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.loyalty import LoyaltyProgram, LoyaltyTransaction, LoyaltyGrade
from ...models.core.discount_management import CustomerDiscount, DiscountRule
from ...models.inventory import Item, ItemWishlist, ItemReview
from ...models.accounting import ChartOfAccount, AccountBalance

logger = logging.getLogger(__name__)

class CustomerIntegrationService:
    """Service for customer integration with all modules"""
    
    def __init__(self):
        self.customer_cache = {}
        self.loyalty_cache = {}
    
    def get_customer_sales_history(self, db: Session, customer_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get customer sales history and analytics"""
        
        try:
            # Get sales orders
            sales_query = db.query(SaleOrder).filter(SaleOrder.customer_id == customer_id)
            if from_date:
                sales_query = sales_query.filter(SaleOrder.order_date >= from_date)
            if to_date:
                sales_query = sales_query.filter(SaleOrder.order_date <= to_date)
            
            sales_orders = sales_query.all()
            
            # Get POS transactions
            pos_query = db.query(POSTransaction).filter(POSTransaction.customer_id == customer_id)
            if from_date:
                pos_query = pos_query.filter(POSTransaction.transaction_date >= from_date)
            if to_date:
                pos_query = pos_query.filter(POSTransaction.transaction_date <= to_date)
            
            pos_transactions = pos_query.all()
            
            # Calculate totals
            total_sales_amount = sum(order.total_amount for order in sales_orders)
            total_pos_amount = sum(transaction.total_amount for transaction in pos_transactions)
            total_amount = total_sales_amount + total_pos_amount
            
            total_sales_count = len(sales_orders)
            total_pos_count = len(pos_transactions)
            total_transactions = total_sales_count + total_pos_count
            
            # Calculate average transaction
            average_transaction = total_amount / total_transactions if total_transactions > 0 else 0
            
            # Get last purchase date
            last_purchase_date = None
            if sales_orders:
                last_sales_date = max(order.order_date for order in sales_orders)
                last_purchase_date = last_sales_date
            if pos_transactions:
                last_pos_date = max(transaction.transaction_date for transaction in pos_transactions)
                if not last_purchase_date or last_pos_date > last_purchase_date:
                    last_purchase_date = last_pos_date
            
            return {
                'customer_id': customer_id,
                'total_sales_amount': total_sales_amount,
                'total_pos_amount': total_pos_amount,
                'total_amount': total_amount,
                'total_sales_count': total_sales_count,
                'total_pos_count': total_pos_count,
                'total_transactions': total_transactions,
                'average_transaction': average_transaction,
                'last_purchase_date': last_purchase_date,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting customer sales history: {str(e)}")
            return {
                'customer_id': customer_id,
                'total_sales_amount': 0,
                'total_pos_amount': 0,
                'total_amount': 0,
                'total_sales_count': 0,
                'total_pos_count': 0,
                'total_transactions': 0,
                'average_transaction': 0,
                'last_purchase_date': None,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def get_customer_loyalty_info(self, db: Session, customer_id: int) -> Dict:
        """Get customer loyalty information and benefits"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Get loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == customer.company_id
            ).first()
            
            if not loyalty_program:
                return {
                    'customer_id': customer_id,
                    'loyalty_enabled': False,
                    'message': 'No loyalty program found'
                }
            
            # Get loyalty transactions
            loyalty_transactions = db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.customer_id == customer_id
            ).all()
            
            # Calculate points
            total_points_earned = sum(t.points for t in loyalty_transactions if t.points > 0)
            total_points_redeemed = sum(abs(t.points) for t in loyalty_transactions if t.points < 0)
            current_points = total_points_earned - total_points_redeemed
            
            # Get loyalty grade
            loyalty_grade = self.get_customer_loyalty_grade(db, customer_id, current_points)
            
            # Get tier benefits
            tier_benefits = self.get_tier_benefits(db, loyalty_grade)
            
            # Get next tier info
            next_tier_info = self.get_next_tier_info(db, current_points)
            
            return {
                'customer_id': customer_id,
                'loyalty_enabled': True,
                'current_points': current_points,
                'points_earned': total_points_earned,
                'points_redeemed': total_points_redeemed,
                'loyalty_grade': loyalty_grade,
                'tier_benefits': tier_benefits,
                'next_tier': next_tier_info,
                'loyalty_program': {
                    'name': loyalty_program.program_name,
                    'points_per_rupee': loyalty_program.points_per_rupee,
                    'is_active': loyalty_program.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting customer loyalty info: {str(e)}")
            return {
                'customer_id': customer_id,
                'loyalty_enabled': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_customer_discounts(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer-specific discounts and benefits"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return []
            
            discounts = []
            
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
                discounts.append({
                    'type': 'customer_specific',
                    'name': f"Customer Discount - {discount.discount_type.name}",
                    'value': discount.discount_value,
                    'percentage': discount.discount_percentage,
                    'max_amount': discount.max_discount_amount,
                    'min_order': discount.min_order_amount,
                    'start_date': discount.start_date,
                    'end_date': discount.end_date
                })
            
            # Get tier-based discounts
            loyalty_grade = self.get_customer_loyalty_grade(db, customer_id, 0)
            tier_discounts = self.get_tier_discounts(db, loyalty_grade)
            discounts.extend(tier_discounts)
            
            return discounts
            
        except Exception as e:
            logger.error(f"Error getting customer discounts: {str(e)}")
            return []
    
    def get_customer_favorite_items(self, db: Session, customer_id: int, limit: int = 10) -> List[Dict]:
        """Get customer favorite items"""
        
        try:
            # Get customer wishlist
            wishlist_items = db.query(ItemWishlist).filter(
                ItemWishlist.customer_id == customer_id
            ).limit(limit).all()
            
            favorite_items = []
            for wishlist_item in wishlist_items:
                item = db.query(Item).filter(Item.id == wishlist_item.item_id).first()
                if item:
                    favorite_items.append({
                        'item_id': item.id,
                        'item_name': item.name,
                        'item_code': item.item_code,
                        'price': item.selling_price,
                        'image': getattr(item, 'image_path', None),
                        'added_date': wishlist_item.created_at
                    })
            
            return favorite_items
            
        except Exception as e:
            logger.error(f"Error getting customer favorite items: {str(e)}")
            return []
    
    def get_customer_purchase_analytics(self, db: Session, customer_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get customer purchase analytics and insights"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=365)  # Last year
            if not to_date:
                to_date = date.today()
            
            # Get sales data
            sales_orders = db.query(SaleOrder).filter(
                SaleOrder.customer_id == customer_id,
                SaleOrder.order_date >= from_date,
                SaleOrder.order_date <= to_date
            ).all()
            
            # Get POS data
            pos_transactions = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id,
                POSTransaction.transaction_date >= from_date,
                POSTransaction.transaction_date <= to_date
            ).all()
            
            # Calculate metrics
            total_purchases = len(sales_orders) + len(pos_transactions)
            total_amount = sum(order.total_amount for order in sales_orders) + sum(transaction.total_amount for transaction in pos_transactions)
            average_purchase = total_amount / total_purchases if total_purchases > 0 else 0
            
            # Get favorite categories
            favorite_categories = self.get_customer_favorite_categories(db, customer_id)
            
            # Get purchase frequency
            purchase_frequency = self.get_customer_purchase_frequency(db, customer_id, from_date, to_date)
            
            # Get loyalty metrics
            loyalty_metrics = self.get_customer_loyalty_metrics(db, customer_id)
            
            return {
                'customer_id': customer_id,
                'total_purchases': total_purchases,
                'total_amount': total_amount,
                'average_purchase': average_purchase,
                'favorite_categories': favorite_categories,
                'purchase_frequency': purchase_frequency,
                'loyalty_metrics': loyalty_metrics,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting customer purchase analytics: {str(e)}")
            return {
                'customer_id': customer_id,
                'total_purchases': 0,
                'total_amount': 0,
                'average_purchase': 0,
                'favorite_categories': [],
                'purchase_frequency': {},
                'loyalty_metrics': {},
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
    
    def update_customer_loyalty_points(self, db: Session, customer_id: int, points: int, transaction_type: str, reference_id: Optional[int] = None) -> Dict:
        """Update customer loyalty points"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Get current points
            current_points = self.get_customer_current_points(db, customer_id)
            
            # Create loyalty transaction
            loyalty_transaction = LoyaltyTransaction(
                customer_id=customer_id,
                transaction_type=transaction_type,
                points=points,
                reference_type='sale',
                reference_id=reference_id,
                balance_before=current_points,
                balance_after=current_points + points,
                description=f"Points {transaction_type} for transaction {reference_id}"
            )
            
            db.add(loyalty_transaction)
            db.commit()
            
            return {
                'success': True,
                'customer_id': customer_id,
                'points_added': points,
                'new_balance': current_points + points,
                'message': f'Loyalty points updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating customer loyalty points: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to update loyalty points: {str(e)}")
    
    def get_customer_recommendations(self, db: Session, customer_id: int, limit: int = 10) -> List[Dict]:
        """Get product recommendations for customer"""
        
        try:
            # Get customer's purchase history
            customer_transactions = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            ).all()
            
            # Get frequently purchased items
            item_counts = {}
            for transaction in customer_transactions:
                for item in transaction.items:
                    item_id = item.item_id
                    item_counts[item_id] = item_counts.get(item_id, 0) + item.quantity
            
            # Get top items
            top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            
            # Get item details
            recommendations = []
            for item_id, count in top_items:
                item = db.query(Item).filter(Item.id == item_id).first()
                if item:
                    recommendations.append({
                        'item_id': item.id,
                        'item_name': item.name,
                        'item_code': item.item_code,
                        'price': item.selling_price,
                        'purchase_count': count,
                        'recommendation_reason': 'Frequently purchased',
                        'image': getattr(item, 'image_path', None)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting customer recommendations: {str(e)}")
            return []
    
    def get_customer_quick_actions(self, db: Session, customer_id: int) -> List[Dict]:
        """Get quick actions available for customer"""
        
        try:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return []
            
            actions = []
            
            # Birthday action
            if customer.date_of_birth:
                today = date.today()
                if (customer.date_of_birth.month == today.month and 
                    customer.date_of_birth.day == today.day):
                    actions.append({
                        'action': 'birthday_discount',
                        'title': 'Birthday Special',
                        'description': 'Apply birthday discount',
                        'icon': 'cake',
                        'color': 'green'
                    })
            
            # Anniversary action
            if customer.anniversary_date:
                today = date.today()
                if (customer.anniversary_date.month == today.month and 
                    customer.anniversary_date.day == today.day):
                    actions.append({
                        'action': 'anniversary_discount',
                        'title': 'Anniversary Special',
                        'description': 'Apply anniversary discount',
                        'icon': 'heart',
                        'color': 'red'
                    })
            
            # Loyalty actions
            current_points = self.get_customer_current_points(db, customer_id)
            if current_points > 0:
                actions.append({
                    'action': 'redeem_points',
                    'title': 'Redeem Points',
                    'description': f'Redeem {current_points} loyalty points',
                    'icon': 'star',
                    'color': 'blue'
                })
            
            # VIP actions
            if getattr(customer, 'customer_type', 'regular') in ['vip', 'premium']:
                actions.append({
                    'action': 'vip_discount',
                    'title': 'VIP Discount',
                    'description': 'Apply VIP customer discount',
                    'icon': 'crown',
                    'color': 'gold'
                })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting customer quick actions: {str(e)}")
            return []
    
    # Helper methods
    def get_customer_loyalty_grade(self, db: Session, customer_id: int, current_points: int) -> str:
        """Get customer loyalty grade based on points"""
        try:
            # Get loyalty grades
            grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from.desc()).all()
            
            for grade in grades:
                if current_points >= grade.amount_from:
                    return grade.name
            
            return 'bronze'
        except Exception as e:
            logger.error(f"Error getting customer loyalty grade: {str(e)}")
            return 'bronze'
    
    def get_tier_benefits(self, db: Session, loyalty_grade: str) -> Dict:
        """Get tier benefits for loyalty grade"""
        try:
            grade = db.query(LoyaltyGrade).filter(LoyaltyGrade.name == loyalty_grade).first()
            if grade:
                return {
                    'discount_percent': grade.discount_percent,
                    'free_delivery': grade.free_delivery,
                    'priority_support': grade.priority_support,
                    'badge_color': grade.badge_color,
                    'description': grade.description
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting tier benefits: {str(e)}")
            return {}
    
    def get_next_tier_info(self, db: Session, current_points: int) -> Dict:
        """Get next tier information"""
        try:
            grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from.asc()).all()
            
            for grade in grades:
                if current_points < grade.amount_from:
                    return {
                        'tier_name': grade.name,
                        'points_needed': grade.amount_from - current_points,
                        'benefits': {
                            'discount_percent': grade.discount_percent,
                            'free_delivery': grade.free_delivery,
                            'priority_support': grade.priority_support
                        }
                    }
            
            return {'tier_name': 'platinum', 'points_needed': 0, 'benefits': {}}
        except Exception as e:
            logger.error(f"Error getting next tier info: {str(e)}")
            return {'tier_name': 'silver', 'points_needed': 1000, 'benefits': {}}
    
    def get_tier_discounts(self, db: Session, loyalty_grade: str) -> List[Dict]:
        """Get tier-based discounts"""
        try:
            grade = db.query(LoyaltyGrade).filter(LoyaltyGrade.name == loyalty_grade).first()
            if grade and grade.discount_percent > 0:
                return [{
                    'type': 'tier_discount',
                    'name': f"{loyalty_grade.title()} Tier Discount",
                    'percentage': grade.discount_percent,
                    'tier': loyalty_grade
                }]
            return []
        except Exception as e:
            logger.error(f"Error getting tier discounts: {str(e)}")
            return []
    
    def get_customer_current_points(self, db: Session, customer_id: int) -> int:
        """Get customer's current loyalty points"""
        try:
            transactions = db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.customer_id == customer_id
            ).all()
            
            total_earned = sum(t.points for t in transactions if t.points > 0)
            total_redeemed = sum(abs(t.points) for t in transactions if t.points < 0)
            
            return total_earned - total_redeemed
        except Exception as e:
            logger.error(f"Error getting customer current points: {str(e)}")
            return 0
    
    def get_customer_favorite_categories(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer's favorite categories"""
        # Implementation for favorite categories
        return []
    
    def get_customer_purchase_frequency(self, db: Session, customer_id: int, from_date: date, to_date: date) -> Dict:
        """Get customer's purchase frequency"""
        # Implementation for purchase frequency
        return {}
    
    def get_customer_loyalty_metrics(self, db: Session, customer_id: int) -> Dict:
        """Get customer loyalty metrics"""
        # Implementation for loyalty metrics
        return {}