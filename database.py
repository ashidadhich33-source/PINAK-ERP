# backend/app/database.py
from sqlalchemy import create_engine, MetaData, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool, QueuePool
from contextlib import contextmanager
import logging
from pathlib import Path
from typing import Generator, Dict, Any
import asyncio
import time

from .config import settings

logger = logging.getLogger(__name__)

# Create database directory if using SQLite
if settings.database_type == "sqlite":
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(exist_ok=True, parents=True)

def create_database_engine():
    """Create database engine with optimized configuration"""
    
    if settings.database_type == "sqlite":
        # SQLite specific settings
        engine = create_engine(
            settings.database_url,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
                "isolation_level": None,  # Use autocommit mode
            },
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=settings.debug and False,  # Set to True for SQL debugging
            future=True
        )
        
        # SQLite optimization pragmas
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys=ON")
            # Use WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            # Optimize SQLite performance
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            cursor.close()
            
    elif settings.database_type == "postgresql":
        # PostgreSQL specific settings
        engine = create_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
            poolclass=QueuePool,
            echo=settings.debug and False,
            future=True,
            connect_args={
                "sslmode": "prefer",
                "connect_timeout": 30,
            }
        )
    else:
        # Default configuration
        engine = create_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=settings.debug and False,
            future=True
        )
    
    return engine

# Create engine
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Connection health check
class DatabaseHealthCheck:
    """Database connection health monitoring"""
    
    @staticmethod
    def check_connection() -> bool:
        """Test database connection"""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info() -> Dict[str, Any]:
        """Get database connection information"""
        try:
            with engine.connect() as conn:
                if settings.database_type == "sqlite":
                    result = conn.execute(text("SELECT sqlite_version()")).scalar()
                    return {
                        "type": "SQLite",
                        "version": result,
                        "file_size_mb": get_database_size(),
                        "status": "connected"
                    }
                elif settings.database_type == "postgresql":
                    result = conn.execute(text("SELECT version()")).scalar()
                    return {
                        "type": "PostgreSQL", 
                        "version": result,
                        "status": "connected"
                    }
        except Exception as e:
            return {
                "type": settings.database_type,
                "status": "error",
                "error": str(e)
            }

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup
    Includes retry logic and connection validation
    """
    db = SessionLocal()
    try:
        # Test connection before yielding
        db.execute(text("SELECT 1"))
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
    Context manager for database session with automatic transaction management
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Async context manager for database session
class AsyncDatabaseSession:
    """Async database session manager"""
    
    def __init__(self):
        self.db = None
    
    async def __aenter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()

# Database initialization functions
def create_tables():
    """Create all tables in the database"""
    try:
        # Import all models to ensure they're registered
        from . import models
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

def drop_tables():
    """Drop all tables from the database (use with caution!)"""
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped")
    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        raise

def init_db():
    """Initialize database with tables and default data"""
    try:
        # Create tables
        create_tables()
        
        # Initialize default data
        logger.info("Initializing default data...")
        from .core.init_data import init_default_data
        with get_db_session() as db:
            init_default_data(db)
        
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

def check_database_connection() -> bool:
    """Check if database connection is working"""
    return DatabaseHealthCheck.check_connection()

def get_database_info() -> Dict[str, Any]:
    """Get comprehensive database information"""
    return DatabaseHealthCheck.get_connection_info()

def get_database_size() -> float:
    """Get database size in MB"""
    try:
        if settings.database_type == "sqlite":
            db_path = Path(settings.sqlite_path)
            if db_path.exists():
                return db_path.stat().st_size / (1024 * 1024)
        elif settings.database_type == "postgresql":
            with engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT pg_database_size('{settings.postgres_db}') / 1024 / 1024 as size")
                )
                return result.scalar()
        return 0
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return 0

def vacuum_database():
    """Optimize database performance"""
    try:
        logger.info("Starting database optimization...")
        
        if settings.database_type == "sqlite":
            with engine.connect() as conn:
                conn.execute(text("VACUUM"))
                conn.execute(text("ANALYZE"))
                logger.info("SQLite database optimized")
                
        elif settings.database_type == "postgresql":
            # PostgreSQL VACUUM needs to be run outside transaction
            with engine.connect() as conn:
                conn.connection.set_isolation_level(0)  # Autocommit mode
                conn.execute(text("VACUUM ANALYZE"))
                logger.info("PostgreSQL database optimized")
                
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise

def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        stats = {
            "size_mb": get_database_size(),
            "connection_info": get_database_info(),
            "tables": []
        }
        
        with engine.connect() as conn:
            if settings.database_type == "sqlite":
                # Get table information for SQLite
                result = conn.execute(text("""
                    SELECT name, 
                           (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count
                    FROM sqlite_master m 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """))
                
                for row in result:
                    # Get actual row count
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM {row.name}"))
                    row_count = count_result.scalar()
                    
                    stats["tables"].append({
                        "name": row.name,
                        "rows": row_count
                    })
                    
            elif settings.database_type == "postgresql":
                # Get table information for PostgreSQL
                result = conn.execute(text("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables
                """))
                
                for row in result:
                    stats["tables"].append({
                        "name": row.tablename,
                        "schema": row.schemaname,
                        "inserts": row.n_tup_ins,
                        "updates": row.n_tup_upd,
                        "deletes": row.n_tup_del
                    })
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {"error": str(e)}

def create_backup():
    """Create database backup"""
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if settings.database_type == "sqlite":
            import shutil
            source = Path(settings.sqlite_path)
            backup_path = backup_dir / f"erp_backup_{timestamp}.db"
            shutil.copy2(source, backup_path)
            logger.info(f"SQLite backup created: {backup_path}")
            return str(backup_path)
            
        elif settings.database_type == "postgresql":
            import subprocess
            from urllib.parse import urlparse
            
            parsed = urlparse(settings.database_url)
            backup_path = backup_dir / f"erp_backup_{timestamp}.sql"
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path.lstrip('/'),
                '-f', str(backup_path),
                '--no-owner',
                '--verbose'
            ]
            
            env = {'PGPASSWORD': parsed.password} if parsed.password else {}
            
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"PostgreSQL backup created: {backup_path}")
            return str(backup_path)
            
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise

# Connection pool monitoring
def get_pool_status() -> Dict[str, Any]:
    """Get connection pool status"""
    try:
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.checkedin() + pool.checkedout()
        }
    except Exception as e:
        return {"error": str(e)}

# Database migration utilities
def run_migrations():
    """Run pending database migrations"""
    try:
        import subprocess
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Database migrations completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Migration failed: {e.stderr}")
        raise
    except FileNotFoundError:
        logger.warning("Alembic not found, skipping migrations")
        return "Alembic not available"

# Performance monitoring
class DatabasePerformanceMonitor:
    """Monitor database performance metrics"""
    
    @staticmethod
    def get_slow_queries():
        """Get slow query information (PostgreSQL only)"""
        if settings.database_type != "postgresql":
            return {"message": "Slow query monitoring only available for PostgreSQL"}
        
        try:
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT query, calls, total_time, mean_time
                    FROM pg_stat_statements
                    WHERE mean_time > 100
                    ORDER BY mean_time DESC
                    LIMIT 10
                """))
                
                return [
                    {
                        "query": row.query[:100] + "..." if len(row.query) > 100 else row.query,
                        "calls": row.calls,
                        "total_time": row.total_time,
                        "mean_time": row.mean_time
                    }
                    for row in result
                ]
        except Exception as e:
            return {"error": str(e)}

# Export commonly used objects
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "metadata",
    "get_db",
    "get_db_session",
    "AsyncDatabaseSession",
    "create_tables",
    "drop_tables", 
    "init_db",
    "check_database_connection",
    "get_database_info",
    "get_database_size",
    "get_database_stats",
    "vacuum_database",
    "create_backup",
    "get_pool_status",
    "run_migrations",
    "DatabasePerformanceMonitor"
]
