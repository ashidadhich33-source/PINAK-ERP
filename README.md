# ERP System - Complete FastAPI Application

A comprehensive Enterprise Resource Planning (ERP) system built with FastAPI, SQLAlchemy, and modern Python practices.

## 🏗️ Project Structure

```
/workspace/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Configuration settings
│   ├── database.py               # Database setup and utilities
│   ├── init_data.py              # Default data initialization
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model classes
│   │   ├── user.py              # User, Role, Permission models
│   │   ├── customer.py          # Customer management models
│   │   ├── item.py              # Item and inventory models
│   │   ├── sales.py             # Sales and invoice models
│   │   ├── purchase.py          # Purchase models
│   │   ├── supplier.py          # Supplier models
│   │   ├── staff.py             # Staff management models
│   │   ├── expense.py           # Expense tracking models
│   │   ├── payment.py           # Payment processing models
│   │   ├── loyalty.py           # Loyalty program models
│   │   ├── company.py           # Company information models
│   │   └── stock.py             # Stock transaction models
│   ├── api/                     # API package
│   │   ├── __init__.py
│   │   └── endpoints/           # API endpoint modules
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── setup.py         # System setup endpoints
│   │       ├── items.py         # Item management endpoints
│   │       ├── customers.py     # Customer management endpoints
│   │       ├── suppliers.py     # Supplier management endpoints
│   │       ├── staff.py         # Staff management endpoints
│   │       ├── sales.py         # Sales and POS endpoints
│   │       ├── purchases.py     # Purchase management endpoints
│   │       ├── payments.py      # Payment processing endpoints
│   │       ├── expenses.py      # Expense management endpoints
│   │       ├── reports.py       # Reports and analytics endpoints
│   │       ├── backup.py        # Backup and restore endpoints
│   │       ├── settings.py      # System settings endpoints
│   │       ├── sale_returns.py  # Sales returns endpoints
│   │       └── whatsapp.py      # WhatsApp integration endpoints
│   ├── core/                    # Core application modules
│   │   ├── __init__.py
│   │   ├── security.py          # Authentication and security utilities
│   │   ├── exceptions.py        # Custom exception handlers
│   │   ├── middleware.py        # FastAPI middleware setup
│   │   ├── backup.py            # Backup utilities
│   │   ├── coupons.py           # Coupon management
│   │   ├── formatters.py        # Data formatting utilities
│   │   ├── helpers.py           # General helper functions
│   │   ├── pos_helpers.py       # Point of Sale helpers
│   │   ├── rbac.py              # Role-based access control
│   │   ├── validators.py        # Data validation utilities
│   │   ├── constants.py         # Application constants
│   │   └── deps.py              # Dependency injection utilities
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── backup_service.py    # Database backup service
│   │   ├── excel_service.py     # Excel file processing
│   │   ├── gst_service.py       # GST calculation service
│   │   ├── loyalty_service.py   # Loyalty program service
│   │   ├── pdf_service.py       # PDF generation service
│   │   ├── settings_service.py  # Settings management service
│   │   ├── stock_service.py     # Stock management service
│   │   └── whatsapp_service.py  # WhatsApp integration service
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── customer_schema.py   # Customer schemas
│   │   ├── item_schema.py       # Item schemas
│   │   ├── purchase_schema.py   # Purchase schemas
│   │   ├── sale_return_schema.py # Sales return schemas
│   │   ├── sales_schema.py      # Sales schemas
│   │   ├── staff_schema.py      # Staff schemas
│   │   ├── supplier_schema.py   # Supplier schemas
│   │   ├── user_schema.py       # User schemas
│   │   ├── expense_schema.py    # Expense schemas
│   │   └── report_schema.py     # Report schemas
│   ├── static/                  # Static files directory
│   └── templates/               # HTML templates directory
├── __init__.py                  # Root package init
├── Requirements.txt             # Python dependencies
├── run.py                       # Alternative run script
└── *.bat files                  # Windows batch scripts
```

## 🚀 Features

### Core Features
- **User Management**: Role-based access control with permissions
- **Customer Management**: Customer database with groups and loyalty
- **Inventory Management**: Items, categories, stock tracking
- **Sales & POS**: Point of sale system with invoices
- **Purchase Management**: Supplier management and purchase orders
- **Expense Tracking**: Business expense categorization and tracking
- **Payment Processing**: Multiple payment methods and tracking
- **Reports & Analytics**: Comprehensive business reporting

### Advanced Features
- **GST Integration**: Indian GST calculation and compliance
- **Loyalty Program**: Customer loyalty points system
- **WhatsApp Integration**: Customer notifications via WhatsApp
- **Backup & Restore**: Automated database backup system
- **Multi-database Support**: SQLite and PostgreSQL support
- **Email Integration**: Email notifications and templates
- **PDF/Excel Export**: Report generation in multiple formats

### Technical Features
- **FastAPI Framework**: Modern, fast web framework
- **SQLAlchemy ORM**: Powerful database abstraction
- **JWT Authentication**: Secure token-based authentication
- **CORS Support**: Cross-origin resource sharing
- **Comprehensive Logging**: Structured logging system
- **Rate Limiting**: Basic rate limiting protection
- **Health Monitoring**: System health checks and monitoring

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps

1. **Install Dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

2. **Setup Environment Variables** (Optional)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

4. **Run the Application**
   ```bash
   # Using main.py directly
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Or using the run script
   python run.py
   ```

### Default Login
- **Username**: admin
- **Password**: admin123

## 📊 API Documentation

Once the application is running, visit:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Admin Panel**: http://localhost:8000/admin

## 🔧 Configuration

The application can be configured using environment variables or the `.env` file:

### Database Configuration
- `DATABASE_TYPE`: sqlite or postgresql (default: sqlite)
- `DATABASE_URL`: Custom database URL
- `SQLITE_PATH`: SQLite database file path

### Security Configuration
- `SECRET_KEY`: JWT secret key (auto-generated if not set)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DEBUG`: Enable debug mode

### Feature Toggles
- `GST_ENABLED`: Enable GST calculations
- `LOYALTY_ENABLED`: Enable loyalty program
- `WHATSAPP_ENABLED`: Enable WhatsApp integration
- `EMAIL_ENABLED`: Enable email notifications
- `BACKUP_ENABLED`: Enable automatic backups

## 🗄️ Database Models

The system includes comprehensive models for:
- Users, Roles, and Permissions
- Customers and Customer Groups
- Items and Categories
- Sales Invoices and Line Items
- Purchase Invoices and Line Items
- Suppliers
- Staff Members
- Expenses and Categories
- Payments
- Loyalty Programs and Points
- Company Information
- Stock Transactions

## 🔐 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Rate limiting
- CORS protection
- Input validation
- SQL injection protection
- XSS protection headers

## 📱 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/change-password` - Change password

### Customer Management
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `PUT /api/v1/customers/{id}` - Update customer

### Inventory Management
- `GET /api/v1/items` - List items
- `POST /api/v1/items` - Create item
- `PUT /api/v1/items/{id}` - Update item

### Sales & POS
- `POST /api/v1/sales/pos` - Create sale
- `GET /api/v1/sales` - List sales
- `GET /api/v1/sales/{id}` - Get sale details

### Reports
- `GET /api/v1/reports/sales` - Sales reports
- `GET /api/v1/reports/inventory` - Inventory reports
- `GET /api/v1/reports/financial` - Financial reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the configuration options in `config.py`

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**