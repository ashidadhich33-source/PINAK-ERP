# backend/app/main.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
import asyncio
from datetime import datetime, time, timedelta
from pathlib import Path

from .config import settings
from .database import create_tables, get_db, engine, Base
from .api.endpoints import auth, setup, items, sales, purchases, reports, customers, suppliers
from .api.endpoints import backup  # Backup endpoint
from .core.security import get_current_user
from .services.backup_service import backup_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{settings.log_dir}/erp_system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Scheduled backup task
async def scheduled_backup_task():
    """Run daily backup at 2:00 AM"""
    while True:
        try:
            now = datetime.now()
            # Calculate seconds until 2:00 AM
            target_time = datetime.combine(now.date(), time(2, 0))
            if now > target_time:
                # If it's past 2 AM today, schedule for tomorrow
                target_time = datetime.combine(
                    now.date() + timedelta(days=1), 
                    time(2, 0)
                )
            
            seconds_until_backup = (target_time - now).total_seconds()
            
            # Wait until backup time
            await asyncio.sleep(seconds_until_backup)
            
            # Perform backup
            logger.info("Starting scheduled backup...")
            result = backup_service.create_backup(
                backup_name=f"scheduled_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if result['success']:
                logger.info(f"Scheduled backup completed: {result['backup_file']}")
            else:
                logger.error(f"Scheduled backup failed: {result.get('error')}")
            
            # Wait a bit before checking again (to avoid duplicate runs)
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Scheduled backup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in scheduled backup task: {e}")
            await asyncio.sleep(3600)  # Wait an hour before retrying

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Initialize default data if needed
    try:
        from .core.init_data import initialize_default_data
        await initialize_default_data()
        logger.info("Default data initialized")
    except Exception as e:
        logger.warning(f"Could not initialize default data: {e}")
    
    # Start scheduled backup task
    backup_task = asyncio.create_task(scheduled_backup_task())
    logger.info("Scheduled backup service started")
    
    # Verify backup directory exists
    backup_service.backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Print startup message
    print("\n" + "="*50)
    print("ERP SYSTEM STARTED SUCCESSFULLY")
    print("="*50)
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"Backup Service: Active")
    print(f"Scheduled Backup: Daily at 02:00 AM")
    print("="*50 + "\n")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ERP System...")
    
    # Cancel backup task
    backup_task.cancel()
    try:
        await backup_task
    except asyncio.CancelledError:
        pass
    
    logger.info("ERP System shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Windows-based ERP System with SQLAlchemy, Backup & Restore",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc) if settings.debug else "An error occurred"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ERP System API",
        "version": settings.app_version,
        "status": "running"
    }

# Health check
@app.get("/health")
async def health_check():
    """System health check with backup information"""
    last_backup = await get_last_backup_info()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "backup_service": "active",
        "last_backup": last_backup
    }

async def get_last_backup_info():
    """Get information about the last backup"""
    try:
        backups = backup_service.list_backups()
        if backups:
            latest = backups[0]
            return {
                "filename": latest['filename'],
                "created": latest['created'],
                "size_mb": latest['size_mb']
            }
    except Exception as e:
        logger.error(f"Error getting last backup info: {e}")
    return None

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(setup.router, prefix="/api/setup", tags=["Setup"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(sales.router, prefix="/api/sales", tags=["Sales"])
app.include_router(purchases.router, prefix="/api/purchases", tags=["Purchases"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup & Restore"])

# Protected route example
@app.get("/api/user/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "is_superuser": current_user.is_superuser,
            "roles": [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers
    )