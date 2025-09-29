# backend/app/services/automation/automation_control_service.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, date
import json
import logging

from ...models.automation import AutomationSettings, AutomationLog, AutomationApproval
from ...models.compliance.indian_compliance import GSTReturn, GSTPayment
from ...models.banking import BankTransaction, BankReconciliation
from ...models.company import Company

logger = logging.getLogger(__name__)

class AutomationControlService:
    """Service for controlling automation features with safety controls"""
    
    def __init__(self):
        self.automation_settings = {}
        self.safety_controls = {}
    
    def get_automation_settings(self, db: Session, company_id: int) -> Dict:
        """Get automation settings for company"""
        
        try:
            # Get company automation settings
            settings = db.query(AutomationSettings).filter(
                AutomationSettings.company_id == company_id
            ).first()
            
            if not settings:
                # Create default settings (all manual)
                settings = self.create_default_settings(db, company_id)
            
            return {
                'company_id': company_id,
                'gst_automation': {
                    'auto_prepare_returns': settings.gst_auto_prepare_returns,
                    'auto_calculate_gst': settings.gst_auto_calculate,
                    'auto_generate_reports': settings.gst_auto_generate_reports,
                    'auto_send_notifications': settings.gst_auto_notifications,
                    'manual_approval_required': settings.gst_manual_approval,
                    'compliance_mode': settings.gst_compliance_mode
                },
                'banking_automation': {
                    'auto_reconcile': settings.bank_auto_reconcile,
                    'auto_match_payments': settings.bank_auto_match,
                    'auto_update_balances': settings.bank_auto_update,
                    'auto_send_confirmations': settings.bank_auto_confirmations,
                    'manual_approval_required': settings.bank_manual_approval,
                    'reconciliation_mode': settings.bank_reconciliation_mode
                },
                'safety_controls': {
                    'audit_trail_enabled': settings.audit_trail_enabled,
                    'rollback_enabled': settings.rollback_enabled,
                    'approval_workflow_enabled': settings.approval_workflow_enabled,
                    'exception_handling_enabled': settings.exception_handling_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting automation settings: {str(e)}")
            return {'error': str(e)}
    
    def create_default_settings(self, db: Session, company_id: int) -> AutomationSettings:
        """Create default automation settings (all manual)"""
        
        try:
            settings = AutomationSettings(
                company_id=company_id,
                # GST Settings (all manual by default)
                gst_auto_prepare_returns=False,
                gst_auto_calculate=True,  # Only auto-calculate, not auto-file
                gst_auto_generate_reports=False,
                gst_auto_notifications=True,  # Only notifications
                gst_manual_approval=True,
                gst_compliance_mode='conservative',
                
                # Banking Settings (all manual by default)
                bank_auto_reconcile=False,
                bank_auto_match=True,  # Only auto-match, not auto-reconcile
                bank_auto_update=True,  # Only auto-update balances
                bank_auto_confirmations=False,
                bank_manual_approval=True,
                bank_reconciliation_mode='manual',
                
                # Safety Controls (all enabled by default)
                audit_trail_enabled=True,
                rollback_enabled=True,
                approval_workflow_enabled=True,
                exception_handling_enabled=True,
                
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
            settings = db.query(AutomationSettings).filter(
                AutomationSettings.company_id == company_id
            ).first()
            
            if not settings:
                settings = self.create_default_settings(db, company_id)
            
            # Update settings with safety controls
            if 'gst_automation' in settings_data:
                gst_settings = settings_data['gst_automation']
                
                # Safety check: If auto-prepare is enabled, manual approval must be enabled
                if gst_settings.get('auto_prepare_returns', False):
                    if not gst_settings.get('manual_approval_required', True):
                        raise ValueError("Manual approval is required when auto-preparing GST returns")
                
                settings.gst_auto_prepare_returns = gst_settings.get('auto_prepare_returns', False)
                settings.gst_auto_calculate = gst_settings.get('auto_calculate_gst', True)
                settings.gst_auto_generate_reports = gst_settings.get('auto_generate_reports', False)
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
                settings.bank_manual_approval = bank_settings.get('manual_approval_required', True)
                settings.bank_reconciliation_mode = bank_settings.get('reconciliation_mode', 'manual')
            
            if 'safety_controls' in settings_data:
                safety_settings = settings_data['safety_controls']
                settings.audit_trail_enabled = safety_settings.get('audit_trail_enabled', True)
                settings.rollback_enabled = safety_settings.get('rollback_enabled', True)
                settings.approval_workflow_enabled = safety_settings.get('approval_workflow_enabled', True)
                settings.exception_handling_enabled = safety_settings.get('exception_handling_enabled', True)
            
            settings.updated_at = datetime.utcnow()
            db.commit()
            
            # Log the changes
            self.log_automation_change(db, company_id, 'settings_updated', settings_data)
            
            return {
                'success': True,
                'message': 'Automation settings updated successfully',
                'settings': self.get_automation_settings(db, company_id)
            }
            
        except Exception as e:
            logger.error(f"Error updating automation settings: {str(e)}")
            db.rollback()
            return {'success': False, 'error': str(e)}
    
    def process_gst_automation(self, db: Session, company_id: int, return_data: Dict) -> Dict:
        """Process GST automation with safety controls"""
        
        try:
            # Get automation settings
            settings = self.get_automation_settings(db, company_id)
            
            if not settings['gst_automation']['auto_prepare_returns']:
                return {
                    'success': False,
                    'message': 'GST automation is disabled',
                    'requires_manual_processing': True
                }
            
            # Check if manual approval is required
            if settings['gst_automation']['manual_approval_required']:
                # Create approval request
                approval_request = AutomationApproval(
                    company_id=company_id,
                    automation_type='gst_return',
                    reference_id=return_data.get('return_id'),
                    reference_data=return_data,
                    status='pending_approval',
                    created_at=datetime.utcnow()
                )
                
                db.add(approval_request)
                db.commit()
                
                return {
                    'success': True,
                    'message': 'GST return prepared, awaiting manual approval',
                    'approval_request_id': approval_request.id,
                    'requires_approval': True
                }
            
            # Process automatically (if approved)
            result = self.process_gst_return_automatically(db, company_id, return_data)
            
            # Log the automation
            self.log_automation_change(db, company_id, 'gst_return_processed', return_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing GST automation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_banking_automation(self, db: Session, company_id: int, transaction_data: Dict) -> Dict:
        """Process banking automation with safety controls"""
        
        try:
            # Get automation settings
            settings = self.get_automation_settings(db, company_id)
            
            if not settings['banking_automation']['auto_reconcile']:
                return {
                    'success': False,
                    'message': 'Banking automation is disabled',
                    'requires_manual_processing': True
                }
            
            # Check if manual approval is required
            if settings['banking_automation']['manual_approval_required']:
                # Create approval request
                approval_request = AutomationApproval(
                    company_id=company_id,
                    automation_type='bank_reconciliation',
                    reference_id=transaction_data.get('transaction_id'),
                    reference_data=transaction_data,
                    status='pending_approval',
                    created_at=datetime.utcnow()
                )
                
                db.add(approval_request)
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Bank reconciliation prepared, awaiting manual approval',
                    'approval_request_id': approval_request.id,
                    'requires_approval': True
                }
            
            # Process automatically (if approved)
            result = self.process_bank_reconciliation_automatically(db, company_id, transaction_data)
            
            # Log the automation
            self.log_automation_change(db, company_id, 'bank_reconciliation_processed', transaction_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing banking automation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def approve_automation_request(self, db: Session, company_id: int, approval_id: int, approved: bool, comments: str = None) -> Dict:
        """Approve or reject automation request"""
        
        try:
            # Get approval request
            approval_request = db.query(AutomationApproval).filter(
                AutomationApproval.id == approval_id,
                AutomationApproval.company_id == company_id,
                AutomationApproval.status == 'pending_approval'
            ).first()
            
            if not approval_request:
                return {'success': False, 'message': 'Approval request not found'}
            
            # Update approval status
            approval_request.status = 'approved' if approved else 'rejected'
            approval_request.approved_by = 'user'  # This would be the actual user ID
            approval_request.approved_at = datetime.utcnow()
            approval_request.comments = comments
            
            db.commit()
            
            # If approved, process the automation
            if approved:
                if approval_request.automation_type == 'gst_return':
                    result = self.process_gst_return_automatically(db, company_id, approval_request.reference_data)
                elif approval_request.automation_type == 'bank_reconciliation':
                    result = self.process_bank_reconciliation_automatically(db, company_id, approval_request.reference_data)
                else:
                    result = {'success': False, 'message': 'Unknown automation type'}
            else:
                result = {'success': True, 'message': 'Automation request rejected'}
            
            # Log the approval
            self.log_automation_change(db, company_id, 'automation_approved' if approved else 'automation_rejected', {
                'approval_id': approval_id,
                'approved': approved,
                'comments': comments
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error approving automation request: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_automation_logs(self, db: Session, company_id: int, limit: int = 100) -> List[Dict]:
        """Get automation logs for audit trail"""
        
        try:
            logs = db.query(AutomationLog).filter(
                AutomationLog.company_id == company_id
            ).order_by(AutomationLog.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'id': log.id,
                    'automation_type': log.automation_type,
                    'action': log.action,
                    'reference_id': log.reference_id,
                    'status': log.status,
                    'created_at': log.created_at,
                    'details': log.details
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Error getting automation logs: {str(e)}")
            return []
    
    def rollback_automation(self, db: Session, company_id: int, log_id: int) -> Dict:
        """Rollback automation action"""
        
        try:
            # Get automation log
            log = db.query(AutomationLog).filter(
                AutomationLog.id == log_id,
                AutomationLog.company_id == company_id
            ).first()
            
            if not log:
                return {'success': False, 'message': 'Automation log not found'}
            
            if not log.rollback_enabled:
                return {'success': False, 'message': 'Rollback not enabled for this action'}
            
            # Perform rollback based on automation type
            if log.automation_type == 'gst_return':
                result = self.rollback_gst_return(db, company_id, log.reference_id)
            elif log.automation_type == 'bank_reconciliation':
                result = self.rollback_bank_reconciliation(db, company_id, log.reference_id)
            else:
                result = {'success': False, 'message': 'Unknown automation type'}
            
            # Log the rollback
            self.log_automation_change(db, company_id, 'automation_rollback', {
                'original_log_id': log_id,
                'rollback_result': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error rolling back automation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_gst_return_automatically(self, db: Session, company_id: int, return_data: Dict) -> Dict:
        """Process GST return automatically (after approval)"""
        
        try:
            # This would contain the actual GST return processing logic
            # For now, returning a placeholder
            return {
                'success': True,
                'message': 'GST return processed automatically',
                'return_id': return_data.get('return_id'),
                'processed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error processing GST return automatically: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_bank_reconciliation_automatically(self, db: Session, company_id: int, transaction_data: Dict) -> Dict:
        """Process bank reconciliation automatically (after approval)"""
        
        try:
            # This would contain the actual bank reconciliation logic
            # For now, returning a placeholder
            return {
                'success': True,
                'message': 'Bank reconciliation processed automatically',
                'transaction_id': transaction_data.get('transaction_id'),
                'processed_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error processing bank reconciliation automatically: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def rollback_gst_return(self, db: Session, company_id: int, return_id: int) -> Dict:
        """Rollback GST return"""
        
        try:
            # This would contain the actual rollback logic
            return {
                'success': True,
                'message': 'GST return rolled back successfully',
                'return_id': return_id
            }
            
        except Exception as e:
            logger.error(f"Error rolling back GST return: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def rollback_bank_reconciliation(self, db: Session, company_id: int, transaction_id: int) -> Dict:
        """Rollback bank reconciliation"""
        
        try:
            # This would contain the actual rollback logic
            return {
                'success': True,
                'message': 'Bank reconciliation rolled back successfully',
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            logger.error(f"Error rolling back bank reconciliation: {str(e)}")
            return {'success': False, 'error': str(e)}
    
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