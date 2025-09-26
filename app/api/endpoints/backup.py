# backend/app/api/endpoints/backup.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from ..database import get_db
from ...models.user import User
from ...core.security import get_current_user
from ...services.backup_service import backup_service
from ...config import settings

router = APIRouter()

@router.post("/create")
async def create_backup(
    backup_name: str = None,
    current_user: User = Depends(get_current_user)
):
    """Create a new backup"""
    try:
        if not current_user.is_superuser and not current_user.has_permission("backup.create"):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        result = backup_service.create_backup(backup_name)

        if result['success']:
            return {
                "message": "Backup created successfully",
                "backup_file": result['backup_file'],
                "size_mb": result['size_mb']
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Backup failed'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_backups(
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """List all available backups"""
    try:
        if not current_user.is_superuser and not current_user.has_permission("backup.view"):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        backups = backup_service.list_backups()
        return backups

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_backup(
    backup_file: str,
    current_user: User = Depends(get_current_user)
):
    """Restore from backup"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only superusers can restore backups")

        result = backup_service.restore_backup(backup_file)

        if result['success']:
            return {
                "message": "Backup restored successfully",
                "restored_from": backup_file
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Restore failed'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{backup_file}")
async def download_backup(
    backup_file: str,
    current_user: User = Depends(get_current_user)
):
    """Download a backup file"""
    try:
        if not current_user.is_superuser and not current_user.has_permission("backup.download"):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        # Find the backup file
        backup_path = Path(settings.backup_location) / backup_file

        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup file not found")

        return FileResponse(
            path=backup_path,
            filename=backup_file,
            media_type="application/octet-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{backup_file}")
async def delete_backup(
    backup_file: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a backup file"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Only superusers can delete backups")

        result = backup_service.delete_backup(backup_file)

        if result['success']:
            return {"message": f"Backup {backup_file} deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Delete failed'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def backup_status(
    current_user: User = Depends(get_current_user)
):
    """Get backup system status"""
    try:
        if not current_user.is_superuser and not current_user.has_permission("backup.view"):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        status_info = {
            "enabled": settings.backup_enabled,
            "schedule": settings.backup_schedule,
            "backup_time": settings.backup_time,
            "retention_days": settings.backup_retention_days,
            "location": settings.backup_location,
            "last_backup": None,
            "next_backup": None,
            "total_backups": 0
        }

        # Get backup information
        try:
            backups = backup_service.list_backups()
            status_info["total_backups"] = len(backups)

            if backups:
                status_info["last_backup"] = backups[0]

                # Calculate next backup time
                from datetime import datetime, time as dt_time, timedelta
                now = datetime.now()
                backup_hour, backup_minute = map(int, settings.backup_time.split(':'))
                target_time = datetime.combine(now.date(), dt_time(backup_hour, backup_minute))

                if now > target_time:
                    target_time = datetime.combine(
                        now.date() + timedelta(days=1),
                        dt_time(backup_hour, backup_minute)
                    )

                status_info["next_backup"] = target_time.isoformat()

        except Exception as e:
            logger.error(f"Error getting backup status: {e}")

        return status_info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))