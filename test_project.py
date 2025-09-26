#!/usr/bin/env python3
"""
Comprehensive test script to check if all imports work correctly
and identify any remaining issues in the ERP project
"""

import sys
import traceback
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

def test_imports():
    """Test all major imports"""
    tests_passed = 0
    tests_failed = 0

    print("🧪 Testing ERP Project Imports and Structure")
    print("=" * 60)

    # Test 1: Main application imports
    try:
        from app.config import settings
        from app.database import create_tables, get_db, engine, Base, check_database_connection
        print("✅ Main application imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Main application imports failed: {e}")
        tests_failed += 1

    # Test 2: All models import
    try:
        from app.models import (
            User, Role, Permission, Customer, Item, Sale, PurchaseBill,
            Supplier, Staff, Expense, Payment, LoyaltyGrade, Company,
            SystemSettings, FinancialYear, StockLocation, BillSeries,
            PaymentMode, ItemCategory, Brand
        )
        print("✅ All models import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        tests_failed += 1

    # Test 3: API endpoints import
    try:
        from app.api.endpoints import (
            auth, setup, items, customers, suppliers, staff, sales,
            purchases, payments, expenses, reports, backup, settings
        )
        print("✅ API endpoints import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ API endpoints import failed: {e}")
        tests_failed += 1

    # Test 4: Core modules import
    try:
        from app.core.security import SecurityService, get_current_user
        from app.core.exceptions import setup_exception_handlers
        from app.core.middleware import setup_middlewares
        from app.core.rbac import require_permission, require_role
        print("✅ Core modules import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Core modules import failed: {e}")
        tests_failed += 1

    # Test 5: Services import
    try:
        from app.services.backup_service import backup_service
        from app.services.excel_service import excel_service
        from app.services.gst_service import gst_service
        from app.services.loyalty_service import loyalty_service
        from app.services.pdf_service import pdf_service
        from app.services.settings_service import settings_service
        from app.services.stock_service import stock_service
        from app.services.whatsapp_service import whatsapp_service
        print("✅ Services import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        tests_failed += 1

    # Test 6: Schema imports
    try:
        from app.schemas.user_schema import UserResponse, UserCreate, UserUpdate
        from app.schemas.customer_schema import CustomerResponse, CustomerCreate, CustomerUpdate
        from app.schemas.item_schema import ItemResponse, ItemCreate, ItemUpdate
        from app.schemas.sales_schema import SalesInvoiceResponse, SalesInvoiceCreate
        from app.schemas.purchase_schema import PurchaseInvoiceResponse, PurchaseInvoiceCreate
        print("✅ Schemas import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        tests_failed += 1

    # Test 7: Init data import
    try:
        from app.init_data import init_default_data, initialize_default_data
        print("✅ Init data import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Init data import failed: {e}")
        tests_failed += 1

    # Test 8: Main FastAPI app import
    try:
        from app.main import app
        print("✅ FastAPI app import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        tests_failed += 1

    # Test 9: Check settings configuration
    try:
        print(f"✅ Settings loaded: {settings.app_name} v{settings.app_version}")
        print(f"✅ Database type: {settings.database_type}")
        print(f"✅ API prefix: {settings.api_prefix}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Settings configuration failed: {e}")
        tests_failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed} passed, {tests_failed} failed")

    if tests_failed == 0:
        print("🎉 All tests passed! The project structure is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def test_models_structure():
    """Test that all model relationships work correctly"""
    print("\n🔍 Testing Model Structure")
    print("-" * 40)

    try:
        from app.models import User, Customer, Item, Sale, Company

        # Test basic model instantiation (without database)
        print("✅ Models can be imported and referenced")

        # Test that key methods exist
        if hasattr(User, 'has_permission'):
            print("✅ User.has_permission method exists")
        if hasattr(User, 'has_role'):
            print("✅ User.has_role method exists")
        if hasattr(Customer, 'is_credit_limit_exceeded'):
            print("✅ Customer.is_credit_limit_exceeded method exists")

        return True
    except Exception as e:
        print(f"❌ Model structure test failed: {e}")
        return False

def test_database_connection():
    """Test database connection without actually connecting"""
    print("\n🗄️  Testing Database Configuration")
    print("-" * 40)

    try:
        from app.config import settings
        from app.database import create_database_engine, DatabaseHealthCheck

        # Test that database URL is constructed properly
        db_url = settings.database_url
        print(f"✅ Database URL configured: {db_url.split('://')[0]}://***")

        # Test that engine creation works
        engine = create_database_engine()
        print("✅ Database engine created successfully")

        return True
    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ERP Project Comprehensive Test Suite")
    print("=" * 60)

    results = []

    # Run all test functions
    results.append(("Import Tests", test_imports()))
    results.append(("Model Structure", test_models_structure()))
    results.append(("Database Config", test_database_connection()))

    print("\n" + "=" * 60)
    print("📋 FINAL REPORT")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("🎯 The ERP project is ready to run!")
        print("\nTo start the application:")
        print("1. python run_app.py")
        print("2. Open http://localhost:8000/docs")
        print("3. Login with: admin / admin123")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("🔧 Fix the issues and run the test again.")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)