# backend/app/services/core/backup_service.py
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

from ...config import settings

logger = logging.getLogger(__name__)

class BackupService:
    """Service for managing database backups"""
    
    def __init__(self):
        self.backup_dir = Path(settings.backup_location)
        self.backup_dir.mkdir(exist_ok=True, parents=True)
    
    def create_backup(self, backup_name: str = None) -> Dict[str, Any]:
        """Create a new database backup"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if settings.database_type == "sqlite":
                return self._create_sqlite_backup(backup_name)
            elif settings.database_type == "postgresql":
                return self._create_postgresql_backup(backup_name)
            else:
                raise ValueError(f"Unsupported database type: {settings.database_type}")
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_sqlite_backup(self, backup_name: str) -> Dict[str, Any]:
        """Create SQLite backup"""
        try:
            source_path = Path(settings.sqlite_path)
            if not source_path.exists():
                raise FileNotFoundError(f"Database file not found: {source_path}")
            
            backup_filename = f"{backup_name}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Copy database file
            shutil.copy2(source_path, backup_path)
            
            # Get file size
            file_size = backup_path.stat().st_size
            
            logger.info(f"SQLite backup created: {backup_path}")
            
            return {
                "success": True,
                "backup_file": str(backup_path),
                "backup_name": backup_name,
                "size": file_size,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SQLite backup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_postgresql_backup(self, backup_name: str) -> Dict[str, Any]:
        """Create PostgreSQL backup"""
        try:
            import subprocess
            from urllib.parse import urlparse
            
            parsed = urlparse(settings.database_url)
            backup_filename = f"{backup_name}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Create pg_dump command
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
            
            # Run pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
            
            # Get file size
            file_size = backup_path.stat().st_size
            
            logger.info(f"PostgreSQL backup created: {backup_path}")
            
            return {
                "success": True,
                "backup_file": str(backup_path),
                "backup_name": backup_name,
                "size": file_size,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.db"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            for backup_file in self.backup_dir.glob("*.sql"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    backups.append({
                        "filename": backup_file.name,
                        "path": str(backup_file),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """Restore from a backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            if settings.database_type == "sqlite":
                return self._restore_sqlite_backup(backup_file)
            elif settings.database_type == "postgresql":
                return self._restore_postgresql_backup(backup_file)
            else:
                raise ValueError(f"Unsupported database type: {settings.database_type}")
                
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _restore_sqlite_backup(self, backup_file: Path) -> Dict[str, Any]:
        """Restore SQLite backup"""
        try:
            source_path = Path(settings.sqlite_path)
            
            # Create backup of current database
            current_backup = source_path.with_suffix(f".backup_{int(time.time())}")
            if source_path.exists():
                shutil.copy2(source_path, current_backup)
            
            # Restore from backup
            shutil.copy2(backup_file, source_path)
            
            logger.info(f"SQLite backup restored from: {backup_file}")
            
            return {
                "success": True,
                "message": "Database restored successfully",
                "backup_file": str(backup_file)
            }
            
        except Exception as e:
            logger.error(f"SQLite restore failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _restore_postgresql_backup(self, backup_file: Path) -> Dict[str, Any]:
        """Restore PostgreSQL backup"""
        try:
            import subprocess
            from urllib.parse import urlparse
            
            parsed = urlparse(settings.database_url)
            
            # Create psql command
            cmd = [
                'psql',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path.lstrip('/'),
                '-f', str(backup_file)
            ]
            
            env = {'PGPASSWORD': parsed.password} if parsed.password else {}
            
            # Run psql
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"psql restore failed: {result.stderr}")
            
            logger.info(f"PostgreSQL backup restored from: {backup_file}")
            
            return {
                "success": True,
                "message": "Database restored successfully",
                "backup_file": str(backup_file)
            }
            
        except Exception as e:
            logger.error(f"PostgreSQL restore failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_backup(self, backup_path: str) -> Dict[str, Any]:
        """Delete a backup file"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            backup_file.unlink()
            
            logger.info(f"Backup deleted: {backup_path}")
            
            return {
                "success": True,
                "message": "Backup deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Backup deletion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup_old_backups(self, days_to_keep: int = 7) -> Dict[str, Any]:
        """Clean up old backups"""
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*"):
                if backup_file.is_file() and backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            
            return {
                "success": True,
                "message": f"Cleaned up {deleted_count} old backups",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Create service instance
backup_service = BackupService()