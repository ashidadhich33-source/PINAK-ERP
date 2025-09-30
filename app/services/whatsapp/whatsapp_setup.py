"""
WhatsApp Setup and Initialization Service
Handles initial setup of WhatsApp templates and configuration
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.whatsapp.whatsapp_models import WhatsAppTemplate, WhatsAppTemplateStatus
from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
from app.services.whatsapp.whatsapp_template_service import WhatsAppTemplateService
from app.services.whatsapp.whatsapp_integration_service import WhatsAppIntegrationService

logger = logging.getLogger(__name__)


class WhatsAppSetupService:
    """Service for setting up WhatsApp integration"""
    
    def __init__(self):
        self.template_service = WhatsAppTemplateService()
        self.integration_service = WhatsAppIntegrationService()
        self.template_manager = WhatsAppTemplateManager()
    
    def initialize_whatsapp_templates(self, db: Session, created_by: str = "system") -> Dict[str, Any]:
        """
        Initialize default WhatsApp templates
        
        Args:
            db: Database session
            created_by: User who created the templates
            
        Returns:
            Dict with initialization results
        """
        try:
            results = {
                "success": True,
                "templates_created": 0,
                "templates_skipped": 0,
                "errors": []
            }
            
            # Get default templates
            default_templates = self.template_manager.get_default_templates()
            
            for template_data in default_templates:
                try:
                    # Check if template already exists
                    existing_template = db.query(WhatsAppTemplate).filter(
                        WhatsAppTemplate.name == template_data["name"]
                    ).first()
                    
                    if existing_template:
                        results["templates_skipped"] += 1
                        logger.info(f"Template {template_data['name']} already exists, skipping")
                        continue
                    
                    # Create template
                    result = self.template_service.create_template(
                        db=db,
                        name=template_data["name"],
                        category=template_data["category"],
                        language=template_data["language"],
                        header_text=template_data.get("header_text"),
                        body_text=template_data["body_text"],
                        footer_text=template_data.get("footer_text"),
                        button_text=template_data.get("button_text"),
                        button_url=template_data.get("button_url"),
                        variables=template_data.get("variables", []),
                        created_by=created_by
                    )
                    
                    if result["success"]:
                        results["templates_created"] += 1
                        logger.info(f"Created template: {template_data['name']}")
                    else:
                        results["errors"].append(f"Failed to create {template_data['name']}: {result['error']}")
                        
                except Exception as e:
                    error_msg = f"Error creating template {template_data['name']}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
            
            return results
            
        except Exception as e:
            logger.error(f"Error initializing WhatsApp templates: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "templates_created": 0,
                "templates_skipped": 0,
                "errors": []
            }
    
    def setup_whatsapp_integration(
        self,
        db: Session,
        access_token: str,
        phone_number_id: str,
        business_account_id: str,
        webhook_verify_token: str = "erp_webhook_token"
    ) -> Dict[str, Any]:
        """
        Setup WhatsApp integration with provided credentials
        
        Args:
            db: Database session
            access_token: WhatsApp access token
            phone_number_id: WhatsApp phone number ID
            business_account_id: WhatsApp business account ID
            webhook_verify_token: Webhook verification token
            
        Returns:
            Dict with setup results
        """
        try:
            # Validate credentials
            validation_result = self._validate_whatsapp_credentials(
                access_token, phone_number_id, business_account_id
            )
            
            if not validation_result["success"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Initialize templates
            template_result = self.initialize_whatsapp_templates(db)
            
            if not template_result["success"]:
                return {
                    "success": False,
                    "error": f"Template initialization failed: {template_result['error']}"
                }
            
            return {
                "success": True,
                "message": "WhatsApp integration setup completed successfully",
                "templates_created": template_result["templates_created"],
                "templates_skipped": template_result["templates_skipped"],
                "next_steps": [
                    "1. Submit templates for approval in WhatsApp Business Manager",
                    "2. Configure webhook URL in WhatsApp Business Manager",
                    "3. Test template messages",
                    "4. Set up customer opt-in/opt-out flows"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error setting up WhatsApp integration: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_whatsapp_credentials(
        self,
        access_token: str,
        phone_number_id: str,
        business_account_id: str
    ) -> Dict[str, Any]:
        """
        Validate WhatsApp credentials
        
        Args:
            access_token: WhatsApp access token
            phone_number_id: WhatsApp phone number ID
            business_account_id: WhatsApp business account ID
            
        Returns:
            Dict with validation results
        """
        try:
            # Basic validation
            if not access_token or len(access_token) < 10:
                return {
                    "success": False,
                    "error": "Invalid access token"
                }
            
            if not phone_number_id or len(phone_number_id) < 10:
                return {
                    "success": False,
                    "error": "Invalid phone number ID"
                }
            
            if not business_account_id or len(business_account_id) < 10:
                return {
                    "success": False,
                    "error": "Invalid business account ID"
                }
            
            # TODO: Add actual API validation here
            # For now, just return success if basic format is correct
            return {
                "success": True,
                "message": "Credentials validated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Credential validation error: {str(e)}"
            }
    
    def get_setup_status(self, db: Session) -> Dict[str, Any]:
        """
        Get WhatsApp setup status
        
        Args:
            db: Database session
            
        Returns:
            Dict with setup status
        """
        try:
            # Check if templates exist
            template_count = db.query(WhatsAppTemplate).count()
            
            # Check template statuses
            approved_templates = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.status == WhatsAppTemplateStatus.APPROVED
            ).count()
            
            pending_templates = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.status == WhatsAppTemplateStatus.PENDING_APPROVAL
            ).count()
            
            draft_templates = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.status == WhatsAppTemplateStatus.DRAFT
            ).count()
            
            return {
                "success": True,
                "setup_complete": template_count > 0,
                "template_stats": {
                    "total_templates": template_count,
                    "approved_templates": approved_templates,
                    "pending_templates": pending_templates,
                    "draft_templates": draft_templates
                },
                "recommendations": self._get_setup_recommendations(
                    template_count, approved_templates, pending_templates
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting setup status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_setup_recommendations(
        self,
        total_templates: int,
        approved_templates: int,
        pending_templates: int
    ) -> List[str]:
        """Get setup recommendations based on current status"""
        recommendations = []
        
        if total_templates == 0:
            recommendations.append("Initialize WhatsApp templates")
        elif approved_templates == 0 and pending_templates == 0:
            recommendations.append("Submit templates for approval")
        elif approved_templates == 0:
            recommendations.append("Wait for template approval or check approval status")
        else:
            recommendations.append("WhatsApp integration is ready for use")
            recommendations.append("Test template messages with customers")
            recommendations.append("Set up customer opt-in flows")
        
        return recommendations
    
    def create_sample_campaign(
        self,
        db: Session,
        campaign_name: str = "Welcome New Customers",
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a sample marketing campaign
        
        Args:
            db: Database session
            campaign_name: Name of the campaign
            created_by: User who created the campaign
            
        Returns:
            Dict with campaign creation results
        """
        try:
            from app.services.whatsapp.whatsapp_campaign_service import WhatsAppCampaignService
            from app.models.whatsapp.whatsapp_models import WhatsAppTemplate
            
            campaign_service = WhatsAppCampaignService()
            
            # Get welcome template
            welcome_template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.name == "welcome_new_customer"
            ).first()
            
            if not welcome_template:
                return {
                    "success": False,
                    "error": "Welcome template not found. Please initialize templates first."
                }
            
            # Create campaign
            result = campaign_service.create_campaign(
                db=db,
                name=campaign_name,
                description="Welcome new customers with special offers",
                template_id=welcome_template.id,
                target_audience={
                    "customer_segments": ["new_customers"],
                    "loyalty_tiers": [],
                    "last_purchase_days": None
                },
                variables={
                    "store_name": "Our Store",
                    "shop_url": "https://yourstore.com"
                },
                created_by=created_by
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating sample campaign: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }