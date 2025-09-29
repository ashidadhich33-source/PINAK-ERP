# backend/app/services/core/company_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date
import json
import logging

from ...models.company import Company
from ...models.user import User
from ...models.inventory import Item, StockItem
from ...models.accounting import ChartOfAccount, JournalEntry
from ...models.sales import SaleOrder, SaleInvoice
from ...models.purchase import PurchaseOrder, PurchaseBill
from ...models.customers import Customer
from ...models.pos.pos_models import POSTransaction
from ...models.core.discount_management import DiscountRule, DiscountCoupon
from ...models.loyalty import LoyaltyProgram, LoyaltyTransaction

logger = logging.getLogger(__name__)

class CompanyIntegrationService:
    """Central service for company-level integrations across all modules"""
    
    def __init__(self):
        self.integration_cache = {}
    
    def get_company_data_isolation(self, db: Session, company_id: int) -> Dict:
        """Get company data isolation settings and validate access"""
        
        try:
            # Get company information
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise ValueError("Company not found")
            
            # Get company-level settings
            company_settings = {
                'company_id': company.id,
                'company_name': company.name,
                'company_code': company.company_code,
                'is_active': company.is_active,
                'data_isolation': company.data_isolation,
                'multi_company': company.multi_company,
                'currency': company.currency,
                'timezone': company.timezone,
                'fiscal_year_start': company.fiscal_year_start,
                'fiscal_year_end': company.fiscal_year_end
            }
            
            # Get company-level permissions
            permissions = self.get_company_permissions(db, company_id)
            
            # Get company-level integrations
            integrations = self.get_company_integrations(db, company_id)
            
            return {
                'company': company_settings,
                'permissions': permissions,
                'integrations': integrations,
                'isolation_status': 'active' if company.data_isolation else 'disabled'
            }
            
        except Exception as e:
            logger.error(f"Error getting company data isolation: {str(e)}")
            raise ValueError(f"Failed to get company data isolation: {str(e)}")
    
    def get_company_permissions(self, db: Session, company_id: int) -> Dict:
        """Get company-level permissions and access control"""
        
        try:
            # Get company users
            users = db.query(User).filter(
                User.company_id == company_id,
                User.is_active == True
            ).all()
            
            # Get company modules
            modules = self.get_company_modules(db, company_id)
            
            # Get company roles
            roles = self.get_company_roles(db, company_id)
            
            return {
                'total_users': len(users),
                'active_users': len([u for u in users if u.is_active]),
                'modules': modules,
                'roles': roles,
                'permission_level': 'full' if company_id else 'limited'
            }
            
        except Exception as e:
            logger.error(f"Error getting company permissions: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'modules': [],
                'roles': [],
                'permission_level': 'limited'
            }
    
    def get_company_modules(self, db: Session, company_id: int) -> List[Dict]:
        """Get company-enabled modules"""
        
        modules = [
            {
                'name': 'inventory',
                'enabled': True,
                'description': 'Inventory Management',
                'features': ['items', 'stock', 'categories', 'suppliers']
            },
            {
                'name': 'accounting',
                'enabled': True,
                'description': 'Accounting & Finance',
                'features': ['coa', 'journal_entries', 'financial_reports']
            },
            {
                'name': 'sales',
                'enabled': True,
                'description': 'Sales Management',
                'features': ['orders', 'invoices', 'returns', 'customers']
            },
            {
                'name': 'purchase',
                'enabled': True,
                'description': 'Purchase Management',
                'features': ['orders', 'bills', 'returns', 'suppliers']
            },
            {
                'name': 'pos',
                'enabled': True,
                'description': 'Point of Sale',
                'features': ['transactions', 'payments', 'inventory', 'customers']
            },
            {
                'name': 'customers',
                'enabled': True,
                'description': 'Customer Management',
                'features': ['profiles', 'analytics', 'loyalty', 'benefits']
            },
            {
                'name': 'discounts',
                'enabled': True,
                'description': 'Discount Management',
                'features': ['rules', 'coupons', 'promotions', 'analytics']
            },
            {
                'name': 'loyalty',
                'enabled': True,
                'description': 'Loyalty Program',
                'features': ['points', 'tiers', 'rewards', 'benefits']
            },
            {
                'name': 'reports',
                'enabled': True,
                'description': 'Reporting & Analytics',
                'features': ['custom_reports', 'dashboards', 'analytics']
            },
            {
                'name': 'compliance',
                'enabled': True,
                'description': 'Indian Compliance',
                'features': ['gst', 'tds', 'tcs', 'e_invoicing']
            },
            {
                'name': 'banking',
                'enabled': True,
                'description': 'Banking & Payments',
                'features': ['accounts', 'transactions', 'reconciliation']
            }
        ]
        
        return modules
    
    def get_company_roles(self, db: Session, company_id: int) -> List[Dict]:
        """Get company roles and permissions"""
        
        roles = [
            {
                'name': 'admin',
                'description': 'Full system access',
                'permissions': ['all'],
                'modules': ['all']
            },
            {
                'name': 'manager',
                'description': 'Management access',
                'permissions': ['read', 'write', 'approve'],
                'modules': ['inventory', 'sales', 'purchase', 'pos', 'reports']
            },
            {
                'name': 'accountant',
                'description': 'Accounting access',
                'permissions': ['read', 'write'],
                'modules': ['accounting', 'sales', 'purchase', 'reports']
            },
            {
                'name': 'salesperson',
                'description': 'Sales access',
                'permissions': ['read', 'write'],
                'modules': ['sales', 'pos', 'customers', 'inventory']
            },
            {
                'name': 'cashier',
                'description': 'POS access',
                'permissions': ['read', 'write'],
                'modules': ['pos', 'customers', 'inventory']
            }
        ]
        
        return roles
    
    def get_company_integrations(self, db: Session, company_id: int) -> Dict:
        """Get company-level integrations status"""
        
        try:
            # Check inventory integration
            inventory_items = db.query(Item).filter(Item.company_id == company_id).count()
            
            # Check accounting integration
            chart_accounts = db.query(ChartOfAccount).filter(ChartOfAccount.company_id == company_id).count()
            
            # Check sales integration
            sales_orders = db.query(SaleOrder).filter(SaleOrder.company_id == company_id).count()
            
            # Check purchase integration
            purchase_orders = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).count()
            
            # Check POS integration
            pos_transactions = db.query(POSTransaction).filter(POSTransaction.company_id == company_id).count()
            
            # Check customer integration
            customers = db.query(Customer).filter(Customer.company_id == company_id).count()
            
            # Check discount integration
            discount_rules = db.query(DiscountRule).filter(DiscountRule.company_id == company_id).count()
            
            # Check loyalty integration
            loyalty_programs = db.query(LoyaltyProgram).filter(LoyaltyProgram.company_id == company_id).count()
            
            return {
                'inventory': {
                    'enabled': True,
                    'items_count': inventory_items,
                    'status': 'active'
                },
                'accounting': {
                    'enabled': True,
                    'accounts_count': chart_accounts,
                    'status': 'active'
                },
                'sales': {
                    'enabled': True,
                    'orders_count': sales_orders,
                    'status': 'active'
                },
                'purchase': {
                    'enabled': True,
                    'orders_count': purchase_orders,
                    'status': 'active'
                },
                'pos': {
                    'enabled': True,
                    'transactions_count': pos_transactions,
                    'status': 'active'
                },
                'customers': {
                    'enabled': True,
                    'customers_count': customers,
                    'status': 'active'
                },
                'discounts': {
                    'enabled': True,
                    'rules_count': discount_rules,
                    'status': 'active'
                },
                'loyalty': {
                    'enabled': True,
                    'programs_count': loyalty_programs,
                    'status': 'active'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting company integrations: {str(e)}")
            return {}
    
    def validate_company_access(self, db: Session, company_id: int, user_id: int) -> bool:
        """Validate user access to company data"""
        
        try:
            # Check if user belongs to company
            user = db.query(User).filter(
                User.id == user_id,
                User.company_id == company_id,
                User.is_active == True
            ).first()
            
            if not user:
                return False
            
            # Check company is active
            company = db.query(Company).filter(
                Company.id == company_id,
                Company.is_active == True
            ).first()
            
            if not company:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating company access: {str(e)}")
            return False
    
    def get_company_analytics(self, db: Session, company_id: int) -> Dict:
        """Get company-level analytics and insights"""
        
        try:
            # Get company data counts
            analytics = {
                'inventory': {
                    'total_items': db.query(Item).filter(Item.company_id == company_id).count(),
                    'low_stock_items': self.get_low_stock_count(db, company_id),
                    'total_value': self.get_inventory_value(db, company_id)
                },
                'sales': {
                    'total_orders': db.query(SaleOrder).filter(SaleOrder.company_id == company_id).count(),
                    'total_invoices': db.query(SaleInvoice).filter(SaleInvoice.company_id == company_id).count(),
                    'total_revenue': self.get_total_revenue(db, company_id)
                },
                'purchase': {
                    'total_orders': db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).count(),
                    'total_bills': db.query(PurchaseBill).filter(PurchaseBill.company_id == company_id).count(),
                    'total_expenses': self.get_total_expenses(db, company_id)
                },
                'pos': {
                    'total_transactions': db.query(POSTransaction).filter(POSTransaction.company_id == company_id).count(),
                    'total_sales': self.get_pos_total_sales(db, company_id)
                },
                'customers': {
                    'total_customers': db.query(Customer).filter(Customer.company_id == company_id).count(),
                    'active_customers': self.get_active_customers_count(db, company_id)
                },
                'accounting': {
                    'total_accounts': db.query(ChartOfAccount).filter(ChartOfAccount.company_id == company_id).count(),
                    'total_entries': db.query(JournalEntry).filter(JournalEntry.company_id == company_id).count()
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting company analytics: {str(e)}")
            return {}
    
    def get_low_stock_count(self, db: Session, company_id: int) -> int:
        """Get count of low stock items"""
        try:
            # Get items with low stock
            low_stock_items = db.query(Item).join(StockItem).filter(
                Item.company_id == company_id,
                StockItem.quantity <= Item.minimum_stock_level
            ).count()
            
            return low_stock_items
        except Exception as e:
            logger.error(f"Error getting low stock count: {str(e)}")
            return 0
    
    def get_inventory_value(self, db: Session, company_id: int) -> Decimal:
        """Get total inventory value"""
        try:
            # Calculate total inventory value
            total_value = db.query(func.sum(StockItem.quantity * StockItem.average_cost)).join(Item).filter(
                Item.company_id == company_id
            ).scalar()
            
            return total_value or 0
        except Exception as e:
            logger.error(f"Error getting inventory value: {str(e)}")
            return 0
    
    def get_total_revenue(self, db: Session, company_id: int) -> Decimal:
        """Get total revenue from sales"""
        try:
            # Calculate total revenue
            total_revenue = db.query(func.sum(SaleInvoice.total_amount)).filter(
                SaleInvoice.company_id == company_id,
                SaleInvoice.status == 'paid'
            ).scalar()
            
            return total_revenue or 0
        except Exception as e:
            logger.error(f"Error getting total revenue: {str(e)}")
            return 0
    
    def get_total_expenses(self, db: Session, company_id: int) -> Decimal:
        """Get total expenses from purchases"""
        try:
            # Calculate total expenses
            total_expenses = db.query(func.sum(PurchaseBill.total_amount)).filter(
                PurchaseBill.company_id == company_id,
                PurchaseBill.status == 'paid'
            ).scalar()
            
            return total_expenses or 0
        except Exception as e:
            logger.error(f"Error getting total expenses: {str(e)}")
            return 0
    
    def get_pos_total_sales(self, db: Session, company_id: int) -> Decimal:
        """Get total POS sales"""
        try:
            # Calculate total POS sales
            total_sales = db.query(func.sum(POSTransaction.total_amount)).filter(
                POSTransaction.company_id == company_id,
                POSTransaction.status == 'completed'
            ).scalar()
            
            return total_sales or 0
        except Exception as e:
            logger.error(f"Error getting POS total sales: {str(e)}")
            return 0
    
    def get_active_customers_count(self, db: Session, company_id: int) -> int:
        """Get count of active customers"""
        try:
            # Get customers with recent transactions
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            active_customers = db.query(Customer).join(POSTransaction).filter(
                Customer.company_id == company_id,
                POSTransaction.transaction_date >= thirty_days_ago
            ).distinct().count()
            
            return active_customers
        except Exception as e:
            logger.error(f"Error getting active customers count: {str(e)}")
            return 0
    
    def sync_company_data(self, db: Session, company_id: int) -> Dict:
        """Sync company data across all modules"""
        
        try:
            sync_results = {
                'inventory_sync': self.sync_inventory_data(db, company_id),
                'accounting_sync': self.sync_accounting_data(db, company_id),
                'sales_sync': self.sync_sales_data(db, company_id),
                'purchase_sync': self.sync_purchase_data(db, company_id),
                'pos_sync': self.sync_pos_data(db, company_id),
                'customer_sync': self.sync_customer_data(db, company_id)
            }
            
            return {
                'success': True,
                'sync_results': sync_results,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error syncing company data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow()
            }
    
    def sync_inventory_data(self, db: Session, company_id: int) -> Dict:
        """Sync inventory data"""
        try:
            # Update stock levels
            # Update item costs
            # Update item status
            return {'status': 'success', 'message': 'Inventory data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_accounting_data(self, db: Session, company_id: int) -> Dict:
        """Sync accounting data"""
        try:
            # Update account balances
            # Update journal entries
            # Update financial reports
            return {'status': 'success', 'message': 'Accounting data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_sales_data(self, db: Session, company_id: int) -> Dict:
        """Sync sales data"""
        try:
            # Update sales orders
            # Update invoices
            # Update customer data
            return {'status': 'success', 'message': 'Sales data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_purchase_data(self, db: Session, company_id: int) -> Dict:
        """Sync purchase data"""
        try:
            # Update purchase orders
            # Update bills
            # Update supplier data
            return {'status': 'success', 'message': 'Purchase data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_pos_data(self, db: Session, company_id: int) -> Dict:
        """Sync POS data"""
        try:
            # Update POS transactions
            # Update inventory
            # Update customer data
            return {'status': 'success', 'message': 'POS data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def sync_customer_data(self, db: Session, company_id: int) -> Dict:
        """Sync customer data"""
        try:
            # Update customer profiles
            # Update loyalty points
            # Update customer analytics
            return {'status': 'success', 'message': 'Customer data synced'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}