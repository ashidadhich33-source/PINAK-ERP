# Loyalty Services
from .loyalty_service import LoyaltyService
from .loyalty_program_service import LoyaltyProgramService

# Service instances
loyalty_service = LoyaltyService()
loyalty_program_service = LoyaltyProgramService()

__all__ = [
    "LoyaltyService",
    "LoyaltyProgramService",
    "loyalty_service",
    "loyalty_program_service"
]