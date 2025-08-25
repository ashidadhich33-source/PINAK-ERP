@echo off
title ERP System - Create Backup
color 0A

echo ========================================
echo         ERP SYSTEM BACKUP UTILITY
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    pause
    exit /b 1
)

:: Run backup script
echo Creating backup...
echo.

python -c "from backend.app.services.backup_service import backup_service; import json; result = backup_service.create_backup(); print(json.dumps(result, indent=2))"

if errorlevel 1 (
    echo.
    echo [ERROR] Backup failed!
) else (
    echo.
    echo [SUCCESS] Backup completed successfully!
)

echo.
pause

:: ============================================