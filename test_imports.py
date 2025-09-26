#!/usr/bin/env python3
"""Test script to check if all imports work correctly"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

try:
    # Test main imports
    from app.config import settings
    print("✅ Config import successful")

    from app.database import get_db, create_tables
    print("✅ Database import successful")

    from app.models.user import User, Role, Permission
    print("✅ User models import successful")

    from app.core.security import SecurityService, get_current_user
    print("✅ Security import successful")

    from app.core.exceptions import setup_exception_handlers
    print("✅ Exceptions import successful")

    from app.core.middleware import setup_middlewares
    print("✅ Middleware import successful")

    from app.api.endpoints.auth import router as auth_router
    print("✅ Auth router import successful")

    from app.services.backup_service import backup_service
    print("✅ Backup service import successful")

    print("\n🎉 All imports successful! The project structure is working correctly.")

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()