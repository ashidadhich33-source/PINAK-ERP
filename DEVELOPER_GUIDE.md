# 👨‍💻 **Enterprise ERP System - Developer Guide**

## 📋 **Table of Contents**

1. [Architecture Overview](#architecture-overview)
2. [Development Environment](#development-environment)
3. [Code Structure](#code-structure)
4. [Database Design](#database-design)
5. [API Development](#api-development)
6. [Authentication & Authorization](#authentication--authorization)
7. [Testing](#testing)
8. [Performance Optimization](#performance-optimization)
9. [Security](#security)
10. [Deployment](#deployment)
11. [Contributing](#contributing)

---

## 🏗️ **Architecture Overview**

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Load Balancer │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (Nginx)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Application   │
                       │   (FastAPI)     │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

### **Technology Stack**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React/Vue.js (planned)
- **Authentication**: JWT, OAuth2
- **Caching**: Redis
- **Message Queue**: Celery (optional)
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Kubernetes

### **Key Principles**
- **Microservices**: Modular architecture
- **RESTful API**: Standard REST endpoints
- **Database-First**: Database-driven design
- **Security-First**: Security by design
- **Performance**: Optimized for speed
- **Scalability**: Horizontal scaling

---

## 🛠️ **Development Environment**

### **1. Prerequisites**
```bash
# Python 3.9+
python --version

# PostgreSQL 13+
psql --version

# Redis 6.0+
redis-cli --version

# Git
git --version
```

### **2. Environment Setup**
```bash
# Clone repository
git clone https://github.com/your-org/enterprise-erp.git
cd enterprise-erp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **3. Database Setup**
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb enterprise_erp_dev

# Run migrations
alembic upgrade head

# Seed test data
python -m app.core.init_data
```

### **4. Redis Setup**
```bash
# Start Redis
sudo systemctl start redis

# Test connection
redis-cli ping
```

### **5. Development Server**
```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Gunicorn
gunicorn app.main:app -c gunicorn.conf.py
```

---

## 📁 **Code Structure**

### **Project Structure**
```
enterprise-erp/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py            # Database connection
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py        # Authentication & authorization
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── middleware.py      # Custom middleware
│   │   └── init_data.py       # Initial data setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py            # Base model
│   │   ├── user.py            # User models
│   │   ├── company.py         # Company models
│   │   ├── gst_state_codes.py # GST models
│   │   ├── financial_year_management.py
│   │   ├── chart_of_accounts.py
│   │   ├── advanced_inventory.py
│   │   ├── enhanced_item_master.py
│   │   ├── enhanced_purchase.py
│   │   ├── enhanced_sales.py
│   │   ├── double_entry_accounting.py
│   │   ├── discount_management.py
│   │   ├── report_studio.py
│   │   ├── loyalty_program.py
│   │   └── stock.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User schemas
│   │   ├── company.py         # Company schemas
│   │   └── common.py          # Common schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   ├── gst_calculation_service.py
│   │   ├── financial_year_service.py
│   │   ├── chart_of_accounts_service.py
│   │   ├── advanced_inventory_service.py
│   │   ├── enhanced_item_master_service.py
│   │   ├── enhanced_purchase_service.py
│   │   ├── enhanced_sales_service.py
│   │   ├── double_entry_accounting_service.py
│   │   ├── discount_management_service.py
│   │   ├── report_studio_service.py
│   │   ├── loyalty_program_service.py
│   │   ├── system_integration_service.py
│   │   └── performance_monitoring_service.py
│   └── api/
│       ├── __init__.py
│       └── endpoints/
│           ├── __init__.py
│           ├── auth.py         # Authentication endpoints
│           ├── companies.py    # Company endpoints
│           ├── gst.py          # GST endpoints
│           ├── financial_year.py
│           ├── chart_of_accounts.py
│           ├── advanced_inventory.py
│           ├── enhanced_item_master.py
│           ├── enhanced_purchase.py
│           ├── enhanced_sales.py
│           ├── double_entry_accounting.py
│           ├── discount_management.py
│           ├── report_studio.py
│           ├── loyalty_program.py
│           └── system_integration.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_auth.py           # Authentication tests
│   ├── test_companies.py      # Company tests
│   └── test_services.py        # Service tests
├── alembic/
│   ├── versions/              # Database migrations
│   └── env.py                 # Alembic configuration
├── scripts/
│   ├── backup_db.sh           # Database backup
│   ├── restore_db.sh          # Database restore
│   └── deploy.sh              # Deployment script
├── docs/
│   ├── API_DOCUMENTATION.md   # API documentation
│   ├── DEPLOYMENT_GUIDE.md    # Deployment guide
│   ├── USER_GUIDE.md          # User guide
│   └── DEVELOPER_GUIDE.md     # Developer guide
├── requirements.txt            # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── .env.example               # Environment variables example
├── .gitignore                 # Git ignore file
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── gunicorn.conf.py           # Gunicorn configuration
├── nginx.conf                 # Nginx configuration
└── README.md                  # Project README
```

### **Code Organization Principles**
1. **Separation of Concerns**: Models, services, and endpoints are separate
2. **Dependency Injection**: Services are injected into endpoints
3. **Error Handling**: Centralized error handling
4. **Logging**: Structured logging throughout
5. **Testing**: Comprehensive test coverage
6. **Documentation**: Inline documentation

---

## 🗄️ **Database Design**

### **Database Schema**
```sql
-- Core tables
CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_code VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),
    gst_number VARCHAR(15),
    pan_number VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    company_id INTEGER REFERENCES company(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Multi-tenancy support
CREATE TABLE user_company (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_id INTEGER REFERENCES company(id),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Database Relationships**
```python
# SQLAlchemy relationships
class Company(Base):
    __tablename__ = "company"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    users = relationship("User", back_populates="company")
    user_companies = relationship("UserCompany", back_populates="company")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company.id"))
    company = relationship("Company", back_populates="users")
    companies = relationship("UserCompany", back_populates="user")
```

### **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current
alembic history
```

---

## 🔌 **API Development**

### **FastAPI Application Structure**
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, companies, gst
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import setup_middlewares

app = FastAPI(
    title="Enterprise ERP System",
    description="Comprehensive business management solution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
setup_middlewares(app)

# Exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(gst.router, prefix="/api/v1/gst", tags=["GST"])
```

### **Endpoint Development**
```python
# app/api/endpoints/companies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services.company_service import company_service
from app.core.security import get_current_user, require_permission

router = APIRouter()

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    current_user: User = Depends(require_permission("company.create")),
    db: Session = Depends(get_db)
):
    """Create a new company"""
    try:
        new_company = company_service.create_company(
            db=db,
            company_data=company,
            user_id=current_user.id
        )
        return new_company
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("company.read")),
    db: Session = Depends(get_db)
):
    """Get list of companies"""
    companies = company_service.get_companies(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return companies
```

### **Pydantic Schemas**
```python
# app/schemas/company.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class CompanyBase(BaseModel):
    company_name: str
    company_code: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

---

## 🔐 **Authentication & Authorization**

### **JWT Authentication**
```python
# app/core/security.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
```

### **Role-Based Access Control**
```python
# app/core/security.py
from functools import wraps

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required permission
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def has_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    # Super users have all permissions
    if user.is_superuser:
        return True
    
    # Check user's role permissions
    user_permissions = get_user_permissions(user)
    return permission in user_permissions

def get_user_permissions(user: User) -> List[str]:
    """Get user's permissions based on role"""
    role_permissions = {
        "admin": [
            "company.create", "company.read", "company.update", "company.delete",
            "user.create", "user.read", "user.update", "user.delete",
            "gst.create", "gst.read", "gst.update", "gst.delete"
        ],
        "manager": [
            "company.read", "company.update",
            "user.read", "user.update",
            "gst.read", "gst.update"
        ],
        "user": [
            "company.read",
            "user.read",
            "gst.read"
        ]
    }
    
    return role_permissions.get(user.role, [])
```

---

## 🧪 **Testing**

### **Test Configuration**
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword"
    }
```

### **Unit Tests**
```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token, verify_password, get_password_hash

def test_create_user(client, test_user):
    """Test user creation"""
    response = client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "id" in data

def test_login_user(client, test_user):
    """Test user login"""
    # Create user first
    client.post("/api/v1/auth/register", json=test_user)
    
    # Login
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint(client, test_user):
    """Test protected endpoint access"""
    # Create user and get token
    client.post("/api/v1/auth/register", json=test_user)
    login_response = client.post("/api/v1/auth/login", data={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/companies", headers=headers)
    assert response.status_code == 200
```

### **Integration Tests**
```python
# tests/test_companies.py
import pytest
from fastapi.testclient import TestClient

def test_create_company(client, test_user, auth_headers):
    """Test company creation"""
    company_data = {
        "company_name": "Test Company",
        "company_code": "TEST",
        "email": "company@example.com",
        "phone": "+1234567890"
    }
    
    response = client.post(
        "/api/v1/companies",
        json=company_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == company_data["company_name"]
    assert data["company_code"] == company_data["company_code"]

def test_get_companies(client, auth_headers):
    """Test getting companies list"""
    response = client.get("/api/v1/companies", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

### **Service Tests**
```python
# tests/test_services.py
import pytest
from app.services.company_service import company_service
from app.schemas.company import CompanyCreate

def test_create_company(db_session, test_user):
    """Test company creation service"""
    company_data = CompanyCreate(
        company_name="Test Company",
        company_code="TEST",
        email="company@example.com"
    )
    
    company = company_service.create_company(
        db=db_session,
        company_data=company_data,
        user_id=test_user.id
    )
    
    assert company.company_name == company_data.company_name
    assert company.company_code == company_data.company_code
    assert company.email == company_data.email
```

---

## ⚡ **Performance Optimization**

### **Database Optimization**
```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/enterprise_erp"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Connection pooling
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **Query Optimization**
```python
# app/services/company_service.py
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import func, desc, asc

def get_companies_with_users(db: Session, skip: int = 0, limit: int = 100):
    """Get companies with users using eager loading"""
    return db.query(Company)\
        .options(joinedload(Company.users))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_company_stats(db: Session, company_id: int):
    """Get company statistics with optimized queries"""
    stats = db.query(
        func.count(User.id).label('user_count'),
        func.count(Customer.id).label('customer_count'),
        func.count(Item.id).label('item_count')
    ).filter(
        User.company_id == company_id,
        Customer.company_id == company_id,
        Item.company_id == company_id
    ).first()
    
    return {
        'user_count': stats.user_count,
        'customer_count': stats.customer_count,
        'item_count': stats.item_count
    }
```

### **Caching**
```python
# app/core/cache.py
import redis
from typing import Optional, Any
import json
import pickle

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        if value:
            return pickle.loads(value)
        return None
    except Exception:
        return None

def cache_set(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache"""
    try:
        redis_client.setex(key, expire, pickle.dumps(value))
        return True
    except Exception:
        return False

def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception:
        return False

# Cache decorator
def cached(expire: int = 3600):
    """Cache decorator for functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator
```

### **Async Operations**
```python
# app/services/async_service.py
import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class AsyncService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def process_bulk_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process bulk data asynchronously"""
        tasks = []
        for item in data:
            task = asyncio.create_task(self.process_item(item))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual item"""
        # Simulate processing
        await asyncio.sleep(0.1)
        return {"processed": True, "item": item}
    
    async def parallel_database_operations(self, operations: List[callable]) -> List[Any]:
        """Execute database operations in parallel"""
        loop = asyncio.get_event_loop()
        tasks = []
        
        for operation in operations:
            task = loop.run_in_executor(self.executor, operation)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

---

## 🔒 **Security**

### **Input Validation**
```python
# app/schemas/validation.py
from pydantic import BaseModel, validator, EmailStr
from typing import Optional
import re

class CompanyCreate(BaseModel):
    company_name: str
    company_code: str
    email: EmailStr
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    
    @validator('company_name')
    def validate_company_name(cls, v):
        if len(v) < 2:
            raise ValueError('Company name must be at least 2 characters')
        if len(v) > 255:
            raise ValueError('Company name must be less than 255 characters')
        return v.strip()
    
    @validator('company_code')
    def validate_company_code(cls, v):
        if not re.match(r'^[A-Z0-9_]+$', v):
            raise ValueError('Company code must contain only uppercase letters, numbers, and underscores')
        if len(v) < 2:
            raise ValueError('Company code must be at least 2 characters')
        return v.upper()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('gst_number')
    def validate_gst_number(cls, v):
        if v and not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', v):
            raise ValueError('Invalid GST number format')
        return v
    
    @validator('pan_number')
    def validate_pan_number(cls, v):
        if v and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v):
            raise ValueError('Invalid PAN number format')
        return v
```

### **SQL Injection Prevention**
```python
# app/core/security.py
from sqlalchemy import text
from sqlalchemy.orm import Session

def safe_query(db: Session, query: str, params: dict = None):
    """Execute safe parameterized query"""
    try:
        result = db.execute(text(query), params or {})
        return result.fetchall()
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database query failed"
        )

# Example usage
def get_companies_by_name(db: Session, name: str):
    """Get companies by name using safe query"""
    query = "SELECT * FROM company WHERE company_name ILIKE :name"
    params = {"name": f"%{name}%"}
    return safe_query(db, query, params)
```

### **Rate Limiting**
```python
# app/core/rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Rate limit decorator
def rate_limit(requests: int, window: int):
    """Rate limit decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check rate limit
            if not limiter.check_rate_limit(requests, window):
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in endpoints
@router.post("/")
@limiter.limit("5/minute")
async def create_company(
    request: Request,
    company: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create company with rate limiting"""
    # Implementation
    pass
```

### **Data Encryption**
```python
# app/core/encryption.py
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            return encrypted_data

# Usage in models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(20))
    
    def set_phone(self, phone: str):
        """Set encrypted phone number"""
        if phone:
            encryption = DataEncryption()
            self.phone = encryption.encrypt(phone)
    
    def get_phone(self) -> str:
        """Get decrypted phone number"""
        if self.phone:
            encryption = DataEncryption()
            return encryption.decrypt(self.phone)
        return None
```

---

## 🚀 **Deployment**

### **Docker Configuration**
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 erpuser && chown -R erpuser:erpuser /app
USER erpuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://erp_user:secure_password@db:5432/enterprise_erp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=enterprise_erp
      - POSTGRES_USER=erp_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

### **Kubernetes Deployment**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enterprise-erp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: enterprise-erp
  template:
    metadata:
      labels:
        app: enterprise-erp
    spec:
      containers:
      - name: app
        image: enterprise-erp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: erp-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: erp-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Write** tests for your changes
5. **Run** the test suite
6. **Commit** your changes
7. **Push** to your fork
8. **Create** a pull request

### **Code Standards**
- **PEP 8**: Follow Python PEP 8 style guide
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Document all functions and classes
- **Tests**: Write tests for all new features
- **Commits**: Use conventional commit messages

### **Pull Request Process**
1. **Description**: Provide clear description of changes
2. **Tests**: Ensure all tests pass
3. **Documentation**: Update documentation if needed
4. **Review**: Address reviewer feedback
5. **Merge**: Merge after approval

### **Issue Reporting**
- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Security Issues**: Report security issues privately
- **Documentation**: Report documentation issues

---

## 📚 **Additional Resources**

### **Documentation**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

### **Tools**
- **IDE**: VS Code, PyCharm, or any Python IDE
- **Database**: pgAdmin, DBeaver, or any PostgreSQL client
- **API Testing**: Postman, Insomnia, or curl
- **Monitoring**: Prometheus, Grafana, or similar

### **Community**
- **GitHub**: [Repository](https://github.com/your-org/enterprise-erp)
- **Discord**: [Community Server](https://discord.gg/enterprise-erp)
- **Stack Overflow**: Tag `enterprise-erp`
- **Reddit**: r/enterpriseerp

---

## 🔗 **Related Documentation**

- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [User Guide](USER_GUIDE.md)
- [Database Schema](DATABASE_SCHEMA.md)