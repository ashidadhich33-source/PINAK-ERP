"""
WhatsApp Integration API Endpoints for POS and Loyalty
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.deps import get_db, get_current_user
from app.services.whatsapp.whatsapp_integration_service import WhatsAppIntegrationService
from app.schemas.whatsapp_schema import (
    POSReceiptRequest,
    LoyaltyPointsRequest,
    InvoiceRequest,
    MarketingMessageRequest,
    OptInRequest,
    OptOutRequest
)

router = APIRouter(prefix="/whatsapp/integration", tags=["WhatsApp Integration"])

# Service instance
integration_service = WhatsAppIntegrationService()


@router.post("/pos/receipt")
async def send_pos_receipt(
    receipt_data: POSReceiptRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send POS receipt via WhatsApp"""
    try:
        result = integration_service.send_pos_receipt(
            db=db,
            customer_id=receipt_data.customer_id,
            transaction_id=receipt_data.transaction_id,
            receipt_data=receipt_data.dict()
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
            detail=f"Error sending POS receipt: {str(e)}"
        )


@router.post("/loyalty/points")
async def send_loyalty_points_update(
    points_data: LoyaltyPointsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send loyalty points update via WhatsApp"""
    try:
        result = integration_service.send_loyalty_points_update(
            db=db,
            customer_id=points_data.customer_id,
            points_earned=points_data.points_earned,
            points_redeemed=points_data.points_redeemed,
            current_balance=points_data.current_balance,
            transaction_id=points_data.transaction_id
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
            detail=f"Error sending loyalty points update: {str(e)}"
        )


@router.post("/invoice")
async def send_invoice(
    invoice_data: InvoiceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send invoice via WhatsApp"""
    try:
        result = integration_service.send_invoice(
            db=db,
            customer_id=invoice_data.customer_id,
            invoice_data=invoice_data.dict()
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
            detail=f"Error sending invoice: {str(e)}"
        )


@router.post("/marketing")
async def send_marketing_message(
    marketing_data: MarketingMessageRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Send marketing message via WhatsApp"""
    try:
        result = integration_service.send_marketing_message(
            db=db,
            customer_id=marketing_data.customer_id,
            campaign_id=marketing_data.campaign_id,
            message_data=marketing_data.dict()
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
            detail=f"Error sending marketing message: {str(e)}"
        )


@router.post("/opt-in")
async def handle_opt_in(
    opt_data: OptInRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Handle customer opt-in for WhatsApp messages"""
    try:
        result = integration_service.handle_customer_opt_in(
            db=db,
            phone_number=opt_data.phone_number,
            opt_type=opt_data.opt_type,
            customer_id=opt_data.customer_id
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
            detail=f"Error handling opt-in: {str(e)}"
        )


@router.post("/opt-out")
async def handle_opt_out(
    opt_data: OptOutRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Handle customer opt-out from WhatsApp messages"""
    try:
        result = integration_service.handle_customer_opt_out(
            db=db,
            phone_number=opt_data.phone_number,
            opt_type=opt_data.opt_type
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
            detail=f"Error handling opt-out: {str(e)}"
        )


@router.get("/customer/{customer_id}/preferences")
async def get_customer_preferences(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get customer WhatsApp preferences"""
    try:
        from app.models.whatsapp.whatsapp_models import WhatsAppCustomer
        
        whatsapp_customer = db.query(WhatsAppCustomer).filter(
            WhatsAppCustomer.customer_id == customer_id
        ).first()
        
        if not whatsapp_customer:
            return {
                "customer_id": customer_id,
                "phone_number": None,
                "transactional_opt_in": False,
                "marketing_opt_in": False,
                "utility_opt_in": False
            }
        
        return {
            "customer_id": whatsapp_customer.customer_id,
            "phone_number": whatsapp_customer.phone_number,
            "transactional_opt_in": whatsapp_customer.transactional_opt_in,
            "marketing_opt_in": whatsapp_customer.marketing_opt_in,
            "utility_opt_in": whatsapp_customer.utility_opt_in,
            "transactional_opted_in_at": whatsapp_customer.transactional_opted_in_at.isoformat() if whatsapp_customer.transactional_opted_in_at else None,
            "marketing_opted_in_at": whatsapp_customer.marketing_opted_in_at.isoformat() if whatsapp_customer.marketing_opted_in_at else None,
            "utility_opted_in_at": whatsapp_customer.utility_opted_in_at.isoformat() if whatsapp_customer.utility_opted_in_at else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting customer preferences: {str(e)}"
        )


@router.get("/messages/{customer_id}")
async def get_customer_messages(
    customer_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get customer WhatsApp message history"""
    try:
        from app.models.whatsapp.whatsapp_models import WhatsAppMessage
        
        messages = db.query(WhatsAppMessage).filter(
            WhatsAppMessage.customer_id == customer_id
        ).order_by(WhatsAppMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        return {
            "customer_id": customer_id,
            "messages": [
                {
                    "id": msg.id,
                    "message_type": msg.message_type,
                    "content": msg.content,
                    "status": msg.status.value,
                    "context_type": msg.context_type,
                    "context_id": msg.context_id,
                    "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                    "delivered_at": msg.delivered_at.isoformat() if msg.delivered_at else None,
                    "read_at": msg.read_at.isoformat() if msg.read_at else None,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ],
            "total": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting customer messages: {str(e)}"
        )