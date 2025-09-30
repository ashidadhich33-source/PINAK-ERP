"""
WhatsApp Template Management Service
Handles template creation, approval, and submission to WhatsApp Business Manager
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.whatsapp import WhatsAppTemplate, WhatsAppTemplateComponent
from app.models.whatsapp.whatsapp_models import WhatsAppTemplateStatus
from app.services.whatsapp.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class WhatsAppTemplateService:
    """Service for managing WhatsApp templates"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
    
    def create_template(
        self,
        db: Session,
        name: str,
        category: str,
        language: str,
        header_text: Optional[str] = None,
        body_text: str = "",
        footer_text: Optional[str] = None,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        variables: Optional[Dict] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a new WhatsApp template
        
        Args:
            db: Database session
            name: Template name
            category: Template category (TRANSACTIONAL, MARKETING, UTILITY)
            language: Template language code
            header_text: Header text content
            body_text: Body text content
            footer_text: Footer text content
            button_text: Button text
            button_url: Button URL
            variables: Template variables
            created_by: Creator user ID
            
        Returns:
            Dict with template creation result
        """
        try:
            # Check if template name already exists
            existing_template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.name == name
            ).first()
            
            if existing_template:
                return {
                    "success": False,
                    "error": "Template name already exists"
                }
            
            # Create template
            template = WhatsAppTemplate(
                name=name,
                category=category,
                language=language,
                header_text=header_text,
                body_text=body_text,
                footer_text=footer_text,
                button_text=button_text,
                button_url=button_url,
                variables=variables or {},
                status=WhatsAppTemplateStatus.DRAFT,
                created_by=created_by
            )
            
            db.add(template)
            db.commit()
            db.refresh(template)
            
            # Create template components
            self._create_template_components(db, template)
            
            return {
                "success": True,
                "template_id": template.id,
                "template": template
            }
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def submit_template_for_approval(
        self,
        db: Session,
        template_id: int,
        submitted_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Submit template to WhatsApp Business Manager for approval
        
        Args:
            db: Database session
            template_id: Template ID to submit
            submitted_by: User who submitted the template
            
        Returns:
            Dict with submission result
        """
        try:
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.id == template_id
            ).first()
            
            if not template:
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            if template.status != WhatsAppTemplateStatus.DRAFT:
                return {
                    "success": False,
                    "error": "Template is not in draft status"
                }
            
            # Submit to WhatsApp Business Manager
            submission_result = self._submit_to_whatsapp_business_manager(template)
            
            if submission_result["success"]:
                template.status = WhatsAppTemplateStatus.PENDING_APPROVAL
                template.whatsapp_template_id = submission_result.get("template_id")
                template.whatsapp_template_name = submission_result.get("template_name")
                template.updated_at = datetime.utcnow()
                
                db.commit()
                
                return {
                    "success": True,
                    "message": "Template submitted for approval",
                    "whatsapp_template_id": template.whatsapp_template_id
                }
            else:
                return {
                    "success": False,
                    "error": submission_result.get("error", "Failed to submit template")
                }
                
        except Exception as e:
            logger.error(f"Error submitting template: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def approve_template(
        self,
        db: Session,
        template_id: int,
        approved_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Mark template as approved (called when approved in WhatsApp Business Manager)
        
        Args:
            db: Database session
            template_id: Template ID to approve
            approved_by: User who approved the template
            
        Returns:
            Dict with approval result
        """
        try:
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.id == template_id
            ).first()
            
            if not template:
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            template.status = WhatsAppTemplateStatus.APPROVED
            template.approved_at = datetime.utcnow()
            template.approved_by = approved_by
            template.updated_at = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "message": "Template approved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error approving template: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_templates(
        self,
        db: Session,
        status: Optional[WhatsAppTemplateStatus] = None,
        category: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[WhatsAppTemplate]:
        """
        Get templates with optional filters
        
        Args:
            db: Database session
            status: Filter by template status
            category: Filter by template category
            language: Filter by template language
            
        Returns:
            List of templates
        """
        try:
            query = db.query(WhatsAppTemplate)
            
            if status:
                query = query.filter(WhatsAppTemplate.status == status)
            if category:
                query = query.filter(WhatsAppTemplate.category == category)
            if language:
                query = query.filter(WhatsAppTemplate.language == language)
            
            return query.order_by(WhatsAppTemplate.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting templates: {str(e)}")
            return []
    
    def get_template_by_name(
        self,
        db: Session,
        name: str
    ) -> Optional[WhatsAppTemplate]:
        """
        Get template by name
        
        Args:
            db: Database session
            name: Template name
            
        Returns:
            Template if found, None otherwise
        """
        try:
            return db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.name == name
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting template by name: {str(e)}")
            return None
    
    def update_template_usage(
        self,
        db: Session,
        template_id: int
    ) -> Dict[str, Any]:
        """
        Update template usage statistics
        
        Args:
            db: Database session
            template_id: Template ID
            
        Returns:
            Dict with update result
        """
        try:
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.id == template_id
            ).first()
            
            if template:
                template.usage_count += 1
                template.last_used = datetime.utcnow()
                template.updated_at = datetime.utcnow()
                
                db.commit()
                
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": "Template not found"
                }
                
        except Exception as e:
            logger.error(f"Error updating template usage: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_template_components(self, db: Session, template: WhatsAppTemplate):
        """Create template components"""
        try:
            components = []
            position = 1
            
            # Header component
            if template.header_text:
                components.append(WhatsAppTemplateComponent(
                    template_id=template.id,
                    component_type="header",
                    position=position,
                    text=template.header_text,
                    variable_count=template.header_text.count("{{") if template.header_text else 0
                ))
                position += 1
            
            # Body component
            if template.body_text:
                components.append(WhatsAppTemplateComponent(
                    template_id=template.id,
                    component_type="body",
                    position=position,
                    text=template.body_text,
                    variable_count=template.body_text.count("{{") if template.body_text else 0
                ))
                position += 1
            
            # Footer component
            if template.footer_text:
                components.append(WhatsAppTemplateComponent(
                    template_id=template.id,
                    component_type="footer",
                    position=position,
                    text=template.footer_text,
                    variable_count=template.footer_text.count("{{") if template.footer_text else 0
                ))
                position += 1
            
            # Button component
            if template.button_text and template.button_url:
                components.append(WhatsAppTemplateComponent(
                    template_id=template.id,
                    component_type="button",
                    position=position,
                    button_text=template.button_text,
                    button_url=template.button_url,
                    button_type="url"
                ))
            
            # Add components to database
            for component in components:
                db.add(component)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error creating template components: {str(e)}")
            db.rollback()
    
    def _submit_to_whatsapp_business_manager(self, template: WhatsAppTemplate) -> Dict[str, Any]:
        """
        Submit template to WhatsApp Business Manager API
        
        Args:
            template: Template to submit
            
        Returns:
            Dict with submission result
        """
        try:
            # This would integrate with WhatsApp Business Manager API
            # For now, we'll simulate the submission
            
            # In a real implementation, you would:
            # 1. Format the template according to WhatsApp's requirements
            # 2. Submit to WhatsApp Business Manager API
            # 3. Handle the response
            
            # Simulate successful submission
            return {
                "success": True,
                "template_id": f"template_{template.id}_{int(datetime.utcnow().timestamp())}",
                "template_name": template.name
            }
            
        except Exception as e:
            logger.error(f"Error submitting to WhatsApp Business Manager: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }