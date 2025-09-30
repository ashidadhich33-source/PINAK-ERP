"""
WhatsApp Campaign Management Service
Handles marketing campaigns and bulk messaging
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.whatsapp import WhatsAppCampaign, WhatsAppCustomer, WhatsAppTemplate
from app.models.whatsapp.whatsapp_models import WhatsAppCampaignStatus
from app.services.whatsapp.whatsapp_service import WhatsAppService
from app.services.whatsapp.whatsapp_template_service import WhatsAppTemplateService

logger = logging.getLogger(__name__)


class WhatsAppCampaignService:
    """Service for managing WhatsApp marketing campaigns"""
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.template_service = WhatsAppTemplateService()
    
    def create_campaign(
        self,
        db: Session,
        name: str,
        description: str,
        template_id: int,
        target_audience: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a new WhatsApp marketing campaign
        
        Args:
            db: Database session
            name: Campaign name
            description: Campaign description
            template_id: Template ID to use
            target_audience: Target audience criteria
            variables: Campaign variables
            scheduled_at: When to start the campaign
            created_by: Creator user ID
            
        Returns:
            Dict with campaign creation result
        """
        try:
            # Validate template
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.id == template_id
            ).first()
            
            if not template:
                return {
                    "success": False,
                    "error": "Template not found"
                }
            
            if template.status.value != "approved":
                return {
                    "success": False,
                    "error": "Template is not approved"
                }
            
            if template.category != "MARKETING":
                return {
                    "success": False,
                    "error": "Template is not a marketing template"
                }
            
            # Create campaign
            campaign = WhatsAppCampaign(
                name=name,
                description=description,
                template_id=template_id,
                target_audience=target_audience,
                variables=variables or {},
                scheduled_at=scheduled_at,
                status=WhatsAppCampaignStatus.DRAFT,
                created_by=created_by
            )
            
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            
            return {
                "success": True,
                "campaign_id": campaign.id,
                "campaign": campaign
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_campaign(
        self,
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        Start a WhatsApp campaign
        
        Args:
            db: Database session
            campaign_id: Campaign ID to start
            
        Returns:
            Dict with campaign start result
        """
        try:
            campaign = db.query(WhatsAppCampaign).filter(
                WhatsAppCampaign.id == campaign_id
            ).first()
            
            if not campaign:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            if campaign.status != WhatsAppCampaignStatus.DRAFT:
                return {
                    "success": False,
                    "error": "Campaign is not in draft status"
                }
            
            # Get target customers
            target_customers = self._get_target_customers(db, campaign.target_audience)
            
            if not target_customers:
                return {
                    "success": False,
                    "error": "No target customers found"
                }
            
            # Update campaign status
            campaign.status = WhatsAppCampaignStatus.RUNNING
            campaign.started_at = datetime.utcnow()
            campaign.total_recipients = len(target_customers)
            
            db.commit()
            
            # Send messages to target customers
            self._send_campaign_messages(db, campaign, target_customers)
            
            return {
                "success": True,
                "message": f"Campaign started with {len(target_customers)} recipients"
            }
            
        except Exception as e:
            logger.error(f"Error starting campaign: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def pause_campaign(
        self,
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        Pause a running campaign
        
        Args:
            db: Database session
            campaign_id: Campaign ID to pause
            
        Returns:
            Dict with campaign pause result
        """
        try:
            campaign = db.query(WhatsAppCampaign).filter(
                WhatsAppCampaign.id == campaign_id
            ).first()
            
            if not campaign:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            if campaign.status != WhatsAppCampaignStatus.RUNNING:
                return {
                    "success": False,
                    "error": "Campaign is not running"
                }
            
            campaign.status = WhatsAppCampaignStatus.PAUSED
            db.commit()
            
            return {
                "success": True,
                "message": "Campaign paused successfully"
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def resume_campaign(
        self,
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        Resume a paused campaign
        
        Args:
            db: Database session
            campaign_id: Campaign ID to resume
            
        Returns:
            Dict with campaign resume result
        """
        try:
            campaign = db.query(WhatsAppCampaign).filter(
                WhatsAppCampaign.id == campaign_id
            ).first()
            
            if not campaign:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            if campaign.status != WhatsAppCampaignStatus.PAUSED:
                return {
                    "success": False,
                    "error": "Campaign is not paused"
                }
            
            campaign.status = WhatsAppCampaignStatus.RUNNING
            db.commit()
            
            return {
                "success": True,
                "message": "Campaign resumed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {str(e)}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_campaigns(
        self,
        db: Session,
        status: Optional[WhatsAppCampaignStatus] = None,
        created_by: Optional[str] = None
    ) -> List[WhatsAppCampaign]:
        """
        Get campaigns with optional filters
        
        Args:
            db: Database session
            status: Filter by campaign status
            created_by: Filter by creator
            
        Returns:
            List of campaigns
        """
        try:
            query = db.query(WhatsAppCampaign)
            
            if status:
                query = query.filter(WhatsAppCampaign.status == status)
            if created_by:
                query = query.filter(WhatsAppCampaign.created_by == created_by)
            
            return query.order_by(WhatsAppCampaign.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error getting campaigns: {str(e)}")
            return []
    
    def get_campaign_statistics(
        self,
        db: Session,
        campaign_id: int
    ) -> Dict[str, Any]:
        """
        Get campaign statistics
        
        Args:
            db: Database session
            campaign_id: Campaign ID
            
        Returns:
            Dict with campaign statistics
        """
        try:
            campaign = db.query(WhatsAppCampaign).filter(
                WhatsAppCampaign.id == campaign_id
            ).first()
            
            if not campaign:
                return {
                    "success": False,
                    "error": "Campaign not found"
                }
            
            # Calculate delivery rate
            delivery_rate = 0
            if campaign.messages_sent > 0:
                delivery_rate = (campaign.messages_delivered / campaign.messages_sent) * 100
            
            # Calculate read rate
            read_rate = 0
            if campaign.messages_delivered > 0:
                read_rate = (campaign.messages_read / campaign.messages_delivered) * 100
            
            return {
                "success": True,
                "statistics": {
                    "total_recipients": campaign.total_recipients,
                    "messages_sent": campaign.messages_sent,
                    "messages_delivered": campaign.messages_delivered,
                    "messages_read": campaign.messages_read,
                    "messages_failed": campaign.messages_failed,
                    "delivery_rate": round(delivery_rate, 2),
                    "read_rate": round(read_rate, 2),
                    "status": campaign.status.value,
                    "started_at": campaign.started_at.isoformat() if campaign.started_at else None,
                    "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign statistics: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_target_customers(
        self,
        db: Session,
        target_audience: Dict[str, Any]
    ) -> List[WhatsAppCustomer]:
        """
        Get target customers based on audience criteria
        
        Args:
            db: Database session
            target_audience: Target audience criteria
            
        Returns:
            List of target customers
        """
        try:
            query = db.query(WhatsAppCustomer).filter(
                WhatsAppCustomer.marketing_opt_in == True
            )
            
            # Apply filters based on target audience criteria
            if "customer_segments" in target_audience:
                # Filter by customer segments (loyalty tiers, etc.)
                segments = target_audience["customer_segments"]
                if segments:
                    # This would need to be implemented based on your customer segmentation logic
                    pass
            
            if "loyalty_tiers" in target_audience:
                # Filter by loyalty tiers
                tiers = target_audience["loyalty_tiers"]
                if tiers:
                    # This would need to be implemented based on your loyalty system
                    pass
            
            if "last_purchase_days" in target_audience:
                # Filter by last purchase date
                days = target_audience["last_purchase_days"]
                if days:
                    cutoff_date = datetime.utcnow() - timedelta(days=days)
                    # This would need to be implemented based on your purchase history
                    pass
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting target customers: {str(e)}")
            return []
    
    def _send_campaign_messages(
        self,
        db: Session,
        campaign: WhatsAppCampaign,
        target_customers: List[WhatsAppCustomer]
    ):
        """
        Send campaign messages to target customers
        
        Args:
            db: Database session
            campaign: Campaign to send
            target_customers: List of target customers
        """
        try:
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.id == campaign.template_id
            ).first()
            
            if not template:
                logger.error(f"Template not found for campaign {campaign.id}")
                return
            
            # Send messages to each target customer
            for customer in target_customers:
                try:
                    # Prepare personalized variables
                    variables = self._prepare_campaign_variables(
                        campaign.variables,
                        customer
                    )
                    
                    # Send template message
                    result = self.whatsapp_service.send_template_message(
                        to=customer.phone_number,
                        template_name=template.whatsapp_template_name,
                        language_code=template.language,
                        components=self._build_campaign_components(variables),
                        db=db
                    )
                    
                    # Update campaign statistics
                    if result["success"]:
                        campaign.messages_sent += 1
                    else:
                        campaign.messages_failed += 1
                    
                    # Log message
                    self._log_campaign_message(
                        db, campaign.id, customer.id, result
                    )
                    
                except Exception as e:
                    logger.error(f"Error sending message to customer {customer.id}: {str(e)}")
                    campaign.messages_failed += 1
            
            # Update campaign status if all messages sent
            if campaign.messages_sent + campaign.messages_failed >= len(target_customers):
                campaign.status = WhatsAppCampaignStatus.COMPLETED
                campaign.completed_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending campaign messages: {str(e)}")
            db.rollback()
    
    def _prepare_campaign_variables(
        self,
        campaign_variables: Dict[str, Any],
        customer: WhatsAppCustomer
    ) -> Dict[str, Any]:
        """
        Prepare personalized variables for campaign message
        
        Args:
            campaign_variables: Campaign-level variables
            customer: Target customer
            
        Returns:
            Dict with personalized variables
        """
        variables = campaign_variables.copy()
        
        # Add customer-specific variables
        if customer.customer:
            variables["customer_name"] = customer.customer.name or "Valued Customer"
            variables["customer_phone"] = customer.phone_number
        
        # Add timestamp
        variables["current_date"] = datetime.utcnow().strftime("%Y-%m-%d")
        
        return variables
    
    def _build_campaign_components(self, variables: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build template components for campaign messages"""
        components = []
        
        # Add body component with variables
        if variables:
            body_variables = []
            for key, value in variables.items():
                body_variables.append({"type": "text", "text": str(value)})
            
            if body_variables:
                components.append({
                    "type": "body",
                    "parameters": body_variables
                })
        
        return components
    
    def _log_campaign_message(
        self,
        db: Session,
        campaign_id: int,
        customer_id: int,
        result: Dict[str, Any]
    ):
        """Log campaign message"""
        try:
            from app.models.whatsapp.whatsapp_models import WhatsAppMessage, WhatsAppMessageStatus
            
            message = WhatsAppMessage(
                template_id=None,  # Will be set based on campaign template
                customer_id=customer_id,
                phone_number="",  # Will be set from customer
                message_type="template",
                content=json.dumps(result),
                context_type="marketing_campaign",
                context_id=campaign_id,
                status=WhatsAppMessageStatus.SENT if result["success"] else WhatsAppMessageStatus.FAILED,
                sent_at=datetime.utcnow() if result["success"] else None,
                error_message=result.get("error") if not result["success"] else None
            )
            
            db.add(message)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging campaign message: {str(e)}")
            db.rollback()