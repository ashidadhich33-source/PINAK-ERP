# backend/app/services/reports/reports_integration_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
from datetime import datetime, date, timedelta
import json
import logging

from ...models.core.report_studio import (
    ReportCategory, ReportTemplate, ReportInstance, ReportView,
    ReportSchedule, ReportBuilder, ReportDashboard, ReportWidget,
    ReportExport, ReportAnalytics, ReportPermission, ReportCache
)
from ...models.sales import SaleOrder, SaleInvoice, SalePayment
from ...models.purchase import PurchaseOrder, PurchaseBill, PurchasePayment
from ...models.pos.pos_models import POSTransaction, POSTransactionItem
from ...models.inventory import Item, StockItem, ItemCategory
from ...models.accounting import JournalEntry, JournalEntryItem, ChartOfAccount
from ...models.customers import Customer
from ...models.suppliers import Supplier
from ...models.company import Company

logger = logging.getLogger(__name__)

class ReportsIntegrationService:
    """Service for reports integration with all modules"""
    
    def __init__(self):
        self.reports_cache = {}
        self.template_cache = {}
        self.dashboard_cache = {}
    
    def create_report_template_with_integrations(self, db: Session, template_data: Dict) -> Dict:
        """Create report template with full module integrations"""
        
        try:
            # Create report template
            report_template = ReportTemplate(
                company_id=template_data['company_id'],
                template_name=template_data['template_name'],
                template_description=template_data.get('template_description'),
                category_id=template_data['category_id'],
                report_type=template_data['report_type'],
                data_source=template_data['data_source'],
                query_sql=template_data.get('query_sql'),
                parameters=template_data.get('parameters', {}),
                columns=template_data.get('columns', []),
                filters=template_data.get('filters', []),
                sorting=template_data.get('sorting', []),
                grouping=template_data.get('grouping', []),
                is_active=template_data.get('is_active', True)
            )
            
            db.add(report_template)
            db.flush()
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Module Integration
            module_result = self.integrate_template_with_modules(db, report_template)
            integration_results['modules'] = module_result
            
            # 2. Permission Integration
            permission_result = self.integrate_template_with_permissions(db, report_template)
            integration_results['permissions'] = permission_result
            
            # 3. Cache Integration
            cache_result = self.integrate_template_with_cache(db, report_template)
            integration_results['cache'] = cache_result
            
            db.commit()
            
            return {
                'success': True,
                'template_id': report_template.id,
                'template_name': report_template.template_name,
                'integration_results': integration_results,
                'message': 'Report template created with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error creating report template with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create report template: {str(e)}")
    
    def integrate_template_with_modules(self, db: Session, report_template: ReportTemplate) -> Dict:
        """Integrate report template with modules"""
        
        try:
            # Determine which modules the template integrates with
            integrated_modules = []
            
            if 'sales' in report_template.data_source.lower():
                integrated_modules.append('sales')
            if 'purchase' in report_template.data_source.lower():
                integrated_modules.append('purchase')
            if 'pos' in report_template.data_source.lower():
                integrated_modules.append('pos')
            if 'inventory' in report_template.data_source.lower():
                integrated_modules.append('inventory')
            if 'accounting' in report_template.data_source.lower():
                integrated_modules.append('accounting')
            if 'customers' in report_template.data_source.lower():
                integrated_modules.append('customers')
            if 'suppliers' in report_template.data_source.lower():
                integrated_modules.append('suppliers')
            
            return {
                'status': 'success',
                'integrated_modules': integrated_modules,
                'message': f'Template integrated with {len(integrated_modules)} modules'
            }
            
        except Exception as e:
            logger.error(f"Error integrating template with modules: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_template_with_permissions(self, db: Session, report_template: ReportTemplate) -> Dict:
        """Integrate report template with permissions"""
        
        try:
            # Create default permissions for the template
            default_permissions = [
                {'role': 'admin', 'permission': 'full_access'},
                {'role': 'manager', 'permission': 'view_export'},
                {'role': 'user', 'permission': 'view_only'}
            ]
            
            for perm_data in default_permissions:
                permission = ReportPermission(
                    template_id=report_template.id,
                    role_name=perm_data['role'],
                    permission_type=perm_data['permission'],
                    is_active=True
                )
                db.add(permission)
            
            return {
                'status': 'success',
                'permissions_created': len(default_permissions),
                'message': 'Default permissions created for template'
            }
            
        except Exception as e:
            logger.error(f"Error integrating template with permissions: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_template_with_cache(self, db: Session, report_template: ReportTemplate) -> Dict:
        """Integrate report template with cache"""
        
        try:
            # Create cache configuration for the template
            cache_config = ReportCache(
                template_id=report_template.id,
                cache_duration=3600,  # 1 hour
                cache_strategy='time_based',
                is_enabled=True,
                last_updated=datetime.utcnow()
            )
            
            db.add(cache_config)
            
            return {
                'status': 'success',
                'cache_enabled': True,
                'cache_duration': 3600,
                'message': 'Cache configuration created for template'
            }
            
        except Exception as e:
            logger.error(f"Error integrating template with cache: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_report_with_integrations(self, db: Session, report_data: Dict) -> Dict:
        """Generate report with full module integrations"""
        
        try:
            # Get report template
            template = db.query(ReportTemplate).filter(
                ReportTemplate.id == report_data['template_id']
            ).first()
            
            if not template:
                raise ValueError("Report template not found")
            
            # Create report instance
            report_instance = ReportInstance(
                template_id=template.id,
                company_id=report_data['company_id'],
                user_id=report_data['user_id'],
                report_name=report_data.get('report_name', template.template_name),
                parameters=report_data.get('parameters', {}),
                filters=report_data.get('filters', {}),
                status='generating',
                generated_at=datetime.utcnow()
            )
            
            db.add(report_instance)
            db.flush()
            
            # Generate report data
            report_data_result = self.generate_report_data(db, template, report_data)
            
            # Create report view
            report_view = ReportView(
                instance_id=report_instance.id,
                view_type=report_data.get('view_type', 'table'),
                columns=report_data_result.get('columns', []),
                data=report_data_result.get('data', []),
                total_records=report_data_result.get('total_records', 0),
                generated_at=datetime.utcnow()
            )
            
            db.add(report_view)
            
            # Update report instance
            report_instance.status = 'completed'
            report_instance.total_records = report_data_result.get('total_records', 0)
            
            # Integrate with other modules
            integration_results = {}
            
            # 1. Analytics Integration
            analytics_result = self.integrate_report_with_analytics(db, report_instance)
            integration_results['analytics'] = analytics_result
            
            # 2. Export Integration
            export_result = self.integrate_report_with_export(db, report_instance)
            integration_results['export'] = export_result
            
            # 3. Dashboard Integration
            dashboard_result = self.integrate_report_with_dashboard(db, report_instance)
            integration_results['dashboard'] = dashboard_result
            
            db.commit()
            
            return {
                'success': True,
                'report_instance_id': report_instance.id,
                'report_name': report_instance.report_name,
                'total_records': report_instance.total_records,
                'integration_results': integration_results,
                'message': 'Report generated with full integrations'
            }
            
        except Exception as e:
            logger.error(f"Error generating report with integrations: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to generate report: {str(e)}")
    
    def generate_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Generate report data based on template"""
        
        try:
            # Get data based on template data source
            if template.data_source == 'sales':
                data = self.get_sales_report_data(db, template, report_data)
            elif template.data_source == 'purchase':
                data = self.get_purchase_report_data(db, template, report_data)
            elif template.data_source == 'pos':
                data = self.get_pos_report_data(db, template, report_data)
            elif template.data_source == 'inventory':
                data = self.get_inventory_report_data(db, template, report_data)
            elif template.data_source == 'accounting':
                data = self.get_accounting_report_data(db, template, report_data)
            elif template.data_source == 'customers':
                data = self.get_customers_report_data(db, template, report_data)
            elif template.data_source == 'suppliers':
                data = self.get_suppliers_report_data(db, template, report_data)
            else:
                data = {'columns': [], 'data': [], 'total_records': 0}
            
            return data
            
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_sales_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get sales report data"""
        
        try:
            # Get sales data based on template parameters
            from_date = report_data.get('from_date', date.today() - timedelta(days=30))
            to_date = report_data.get('to_date', date.today())
            
            # Get sales invoices
            sales_invoices = db.query(SaleInvoice).filter(
                SaleInvoice.company_id == report_data['company_id'],
                SaleInvoice.invoice_date >= from_date,
                SaleInvoice.invoice_date <= to_date
            ).all()
            
            # Prepare data
            columns = ['Invoice Number', 'Invoice Date', 'Customer', 'Total Amount', 'Tax Amount', 'Status']
            data = []
            
            for invoice in sales_invoices:
                customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
                data.append([
                    invoice.invoice_number,
                    invoice.invoice_date.strftime('%Y-%m-%d'),
                    customer.name if customer else 'Unknown',
                    float(invoice.total_amount),
                    float(invoice.tax_amount),
                    invoice.payment_status
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting sales report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_purchase_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get purchase report data"""
        
        try:
            # Get purchase data based on template parameters
            from_date = report_data.get('from_date', date.today() - timedelta(days=30))
            to_date = report_data.get('to_date', date.today())
            
            # Get purchase bills
            purchase_bills = db.query(PurchaseBill).filter(
                PurchaseBill.company_id == report_data['company_id'],
                PurchaseBill.bill_date >= from_date,
                PurchaseBill.bill_date <= to_date
            ).all()
            
            # Prepare data
            columns = ['Bill Number', 'Bill Date', 'Supplier', 'Total Amount', 'Tax Amount', 'Status']
            data = []
            
            for bill in purchase_bills:
                supplier = db.query(Supplier).filter(Supplier.id == bill.supplier_id).first()
                data.append([
                    bill.bill_number,
                    bill.bill_date.strftime('%Y-%m-%d'),
                    supplier.name if supplier else 'Unknown',
                    float(bill.total_amount),
                    float(bill.tax_amount),
                    bill.payment_status
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting purchase report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_pos_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get POS report data"""
        
        try:
            # Get POS data based on template parameters
            from_date = report_data.get('from_date', date.today() - timedelta(days=30))
            to_date = report_data.get('to_date', date.today())
            
            # Get POS transactions
            pos_transactions = db.query(POSTransaction).filter(
                POSTransaction.company_id == report_data['company_id'],
                POSTransaction.transaction_date >= from_date,
                POSTransaction.transaction_date <= to_date
            ).all()
            
            # Prepare data
            columns = ['Transaction Number', 'Transaction Date', 'Customer', 'Total Amount', 'Payment Method', 'Status']
            data = []
            
            for transaction in pos_transactions:
                customer = db.query(Customer).filter(Customer.id == transaction.customer_id).first()
                data.append([
                    transaction.transaction_number,
                    transaction.transaction_date.strftime('%Y-%m-%d'),
                    customer.name if customer else 'Walk-in',
                    float(transaction.total_amount),
                    transaction.payment_method,
                    transaction.status
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting POS report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_inventory_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get inventory report data"""
        
        try:
            # Get inventory data based on template parameters
            # Get stock items
            stock_items = db.query(StockItem).filter(
                StockItem.company_id == report_data['company_id']
            ).all()
            
            # Prepare data
            columns = ['Item Name', 'Item Code', 'Category', 'Current Stock', 'Available Stock', 'Unit Cost']
            data = []
            
            for stock_item in stock_items:
                item = db.query(Item).filter(Item.id == stock_item.item_id).first()
                if item:
                    category = db.query(ItemCategory).filter(ItemCategory.id == item.category_id).first()
                    data.append([
                        item.name,
                        item.item_code,
                        category.name if category else 'Uncategorized',
                        stock_item.quantity,
                        stock_item.available_quantity,
                        float(stock_item.average_cost)
                    ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_accounting_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get accounting report data"""
        
        try:
            # Get accounting data based on template parameters
            from_date = report_data.get('from_date', date.today() - timedelta(days=30))
            to_date = report_data.get('to_date', date.today())
            
            # Get journal entries
            journal_entries = db.query(JournalEntry).filter(
                JournalEntry.company_id == report_data['company_id'],
                JournalEntry.entry_date >= from_date,
                JournalEntry.entry_date <= to_date
            ).all()
            
            # Prepare data
            columns = ['Entry Number', 'Entry Date', 'Reference Type', 'Reference ID', 'Total Debit', 'Total Credit', 'Status']
            data = []
            
            for entry in journal_entries:
                data.append([
                    entry.entry_number,
                    entry.entry_date.strftime('%Y-%m-%d'),
                    entry.reference_type,
                    entry.reference_id,
                    float(entry.total_debit),
                    float(entry.total_credit),
                    entry.status
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting accounting report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_customers_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get customers report data"""
        
        try:
            # Get customers data
            customers = db.query(Customer).filter(
                Customer.company_id == report_data['company_id']
            ).all()
            
            # Prepare data
            columns = ['Customer Name', 'Phone', 'Email', 'City', 'State', 'Total Purchases', 'Last Purchase']
            data = []
            
            for customer in customers:
                data.append([
                    customer.name,
                    customer.phone or '',
                    customer.email or '',
                    customer.city or '',
                    customer.state or '',
                    float(customer.total_purchases or 0),
                    customer.last_purchase_date.strftime('%Y-%m-%d') if customer.last_purchase_date else 'Never'
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting customers report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def get_suppliers_report_data(self, db: Session, template: ReportTemplate, report_data: Dict) -> Dict:
        """Get suppliers report data"""
        
        try:
            # Get suppliers data
            suppliers = db.query(Supplier).filter(
                Supplier.company_id == report_data['company_id']
            ).all()
            
            # Prepare data
            columns = ['Supplier Name', 'Phone', 'Email', 'City', 'State', 'Total Purchases', 'Last Purchase']
            data = []
            
            for supplier in suppliers:
                data.append([
                    supplier.name,
                    supplier.phone or '',
                    supplier.email or '',
                    supplier.city or '',
                    supplier.state or '',
                    float(supplier.total_purchases or 0),
                    supplier.last_purchase_date.strftime('%Y-%m-%d') if supplier.last_purchase_date else 'Never'
                ])
            
            return {
                'columns': columns,
                'data': data,
                'total_records': len(data)
            }
            
        except Exception as e:
            logger.error(f"Error getting suppliers report data: {str(e)}")
            return {'columns': [], 'data': [], 'total_records': 0}
    
    def integrate_report_with_analytics(self, db: Session, report_instance: ReportInstance) -> Dict:
        """Integrate report with analytics"""
        
        try:
            # Create analytics record
            analytics = ReportAnalytics(
                instance_id=report_instance.id,
                view_count=0,
                export_count=0,
                last_viewed=None,
                last_exported=None,
                created_at=datetime.utcnow()
            )
            
            db.add(analytics)
            
            return {
                'status': 'success',
                'analytics_created': True,
                'message': 'Analytics tracking enabled for report'
            }
            
        except Exception as e:
            logger.error(f"Error integrating report with analytics: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_report_with_export(self, db: Session, report_instance: ReportInstance) -> Dict:
        """Integrate report with export functionality"""
        
        try:
            # Create export configuration
            export_config = ReportExport(
                instance_id=report_instance.id,
                export_formats=['pdf', 'excel', 'csv'],
                is_enabled=True,
                created_at=datetime.utcnow()
            )
            
            db.add(export_config)
            
            return {
                'status': 'success',
                'export_enabled': True,
                'formats': ['pdf', 'excel', 'csv'],
                'message': 'Export functionality enabled for report'
            }
            
        except Exception as e:
            logger.error(f"Error integrating report with export: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_report_with_dashboard(self, db: Session, report_instance: ReportInstance) -> Dict:
        """Integrate report with dashboard"""
        
        try:
            # Check if report can be added to dashboard
            if report_instance.total_records > 0:
                # Create dashboard widget
                widget = ReportWidget(
                    instance_id=report_instance.id,
                    widget_type='report',
                    widget_title=report_instance.report_name,
                    widget_config={'report_id': report_instance.id},
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.add(widget)
                
                return {
                    'status': 'success',
                    'widget_created': True,
                    'message': 'Report widget created for dashboard'
                }
            
            return {'status': 'skipped', 'message': 'No data to display in dashboard'}
            
        except Exception as e:
            logger.error(f"Error integrating report with dashboard: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def get_reports_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get comprehensive reports analytics"""
        
        try:
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # Get report templates
            templates = db.query(ReportTemplate).filter(
                ReportTemplate.company_id == company_id,
                ReportTemplate.is_active == True
            ).all()
            
            # Get report instances
            instances = db.query(ReportInstance).filter(
                ReportInstance.company_id == company_id,
                ReportInstance.generated_at >= from_date,
                ReportInstance.generated_at <= to_date
            ).all()
            
            # Calculate metrics
            total_templates = len(templates)
            total_instances = len(instances)
            completed_instances = len([i for i in instances if i.status == 'completed'])
            failed_instances = len([i for i in instances if i.status == 'failed'])
            
            # Get template usage analytics
            template_usage = []
            for template in templates:
                template_instances = [i for i in instances if i.template_id == template.id]
                template_usage.append({
                    'template_id': template.id,
                    'template_name': template.template_name,
                    'usage_count': len(template_instances),
                    'last_used': max([i.generated_at for i in template_instances]) if template_instances else None
                })
            
            return {
                'total_templates': total_templates,
                'total_instances': total_instances,
                'completed_instances': completed_instances,
                'failed_instances': failed_instances,
                'success_rate': (completed_instances / total_instances * 100) if total_instances > 0 else 0,
                'template_usage': template_usage,
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting reports analytics: {str(e)}")
            return {
                'total_templates': 0,
                'total_instances': 0,
                'completed_instances': 0,
                'failed_instances': 0,
                'success_rate': 0,
                'template_usage': [],
                'period': {
                    'from_date': from_date,
                    'to_date': to_date
                }
            }