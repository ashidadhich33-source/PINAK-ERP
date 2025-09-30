# PINAK ERP System - Complete Setup Guide

## 🎯 Project Overview

This is a comprehensive ERP (Enterprise Resource Planning) system built with:
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Frontend**: React with Vite, Tailwind CSS
- **Database**: SQLite (default) or PostgreSQL
- **Features**: Inventory, Sales, Purchase, Accounting, GST, Loyalty, POS, Reports

## 📁 Project Structure

```
/workspace/
├── app/                          # Backend FastAPI application
│   ├── api/endpoints/           # API route handlers
│   ├── core/                    # Core utilities (security, middleware, etc.)
│   ├── models/                  # Database models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic services
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── main.py                 # FastAPI application entry point
│   └── init_data.py            # Default data initialization
├── frontend/                    # React frontend application
│   ├── src/                    # React source code
│   ├── public/                 # Static assets
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   └── tailwind.config.js      # Tailwind CSS configuration
├── data/                       # Data processing scripts
├── Requirements.txt            # Python dependencies
├── run_app.py                 # Main application runner
└── setup_wizard.html          # Setup wizard interface
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for version control)

### 1. Backend Setup

#### Install Python Dependencies
```bash
# Install Python dependencies
pip install -r Requirements.txt
```

#### Configure Environment (Optional)
Create a `.env` file in the root directory:
```env
# Database Configuration
DATABASE_TYPE=sqlite
SQLITE_PATH=./database/erp_system.db

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here

# Company Settings
COMPANY_NAME=Your Company Name
COMPANY_ADDRESS=Your Company Address
```

#### Start Backend Server
```bash
# Method 1: Using the main runner
python run_app.py

# Method 2: Direct FastAPI
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend will be available at: `http://127.0.0.1:8000`

### 2. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Start Frontend Development Server
```bash
# Development mode
npm run dev

# Production build
npm run build
```

The frontend will be available at: `http://localhost:3000`

## 🗄️ Database Setup

### SQLite (Default)
The system uses SQLite by default. The database file will be created automatically at:
- `./database/erp_system.db`

### PostgreSQL (Optional)
To use PostgreSQL instead:

1. Install PostgreSQL
2. Create a database:
```sql
CREATE DATABASE erp_system;
```

3. Update `.env` file:
```env
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=erp_system
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

## 🔧 Configuration

### Backend Configuration
Key settings in `app/config.py`:

- **Database**: SQLite or PostgreSQL
- **Security**: JWT tokens, password policies
- **Features**: GST, Loyalty, WhatsApp, Email
- **Backup**: Automated backups
- **Logging**: Comprehensive logging

### Frontend Configuration
Key settings in `frontend/vite.config.js`:

- **Development Server**: Port 3000
- **API Proxy**: Routes `/api` to backend
- **Build**: Optimized production builds

## 📊 Initial Setup

### 1. Access Setup Wizard
Visit: `http://127.0.0.1:8000/setup`

### 2. Complete Setup Steps
1. **Database Setup**: Initialize database tables
2. **Company Setup**: Enter company details
3. **User Setup**: Create admin user
4. **Feature Configuration**: Enable/disable features

### 3. Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 🎯 Key Features

### Core Modules
- **Dashboard**: Overview and analytics
- **Inventory**: Item management, stock tracking
- **Sales**: Point of Sale, invoicing, returns
- **Purchase**: Purchase orders, supplier management
- **Accounting**: Double-entry bookkeeping, reports
- **Customers**: Customer management, loyalty program
- **Reports**: Comprehensive reporting system

### Advanced Features
- **GST Compliance**: Indian GST calculations and reports
- **Loyalty Program**: Customer loyalty points system
- **WhatsApp Integration**: Automated notifications
- **Backup System**: Automated data backups
- **Multi-company**: Support for multiple companies
- **Role-based Access**: User permissions and roles

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Policies**: Configurable password requirements
- **Role-based Access Control**: Granular permissions
- **Rate Limiting**: API rate limiting
- **CORS Protection**: Cross-origin request security
- **Input Validation**: Comprehensive data validation

## 📱 API Documentation

### Interactive API Docs
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Key API Endpoints
- **Authentication**: `/api/v1/auth/`
- **Companies**: `/api/v1/companies/`
- **Inventory**: `/api/v1/items/`
- **Sales**: `/api/v1/pos/`
- **Purchase**: `/api/v1/purchases/`
- **Reports**: `/api/v1/reports/`

## 🚀 Production Deployment

### Backend Deployment
1. **Install Dependencies**:
```bash
pip install -r Requirements.txt
```

2. **Configure Environment**:
```bash
# Set production environment variables
export DEBUG=false
export DATABASE_URL=your_production_database_url
export SECRET_KEY=your_production_secret_key
```

3. **Run with Gunicorn**:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
1. **Build for Production**:
```bash
cd frontend
npm run build
```

2. **Serve Static Files**:
```bash
# Using nginx or any static file server
# Serve the 'dist' directory
```

### Database Migration
```bash
# Initialize database
python -c "from app.database import create_tables; create_tables()"

# Initialize default data
python -c "from app.init_data import init_default_data; from app.database import get_db_session; init_default_data(next(get_db_session()))"
```

## 🔧 Development

### Backend Development
```bash
# Install development dependencies
pip install -r Requirements.txt

# Run with auto-reload
python run_app.py

# Run tests
python -m pytest
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

## 📊 Monitoring & Logging

### Log Files
- **Application Logs**: `./logs/erp_system.log`
- **Daily Logs**: `./logs/erp_YYYYMMDD.log`
- **Error Logs**: Detailed error tracking

### Health Checks
- **System Health**: `http://127.0.0.1:8000/health`
- **Database Status**: Included in health check
- **Service Status**: Backup, email, WhatsApp services

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check database configuration
   - Ensure database server is running
   - Verify connection credentials

2. **Frontend Not Loading**:
   - Check if backend is running on port 8000
   - Verify CORS settings
   - Check browser console for errors

3. **Import Errors**:
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify file permissions

### Getting Help
- Check the logs in `./logs/` directory
- Review API documentation at `/docs`
- Check system health at `/health`

## 📈 Performance Optimization

### Backend Optimization
- **Database Indexing**: Optimized database queries
- **Caching**: Redis caching support
- **Connection Pooling**: Database connection optimization
- **Async Operations**: Non-blocking I/O operations

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Minimized production builds
- **Caching**: Browser caching for static assets
- **PWA Support**: Progressive Web App features

## 🔄 Backup & Restore

### Automated Backups
- **Daily Backups**: Automatic database backups
- **Retention Policy**: Configurable backup retention
- **Backup Location**: `./backups/` directory

### Manual Backup
```bash
# Create backup
python -c "from app.services.core.backup_service import backup_service; backup_service.create_backup()"

# List backups
python -c "from app.services.core.backup_service import backup_service; print(backup_service.list_backups())"
```

## 🎉 Success!

Your PINAK ERP system is now ready to use! 

### Next Steps:
1. **Complete Setup**: Use the setup wizard to configure your company
2. **Add Data**: Start adding customers, items, and suppliers
3. **Configure Features**: Enable GST, loyalty, and other features as needed
4. **Train Users**: Set up user accounts and permissions
5. **Go Live**: Start using the system for your business operations

### Support:
- **Documentation**: Check `/docs` for API documentation
- **Health Check**: Monitor system health at `/health`
- **Logs**: Review logs for troubleshooting

---

**PINAK ERP System** - Complete Business Management Solution