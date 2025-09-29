# backend/app/services/discount_management_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging
import uuid

from ..models.core import (
    DiscountType, DiscountRule, DiscountApplication, DiscountCoupon, CouponUsage,
    DiscountTier, TierApplication, CustomerDiscount, DiscountAnalytics,
    DiscountReport, DiscountConfiguration, DiscountValidation, DiscountAudit
)
from ..models.inventory import Item
from ..models.customers import Customer

logger = logging.getLogger(__name__)

class DiscountManagementService:
    """Service class for discount management"""
    
    def __init__(self):
        pass
    
    # Discount Type Management
    def create_discount_type(
        self, 
        db: Session, 
        company_id: int,
        type_name: str,
        type_code: str,
        calculation_method: str,
        description: str = None,
        is_default: bool = False,
        notes: str = None,
        user_id: int = None
    ) -> DiscountType:
        """Create discount type"""
        
        # Check if type code already exists
        existing_type = db.query(DiscountType).filter(
            DiscountType.company_id == company_id,
            DiscountType.type_code == type_code
        ).first()
        
        if existing_type:
            raise ValueError(f"Discount type code {type_code} already exists")
        
        # If setting as default, unset other default types
        if is_default:
            db.query(DiscountType).filter(
                DiscountType.company_id == company_id,
                DiscountType.is_default == True
            ).update({"is_default": False})
        
        # Create discount type
        discount_type = DiscountType(
            company_id=company_id,
            type_name=type_name,
            type_code=type_code,
            calculation_method=calculation_method,
            description=description,
            is_default=is_default,
            notes=notes,
            created_by=user_id
        )
        
        db.add(discount_type)
        db.commit()
        db.refresh(discount_type)
        
        logger.info(f"Discount type created: {type_name}")
        
        return discount_type
    
    def get_discount_types(
        self, 
        db: Session, 
        company_id: int,
        is_active: Optional[bool] = None
    ) -> List[DiscountType]:
        """Get discount types"""
        
        query = db.query(DiscountType).filter(DiscountType.company_id == company_id)
        
        if is_active is not None:
            query = query.filter(DiscountType.is_active == is_active)
        
        types = query.order_by(DiscountType.type_name).all()
        
        return types
    
    # Discount Rule Management
    def create_discount_rule(
        self, 
        db: Session, 
        company_id: int,
        rule_name: str,
        rule_code: str,
        discount_type_id: int,
        rule_type: str,
        target_type: str = None,
        target_id: int = None,
        condition_type: str = 'quantity',
        condition_value: Decimal = None,
        condition_operator: str = '>=',
        discount_value: Decimal = 0,
        discount_percentage: Decimal = None,
        max_discount_amount: Decimal = None,
        min_order_amount: Decimal = None,
        start_date: date = None,
        end_date: date = None,
        priority: int = 0,
        is_automatic: bool = False,
        notes: str = None,
        user_id: int = None
    ) -> DiscountRule:
        """Create discount rule"""
        
        # Check if rule code already exists
        existing_rule = db.query(DiscountRule).filter(
            DiscountRule.company_id == company_id,
            DiscountRule.rule_code == rule_code
        ).first()
        
        if existing_rule:
            raise ValueError(f"Discount rule code {rule_code} already exists")
        
        # Validate discount type
        discount_type = db.query(DiscountType).filter(
            DiscountType.id == discount_type_id,
            DiscountType.company_id == company_id
        ).first()
        
        if not discount_type:
            raise ValueError("Discount type not found")
        
        # Create discount rule
        rule = DiscountRule(
            company_id=company_id,
            rule_name=rule_name,
            rule_code=rule_code,
            discount_type_id=discount_type_id,
            rule_type=rule_type,
            target_type=target_type,
            target_id=target_id,
            condition_type=condition_type,
            condition_value=condition_value,
            condition_operator=condition_operator,
            discount_value=discount_value,
            discount_percentage=discount_percentage,
            max_discount_amount=max_discount_amount,
            min_order_amount=min_order_amount,
            start_date=start_date or date.today(),
            end_date=end_date,
            priority=priority,
            is_automatic=is_automatic,
            notes=notes,
            created_by=user_id
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Discount rule created: {rule_name}")
        
        return rule
    
    def get_discount_rules(
        self, 
        db: Session, 
        company_id: int,
        rule_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[DiscountRule]:
        """Get discount rules"""
        
        query = db.query(DiscountRule).filter(DiscountRule.company_id == company_id)
        
        if rule_type:
            query = query.filter(DiscountRule.rule_type == rule_type)
        
        if is_active is not None:
            query = query.filter(DiscountRule.is_active == is_active)
        
        rules = query.order_by(DiscountRule.priority.desc(), DiscountRule.rule_name).all()
        
        return rules
    
    def apply_discount_rule(
        self, 
        db: Session, 
        company_id: int,
        rule_id: int,
        transaction_type: str,
        transaction_id: int,
        item_id: int = None,
        customer_id: int = None,
        original_amount: Decimal = 0,
        quantity: Decimal = 1,
        user_id: int = None
    ) -> DiscountApplication:
        """Apply discount rule"""
        
        rule = db.query(DiscountRule).filter(
            DiscountRule.id == rule_id,
            DiscountRule.company_id == company_id,
            DiscountRule.is_active == True
        ).first()
        
        if not rule:
            raise ValueError("Discount rule not found")
        
        # Check if rule is valid for current date
        today = date.today()
        if rule.start_date > today or (rule.end_date and rule.end_date < today):
            raise ValueError("Discount rule is not valid for current date")
        
        # Check conditions
        if not self._check_rule_conditions(rule, quantity, original_amount, customer_id):
            raise ValueError("Discount rule conditions not met")
        
        # Calculate discount
        discount_amount = self._calculate_discount_amount(
            rule, original_amount, quantity
        )
        
        # Apply maximum discount limit
        if rule.max_discount_amount and discount_amount > rule.max_discount_amount:
            discount_amount = rule.max_discount_amount
        
        final_amount = original_amount - discount_amount
        
        # Create discount application
        application = DiscountApplication(
            company_id=company_id,
            rule_id=rule_id,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            item_id=item_id,
            customer_id=customer_id,
            original_amount=original_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            applied_by=user_id,
            created_by=user_id
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        logger.info(f"Discount rule applied: {rule.rule_name}, amount: {discount_amount}")
        
        return application
    
    def _check_rule_conditions(
        self, 
        rule: DiscountRule, 
        quantity: Decimal, 
        amount: Decimal, 
        customer_id: int = None
    ) -> bool:
        """Check if rule conditions are met"""
        
        # Check minimum order amount
        if rule.min_order_amount and amount < rule.min_order_amount:
            return False
        
        # Check condition value
        if rule.condition_value:
            if rule.condition_type == 'quantity':
                condition_value = quantity
            elif rule.condition_type == 'amount':
                condition_value = amount
            else:
                condition_value = 0
            
            if rule.condition_operator == '>=':
                if condition_value < rule.condition_value:
                    return False
            elif rule.condition_operator == '<=':
                if condition_value > rule.condition_value:
                    return False
            elif rule.condition_operator == '=':
                if condition_value != rule.condition_value:
                    return False
            elif rule.condition_operator == '>':
                if condition_value <= rule.condition_value:
                    return False
            elif rule.condition_operator == '<':
                if condition_value >= rule.condition_value:
                    return False
        
        return True
    
    def _calculate_discount_amount(
        self, 
        rule: DiscountRule, 
        amount: Decimal, 
        quantity: Decimal
    ) -> Decimal:
        """Calculate discount amount"""
        
        if rule.discount_percentage:
            discount_amount = (amount * rule.discount_percentage / 100)
        else:
            discount_amount = rule.discount_value
        
        return discount_amount
    
    # Discount Coupon Management
    def create_discount_coupon(
        self, 
        db: Session, 
        company_id: int,
        coupon_code: str,
        coupon_name: str,
        discount_type_id: int,
        discount_value: Decimal = 0,
        discount_percentage: Decimal = None,
        max_discount_amount: Decimal = None,
        min_order_amount: Decimal = None,
        max_usage_count: int = None,
        start_date: date = None,
        end_date: date = None,
        is_single_use: bool = False,
        customer_id: int = None,
        notes: str = None,
        user_id: int = None
    ) -> DiscountCoupon:
        """Create discount coupon"""
        
        # Check if coupon code already exists
        existing_coupon = db.query(DiscountCoupon).filter(
            DiscountCoupon.company_id == company_id,
            DiscountCoupon.coupon_code == coupon_code
        ).first()
        
        if existing_coupon:
            raise ValueError(f"Coupon code {coupon_code} already exists")
        
        # Validate discount type
        discount_type = db.query(DiscountType).filter(
            DiscountType.id == discount_type_id,
            DiscountType.company_id == company_id
        ).first()
        
        if not discount_type:
            raise ValueError("Discount type not found")
        
        # Create discount coupon
        coupon = DiscountCoupon(
            company_id=company_id,
            coupon_code=coupon_code,
            coupon_name=coupon_name,
            discount_type_id=discount_type_id,
            discount_value=discount_value,
            discount_percentage=discount_percentage,
            max_discount_amount=max_discount_amount,
            min_order_amount=min_order_amount,
            max_usage_count=max_usage_count,
            start_date=start_date or date.today(),
            end_date=end_date,
            is_single_use=is_single_use,
            customer_id=customer_id,
            notes=notes,
            created_by=user_id
        )
        
        db.add(coupon)
        db.commit()
        db.refresh(coupon)
        
        logger.info(f"Discount coupon created: {coupon_code}")
        
        return coupon
    
    def apply_discount_coupon(
        self, 
        db: Session, 
        company_id: int,
        coupon_code: str,
        customer_id: int,
        transaction_type: str,
        transaction_id: int,
        order_amount: Decimal = 0,
        user_id: int = None
    ) -> CouponUsage:
        """Apply discount coupon"""
        
        coupon = db.query(DiscountCoupon).filter(
            DiscountCoupon.coupon_code == coupon_code,
            DiscountCoupon.company_id == company_id,
            DiscountCoupon.is_active == True
        ).first()
        
        if not coupon:
            raise ValueError("Invalid coupon code")
        
        # Check if coupon is valid for current date
        today = date.today()
        if coupon.start_date > today or (coupon.end_date and coupon.end_date < today):
            raise ValueError("Coupon has expired")
        
        # Check if coupon is for specific customer
        if coupon.customer_id and coupon.customer_id != customer_id:
            raise ValueError("Coupon is not valid for this customer")
        
        # Check minimum order amount
        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            raise ValueError(f"Minimum order amount of {coupon.min_order_amount} required")
        
        # Check usage limits
        if coupon.max_usage_count and coupon.current_usage_count >= coupon.max_usage_count:
            raise ValueError("Coupon usage limit exceeded")
        
        # Check if customer has already used this coupon (for single use)
        if coupon.is_single_use:
            existing_usage = db.query(CouponUsage).filter(
                CouponUsage.coupon_id == coupon.id,
                CouponUsage.customer_id == customer_id
            ).first()
            
            if existing_usage:
                raise ValueError("Coupon has already been used")
        
        # Calculate discount amount
        if coupon.discount_percentage:
            discount_amount = (order_amount * coupon.discount_percentage / 100)
        else:
            discount_amount = coupon.discount_value
        
        # Apply maximum discount limit
        if coupon.max_discount_amount and discount_amount > coupon.max_discount_amount:
            discount_amount = coupon.max_discount_amount
        
        # Create coupon usage
        usage = CouponUsage(
            company_id=company_id,
            coupon_id=coupon.id,
            customer_id=customer_id,
            transaction_type=transaction_type,
            transaction_id=transaction_id,
            discount_amount=discount_amount,
            used_by=user_id,
            created_by=user_id
        )
        
        db.add(usage)
        
        # Update coupon usage count
        coupon.current_usage_count += 1
        
        db.commit()
        db.refresh(usage)
        
        logger.info(f"Discount coupon applied: {coupon_code}, amount: {discount_amount}")
        
        return usage
    
    # Discount Tier Management
    def create_discount_tier(
        self, 
        db: Session, 
        company_id: int,
        tier_name: str,
        tier_code: str,
        min_quantity: Decimal,
        max_quantity: Decimal = None,
        discount_percentage: Decimal = None,
        discount_amount: Decimal = None,
        display_order: int = 0,
        notes: str = None,
        user_id: int = None
    ) -> DiscountTier:
        """Create discount tier"""
        
        # Check if tier code already exists
        existing_tier = db.query(DiscountTier).filter(
            DiscountTier.company_id == company_id,
            DiscountTier.tier_code == tier_code
        ).first()
        
        if existing_tier:
            raise ValueError(f"Discount tier code {tier_code} already exists")
        
        # Create discount tier
        tier = DiscountTier(
            company_id=company_id,
            tier_name=tier_name,
            tier_code=tier_code,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            display_order=display_order,
            notes=notes,
            created_by=user_id
        )
        
        db.add(tier)
        db.commit()
        db.refresh(tier)
        
        logger.info(f"Discount tier created: {tier_name}")
        
        return tier
    
    def apply_discount_tier(
        self, 
        db: Session, 
        company_id: int,
        item_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        customer_id: int = None,
        user_id: int = None
    ) -> TierApplication:
        """Apply discount tier"""
        
        # Find applicable tier
        tier = db.query(DiscountTier).filter(
            DiscountTier.company_id == company_id,
            DiscountTier.is_active == True,
            DiscountTier.min_quantity <= quantity,
            or_(
                DiscountTier.max_quantity.is_(None),
                DiscountTier.max_quantity >= quantity
            )
        ).order_by(DiscountTier.min_quantity.desc()).first()
        
        if not tier:
            raise ValueError("No applicable discount tier found")
        
        original_amount = quantity * unit_price
        
        # Calculate discount
        if tier.discount_percentage:
            discount_amount = (original_amount * tier.discount_percentage / 100)
        else:
            discount_amount = tier.discount_amount or 0
        
        final_amount = original_amount - discount_amount
        
        # Create tier application
        application = TierApplication(
            company_id=company_id,
            tier_id=tier.id,
            item_id=item_id,
            customer_id=customer_id,
            quantity=quantity,
            unit_price=unit_price,
            original_amount=original_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            applied_by=user_id,
            created_by=user_id
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        logger.info(f"Discount tier applied: {tier.tier_name}, amount: {discount_amount}")
        
        return application
    
    # Customer Discount Management
    def create_customer_discount(
        self, 
        db: Session, 
        company_id: int,
        customer_id: int,
        discount_type_id: int,
        discount_value: Decimal = 0,
        discount_percentage: Decimal = None,
        max_discount_amount: Decimal = None,
        min_order_amount: Decimal = None,
        start_date: date = None,
        end_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> CustomerDiscount:
        """Create customer-specific discount"""
        
        # Validate customer
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise ValueError("Customer not found")
        
        # Validate discount type
        discount_type = db.query(DiscountType).filter(
            DiscountType.id == discount_type_id,
            DiscountType.company_id == company_id
        ).first()
        
        if not discount_type:
            raise ValueError("Discount type not found")
        
        # Create customer discount
        customer_discount = CustomerDiscount(
            company_id=company_id,
            customer_id=customer_id,
            discount_type_id=discount_type_id,
            discount_value=discount_value,
            discount_percentage=discount_percentage,
            max_discount_amount=max_discount_amount,
            min_order_amount=min_order_amount,
            start_date=start_date or date.today(),
            end_date=end_date,
            notes=notes,
            created_by=user_id
        )
        
        db.add(customer_discount)
        db.commit()
        db.refresh(customer_discount)
        
        logger.info(f"Customer discount created: {customer.name}")
        
        return customer_discount
    
    # Discount Analytics
    def get_discount_analytics(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        rule_id: Optional[int] = None,
        coupon_id: Optional[int] = None
    ) -> Dict:
        """Get discount analytics"""
        
        # Get discount applications
        query = db.query(DiscountApplication).filter(
            DiscountApplication.company_id == company_id
        )
        
        if from_date:
            query = query.filter(DiscountApplication.applied_date >= from_date)
        
        if to_date:
            query = query.filter(DiscountApplication.applied_date <= to_date)
        
        if rule_id:
            query = query.filter(DiscountApplication.rule_id == rule_id)
        
        applications = query.all()
        
        # Calculate analytics
        total_applications = len(applications)
        total_discount_amount = sum(app.discount_amount for app in applications)
        total_original_amount = sum(app.original_amount for app in applications)
        
        if total_original_amount > 0:
            average_discount_percentage = (total_discount_amount / total_original_amount) * 100
        else:
            average_discount_percentage = 0
        
        # Get unique customers
        unique_customers = len(set(app.customer_id for app in applications if app.customer_id))
        
        # Get top discount rules
        rule_stats = db.query(
            DiscountApplication.rule_id,
            func.count(DiscountApplication.id).label('application_count'),
            func.sum(DiscountApplication.discount_amount).label('total_discount')
        ).filter(
            DiscountApplication.company_id == company_id
        ).group_by(DiscountApplication.rule_id).all()
        
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "summary": {
                "total_applications": total_applications,
                "total_discount_amount": total_discount_amount,
                "total_original_amount": total_original_amount,
                "average_discount_percentage": average_discount_percentage,
                "unique_customers": unique_customers
            },
            "rule_statistics": [
                {
                    "rule_id": stat.rule_id,
                    "application_count": stat.application_count,
                    "total_discount": stat.total_discount
                }
                for stat in rule_stats
            ]
        }
    
    # Discount Report Generation
    def generate_discount_report(
        self, 
        db: Session, 
        company_id: int,
        report_name: str,
        report_type: str,
        from_date: date,
        to_date: date,
        user_id: int = None
    ) -> DiscountReport:
        """Generate discount report"""
        
        # Get discount data based on report type
        if report_type == 'summary':
            report_data = self._generate_summary_report(db, company_id, from_date, to_date)
        elif report_type == 'detailed':
            report_data = self._generate_detailed_report(db, company_id, from_date, to_date)
        elif report_type == 'customer':
            report_data = self._generate_customer_report(db, company_id, from_date, to_date)
        elif report_type == 'item':
            report_data = self._generate_item_report(db, company_id, from_date, to_date)
        else:
            raise ValueError(f"Invalid report type: {report_type}")
        
        # Create discount report
        report = DiscountReport(
            company_id=company_id,
            report_name=report_name,
            report_type=report_type,
            from_date=from_date,
            to_date=to_date,
            report_data=report_data,
            total_discounts=report_data.get('total_discounts', 0),
            total_applications=report_data.get('total_applications', 0),
            average_discount=report_data.get('average_discount', 0),
            generated_by=user_id,
            created_by=user_id
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Discount report generated: {report_name}")
        
        return report
    
    def _generate_summary_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate summary report data"""
        
        # Get discount applications
        applications = db.query(DiscountApplication).filter(
            DiscountApplication.company_id == company_id,
            DiscountApplication.applied_date >= from_date,
            DiscountApplication.applied_date <= to_date
        ).all()
        
        total_discounts = sum(app.discount_amount for app in applications)
        total_applications = len(applications)
        average_discount = total_discounts / total_applications if total_applications > 0 else 0
        
        return {
            "total_discounts": total_discounts,
            "total_applications": total_applications,
            "average_discount": average_discount,
            "applications": [
                {
                    "id": app.id,
                    "rule_id": app.rule_id,
                    "discount_amount": app.discount_amount,
                    "applied_date": app.applied_date
                }
                for app in applications
            ]
        }
    
    def _generate_detailed_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate detailed report data"""
        
        # Get detailed discount data
        applications = db.query(DiscountApplication).filter(
            DiscountApplication.company_id == company_id,
            DiscountApplication.applied_date >= from_date,
            DiscountApplication.applied_date <= to_date
        ).all()
        
        return {
            "applications": [
                {
                    "id": app.id,
                    "rule_id": app.rule_id,
                    "item_id": app.item_id,
                    "customer_id": app.customer_id,
                    "original_amount": app.original_amount,
                    "discount_amount": app.discount_amount,
                    "final_amount": app.final_amount,
                    "applied_date": app.applied_date
                }
                for app in applications
            ]
        }
    
    def _generate_customer_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate customer report data"""
        
        # Get customer discount data
        customer_stats = db.query(
            DiscountApplication.customer_id,
            func.count(DiscountApplication.id).label('application_count'),
            func.sum(DiscountApplication.discount_amount).label('total_discount')
        ).filter(
            DiscountApplication.company_id == company_id,
            DiscountApplication.applied_date >= from_date,
            DiscountApplication.applied_date <= to_date
        ).group_by(DiscountApplication.customer_id).all()
        
        return {
            "customer_statistics": [
                {
                    "customer_id": stat.customer_id,
                    "application_count": stat.application_count,
                    "total_discount": stat.total_discount
                }
                for stat in customer_stats
            ]
        }
    
    def _generate_item_report(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Generate item report data"""
        
        # Get item discount data
        item_stats = db.query(
            DiscountApplication.item_id,
            func.count(DiscountApplication.id).label('application_count'),
            func.sum(DiscountApplication.discount_amount).label('total_discount')
        ).filter(
            DiscountApplication.company_id == company_id,
            DiscountApplication.applied_date >= from_date,
            DiscountApplication.applied_date <= to_date
        ).group_by(DiscountApplication.item_id).all()
        
        return {
            "item_statistics": [
                {
                    "item_id": stat.item_id,
                    "application_count": stat.application_count,
                    "total_discount": stat.total_discount
                }
                for stat in item_stats
            ]
        }

# Global service instance
discount_management_service = DiscountManagementService()