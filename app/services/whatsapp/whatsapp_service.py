"""
WhatsApp Business API Service
Handles all WhatsApp Business API interactions
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.whatsapp import WhatsAppMessage, WhatsAppTemplate, WhatsAppCustomer
from app.models.whatsapp.whatsapp_models import WhatsAppMessageStatus
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Core WhatsApp Business API service"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for WhatsApp API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def send_template_message(
        self, 
        to: str, 
        template_name: str, 
        language_code: str = "en",
        components: Optional[List[Dict]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp Business API
        
        Args:
            to: Recipient phone number
            template_name: WhatsApp template name
            language_code: Template language code
            components: Template components with variables
            db: Database session
            
        Returns:
            Dict with message ID and status
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id")
            
            # Log message in database if session provided
            if db:
                self._log_message(
                    db=db,
                    template_name=template_name,
                    phone_number=to,
                    whatsapp_message_id=message_id,
                    content=json.dumps(payload),
                    status=WhatsAppMessageStatus.SENT
                )
            
            return {
                "success": True,
                "message_id": message_id,
                "status": "sent"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            if db:
                self._log_message(
                    db=db,
                    template_name=template_name,
                    phone_number=to,
                    content=json.dumps(payload),
                    status=WhatsAppMessageStatus.FAILED,
                    error_message=str(e)
                )
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def send_text_message(
        self, 
        to: str, 
        text: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a simple text message via WhatsApp Business API
        
        Args:
            to: Recipient phone number
            text: Message text
            db: Database session
            
        Returns:
            Dict with message ID and status
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": text
                }
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id")
            
            # Log message in database if session provided
            if db:
                self._log_message(
                    db=db,
                    message_type="text",
                    phone_number=to,
                    whatsapp_message_id=message_id,
                    content=text,
                    status=WhatsAppMessageStatus.SENT
                )
            
            return {
                "success": True,
                "message_id": message_id,
                "status": "sent"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            if db:
                self._log_message(
                    db=db,
                    message_type="text",
                    phone_number=to,
                    content=text,
                    status=WhatsAppMessageStatus.FAILED,
                    error_message=str(e)
                )
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def send_media_message(
        self, 
        to: str, 
        media_type: str, 
        media_url: str,
        caption: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Send a media message via WhatsApp Business API
        
        Args:
            to: Recipient phone number
            media_type: Type of media (image, document, video, audio)
            media_url: URL of the media file
            caption: Optional caption for the media
            db: Database session
            
        Returns:
            Dict with message ID and status
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": media_type,
                media_type: {
                    "link": media_url
                }
            }
            
            if caption and media_type in ["image", "video", "document"]:
                payload[media_type]["caption"] = caption
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id")
            
            # Log message in database if session provided
            if db:
                self._log_message(
                    db=db,
                    message_type=media_type,
                    phone_number=to,
                    whatsapp_message_id=message_id,
                    content=caption or "",
                    media_url=media_url,
                    media_type=media_type,
                    status=WhatsAppMessageStatus.SENT
                )
            
            return {
                "success": True,
                "message_id": message_id,
                "status": "sent"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API error: {str(e)}")
            if db:
                self._log_message(
                    db=db,
                    message_type=media_type,
                    phone_number=to,
                    content=caption or "",
                    media_url=media_url,
                    media_type=media_type,
                    status=WhatsAppMessageStatus.FAILED,
                    error_message=str(e)
                )
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a WhatsApp message
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            Dict with message status
        """
        try:
            url = f"{self.base_url}/{message_id}"
            
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting message status: {str(e)}")
            return {"error": str(e)}
    
    def _log_message(
        self,
        db: Session,
        template_name: Optional[str] = None,
        message_type: str = "template",
        phone_number: str = "",
        whatsapp_message_id: Optional[str] = None,
        content: str = "",
        media_url: Optional[str] = None,
        media_type: Optional[str] = None,
        status: WhatsAppMessageStatus = WhatsAppMessageStatus.PENDING,
        error_message: Optional[str] = None,
        context_type: Optional[str] = None,
        context_id: Optional[int] = None
    ):
        """Log message to database"""
        try:
            message = WhatsAppMessage(
                template_id=None,  # Will be set if template_name is provided
                phone_number=phone_number,
                message_type=message_type,
                content=content,
                media_url=media_url,
                media_type=media_type,
                whatsapp_message_id=whatsapp_message_id,
                status=status,
                error_message=error_message,
                context_type=context_type,
                context_id=context_id,
                sent_at=datetime.utcnow() if status == WhatsAppMessageStatus.SENT else None
            )
            
            db.add(message)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging message: {str(e)}")
            db.rollback()
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify WhatsApp webhook
        
        Args:
            mode: Verification mode
            token: Verification token
            challenge: Challenge string
            
        Returns:
            Challenge string if verification successful
        """
        if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            return challenge
        return None
    
    def process_webhook(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Process incoming WhatsApp webhook data
        
        Args:
            data: Webhook payload
            db: Database session
            
        Returns:
            Processing result
        """
        try:
            # Extract message data from webhook
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            # Process message status updates
            if "statuses" in value:
                for status in value["statuses"]:
                    self._update_message_status(db, status)
            
            # Process incoming messages
            if "messages" in value:
                for message in value["messages"]:
                    self._process_incoming_message(db, message)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _update_message_status(self, db: Session, status_data: Dict[str, Any]):
        """Update message status in database"""
        try:
            message_id = status_data.get("id")
            status = status_data.get("status")
            timestamp = status_data.get("timestamp")
            
            if message_id:
                message = db.query(WhatsAppMessage).filter(
                    WhatsAppMessage.whatsapp_message_id == message_id
                ).first()
                
                if message:
                    if status == "delivered":
                        message.status = WhatsAppMessageStatus.DELIVERED
                        message.delivered_at = datetime.fromtimestamp(int(timestamp))
                    elif status == "read":
                        message.status = WhatsAppMessageStatus.READ
                        message.read_at = datetime.fromtimestamp(int(timestamp))
                    elif status == "failed":
                        message.status = WhatsAppMessageStatus.FAILED
                    
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Error updating message status: {str(e)}")
            db.rollback()
    
    def _process_incoming_message(self, db: Session, message_data: Dict[str, Any]):
        """Process incoming WhatsApp message"""
        try:
            # Handle incoming messages (opt-in/opt-out, customer responses)
            # This can be extended based on your business needs
            pass
            
        except Exception as e:
            logger.error(f"Error processing incoming message: {str(e)}")