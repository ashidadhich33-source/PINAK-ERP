# 🚀 **Enterprise ERP System - Deployment Guide**

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Production Configuration](#production-configuration)
6. [Security Configuration](#security-configuration)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 **Prerequisites**

### **System Requirements**
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Storage**: 100GB+ SSD recommended
- **Network**: Stable internet connection

### **Software Requirements**
- **Python**: 3.9+
- **PostgreSQL**: 13+
- **Redis**: 6.0+ (for caching)
- **Nginx**: 1.18+ (for reverse proxy)
- **Docker**: 20.10+ (optional)
- **Git**: 2.25+

---

## 🌍 **Environment Setup**

### **1. Create Virtual Environment**
```bash
# Create project directory
mkdir enterprise-erp
cd enterprise-erp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **2. Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib redis-server nginx

# Install system dependencies (CentOS/RHEL)
sudo yum update
sudo yum install -y postgresql-server postgresql-contrib redis nginx
```

### **3. Environment Variables**
```bash
# Create environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Environment Variables:**
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/enterprise_erp
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=enterprise_erp
DATABASE_USER=erp_user
DATABASE_PASSWORD=secure_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# Security Configuration
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=Enterprise ERP
APP_VERSION=1.0.0
DEBUG=False
LOG_LEVEL=INFO

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=True

# File Storage
UPLOAD_DIR=/var/enterprise-erp/uploads
MAX_FILE_SIZE=10485760  # 10MB

# API Configuration
API_V1_STR=/api/v1
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## 🗄️ **Database Setup**

### **1. PostgreSQL Installation**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### **2. Database Configuration**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE enterprise_erp;
CREATE USER erp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE enterprise_erp TO erp_user;
ALTER USER erp_user CREATEDB;
\q
```

### **3. Database Migration**
```bash
# Run database migrations
python -m alembic upgrade head

# Create initial data
python -m app.core.init_data
```

### **4. Database Optimization**
```sql
-- Connect to database
psql -U erp_user -d enterprise_erp

-- Create indexes for performance
CREATE INDEX idx_company_id ON users(company_id);
CREATE INDEX idx_customer_company ON customers(company_id);
CREATE INDEX idx_item_company ON items(company_id);
CREATE INDEX idx_sale_company ON sale_bill(company_id);
CREATE INDEX idx_purchase_company ON purchase_bill(company_id);

-- Analyze tables for better performance
ANALYZE;
```

---

## 🚀 **Application Deployment**

### **1. Using Gunicorn (Recommended)**
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
accesslog = "/var/log/enterprise-erp/access.log"
errorlog = "/var/log/enterprise-erp/error.log"
loglevel = "info"
EOF

# Start application
gunicorn app.main:app -c gunicorn.conf.py
```

### **2. Using Docker (Optional)**
```dockerfile
# Dockerfile
FROM python:3.9-slim

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

# Start application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

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

### **3. Using Systemd Service**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/enterprise-erp.service
```

```ini
[Unit]
Description=Enterprise ERP System
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=erpuser
Group=erpuser
WorkingDirectory=/opt/enterprise-erp
Environment=PATH=/opt/enterprise-erp/venv/bin
ExecStart=/opt/enterprise-erp/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable enterprise-erp
sudo systemctl start enterprise-erp
sudo systemctl status enterprise-erp
```

---

## ⚙️ **Production Configuration**

### **1. Nginx Configuration**
```nginx
# /etc/nginx/sites-available/enterprise-erp
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

    # API Routes
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Authentication Routes
    location /api/v1/auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static Files
    location /static/ {
        alias /opt/enterprise-erp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # File Uploads
    location /uploads/ {
        alias /var/enterprise-erp/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Health Check
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

### **2. SSL Certificate Setup**
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **3. Firewall Configuration**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 🔒 **Security Configuration**

### **1. Database Security**
```sql
-- Create read-only user for reports
CREATE USER erp_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE enterprise_erp TO erp_readonly;
GRANT USAGE ON SCHEMA public TO erp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO erp_readonly;

-- Set up row-level security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_company_policy ON users
    FOR ALL TO erp_user
    USING (company_id = current_setting('app.current_company_id')::int);
```

### **2. Application Security**
```python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
```

### **3. File Upload Security**
```python
# app/core/security.py
import os
import magic
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.xlsx', '.csv'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file):
    # Check file extension
    if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise ValueError("File type not allowed")
    
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    # Check MIME type
    file.seek(0)
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    if mime_type not in ['image/jpeg', 'image/png', 'application/pdf', 'application/vnd.ms-excel']:
        raise ValueError("Invalid file type")
    
    return secure_filename(file.filename)
```

---

## 📊 **Monitoring Setup**

### **1. Application Monitoring**
```python
# app/core/monitoring.py
import logging
import time
from functools import wraps
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

def monitor_requests(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='GET', endpoint=func.__name__, status='200').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method='GET', endpoint=func.__name__, status='500').inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper
```

### **2. Logging Configuration**
```python
# app/core/logging.py
import logging
import logging.config
from datetime import datetime

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/enterprise-erp/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'error_file': {
            'level': 'ERROR',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/enterprise-erp/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'app': {
            'handlers': ['default', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### **3. Health Check Endpoint**
```python
# app/api/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "database": db_status,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
    }
```

---

## 💾 **Backup & Recovery**

### **1. Database Backup**
```bash
#!/bin/bash
# backup_db.sh

# Configuration
DB_NAME="enterprise_erp"
DB_USER="erp_user"
BACKUP_DIR="/var/backups/enterprise-erp"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: $BACKUP_DIR/db_backup_$DATE.sql.gz"
```

### **2. Application Backup**
```bash
#!/bin/bash
# backup_app.sh

# Configuration
APP_DIR="/opt/enterprise-erp"
BACKUP_DIR="/var/backups/enterprise-erp"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C $APP_DIR .

# Backup uploads
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz -C /var/enterprise-erp/uploads .

# Keep only last 7 days of backups
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "uploads_backup_*.tar.gz" -mtime +7 -delete

echo "Application backup completed: $BACKUP_DIR/app_backup_$DATE.tar.gz"
```

### **3. Automated Backup**
```bash
# Add to crontab
crontab -e

# Daily backups at 2 AM
0 2 * * * /opt/enterprise-erp/scripts/backup_db.sh
0 2 * * * /opt/enterprise-erp/scripts/backup_app.sh

# Weekly full backup
0 1 * * 0 /opt/enterprise-erp/scripts/full_backup.sh
```

### **4. Recovery Process**
```bash
#!/bin/bash
# restore_db.sh

# Configuration
DB_NAME="enterprise_erp"
DB_USER="erp_user"
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop application
sudo systemctl stop enterprise-erp

# Drop and recreate database
dropdb -h localhost -U $DB_USER $DB_NAME
createdb -h localhost -U $DB_USER $DB_NAME

# Restore database
gunzip -c $BACKUP_FILE | psql -h localhost -U $DB_USER -d $DB_NAME

# Start application
sudo systemctl start enterprise-erp

echo "Database restored from: $BACKUP_FILE"
```

---

## 📈 **Scaling**

### **1. Horizontal Scaling**
```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  app:
    build: .
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://erp_user:secure_password@db:5432/enterprise_erp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

### **2. Load Balancer Configuration**
```nginx
# nginx.conf
upstream app_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **3. Database Scaling**
```sql
-- Read replica setup
-- On master database
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 3;
ALTER SYSTEM SET max_replication_slots = 3;
SELECT pg_reload_conf();

-- Create replication user
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator_password';

-- On replica database
pg_basebackup -h master_host -D /var/lib/postgresql/data -U replicator -v -P -W
```

---

## 🔧 **Troubleshooting**

### **1. Common Issues**

#### **Database Connection Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U erp_user -d enterprise_erp -c "SELECT 1;"

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### **Application Issues**
```bash
# Check application status
sudo systemctl status enterprise-erp

# Check application logs
sudo journalctl -u enterprise-erp -f

# Check application logs
tail -f /var/log/enterprise-erp/error.log
```

#### **Nginx Issues**
```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### **2. Performance Issues**

#### **Database Performance**
```sql
-- Check slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### **Application Performance**
```bash
# Check system resources
htop
iostat -x 1
free -h
df -h

# Check application metrics
curl http://localhost:8000/metrics
```

### **3. Security Issues**

#### **SSL Certificate Issues**
```bash
# Check SSL certificate
openssl x509 -in /etc/nginx/ssl/cert.pem -text -noout

# Test SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

#### **Firewall Issues**
```bash
# Check firewall status
sudo ufw status
sudo firewall-cmd --list-all

# Test connectivity
telnet yourdomain.com 443
curl -I https://yourdomain.com
```

---

## 📞 **Support**

For deployment support and troubleshooting:

1. **Documentation**: Check this guide and API documentation
2. **Logs**: Check application and system logs
3. **Health Check**: Use `/health` endpoint to check system status
4. **Monitoring**: Use system metrics endpoint for performance monitoring
5. **Backup**: Ensure regular backups are in place

---

## 🔗 **Related Documentation**

- [API Documentation](API_DOCUMENTATION.md)
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Database Schema](DATABASE_SCHEMA.md)