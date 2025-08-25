# backend/app/config.py
import os
import secrets
from pathlib import Path
from typing import Optional, Any, Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "ERP System"
    app_version: str = "1.0.0"
    app_description: str = "Complete ERP System with Inventory, Sales, and Accounting"
    debug: bool = Field(default=True, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    
    # API Settings
    api_prefix: str = "/api/v1"
    api_title: str = "ERP System API"
    
    # Server Settings
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    reload: bool = Field(default=True, env="RELOAD")
    
    # Database Settings
    database_type: str = Field(default="sqlite", env="DATABASE_TYPE")
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # SQLite specific
    sqlite_path: str = Field(default="./database/erp_system.db", env="SQLITE_PATH")
    
    # PostgreSQL specific
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="erp_system", env="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="", env="POSTGRES_PASSWORD")
    
    # Security Settings
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=10080, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 7 days
    refresh_token_expire_minutes: int = Field(default=43200, env="REFRESH_TOKEN_EXPIRE_MINUTES")  # 30 days
    
    # Password Policy
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_uppercase: bool = Field(default=True, env="PASSWORD_REQUIRE_UPPERCASE")
    password_require_lowercase: bool = Field(default=True, env="PASSWORD_REQUIRE_LOWERCASE")
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_special: bool = Field(default=False, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Security Features
    max_login_attempts: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    lockout_duration_minutes: int = Field(default=30, env="LOCKOUT_DURATION_MINUTES")
    enable_2fa: bool = Field(default=False, env="ENABLE_2FA")
    
    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # WhatsApp Settings
    whatsapp_enabled: bool = Field(default=False, env="WHATSAPP_ENABLED")
    whatsapp_access_token: str = Field(default="", env="WHATSAPP_ACCESS_TOKEN")
    whatsapp_phone_number_id: str = Field(default="", env="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id: str = Field(default="", env="WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_webhook_verify_token: str = Field(default="erp_webhook_token", env="WHATSAPP_WEBHOOK_VERIFY_TOKEN")
    whatsapp_api_version: str = Field(default="v18.0", env="WHATSAPP_API_VERSION")
    
    # WhatsApp Templates
    whatsapp_otp_template: str = Field(default="otp_template", env="WHATSAPP_OTP_TEMPLATE")
    whatsapp_invoice_template: str = Field(default="invoice_template", env="WHATSAPP_INVOICE_TEMPLATE")
    whatsapp_return_template: str = Field(default="return_template", env="WHATSAPP_RETURN_TEMPLATE")
    
    # Email Settings
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="", env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="ERP System", env="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    
    # SMS Settings
    sms_enabled: bool = Field(default=False, env="SMS_ENABLED")
    sms_api_key: str = Field(default="", env="SMS_API_KEY")
    sms_sender_id: str = Field(default="ERPAPP", env="SMS_SENDER_ID")
    sms_api_url: str = Field(default="", env="SMS_API_URL")
    
    # GST Settings
    gst_enabled: bool = Field(default=True, env="GST_ENABLED")
    gst_round_off: float = Field(default=0.01, env="GST_ROUND_OFF")
    default_gst_rate: float = Field(default=18.0, env="DEFAULT_GST_RATE")
    gst_rate_5: float = Field(default=5.0, env="GST_RATE_5")
    gst_rate_12: float = Field(default=12.0, env="GST_RATE_12")
    gst_rate_18: float = Field(default=18.0, env="GST_RATE_18")
    gst_rate_28: float = Field(default=28.0, env="GST_RATE_28")
    gst_threshold_amount: float = Field(default=999.00, env="GST_THRESHOLD_AMOUNT")
    
    # Company Settings
    company_name: str = Field(default="Your Company Name", env="COMPANY_NAME")
    company_address: str = Field(default="", env="COMPANY_ADDRESS")
    company_city: str = Field(default="", env="COMPANY_CITY")
    company_state: str = Field(default="", env="COMPANY_STATE")
    company_pincode: str = Field(default="", env="COMPANY_PINCODE")
    company_phone: str = Field(default="", env="COMPANY_PHONE")
    company_email: str = Field(default="", env="COMPANY_EMAIL")
    company_website: str = Field(default="", env="COMPANY_WEBSITE")
    company_gst_number: str = Field(default="", env="COMPANY_GST_NUMBER")
    company_pan_number: str = Field(default="", env="COMPANY_PAN_NUMBER")
    company_cin_number: str = Field(default="", env="COMPANY_CIN_NUMBER")
    
    # Financial Settings
    financial_year_start: str = Field(default="04-01", env="FINANCIAL_YEAR_START")
    financial_year_end: str = Field(default="03-31", env="FINANCIAL_YEAR_END")
    currency: str = Field(default="INR", env="CURRENCY")
    currency_symbol: str = Field(default="₹", env="CURRENCY_SYMBOL")
    decimal_places: int = Field(default=2, env="DECIMAL_PLACES")
    
    # Loyalty Settings
    loyalty_enabled: bool = Field(default=True, env="LOYALTY_ENABLED")
    loyalty_points_per_100: int = Field(default=1, env="LOYALTY_POINTS_PER_100")
    loyalty_point_value: float = Field(default=0.25, env="LOYALTY_POINT_VALUE")
    loyalty_min_redemption: int = Field(default=100, env="LOYALTY_MIN_REDEMPTION")
    loyalty_points_expiry_days: int = Field(default=365, env="LOYALTY_POINTS_EXPIRY_DAYS")
    
    # Inventory Settings
    enable_negative_stock: bool = Field(default=False, env="ENABLE_NEGATIVE_STOCK")
    low_stock_threshold: int = Field(default=10, env="LOW_STOCK_THRESHOLD")
    enable_batch_tracking: bool = Field(default=False, env="ENABLE_BATCH_TRACKING")
    enable_serial_tracking: bool = Field(default=False, env="ENABLE_SERIAL_TRACKING")
    
    # Backup Settings
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="daily", env="BACKUP_SCHEDULE")  # daily, weekly, monthly
    backup_time: str = Field(default="02:00", env="BACKUP_TIME")
    backup_retention_days: int = Field(default=7, env="BACKUP_RETENTION_DAYS")
    backup_location: str = Field(default="./backups", env="BACKUP_LOCATION")
    
    # File Storage Settings
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=10, env="MAX_UPLOAD_SIZE_MB")
    allowed_upload_extensions: List[str] = Field(
        default=["jpg", "jpeg", "png", "pdf", "xlsx", "xls", "csv"],
        env="ALLOWED_UPLOAD_EXTENSIONS"
    )
    
    # Logging Settings
    log_dir: str = Field(default="logs", env="LOG_DIR")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    log_rotation: str = Field(default="daily", env="LOG_ROTATION")
    log_retention_days: int = Field(default=30, env="LOG_RETENTION_DAYS")
    
    # Cache Settings
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Payment Gateway Settings
    payment_gateway_enabled: bool = Field(default=False, env="PAYMENT_GATEWAY_ENABLED")
    razorpay_key_id: str = Field(default="", env="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(default="", env="RAZORPAY_KEY_SECRET")
    paytm_merchant_id: str = Field(default="", env="PAYTM_MERCHANT_ID")
    paytm_merchant_key: str = Field(default="", env="PAYTM_MERCHANT_KEY")
    
    # External Integrations
    tally_integration_enabled: bool = Field(default=False, env="TALLY_INTEGRATION_ENABLED")
    tally_server_url: str = Field(default="", env="TALLY_SERVER_URL")
    einvoice_enabled: bool = Field(default=False, env="EINVOICE_ENABLED")
    einvoice_api_url: str = Field(default="", env="EINVOICE_API_URL")
    einvoice_api_key: str = Field(default="", env="EINVOICE_API_KEY")
    
    # Monitoring Settings
    sentry_enabled: bool = Field(default=False, env="SENTRY_ENABLED")
    sentry_dsn: str = Field(default="", env="SENTRY_DSN")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Timezone Settings
    timezone: str = Field(default="Asia/Kolkata", env="TIMEZONE")
    date_format: str = Field(default="%d-%m-%Y", env="DATE_FORMAT")
    datetime_format: str = Field(default="%d-%m-%Y %H:%M:%S", env="DATETIME_FORMAT")
    
    @validator("database_url", pre=True)
    def construct_database_url(cls, v, values):
        if v:
            return v
        
        db_type = values.get("database_type", "sqlite")
        if db_type == "sqlite":
            return f"sqlite:///{values.get('sqlite_path', './database/erp_system.db')}"
        elif db_type == "postgresql":
            host = values.get("postgres_host", "localhost")
            port = values.get("postgres_port", 5432)
            db = values.get("postgres_db", "erp_system")
            user = values.get("postgres_user", "postgres")
            password = values.get("postgres_password", "")
            return f"postgresql://{user}:{password}@{host}:{port}/{db}"
        else:
            return f"sqlite:///./database/erp_system.db"
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            Path("database"),
            Path(self.upload_dir),
            Path(self.log_dir),
            Path(self.backup_location),
            Path("config"),
            Path("temp")
        ]
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True, parents=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()

# Export commonly used settings
DATABASE_URL = settings.database_url
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
