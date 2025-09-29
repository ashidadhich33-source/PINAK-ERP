# backend/app/services/coa_init_service.py
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from decimal import Decimal
import logging

from ..models.company import Company, ChartOfAccount
from ..services.chart_of_accounts_service import chart_of_accounts_service

logger = logging.getLogger(__name__)

class COAInitService:
    """Service class for chart of accounts initialization"""
    
    def __init__(self):
        pass
    
    def initialize_default_chart_of_accounts(
        self, 
        db: Session, 
        company_id: int,
        user_id: int
    ) -> List[ChartOfAccount]:
        """Initialize default chart of accounts for new company"""
        
        # Check if chart of accounts already exists
        existing_count = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        ).count()
        
        if existing_count > 0:
            logger.info("Chart of accounts already exists for company")
            return []
        
        # Create Indian chart of accounts
        accounts = chart_of_accounts_service.create_indian_chart_of_accounts(
            db=db,
            company_id=company_id,
            user_id=user_id
        )
        
        logger.info(f"Default chart of accounts created for company {company_id}")
        
        return accounts
    
    def get_chart_of_accounts_template(
        self, 
        company_type: str = "retail"
    ) -> Dict:
        """Get chart of accounts template based on company type"""
        
        templates = {
            "retail": {
                "name": "Retail Business Chart of Accounts",
                "description": "Standard chart of accounts for retail businesses",
                "accounts": [
                    {"code": "1000", "name": "ASSETS", "type": "Asset"},
                    {"code": "1100", "name": "Current Assets", "type": "Asset"},
                    {"code": "1110", "name": "Cash and Cash Equivalents", "type": "Asset"},
                    {"code": "1111", "name": "Cash in Hand", "type": "Asset"},
                    {"code": "1112", "name": "Bank Account", "type": "Asset"},
                    {"code": "1120", "name": "Accounts Receivable", "type": "Asset"},
                    {"code": "1130", "name": "Inventory", "type": "Asset"},
                    {"code": "2000", "name": "LIABILITIES", "type": "Liability"},
                    {"code": "2100", "name": "Current Liabilities", "type": "Liability"},
                    {"code": "2110", "name": "Accounts Payable", "type": "Liability"},
                    {"code": "2120", "name": "GST Payable", "type": "Liability", "gst_applicable": True},
                    {"code": "3000", "name": "EQUITY", "type": "Equity"},
                    {"code": "3100", "name": "Share Capital", "type": "Equity"},
                    {"code": "4000", "name": "INCOME", "type": "Income"},
                    {"code": "4100", "name": "Sales Revenue", "type": "Income"},
                    {"code": "5000", "name": "EXPENSES", "type": "Expense"},
                    {"code": "5100", "name": "Cost of Goods Sold", "type": "Expense"},
                    {"code": "5200", "name": "Operating Expenses", "type": "Expense"}
                ]
            },
            "manufacturing": {
                "name": "Manufacturing Business Chart of Accounts",
                "description": "Standard chart of accounts for manufacturing businesses",
                "accounts": [
                    {"code": "1000", "name": "ASSETS", "type": "Asset"},
                    {"code": "1100", "name": "Current Assets", "type": "Asset"},
                    {"code": "1110", "name": "Cash and Cash Equivalents", "type": "Asset"},
                    {"code": "1120", "name": "Accounts Receivable", "type": "Asset"},
                    {"code": "1130", "name": "Inventory", "type": "Asset"},
                    {"code": "1131", "name": "Raw Materials", "type": "Asset"},
                    {"code": "1132", "name": "Work in Progress", "type": "Asset"},
                    {"code": "1133", "name": "Finished Goods", "type": "Asset"},
                    {"code": "1200", "name": "Fixed Assets", "type": "Asset"},
                    {"code": "1210", "name": "Property, Plant & Equipment", "type": "Asset"},
                    {"code": "2000", "name": "LIABILITIES", "type": "Liability"},
                    {"code": "2100", "name": "Current Liabilities", "type": "Liability"},
                    {"code": "2110", "name": "Accounts Payable", "type": "Liability"},
                    {"code": "2120", "name": "GST Payable", "type": "Liability", "gst_applicable": True},
                    {"code": "3000", "name": "EQUITY", "type": "Equity"},
                    {"code": "3100", "name": "Share Capital", "type": "Equity"},
                    {"code": "4000", "name": "INCOME", "type": "Income"},
                    {"code": "4100", "name": "Sales Revenue", "type": "Income"},
                    {"code": "5000", "name": "EXPENSES", "type": "Expense"},
                    {"code": "5100", "name": "Cost of Goods Sold", "type": "Expense"},
                    {"code": "5110", "name": "Raw Material Cost", "type": "Expense"},
                    {"code": "5120", "name": "Direct Labor", "type": "Expense"},
                    {"code": "5130", "name": "Manufacturing Overhead", "type": "Expense"},
                    {"code": "5200", "name": "Operating Expenses", "type": "Expense"}
                ]
            },
            "service": {
                "name": "Service Business Chart of Accounts",
                "description": "Standard chart of accounts for service businesses",
                "accounts": [
                    {"code": "1000", "name": "ASSETS", "type": "Asset"},
                    {"code": "1100", "name": "Current Assets", "type": "Asset"},
                    {"code": "1110", "name": "Cash and Cash Equivalents", "type": "Asset"},
                    {"code": "1120", "name": "Accounts Receivable", "type": "Asset"},
                    {"code": "1200", "name": "Fixed Assets", "type": "Asset"},
                    {"code": "1210", "name": "Property, Plant & Equipment", "type": "Asset"},
                    {"code": "2000", "name": "LIABILITIES", "type": "Liability"},
                    {"code": "2100", "name": "Current Liabilities", "type": "Liability"},
                    {"code": "2110", "name": "Accounts Payable", "type": "Liability"},
                    {"code": "2120", "name": "GST Payable", "type": "Liability", "gst_applicable": True},
                    {"code": "3000", "name": "EQUITY", "type": "Equity"},
                    {"code": "3100", "name": "Share Capital", "type": "Equity"},
                    {"code": "4000", "name": "INCOME", "type": "Income"},
                    {"code": "4100", "name": "Service Revenue", "type": "Income"},
                    {"code": "5000", "name": "EXPENSES", "type": "Expense"},
                    {"code": "5100", "name": "Service Costs", "type": "Expense"},
                    {"code": "5200", "name": "Operating Expenses", "type": "Expense"}
                ]
            }
        }
        
        return templates.get(company_type, templates["retail"])
    
    def create_custom_chart_of_accounts(
        self, 
        db: Session, 
        company_id: int,
        template: Dict,
        user_id: int
    ) -> List[ChartOfAccount]:
        """Create custom chart of accounts from template"""
        
        created_accounts = []
        
        for account_data in template["accounts"]:
            try:
                account = chart_of_accounts_service.create_account(
                    db=db,
                    company_id=company_id,
                    account_code=account_data["code"],
                    account_name=account_data["name"],
                    account_type=account_data["type"],
                    gst_applicable=account_data.get("gst_applicable", False),
                    user_id=user_id
                )
                created_accounts.append(account)
            except ValueError as e:
                logger.warning(f"Failed to create account {account_data['code']}: {str(e)}")
                continue
        
        logger.info(f"Created {len(created_accounts)} accounts from template")
        
        return created_accounts
    
    def get_chart_of_accounts_workflow(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get chart of accounts setup workflow"""
        
        # Check if chart of accounts exists
        existing_accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        ).count()
        
        workflow_steps = [
            {
                "step": 1,
                "title": "Create Chart of Accounts",
                "description": "Create or import chart of accounts",
                "status": "completed" if existing_accounts > 0 else "pending",
                "endpoint": "POST /api/v1/chart-of-accounts/initialize-indian",
                "required": True
            },
            {
                "step": 2,
                "title": "Setup Account Hierarchy",
                "description": "Organize accounts in proper hierarchy",
                "status": "pending",
                "endpoint": "PUT /api/v1/chart-of-accounts/{account_id}",
                "required": True
            },
            {
                "step": 3,
                "title": "Configure GST Accounts",
                "description": "Setup GST-related accounts",
                "status": "pending",
                "endpoint": "PUT /api/v1/chart-of-accounts/{account_id}",
                "required": True
            },
            {
                "step": 4,
                "title": "Validate Chart of Accounts",
                "description": "Ensure all required accounts are present",
                "status": "pending",
                "endpoint": "GET /api/v1/chart-of-accounts/validate",
                "required": True
            },
            {
                "step": 5,
                "title": "Setup Opening Balances",
                "description": "Enter opening balances for all accounts",
                "status": "pending",
                "endpoint": "POST /api/v1/financial-years/{fy_id}/opening-balances",
                "required": True
            }
        ]
        
        return {
            "current_step": 1 if existing_accounts == 0 else 2,
            "workflow_steps": workflow_steps,
            "next_step": self._get_next_step(workflow_steps, existing_accounts)
        }
    
    def _get_next_step(self, workflow_steps: List[Dict], existing_accounts: int) -> Dict:
        """Get next step in chart of accounts workflow"""
        
        if existing_accounts == 0:
            return workflow_steps[0]
        
        # Check if accounts are properly organized
        # This would require additional validation
        return workflow_steps[1]
    
    def get_chart_of_accounts_validation(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get chart of accounts validation results"""
        
        accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.is_active == True
        ).all()
        
        validation_results = {
            "total_accounts": len(accounts),
            "accounts_by_type": {},
            "missing_accounts": [],
            "duplicate_codes": [],
            "validation_passed": True,
            "recommendations": []
        }
        
        # Check account types
        for account in accounts:
            account_type = account.account_type
            if account_type not in validation_results["accounts_by_type"]:
                validation_results["accounts_by_type"][account_type] = 0
            validation_results["accounts_by_type"][account_type] += 1
        
        # Check for required account types
        required_types = ["Asset", "Liability", "Equity", "Income", "Expense"]
        for account_type in required_types:
            if account_type not in validation_results["accounts_by_type"]:
                validation_results["missing_accounts"].append(account_type)
                validation_results["validation_passed"] = False
        
        # Check for duplicate account codes
        account_codes = [account.account_code for account in accounts]
        duplicate_codes = [code for code in account_codes if account_codes.count(code) > 1]
        validation_results["duplicate_codes"] = list(set(duplicate_codes))
        
        if validation_results["duplicate_codes"]:
            validation_results["validation_passed"] = False
        
        # Generate recommendations
        if validation_results["missing_accounts"]:
            validation_results["recommendations"].append(
                f"Add missing account types: {', '.join(validation_results['missing_accounts'])}"
            )
        
        if validation_results["duplicate_codes"]:
            validation_results["recommendations"].append(
                f"Fix duplicate account codes: {', '.join(validation_results['duplicate_codes'])}"
            )
        
        if validation_results["validation_passed"]:
            validation_results["recommendations"].append("Chart of accounts is properly configured")
        
        return validation_results
    
    def get_chart_of_accounts_statistics(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get chart of accounts statistics"""
        
        accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        ).all()
        
        total_accounts = len(accounts)
        active_accounts = sum(1 for account in accounts if account.is_active)
        gst_applicable_accounts = sum(1 for account in accounts if account.gst_applicable)
        
        accounts_by_type = {}
        for account in accounts:
            account_type = account.account_type
            if account_type not in accounts_by_type:
                accounts_by_type[account_type] = 0
            accounts_by_type[account_type] += 1
        
        return {
            "total_accounts": total_accounts,
            "active_accounts": active_accounts,
            "inactive_accounts": total_accounts - active_accounts,
            "gst_applicable_accounts": gst_applicable_accounts,
            "accounts_by_type": accounts_by_type,
            "completion_percentage": (active_accounts / total_accounts * 100) if total_accounts > 0 else 0
        }
    
    def get_chart_of_accounts_templates(
        self
    ) -> List[Dict]:
        """Get available chart of accounts templates"""
        
        templates = [
            {
                "id": "indian_standard",
                "name": "Indian Standard Chart of Accounts",
                "description": "Standard Indian chart of accounts with GST compliance",
                "account_count": 50,
                "gst_compliant": True,
                "suitable_for": ["retail", "manufacturing", "service"]
            },
            {
                "id": "retail_basic",
                "name": "Basic Retail Chart of Accounts",
                "description": "Simple chart of accounts for small retail businesses",
                "account_count": 25,
                "gst_compliant": True,
                "suitable_for": ["retail"]
            },
            {
                "id": "manufacturing_standard",
                "name": "Manufacturing Chart of Accounts",
                "description": "Comprehensive chart of accounts for manufacturing businesses",
                "account_count": 75,
                "gst_compliant": True,
                "suitable_for": ["manufacturing"]
            },
            {
                "id": "service_basic",
                "name": "Service Business Chart of Accounts",
                "description": "Chart of accounts for service-based businesses",
                "account_count": 30,
                "gst_compliant": True,
                "suitable_for": ["service"]
            }
        ]
        
        return templates

# Global service instance
coa_init_service = COAInitService()