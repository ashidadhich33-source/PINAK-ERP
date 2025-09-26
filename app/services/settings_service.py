"""
System Settings and Configuration Management Service
Handles all system-wide configurations for the ERP
"""

import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.company import Company
from ..core.security import get_password_hash

logger = logging.getLogger(__name__)

class SystemSettingsService:
    """Manages all system configuration settings"""
    
    def __init__(self):
        self.config_path = Path('config/settings.ini')
        self.templates_path = Path('config/templates')
        self.config = configparser.ConfigParser()
        self.load_config()
        
        # Ensure directories exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.templates_path.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        """Load configuration from INI file"""
        if self.config_path.exists():
            self.config.read(self.config_path)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config['database'] = {
            'type': 'sqlite',
            'path': 'database/erp_system.db'
        }
        
        self.config['server'] = {
            'host': '127.0.0.1',
            'port': '8000',
            'workers': '4',
            'debug': 'false'
        }
        
        self.config['security'] = {
            'secret_key': 'change-this-secret-key-in-production',
            'algorithm': 'HS256',
            'access_token_expire_minutes': '10080',
            'password_min_length': '8',
            'max_login_attempts': '5',
            'lockout_duration_minutes': '30'
        }
        
        self.config['business'] = {
            'financial_year_start': '04-01',  # April 1st
            'financial_year_end': '03-31',    # March 31st
            'default_payment_terms': '30',    # days
            'low_stock_threshold': '10',
            'invoice_prefix': 'INV',
            'return_prefix': 'RET',
            'purchase_prefix': 'PUR',
            'expense_prefix': 'EXP'
        }
        
        self.config['gst'] = {
            'enable': 'true',
            'round_off': '0.01',
            'gst_5_max_price': '999',
            'gst_5_rate': '5',
            'gst_12_rate': '12',
            'default_tax_type': 'local',  # local or interstate
            'hsn_code_mandatory': 'false'
        }
        
        self.config['loyalty'] = {
            'enable': 'true',
            'points_per_100': '1',
            'points_value': '0.25',  # 1 point = 0.25 rupees
            'min_redemption_points': '100',
            'points_expiry_days': '365',
            'auto_upgrade_grades': 'true'
        }
        
        self.config['whatsapp'] = {
            'enable': 'false',
            'access_token': '',
            'phone_number_id': '',
            'business_account_id': '',
            'send_invoice': 'true',
            'send_birthday_wishes': 'true',
            'send_promotional': 'false'
        }
        
        self.config['email'] = {
            'enable': 'false',
            'smtp_host': 'smtp.gmail.com',
            'smtp_port': '587',
            'smtp_user': '',
            'smtp_password': '',
            'from_email': '',
            'from_name': 'ERP System'
        }
        
        self.config['backup'] = {
            'auto_backup': 'true',
            'backup_time': '02:00',
            'max_backups': '7',
            'backup_dir': 'backups',
            'include_logs': 'false'
        }
        
        self.config['print'] = {
            'paper_size': 'A4',
            'margin_top': '10',
            'margin_bottom': '10',
            'margin_left': '10',
            'margin_right': '10',
            'show_logo': 'true',
            'show_terms': 'true',
            'default_copies': '1'
        }
        
        self.config['system'] = {
            'timezone': 'Asia/Kolkata',
            'date_format': '%d/%m/%Y',
            'currency': 'INR',
            'currency_symbol': '₹',
            'decimal_places': '2',
            'thousands_separator': ',',
            'language': 'en'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to INI file"""
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Get all settings in a section"""
        if section in self.config:
            return dict(self.config[section])
        return {}
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            value = self.config.get(section, key)
            # Try to parse as JSON for complex types
            try:
                return json.loads(value)
            except:
                return value
        except:
            return default
    
    def update_setting(self, section: str, key: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            # Convert to string, use JSON for complex types
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            else:
                value = str(value)
            
            self.config[section][key] = value
            self.save_config()
            logger.info(f"Updated setting: {section}.{key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update setting: {e}")
            return False
    
    def update_section(self, section: str, settings: Dict[str, Any]) -> bool:
        """Update all settings in a section"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            for key, value in settings.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                else:
                    value = str(value)
                self.config[section][key] = value
            
            self.save_config()
            logger.info(f"Updated section: {section}")
            return True
        except Exception as e:
            logger.error(f"Failed to update section: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Dict[str, str]]:
        """Get all settings organized by section"""
        settings = {}
        for section in self.config.sections():
            settings[section] = dict(self.config[section])
        return settings
    
    def reset_section(self, section: str) -> bool:
        """Reset a section to default values"""
        try:
            self.create_default_config()
            default_config = configparser.ConfigParser()
            default_config.read(self.config_path)
            
            if section in default_config:
                self.config[section] = default_config[section]
                self.save_config()
                logger.info(f"Reset section to defaults: {section}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to reset section: {e}")
            return False
    
    def validate_settings(self) -> Dict[str, List[str]]:
        """Validate all settings and return errors"""
        errors = {}
        
        # Validate database settings
        if self.config.get('database', 'type') not in ['sqlite', 'postgresql']:
            errors.setdefault('database', []).append('Invalid database type')
        
        # Validate security settings
        try:
            token_expire = int(self.config.get('security', 'access_token_expire_minutes'))
            if token_expire < 1:
                errors.setdefault('security', []).append('Token expire time must be positive')
        except:
            errors.setdefault('security', []).append('Invalid token expire time')
        
        # Validate GST settings
        try:
            gst_5 = float(self.config.get('gst', 'gst_5_rate'))
            gst_12 = float(self.config.get('gst', 'gst_12_rate'))
            if gst_5 < 0 or gst_12 < 0:
                errors.setdefault('gst', []).append('GST rates must be positive')
        except:
            errors.setdefault('gst', []).append('Invalid GST rates')
        
        # Validate email settings if enabled
        if self.config.get('email', 'enable') == 'true':
            if not self.config.get('email', 'smtp_host'):
                errors.setdefault('email', []).append('SMTP host required when email enabled')
            if not self.config.get('email', 'from_email'):
                errors.setdefault('email', []).append('From email required when email enabled')
        
        return errors
    
    def export_settings(self, filepath: str = None) -> str:
        """Export settings to JSON file"""
        if not filepath:
            filepath = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        settings = self.get_all_settings()
        with open(filepath, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logger.info(f"Settings exported to: {filepath}")
        return filepath
    
    def import_settings(self, filepath: str) -> bool:
        """Import settings from JSON file"""
        try:
            with open(filepath, 'r') as f:
                settings = json.load(f)
            
            for section, section_settings in settings.items():
                self.update_section(section, section_settings)
            
            logger.info(f"Settings imported from: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False


class CompanySettingsService:
    """Manages company-specific settings"""
    
    @staticmethod
    def get_company_settings(db: Session) -> Dict[str, Any]:
        """Get current company settings"""
        company = db.query(Company).first()
        
        if not company:
            return {}
        
        return {
            'id': company.id,
            'name': company.name,
            'address': company.address,
            'city': company.city,
            'state': company.state,
            'pincode': company.pincode,
            'phone': company.phone,
            'email': company.email,
            'gstin': company.gstin,
            'pan': company.pan,
            'bank_name': company.bank_name,
            'bank_account': company.bank_account,
            'bank_ifsc': company.bank_ifsc,
            'logo_path': company.logo_path,
            'website': company.website,
            'terms_conditions': company.terms_conditions,
            'return_policy': company.return_policy,
            'created_at': company.created_at.isoformat() if company.created_at else None
        }
    
    @staticmethod
    def update_company_settings(db: Session, settings: Dict[str, Any]) -> bool:
        """Update company settings"""
        try:
            company = db.query(Company).first()
            
            if not company:
                # Create new company record
                company = Company()
                db.add(company)
            
            # Update fields
            for key, value in settings.items():
                if hasattr(company, key) and key not in ['id', 'created_at']:
                    setattr(company, key, value)
            
            company.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info("Company settings updated")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update company settings: {e}")
            return False


class PrintTemplateService:
    """Manages print templates for invoices, reports, etc."""
    
    def __init__(self):
        self.templates_dir = Path('config/templates')
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.default_templates = {
            'invoice': self._get_default_invoice_template(),
            'purchase': self._get_default_purchase_template(),
            'return': self._get_default_return_template(),
            'receipt': self._get_default_receipt_template()
        }
    
    def _get_default_invoice_template(self) -> str:
        """Get default invoice template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .header { text-align: center; margin-bottom: 20px; }
                .company-name { font-size: 24px; font-weight: bold; }
                .invoice-title { font-size: 18px; margin-top: 10px; }
                .info-section { margin-bottom: 20px; }
                .items-table { width: 100%; border-collapse: collapse; }
                .items-table th, .items-table td { border: 1px solid #ddd; padding: 8px; }
                .items-table th { background-color: #f2f2f2; }
                .totals { text-align: right; margin-top: 20px; }
                .footer { margin-top: 50px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="company-name">{{company_name}}</div>
                <div>{{company_address}}</div>
                <div>GSTIN: {{company_gstin}}</div>
                <div class="invoice-title">TAX INVOICE</div>
            </div>
            
            <div class="info-section">
                <table width="100%">
                    <tr>
                        <td>
                            <strong>Bill To:</strong><br>
                            {{customer_name}}<br>
                            {{customer_phone}}<br>
                            {{customer_address}}
                        </td>
                        <td align="right">
                            <strong>Invoice No:</strong> {{invoice_no}}<br>
                            <strong>Date:</strong> {{invoice_date}}<br>
                            <strong>Time:</strong> {{invoice_time}}
                        </td>
                    </tr>
                </table>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Sr.</th>
                        <th>Item Description</th>
                        <th>HSN</th>
                        <th>Qty</th>
                        <th>MRP</th>
                        <th>Disc%</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {{items_rows}}
                </tbody>
            </table>
            
            <div class="totals">
                <table align="right">
                    <tr><td>Subtotal:</td><td>₹{{subtotal}}</td></tr>
                    <tr><td>CGST:</td><td>₹{{cgst}}</td></tr>
                    <tr><td>SGST:</td><td>₹{{sgst}}</td></tr>
                    <tr><td>Round Off:</td><td>₹{{round_off}}</td></tr>
                    <tr><td><strong>Total:</strong></td><td><strong>₹{{total}}</strong></td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>{{terms_conditions}}</p>
                <p>Thank you for your business!</p>
            </div>
        </body>
        </html>
        """
    
    def _get_default_purchase_template(self) -> str:
        """Get default purchase template"""
        return """<!-- Purchase Bill Template -->"""
    
    def _get_default_return_template(self) -> str:
        """Get default return template"""
        return """<!-- Return Note Template -->"""
    
    def _get_default_receipt_template(self) -> str:
        """Get default receipt template"""
        return """<!-- Payment Receipt Template -->"""
    
    def get_template(self, template_type: str) -> str:
        """Get a specific template"""
        template_path = self.templates_dir / f"{template_type}.html"
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                return f.read()
        
        # Return default template if custom doesn't exist
        return self.default_templates.get(template_type, '')
    
    def save_template(self, template_type: str, content: str) -> bool:
        """Save a custom template"""
        try:
            template_path = self.templates_dir / f"{template_type}.html"
            with open(template_path, 'w') as f:
                f.write(content)
            logger.info(f"Template saved: {template_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def reset_template(self, template_type: str) -> bool:
        """Reset template to default"""
        try:
            template_path = self.templates_dir / f"{template_type}.html"
            if template_path.exists():
                template_path.unlink()
            logger.info(f"Template reset to default: {template_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset template: {e}")
            return False
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        templates = []
        
        for template_type in self.default_templates.keys():
            template_path = self.templates_dir / f"{template_type}.html"
            templates.append({
                'type': template_type,
                'customized': template_path.exists(),
                'path': str(template_path) if template_path.exists() else None
            })
        
        return templates


# Singleton instances
system_settings = SystemSettingsService()
company_settings = CompanySettingsService()
print_templates = PrintTemplateService()