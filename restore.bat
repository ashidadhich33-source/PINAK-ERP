:: restore.bat - Restore from backup
@echo off
title ERP System - Restore Backup
color 0E

echo ========================================
echo       ERP SYSTEM RESTORE UTILITY
echo ========================================
echo.
echo WARNING: This will replace all current data!
echo.

:: List available backups
echo Available backups:
echo ------------------

python -c "from backend.app.services.backup_service import backup_service; backups = backup_service.list_backups(); [print(f'{i+1}. {b[\"filename\"]} ({b[\"size_mb\"]} MB)') for i, b in enumerate(backups)]"

echo.
set /p choice="Enter backup number to restore (or 0 to cancel): "

if "%choice%"=="0" (
    echo Restore cancelled.
    pause
    exit /b 0
)

:: Confirm restore
echo.
set /p confirm="Are you sure you want to restore? (yes/no): "

if not "%confirm%"=="yes" (
    echo Restore cancelled.
    pause
    exit /b 0
)

:: Perform restore
echo.
echo Restoring backup...

python -c "from backend.app.services.backup_service import backup_service; backups = backup_service.list_backups(); choice = int('%choice%') - 1; result = backup_service.restore_backup(backups[choice]['path']); print('Restore completed!' if result['success'] else f'Restore failed: {result.get(\"error\")}')"

echo.
pause

:: ============================================