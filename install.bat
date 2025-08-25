```batch
@echo off
echo Installing ERP System...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9+
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r backend\requirements.txt

REM Create necessary directories
mkdir database 2>nul
mkdir logs 2>nul
mkdir uploads 2>nul
mkdir config 2>nul

REM Initialize database
echo Setting up database...
cd backend
alembic upgrade head
cd ..

echo Installation complete!
echo Run 'run.bat' to start the application
pause
```