# backend/run.py
import uvicorn
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.config import settings
from app.main import app

if __name__ == "__main__":
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 Server: http://{settings.host}:{settings.port}")
    print(f"📚 API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"🔒 Admin Login: username=admin, password=admin123")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level="info"
    )

# requirements.txt
"""
# Core FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Authentication & Security  
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Data Processing
pandas==2.1.3
openpyxl==3.1.2
xlsxwriter==3.1.9

# PDF Generation
reportlab==4.0.7

# HTTP Requests
requests==2.31.0
httpx==0.25.2

# Validation
pydantic==2.5.2
pydantic-settings==2.0.3
email-validator==2.1.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Barcode Generation
python-barcode==0.15.1
pillow==10.1.0

# Windows specific
pywin32==306; sys_platform == "win32"

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
"""

# install.bat - Windows Installation Script
install_script = '''@echo off
echo Installing ERP System...
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\\Scripts\\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
mkdir database 2>nul
mkdir logs 2>nul
mkdir uploads 2>nul
mkdir config 2>nul
mkdir backups 2>nul

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📄 Creating .env file...
    echo SECRET_KEY=your-secret-key-change-in-production > .env
    echo DEBUG=True >> .env
    echo DATABASE_URL=sqlite:///./database/erp_system.db >> .env
)

echo.
echo ✅ Installation complete!
echo.
echo To start the application:
echo   1. Run: run.bat
echo   2. Open browser: http://localhost:8000
echo   3. API Docs: http://localhost:8000/docs
echo   4. Login with: admin / admin123
echo.
pause
'''

# run.bat - Windows Run Script
run_script = '''@echo off
echo Starting ERP System...
echo.

REM Check if virtual environment exists
if not exist venv\\Scripts\\activate.bat (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Run the application
python run.py

pause
'''

# .env template
env_template = '''# ERP System Configuration

# Security
SECRET_KEY=your-secret-key-change-in-production-this-should-be-very-long-and-random
DEBUG=True

# Database
DATABASE_URL=sqlite:///./database/erp_system.db

# Server
HOST=127.0.0.1
PORT=8000

# Company Information
COMPANY_NAME=Your Company Name
COMPANY_EMAIL=info@company.com
COMPANY_PHONE=1234567890

# WhatsApp Cloud API (Optional)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_BUSINESS_ACCOUNT_ID=

# GST Settings
GST_ENABLED=true
DEFAULT_GST_RATE=18.0

# File Paths
UPLOAD_DIR=uploads
LOG_DIR=logs
BACKUP_DIR=backups
'''

# Project structure creation script
def create_project_structure():
    """Create the complete project directory structure"""
    
    directories = [
        "backend/app",
        "backend/app/api/endpoints", 
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services", 
        "backend/app/core",
        "backend/app/utils",
        "backend/migrations/alembic",
        "backend/tests",
        "frontend/src/main",
        "frontend/src/renderer/components",
        "frontend/src/renderer/pages", 
        "frontend/src/renderer/services",
        "frontend/src/assets",
        "database",
        "logs",
        "uploads", 
        "config",
        "backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if 'backend/app' in directory and not directory.endswith('tests'):
            init_file = Path(directory) / "__init__.py" 
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Project structure created successfully!")

if __name__ == "__main__":
    print("🏗️  Creating ERP System project structure...")
    create_project_structure()
    
    # Write batch files
    with open("install.bat", "w") as f:
        f.write(install_script)
    
    with open("run.bat", "w") as f:
        f.write(run_script)
    
    # Write .env template  
    with open(".env.example", "w") as f:
        f.write(env_template)
    
    print("✅ Setup files created!")
    print("\nNext steps:")
    print("1. Run: python -m pip install -r requirements.txt")
    print("2. Copy .env.example to .env and customize")  
    print("3. Run: python run.py")
    print("4. Open: http://localhost:8000")
    print("5. Login: admin / admin123")