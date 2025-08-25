:: auto_backup.bat - Setup scheduled backup
@echo off
title ERP System - Scheduled Backup Setup
color 0B

echo ========================================
echo    ERP SCHEDULED BACKUP CONFIGURATION
echo ========================================
echo.

echo This will create a Windows Task Scheduler entry
echo for daily automatic backups at 2:00 AM
echo.

set /p setup="Do you want to set up automatic backups? (yes/no): "

if not "%setup%"=="yes" (
    echo Setup cancelled.
    pause
    exit /b 0
)

:: Create scheduled task
set TASK_NAME=ERPSystemBackup
set BACKUP_TIME=02:00
set BACKUP_SCRIPT=%cd%\scheduled_backup.vbs

:: Create VBScript for silent execution
echo Set objShell = CreateObject("WScript.Shell") > %BACKUP_SCRIPT%
echo objShell.Run "cmd /c cd /d %cd% && venv\Scripts\python.exe -c ""from backend.app.services.backup_service import backup_service; backup_service.create_backup()""", 0, True >> %BACKUP_SCRIPT%

:: Create Windows scheduled task
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe %BACKUP_SCRIPT%" /sc daily /st %BACKUP_TIME% /f

if errorlevel 1 (
    echo [ERROR] Failed to create scheduled task
    del %BACKUP_SCRIPT%
) else (
    echo [SUCCESS] Scheduled backup configured!
    echo.
    echo Backup will run daily at %BACKUP_TIME%
    echo Task name: %TASK_NAME%
    echo.
    echo To manage this task:
    echo - View: schtasks /query /tn "%TASK_NAME%"
    echo - Delete: schtasks /delete /tn "%TASK_NAME%"
    echo - Run now: schtasks /run /tn "%TASK_NAME%"
)

echo.
pause

:: ============================================