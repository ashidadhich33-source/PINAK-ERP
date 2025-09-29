# backend/app/core/enhanced_error_handling.py
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union, Dict, Any
import logging
import traceback
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Custom Exception Classes
class ValidationError(Exception):
    """Raised when data validation fails"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

class BusinessRuleError(Exception):
    """Raised when business rules are violated"""
    def __init__(self, message: str, rule: str = None, code: str = None):
        self.message = message
        self.rule = rule
        self.code = code
        super().__init__(self.message)

class InventoryError(Exception):
    """Raised when inventory operations fail"""
    def __init__(self, message: str, item_id: int = None, code: str = None):
        self.message = message
        self.item_id = item_id
        self.code = code
        super().__init__(self.message)

class PaymentError(Exception):
    """Raised when payment operations fail"""
    def __init__(self, message: str, transaction_id: str = None, code: str = None):
        self.message = message
        self.transaction_id = transaction_id
        self.code = code
        super().__init__(self.message)

class NotificationError(Exception):
    """Raised when notification operations fail"""
    def __init__(self, message: str, notification_type: str = None, code: str = None):
        self.message = message
        self.notification_type = notification_type
        self.code = code
        super().__init__(self.message)

class DatabaseError(Exception):
    """Raised when database operations fail"""
    def __init__(self, message: str, operation: str = None, code: str = None):
        self.message = message
        self.operation = operation
        self.code = code
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    def __init__(self, message: str, user_id: int = None, code: str = None):
        self.message = message
        self.user_id = user_id
        self.code = code
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Raised when authorization fails"""
    def __init__(self, message: str, user_id: int = None, permission: str = None, code: str = None):
        self.message = message
        self.user_id = user_id
        self.permission = permission
        self.code = code
        super().__init__(self.message)

class ExternalServiceError(Exception):
    """Raised when external service calls fail"""
    def __init__(self, message: str, service: str = None, code: str = None):
        self.message = message
        self.service = service
        self.code = code
        super().__init__(self.message)

# Error Response Models
class ErrorResponse:
    """Standardized error response model"""
    
    def __init__(self, 
                 error_type: str,
                 message: str,
                 code: str = None,
                 details: Dict[str, Any] = None,
                 timestamp: datetime = None,
                 request_id: str = None):
        self.error_type = error_type
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.request_id = request_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.error_type,
            'message': self.message,
            'code': self.code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id
        }

# Enhanced Error Handlers
class EnhancedErrorHandler:
    """Enhanced error handling with comprehensive logging and recovery"""
    
    def __init__(self):
        self.error_counts = {}
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'exponential_backoff': True
        }
    
    def handle_validation_error(self, exc: ValidationError, request: Request) -> JSONResponse:
        """Handle validation errors with detailed field information"""
        error_response = ErrorResponse(
            error_type='ValidationError',
            message=exc.message,
            code=exc.code or 'VALIDATION_ERROR',
            details={
                'field': exc.field,
                'validation_type': 'field_validation'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.warning(f"Validation error: {exc.message} for field {exc.field}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict()
        )
    
    def handle_business_rule_error(self, exc: BusinessRuleError, request: Request) -> JSONResponse:
        """Handle business rule violations"""
        error_response = ErrorResponse(
            error_type='BusinessRuleError',
            message=exc.message,
            code=exc.code or 'BUSINESS_RULE_VIOLATION',
            details={
                'rule': exc.rule,
                'violation_type': 'business_rule'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.warning(f"Business rule violation: {exc.message} for rule {exc.rule}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict()
        )
    
    def handle_inventory_error(self, exc: InventoryError, request: Request) -> JSONResponse:
        """Handle inventory operation errors"""
        error_response = ErrorResponse(
            error_type='InventoryError',
            message=exc.message,
            code=exc.code or 'INVENTORY_ERROR',
            details={
                'item_id': exc.item_id,
                'error_type': 'inventory_operation'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.error(f"Inventory error: {exc.message} for item {exc.item_id}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response.to_dict()
        )
    
    def handle_payment_error(self, exc: PaymentError, request: Request) -> JSONResponse:
        """Handle payment operation errors"""
        error_response = ErrorResponse(
            error_type='PaymentError',
            message=exc.message,
            code=exc.code or 'PAYMENT_ERROR',
            details={
                'transaction_id': exc.transaction_id,
                'error_type': 'payment_operation'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.error(f"Payment error: {exc.message} for transaction {exc.transaction_id}")
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content=error_response.to_dict()
        )
    
    def handle_notification_error(self, exc: NotificationError, request: Request) -> JSONResponse:
        """Handle notification errors (non-critical)"""
        error_response = ErrorResponse(
            error_type='NotificationError',
            message=exc.message,
            code=exc.code or 'NOTIFICATION_ERROR',
            details={
                'notification_type': exc.notification_type,
                'error_type': 'notification_operation'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.warning(f"Notification error: {exc.message} for type {exc.notification_type}")
        # Don't fail the operation for notification errors
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                'success': True,
                'warning': error_response.to_dict()
            }
        )
    
    def handle_database_error(self, exc: DatabaseError, request: Request) -> JSONResponse:
        """Handle database operation errors"""
        error_response = ErrorResponse(
            error_type='DatabaseError',
            message=exc.message,
            code=exc.code or 'DATABASE_ERROR',
            details={
                'operation': exc.operation,
                'error_type': 'database_operation'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.error(f"Database error: {exc.message} for operation {exc.operation}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict()
        )
    
    def handle_authentication_error(self, exc: AuthenticationError, request: Request) -> JSONResponse:
        """Handle authentication errors"""
        error_response = ErrorResponse(
            error_type='AuthenticationError',
            message=exc.message,
            code=exc.code or 'AUTHENTICATION_ERROR',
            details={
                'user_id': exc.user_id,
                'error_type': 'authentication'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.warning(f"Authentication error: {exc.message} for user {exc.user_id}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response.to_dict()
        )
    
    def handle_authorization_error(self, exc: AuthorizationError, request: Request) -> JSONResponse:
        """Handle authorization errors"""
        error_response = ErrorResponse(
            error_type='AuthorizationError',
            message=exc.message,
            code=exc.code or 'AUTHORIZATION_ERROR',
            details={
                'user_id': exc.user_id,
                'permission': exc.permission,
                'error_type': 'authorization'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.warning(f"Authorization error: {exc.message} for user {exc.user_id} permission {exc.permission}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response.to_dict()
        )
    
    def handle_external_service_error(self, exc: ExternalServiceError, request: Request) -> JSONResponse:
        """Handle external service errors"""
        error_response = ErrorResponse(
            error_type='ExternalServiceError',
            message=exc.message,
            code=exc.code or 'EXTERNAL_SERVICE_ERROR',
            details={
                'service': exc.service,
                'error_type': 'external_service'
            },
            request_id=self._get_request_id(request)
        )
        
        logger.error(f"External service error: {exc.message} for service {exc.service}")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=error_response.to_dict()
        )
    
    def handle_generic_error(self, exc: Exception, request: Request) -> JSONResponse:
        """Handle generic errors with comprehensive logging"""
        error_id = self._generate_error_id()
        error_response = ErrorResponse(
            error_type='InternalServerError',
            message='An unexpected error occurred',
            code='INTERNAL_SERVER_ERROR',
            details={
                'error_id': error_id,
                'error_type': 'unexpected_error'
            },
            request_id=self._get_request_id(request)
        )
        
        # Log the full error with stack trace
        logger.error(f"Unexpected error {error_id}: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict()
        )
    
    def _get_request_id(self, request: Request) -> str:
        """Get or generate request ID"""
        return getattr(request.state, 'request_id', 'unknown')
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ERR_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if operation should be retried"""
        if attempt >= self.retry_config['max_retries']:
            return False
        
        # Don't retry certain error types
        non_retryable_errors = [
            ValidationError,
            BusinessRuleError,
            AuthenticationError,
            AuthorizationError
        ]
        
        if any(isinstance(error, error_type) for error_type in non_retryable_errors):
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff"""
        base_delay = self.retry_config['retry_delay']
        if self.retry_config['exponential_backoff']:
            return base_delay * (2 ** attempt)
        return base_delay

# Retry Decorator
import asyncio
from functools import wraps

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator for retrying operations on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            error_handler = EnhancedErrorHandler()
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not error_handler.should_retry(e, attempt):
                        raise
                    
                    if attempt < max_retries:
                        retry_delay = error_handler.get_retry_delay(attempt)
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                    else:
                        raise
            
            return None
        return wrapper
    return decorator

# Global Exception Handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    error_handler = EnhancedErrorHandler()
    
    errors = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'])
        errors.append({
            'field': field,
            'message': error['msg'],
            'type': error['type']
        })
    
    error_response = ErrorResponse(
        error_type='ValidationError',
        message='Request validation failed',
        code='VALIDATION_ERROR',
        details={'errors': errors},
        request_id=error_handler._get_request_id(request)
    )
    
    logger.warning(f"Request validation failed: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    error_handler = EnhancedErrorHandler()
    
    error_response = ErrorResponse(
        error_type='HTTPException',
        message=exc.detail,
        code=f'HTTP_{exc.status_code}',
        request_id=error_handler._get_request_id(request)
    )
    
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.to_dict()
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions"""
    error_handler = EnhancedErrorHandler()
    
    # Handle custom exceptions
    if isinstance(exc, ValidationError):
        return error_handler.handle_validation_error(exc, request)
    elif isinstance(exc, BusinessRuleError):
        return error_handler.handle_business_rule_error(exc, request)
    elif isinstance(exc, InventoryError):
        return error_handler.handle_inventory_error(exc, request)
    elif isinstance(exc, PaymentError):
        return error_handler.handle_payment_error(exc, request)
    elif isinstance(exc, NotificationError):
        return error_handler.handle_notification_error(exc, request)
    elif isinstance(exc, DatabaseError):
        return error_handler.handle_database_error(exc, request)
    elif isinstance(exc, AuthenticationError):
        return error_handler.handle_authentication_error(exc, request)
    elif isinstance(exc, AuthorizationError):
        return error_handler.handle_authorization_error(exc, request)
    elif isinstance(exc, ExternalServiceError):
        return error_handler.handle_external_service_error(exc, request)
    else:
        return error_handler.handle_generic_error(exc, request)

# Error Recovery Functions
class ErrorRecoveryService:
    """Service for error recovery and mitigation"""
    
    @staticmethod
    async def recover_from_database_error(error: DatabaseError, operation: str) -> bool:
        """Attempt to recover from database errors"""
        try:
            # Implement database recovery logic
            logger.info(f"Attempting database recovery for operation: {operation}")
            # Add specific recovery logic here
            return True
        except Exception as e:
            logger.error(f"Database recovery failed: {str(e)}")
            return False
    
    @staticmethod
    async def recover_from_external_service_error(error: ExternalServiceError, service: str) -> bool:
        """Attempt to recover from external service errors"""
        try:
            # Implement external service recovery logic
            logger.info(f"Attempting external service recovery for: {service}")
            # Add specific recovery logic here
            return True
        except Exception as e:
            logger.error(f"External service recovery failed: {str(e)}")
            return False
    
    @staticmethod
    async def mitigate_inventory_error(error: InventoryError, item_id: int) -> bool:
        """Attempt to mitigate inventory errors"""
        try:
            # Implement inventory error mitigation
            logger.info(f"Attempting inventory error mitigation for item: {item_id}")
            # Add specific mitigation logic here
            return True
        except Exception as e:
            logger.error(f"Inventory error mitigation failed: {str(e)}")
            return False

# Initialize error handler
enhanced_error_handler = EnhancedErrorHandler()
error_recovery_service = ErrorRecoveryService()