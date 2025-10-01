# backend/app/api/endpoints/database_setup.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any
import logging

from ...database import get_db
from ...models.core.user import User
from ...core.security import get_current_user
from ...init_data import init_default_data
from ...database import create_tables, check_database_connection

router = APIRouter()
logger = logging.getLogger(__name__)

class SetupStatus(BaseModel):
    database_connected: bool
    tables_created: bool
    default_data_initialized: bool
    admin_user_created: bool
    is_setup_complete: bool = False
    setup_stage: str = "initial"

@router.get("/status")
async def get_setup_status(
    current_user: User = Depends(get_current_user)
) -> SetupStatus:
    """Get system setup status"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only superusers can view setup status")

        # Check database connection
        db_connected = check_database_connection()

        # Check if tables exist
        tables_created = False
        if db_connected:
            try:
                create_tables()  # This will create tables if they don't exist
                tables_created = True
            except Exception as e:
                logger.error(f"Error checking tables: {e}")

        # Check if admin user exists
        admin_exists = False
        if db_connected:
            try:
                from ...database import get_db
                with get_db() as db:
                    admin_exists = db.query(User).filter(User.is_superuser == True).first() is not None
            except Exception as e:
                logger.error(f"Error checking admin user: {e}")

        is_setup_complete = db_connected and tables_created and admin_exists
        setup_stage = "complete" if is_setup_complete else "in_progress"

        return SetupStatus(
            database_connected=db_connected,
            tables_created=tables_created,
            default_data_initialized=admin_exists,
            admin_user_created=admin_exists,
            is_setup_complete=is_setup_complete,
            setup_stage=setup_stage
        )

    except Exception as e:
        logger.error(f"Error getting setup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
async def initialize_system(
    current_user: User = Depends(get_current_user)
):
    """Initialize the entire system"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only superusers can initialize system")

        # Create tables
        create_tables()
        logger.info("Database tables created")

        # Initialize default data
        await init_default_data()
        logger.info("Default data initialized")

        return {"message": "System initialized successfully"}

    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-admin")
async def create_admin_user(
    username: str,
    password: str,
    email: str,
    full_name: str = "Administrator",
    current_user: User = Depends(get_current_user)
):
    """Create initial admin user"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only superusers can create admin users")

        # Check if admin already exists
        from ...database import get_db
        with get_db() as db:
            existing_admin = db.query(User).filter(User.is_superuser == True).first()
            if existing_admin:
                raise HTTPException(status_code=400, detail="Admin user already exists")

            # Create admin user
            from ...core.security import SecurityService
            from ...models.core.user import Role

            admin_user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=SecurityService.get_password_hash(password),
                is_superuser=True
            )

            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                admin_user.roles.append(admin_role)

            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            return {"message": "Admin user created successfully"}

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def system_health():
    """Get system health information"""
    health_info = {
        "database": {
            "connected": check_database_connection(),
            "type": "sqlite"  # This could be made dynamic
        },
        "tables_exist": False,
        "admin_exists": False
    }

    try:
        # Check tables
        from ...database import get_db
        with get_db() as db:
            # Try to query a basic table
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            health_info["tables_exist"] = len(result) > 0

            # Check admin user
            admin_count = db.query(User).filter(User.is_superuser == True).count()
            health_info["admin_exists"] = admin_count > 0

    except Exception as e:
        logger.error(f"Error checking system health: {e}")

    return health_info