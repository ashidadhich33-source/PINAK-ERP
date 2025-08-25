# backend/app/models/company.py
from sqlalchemy import Column, String, Text, Boolean, Numeric, Integer, JSON
from .base import BaseModel

class Company(BaseModel):
    __tablename__ = "company"
    
    # Basic Information
    name = Column(String(200), nullable=False)
    display_name = Column(String(200), nullable=True)
    legal_name = Column(String(200), nullable=True)
    
    # Contact Information
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Business Information
    business_type = Column(String(50), nullable=True)  # retail, wholesale, service, etc.
    industry = Column(String(100), nullable=True)
    establishment_date = Column(String(10), nullable=True)  # YYYY-MM-DD
    
    # Tax Information
    gst_number = Column(String(15), nullable=True, unique=True)
    pan_number = Column(String(10), nullable=True)
    cin_number = Column(String(21), nullable=True)  # Corporate Identity Number
    tan_number = Column(String(10), nullable=True)  # Tax Deduction Account Number
    
    # Bank Information
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    account_number = Column(String(20), nullable=True)
    ifsc_code = Column(String(11), nullable=True)
    
    # Logo and Branding
    logo_path = Column(String(500), nullable=True)
    signature_path = Column(String(500), nullable=True)
    
    # Settings
    financial_year_start = Column(String(5), default="04-01")  # MM-DD format
    currency = Column(String(3), default="INR")
    decimal_places = Column(Integer, default=2)
    
    def __repr__(self):
        return f"<Company(name='{self.name}')>"

class SystemSettings(BaseModel):
    __tablename__ = "system_settings"
    
    # Key-value pairs for system settings
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(Text, nullable=True)
    setting_type = Column(String(20), default="string")  # string, integer, boolean, json
    module = Column(String(50), nullable=False)
    display_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    is_editable = Column(Boolean, default=True)
    
    def get_value(self):
        """Get typed value based on setting_type"""
        if self.setting_value is None:
            return None
            
        if self.setting_type == "boolean":
            return self.setting_value.lower() in ("true", "1", "yes")
        elif self.setting_type == "integer":
            try:
                return int(self.setting_value)
            except ValueError:
                return 0
        elif self.setting_type == "float":
            try:
                return float(self.setting_value)
            except ValueError:
                return 0.0
        elif self.setting_type == "json":
            try:
                import json
                return json.loads(self.setting_value)
            except:
                return {}
        else:  # string
            return self.setting_value
    
    def set_value(self, value):
        """Set value with proper type conversion"""
        if self.setting_type == "json":
            import json
            self.setting_value = json.dumps(value)
        else:
            self.setting_value = str(value)
    
    def __repr__(self):
        return f"<SystemSettings(key='{self.setting_key}', value='{self.setting_value}')>"

class FinancialYear(BaseModel):
    __tablename__ = "financial_year"
    
    year_name = Column(String(10), nullable=False, unique=True)  # e.g., "2024-25"
    start_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    end_date = Column(String(10), nullable=False)    # YYYY-MM-DD
    is_current = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<FinancialYear(year='{self.year_name}')>"