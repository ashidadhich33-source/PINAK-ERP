# backend/app/api/endpoints/whatsapp_messages.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...models.whatsapp.whatsapp_models import WhatsAppMessage
from ...models.core.user import User
from ...core.security import get_current_user, require_permission

router = APIRouter()

# Pydantic schemas
class WhatsAppMessageCreate(BaseModel):
    campaign_id: Optional[int] = None
    contact_id: int
    message_type: str
    message_content: str
    company_id: int

class WhatsAppMessageResponse(BaseModel):
    id: int
    campaign_id: Optional[int]
    contact_id: int
    message_type: str
    message_content: str
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True

@router.post("/messages", response_model=WhatsAppMessageResponse)
async def create_whatsapp_message(
    message_data: WhatsAppMessageCreate,
    current_user: User = Depends(require_permission("whatsapp.create")),
    db: Session = Depends(get_db)
):
    """Create a new WhatsApp message"""
    
    # Create WhatsApp message
    whatsapp_message = WhatsAppMessage(
        campaign_id=message_data.campaign_id,
        contact_id=message_data.contact_id,
        message_type=message_data.message_type,
        message_content=message_data.message_content,
        company_id=message_data.company_id,
        created_by=current_user.id
    )
    
    db.add(whatsapp_message)
    db.commit()
    db.refresh(whatsapp_message)
    
    return whatsapp_message

@router.get("/messages", response_model=List[WhatsAppMessageResponse])
async def get_whatsapp_messages(
    company_id: int,
    campaign_id: Optional[int] = None,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get WhatsApp messages for a company"""
    
    query = db.query(WhatsAppMessage).filter(WhatsAppMessage.company_id == company_id)
    
    if campaign_id:
        query = query.filter(WhatsAppMessage.campaign_id == campaign_id)
    
    messages = query.all()
    return messages

@router.get("/messages/{message_id}", response_model=WhatsAppMessageResponse)
async def get_whatsapp_message(
    message_id: int,
    current_user: User = Depends(require_permission("whatsapp.view")),
    db: Session = Depends(get_db)
):
    """Get a specific WhatsApp message"""
    
    message = db.query(WhatsAppMessage).filter(WhatsAppMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="WhatsApp message not found")
    
    return message

@router.put("/messages/{message_id}/resend")
async def resend_whatsapp_message(
    message_id: int,
    current_user: User = Depends(require_permission("whatsapp.update")),
    db: Session = Depends(get_db)
):
    """Resend a WhatsApp message"""
    
    message = db.query(WhatsAppMessage).filter(WhatsAppMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="WhatsApp message not found")
    
    # Reset message status for resending
    message.status = "pending"
    message.sent_at = None
    message.delivered_at = None
    message.read_at = None
    message.error_message = None
    message.updated_by = current_user.id
    
    db.commit()
    
    return {"message": "WhatsApp message queued for resending"}