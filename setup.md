# PINAK ERP System - Complete Setup Guide

## 🎯 Project Overview

This is a comprehensive ERP (Enterprise Resource Planning) system built with:
- **Backend**: FastAPI (Python 3.8+) with SQLAlchemy ORM
- **Frontend**: React 18+ with Vite, Tailwind CSS
- **Database**: SQLite (default) or PostgreSQL 12+
- **Features**: Inventory, Sales, Purchase, Accounting, GST, Loyalty, POS, Reports
- **Server Requirements**: Python 3.8+, Node.js 16+, PostgreSQL 12+ (optional)

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

#### For Windows Systems:
- **Python 3.8+** with pip (Download from python.org)
- **Node.js 16+** with npm (Download from nodejs.org)
- **Git** (for version control) - Download from git-scm.com
- **PostgreSQL 12+** (optional, for production) - Download from postgresql.org
- **Visual Studio Build Tools** (for Python packages with C extensions)

#### For Linux/Mac Systems:
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for version control)
- **PostgreSQL 12+** (optional, for production)

## 🪟 Windows Installation Guide

### Step 1: Install Prerequisites

#### 1.1 Install Python 3.8+
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### 1.2 Install Node.js 16+
1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Choose the LTS version (recommended)
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

#### 1.3 Install PostgreSQL (Optional but Recommended)
1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. During installation:
   - Set a strong password for the `postgres` user
   - Note the port (default: 5432)
   - Remember the installation directory
3. Verify installation:
   ```cmd
   psql --version
   ```

#### 1.4 Install Visual Studio Build Tools (Required for some Python packages)
1. Download from [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
2. Install "C++ build tools" workload
3. This is required for packages like `psycopg2-binary`

### Step 2: Clone and Setup Project

#### 2.1 Clone the Repository
```cmd
git clone <repository-url>
cd pinak-erp-system
```

#### 2.2 Create Virtual Environment
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
```

### Step 3: Backend Setup

#### 3.1 Install Python Dependencies
```cmd
# Make sure virtual environment is activated
pip install --upgrade pip
pip install -r Requirements.txt
```

#### 3.2 Database Setup Options

**Option A: SQLite (Default - Easiest)**
```cmd
# No additional setup required
# Database will be created automatically at ./database/erp_system.db
```

**Option B: PostgreSQL (Recommended for Production)**
```cmd
# 1. Create database in PostgreSQL
psql -U postgres -h localhost
CREATE DATABASE erp_system;
CREATE USER erp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE erp_system TO erp_user;
\q

# 2. Create .env file in project root
# Copy the example below and modify as needed
```

#### 3.3 Environment Configuration
Create a `.env` file in the project root:
```env
# Database Configuration
DATABASE_TYPE=sqlite
# For PostgreSQL, use:
# DATABASE_TYPE=postgresql
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=erp_system
# POSTGRES_USER=erp_user
# POSTGRES_PASSWORD=your_secure_password

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production

# Company Settings
COMPANY_NAME=Your Company Name
COMPANY_ADDRESS=Your Company Address
```

### Step 4: Frontend Setup

#### 4.1 Install Node.js Dependencies
```cmd
cd frontend
npm install
```

#### 4.2 Build Frontend (Optional)
```cmd
# For development
npm run dev

# For production
npm run build
```

### Step 5: Run the Application

#### 5.1 Start Backend Server
```cmd
# From project root directory
python run_app.py
```

#### 5.2 Start Frontend (In a new terminal)
```cmd
cd frontend
npm run dev
```

#### 5.3 Access the Application
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Setup Wizard**: http://127.0.0.1:8000/setup
- **Frontend**: http://localhost:3000

### Step 6: Initial Setup Wizard

1. Open your browser and go to: http://127.0.0.1:8000/setup
2. Follow the setup wizard:
   - **Step 1**: Choose database type (SQLite or PostgreSQL)
   - **Step 2**: Enter company information
   - **Step 3**: Create admin user account
   - **Step 4**: Complete setup

3. **Default Login Credentials**:
   - Username: `admin`
   - Password: `admin123`

## 🚀 Quick Start (Alternative Method)

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

## 🖥️ Server Requirements

### Minimum System Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.15+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **CPU**: 2 cores minimum, 4 cores recommended

### Production Server Requirements
- **OS**: Linux (Ubuntu 20.04+), CentOS 8+, RHEL 8+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB+ SSD recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Database**: PostgreSQL 12+ (recommended for production)

### Database Requirements

#### SQLite (Default - Development/Small Business)
- **Pros**: No server setup, file-based, easy to backup
- **Cons**: Limited concurrent users, not suitable for production
- **Use Case**: Development, small businesses (< 10 users)
- **File Location**: `./database/erp_system.db`

#### PostgreSQL (Recommended for Production)
- **Pros**: High performance, concurrent users, ACID compliance
- **Cons**: Requires server setup and maintenance
- **Use Case**: Production, medium to large businesses
- **Requirements**: PostgreSQL 12+, 2GB+ RAM for database server

#### MySQL (Alternative)
- **Pros**: Popular, good performance, easy setup
- **Cons**: Less advanced features than PostgreSQL
- **Use Case**: Web applications, existing MySQL infrastructure

## 🗄️ Database Setup

### SQLite (Default)
The system uses SQLite by default. The database file will be created automatically at:
- `./database/erp_system.db`

### PostgreSQL (Recommended for Production)
To use PostgreSQL instead:

1. **Install PostgreSQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   
   # Windows - Download from postgresql.org
   # macOS
   brew install postgresql
   ```

2. **Create Database and User**:
   ```sql
   -- Connect as postgres user
   sudo -u postgres psql
   
   -- Create database
   CREATE DATABASE erp_system;
   
   -- Create user
   CREATE USER erp_user WITH PASSWORD 'your_secure_password';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE erp_system TO erp_user;
   GRANT ALL PRIVILEGES ON SCHEMA public TO erp_user;
   
   -- Exit
   \q
   ```

3. **Update Environment Configuration**:
   ```env
   DATABASE_TYPE=postgresql
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=erp_system
   POSTGRES_USER=erp_user
   POSTGRES_PASSWORD=your_secure_password
   ```

### MySQL (Alternative)
To use MySQL:

1. **Install MySQL**:
   ```bash
   # Ubuntu/Debian
   sudo apt install mysql-server
   
   # Windows - Download from mysql.com
   # macOS
   brew install mysql
   ```

2. **Create Database**:
   ```sql
   CREATE DATABASE erp_system;
   CREATE USER 'erp_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON erp_system.* TO 'erp_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Update Environment Configuration**:
   ```env
   DATABASE_TYPE=mysql
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DB=erp_system
   MYSQL_USER=erp_user
   MYSQL_PASSWORD=your_secure_password
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

#### Windows-Specific Issues

1. **Python Installation Issues**:
   ```
   Error: 'python' is not recognized as an internal or external command
   Solution: Add Python to PATH during installation or manually add to system PATH
   ```

2. **Visual Studio Build Tools Required**:
   ```
   Error: Microsoft Visual C++ 14.0 is required
   Solution: Install Visual Studio Build Tools with C++ workload
   ```

3. **PostgreSQL Connection Issues**:
   ```
   Error: psycopg2.OperationalError: FATAL: password authentication failed
   Solution: Check PostgreSQL user credentials and pg_hba.conf settings
   ```

4. **Node.js/npm Issues**:
   ```
   Error: 'npm' is not recognized
   Solution: Reinstall Node.js and ensure it's added to PATH
   ```

#### General Issues

1. **Database Connection Failed**:
   - Check database configuration in `.env` file
   - Ensure database server is running
   - Verify connection credentials
   - For PostgreSQL: Check `pg_hba.conf` and `postgresql.conf`

2. **Frontend Not Loading**:
   - Check if backend is running on port 8000
   - Verify CORS settings in `app/config.py`
   - Check browser console for errors
   - Ensure frontend is running on port 3000

3. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r Requirements.txt`
   - Check Python path configuration
   - Verify file permissions
   - Activate virtual environment: `venv\Scripts\activate` (Windows)

4. **Port Already in Use**:
   ```
   Error: [Errno 98] Address already in use
   Solution: Change port in .env file or kill process using the port
   ```

5. **Permission Denied Errors**:
   - Run Command Prompt as Administrator (Windows)
   - Check file/folder permissions
   - Ensure user has write access to project directory

### Database-Specific Troubleshooting

#### SQLite Issues
- **Database locked**: Close all connections, restart application
- **File permissions**: Ensure write access to database directory
- **Corrupted database**: Restore from backup or recreate

#### PostgreSQL Issues
- **Connection refused**: Check if PostgreSQL service is running
- **Authentication failed**: Verify user credentials and pg_hba.conf
- **Database does not exist**: Create database manually
- **Permission denied**: Grant proper privileges to user

#### MySQL Issues
- **Access denied**: Check user privileges and password
- **Connection timeout**: Check firewall and network settings
- **Character set issues**: Ensure UTF-8 encoding

### Performance Issues

1. **Slow Database Queries**:
   - Add database indexes
   - Optimize query patterns
   - Consider database connection pooling

2. **High Memory Usage**:
   - Check for memory leaks
   - Optimize data loading
   - Consider increasing server RAM

3. **Slow Frontend Loading**:
   - Enable gzip compression
   - Optimize images and assets
   - Use CDN for static files

### Getting Help

1. **Check Logs**:
   - Application logs: `./logs/erp_system.log`
   - Daily logs: `./logs/erp_YYYYMMDD.log`
   - Database logs: Check PostgreSQL/MySQL logs

2. **System Health**:
   - Health check: http://127.0.0.1:8000/health
   - API documentation: http://127.0.0.1:8000/docs
   - Database status: Check connection in health endpoint

3. **Debug Mode**:
   - Enable debug mode in `.env`: `DEBUG=true`
   - Check detailed error messages
   - Use development tools for frontend debugging

4. **Community Support**:
   - Check project documentation
   - Review GitHub issues
   - Contact support team

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