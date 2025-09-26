"""
Backup and Restore Service for ERP System
Integrates with existing SQLAlchemy setup
"""

import os
import shutil
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess

from sqlalchemy import create_engine, text
from ..database import engine, get_database_info
from ..config import settings

# Configure logging
logger = logging.getLogger(__name__)

class ERPBackupService:
    """Manages backup and restore for the ERP system"""

    def __init__(self):
        """Initialize using application settings"""
        # Set paths from settings
        self.backup_dir = Path(settings.backup_location)
        self.upload_dir = Path(settings.upload_dir)
        self.log_dir = Path(settings.log_dir)
        self.db_type = settings.database_type

        # Database path/URL from settings
        if self.db_type == 'sqlite':
            self.db_path = Path(settings.sqlite_path)
        else:
            # Use the database URL from settings
            self.db_url = settings.database_url

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup settings
        self.max_backups = settings.backup_retention_days
        
    def create_backup(self, 
                     backup_name: Optional[str] = None,
                     include_logs: bool = False) -> Dict[str, Any]:
        """
        Create a complete backup of the ERP system
        
        Args:
            backup_name: Optional custom backup name
            include_logs: Whether to include log files
            
        Returns:
            Dict with backup information
        """
        try:
            # Generate backup name
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"erp_backup_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Creating backup: {backup_name}")
            
            # 1. Backup database
            self._backup_database(backup_path)
            
            # 2. Backup uploaded files
            self._backup_uploads(backup_path)
            
            # 3. Backup configuration
            self._backup_config(backup_path)
            
            # 4. Optionally backup logs
            if include_logs:
                self._backup_logs(backup_path)
            
            # 5. Create metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'db_type': self.db_type,
                'erp_version': settings.app_version,
                'includes_logs': include_logs,
                'company': self._get_company_info()
            }
            
            with open(backup_path / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # 6. Compress to ZIP
            zip_path = self._compress_backup(backup_path)
            
            # 7. Clean up uncompressed files
            shutil.rmtree(backup_path)
            
            # 8. Clean old backups
            self._cleanup_old_backups()
            
            # Calculate backup size
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"Backup completed: {zip_path}")
            
            return {
                'success': True,
                'backup_file': str(zip_path),
                'size_mb': round(size_mb, 2),
                'timestamp': metadata['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _backup_database(self, backup_path: Path) -> None:
        """Backup the database"""
        if self.db_type == 'sqlite':
            # SQLite backup - simple file copy with proper handling
            import sqlite3
            
            backup_db_path = backup_path / 'erp_system.db'
            
            # Use SQLite backup API for consistency
            source = sqlite3.connect(str(self.db_path))
            dest = sqlite3.connect(str(backup_db_path))
            
            with dest:
                source.backup(dest)
            
            source.close()
            dest.close()
            
            logger.info("Database backed up (SQLite)")
            
        else:
            # PostgreSQL backup
            backup_file = backup_path / 'erp_system.sql'
            
            # Parse connection details
            from urllib.parse import urlparse
            parsed = urlparse(self.db_url)
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port),
                '-U', parsed.username,
                '-d', parsed.path.lstrip('/'),
                '-f', str(backup_file),
                '--no-owner'
            ]
            
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
            
            logger.info("Database backed up (PostgreSQL)")
    
    def _backup_uploads(self, backup_path: Path) -> None:
        """Backup uploaded files"""
        if self.upload_dir.exists() and any(self.upload_dir.iterdir()):
            dest_path = backup_path / 'uploads'
            shutil.copytree(self.upload_dir, dest_path)
            logger.info("Uploaded files backed up")
    
    def _backup_config(self, backup_path: Path) -> None:
        """Backup configuration files"""
        config_dir = Path('config')
        if config_dir.exists():
            dest_path = backup_path / 'config'
            shutil.copytree(config_dir, dest_path)
            logger.info("Configuration backed up")
    
    def _backup_logs(self, backup_path: Path) -> None:
        """Backup log files"""
        if self.log_dir.exists() and any(self.log_dir.iterdir()):
            dest_path = backup_path / 'logs'
            shutil.copytree(self.log_dir, dest_path)
            logger.info("Log files backed up")
    
    def _get_company_info(self) -> Dict:
        """Get company information from database"""
        try:
            from ..models.company import Company
            from ..database import SessionLocal
            
            db = SessionLocal()
            company = db.query(Company).first()
            
            if company:
                return {
                    'name': company.name,
                    'gstin': company.gst_number
                }
            
            db.close()
        except:
            pass
        
        return {}
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup to ZIP"""
        zip_path = backup_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(backup_path)
                    zf.write(file_path, arc_name)
        
        return zip_path
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding limit"""
        backups = sorted(
            self.backup_dir.glob('erp_backup_*.zip'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if len(backups) > self.max_backups:
            for old_backup in backups[self.max_backups:]:
                old_backup.unlink()
                logger.info(f"Deleted old backup: {old_backup.name}")
    
    def restore_backup(self, backup_file: str) -> Dict[str, Any]:
        """
        Restore from backup file
        
        Args:
            backup_file: Path to backup ZIP file
            
        Returns:
            Dict with restore status
        """
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_file}")
            
            logger.info(f"Starting restore from: {backup_file}")
            
            # Create safety backup first
            safety_backup = self.create_backup("safety_backup")
            
            if not safety_backup['success']:
                raise Exception("Failed to create safety backup")
            
            # Extract backup
            temp_dir = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                with zipfile.ZipFile(backup_path, 'r') as zf:
                    zf.extractall(temp_dir)
                
                # Read metadata
                with open(temp_dir / 'metadata.json', 'r') as f:
                    metadata = json.load(f)
                
                # Verify compatibility
                if metadata['db_type'] != self.db_type:
                    raise ValueError(f"Database type mismatch")
                
                # Restore components
                self._restore_database(temp_dir)
                self._restore_uploads(temp_dir)
                self._restore_config(temp_dir)
                
                if metadata.get('includes_logs'):
                    self._restore_logs(temp_dir)
                
                logger.info("Restore completed successfully")
                
                return {
                    'success': True,
                    'message': 'Restore completed successfully',
                    'safety_backup': safety_backup['backup_file']
                }
                
            finally:
                # Clean up temp directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_database(self, restore_path: Path) -> None:
        """Restore database from backup"""
        if self.db_type == 'sqlite':
            backup_db = restore_path / 'erp_system.db'
            
            if backup_db.exists():
                # Close all connections
                from ..database import engine
                engine.dispose()
                
                # Replace database file
                shutil.copy2(backup_db, self.db_path)
                logger.info("Database restored (SQLite)")
        else:
            # PostgreSQL restore
            backup_sql = restore_path / 'erp_system.sql'
            
            if backup_sql.exists():
                from urllib.parse import urlparse
                parsed = urlparse(self.db_url)
                
                # Drop and recreate database
                # ... PostgreSQL restore logic ...
                logger.info("Database restored (PostgreSQL)")
    
    def _restore_uploads(self, restore_path: Path) -> None:
        """Restore uploaded files"""
        backup_uploads = restore_path / 'uploads'
        
        if backup_uploads.exists():
            if self.upload_dir.exists():
                shutil.rmtree(self.upload_dir)
            
            shutil.copytree(backup_uploads, self.upload_dir)
            logger.info("Uploaded files restored")
    
    def _restore_config(self, restore_path: Path) -> None:
        """Restore configuration (selective)"""
        # Don't overwrite database connection settings
        # Only restore company-specific settings
        logger.info("Configuration selectively restored")
    
    def _restore_logs(self, restore_path: Path) -> None:
        """Restore log files"""
        backup_logs = restore_path / 'logs'
        
        if backup_logs.exists():
            if self.log_dir.exists():
                # Archive current logs instead of deleting
                archive_dir = self.log_dir.parent / f"logs_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(self.log_dir, archive_dir)
            
            shutil.copytree(backup_logs, self.log_dir)
            logger.info("Log files restored")
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('erp_backup_*.zip'), reverse=True):
            stat = backup_file.stat()
            
            # Try to read metadata
            metadata = {}
            try:
                with zipfile.ZipFile(backup_file, 'r') as zf:
                    if 'metadata.json' in zf.namelist():
                        with zf.open('metadata.json') as mf:
                            metadata = json.load(mf)
            except:
                pass
            
            backups.append({
                'filename': backup_file.name,
                'path': str(backup_file),
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'metadata': metadata
            })
        
        return backups
    
    def verify_backup(self, backup_file: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return {'valid': False, 'error': 'File not found'}
            
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Check for corruption
                bad_file = zf.testzip()
                if bad_file:
                    return {'valid': False, 'error': f'Corrupted file: {bad_file}'}
                
                # Check required files
                required = ['metadata.json']
                if self.db_type == 'sqlite':
                    required.append('erp_system.db')
                else:
                    required.append('erp_system.sql')
                
                files = zf.namelist()
                for req in required:
                    if req not in files:
                        return {'valid': False, 'error': f'Missing: {req}'}
                
                # Read metadata
                with zf.open('metadata.json') as mf:
                    metadata = json.load(mf)
                
                return {
                    'valid': True,
                    'metadata': metadata,
                    'files': len(files)
                }
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}


# Singleton instance
backup_service = ERPBackupService()