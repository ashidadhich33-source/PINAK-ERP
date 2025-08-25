# backend/app/database.py
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Generator

from .config import settings

logger = logging.getLogger(__name__)

# Create database directory if using SQLite
if settings.database_type == "sqlite":
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(exist_ok=True, parents=True)

# Configure engine based on database type
if settings.database_type == "sqlite":
    # SQLite specific settings
    engine = create_engine(
        settings.database_url,
        connect_args={
            "check_same_thread": False,  # Allow multiple threads
            "timeout": 30,  # Connection timeout in seconds
        },
        poolclass=StaticPool,  # Use StaticPool for SQLite
        echo=settings.debug,  # Log SQL statements in debug mode
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
        cursor.close()
        
elif settings.database_type == "postgresql":
    # PostgreSQL specific settings
    engine = create_engine(
        settings.database_url,
        pool_size=20,  # Number of connections to maintain in pool
        max_overflow=40,  # Maximum overflow connections
        pool_pre_ping=True,  # Test connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.debug,
    )
else:
    # Default configuration
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.debug,
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Don't expire objects after commit
)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    Yields session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Context manager for database session
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database session.
    Usage: 
        with get_db_session() as db:
            # do something with db
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database initialization functions
def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise

def drop_tables():
    """Drop all tables from the database (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise

def init_db():
    """Initialize database with tables and default data"""
    try:
        # Create tables
        create_tables()
        
        # Initialize default data
        from .core.init_data import init_default_data
        with get_db_session() as db:
            init_default_data(db)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def get_database_size() -> float:
    """Get database size in MB"""
    try:
        if settings.database_type == "sqlite":
            db_path = Path(settings.sqlite_path)
            if db_path.exists():
                return db_path.stat().st_size / (1024 * 1024)  # Convert to MB
        elif settings.database_type == "postgresql":
            with engine.connect() as conn:
                result = conn.execute(
                    f"SELECT pg_database_size('{settings.postgres_db}') / 1024 / 1024 as size"
                )
                return result.scalar()
        return 0
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return 0

def vacuum_database():
    """Optimize database (vacuum for SQLite, VACUUM ANALYZE for PostgreSQL)"""
    try:
        if settings.database_type == "sqlite":
            with engine.connect() as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
        elif settings.database_type == "postgresql":
            with engine.connect() as conn:
                conn.execute("VACUUM ANALYZE")
        logger.info("Database optimized successfully")
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise

# Export commonly used objects
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "metadata",
    "get_db",
    "get_db_session",
    "create_tables",
    "drop_tables",
    "init_db",
    "check_database_connection",
    "get_database_size",
    "vacuum_database",
]
