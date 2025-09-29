# backend/app/services/automation/complete_automation_control_service.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, date
import json
import logging

from ...models.automation import CompleteAutomationSettings, AutomationLog, AutomationApproval
from ...models.company import Company

logger = logging.getLogger(__name__)

class CompleteAutomationControlService:
    """Service for controlling ALL automation features with complete safety controls"""
    
    def __init__(self):
        self.automation_settings = {}
        self.safety_controls = {}
    
    def get_complete_automation_settings(self, db: Session, company_id: int) -> Dict:
        """Get complete automation settings for company - ALL DISABLED BY DEFAULT"""
        
        try:
            # Get company automation settings
            settings = db.query(CompleteAutomationSettings).filter(
                CompleteAutomationSettings.company_id == company_id
            ).first()
            
            if not settings:
                # Create default settings (ALL DISABLED)
                settings = self.create_default_settings(db, company_id)
            
            return {
                'company_id': company_id,
                'accounting_automation': {
                    'auto_double_entry': False,           # DISABLED by default
                    'auto_journal_entries': False,        # DISABLED by default
                    'auto_account_balances': False,       # DISABLED by default
                    'auto_financial_reports': False,      # DISABLED by default
                    'manual_approval_required': True,     # Always require approval
                    'compliance_mode': 'conservative'     # Conservative approach
                },
                'gst_automation': {
                    'auto_prepare_returns': False,        # DISABLED by default
                    'auto_calculate_gst': True,          # Only auto-calculate (safe)
                    'auto_generate_reports': False,      # DISABLED by default
                    'auto_file_returns': False,          # DISABLED by default
                    'auto_send_notifications': True,     # Only notifications (safe)
                    'manual_approval_required': True,     # Always require approval
                    'compliance_mode': 'conservative'     # Conservative approach
                },
                'banking_automation': {
                    'auto_reconcile': False,             # DISABLED by default
                    'auto_match_payments': True,         # Only auto-match (safe)
                    'auto_update_balances': True,        # Only auto-update (safe)
                    'auto_send_confirmations': False,    # DISABLED by default
                    'auto_process_payments': False,      # DISABLED by default
                    'manual_approval_required': True,    # Always require approval
                    'reconciliation_mode': 'manual'      # Manual by default
                },
                'inventory_automation': {
                    'auto_update_stock': True,          # Only auto-update (safe)
                    'auto_low_stock_alerts': True,      # Only alerts (safe)
                    'auto_reorder_suggestions': False,   # DISABLED by default
                    'auto_purchase_orders': False,       # DISABLED by default
                    'auto_inventory_valuation': False,    # DISABLED by default
                    'manual_approval_required': True,     # Always require approval
                    'inventory_mode': 'manual'           # Manual by default
                },
                'sales_automation': {
                    'auto_create_invoices': False,       # DISABLED by default
                    'auto_send_invoices': False,         # DISABLED by default
                    'auto_payment_reminders': False,     # DISABLED by default
                    'auto_customer_analytics': True,     # Only analytics (safe)
                    'auto_loyalty_points': True,         # Only points (safe)
                    'manual_approval_required': True,     # Always require approval
                    'sales_mode': 'manual'               # Manual by default
                },
                'purchase_automation': {
                    'auto_create_bills': False,         # DISABLED by default
                    'auto_send_purchase_orders': False,  # DISABLED by default
                    'auto_payment_processing': False,    # DISABLED by default
                    'auto_supplier_analytics': True,     # Only analytics (safe)
                    'auto_cost_updates': True,          # Only cost updates (safe)
                    'manual_approval_required': True,    # Always require approval
                    'purchase_mode': 'manual'            # Manual by default
                },
                'pos_automation': {
                    'auto_inventory_updates': True,     # Only updates (safe)
                    'auto_customer_updates': True,      # Only updates (safe)
                    'auto_loyalty_processing': True,    # Only processing (safe)
                    'auto_sales_records': False,        # DISABLED by default
                    'auto_payment_processing': False,    # DISABLED by default
                    'manual_approval_required': True,   # Always require approval
                    'pos_mode': 'semi_auto'             # Semi-automatic by default
                },
                'reports_automation': {
                    'auto_generate_reports': False,     # DISABLED by default
                    'auto_send_reports': False,         # DISABLED by default
                    'auto_schedule_reports': False,     # DISABLED by default
                    'auto_analytics_updates': True,     # Only updates (safe)
                    'auto_dashboard_updates': True,     # Only updates (safe)
                    'manual_approval_required': True,   # Always require approval
                    'reports_mode': 'manual'            # Manual by default
                },
                'safety_controls': {
                    'audit_trail_enabled': True,        # Always enabled
                    'rollback_enabled': True,            # Always enabled
                    'approval_workflow_enabled': True,   # Always enabled
                    'exception_handling_enabled': True,  # Always enabled
                    'manual_override_enabled': True,     # Always enabled
                    'safety_mode': 'maximum'            # Maximum safety
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting complete automation settings: {str(e)}")
            return {'error': str(e)}
    
    def create_default_settings(self, db: Session, company_id: int) -> CompleteAutomationSettings:
        """Create default automation settings - ALL DISABLED"""
        
        try:
            settings = CompleteAutomationSettings(
                company_id=company_id,
                
                # Accounting Settings (ALL DISABLED)
                auto_double_entry=False,
                auto_journal_entries=False,
                auto_account_balances=False,
                auto_financial_reports=False,
                accounting_manual_approval=True,
                accounting_compliance_mode='conservative',
                
                # GST Settings (ALL DISABLED)
                gst_auto_prepare_returns=False,
                gst_auto_calculate=True,  # Only auto-calculate (safe)
                gst_auto_generate_reports=False,
                gst_auto_file_returns=False,
                gst_auto_notifications=True,  # Only notifications (safe)
                gst_manual_approval=True,
                gst_compliance_mode='conservative',
                
                # Banking Settings (ALL DISABLED)
                bank_auto_reconcile=False,
                bank_auto_match=True,  # Only auto-match (safe)
                bank_auto_update=True,  # Only auto-update (safe)
                bank_auto_confirmations=False,
                bank_auto_process_payments=False,
                bank_manual_approval=True,
                bank_reconciliation_mode='manual',
                
                # Inventory Settings (ALL DISABLED)
                inventory_auto_update_stock=True,  # Only updates (safe)
                inventory_auto_low_stock_alerts=True,  # Only alerts (safe)
                inventory_auto_reorder_suggestions=False,
                inventory_auto_purchase_orders=False,
                inventory_auto_valuation=False,
                inventory_manual_approval=True,
                inventory_mode='manual',
                
                # Sales Settings (ALL DISABLED)
                sales_auto_create_invoices=False,
                sales_auto_send_invoices=False,
                sales_auto_payment_reminders=False,
                sales_auto_customer_analytics=True,  # Only analytics (safe)
                sales_auto_loyalty_points=True,  # Only points (safe)
                sales_manual_approval=True,
                sales_mode='manual',
                
                # Purchase Settings (ALL DISABLED)
                purchase_auto_create_bills=False,
                purchase_auto_send_orders=False,
                purchase_auto_payment_processing=False,
                purchase_auto_supplier_analytics=True,  # Only analytics (safe)
                purchase_auto_cost_updates=True,  # Only cost updates (safe)
                purchase_manual_approval=True,
                purchase_mode='manual',
                
                # POS Settings (ALL DISABLED)
                pos_auto_inventory_updates=True,  # Only updates (safe)
                pos_auto_customer_updates=True,  # Only updates (safe)
                pos_auto_loyalty_processing=True,  # Only processing (safe)
                pos_auto_sales_records=False,
                pos_auto_payment_processing=False,
                pos_manual_approval=True,
                pos_mode='semi_auto',
                
                # Reports Settings (ALL DISABLED)
                reports_auto_generate=False,
                reports_auto_send=False,
                reports_auto_schedule=False,
                reports_auto_analytics_updates=True,  # Only updates (safe)
                reports_auto_dashboard_updates=True,  # Only updates (safe)
                reports_manual_approval=True,
                reports_mode='manual',
                
                # Safety Controls (ALL ENABLED)
                audit_trail_enabled=True,
                rollback_enabled=True,
                approval_workflow_enabled=True,
                exception_handling_enabled=True,
                manual_override_enabled=True,
                safety_mode='maximum',
                
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(settings)
            db.commit()
            
            return settings
            
        except Exception as e:
            logger.error(f"Error creating default settings: {str(e)}")
            db.rollback()
            raise ValueError(f"Failed to create default settings: {str(e)}")
    
    def update_automation_settings(self, db: Session, company_id: int, settings_data: Dict) -> Dict:
        """Update automation settings with safety controls"""
        
        try:
            # Get existing settings
            settings = db.query(CompleteAutomationSettings).filter(
                CompleteAutomationSettings.company_id == company_id
            ).first()
            
            if not settings:
                settings = self.create_default_settings(db, company_id)
            
            # Update settings with safety controls
            if 'accounting_automation' in settings_data:
                accounting_settings = settings_data['accounting_automation']
                
                # Safety check: If auto-double-entry is enabled, manual approval must be enabled
                if accounting_settings.get('auto_double_entry', False):
                    if not accounting_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-double-entry is enabled")
                
                settings.auto_double_entry = accounting_settings.get('auto_double_entry', False)
                settings.auto_journal_entries = accounting_settings.get('auto_journal_entries', False)
                settings.auto_account_balances = accounting_settings.get('auto_account_balances', False)
                settings.auto_financial_reports = accounting_settings.get('auto_financial_reports', False)
                settings.accounting_manual_approval = accounting_settings.get('manual_approval_required', True)
                settings.accounting_compliance_mode = accounting_settings.get('compliance_mode', 'conservative')
            
            if 'gst_automation' in settings_data:
                gst_settings = settings_data['gst_automation']
                
                # Safety check: If auto-prepare is enabled, manual approval must be enabled
                if gst_settings.get('auto_prepare_returns', False):
                    if not gst_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-preparing GST returns")
                
                settings.gst_auto_prepare_returns = gst_settings.get('auto_prepare_returns', False)
                settings.gst_auto_calculate = gst_settings.get('auto_calculate_gst', True)
                settings.gst_auto_generate_reports = gst_settings.get('auto_generate_reports', False)
                settings.gst_auto_file_returns = gst_settings.get('auto_file_returns', False)
                settings.gst_auto_notifications = gst_settings.get('auto_send_notifications', True)
                settings.gst_manual_approval = gst_settings.get('manual_approval_required', True)
                settings.gst_compliance_mode = gst_settings.get('compliance_mode', 'conservative')
            
            if 'banking_automation' in settings_data:
                bank_settings = settings_data['banking_automation']
                
                # Safety check: If auto-reconcile is enabled, manual approval must be enabled
                if bank_settings.get('auto_reconcile', False):
                    if not bank_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-reconciling bank transactions")
                
                settings.bank_auto_reconcile = bank_settings.get('auto_reconcile', False)
                settings.bank_auto_match = bank_settings.get('auto_match_payments', True)
                settings.bank_auto_update = bank_settings.get('auto_update_balances', True)
                settings.bank_auto_confirmations = bank_settings.get('auto_send_confirmations', False)
                settings.bank_auto_process_payments = bank_settings.get('auto_process_payments', False)
                settings.bank_manual_approval = bank_settings.get('manual_approval_required', True)
                settings.bank_reconciliation_mode = bank_settings.get('reconciliation_mode', 'manual')
            
            if 'inventory_automation' in settings_data:
                inventory_settings = settings_data['inventory_automation']
                
                # Safety check: If auto-purchase-orders is enabled, manual approval must be enabled
                if inventory_settings.get('auto_purchase_orders', False):
                    if not inventory_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-creating purchase orders")
                
                settings.inventory_auto_update_stock = inventory_settings.get('auto_update_stock', True)
                settings.inventory_auto_low_stock_alerts = inventory_settings.get('auto_low_stock_alerts', True)
                settings.inventory_auto_reorder_suggestions = inventory_settings.get('auto_reorder_suggestions', False)
                settings.inventory_auto_purchase_orders = inventory_settings.get('auto_purchase_orders', False)
                settings.inventory_auto_valuation = inventory_settings.get('auto_inventory_valuation', False)
                settings.inventory_manual_approval = inventory_settings.get('manual_approval_required', True)
                settings.inventory_mode = inventory_settings.get('inventory_mode', 'manual')
            
            if 'sales_automation' in settings_data:
                sales_settings = settings_data['sales_automation']
                
                # Safety check: If auto-create-invoices is enabled, manual approval must be enabled
                if sales_settings.get('auto_create_invoices', False):
                    if not sales_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-creating invoices")
                
                settings.sales_auto_create_invoices = sales_settings.get('auto_create_invoices', False)
                settings.sales_auto_send_invoices = sales_settings.get('auto_send_invoices', False)
                settings.sales_auto_payment_reminders = sales_settings.get('auto_payment_reminders', False)
                settings.sales_auto_customer_analytics = sales_settings.get('auto_customer_analytics', True)
                settings.sales_auto_loyalty_points = sales_settings.get('auto_loyalty_points', True)
                settings.sales_manual_approval = sales_settings.get('manual_approval_required', True)
                settings.sales_mode = sales_settings.get('sales_mode', 'manual')
            
            if 'purchase_automation' in settings_data:
                purchase_settings = settings_data['purchase_automation']
                
                # Safety check: If auto-create-bills is enabled, manual approval must be enabled
                if purchase_settings.get('auto_create_bills', False):
                    if not purchase_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-creating bills")
                
                settings.purchase_auto_create_bills = purchase_settings.get('auto_create_bills', False)
                settings.purchase_auto_send_orders = purchase_settings.get('auto_send_purchase_orders', False)
                settings.purchase_auto_payment_processing = purchase_settings.get('auto_payment_processing', False)
                settings.purchase_auto_supplier_analytics = purchase_settings.get('auto_supplier_analytics', True)
                settings.purchase_auto_cost_updates = purchase_settings.get('auto_cost_updates', True)
                settings.purchase_manual_approval = purchase_settings.get('manual_approval_required', True)
                settings.purchase_mode = purchase_settings.get('purchase_mode', 'manual')
            
            if 'pos_automation' in settings_data:
                pos_settings = settings_data['pos_automation']
                
                # Safety check: If auto-sales-records is enabled, manual approval must be enabled
                if pos_settings.get('auto_sales_records', False):
                    if not pos_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-creating sales records")
                
                settings.pos_auto_inventory_updates = pos_settings.get('auto_inventory_updates', True)
                settings.pos_auto_customer_updates = pos_settings.get('auto_customer_updates', True)
                settings.pos_auto_loyalty_processing = pos_settings.get('auto_loyalty_processing', True)
                settings.pos_auto_sales_records = pos_settings.get('auto_sales_records', False)
                settings.pos_auto_payment_processing = pos_settings.get('auto_payment_processing', False)
                settings.pos_manual_approval = pos_settings.get('manual_approval_required', True)
                settings.pos_mode = pos_settings.get('pos_mode', 'semi_auto')
            
            if 'reports_automation' in settings_data:
                reports_settings = settings_data['reports_automation']
                
                # Safety check: If auto-generate-reports is enabled, manual approval must be enabled
                if reports_settings.get('auto_generate_reports', False):
                    if not reports_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-generating reports")
                
                settings.reports_auto_generate = reports_settings.get('auto_generate_reports', False)
                settings.reports_auto_send = reports_settings.get('auto_send_reports', False)
                settings.reports_auto_schedule = reports_settings.get('auto_schedule_reports', False)
                settings.reports_auto_analytics_updates = reports_settings.get('auto_analytics_updates', True)
                settings.reports_auto_dashboard_updates = reports_settings.get('auto_dashboard_updates', True)
                settings.reports_manual_approval = reports_settings.get('manual_approval_required', True)
                settings.reports_mode = reports_settings.get('reports_mode', 'manual')
            
            if 'safety_controls' in settings_data:
                safety_settings = settings_data['safety_controls']
                settings.audit_trail_enabled = safety_settings.get('audit_trail_enabled', True)
                settings.rollback_enabled = safety_settings.get('rollback_enabled', True)
                settings.approval_workflow_enabled = safety_settings.get('approval_workflow_enabled', True)
                settings.exception_handling_enabled = safety_settings.get('exception_handling_enabled', True)
                settings.manual_override_enabled = safety_settings.get('manual_override_enabled', True)
                settings.safety_mode = safety_settings.get('safety_mode', 'maximum')
            
            settings.updated_at = datetime.utcnow()
            db.commit()
            
            # Log the changes
            self.log_automation_change(db, company_id, 'settings_updated', settings_data)
            
            return {
                'success': True,
                'message': 'Automation settings updated successfully',
                'settings': self.get_complete_automation_settings(db, company_id)
            }
            
        except Exception as e:
            logger.error(f"Error updating automation settings: {str(e)}")
            db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_automation_summary(self, db: Session, company_id: int) -> Dict:
        """Get automation summary - what's enabled/disabled"""
        
        try:
            settings = self.get_complete_automation_settings(db, company_id)
            
            return {
                'automation_summary': {
                    'accounting_automation': {
                        'auto_double_entry': settings['accounting_automation']['auto_double_entry'],
                        'auto_journal_entries': settings['accounting_automation']['auto_journal_entries'],
                        'auto_account_balances': settings['accounting_automation']['auto_account_balances'],
                        'auto_financial_reports': settings['accounting_automation']['auto_financial_reports'],
                        'status': 'manual' if not any([
                            settings['accounting_automation']['auto_double_entry'],
                            settings['accounting_automation']['auto_journal_entries'],
                            settings['accounting_automation']['auto_account_balances'],
                            settings['accounting_automation']['auto_financial_reports']
                        ]) else 'semi_auto'
                    },
                    'gst_automation': {
                        'auto_prepare_returns': settings['gst_automation']['auto_prepare_returns'],
                        'auto_generate_reports': settings['gst_automation']['auto_generate_reports'],
                        'auto_file_returns': settings['gst_automation']['auto_file_returns'],
                        'status': 'manual' if not any([
                            settings['gst_automation']['auto_prepare_returns'],
                            settings['gst_automation']['auto_generate_reports'],
                            settings['gst_automation']['auto_file_returns']
                        ]) else 'semi_auto'
                    },
                    'banking_automation': {
                        'auto_reconcile': settings['banking_automation']['auto_reconcile'],
                        'auto_send_confirmations': settings['banking_automation']['auto_send_confirmations'],
                        'auto_process_payments': settings['banking_automation']['auto_process_payments'],
                        'status': 'manual' if not any([
                            settings['banking_automation']['auto_reconcile'],
                            settings['banking_automation']['auto_send_confirmations'],
                            settings['banking_automation']['auto_process_payments']
                        ]) else 'semi_auto'
                    },
                    'inventory_automation': {
                        'auto_reorder_suggestions': settings['inventory_automation']['auto_reorder_suggestions'],
                        'auto_purchase_orders': settings['inventory_automation']['auto_purchase_orders'],
                        'auto_inventory_valuation': settings['inventory_automation']['auto_inventory_valuation'],
                        'status': 'manual' if not any([
                            settings['inventory_automation']['auto_reorder_suggestions'],
                            settings['inventory_automation']['auto_purchase_orders'],
                            settings['inventory_automation']['auto_inventory_valuation']
                        ]) else 'semi_auto'
                    },
                    'sales_automation': {
                        'auto_create_invoices': settings['sales_automation']['auto_create_invoices'],
                        'auto_send_invoices': settings['sales_automation']['auto_send_invoices'],
                        'auto_payment_reminders': settings['sales_automation']['auto_payment_reminders'],
                        'status': 'manual' if not any([
                            settings['sales_automation']['auto_create_invoices'],
                            settings['sales_automation']['auto_send_invoices'],
                            settings['sales_automation']['auto_payment_reminders']
                        ]) else 'semi_auto'
                    },
                    'purchase_automation': {
                        'auto_create_bills': settings['purchase_automation']['auto_create_bills'],
                        'auto_send_purchase_orders': settings['purchase_automation']['auto_send_purchase_orders'],
                        'auto_payment_processing': settings['purchase_automation']['auto_payment_processing'],
                        'status': 'manual' if not any([
                            settings['purchase_automation']['auto_create_bills'],
                            settings['purchase_automation']['auto_send_purchase_orders'],
                            settings['purchase_automation']['auto_payment_processing']
                        ]) else 'semi_auto'
                    },
                    'pos_automation': {
                        'auto_sales_records': settings['pos_automation']['auto_sales_records'],
                        'auto_payment_processing': settings['pos_automation']['auto_payment_processing'],
                        'status': 'semi_auto' if settings['pos_automation']['pos_mode'] == 'semi_auto' else 'manual'
                    },
                    'reports_automation': {
                        'auto_generate_reports': settings['reports_automation']['auto_generate_reports'],
                        'auto_send_reports': settings['reports_automation']['auto_send_reports'],
                        'auto_schedule_reports': settings['reports_automation']['auto_schedule_reports'],
                        'status': 'manual' if not any([
                            settings['reports_automation']['auto_generate_reports'],
                            settings['reports_automation']['auto_send_reports'],
                            settings['reports_automation']['auto_schedule_reports']
                        ]) else 'semi_auto'
                    }
                },
                'safety_controls': {
                    'audit_trail_enabled': settings['safety_controls']['audit_trail_enabled'],
                    'rollback_enabled': settings['safety_controls']['rollback_enabled'],
                    'approval_workflow_enabled': settings['safety_controls']['approval_workflow_enabled'],
                    'exception_handling_enabled': settings['safety_controls']['exception_handling_enabled'],
                    'manual_override_enabled': settings['safety_controls']['manual_override_enabled'],
                    'safety_mode': settings['safety_controls']['safety_mode']
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting automation summary: {str(e)}")
            return {'error': str(e)}
    
    def log_automation_change(self, db: Session, company_id: int, action: str, details: Dict) -> None:
        """Log automation change for audit trail"""
        
        try:
            log = AutomationLog(
                company_id=company_id,
                automation_type=details.get('automation_type', 'general'),
                action=action,
                reference_id=details.get('reference_id'),
                status='completed',
                details=details,
                created_at=datetime.utcnow()
            )
            
            db.add(log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging automation change: {str(e)}")