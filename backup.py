"""
Backup and Restore API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
import os

from ...services.backup_service import backup_service
from ...core.security import get_current_user
from ...core.rbac import require_role
from ...models.user import User

router = APIRouter()

# Request/Response Models
class BackupRequest(BaseModel):
    name: str = None
    include_logs: bool = False

class BackupResponse(BaseModel):
    success: bool
    backup_file: str = None
    size_mb: float = None
    timestamp: str = None
    error: str = None

class RestoreRequest(BaseModel):
    backup_file: str

class BackupInfo(BaseModel):
    filename: str
    path: str
    size_mb: float
    created: str
    metadata: dict = {}

# Endpoints
@router.post("/backup/create", response_model=BackupResponse)
async def create_backup(
    request: BackupRequest = BackupRequest(),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Create a new backup of the ERP system
    Requires admin or manager role
    """
    result = backup_service.create_backup(
        backup_name=request.name,
        include_logs=request.include_logs
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail=result.get('error', 'Backup failed'))
    
    return BackupResponse(**result)

@router.post("/backup/restore")
async def restore_backup(
    request: RestoreRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Restore from a backup file
    Requires admin role only
    """
    # Verify backup exists and is valid
    verify_result = backup_service.verify_backup(request.backup_file)
    
    if not verify_result['valid']:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid backup: {verify_result.get('error')}"
        )
    
    # Perform restore in background
    background_tasks.add_task(
        backup_service.restore_backup,
        request.backup_file
    )
    
    return {
        "message": "Restore initiated in background",
        "backup_file": request.backup_file
    }

@router.get("/backup/list", response_model=List[BackupInfo])
async def list_backups(
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    List all available backups
    """
    backups = backup_service.list_backups()
    return [BackupInfo(**b) for b in backups]

@router.get("/backup/download/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Download a backup file
    """
    from pathlib import Path
    
    backup_path = Path(backup_service.backup_dir) / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    return FileResponse(
        path=backup_path,
        filename=filename,
        media_type='application/zip'
    )

@router.delete("/backup/{filename}")
async def delete_backup(
    filename: str,
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Delete a backup file
    """
    from pathlib import Path
    
    backup_path = Path(backup_service.backup_dir) / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    try:
        backup_path.unlink()
        return {"message": f"Backup {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup/verify")
async def verify_backup(
    request: RestoreRequest,
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """
    Verify backup file integrity
    """
    result = backup_service.verify_backup(request.backup_file)
    
    if not result['valid']:
        return {
            "valid": False,
            "error": result.get('error')
        }
    
    return {
        "valid": True,
        "metadata": result.get('metadata'),
        "file_count": result.get('files')
    }

# Scheduled backup endpoint (for manual trigger)
@router.post("/backup/schedule")
async def trigger_scheduled_backup(
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Manually trigger the scheduled backup
    """
    result = backup_service.create_backup(
        backup_name=f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    if not result['success']:
        raise HTTPException(status_code=500, detail="Scheduled backup failed")
    
    return {
        "message": "Scheduled backup completed",
        "backup_file": result['backup_file']
    }