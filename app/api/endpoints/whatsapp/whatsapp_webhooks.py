"""
WhatsApp Webhook API Endpoints
Handles incoming webhooks from WhatsApp Business API
"""
from fastapi import APIRouter, Request, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.deps import get_db
from app.services.whatsapp.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/whatsapp/webhooks", tags=["WhatsApp Webhooks"])

# Service instance
whatsapp_service = WhatsAppService()


@router.get("/verify")
async def verify_webhook(
    mode: str = Query(..., description="Verification mode"),
    token: str = Query(..., description="Verification token"),
    challenge: str = Query(..., description="Challenge string")
):
    """Verify WhatsApp webhook"""
    try:
        result = whatsapp_service.verify_webhook(mode, token, challenge)
        
        if result:
            return int(result)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Webhook verification failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying webhook: {str(e)}"
        )


@router.post("/")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle incoming WhatsApp webhook"""
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Process webhook
        result = whatsapp_service.process_webhook(webhook_data, db)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Webhook processing failed")
            )
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )


@router.post("/test")
async def test_webhook(
    test_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Test webhook processing with sample data"""
    try:
        # Sample webhook data for testing
        sample_data = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456789",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "1234567890",
                                    "phone_number_id": "123456789"
                                },
                                "statuses": [
                                    {
                                        "id": "wamid.test123",
                                        "status": "delivered",
                                        "timestamp": "1234567890",
                                        "recipient_id": "1234567890"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        # Process test webhook
        result = whatsapp_service.process_webhook(sample_data, db)
        
        return {
            "success": True,
            "message": "Test webhook processed successfully",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing test webhook: {str(e)}"
        )