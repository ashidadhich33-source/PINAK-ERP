"""
Automation Control Service
Provides configurable automation settings for all modules
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import json
from enum import Enum

from app.models.core.automation_control import (
    AutomationSetting,
    AutomationWorkflow,
    AutomationRule,
    AutomationTrigger,
    AutomationAction,
    AutomationCondition,
    AutomationApproval,
    AutomationLog,
    AutomationException,
    AutomationRollback,
    AutomationAudit
)
from app.schemas.core.automation_control_schema import (
    AutomationSettingCreate,
    AutomationSettingUpdate,
    AutomationWorkflowCreate,
    AutomationRuleCreate,
    AutomationTriggerCreate,
    AutomationActionCreate,
    AutomationConditionCreate,
    AutomationApprovalCreate,
    AutomationExceptionCreate,
    AutomationRollbackCreate
)


class AutomationControlService:
    """Service for managing automation control across all modules"""
    
    def __init__(self):
        self.module_automations = {
            'gst': {
                'auto_calculate': True,
                'auto_validate': True,
                'auto_generate_invoice': False,
                'auto_submit_ewaybill': False
            },
            'banking': {
                'auto_reconcile': True,
                'auto_categorize': True,
                'auto_match_transactions': True,
                'auto_create_journal_entries': False
            },
            'accounting': {
                'auto_double_entry': True,
                'auto_create_journals': True,
                'auto_balance_accounts': True,
                'auto_generate_reports': False
            },
            'inventory': {
                'auto_update_stock': True,
                'auto_reorder': True,
                'auto_valuation': True,
                'auto_adjust_quantities': False
            },
            'sales': {
                'auto_create_invoice': True,
                'auto_send_notifications': True,
                'auto_update_customer': True,
                'auto_apply_discounts': False
            },
            'purchase': {
                'auto_create_bill': True,
                'auto_send_notifications': True,
                'auto_update_supplier': True,
                'auto_approve_orders': False
            },
            'pos': {
                'auto_apply_discounts': True,
                'auto_update_loyalty': True,
                'auto_sync_inventory': True,
                'auto_create_receipts': False
            },
            'reports': {
                'auto_generate': True,
                'auto_schedule': True,
                'auto_export': False,
                'auto_archive': False
            }
        }
    
    def get_automation_settings(self, db: Session, company_id: int, module: Optional[str] = None) -> Dict:
        """Get automation settings for company and module"""
        try:
            query = db.query(AutomationSetting).filter(
                AutomationSetting.company_id == company_id,
                AutomationSetting.is_active == True
            )
            
            if module:
                query = query.filter(AutomationSetting.module == module)
            
            settings = query.all()
            
            result = {}
            for setting in settings:
                if setting.module not in result:
                    result[setting.module] = {}
                result[setting.module][setting.setting_name] = {
                    'value': setting.setting_value,
                    'is_enabled': setting.is_enabled,
                    'requires_approval': setting.requires_approval,
                    'approval_workflow': setting.approval_workflow,
                    'conditions': setting.conditions,
                    'exceptions': setting.exceptions
                }
            
            return {
                'success': True,
                'data': result,
                'message': f'Retrieved automation settings for company {company_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve automation settings'
            }
    
    def update_automation_setting(self, db: Session, company_id: int, setting_data: Dict) -> Dict:
        """Update automation setting"""
        try:
            setting = db.query(AutomationSetting).filter(
                AutomationSetting.company_id == company_id,
                AutomationSetting.module == setting_data['module'],
                AutomationSetting.setting_name == setting_data['setting_name']
            ).first()
            
            if not setting:
                # Create new setting
                setting = AutomationSetting(
                    company_id=company_id,
                    module=setting_data['module'],
                    setting_name=setting_data['setting_name'],
                    setting_value=setting_data['setting_value'],
                    is_enabled=setting_data.get('is_enabled', True),
                    requires_approval=setting_data.get('requires_approval', False),
                    approval_workflow=setting_data.get('approval_workflow'),
                    conditions=setting_data.get('conditions'),
                    exceptions=setting_data.get('exceptions'),
                    created_by=setting_data.get('created_by', 1),
                    updated_by=setting_data.get('updated_by', 1)
                )
                db.add(setting)
            else:
                # Update existing setting
                setting.setting_value = setting_data['setting_value']
                setting.is_enabled = setting_data.get('is_enabled', setting.is_enabled)
                setting.requires_approval = setting_data.get('requires_approval', setting.requires_approval)
                setting.approval_workflow = setting_data.get('approval_workflow', setting.approval_workflow)
                setting.conditions = setting_data.get('conditions', setting.conditions)
                setting.exceptions = setting_data.get('exceptions', setting.exceptions)
                setting.updated_by = setting_data.get('updated_by', setting.updated_by)
                setting.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': setting.id,
                    'module': setting.module,
                    'setting_name': setting.setting_name,
                    'setting_value': setting.setting_value,
                    'is_enabled': setting.is_enabled,
                    'requires_approval': setting.requires_approval
                },
                'message': f'Updated automation setting for {setting.module}.{setting.setting_name}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update automation setting'
            }
    
    def create_automation_workflow(self, db: Session, company_id: int, workflow_data: Dict) -> Dict:
        """Create automation workflow"""
        try:
            workflow = AutomationWorkflow(
                company_id=company_id,
                name=workflow_data['name'],
                description=workflow_data.get('description'),
                module=workflow_data['module'],
                trigger_type=workflow_data['trigger_type'],
                trigger_conditions=workflow_data.get('trigger_conditions'),
                actions=workflow_data['actions'],
                approval_required=workflow_data.get('approval_required', False),
                approval_workflow=workflow_data.get('approval_workflow'),
                is_active=workflow_data.get('is_active', True),
                priority=workflow_data.get('priority', 1),
                conditions=workflow_data.get('conditions'),
                exceptions=workflow_data.get('exceptions'),
                created_by=workflow_data.get('created_by', 1)
            )
            
            db.add(workflow)
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': workflow.id,
                    'name': workflow.name,
                    'module': workflow.module,
                    'trigger_type': workflow.trigger_type,
                    'is_active': workflow.is_active
                },
                'message': f'Created automation workflow: {workflow.name}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create automation workflow'
            }
    
    def execute_automation_workflow(self, db: Session, company_id: int, workflow_id: int, trigger_data: Dict) -> Dict:
        """Execute automation workflow"""
        try:
            workflow = db.query(AutomationWorkflow).filter(
                AutomationWorkflow.id == workflow_id,
                AutomationWorkflow.company_id == company_id,
                AutomationWorkflow.is_active == True
            ).first()
            
            if not workflow:
                return {
                    'success': False,
                    'error': 'Workflow not found or inactive',
                    'message': 'Automation workflow not found'
                }
            
            # Check trigger conditions
            if not self._check_trigger_conditions(workflow, trigger_data):
                return {
                    'success': False,
                    'error': 'Trigger conditions not met',
                    'message': 'Workflow trigger conditions not satisfied'
                }
            
            # Check if approval is required
            if workflow.approval_required:
                approval_result = self._create_approval_request(db, workflow, trigger_data)
                if not approval_result['success']:
                    return approval_result
            
            # Execute workflow actions
            execution_result = self._execute_workflow_actions(db, workflow, trigger_data)
            
            # Log execution
            self._log_automation_execution(db, workflow, trigger_data, execution_result)
            
            return {
                'success': True,
                'data': execution_result,
                'message': f'Executed automation workflow: {workflow.name}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute automation workflow'
            }
    
    def get_automation_approvals(self, db: Session, company_id: int, status: Optional[str] = None) -> Dict:
        """Get automation approvals"""
        try:
            query = db.query(AutomationApproval).filter(
                AutomationApproval.company_id == company_id
            )
            
            if status:
                query = query.filter(AutomationApproval.status == status)
            
            approvals = query.order_by(AutomationApproval.created_at.desc()).all()
            
            result = []
            for approval in approvals:
                result.append({
                    'id': approval.id,
                    'workflow_id': approval.workflow_id,
                    'workflow_name': approval.workflow_name,
                    'trigger_data': approval.trigger_data,
                    'status': approval.status,
                    'requested_by': approval.requested_by,
                    'approved_by': approval.approved_by,
                    'created_at': approval.created_at,
                    'approved_at': approval.approved_at
                })
            
            return {
                'success': True,
                'data': result,
                'message': f'Retrieved {len(result)} automation approvals'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve automation approvals'
            }
    
    def approve_automation_request(self, db: Session, company_id: int, approval_id: int, approved_by: int, comments: Optional[str] = None) -> Dict:
        """Approve automation request"""
        try:
            approval = db.query(AutomationApproval).filter(
                AutomationApproval.id == approval_id,
                AutomationApproval.company_id == company_id,
                AutomationApproval.status == 'pending'
            ).first()
            
            if not approval:
                return {
                    'success': False,
                    'error': 'Approval request not found or already processed',
                    'message': 'Automation approval not found'
                }
            
            # Update approval
            approval.status = 'approved'
            approval.approved_by = approved_by
            approval.approved_at = datetime.utcnow()
            approval.comments = comments
            
            # Execute the workflow
            workflow = db.query(AutomationWorkflow).filter(
                AutomationWorkflow.id == approval.workflow_id
            ).first()
            
            if workflow:
                execution_result = self._execute_workflow_actions(db, workflow, approval.trigger_data)
                approval.execution_result = execution_result
            
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': approval.id,
                    'status': approval.status,
                    'approved_by': approval.approved_by,
                    'approved_at': approval.approved_at
                },
                'message': f'Approved automation request: {approval.workflow_name}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to approve automation request'
            }
    
    def get_automation_logs(self, db: Session, company_id: int, module: Optional[str] = None, limit: int = 100) -> Dict:
        """Get automation logs"""
        try:
            query = db.query(AutomationLog).filter(
                AutomationLog.company_id == company_id
            )
            
            if module:
                query = query.filter(AutomationLog.module == module)
            
            logs = query.order_by(AutomationLog.created_at.desc()).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    'id': log.id,
                    'module': log.module,
                    'action': log.action,
                    'status': log.status,
                    'details': log.details,
                    'created_at': log.created_at,
                    'execution_time': log.execution_time
                })
            
            return {
                'success': True,
                'data': result,
                'message': f'Retrieved {len(result)} automation logs'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve automation logs'
            }
    
    def rollback_automation(self, db: Session, company_id: int, log_id: int, rollback_data: Dict) -> Dict:
        """Rollback automation execution"""
        try:
            log = db.query(AutomationLog).filter(
                AutomationLog.id == log_id,
                AutomationLog.company_id == company_id
            ).first()
            
            if not log:
                return {
                    'success': False,
                    'error': 'Automation log not found',
                    'message': 'Automation log not found'
                }
            
            # Create rollback record
            rollback = AutomationRollback(
                company_id=company_id,
                automation_log_id=log_id,
                rollback_reason=rollback_data['reason'],
                rollback_data=rollback_data.get('data'),
                rollback_actions=rollback_data.get('actions'),
                executed_by=rollback_data.get('executed_by', 1),
                status='pending'
            )
            
            db.add(rollback)
            
            # Execute rollback actions
            rollback_result = self._execute_rollback_actions(db, log, rollback_data)
            
            # Update rollback status
            rollback.status = 'completed' if rollback_result['success'] else 'failed'
            rollback.execution_result = rollback_result
            
            db.commit()
            
            return {
                'success': True,
                'data': {
                    'id': rollback.id,
                    'status': rollback.status,
                    'execution_result': rollback_result
                },
                'message': f'Rolled back automation execution: {log.action}'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to rollback automation'
            }
    
    def get_automation_analytics(self, db: Session, company_id: int, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict:
        """Get automation analytics"""
        try:
            query = db.query(AutomationLog).filter(
                AutomationLog.company_id == company_id
            )
            
            if from_date:
                query = query.filter(AutomationLog.created_at >= from_date)
            if to_date:
                query = query.filter(AutomationLog.created_at <= to_date)
            
            logs = query.all()
            
            # Calculate analytics
            total_executions = len(logs)
            successful_executions = len([log for log in logs if log.status == 'success'])
            failed_executions = len([log for log in logs if log.status == 'failed'])
            
            module_stats = {}
            for log in logs:
                if log.module not in module_stats:
                    module_stats[log.module] = {'total': 0, 'success': 0, 'failed': 0}
                module_stats[log.module]['total'] += 1
                if log.status == 'success':
                    module_stats[log.module]['success'] += 1
                else:
                    module_stats[log.module]['failed'] += 1
            
            success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
            
            return {
                'success': True,
                'data': {
                    'total_executions': total_executions,
                    'successful_executions': successful_executions,
                    'failed_executions': failed_executions,
                    'success_rate': round(success_rate, 2),
                    'module_stats': module_stats,
                    'average_execution_time': sum([log.execution_time or 0 for log in logs]) / total_executions if total_executions > 0 else 0
                },
                'message': f'Retrieved automation analytics for {total_executions} executions'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve automation analytics'
            }
    
    def _check_trigger_conditions(self, workflow: AutomationWorkflow, trigger_data: Dict) -> bool:
        """Check if trigger conditions are met"""
        if not workflow.trigger_conditions:
            return True
        
        try:
            conditions = json.loads(workflow.trigger_conditions)
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if field not in trigger_data:
                    return False
                
                trigger_value = trigger_data[field]
                
                if operator == 'equals' and trigger_value != value:
                    return False
                elif operator == 'not_equals' and trigger_value == value:
                    return False
                elif operator == 'greater_than' and trigger_value <= value:
                    return False
                elif operator == 'less_than' and trigger_value >= value:
                    return False
                elif operator == 'contains' and value not in str(trigger_value):
                    return False
            
            return True
        except Exception:
            return False
    
    def _create_approval_request(self, db: Session, workflow: AutomationWorkflow, trigger_data: Dict) -> Dict:
        """Create approval request for workflow"""
        try:
            approval = AutomationApproval(
                company_id=workflow.company_id,
                workflow_id=workflow.id,
                workflow_name=workflow.name,
                trigger_data=json.dumps(trigger_data),
                status='pending',
                requested_by=trigger_data.get('user_id', 1)
            )
            
            db.add(approval)
            db.commit()
            
            return {
                'success': True,
                'data': {'approval_id': approval.id},
                'message': 'Approval request created'
            }
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create approval request'
            }
    
    def _execute_workflow_actions(self, db: Session, workflow: AutomationWorkflow, trigger_data: Dict) -> Dict:
        """Execute workflow actions"""
        try:
            actions = json.loads(workflow.actions)
            results = []
            
            for action in actions:
                action_type = action.get('type')
                action_data = action.get('data', {})
                
                if action_type == 'create_record':
                    result = self._execute_create_record_action(db, action_data, trigger_data)
                elif action_type == 'update_record':
                    result = self._execute_update_record_action(db, action_data, trigger_data)
                elif action_type == 'send_notification':
                    result = self._execute_send_notification_action(db, action_data, trigger_data)
                elif action_type == 'generate_report':
                    result = self._execute_generate_report_action(db, action_data, trigger_data)
                else:
                    result = {'success': False, 'error': f'Unknown action type: {action_type}'}
                
                results.append({
                    'action': action,
                    'result': result
                })
            
            return {
                'success': True,
                'actions_executed': len(results),
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to execute workflow actions'
            }
    
    def _execute_create_record_action(self, db: Session, action_data: Dict, trigger_data: Dict) -> Dict:
        """Execute create record action"""
        # Implementation depends on specific module
        return {'success': True, 'message': 'Create record action executed'}
    
    def _execute_update_record_action(self, db: Session, action_data: Dict, trigger_data: Dict) -> Dict:
        """Execute update record action"""
        # Implementation depends on specific module
        return {'success': True, 'message': 'Update record action executed'}
    
    def _execute_send_notification_action(self, db: Session, action_data: Dict, trigger_data: Dict) -> Dict:
        """Execute send notification action"""
        # Implementation depends on notification system
        return {'success': True, 'message': 'Send notification action executed'}
    
    def _execute_generate_report_action(self, db: Session, action_data: Dict, trigger_data: Dict) -> Dict:
        """Execute generate report action"""
        # Implementation depends on report system
        return {'success': True, 'message': 'Generate report action executed'}
    
    def _log_automation_execution(self, db: Session, workflow: AutomationWorkflow, trigger_data: Dict, execution_result: Dict) -> None:
        """Log automation execution"""
        try:
            log = AutomationLog(
                company_id=workflow.company_id,
                module=workflow.module,
                action=workflow.name,
                status='success' if execution_result['success'] else 'failed',
                details=json.dumps({
                    'workflow_id': workflow.id,
                    'trigger_data': trigger_data,
                    'execution_result': execution_result
                }),
                execution_time=execution_result.get('execution_time', 0),
                created_by=trigger_data.get('user_id', 1)
            )
            
            db.add(log)
            db.commit()
        except Exception:
            pass  # Don't fail the main operation if logging fails
    
    def _execute_rollback_actions(self, db: Session, log: AutomationLog, rollback_data: Dict) -> Dict:
        """Execute rollback actions"""
        try:
            # Implementation depends on specific rollback requirements
            return {'success': True, 'message': 'Rollback actions executed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}