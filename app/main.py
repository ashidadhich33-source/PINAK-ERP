# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
import asyncio
import time
from datetime import datetime, time as dt_time, timedelta
from pathlib import Path
import sys
import os
from typing import Dict, Any

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from .config import settings
from .database import create_tables, get_db, engine, Base, check_database_connection
from .api.endpoints import (
    # Core endpoints
    auth, setup, companies, settings as settings_api, payments, expenses, reports, backup, gst, discount_management, report_studio, system_integration, whatsapp, database_setup,
    # Accounting endpoints  
    double_entry_accounting, chart_of_accounts, financial_year, financial_year_management,
    # Sales endpoints
    enhanced_sales, sale_returns,
    # Purchase endpoints
    enhanced_purchase, purchases,
    # Inventory endpoints
    items, enhanced_item_master, advanced_inventory,
    # Customer endpoints
    customers, suppliers,
    # Loyalty endpoints
    loyalty_program
)
from .core.security import get_current_user
from .services.core.backup_service import backup_service
from .core.init_data import initialize_default_data
from .core.exceptions import setup_exception_handlers
from .core.middleware import setup_middlewares

# Configure logging
def setup_logging():
    """Setup comprehensive logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory
    logs_dir = Path(settings.log_dir)
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / "erp_system.log"),
            logging.FileHandler(logs_dir / f"erp_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )
    
    # Configure specific loggers
    loggers = {
        'uvicorn': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'fastapi': logging.INFO,
        'app': logging.DEBUG if settings.debug else logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)

setup_logging()
logger = logging.getLogger(__name__)

# Scheduled backup task
async def scheduled_backup_task():
    """Run daily backup at configured time"""
    while True:
        try:
            now = datetime.now()
            # Parse backup time from settings (e.g., "02:00")
            backup_hour, backup_minute = map(int, settings.backup_time.split(':'))
            target_time = datetime.combine(now.date(), dt_time(backup_hour, backup_minute))
            
            if now > target_time:
                # If it's past backup time today, schedule for tomorrow
                target_time = datetime.combine(
                    now.date() + timedelta(days=1), 
                    dt_time(backup_hour, backup_minute)
                )
            
            seconds_until_backup = (target_time - now).total_seconds()
            
            # Wait until backup time
            await asyncio.sleep(seconds_until_backup)
            
            # Perform backup
            logger.info("Starting scheduled backup...")
            result = backup_service.create_backup(
                backup_name=f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            if result['success']:
                logger.info(f"Scheduled backup completed: {result['backup_file']}")
            else:
                logger.error(f"Scheduled backup failed: {result.get('error')}")
            
            # Wait a bit before checking again
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Scheduled backup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in scheduled backup task: {e}")
            await asyncio.sleep(3600)  # Wait an hour before retrying

# Health check tasks
async def health_check_task():
    """Periodic health checks"""
    while True:
        try:
            # Check database connection
            db_healthy = check_database_connection()
            if not db_healthy:
                logger.error("Database health check failed")
            
            # Check disk space
            import shutil
            disk_usage = shutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 1:  # Less than 1GB free
                logger.warning(f"Low disk space: {free_gb:.2f}GB remaining")
            
            # Wait 5 minutes before next check
            await asyncio.sleep(300)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {e}")
            await asyncio.sleep(300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Check database connection
    if not check_database_connection():
        logger.error("❌ Database connection failed!")
        raise RuntimeError("Database connection failed")
    
    # Create database tables
    try:
        create_tables()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database table creation failed: {e}")
        raise
    
    # Initialize default data
    try:
        from .init_data import init_default_data
        with get_db_session() as db:
            init_default_data(db)
        logger.info("✅ Default data initialized")
    except Exception as e:
        logger.warning(f"⚠️  Could not initialize default data: {e}")
    
    # Create necessary directories
    for directory in [settings.upload_dir, settings.backup_location, settings.log_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Start background tasks
    backup_task = None
    health_task = None
    
    if settings.backup_enabled:
        backup_task = asyncio.create_task(scheduled_backup_task())
        logger.info("✅ Scheduled backup service started")
    
    health_task = asyncio.create_task(health_check_task())
    logger.info("✅ Health monitoring started")
    
    # Print startup message
    print("\n" + "="*60)
    print(f"🎉 {settings.app_name.upper()} STARTED SUCCESSFULLY")
    print("="*60)
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔒 Admin Panel: http://{settings.host}:{settings.port}/admin")
    print(f"💾 Database: {settings.database_type.title()}")
    print(f"🔄 Backup: {'Enabled' if settings.backup_enabled else 'Disabled'}")
    print(f"📱 WhatsApp: {'Enabled' if settings.whatsapp_enabled else 'Disabled'}")
    print(f"📧 Email: {'Enabled' if settings.email_enabled else 'Disabled'}")
    print("="*60)
    print("🔑 Default Login: admin / admin123")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ERP System...")
    
    # Cancel background tasks
    if backup_task:
        backup_task.cancel()
        try:
            await backup_task
        except asyncio.CancelledError:
            pass
    
    if health_task:
        health_task.cancel()
        try:
            await health_task
        except asyncio.CancelledError:
            pass
    
    logger.info("✅ ERP System shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.api_title,
    version=settings.app_version,
    description=settings.app_description,
    docs_url="/docs" if settings.debug else "/docs",
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else "/openapi.json",
    lifespan=lifespan
)

# Setup middlewares
setup_middlewares(app)

# Setup exception handlers
setup_exception_handlers(app)

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

# Mount static files
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount uploads directory
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

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
    logger.info(f"🔴 {response.status_code} {request.url.path} - {process_time:.3f}s")
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with system information and setup check"""
    try:
        # Check if system is set up
        from .api.endpoints.core.database_setup import get_setup_status
        setup_status = await get_setup_status()
        
        if not setup_status.is_setup_complete:
            return {
                "message": f"{settings.app_name} - Setup Required",
                "version": settings.app_version,
                "setup_url": "/setup",
                "status": "setup_required",
                "setup_stage": setup_status.setup_stage,
                "docs": "/docs"
            }
        else:
            return {
                "message": f"Welcome to {settings.app_name}",
                "version": settings.app_version,
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "docs": "/docs",
                "admin": "/admin"
            }
    except Exception as e:
        # If setup check fails, assume setup is needed
        return {
            "message": f"{settings.app_name} - Setup Required",
            "version": settings.app_version,
            "setup_url": "/setup",
            "status": "setup_required",
            "error": str(e),
            "docs": "/docs"
        }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "database": {
            "status": "connected" if check_database_connection() else "disconnected",
            "type": settings.database_type
        },
        "services": {
            "backup_service": "active" if settings.backup_enabled else "disabled",
            "whatsapp": "enabled" if settings.whatsapp_enabled else "disabled",
            "email": "enabled" if settings.email_enabled else "disabled",
        }
    }
    
    # Add last backup info
    try:
        backups = backup_service.list_backups()
        if backups:
            latest = backups[0]
            health_data["last_backup"] = {
                "filename": latest['filename'],
                "created": latest['created'],
                "size_mb": latest['size_mb']
            }
    except Exception:
        pass
    
    return health_data

@app.get("/version")
async def version_info():
    """Get detailed version information"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "build_date": "2024-08-26",
        "python_version": sys.version,
        "database": settings.database_type,
        "features": {
            "gst_enabled": settings.gst_enabled,
            "loyalty_enabled": settings.loyalty_enabled,
            "whatsapp_enabled": settings.whatsapp_enabled,
            "email_enabled": settings.email_enabled,
            "backup_enabled": settings.backup_enabled
        }
    }

# Include API routers with proper prefixes and tags
api_routers = [
    # Core endpoints
    (auth.router, "/auth", ["🔐 Authentication"]),
    (setup.router, "/setup", ["⚙️ Setup"]),
    (companies.router, "/companies", ["🏢 Company Management"]),
    (settings_api.router, "/settings", ["🔧 System Settings"]),
    (payments.router, "/payments", ["💳 Payment Processing"]),
    (expenses.router, "/expenses", ["💸 Expense Management"]),
    (reports.router, "/reports", ["📊 Reports & Analytics"]),
    (backup.router, "/backup", ["💾 Backup & Restore"]),
    (gst.router, "/gst", ["🏛️ GST Management"]),
    (discount_management.router, "/discount-management", ["💰 Discount Management"]),
    (report_studio.router, "/report-studio", ["📊 Report Studio"]),
    (system_integration.router, "/system-integration", ["🔧 System Integration"]),
    (whatsapp.router, "/whatsapp", ["📱 WhatsApp Integration"]),
    (database_setup.router, "/database-setup", ["🗄️ Database Setup Wizard"]),
    
    # Accounting endpoints
    (double_entry_accounting.router, "/double-entry-accounting", ["📊 Double Entry Accounting"]),
    (chart_of_accounts.router, "/chart-of-accounts", ["📊 Chart of Accounts"]),
    (financial_year.router, "/financial-years", ["📅 Financial Year Management"]),
    (financial_year_management.router, "/financial-year-management", ["📅 Financial Year Management"]),
    
    # Sales endpoints
    (enhanced_sales.router, "/enhanced-sales", ["💰 Enhanced Sales Management"]),
    (sale_returns.router, "/sale-returns", ["🔄 Sales Returns"]),
    
    # Purchase endpoints
    (enhanced_purchase.router, "/enhanced-purchase", ["🛒 Enhanced Purchase Management"]),
    (purchases.router, "/purchases", ["🛒 Purchase Management"]),
    
    # Inventory endpoints
    (items.router, "/items", ["📦 Items & Inventory"]),
    (enhanced_item_master.router, "/enhanced-item-master", ["📦 Enhanced Item Master"]),
    (advanced_inventory.router, "/advanced-inventory", ["📦 Advanced Inventory Management"]),
    
    # Customer endpoints
    (customers.router, "/customers", ["👥 Customer Management"]),
    (suppliers.router, "/suppliers", ["🏪 Supplier Management"]),
    
    # Loyalty endpoints
    (loyalty_program.router, "/loyalty-program", ["🎁 Loyalty Program"])
]

for router, prefix, tags in api_routers:
    app.include_router(router, prefix=f"{settings.api_prefix}{prefix}", tags=tags)

# Setup wizard redirect
@app.get("/setup")
async def setup_wizard():
    """Serve the setup wizard"""
    from fastapi.responses import FileResponse
    return FileResponse("setup_wizard.html")

# Admin panel redirect
@app.get("/admin")
async def admin_panel():
    """Redirect to admin panel"""
    return {
        "message": "Admin Panel",
        "login_url": f"{settings.api_prefix}/auth/login",
        "docs_url": "/docs",
        "version": settings.app_version
    }

# Protected route examples
@app.get(f"{settings.api_prefix}/profile")
async def get_user_profile(current_user=Depends(get_current_user)):
    """Get current user profile"""
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "is_superuser": current_user.is_superuser,
            "last_login": current_user.last_login,
            "roles": [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
        },
        "permissions": {
            "can_view_reports": current_user.has_permission("reports.view"),
            "can_manage_users": current_user.has_permission("users.manage"),
            "can_backup": current_user.has_permission("backup.create")
        }
    }

@app.get(f"{settings.api_prefix}/dashboard")
async def get_dashboard(current_user=Depends(get_current_user), db=Depends(get_db)):
    """Get dashboard summary data"""
    from .models.sales import SalesInvoice
    from .models.customers import Customer
    from .models.inventory import Item
    from sqlalchemy import func
    from datetime import date
    
    today = date.today()
    
    # Get basic counts
    total_customers = db.query(Customer).count()
    total_items = db.query(Item).filter(Item.status == 'active').count()
    
    # Today's sales
    today_sales = db.query(func.sum(SalesInvoice.total_amount)).filter(
        func.date(SalesInvoice.invoice_date) == today
    ).scalar() or 0
    
    return {
        "welcome_message": f"Welcome back, {current_user.full_name}!",
        "summary": {
            "total_customers": total_customers,
            "total_items": total_items,
            "today_sales": float(today_sales),
            "system_status": "operational"
        },
        "quick_actions": [
            {"name": "New Sale", "url": f"{settings.api_prefix}/sales/pos"},
            {"name": "Add Customer", "url": f"{settings.api_prefix}/customers"},
            {"name": "Reports", "url": f"{settings.api_prefix}/reports"},
            {"name": "Backup", "url": f"{settings.api_prefix}/backup"}
        ]
    }

# Development utilities (only in debug mode)
if settings.debug:
    @app.get("/dev/reset-db")
    async def reset_database():
        """Reset database (DEBUG ONLY)"""
        try:
            from .database import drop_tables, get_db_session
            from .init_data import init_default_data
            drop_tables()
            create_tables()
            with get_db_session() as db:
                init_default_data(db)
            return {"message": "Database reset successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/dev/logs")
    async def view_logs(lines: int = 100):
        """View recent log entries (DEBUG ONLY)"""
        try:
            log_file = Path(settings.log_dir) / "erp_system.log"
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = f.readlines()
                return {"logs": logs[-lines:]}
            return {"logs": []}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔒 Default Login: admin / admin123")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level="info",
        access_log=settings.debug
    )
