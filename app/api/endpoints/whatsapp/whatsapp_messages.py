"""
WhatsApp Message Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user
from app.models.whatsapp.whatsapp_models import WhatsAppMessage, WhatsAppMessageStatus
from app.services.whatsapp.whatsapp_service import WhatsAppService
from app.schemas.whatsapp_schema import (
    WhatsAppMessageSend,
    WhatsAppMessageResponse,
    WhatsAppMessageStatusUpdate
)

router = APIRouter(prefix="/whatsapp/messages", tags=["WhatsApp Messages"])

# Service instance
whatsapp_service = WhatsAppService()


@router.post("/send", response_model=dict)
async def send_message(
    message_data: WhatsAppMessageSend,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send a WhatsApp message"""
    try:
        if message_data.message_type == "template":
            result = whatsapp_service.send_template_message(
                to=message_data.to,
                template_name=message_data.template_name,
                language_code=message_data.language_code or "en",
                components=message_data.components,
                db=db
            )
        elif message_data.message_type == "text":
            result = whatsapp_service.send_text_message(
                to=message_data.to,
                text=message_data.content,
                db=db
            )
        elif message_data.message_type in ["image", "document", "video", "audio"]:
            result = whatsapp_service.send_media_message(
                to=message_data.to,
                media_type=message_data.message_type,
                media_url=message_data.media_url,
                caption=message_data.content,
                db=db
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid message type"
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
            detail=f"Error sending message: {str(e)}"
        )


@router.get("/", response_model=List[WhatsAppMessageResponse])
async def get_messages(
    customer_id: Optional[int] = None,
    status: Optional[WhatsAppMessageStatus] = None,
    context_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WhatsApp messages with optional filters"""
    try:
        query = db.query(WhatsAppMessage)
        
        if customer_id:
            query = query.filter(WhatsAppMessage.customer_id == customer_id)
        if status:
            query = query.filter(WhatsAppMessage.status == status)
        if context_type:
            query = query.filter(WhatsAppMessage.context_type == context_type)
        
        messages = query.order_by(WhatsAppMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        return messages
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting messages: {str(e)}"
        )


@router.get("/{message_id}", response_model=WhatsAppMessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific WhatsApp message"""
    try:
        message = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.id == message_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        return message
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting message: {str(e)}"
        )


@router.get("/{message_id}/status")
async def get_message_status(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get message status from WhatsApp API"""
    try:
        message = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.id == message_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        if not message.whatsapp_message_id:
            return {
                "message_id": message.id,
                "status": message.status.value,
                "error": "No WhatsApp message ID found"
            }
        
        # Get status from WhatsApp API
        status_result = whatsapp_service.get_message_status(message.whatsapp_message_id)
        
        return {
            "message_id": message.id,
            "whatsapp_message_id": message.whatsapp_message_id,
            "local_status": message.status.value,
            "whatsapp_status": status_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting message status: {str(e)}"
        )


@router.put("/{message_id}/status")
async def update_message_status(
    message_id: int,
    status_data: WhatsAppMessageStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update message status"""
    try:
        message = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.id == message_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Update message status
        message.status = status_data.status
        
        if status_data.status == WhatsAppMessageStatus.DELIVERED:
            message.delivered_at = status_data.delivered_at
        elif status_data.status == WhatsAppMessageStatus.READ:
            message.read_at = status_data.read_at
        elif status_data.status == WhatsAppMessageStatus.FAILED:
            message.error_message = status_data.error_message
        
        db.commit()
        
        return {
            "success": True,
            "message": "Message status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message status: {str(e)}"
        )


@router.get("/statistics/overview")
async def get_message_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get message statistics overview"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get message counts by status
        status_counts = db.query(
            WhatsAppMessage.status,
            func.count(WhatsAppMessage.id).label('count')
        ).filter(
            WhatsAppMessage.created_at >= start_date
        ).group_by(WhatsAppMessage.status).all()
        
        # Get messages by context type
        context_counts = db.query(
            WhatsAppMessage.context_type,
            func.count(WhatsAppMessage.id).label('count')
        ).filter(
            WhatsAppMessage.created_at >= start_date
        ).group_by(WhatsAppMessage.context_type).all()
        
        # Get daily message counts
        daily_counts = db.query(
            func.date(WhatsAppMessage.created_at).label('date'),
            func.count(WhatsAppMessage.id).label('count')
        ).filter(
            WhatsAppMessage.created_at >= start_date
        ).group_by(func.date(WhatsAppMessage.created_at)).all()
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status_breakdown": {
                status.value: count for status, count in status_counts
            },
            "context_breakdown": {
                context_type or "unknown": count for context_type, count in context_counts
            },
            "daily_counts": [
                {"date": date.isoformat(), "count": count} for date, count in daily_counts
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting message statistics: {str(e)}"
        )