# backend/app/services/pos/pos_crm_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ...models.customers import Customer
from ...models.pos.pos_models import POSTransaction
from ...models.inventory import Item
from ...models.loyalty import LoyaltyProgram, LoyaltyTransaction
from ...models.core.discount_management import CustomerDiscount

logger = logging.getLogger(__name__)

class POSCRMService:
    """Service class for POS CRM integration"""
    
    def __init__(self):
        pass
    
    def search_customers(
        self, 
        db: Session, 
        company_id: int,
        search_term: str,
        search_type: str = "all",
        limit: int = 10
    ) -> Dict:
        """Search customers for POS"""
        
        try:
            query = db.query(Customer).filter(Customer.company_id == company_id)
            
            if search_type == "name":
                query = query.filter(Customer.name.ilike(f"%{search_term}%"))
            elif search_type == "phone":
                query = query.filter(Customer.phone.ilike(f"%{search_term}%"))
            elif search_type == "email":
                query = query.filter(Customer.email.ilike(f"%{search_term}%"))
            elif search_type == "customer_id":
                try:
                    customer_id = int(search_term)
                    query = query.filter(Customer.id == customer_id)
                except ValueError:
                    query = query.filter(Customer.id == 0)  # No results
            else:  # all
                query = query.filter(
                    or_(
                        Customer.name.ilike(f"%{search_term}%"),
                        Customer.phone.ilike(f"%{search_term}%"),
                        Customer.email.ilike(f"%{search_term}%")
                    )
                )
            
            # Get total count
            total_count = query.count()
            
            # Get customers with pagination
            customers = query.limit(limit).all()
            
            # Format customer data
            customer_list = []
            for customer in customers:
                customer_data = {
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email,
                    'customer_type': getattr(customer, 'customer_type', 'regular'),
                    'loyalty_points': self.get_customer_loyalty_points(db, customer.id),
                    'last_purchase_date': self.get_last_purchase_date(db, customer.id),
                    'total_purchases': self.get_total_purchases(db, customer.id)
                }
                customer_list.append(customer_data)
            
            return {
                'customers': customer_list,
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Error searching customers: {str(e)}")
            return {'customers': [], 'total_count': 0}
    
    def create_customer(
        self, 
        db: Session, 
        company_id: int,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        customer_type: str = "regular",
        date_of_birth: Optional[date] = None,
        anniversary_date: Optional[date] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """Create new customer from POS"""
        
        try:
            # Generate customer code
            customer_code = self.generate_customer_code(db, company_id)
            
            # Create customer
            customer = Customer(
                company_id=company_id,
                name=name,
                phone=phone,
                email=email,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                customer_type=customer_type,
                date_of_birth=date_of_birth,
                anniversary_date=anniversary_date,
                notes=notes,
                created_by=user_id
            )
            
            db.add(customer)
            db.commit()
            db.refresh(customer)
            
            # Initialize loyalty points
            loyalty_points = 0
            if customer_type in ['vip', 'premium']:
                loyalty_points = 100  # Welcome bonus
            
            # Create loyalty transaction if points > 0
            if loyalty_points > 0:
                self.create_loyalty_transaction(
                    db, customer.id, 'welcome_bonus', loyalty_points, 0
                )
            
            return {
                'customer_id': customer.id,
                'customer_code': customer_code,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'customer_type': customer.customer_type,
                'loyalty_points': loyalty_points,
                'message': f"Customer '{name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise ValueError(f"Failed to create customer: {str(e)}")
    
    def get_customer_info(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int
    ) -> Dict:
        """Get comprehensive customer information for POS"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(
                Customer.id == customer_id,
                Customer.company_id == company_id
            ).first()
            
            if not customer:
                raise ValueError("Customer not found")
            
            # Get loyalty information
            loyalty_points = self.get_customer_loyalty_points(db, customer_id)
            loyalty_tier = self.get_customer_loyalty_tier(db, customer_id)
            
            # Get purchase history
            total_purchases = self.get_total_purchases(db, customer_id)
            last_purchase_date = self.get_last_purchase_date(db, customer_id)
            
            # Get available discounts
            available_discounts = self.get_customer_available_discounts(db, customer_id)
            
            # Get loyalty benefits
            loyalty_benefits = self.get_customer_loyalty_benefits(db, customer_id)
            
            return {
                'customer_id': customer.id,
                'customer_code': getattr(customer, 'customer_code', f"CUST{customer.id:06d}"),
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address,
                'city': customer.city,
                'state': customer.state,
                'pincode': customer.pincode,
                'customer_type': getattr(customer, 'customer_type', 'regular'),
                'date_of_birth': customer.date_of_birth,
                'anniversary_date': customer.anniversary_date,
                'loyalty_points': loyalty_points,
                'total_purchases': total_purchases,
                'last_purchase_date': last_purchase_date,
                'customer_tier': loyalty_tier,
                'available_discounts': available_discounts,
                'loyalty_benefits': loyalty_benefits,
                'notes': customer.notes,
                'created_at': customer.created_at,
                'updated_at': customer.updated_at
            }
            
        except Exception as e:
            logger.error(f"Error getting customer info: {str(e)}")
            raise ValueError(f"Failed to get customer info: {str(e)}")
    
    def update_customer(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        customer_type: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        anniversary_date: Optional[date] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict:
        """Update customer information from POS"""
        
        try:
            # Get customer
            customer = db.query(Customer).filter(
                Customer.id == customer_id,
                Customer.company_id == company_id
            ).first()
            
            if not customer:
                raise ValueError("Customer not found")
            
            # Update fields
            if name is not None:
                customer.name = name
            if phone is not None:
                customer.phone = phone
            if email is not None:
                customer.email = email
            if address is not None:
                customer.address = address
            if city is not None:
                customer.city = city
            if state is not None:
                customer.state = state
            if pincode is not None:
                customer.pincode = pincode
            if customer_type is not None:
                customer.customer_type = customer_type
            if date_of_birth is not None:
                customer.date_of_birth = date_of_birth
            if anniversary_date is not None:
                customer.anniversary_date = anniversary_date
            if notes is not None:
                customer.notes = notes
            
            customer.updated_by = user_id
            customer.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(customer)
            
            # Return updated customer info
            return self.get_customer_info(db, company_id, customer_id)
            
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            raise ValueError(f"Failed to update customer: {str(e)}")
    
    def get_customer_transaction_history(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """Get customer transaction history"""
        
        try:
            # Build query
            query = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            )
            
            if from_date:
                query = query.filter(POSTransaction.transaction_date >= from_date)
            if to_date:
                query = query.filter(POSTransaction.transaction_date <= to_date)
            
            # Get total count
            total_count = query.count()
            
            # Get transactions with pagination
            transactions = query.order_by(
                desc(POSTransaction.transaction_date)
            ).offset(offset).limit(limit).all()
            
            # Format transaction data
            transaction_list = []
            for transaction in transactions:
                transaction_data = {
                    'transaction_id': transaction.id,
                    'transaction_number': transaction.transaction_number,
                    'transaction_date': transaction.transaction_date,
                    'transaction_type': transaction.transaction_type,
                    'subtotal': transaction.subtotal,
                    'discount_amount': transaction.discount_amount,
                    'tax_amount': transaction.tax_amount,
                    'total_amount': transaction.total_amount,
                    'payment_method': transaction.payment_method,
                    'status': transaction.status,
                    'items_count': len(transaction.items)
                }
                transaction_list.append(transaction_data)
            
            # Calculate summary
            total_amount = sum(t.total_amount for t in transactions)
            average_transaction = total_amount / len(transactions) if transactions else 0
            
            # Customer summary
            customer_summary = {
                'total_transactions': total_count,
                'total_spent': total_amount,
                'average_transaction': average_transaction,
                'last_purchase_date': transactions[0].transaction_date if transactions else None
            }
            
            return {
                'transactions': transaction_list,
                'total_count': total_count,
                'total_amount': total_amount,
                'average_transaction': average_transaction,
                'customer_summary': customer_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {str(e)}")
            return {
                'transactions': [],
                'total_count': 0,
                'total_amount': 0,
                'average_transaction': 0,
                'customer_summary': {}
            }
    
    def get_customer_loyalty_info(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int
    ) -> Dict:
        """Get customer loyalty information"""
        
        try:
            # Get current points
            current_points = self.get_customer_loyalty_points(db, customer_id)
            
            # Get loyalty tier
            loyalty_tier = self.get_customer_loyalty_tier(db, customer_id)
            
            # Get tier benefits
            tier_benefits = self.get_tier_benefits(db, loyalty_tier)
            
            # Get next tier information
            next_tier_info = self.get_next_tier_info(db, current_points)
            
            return {
                'customer_id': customer_id,
                'current_points': current_points,
                'points_earned': 0,  # Will be calculated during transaction
                'points_redeemed': 0,  # Will be calculated during transaction
                'loyalty_tier': loyalty_tier,
                'tier_benefits': tier_benefits,
                'next_tier_points': next_tier_info['points_needed'],
                'next_tier_name': next_tier_info['tier_name']
            }
            
        except Exception as e:
            logger.error(f"Error getting loyalty info: {str(e)}")
            return {
                'customer_id': customer_id,
                'current_points': 0,
                'points_earned': 0,
                'points_redeemed': 0,
                'loyalty_tier': 'bronze',
                'tier_benefits': {},
                'next_tier_points': 100,
                'next_tier_name': 'silver'
            }
    
    def get_customer_analytics(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get customer analytics and insights"""
        
        try:
            # Get transaction data
            query = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            )
            
            if from_date:
                query = query.filter(POSTransaction.transaction_date >= from_date)
            if to_date:
                query = query.filter(POSTransaction.transaction_date <= to_date)
            
            transactions = query.all()
            
            # Calculate metrics
            total_transactions = len(transactions)
            total_spent = sum(t.total_amount for t in transactions)
            average_transaction = total_spent / total_transactions if total_transactions > 0 else 0
            
            # Get favorite categories
            favorite_categories = self.get_favorite_categories(db, customer_id)
            
            # Get purchase frequency
            purchase_frequency = self.get_purchase_frequency(db, customer_id)
            
            # Get loyalty metrics
            loyalty_metrics = self.get_loyalty_metrics(db, customer_id)
            
            # Get recommendations
            recommendations = self.get_customer_recommendations(db, customer_id, limit=5)
            
            return {
                'customer_id': customer_id,
                'total_transactions': total_transactions,
                'total_spent': total_spent,
                'average_transaction': average_transaction,
                'favorite_categories': favorite_categories,
                'purchase_frequency': purchase_frequency,
                'loyalty_metrics': loyalty_metrics,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error getting customer analytics: {str(e)}")
            return {
                'customer_id': customer_id,
                'total_transactions': 0,
                'total_spent': 0,
                'average_transaction': 0,
                'favorite_categories': [],
                'purchase_frequency': {},
                'loyalty_metrics': {},
                'recommendations': []
            }
    
    def get_customer_benefits(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        order_amount: Decimal = 0
    ) -> Dict:
        """Get customer-specific benefits and discounts"""
        
        try:
            # Get customer discounts
            customer_discounts = db.query(CustomerDiscount).filter(
                CustomerDiscount.customer_id == customer_id,
                CustomerDiscount.is_active == True
            ).all()
            
            # Get loyalty benefits
            loyalty_benefits = self.get_customer_loyalty_benefits(db, customer_id)
            
            # Get tier benefits
            customer_tier = self.get_customer_loyalty_tier(db, customer_id)
            tier_benefits = self.get_tier_benefits(db, customer_tier)
            
            return {
                'customer_discounts': [
                    {
                        'type': 'customer_specific',
                        'name': f"Customer Discount - {discount.discount_type.name}",
                        'value': discount.discount_value,
                        'percentage': discount.discount_percentage,
                        'max_amount': discount.max_discount_amount,
                        'min_order': discount.min_order_amount
                    }
                    for discount in customer_discounts
                ],
                'loyalty_benefits': loyalty_benefits,
                'tier_benefits': tier_benefits,
                'customer_tier': customer_tier
            }
            
        except Exception as e:
            logger.error(f"Error getting customer benefits: {str(e)}")
            return {
                'customer_discounts': [],
                'loyalty_benefits': {},
                'tier_benefits': {},
                'customer_tier': 'bronze'
            }
    
    def get_customer_recommendations(
        self, 
        db: Session, 
        customer_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Get product recommendations for customer"""
        
        try:
            # Get customer's purchase history
            transactions = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            ).all()
            
            # Get frequently purchased items
            item_counts = {}
            for transaction in transactions:
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
                        'name': item.name,
                        'price': item.selling_price,
                        'purchase_count': count,
                        'recommendation_reason': 'Frequently purchased'
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def get_customer_quick_actions(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int
    ) -> List[Dict]:
        """Get quick actions available for customer"""
        
        try:
            customer = db.query(Customer).filter(
                Customer.id == customer_id,
                Customer.company_id == company_id
            ).first()
            
            if not customer:
                return []
            
            actions = []
            
            # Birthday/Anniversary actions
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
            loyalty_points = self.get_customer_loyalty_points(db, customer_id)
            if loyalty_points > 0:
                actions.append({
                    'action': 'redeem_points',
                    'title': 'Redeem Points',
                    'description': f'Redeem {loyalty_points} loyalty points',
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
            logger.error(f"Error getting quick actions: {str(e)}")
            return []
    
    def add_to_customer_favorites(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        item_id: int,
        user_id: Optional[int] = None
    ) -> Dict:
        """Add item to customer favorites"""
        
        try:
            # Check if already in favorites
            existing = db.query(ItemWishlist).filter(
                ItemWishlist.customer_id == customer_id,
                ItemWishlist.item_id == item_id
            ).first()
            
            if existing:
                return {
                    'success': False,
                    'message': 'Item already in favorites'
                }
            
            # Add to favorites
            favorite = ItemWishlist(
                customer_id=customer_id,
                item_id=item_id
            )
            
            db.add(favorite)
            db.commit()
            
            return {
                'success': True,
                'message': 'Item added to favorites successfully'
            }
            
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to add to favorites: {str(e)}'
            }
    
    def get_customer_favorites(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """Get customer favorite items"""
        
        try:
            favorites = db.query(ItemWishlist).filter(
                ItemWishlist.customer_id == customer_id
            ).limit(limit).all()
            
            favorite_items = []
            for favorite in favorites:
                item = db.query(Item).filter(Item.id == favorite.item_id).first()
                if item:
                    favorite_items.append({
                        'item_id': item.id,
                        'name': item.name,
                        'price': item.selling_price,
                        'image': getattr(item, 'image_path', None),
                        'added_date': favorite.created_at
                    })
            
            return favorite_items
            
        except Exception as e:
            logger.error(f"Error getting favorites: {str(e)}")
            return []
    
    # Helper methods
    def get_customer_loyalty_points(self, db: Session, customer_id: int) -> int:
        """Get customer's current loyalty points"""
        try:
            # Get loyalty transactions
            transactions = db.query(LoyaltyTransaction).filter(
                LoyaltyTransaction.customer_id == customer_id
            ).all()
            
            points_earned = sum(t.points_earned for t in transactions)
            points_redeemed = sum(t.points_redeemed for t in transactions)
            
            return points_earned - points_redeemed
            
        except Exception as e:
            logger.error(f"Error getting loyalty points: {str(e)}")
            return 0
    
    def get_customer_loyalty_tier(self, db: Session, customer_id: int) -> str:
        """Get customer's loyalty tier"""
        try:
            points = self.get_customer_loyalty_points(db, customer_id)
            
            if points >= 10000:
                return 'platinum'
            elif points >= 5000:
                return 'gold'
            elif points >= 1000:
                return 'silver'
            else:
                return 'bronze'
                
        except Exception as e:
            logger.error(f"Error getting loyalty tier: {str(e)}")
            return 'bronze'
    
    def get_total_purchases(self, db: Session, customer_id: int) -> Decimal:
        """Get customer's total purchase amount"""
        try:
            result = db.query(func.sum(POSTransaction.total_amount)).filter(
                POSTransaction.customer_id == customer_id
            ).scalar()
            
            return result or 0
            
        except Exception as e:
            logger.error(f"Error getting total purchases: {str(e)}")
            return 0
    
    def get_last_purchase_date(self, db: Session, customer_id: int) -> Optional[datetime]:
        """Get customer's last purchase date"""
        try:
            transaction = db.query(POSTransaction).filter(
                POSTransaction.customer_id == customer_id
            ).order_by(desc(POSTransaction.transaction_date)).first()
            
            return transaction.transaction_date if transaction else None
            
        except Exception as e:
            logger.error(f"Error getting last purchase date: {str(e)}")
            return None
    
    def generate_customer_code(self, db: Session, company_id: int) -> str:
        """Generate unique customer code"""
        try:
            # Get next customer number
            last_customer = db.query(Customer).filter(
                Customer.company_id == company_id
            ).order_by(desc(Customer.id)).first()
            
            next_number = (last_customer.id + 1) if last_customer else 1
            return f"CUST{next_number:06d}"
            
        except Exception as e:
            logger.error(f"Error generating customer code: {str(e)}")
            return f"CUST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def create_loyalty_transaction(
        self, 
        db: Session, 
        customer_id: int, 
        transaction_type: str, 
        points_earned: int, 
        points_redeemed: int
    ):
        """Create loyalty transaction"""
        try:
            transaction = LoyaltyTransaction(
                customer_id=customer_id,
                transaction_type=transaction_type,
                points_earned=points_earned,
                points_redeemed=points_redeemed,
                points_balance_before=self.get_customer_loyalty_points(db, customer_id),
                points_balance_after=self.get_customer_loyalty_points(db, customer_id) + points_earned - points_redeemed
            )
            
            db.add(transaction)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error creating loyalty transaction: {str(e)}")
    
    def get_tier_benefits(self, db: Session, tier: str) -> Dict:
        """Get tier-specific benefits"""
        benefits = {
            'bronze': {'discount_percentage': 0, 'free_shipping': False},
            'silver': {'discount_percentage': 5, 'free_shipping': True},
            'gold': {'discount_percentage': 10, 'free_shipping': True},
            'platinum': {'discount_percentage': 15, 'free_shipping': True}
        }
        
        return benefits.get(tier, benefits['bronze'])
    
    def get_next_tier_info(self, db: Session, current_points: int) -> Dict:
        """Get next tier information"""
        if current_points < 1000:
            return {'tier_name': 'silver', 'points_needed': 1000 - current_points}
        elif current_points < 5000:
            return {'tier_name': 'gold', 'points_needed': 5000 - current_points}
        elif current_points < 10000:
            return {'tier_name': 'platinum', 'points_needed': 10000 - current_points}
        else:
            return {'tier_name': 'platinum', 'points_needed': 0}
    
    def get_favorite_categories(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer's favorite categories"""
        # Implementation for favorite categories
        return []
    
    def get_purchase_frequency(self, db: Session, customer_id: int) -> Dict:
        """Get customer's purchase frequency"""
        # Implementation for purchase frequency
        return {}
    
    def get_loyalty_metrics(self, db: Session, customer_id: int) -> Dict:
        """Get loyalty metrics"""
        # Implementation for loyalty metrics
        return {}
    
    def get_customer_loyalty_benefits(self, db: Session, customer_id: int) -> Dict:
        """Get customer loyalty benefits"""
        # Implementation for loyalty benefits
        return {}
    
    def get_customer_available_discounts(self, db: Session, customer_id: int) -> List[Dict]:
        """Get customer available discounts"""
        # Implementation for available discounts
        return []