"""
WhatsApp Setup and Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.deps import get_db, get_current_user
from app.services.whatsapp.whatsapp_setup import WhatsAppSetupService
from app.schemas.whatsapp_schema import WhatsAppSetupRequest, WhatsAppSetupResponse

router = APIRouter(prefix="/whatsapp/setup", tags=["WhatsApp Setup"])

# Service instance
setup_service = WhatsAppSetupService()


@router.post("/initialize", response_model=WhatsAppSetupResponse)
async def initialize_whatsapp_templates(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Initialize default WhatsApp templates"""
    try:
        result = setup_service.initialize_whatsapp_templates(
            db=db,
            created_by=current_user.get("user_id", "system")
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing templates: {str(e)}"
        )


@router.post("/configure")
async def setup_whatsapp_integration(
    setup_data: WhatsAppSetupRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Setup WhatsApp integration with credentials"""
    try:
        result = setup_service.setup_whatsapp_integration(
            db=db,
            access_token=setup_data.access_token,
            phone_number_id=setup_data.phone_number_id,
            business_account_id=setup_data.business_account_id,
            webhook_verify_token=setup_data.webhook_verify_token
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting up WhatsApp integration: {str(e)}"
        )


@router.get("/status")
async def get_setup_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp setup status"""
    try:
        result = setup_service.get_setup_status(db=db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting setup status: {str(e)}"
        )


@router.post("/sample-campaign")
async def create_sample_campaign(
    campaign_name: str = "Welcome New Customers",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a sample marketing campaign"""
    try:
        result = setup_service.create_sample_campaign(
            db=db,
            campaign_name=campaign_name,
            created_by=current_user.get("user_id", "system")
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sample campaign: {str(e)}"
        )


@router.get("/templates/preview")
async def preview_templates(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Preview available WhatsApp templates"""
    try:
        from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
        
        template_manager = WhatsAppTemplateManager()
        
        if category:
            templates = template_manager.get_templates_by_category(category)
        else:
            templates = template_manager.get_default_templates()
        
        return {
            "success": True,
            "templates": templates,
            "categories": ["TRANSACTIONAL", "MARKETING", "UTILITY"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing templates: {str(e)}"
        )


@router.get("/templates/{template_name}/preview")
async def preview_template(
    template_name: str,
    sample_variables: Dict[str, Any] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Preview a specific template with sample data"""
    try:
        from app.services.whatsapp.whatsapp_template_management import WhatsAppTemplateManager
        
        template_manager = WhatsAppTemplateManager()
        
        # Get template
        template = template_manager.get_template_by_use_case(template_name)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # Prepare sample variables
        sample_data = sample_variables or {}
        validated_variables = template_manager.validate_template_variables(template, sample_data)
        
        # Create preview
        preview = {
            "template_name": template["name"],
            "category": template["category"],
            "language": template["language"],
            "header": template.get("header_text", ""),
            "body": template["body_text"],
            "footer": template.get("footer_text", ""),
            "button": template.get("button_text", ""),
            "variables": validated_variables,
            "preview_text": template["body_text"].format(**validated_variables)
        }
        
        return {
            "success": True,
            "preview": preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing template: {str(e)}"
        )


@router.get("/documentation")
async def get_whatsapp_documentation(
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp integration documentation"""
    try:
        documentation = {
            "overview": "WhatsApp Business API Integration for POS and Marketing",
            "features": [
                "POS receipt delivery via WhatsApp",
                "Loyalty points notifications",
                "Invoice delivery with PDF attachments",
                "Marketing campaigns",
                "Customer opt-in/opt-out management",
                "Template management and approval workflow"
            ],
            "setup_steps": [
                {
                    "step": 1,
                    "title": "Get WhatsApp Business Account",
                    "description": "Create a WhatsApp Business Account and get verified",
                    "requirements": [
                        "Facebook Business Manager account",
                        "Verified business phone number",
                        "Business verification documents"
                    ]
                },
                {
                    "step": 2,
                    "title": "Get API Credentials",
                    "description": "Obtain access token, phone number ID, and business account ID",
                    "requirements": [
                        "WhatsApp Business API access",
                        "Phone number ID from WhatsApp Business Manager",
                        "Business Account ID"
                    ]
                },
                {
                    "step": 3,
                    "title": "Configure Templates",
                    "description": "Create and submit message templates for approval",
                    "requirements": [
                        "Template content following WhatsApp guidelines",
                        "Proper template categorization",
                        "Variable placeholders in templates"
                    ]
                },
                {
                    "step": 4,
                    "title": "Setup Webhooks",
                    "description": "Configure webhook URL for message status updates",
                    "requirements": [
                        "Public webhook URL",
                        "SSL certificate",
                        "Webhook verification token"
                    ]
                },
                {
                    "step": 5,
                    "title": "Test Integration",
                    "description": "Test template messages and webhook functionality",
                    "requirements": [
                        "Test phone numbers",
                        "Approved templates",
                        "Working webhook endpoint"
                    ]
                }
            ],
            "template_categories": {
                "TRANSACTIONAL": "For receipts, invoices, order confirmations",
                "MARKETING": "For promotions, offers, announcements",
                "UTILITY": "For account updates, notifications, reminders"
            },
            "best_practices": [
                "Always get customer opt-in before sending messages",
                "Use appropriate template categories",
                "Keep messages concise and clear",
                "Include clear call-to-action buttons",
                "Test templates before submitting for approval",
                "Monitor message delivery and engagement rates"
            ],
            "compliance": [
                "Follow WhatsApp Business Policy",
                "Respect customer opt-in/opt-out preferences",
                "Include unsubscribe options in marketing messages",
                "Maintain customer data privacy",
                "Follow local regulations for marketing communications"
            ]
        }
        
        return {
            "success": True,
            "documentation": documentation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting documentation: {str(e)}"
        )