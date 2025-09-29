# backend/app/core/init_data.py
"""
Initialize default data for the ERP system
Creates default users, roles, permissions, and system settings
"""

import logging
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal

from ..models.core import User, Role, Permission, Company, SystemSettings, FinancialYear, PaymentMode, Staff
from ..models.sales import BillSeries
from ..models.loyalty import LoyaltyGrade
from ..models.inventory import StockLocation
from ..core.security import SecurityService

logger = logging.getLogger(__name__)

async def initialize_default_data():
    """Initialize all default data"""
    from ..database import get_db_session

    with get_db_session() as db:
        await init_default_data(db)

def init_default_data(db: Session):
    """Initialize default system data"""
    try:
        logger.info("Initializing default data...")
        
        # Create default permissions
        create_default_permissions(db)

        # Create default roles
        create_default_roles(db)

        # Create default admin user
        create_default_users(db)

        # Create default company
        create_default_company(db)

        # Create system settings
        create_system_settings(db)

        # Create bill series
        create_default_bill_series(db)

        # Create payment modes
        create_default_payment_modes(db)

        # Create loyalty grades
        create_default_loyalty_grades(db)

        # Create stock locations
        create_default_stock_locations(db)

        # Create financial year
        create_default_financial_year(db)
        
        logger.info("✅ Default data initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Error initializing default data: {e}")
        db.rollback()
        raise

def create_default_permissions(db: Session):
    """Create default system permissions"""
    permissions_data = [
        # User Management
        ("users.view", "View Users", "View user list and details", "users"),
        ("users.create", "Create Users", "Create new user accounts", "users"),
        ("users.edit", "Edit Users", "Modify user information", "users"),
        ("users.delete", "Delete Users", "Remove user accounts", "users"),
        ("users.manage", "Manage Users", "Full user management access", "users"),
        
        # Items & Inventory
        ("items.view", "View Items", "View item catalog and inventory", "items"),
        ("items.create", "Create Items", "Add new items to catalog", "items"),
        ("items.edit", "Edit Items", "Modify item information", "items"),
        ("items.delete", "Delete Items", "Remove items from catalog", "items"),
        ("items.import", "Import Items", "Import items from Excel", "items"),
        ("items.export", "Export Items", "Export item data", "items"),
        
        # Customer Management  
        ("customers.view", "View Customers", "View customer list and details", "customers"),
        ("customers.create", "Create Customers", "Add new customers", "customers"),
        ("customers.edit", "Edit Customers", "Modify customer information", "customers"),
        ("customers.delete", "Delete Customers", "Remove customers", "customers"),
        ("customers.import", "Import Customers", "Import customer data", "customers"),
        
        # Supplier Management
        ("suppliers.view", "View Suppliers", "View supplier list and details", "suppliers"),
        ("suppliers.create", "Create Suppliers", "Add new suppliers", "suppliers"),
        ("suppliers.edit", "Edit Suppliers", "Modify supplier information", "suppliers"),
        ("suppliers.delete", "Delete Suppliers", "Remove suppliers", "suppliers"),
        
        # Sales & POS
        ("sales.view", "View Sales", "View sales data and transactions", "sales"),
        ("sales.create", "Create Sales", "Process sales transactions", "sales"),
        ("sales.edit", "Edit Sales", "Modify sales records", "sales"),
        ("sales.delete", "Delete Sales", "Cancel sales transactions", "sales"),
        ("sales.return", "Process Returns", "Handle sale returns", "sales"),
        ("sales.pos", "POS Access", "Access point of sale system", "sales"),
        
        # Purchase Management
        ("purchases.view", "View Purchases", "View purchase orders and bills", "purchases"),
        ("purchases.create", "Create Purchases", "Create purchase orders", "purchases"),
        ("purchases.edit", "Edit Purchases", "Modify purchase records", "purchases"),
        ("purchases.delete", "Delete Purchases", "Cancel purchases", "purchases"),
        
        # Reports & Analytics
        ("reports.view", "View Reports", "Access reporting system", "reports"),
        ("reports.sales", "Sales Reports", "Generate sales reports", "reports"),
        ("reports.purchase", "Purchase Reports", "Generate purchase reports", "reports"),
        ("reports.stock", "Stock Reports", "Generate inventory reports", "reports"),
        ("reports.financial", "Financial Reports", "Generate financial reports", "reports"),
        ("reports.export", "Export Reports", "Export report data", "reports"),
        
        # Settings & Configuration
        ("settings.view", "View Settings", "View system settings", "settings"),
        ("settings.edit", "Edit Settings", "Modify system configuration", "settings"),
        ("settings.backup", "Backup System", "Create system backups", "settings"),
        ("settings.restore", "Restore System", "Restore from backup", "settings"),
        
        # Staff Management
        ("staff.view", "View Staff", "View staff information", "staff"),
        ("staff.create", "Create Staff", "Add new staff members", "staff"),
        ("staff.edit", "Edit Staff", "Modify staff information", "staff"),
        ("staff.delete", "Delete Staff", "Remove staff members", "staff"),
        
        # Payment Processing
        ("payments.view", "View Payments", "View payment records", "payments"),
        ("payments.create", "Process Payments", "Create payment entries", "payments"),
        ("payments.edit", "Edit Payments", "Modify payment records", "payments"),
        
        # Expense Management
        ("expenses.view", "View Expenses", "View expense records", "expenses"),
        ("expenses.create", "Create Expenses", "Add new expenses", "expenses"),
        ("expenses.edit", "Edit Expenses", "Modify expense records", "expenses"),
        ("expenses.approve", "Approve Expenses", "Approve expense claims", "expenses"),
        
        # Backup & Restore
        ("backup.create", "Create Backup", "Create system backups", "backup"),
        ("backup.restore", "Restore Backup", "Restore from backups", "backup"),
        ("backup.download", "Download Backup", "Download backup files", "backup"),
    ]
    
    for name, display_name, description, module in permissions_data:
        if not db.query(Permission).filter(Permission.name == name).first():
            permission = Permission(
                name=name,
                display_name=display_name,
                description=description,
                module=module
            )
            db.add(permission)
    
    db.commit()
    logger.info("✅ Default permissions created")

def create_default_roles(db: Session):
    """Create default user roles"""
    roles_data = [
        {
            "name": "admin",
            "display_name": "Administrator", 
            "description": "Full system access with all permissions",
            "permissions": ["*"]  # All permissions
        },
        {
            "name": "manager",
            "display_name": "Manager",
            "description": "Management level access with reporting capabilities",
            "permissions": [
                "users.view", "items.*", "customers.*", "suppliers.*", 
                "sales.*", "purchases.*", "reports.*", "staff.*",
                "payments.*", "expenses.view", "expenses.approve"
            ]
        },
        {
            "name": "cashier",
            "display_name": "Cashier",
            "description": "Point of sale and basic customer operations",
            "permissions": [
                "items.view", "customers.view", "customers.create", 
                "sales.*", "payments.view", "payments.create"
            ]
        },
        {
            "name": "inventory",
            "display_name": "Inventory Manager",
            "description": "Inventory and stock management",
            "permissions": [
                "items.*", "suppliers.*", "purchases.*", 
                "reports.stock", "reports.purchase"
            ]
        },
        {
            "name": "accountant",
            "display_name": "Accountant",
            "description": "Financial operations and reporting",
            "permissions": [
                "reports.financial", "payments.*", "expenses.*",
                "customers.view", "suppliers.view"
            ]
        },
        {
            "name": "viewer",
            "display_name": "Viewer",
            "description": "Read-only access to most system data",
            "permissions": [
                "items.view", "customers.view", "suppliers.view",
                "sales.view", "purchases.view", "reports.view"
            ]
        }
    ]
    
    for role_data in roles_data:
        if not db.query(Role).filter(Role.name == role_data["name"]).first():
            role = Role(
                name=role_data["name"],
                display_name=role_data["display_name"],
                description=role_data["description"]
            )
            db.add(role)
            db.flush()
            
            # Assign permissions to role
            if role_data["permissions"] == ["*"]:
                # Assign all permissions to admin
                all_permissions = db.query(Permission).all()
                role.permissions.extend(all_permissions)
            else:
                for perm_pattern in role_data["permissions"]:
                    if perm_pattern.endswith(".*"):
                        # Module wildcard (e.g., "items.*")
                        module = perm_pattern[:-2]
                        perms = db.query(Permission).filter(Permission.module == module).all()
                        role.permissions.extend(perms)
                    else:
                        # Specific permission
                        perm = db.query(Permission).filter(Permission.name == perm_pattern).first()
                        if perm:
                            role.permissions.append(perm)
    
    db.commit()
    logger.info("✅ Default roles created")

def create_default_users(db: Session):
    """Create default admin user"""
    # Check if admin user exists
    if not db.query(User).filter(User.username == "admin").first():
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        
        admin_user = User(
            username="admin",
            email="admin@erp.local",
            full_name="System Administrator",
            hashed_password=SecurityService.get_password_hash("admin123"),
            is_superuser=True,
            is_active=True
        )
        
        if admin_role:
            admin_user.roles.append(admin_role)
        
        db.add(admin_user)
        db.commit()
        logger.info("✅ Default admin user created (admin/admin123)")
    
    # Create demo cashier user
    if not db.query(User).filter(User.username == "cashier").first():
        cashier_role = db.query(Role).filter(Role.name == "cashier").first()
        
        cashier_user = User(
            username="cashier",
            email="cashier@erp.local", 
            full_name="Demo Cashier",
            hashed_password=SecurityService.get_password_hash("cashier123"),
            is_superuser=False,
            is_active=True
        )
        
        if cashier_role:
            cashier_user.roles.append(cashier_role)
        
        db.add(cashier_user)
        db.commit()
        logger.info("✅ Default cashier user created (cashier/cashier123)")

def create_default_company(db: Session):
    """Create default company record"""
    if not db.query(Company).first():
        company = Company(
            name="Your Company Name",
            display_name="Your Company Display Name",
            address_line1="123 Business Street",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400001",
            phone="022-12345678",
            email="info@yourcompany.com",
            financial_year_start="04-01",
            currency="INR",
            decimal_places=2
        )
        
        db.add(company)
        db.commit()
        logger.info("✅ Default company created")

def create_system_settings(db: Session):
    """Create default system settings"""
    settings_data = [
        # GST Settings
        ("gst_enabled", "true", "boolean", "gst", "Enable GST", "Enable GST calculations"),
        ("default_gst_rate", "18.0", "float", "gst", "Default GST Rate", "Default GST rate percentage"),
        ("gst_threshold", "999.00", "float", "gst", "GST Threshold", "Amount below which 5% GST applies"),
        
        # Loyalty Settings
        ("loyalty_enabled", "true", "boolean", "loyalty", "Enable Loyalty", "Enable loyalty points system"),
        ("points_per_100", "1", "integer", "loyalty", "Points per ₹100", "Points earned per ₹100 spent"),
        ("point_value", "0.25", "float", "loyalty", "Point Value", "Monetary value of each point"),
        ("min_redemption", "100", "integer", "loyalty", "Min Redemption", "Minimum points for redemption"),
        
        # Inventory Settings
        ("negative_stock", "false", "boolean", "inventory", "Allow Negative Stock", "Allow sales when stock is negative"),
        ("low_stock_alert", "10", "integer", "inventory", "Low Stock Alert", "Alert when stock below this level"),
        
        # POS Settings
        ("auto_print_receipt", "true", "boolean", "pos", "Auto Print Receipt", "Automatically print receipts"),
        ("show_stock_pos", "true", "boolean", "pos", "Show Stock in POS", "Display current stock in POS"),
        
        # Business Settings
        ("business_hours_start", "09:00", "string", "business", "Business Hours Start", "Daily business start time"),
        ("business_hours_end", "21:00", "string", "business", "Business Hours End", "Daily business end time"),
        ("return_policy_days", "7", "integer", "business", "Return Policy", "Days allowed for returns"),
        
        # WhatsApp Settings
        ("whatsapp_enabled", "false", "boolean", "whatsapp", "Enable WhatsApp", "Enable WhatsApp integration"),
        ("whatsapp_send_invoice", "true", "boolean", "whatsapp", "Send Invoice", "Send invoice via WhatsApp"),
        ("whatsapp_birthday_wishes", "true", "boolean", "whatsapp", "Birthday Wishes", "Send birthday wishes"),
        
        # Backup Settings
        ("auto_backup", "true", "boolean", "backup", "Auto Backup", "Enable automatic backups"),
        ("backup_retention", "7", "integer", "backup", "Backup Retention", "Days to keep backup files"),
    ]
    
    for key, value, setting_type, module, display_name, description in settings_data:
        if not db.query(SystemSettings).filter(SystemSettings.setting_key == key).first():
            setting = SystemSettings(
                setting_key=key,
                setting_value=value,
                setting_type=setting_type,
                module=module,
                display_name=display_name,
                description=description,
                is_editable=True
            )
            db.add(setting)
    
    db.commit()
    logger.info("✅ System settings created")

def create_default_bill_series(db: Session):
    """Create default bill numbering series"""
    series_data = [
        {
            "code": "SALE",
            "description": "Sale Bills",
            "prefix": "S",
            "next_no": 1,
            "width": 5,
            "fy": "2024-25",
            "default_tax_region": "local",
            "active": True
        },
        {
            "code": "SR",
            "description": "Sale Returns",
            "prefix": "SR",
            "next_no": 1, 
            "width": 5,
            "fy": "2024-25",
            "default_tax_region": "local",
            "active": True
        },
        {
            "code": "PB",
            "description": "Purchase Bills",
            "prefix": "PB",
            "next_no": 1,
            "width": 5,
            "fy": "2024-25",
            "default_tax_region": "local",
            "active": True
        },
        {
            "code": "PR",
            "description": "Purchase Returns", 
            "prefix": "PR",
            "next_no": 1,
            "width": 5,
            "fy": "2024-25",
            "default_tax_region": "local",
            "active": True
        },
        {
            "code": "INV",
            "description": "Tax Invoices",
            "prefix": "INV",
            "next_no": 1,
            "width": 6,
            "fy": "2024-25",
            "default_tax_region": "local",
            "active": True
        }
    ]
    
    for series_info in series_data:
        if not db.query(BillSeries).filter(BillSeries.code == series_info["code"]).first():
            series = BillSeries(**series_info)
            db.add(series)
    
    db.commit()
    logger.info("✅ Default bill series created")

def create_default_payment_modes(db: Session):
    """Create default payment methods"""
    payment_modes = [
        {"name": "Cash", "settlement_type": "cash", "active": True},
        {"name": "Card", "settlement_type": "bank", "active": True},
        {"name": "UPI", "settlement_type": "bank", "active": True},
        {"name": "Bank Transfer", "settlement_type": "bank", "active": True},
        {"name": "Cheque", "settlement_type": "bank", "active": True},
        {"name": "Paytm", "settlement_type": "supplier", "active": True},
        {"name": "PhonePe", "settlement_type": "supplier", "active": True},
        {"name": "GooglePay", "settlement_type": "supplier", "active": True},
    ]
    
    for mode_data in payment_modes:
        if not db.query(PaymentMode).filter(PaymentMode.name == mode_data["name"]).first():
            payment_mode = PaymentMode(**mode_data)
            db.add(payment_mode)
    
    db.commit() 
    logger.info("✅ Default payment modes created")

def create_default_loyalty_grades(db: Session):
    """Create default customer loyalty grades"""
    grades_data = [
        {
            "name": "Silver",
            "amount_from": Decimal('0'),
            "amount_to": Decimal('10000'),
            "earn_pct": Decimal('1.0'),
            "discount_percent": Decimal('0'),
            "badge_color": "#C0C0C0",
            "description": "Entry level loyalty grade"
        },
        {
            "name": "Gold", 
            "amount_from": Decimal('10001'),
            "amount_to": Decimal('25000'),
            "earn_pct": Decimal('1.5'),
            "discount_percent": Decimal('2'),
            "badge_color": "#FFD700",
            "description": "Mid-tier loyalty grade with benefits"
        },
        {
            "name": "Platinum",
            "amount_from": Decimal('25001'),
            "amount_to": Decimal('999999999'),
            "earn_pct": Decimal('2.0'),
            "discount_percent": Decimal('5'),
            "badge_color": "#E5E4E2",
            "description": "Premium loyalty grade with maximum benefits"
        }
    ]
    
    for grade_data in grades_data:
        if not db.query(LoyaltyGrade).filter(LoyaltyGrade.name == grade_data["name"]).first():
            grade = LoyaltyGrade(**grade_data)
            db.add(grade)
    
    db.commit()
    logger.info("✅ Default loyalty grades created")

def create_default_stock_locations(db: Session):
    """Create default stock locations"""
    if not db.query(StockLocation).filter(StockLocation.code == "MAIN").first():
        main_location = StockLocation(
            code="MAIN",
            name="Main Store",
            description="Primary stock location",
            is_main_location=True,
            is_active=True
        )
        db.add(main_location)
    
    # Additional locations
    locations = [
        {"code": "WH01", "name": "Warehouse 1", "description": "Secondary warehouse"},
        {"code": "SHOP", "name": "Shop Floor", "description": "Display area stock"},
        {"code": "DAMAGED", "name": "Damaged Stock", "description": "Damaged items location"}
    ]
    
    for loc_data in locations:
        if not db.query(StockLocation).filter(StockLocation.code == loc_data["code"]).first():
            location = StockLocation(**loc_data, is_active=True)
            db.add(location)
    
    db.commit()
    logger.info("✅ Default stock locations created")

def create_default_financial_year(db: Session):
    """Create current financial year"""
    current_year = datetime.now().year
    fy_name = f"{current_year}-{str(current_year + 1)[-2:]}"
    
    if not db.query(FinancialYear).filter(FinancialYear.year_name == fy_name).first():
        fy = FinancialYear(
            year_name=fy_name,
            start_date=f"{current_year}-04-01",
            end_date=f"{current_year + 1}-03-31", 
            is_current=True,
            is_closed=False
        )
        db.add(fy)
        db.commit()
        logger.info(f"✅ Financial year {fy_name} created")

async def create_sample_data(db: Session):
    """Create sample data for testing (optional)"""
    try:
        # This function can be called separately to add demo data
        logger.info("Creating sample data...")
        
        # Add demo staff member
        if not db.query(Staff).filter(Staff.code == "EMP001").first():
            demo_staff = Staff(
                code="EMP001",
                name="Demo Sales Person",
                mobile="9876543210",
                role="Sales Executive",
                email="sales@demo.com",
                joining_date=date.today(),
                basic_salary=Decimal('25000'),
                commission_enabled=True,
                active=True
            )
            db.add(demo_staff)
        
        db.commit()
        logger.info("✅ Sample data created")
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()

# No longer needed since we made all functions synchronous
