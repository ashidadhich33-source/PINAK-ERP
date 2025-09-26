# backend/app/core/middleware.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from pathlib import Path
from ..config import settings

logger = logging.getLogger(__name__)

def setup_middlewares(app: FastAPI):
    """Setup all middleware for the application"""

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add trusted host middleware for security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.localhost", settings.host]
    )

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all HTTP requests"""
        start_time = time.time()

        # Skip logging for static files and health checks
        skip_paths = ["/static", "/uploads", "/favicon.ico", "/health"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Log request
        logger.info(f"🔵 {request.method} {request.url.path} - {request.client.host}")

        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(f"🔴 {response.status_code} {request.url.path} - {process_time".3f"}s")

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response

    # Rate limiting middleware (basic implementation)
    if settings.rate_limit_enabled:
        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            """Basic rate limiting"""
            # This is a simple implementation - for production use a proper rate limiter like Redis
            client_ip = request.client.host
            # You could implement in-memory rate limiting here
            # For now, just pass through
            response = await call_next(request)
            return response

    # Security headers middleware
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        """Add security headers to responses"""
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response