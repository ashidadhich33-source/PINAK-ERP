from decimal import Decimal
from sqlalchemy.orm import Session
from typing import Optional
from ..models import LoyaltyGrade

class LoyaltyService:
    """Service for loyalty points and grades"""
    
    @staticmethod
    def calculate_points_earned(base_amount: Decimal, customer_grade: str) -> int:
        """Calculate points earned based on grade"""
        # Default earn rates
        earn_rates = {
            "Silver": Decimal('1.0'),
            "Gold": Decimal('1.5'),
            "Platinum": Decimal('2.0')
        }
        
        earn_rate = earn_rates.get(customer_grade, Decimal('1.0'))
        points = (base_amount * earn_rate / 100).quantize(Decimal('1'))
        
        return int(points)
    
    @staticmethod
    def check_grade_upgrade(db: Session, lifetime_purchase: Decimal) -> Optional[str]:
        """Check if customer qualifies for grade upgrade"""
        grades = db.query(LoyaltyGrade).order_by(LoyaltyGrade.amount_from).all()
        
        qualified_grade = None
        for grade in grades:
            if lifetime_purchase >= grade.amount_from and lifetime_purchase <= grade.amount_to:
                qualified_grade = grade.name
                break
        
        return qualified_grade
    
    @staticmethod
    def validate_redemption(points_balance: int, points_to_redeem: int) -> bool:
        """Validate if redemption is possible"""
        return points_balance >= points_to_redeem and points_to_redeem > 0
    
    @staticmethod
    def get_redemption_value(points: int) -> Decimal:
        """Convert points to monetary value (1 point = ₹1)"""
        return Decimal(str(points))