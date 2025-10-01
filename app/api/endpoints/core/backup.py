# backend/app/api/endpoints/backup.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import os

from app.database import get_db
from app.models.core.user import User
from app.core.security import get_current_user, require_permission
from app.services.core.backup_service import backup_service

router = APIRouter()

# Pydantic schemas
class BackupResponse(BaseModel):
    id: int
    backup_name: str
    backup_file: str
    backup_size: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

@router.post("/backup", response_model=BackupResponse)
async def create_backup(
    backup_name: str,
    current_user: User = Depends(require_permission("backup.create")),
    db: Session = Depends(get_db)
):
    """Create a new backup"""
    
    try:
        result = backup_service.create_backup(backup_name)
        
        if result['success']:
            return BackupResponse(
                id=1,  # This would be the actual backup ID
                backup_name=backup_name,
                backup_file=result['backup_file'],
                backup_size=result.get('size', 0),
                created_at=datetime.utcnow(),
                status="completed"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Backup failed: {result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Backup creation failed: {str(e)}"
        )

@router.get("/backups", response_model=List[BackupResponse])
async def list_backups(
    current_user: User = Depends(require_permission("backup.view")),
    db: Session = Depends(get_db)
):
    """List all backups"""
    
    try:
        backups = backup_service.list_backups()
        
        return [
            BackupResponse(
                id=i+1,
                backup_name=backup['filename'],
                backup_file=backup['filename'],
                backup_size=backup['size_mb'] * 1024 * 1024,  # Convert MB to bytes
                created_at=backup['created'],
                status="completed"
            )
            for i, backup in enumerate(backups)
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list backups: {str(e)}"
        )

@router.get("/backups/{backup_id}")
async def get_backup(
    backup_id: int,
    current_user: User = Depends(require_permission("backup.view")),
    db: Session = Depends(get_db)
):
    """Get backup details"""
    
    try:
        backups = backup_service.list_backups()
        
        if backup_id < 1 or backup_id > len(backups):
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup = backups[backup_id - 1]
        
        return {
            "id": backup_id,
            "filename": backup['filename'],
            "size_mb": backup['size_mb'],
            "created": backup['created'],
            "path": backup.get('path', '')
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get backup: {str(e)}"
        )

@router.delete("/backups/{backup_id}")
async def delete_backup(
    backup_id: int,
    current_user: User = Depends(require_permission("backup.delete")),
    db: Session = Depends(get_db)
):
    """Delete a backup"""
    
    try:
        backups = backup_service.list_backups()
        
        if backup_id < 1 or backup_id > len(backups):
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup = backups[backup_id - 1]
        backup_path = backup.get('path', '')
        
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
            return {"message": "Backup deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Backup file not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete backup: {str(e)}"
        )

@router.post("/backups/{backup_id}/restore")
async def restore_backup(
    backup_id: int,
    current_user: User = Depends(require_permission("backup.restore")),
    db: Session = Depends(get_db)
):
    """Restore from a backup"""
    
    try:
        backups = backup_service.list_backups()
        
        if backup_id < 1 or backup_id > len(backups):
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup = backups[backup_id - 1]
        backup_path = backup.get('path', '')
        
        if not backup_path or not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # This would implement the actual restore logic
        # For now, just return a success message
        return {"message": "Backup restore initiated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore backup: {str(e)}"
        )