# backend/app/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    app_name: str = "ERP System"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Settings
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 4
    
    # Database Settings
    database_url: str = "sqlite:///./database/erp_system.db"
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    
    # WhatsApp Settings
    whatsapp_access_token: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_business_account_id: Optional[str] = None
    
    # GST Settings
    gst_enabled: bool = True
    gst_round_off: float = 0.01
    
    # Company Settings
    company_name: str = "Your Company Name"
    company_address: str = ""
    company_phone: str = ""
    company_email: str = ""
    company_gst_number: str = ""
    financial_year: str = "2024-25"
    
    # File Paths
    upload_dir: str = "uploads"
    log_dir: str = "logs"
    backup_dir: str = "backups"
    
    # Create directories
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_directories()
    
    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            Path("database"),
            Path(self.upload_dir),
            Path(self.log_dir),
            Path(self.backup_dir),
            Path("config")
        ]
        for dir_path in dirs:
            dir_path.mkdir(exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Environment-specific configurations
def get_database_url():
    """Get database URL based on environment"""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    return settings.database_url