# backend/app/services/customers/customer_loyalty_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.customers import Customer
from ...models.loyalty import LoyaltyProgram, LoyaltyTransaction, LoyaltyGrade, LoyaltyReward
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.inventory import Item, ItemWishlist, ItemReview
from ...models.core.discount_management import CustomerDiscount, DiscountRule, DiscountCoupon
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.core.payment import Payment

logger = logging.getLogger(__name__)

class CustomerLoyaltyIntegrationService:
    """Service for customer and loyalty integration with all modules"""
    
    def __init__(self):
        self.customer_cache = {}
        self.loyalty_cache = {}
        self.tier_cache = {}
    
    def create_customer_with_loyalty_integration(self, db: Session, customer_data: Dict) -> Dict:
        """Create customer with full loyalty integration"""
        
        try:
            # Create customer
            customer = Customer(
                company_id=customer_data['company_id'],
                name=customer_data['name'],
                phone=customer_data.get('phone'),
                email=customer_data.get('email'),
                address=customer_data.get('address'),
                city=customer_data.get('city'),
                state=customer_data.get('state'),
                pincode=customer_data.get('pincode'),
                customer_type=customer_data.get('customer_type', 'regular'),
                date_of_birth=customer_data.get('date_of_birth'),
                anniversary_date=customer_data.get('anniversary_date'),
                notes=customer_data.get('notes')
            )
            
            db.add(customer)
            db.flush()
            
            # Integrate with loyalty system
            loyalty_result = self.integrate_customer_with_loyalty(db, customer)
            
            # Integrate with discount system
            discount_result = self.integrate_customer_with_discounts(db, customer)
            
            # Integrate with accounting
            accounting_result = self.integrate_customer_with_accounting(db, customer)
            
            db.commit()
            
            return {
                'success': True,
                'customer_id': customer.id,
                'customer_name': customer.name,
                'loyalty_integration': loyalty_result,
                'discount_integration': discount_result,
                'accounting_integration': accounting_result,
                'message': 'Customer created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating customer with loyalty integration: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create customer: {str(e)}")
    
    def integrate_customer_with_loyalty(self, db: Session, customer: Customer) -> Dict:
        """Integrate customer with loyalty system"""
        
        try:
            # Get loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == customer.company_id,
                LoyaltyProgram.is_active == True
            ).first()
            
            if not loyalty_program:
                return {'status': 'skipped', 'message': 'No loyalty program found'}
            
            # Initialize customer loyalty
            customer.loyalty_points = 0
            customer.customer_tier = 'bronze'
            
            # Create welcome bonus if applicable
            if customer.customer_type in ['vip', 'premium']:
                welcome_bonus = 100  # Welcome bonus points
                customer.loyalty_points = welcome_bonus
                
                # Create loyalty transaction
                loyalty_transaction = LoyaltyTransaction(
                    customer_id=customer.id,
                    transaction_type='earned',
                    points=welcome_bonus,
                    reference_type='welcome_bonus',
                    reference_id=customer.id,
                    description=f"Welcome bonus for {customer.customer_type} customer"
                )
                db.add(loyalty_transaction)
            
            return {
                'status': 'success',
                'loyalty_program': loyalty_program.program_name,
                'initial_points': customer.loyalty_points,
                'customer_tier': customer.customer_tier
            }
            
        except Exception as e:
            logger.error(f"Error integrating customer with loyalty: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_customer_with_discounts(self, db: Session, customer: Customer) -> Dict:
        """Integrate customer with discount system"""
        
        try:
            # Create customer-specific discounts based on tier
            customer_discounts = []
            
            if customer.customer_type == 'vip':
                # VIP customer discount
                vip_discount = CustomerDiscount(
                    customer_id=customer.id,
                    discount_type_id=1,  # Percentage discount
                    discount_value=10,  # 10% discount
                    discount_percentage=10,
                    max_discount_amount=1000,
                    min_order_amount=500,
                    is_active=True,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=365)
                )
                db.add(vip_discount)
                customer_discounts.append('VIP discount created')
            
            elif customer.customer_type == 'premium':
                # Premium customer discount
                premium_discount = CustomerDiscount(
                    customer_id=customer.id,
                    discount_type_id=1,  # Percentage discount
                    discount_value=5,  # 5% discount
                    discount_percentage=5,
                    max_discount_amount=500,
                    min_order_amount=200,
                    is_active=True,
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=365)
                )
                db.add(premium_discount)
                customer_discounts.append('Premium discount created')
            
            return {
                'status': 'success',
                'discounts_created': customer_discounts,
                'customer_type': customer.customer_type
            }
            
        except Exception as e:
            logger.error(f"Error integrating customer with discounts: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_customer_with_accounting(self, db: Session, customer: Customer) -> Dict:
        """Integrate customer with accounting system"""
        
        try:
            # Create customer account in chart of accounts
            customer_account = ChartOfAccount(
                company_id=customer.company_id,
                account_name=f"Customer - {customer.name}",
                account_code=f"CUST-{customer.id:06d}",
                account_type='asset',
                parent_account_id=None,
                is_active=True,
                description=f"Customer account for {customer.name}"
            )
            
            db.add(customer_account)
            
            return {
                'status': 'success',
                'account_created': True,
                'account_name': customer_account.account_name
            }
            
        except Exception as e:
            logger.error(f"Error integrating customer with accounting: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def process_loyalty_points_earning(self, db: Session, customer_id: int, transaction_data: Dict) -> Dict:
        """Process loyalty points earning for customer"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Get loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == customer.company_id,
                LoyaltyProgram.is_active == True
            ).first()
            
            if not loyalty_program:
                return {'status': 'skipped', 'message': 'No loyalty program found'}
            
            # Calculate points earned
            transaction_amount = transaction_data.get('total_amount', 0)
            points_earned = int(transaction_amount * loyalty_program.points_per_rupee)
            
            if points_earned > 0:
                # Get current points
                current_points = customer.loyalty_points or 0
                
                # Create loyalty transaction
                loyalty_transaction = LoyaltyTransaction(
                    customer_id=customer_id,
                    transaction_type='earned',
                    points=points_earned,
                    reference_type=transaction_data.get('transaction_type', 'sale'),
                    reference_id=transaction_data.get('transaction_id'),
                    reference_number=transaction_data.get('transaction_number'),
                    balance_before=current_points,
                    balance_after=current_points + points_earned,
                    description=f"Points earned for {transaction_data.get('transaction_type', 'sale')} {transaction_data.get('transaction_number', '')}"
                )
                
                db.add(loyalty_transaction)
                
                # Update customer points
                customer.loyalty_points = current_points + points_earned
                
                # Check for tier upgrade
                new_tier = self.calculate_customer_tier(db, customer)
                if new_tier != customer.customer_tier:
                    customer.customer_tier = new_tier
                    
                    # Create tier upgrade transaction
                    tier_upgrade_transaction = LoyaltyTransaction(
                        customer_id=customer_id,
                        transaction_type='tier_upgrade',
                        points=0,
                        reference_type='tier_upgrade',
                        reference_id=customer_id,
                        description=f"Tier upgraded to {new_tier}"
                    )
                    db.add(tier_upgrade_transaction)
                
                db.commit()
                
                return {
                    'status': 'success',
                    'points_earned': points_earned,
                    'new_balance': customer.loyalty_points,
                    'new_tier': customer.customer_tier,
                    'tier_upgraded': new_tier != customer.customer_tier
                }
            
            return {'status': 'skipped', 'message': 'No points earned'}
            
        except Exception as e:
            logger.error(f"Error processing loyalty points earning: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process loyalty points: {str(e)}")
    
    def process_loyalty_points_redemption(self, db: Session, customer_id: int, redemption_data: Dict) -> Dict:
        """Process loyalty points redemption for customer"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Check if customer has enough points
            points_to_redeem = redemption_data.get('points_to_redeem', 0)
            if customer.loyalty_points < points_to_redeem:
                raise ValueError("Insufficient loyalty points")
            
            # Get current points
            current_points = customer.loyalty_points
            
            # Create loyalty transaction
            loyalty_transaction = LoyaltyTransaction(
                customer_id=customer_id,
                transaction_type='redeemed',
                points=-points_to_redeem,
                reference_type='redemption',
                reference_id=redemption_data.get('redemption_id'),
                reference_number=redemption_data.get('redemption_number'),
                balance_before=current_points,
                balance_after=current_points - points_to_redeem,
                description=f"Points redeemed for {redemption_data.get('redemption_type', 'discount')}"
            )
            
            db.add(loyalty_transaction)
            
            # Update customer points
            customer.loyalty_points = current_points - points_to_redeem
            
            # Check for tier downgrade
            new_tier = self.calculate_customer_tier(db, customer)
            if new_tier != customer.customer_tier:
                customer.customer_tier = new_tier
                
                # Create tier downgrade transaction
                tier_downgrade_transaction = LoyaltyTransaction(
                    customer_id=customer_id,
                    transaction_type='tier_downgrade',
                    points=0,
                    reference_type='tier_downgrade',
                    reference_id=customer_id,
                    description=f"Tier downgraded to {new_tier}"
                )
                db.add(tier_downgrade_transaction)
            
            db.commit()
            
            return {
                'status': 'success',
                'points_redeemed': points_to_redeem,
                'new_balance': customer.loyalty_points,
                'new_tier': customer.customer_tier,
                'tier_downgraded': new_tier != customer.customer_tier
            }
            
        except Exception as e:
            logger.error(f"Error processing loyalty points redemption: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to process loyalty points redemption: {str(e)}")
    
    def get_customer_loyalty_benefits(self, db: Session, customer_id: int) -> Dict:
        """Get customer loyalty benefits and rewards"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Get loyalty program
            loyalty_program = db.query(LoyaltyProgram).filter(
                LoyaltyProgram.company_id == customer.company_id,
                LoyaltyProgram.is_active == True
            ).first()
            
            if not loyalty_program:
                return {'status': 'no_program', 'message': 'No loyalty program found'}
            
            # Get customer tier benefits
            tier_benefits = self.get_tier_benefits(db, customer.customer_tier)
            
            # Get available rewards
            available_rewards = self.get_available_rewards(db, customer_id)
            
            # Get loyalty history
            loyalty_history = self.get_loyalty_history(db, customer_id)
            
            # Get next tier info
            next_tier_info = self.get_next_tier_info(db, customer.loyalty_points)
            
            return {
                'customer_id': customer_id,
                'current_points': customer.loyalty_points,
                'current_tier': customer.customer_tier,
                'tier_benefits': tier_benefits,
                'available_rewards': available_rewards,
                'loyalty_history': loyalty_history,
                'next_tier': next_tier_info,
                'loyalty_program': {
                    'name': loyalty_program.program_name,
                    'points_per_rupee': loyalty_program.points_per_rupee,
                    'is_active': loyalty_program.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting customer loyalty benefits: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_tier_benefits(self, db: Session, customer_tier: str) -> Dict:
        """Get tier-specific benefits"""
        
        try:
            # Get loyalty grade
            loyalty_grade = db.query(LoyaltyGrade).filter(
                LoyaltyGrade.name == customer_tier
            ).first()
            
            if loyalty_grade:
                return {
                    'tier_name': loyalty_grade.name,
                    'discount_percentage': loyalty_grade.discount_percent,
                    'free_delivery': loyalty_grade.free_delivery,
                    'priority_support': loyalty_grade.priority_support,
                    'badge_color': loyalty_grade.badge_color,
                    'description': loyalty_grade.description
                }
            
            # Default benefits
            default_benefits = {
                'bronze': {'discount_percentage': 0, 'free_delivery': False, 'priority_support': False},
                'silver': {'discount_percentage': 5, 'free_delivery': True, 'priority_support': False},
                'gold': {'discount_percentage': 10, 'free_delivery': True, 'priority_support': True},
                'platinum': {'discount_percentage': 15, 'free_delivery': True, 'priority_support': True}
            }
            
            return default_benefits.get(customer_tier, default_benefits['bronze'])
            
        except Exception as e:
            logger.error(f"Error getting tier benefits: {str(e)}")
            return {}
    
    def get_available_rewards(self, db: Session, customer_id: int) -> List[Dict]:
        """Get available rewards for customer"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                return []
            
            # Get available rewards based on customer tier
            rewards = db.query(LoyaltyReward).filter(
                LoyaltyReward.is_active == True,
                LoyaltyReward.min_tier <= customer.customer_tier
            ).all()
            
            available_rewards = []
            for reward in rewards:
                if customer.loyalty_points >= reward.points_required:
                    available_rewards.append({
                        'reward_id': reward.id,
                        'reward_name': reward.reward_name,
                        'description': reward.description,
                        'points_required': reward.points_required,
                        'reward_type': reward.reward_type,
                        'reward_value': reward.reward_value,
                        'is_available': True
                    })
            
            return available_rewards
            
        except Exception as e:
            logger.error(f"Error getting available rewards: {str(e)}")
            return []
    
    def get_loyalty_history(self, db: Session, customer_id: int, limit: int = 20) -> List[Dict]:
        """Get customer loyalty history"""
        
        try:
            # Get loyalty transactions
            transactions = db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.customer_id == customer_id
            ).order_by(desc(LoyaltyTransaction.created_at)).limit(limit).all()
            
            history = []
            for transaction in transactions:
                history.append({
                    'transaction_id': transaction.id,
                    'transaction_type': transaction.transaction_type,
                    'points': transaction.points,
                    'balance_before': transaction.balance_before,
                    'balance_after': transaction.balance_after,
                    'reference_type': transaction.reference_type,
                    'reference_id': transaction.reference_id,
                    'description': transaction.description,
                    'created_at': transaction.created_at
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting loyalty history: {str(e)}")
            return []
    
    def get_next_tier_info(self, db: Session, current_points: int) -> Dict:
        """Get next tier information"""
        
        try:
            # Get loyalty grades
            grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from.asc()).all()
            
            for grade in grades:
                if current_points < grade.amount_from:
                    return {
                        'tier_name': grade.name,
                        'points_needed': grade.amount_from - current_points,
                        'benefits': {
                            'discount_percentage': grade.discount_percent,
                            'free_delivery': grade.free_delivery,
                            'priority_support': grade.priority_support
                        }
                    }
            
            return {'tier_name': 'platinum', 'points_needed': 0, 'benefits': {}}
            
        except Exception as e:
            logger.error(f"Error getting next tier info: {str(e)}")
            return {'tier_name': 'silver', 'points_needed': 1000, 'benefits': {}}
    
    def calculate_customer_tier(self, db: Session, customer: Customer) -> str:
        """Calculate customer tier based on loyalty points"""
        
        try:
            # Get loyalty grades
            grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from.desc()).all()
            
            current_points = customer.loyalty_points or 0
            
            for grade in grades:
                if current_points >= grade.amount_from:
                    return grade.name
            
            return 'bronze'
            
        except Exception as e:
            logger.error(f"Error calculating customer tier: {str(e)}")
            return 'bronze'
    
    def get_customer_analytics(self, db: Session, customer_id: int) -> Dict:
        """Get comprehensive customer analytics"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                raise ValueError("Customer not found")
            
            # Get sales analytics
            sales_analytics = self.get_customer_sales_analytics(db, customer_id)
            
            # Get loyalty analytics
            loyalty_analytics = self.get_customer_loyalty_analytics(db, customer_id)
            
            # Get purchase behavior
            purchase_behavior = self.get_customer_purchase_behavior(db, customer_id)
            
            # Get recommendations
            recommendations = self.get_customer_recommendations(db, customer_id)
            
            return {
                'customer_id': customer_id,
                'customer_name': customer.name,
                'customer_type': customer.customer_type,
                'customer_tier': customer.customer_tier,
                'loyalty_points': customer.loyalty_points,
                'sales_analytics': sales_analytics,
                'loyalty_analytics': loyalty_analytics,
                'purchase_behavior': purchase_behavior,
                'recommendations': recommendations,
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting customer analytics: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_customer_sales_analytics(self, db: Session, customer_id: int) -> Dict:
        """Get customer sales analytics"""
        
        try:
            # Get total sales
            total_sales = db.query(func.sum(SaleOrder.total_amount)).filter(
                SaleOrder.customer_id == customer_id
            ).scalar() or 0
            
            # Get POS sales
            pos_sales = db.query(func.sum(POSTransaction.total_amount)).filter(
                POSTransaction.customer_id == customer_id
            ).scalar() or 0
            
            # Get total transactions
            total_transactions = db.query(SaleOrder).filter(
                SaleOrder.customer_id == customer_id
            ).count()
            
            pos_transactions = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            ).count()
            
            return {
                'total_sales': total_sales,
                'pos_sales': pos_sales,
                'total_amount': total_sales + pos_sales,
                'total_transactions': total_transactions + pos_transactions,
                'average_transaction': (total_sales + pos_sales) / (total_transactions + pos_transactions) if (total_transactions + pos_transactions) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting customer sales analytics: {str(e)}")
            return {}
    
    def get_customer_loyalty_analytics(self, db: Session, customer_id: int) -> Dict:
        """Get customer loyalty analytics"""
        
        try:
            # Get loyalty transactions
            transactions = db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.customer_id == customer_id
            ).all()
            
            total_earned = sum(t.points for t in transactions if t.points > 0)
            total_redeemed = sum(abs(t.points) for t in transactions if t.points < 0)
            current_balance = total_earned - total_redeemed
            
            return {
                'total_earned': total_earned,
                'total_redeemed': total_redeemed,
                'current_balance': current_balance,
                'transaction_count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Error getting customer loyalty analytics: {str(e)}")
            return {}
    
    def get_customer_purchase_behavior(self, db: Session, customer_id: int) -> Dict:
        """Get customer purchase behavior"""
        
        try:
            # Get favorite categories
            favorite_categories = self.get_customer_favorite_categories(db, customer_id)
            
            # Get purchase frequency
            purchase_frequency = self.get_customer_purchase_frequency(db, customer_id)
            
            # Get seasonal patterns
            seasonal_patterns = self.get_customer_seasonal_patterns(db, customer_id)
            
            return {
                'favorite_categories': favorite_categories,
                'purchase_frequency': purchase_frequency,
                'seasonal_patterns': seasonal_patterns
            }
            
        except Exception as e:
            logger.error(f"Error getting customer purchase behavior: {str(e)}")
            return {}
    
    def get_customer_recommendations(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer recommendations"""
        
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
            top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get item details and recommendations
            recommendations = []
            for item_id, count in top_items:
                item = db.query(Item).filter(Item.id == item_id).first()
                if item:
                    recommendations.append({
                        'item_id': item.id,
                        'item_name': item.name,
                        'purchase_count': count,
                        'recommendation_type': 'frequently_purchased',
                        'confidence': min(100, count * 10)  # Confidence based on purchase count
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting customer recommendations: {str(e)}")
            return []
    
    def get_customer_favorite_categories(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer's favorite categories"""
        # Implementation for favorite categories
        return []
    
    def get_customer_purchase_frequency(self, db: Session, customer_id: int) -> Dict:
        """Get customer's purchase frequency"""
        # Implementation for purchase frequency
        return {}
    
    def get_customer_seasonal_patterns(self, db: Session, customer_id: int) -> Dict:
        """Get customer's seasonal patterns"""
        # Implementation for seasonal patterns
        return {}