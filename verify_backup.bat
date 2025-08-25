:: verify_backup.bat - Verify backup integrity
@echo off
title ERP System - Verify Backup
color 09

echo ========================================
echo      ERP BACKUP VERIFICATION TOOL
echo ========================================
echo.

:: List available backups
echo Available backups:
echo ------------------

python -c "from backend.app.services.backup_service import backup_service; backups = backup_service.list_backups(); [print(f'{i+1}. {b[\"filename\"]} ({b[\"size_mb\"]} MB)') for i, b in enumerate(backups)]"

echo.
set /p choice="Enter backup number to verify (or 0 to cancel): "

if "%choice%"=="0" (
    echo Verification cancelled.
    pause
    exit /b 0
)

echo.
echo Verifying backup...

python -c "from backend.app.services.backup_service import backup_service; import json; backups = backup_service.list_backups(); choice = int('%choice%') - 1; result = backup_service.verify_backup(backups[choice]['path']); print(json.dumps(result, indent=2))"

echo.
pause