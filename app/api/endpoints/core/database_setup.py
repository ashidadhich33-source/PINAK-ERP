# backend/app/api/endpoints/database_setup.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from pydantic import BaseModel, validator
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from pathlib import Path
import secrets

from ...database import get_db, create_tables, Base, engine
from ...models.core import Company, User, Role, Permission
from ...core.security import SecurityService
from ...core.init_data import initialize_default_data

router = APIRouter()
logger = logging.getLogger(__name__)

# Database Configuration Models
class DatabaseConfig(BaseModel):
    database_type: str
    database_name: str
    host: Optional[str] = "localhost"
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    @validator('database_type')
    def validate_database_type(cls, v):
        if v not in ['sqlite', 'postgresql', 'mysql']:
            raise ValueError('Database type must be sqlite, postgresql, or mysql')
        return v
    
    @validator('port')
    def set_default_port(cls, v, values):
        if v is None:
            if values.get('database_type') == 'postgresql':
                return 5432
            elif values.get('database_type') == 'mysql':
                return 3306
        return v

class CompanySetup(BaseModel):
    company_name: str
    company_email: str
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    company_city: Optional[str] = None
    company_state: Optional[str] = None
    company_country: Optional[str] = None
    company_pincode: Optional[str] = None
    company_gstin: Optional[str] = None
    company_website: Optional[str] = None
    financial_year_start: str = "04-01"  # April 1st
    financial_year_end: str = "03-31"   # March 31st
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    
    @validator('company_name')
    def validate_company_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Company name must be at least 2 characters')
        return v.strip()
    
    @validator('company_email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

class AdminUserSetup(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v.lower()

class SetupWizardRequest(BaseModel):
    database_config: DatabaseConfig
    company_setup: CompanySetup
    admin_user: AdminUserSetup
    create_sample_data: bool = True

class DatabaseTestResult(BaseModel):
    success: bool
    message: str
    connection_string: Optional[str] = None

class SetupStatus(BaseModel):
    is_setup_complete: bool
    database_connected: bool
    tables_created: bool
    company_created: bool
    admin_user_created: bool
    sample_data_loaded: bool
    setup_stage: str  # "database", "company", "admin", "complete"

# Database Connection Testing
@router.post("/test-database", response_model=DatabaseTestResult)
async def test_database_connection(config: DatabaseConfig):
    """Test database connection before setup"""
    try:
        if config.database_type == "sqlite":
            # For SQLite, just check if we can create the file
            db_path = Path(f"./database/{config.database_name}.db")
            db_path.parent.mkdir(exist_ok=True, parents=True)
            connection_string = f"sqlite:///{db_path}"
            
        elif config.database_type == "postgresql":
            connection_string = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
            
        elif config.database_type == "mysql":
            connection_string = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
        
        # Test connection
        test_engine = create_engine(connection_string)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return DatabaseTestResult(
            success=True,
            message=f"Successfully connected to {config.database_type} database",
            connection_string=connection_string
        )
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return DatabaseTestResult(
            success=False,
            message=f"Database connection failed: {str(e)}"
        )

# Get Available Database Types
@router.get("/database-types")
async def get_database_types():
    """Get available database types and their requirements"""
    return {
        "database_types": [
            {
                "type": "sqlite",
                "name": "SQLite",
                "description": "Lightweight, file-based database. Perfect for development and small deployments.",
                "requirements": ["database_name"],
                "default_port": None,
                "recommended_for": "Development, Small businesses"
            },
            {
                "type": "postgresql", 
                "name": "PostgreSQL",
                "description": "Powerful, open-source relational database. Recommended for production.",
                "requirements": ["database_name", "host", "port", "username", "password"],
                "default_port": 5432,
                "recommended_for": "Production, Large businesses"
            },
            {
                "type": "mysql",
                "name": "MySQL",
                "description": "Popular open-source database. Good for web applications.",
                "requirements": ["database_name", "host", "port", "username", "password"],
                "default_port": 3306,
                "recommended_for": "Web applications, Medium businesses"
            }
        ]
    }

# Check Setup Status
@router.get("/status", response_model=SetupStatus)
async def get_setup_status():
    """Get current setup status"""
    try:
        # Check database connection
        from ...database import check_database_connection
        db_connected = check_database_connection()
        
        if not db_connected:
            return SetupStatus(
                is_setup_complete=False,
                database_connected=False,
                tables_created=False,
                company_created=False,
                admin_user_created=False,
                sample_data_loaded=False,
                setup_stage="database"
            )
        
        # Check if tables exist
        tables_created = False
        try:
            create_tables()
            tables_created = True
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
        
        if not tables_created:
            return SetupStatus(
                is_setup_complete=False,
                database_connected=True,
                tables_created=False,
                company_created=False,
                admin_user_created=False,
                sample_data_loaded=False,
                setup_stage="database"
            )
        
        # Check if company exists
        company_created = False
        admin_user_created = False
        sample_data_loaded = False
        
        try:
            with get_db() as db:
                company_created = db.query(Company).first() is not None
                admin_user_created = db.query(User).filter(User.is_superuser == True).first() is not None
                # Check if we have sample data (items, customers, etc.)
                from ...models.inventory import Item
                from ...models.customers import Customer
                sample_data_loaded = (
                    db.query(Item).count() > 0 or 
                    db.query(Customer).count() > 0
                )
        except Exception as e:
            logger.error(f"Error checking setup status: {e}")
        
        # Determine setup stage
        if not company_created:
            setup_stage = "company"
        elif not admin_user_created:
            setup_stage = "admin"
        elif not sample_data_loaded:
            setup_stage = "sample_data"
        else:
            setup_stage = "complete"
        
        is_setup_complete = (
            db_connected and 
            tables_created and 
            company_created and 
            admin_user_created
        )
        
        return SetupStatus(
            is_setup_complete=is_setup_complete,
            database_connected=db_connected,
            tables_created=tables_created,
            company_created=company_created,
            admin_user_created=admin_user_created,
            sample_data_loaded=sample_data_loaded,
            setup_stage=setup_stage
        )
        
    except Exception as e:
        logger.error(f"Error getting setup status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking setup status: {str(e)}"
        )

# Complete Setup Wizard
@router.post("/complete-setup")
async def complete_setup_wizard(
    setup_data: SetupWizardRequest,
    db: Session = Depends(get_db)
):
    """Complete the setup wizard with database, company, and admin user"""
    try:
        # Step 1: Create/Update database configuration
        logger.info("Starting setup wizard...")
        
        # Step 2: Create tables
        logger.info("Creating database tables...")
        create_tables()
        
        # Step 3: Create company
        logger.info("Creating company...")
        company = Company(
            company_name=setup_data.company_setup.company_name,
            company_email=setup_data.company_setup.company_email,
            company_phone=setup_data.company_setup.company_phone,
            company_address=setup_data.company_setup.company_address,
            company_city=setup_data.company_setup.company_city,
            company_state=setup_data.company_setup.company_state,
            company_country=setup_data.company_setup.company_country,
            company_pincode=setup_data.company_setup.company_pincode,
            company_gstin=setup_data.company_setup.company_gstin,
            company_website=setup_data.company_setup.company_website,
            currency=setup_data.company_setup.currency,
            timezone=setup_data.company_setup.timezone,
            is_active=True,
            created_at=datetime.now()
        )
        db.add(company)
        db.flush()  # Get company ID
        
        # Step 4: Create admin user
        logger.info("Creating admin user...")
        security_service = SecurityService()
        hashed_password = security_service.hash_password(setup_data.admin_user.password)
        
        admin_user = User(
            username=setup_data.admin_user.username,
            email=setup_data.admin_user.email,
            password_hash=hashed_password,
            first_name=setup_data.admin_user.first_name,
            last_name=setup_data.admin_user.last_name,
            phone=setup_data.admin_user.phone,
            is_active=True,
            is_superuser=True,
            is_staff=True,
            company_id=company.id,
            created_at=datetime.now()
        )
        db.add(admin_user)
        
        # Step 5: Create default roles and permissions
        logger.info("Creating default roles and permissions...")
        
        # Create superuser role
        superuser_role = Role(
            name="Superuser",
            description="Full system access",
            company_id=company.id,
            is_system_role=True
        )
        db.add(superuser_role)
        
        # Create admin role
        admin_role = Role(
            name="Administrator", 
            description="Administrative access",
            company_id=company.id,
            is_system_role=True
        )
        db.add(admin_role)
        
        # Create user role
        user_role = Role(
            name="User",
            description="Standard user access", 
            company_id=company.id,
            is_system_role=True
        )
        db.add(user_role)
        
        db.flush()
        
        # Assign superuser role to admin user
        from ...models.core import UserRole
        user_role_assignment = UserRole(
            user_id=admin_user.id,
            role_id=superuser_role.id,
            company_id=company.id
        )
        db.add(user_role_assignment)
        
        # Step 6: Initialize default data
        if setup_data.create_sample_data:
            logger.info("Loading sample data...")
            await initialize_default_data()
        
        db.commit()
        
        logger.info("Setup wizard completed successfully!")
        
        return {
            "success": True,
            "message": "Setup completed successfully!",
            "company_id": company.id,
            "admin_user_id": admin_user.id,
            "next_steps": [
                "Login with your admin credentials",
                "Configure your business settings",
                "Add your first customers and suppliers",
                "Set up your inventory items"
            ]
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Setup wizard failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Setup failed: {str(e)}"
        )

# Reset Setup (for development/testing)
@router.post("/reset-setup")
async def reset_setup():
    """Reset the entire setup (WARNING: This will delete all data!)"""
    try:
        # This is a dangerous operation - only allow in development
        from ...config import settings
        if not settings.debug:
            raise HTTPException(
                status_code=403,
                detail="Reset setup is only allowed in development mode"
            )
        
        # Drop all tables and recreate
        Base.metadata.drop_all(bind=engine)
        create_tables()
        
        logger.warning("Setup has been reset - all data deleted!")
        
        return {
            "success": True,
            "message": "Setup has been reset. You can now run the setup wizard again.",
            "warning": "All data has been deleted!"
        }
        
    except Exception as e:
        logger.error(f"Reset setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reset failed: {str(e)}"
        )