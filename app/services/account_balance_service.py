# backend/app/services/account_balance_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ..models.company import Company, ChartOfAccount
from ..models.sales import SalesInvoice, SalesInvoiceItem
from ..models.purchase import PurchaseBill, PurchaseBillItem

logger = logging.getLogger(__name__)

class AccountBalanceService:
    """Service class for account balance management"""
    
    def __init__(self):
        pass
    
    def calculate_account_balance(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Calculate account balance for period"""
        
        # Get account
        account = db.query(ChartOfAccount).filter(
            ChartOfAccount.id == account_id,
            ChartOfAccount.company_id == company_id
        ).first()
        
        if not account:
            raise ValueError("Account not found")
        
        # This would require implementing journal entries
        # For now, return basic structure with mock data
        return {
            "account": {
                "id": account.id,
                "account_code": account.account_code,
                "account_name": account.account_name,
                "account_type": account.account_type
            },
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "opening_balance": Decimal('0'),
            "debit_total": Decimal('0'),
            "credit_total": Decimal('0'),
            "closing_balance": Decimal('0'),
            "balance_type": "debit" if account.account_type in ["Asset", "Expense"] else "credit",
            "transaction_count": 0
        }
    
    def get_account_balances_bulk(
        self, 
        db: Session, 
        company_id: int,
        account_ids: List[int],
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[Dict]:
        """Get balances for multiple accounts"""
        
        balances = []
        
        for account_id in account_ids:
            try:
                balance = self.calculate_account_balance(
                    db=db,
                    company_id=company_id,
                    account_id=account_id,
                    from_date=from_date,
                    to_date=to_date
                )
                balances.append(balance)
            except ValueError:
                continue
        
        return balances
    
    def get_account_balance_summary(
        self, 
        db: Session, 
        company_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Dict:
        """Get account balance summary"""
        
        # Get all active accounts
        accounts = db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id,
            ChartOfAccount.is_active == True
        ).all()
        
        summary = {
            "total_accounts": len(accounts),
            "accounts_by_type": {},
            "total_debit": Decimal('0'),
            "total_credit": Decimal('0'),
            "balanced": False
        }
        
        for account in accounts:
            account_type = account.account_type
            if account_type not in summary["accounts_by_type"]:
                summary["accounts_by_type"][account_type] = {
                    "count": 0,
                    "total_debit": Decimal('0'),
                    "total_credit": Decimal('0')
                }
            
            summary["accounts_by_type"][account_type]["count"] += 1
            
            # This would require actual balance calculation
            # For now, use mock data
            mock_balance = Decimal('0')
            if account.account_type in ["Asset", "Expense"]:
                summary["accounts_by_type"][account_type]["total_debit"] += mock_balance
                summary["total_debit"] += mock_balance
            else:
                summary["accounts_by_type"][account_type]["total_credit"] += mock_balance
                summary["total_credit"] += mock_balance
        
        summary["balanced"] = summary["total_debit"] == summary["total_credit"]
        
        return summary
    
    def get_account_balance_history(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        from_date: date,
        to_date: date
    ) -> List[Dict]:
        """Get account balance history"""
        
        # This would require implementing journal entries
        # For now, return mock data
        history = []
        
        current_date = from_date
        while current_date <= to_date:
            history.append({
                "date": current_date,
                "opening_balance": Decimal('0'),
                "debit_total": Decimal('0'),
                "credit_total": Decimal('0'),
                "closing_balance": Decimal('0'),
                "transaction_count": 0
            })
            
            # Move to next day
            current_date = current_date.replace(day=current_date.day + 1)
        
        return history
    
    def get_account_balance_trend(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        from_date: date,
        to_date: date,
        period: str = "daily"  # daily, weekly, monthly
    ) -> Dict:
        """Get account balance trend"""
        
        # This would require implementing journal entries
        # For now, return mock data
        trend_data = []
        
        if period == "daily":
            current_date = from_date
            while current_date <= to_date:
                trend_data.append({
                    "period": current_date.isoformat(),
                    "balance": Decimal('0'),
                    "change": Decimal('0')
                })
                current_date = current_date.replace(day=current_date.day + 1)
        
        elif period == "weekly":
            # Weekly aggregation
            pass
        
        elif period == "monthly":
            # Monthly aggregation
            pass
        
        return {
            "account_id": account_id,
            "period": {
                "from_date": from_date,
                "to_date": to_date,
                "type": period
            },
            "trend_data": trend_data,
            "summary": {
                "start_balance": Decimal('0'),
                "end_balance": Decimal('0'),
                "total_change": Decimal('0'),
                "average_balance": Decimal('0')
            }
        }
    
    def get_account_balance_comparison(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        current_period: Dict,
        previous_period: Dict
    ) -> Dict:
        """Get account balance comparison between periods"""
        
        # This would require implementing journal entries
        # For now, return mock data
        return {
            "account_id": account_id,
            "current_period": {
                "from_date": current_period["from_date"],
                "to_date": current_period["to_date"],
                "balance": Decimal('0'),
                "change": Decimal('0')
            },
            "previous_period": {
                "from_date": previous_period["from_date"],
                "to_date": previous_period["to_date"],
                "balance": Decimal('0'),
                "change": Decimal('0')
            },
            "comparison": {
                "balance_change": Decimal('0'),
                "percentage_change": Decimal('0'),
                "trend": "increasing"  # increasing, decreasing, stable
            }
        }
    
    def get_account_balance_forecast(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        forecast_periods: int = 12
    ) -> Dict:
        """Get account balance forecast"""
        
        # This would require implementing forecasting algorithms
        # For now, return mock data
        forecast_data = []
        
        for i in range(forecast_periods):
            forecast_data.append({
                "period": f"Period {i + 1}",
                "forecasted_balance": Decimal('0'),
                "confidence_level": 0.8
            })
        
        return {
            "account_id": account_id,
            "forecast_periods": forecast_periods,
            "forecast_data": forecast_data,
            "summary": {
                "average_forecast": Decimal('0'),
                "trend": "stable",
                "confidence": 0.8
            }
        }
    
    def get_account_balance_alerts(
        self, 
        db: Session, 
        company_id: int,
        account_id: int
    ) -> List[Dict]:
        """Get account balance alerts"""
        
        # This would require implementing alert rules
        # For now, return mock data
        alerts = []
        
        # Check for negative balance
        balance = self.calculate_account_balance(db, company_id, account_id)
        if balance["closing_balance"] < 0:
            alerts.append({
                "type": "negative_balance",
                "message": "Account has negative balance",
                "severity": "high",
                "balance": balance["closing_balance"]
            })
        
        # Check for unusual activity
        if balance["transaction_count"] > 100:
            alerts.append({
                "type": "high_activity",
                "message": "Unusually high transaction activity",
                "severity": "medium",
                "count": balance["transaction_count"]
            })
        
        return alerts
    
    def get_account_balance_reconciliation(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        as_on_date: date
    ) -> Dict:
        """Get account balance reconciliation"""
        
        # This would require implementing reconciliation logic
        # For now, return mock data
        return {
            "account_id": account_id,
            "as_on_date": as_on_date,
            "book_balance": Decimal('0'),
            "bank_balance": Decimal('0'),
            "difference": Decimal('0'),
            "reconciled": True,
            "reconciliation_items": []
        }
    
    def get_account_balance_aging(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        as_on_date: date
    ) -> Dict:
        """Get account balance aging"""
        
        # This would require implementing aging logic
        # For now, return mock data
        return {
            "account_id": account_id,
            "as_on_date": as_on_date,
            "aging_buckets": {
                "current": Decimal('0'),
                "1_30_days": Decimal('0'),
                "31_60_days": Decimal('0'),
                "61_90_days": Decimal('0'),
                "over_90_days": Decimal('0')
            },
            "total_balance": Decimal('0')
        }
    
    def get_account_balance_analysis(
        self, 
        db: Session, 
        company_id: int,
        account_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Get account balance analysis"""
        
        # This would require implementing analysis logic
        # For now, return mock data
        return {
            "account_id": account_id,
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "analysis": {
                "volatility": "low",
                "trend": "stable",
                "seasonality": "none",
                "outliers": 0,
                "correlation": 0.5
            },
            "recommendations": [
                "Account balance is stable",
                "No unusual activity detected",
                "Consider regular monitoring"
            ]
        }
    
    def get_account_balance_dashboard(
        self, 
        db: Session, 
        company_id: int,
        from_date: date,
        to_date: date
    ) -> Dict:
        """Get account balance dashboard"""
        
        # This would require implementing dashboard logic
        # For now, return mock data
        return {
            "period": {
                "from_date": from_date,
                "to_date": to_date
            },
            "summary": {
                "total_accounts": 0,
                "active_accounts": 0,
                "total_balance": Decimal('0'),
                "balanced": True
            },
            "top_accounts": [],
            "alerts": [],
            "trends": []
        }

# Global service instance
account_balance_service = AccountBalanceService()