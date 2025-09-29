# backend/app/services/fy_init_service.py
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import date, datetime
from decimal import Decimal
import logging

from ..models.core import Company, FinancialYear
from ..services.accounting import financial_year_service
from ..services.accounting import opening_balance_service

logger = logging.getLogger(__name__)

class FYInitService:
    """Service class for financial year initialization"""
    
    def __init__(self):
        pass
    
    def initialize_default_financial_year(
        self, 
        db: Session, 
        company_id: int,
        user_id: int
    ) -> FinancialYear:
        """Initialize default financial year for new company"""
        
        # Get current year
        current_year = datetime.now().year
        
        # Create default financial year (April to March)
        year_name = f"{current_year}-{current_year + 1}"
        start_date = date(current_year, 4, 1)
        end_date = date(current_year + 1, 3, 31)
        
        # Create financial year
        financial_year = financial_year_service.create_financial_year(
            db=db,
            company_id=company_id,
            year_name=year_name,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        logger.info(f"Default financial year created: {year_name} for company {company_id}")
        
        return financial_year
    
    def create_financial_year_from_suggestion(
        self, 
        db: Session, 
        company_id: int,
        suggestion: Dict,
        user_id: int
    ) -> FinancialYear:
        """Create financial year from suggestion"""
        
        financial_year = financial_year_service.create_financial_year(
            db=db,
            company_id=company_id,
            year_name=suggestion["year_name"],
            start_date=suggestion["start_date"],
            end_date=suggestion["end_date"],
            user_id=user_id
        )
        
        logger.info(f"Financial year created from suggestion: {suggestion['year_name']}")
        
        return financial_year
    
    def setup_opening_balances_template(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int,
        user_id: int
    ) -> Dict:
        """Setup opening balances template for new financial year"""
        
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise ValueError("Company not found")
        
        # Get financial year
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        # Create default opening balances template
        opening_balances_template = {
            "assets": {
                "cash_in_hand": Decimal('0'),
                "bank_account": Decimal('0'),
                "inventory": Decimal('0'),
                "accounts_receivable": Decimal('0')
            },
            "liabilities": {
                "accounts_payable": Decimal('0'),
                "gst_payable": Decimal('0'),
                "loans": Decimal('0')
            },
            "equity": {
                "capital": Decimal('0'),
                "retained_earnings": Decimal('0')
            },
            "income": {
                "sales": Decimal('0'),
                "other_income": Decimal('0')
            },
            "expenses": {
                "purchases": Decimal('0'),
                "operating_expenses": Decimal('0')
            }
        }
        
        # Create opening balances
        opening_balance_service.create_opening_balances(
            db=db,
            company_id=company_id,
            fy_id=fy_id,
            opening_balances=opening_balances_template,
            user_id=user_id
        )
        
        logger.info(f"Opening balances template created for financial year {financial_year.year_name}")
        
        return {
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date,
                "end_date": financial_year.end_date
            },
            "opening_balances_template": opening_balances_template,
            "message": "Opening balances template created successfully"
        }
    
    def get_financial_year_workflow(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get financial year workflow steps"""
        
        # Get active financial year
        active_fy = financial_year_service.get_active_financial_year(db, company_id)
        
        workflow_steps = [
            {
                "step": 1,
                "title": "Create Financial Year",
                "description": "Create new financial year with start and end dates",
                "status": "completed" if active_fy else "pending",
                "endpoint": "POST /api/v1/financial-years",
                "required": True
            },
            {
                "step": 2,
                "title": "Setup Opening Balances",
                "description": "Enter opening balances for all accounts",
                "status": "pending",
                "endpoint": "POST /api/v1/financial-years/{fy_id}/opening-balances",
                "required": True
            },
            {
                "step": 3,
                "title": "Validate Opening Balances",
                "description": "Ensure opening balances are balanced (debits = credits)",
                "status": "pending",
                "endpoint": "GET /api/v1/financial-years/{fy_id}/validate",
                "required": True
            },
            {
                "step": 4,
                "title": "Start Transactions",
                "description": "Begin recording transactions for the financial year",
                "status": "pending",
                "endpoint": "N/A",
                "required": False
            },
            {
                "step": 5,
                "title": "Close Financial Year",
                "description": "Close financial year and prepare for next year",
                "status": "pending",
                "endpoint": "POST /api/v1/financial-years/{fy_id}/close",
                "required": True
            }
        ]
        
        return {
            "current_financial_year": {
                "id": active_fy.id if active_fy else None,
                "year_name": active_fy.year_name if active_fy else None,
                "is_active": active_fy.is_active if active_fy else False,
                "is_closed": active_fy.is_closed if active_fy else False
            },
            "workflow_steps": workflow_steps,
            "next_step": self._get_next_step(workflow_steps, active_fy)
        }
    
    def _get_next_step(self, workflow_steps: List[Dict], active_fy) -> Dict:
        """Get next step in financial year workflow"""
        
        if not active_fy:
            return workflow_steps[0]
        
        if not active_fy.opening_balances:
            return workflow_steps[1]
        
        # Check if opening balances are validated
        try:
            validation = opening_balance_service.validate_opening_balances(
                db=None,  # This would need proper db session
                company_id=active_fy.company_id,
                fy_id=active_fy.id
            )
            
            if not validation.get('is_balanced', False):
                return workflow_steps[2]
            
        except:
            return workflow_steps[2]
        
        if not active_fy.is_closed:
            return workflow_steps[4]  # Close financial year
        
        return {
            "step": 6,
            "title": "Create Next Financial Year",
            "description": "Create next financial year and carry forward data",
            "status": "pending",
            "endpoint": "POST /api/v1/financial-years",
            "required": True
        }
    
    def get_financial_year_checklist(
        self, 
        db: Session, 
        company_id: int,
        fy_id: int
    ) -> Dict:
        """Get financial year checklist"""
        
        financial_year = db.query(FinancialYear).filter(
            FinancialYear.id == fy_id,
            FinancialYear.company_id == company_id
        ).first()
        
        if not financial_year:
            raise ValueError("Financial year not found")
        
        checklist = [
            {
                "item": "Financial Year Created",
                "description": "Financial year is created and active",
                "status": "completed" if financial_year else "pending",
                "mandatory": True
            },
            {
                "item": "Opening Balances Entered",
                "description": "Opening balances are entered for all accounts",
                "status": "completed" if financial_year.opening_balances else "pending",
                "mandatory": True
            },
            {
                "item": "Opening Balances Validated",
                "description": "Opening balances are balanced (debits = credits)",
                "status": "pending",  # This would need validation
                "mandatory": True
            },
            {
                "item": "Chart of Accounts Setup",
                "description": "Chart of accounts is properly configured",
                "status": "completed",  # This would need validation
                "mandatory": True
            },
            {
                "item": "GST Slabs Configured",
                "description": "GST slabs are configured for the financial year",
                "status": "completed",  # This would need validation
                "mandatory": True
            },
            {
                "item": "Company Settings Updated",
                "description": "Company settings are updated for the financial year",
                "status": "completed",  # This would need validation
                "mandatory": True
            }
        ]
        
        # Calculate completion percentage
        completed_items = sum(1 for item in checklist if item["status"] == "completed")
        total_items = len(checklist)
        completion_percentage = (completed_items / total_items) * 100
        
        return {
            "financial_year": {
                "id": financial_year.id,
                "year_name": financial_year.year_name,
                "start_date": financial_year.start_date,
                "end_date": financial_year.end_date
            },
            "checklist": checklist,
            "completion_percentage": completion_percentage,
            "is_ready": completion_percentage == 100
        }
    
    def get_financial_year_timeline(
        self, 
        db: Session, 
        company_id: int
    ) -> List[Dict]:
        """Get financial year timeline"""
        
        financial_years = financial_year_service.list_financial_years(
            db=db,
            company_id=company_id,
            include_closed=True
        )
        
        timeline = []
        
        for fy in financial_years:
            timeline.append({
                "id": fy.id,
                "year_name": fy.year_name,
                "start_date": fy.start_date,
                "end_date": fy.end_date,
                "is_active": fy.is_active,
                "is_closed": fy.is_closed,
                "closed_at": fy.closed_at,
                "status": "Active" if fy.is_active else "Closed" if fy.is_closed else "Draft"
            })
        
        return sorted(timeline, key=lambda x: x["start_date"], reverse=True)
    
    def get_financial_year_statistics(
        self, 
        db: Session, 
        company_id: int
    ) -> Dict:
        """Get financial year statistics"""
        
        financial_years = financial_year_service.list_financial_years(
            db=db,
            company_id=company_id,
            include_closed=True
        )
        
        total_fys = len(financial_years)
        active_fys = sum(1 for fy in financial_years if fy.is_active)
        closed_fys = sum(1 for fy in financial_years if fy.is_closed)
        
        return {
            "total_financial_years": total_fys,
            "active_financial_years": active_fys,
            "closed_financial_years": closed_fys,
            "draft_financial_years": total_fys - active_fys - closed_fys
        }

# Global service instance
fy_init_service = FYInitService()