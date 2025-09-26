# backend/app/core/exceptions.py
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class ERPException(Exception):
    """Base exception for ERP system"""

    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DatabaseException(ERPException):
    """Database related exceptions"""
    pass

class ValidationException(ERPException):
    """Data validation exceptions"""
    pass

class AuthenticationException(ERPException):
    """Authentication related exceptions"""
    pass

class AuthorizationException(ERPException):
    """Authorization related exceptions"""
    pass

def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""

    @app.exception_handler(ERPException)
    async def erp_exception_handler(request, exc: ERPException):
        logger.error(f"ERP Exception: {exc.message}", extra={"details": exc.details})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "ERP System Error",
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Request data validation failed",
                "details": exc.errors()
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )