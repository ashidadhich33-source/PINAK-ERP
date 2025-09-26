"""
WhatsApp API endpoints for webhook and management
"""

from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
import hmac
import hashlib

from ...database import get_db
from ...services.whatsapp_service import WhatsAppService
from ...core.security import get_current_user
from ...config import settings

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp webhooks
    """
    # Verify webhook signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    if signature:
        body = await request.body()
        expected_signature = hmac.new(
            settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={expected_signature}", signature):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook
    data = await request.json()
    result = WhatsAppService.handle_webhook(data)
    
    return {"status": "ok", "result": result}

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verify webhook endpoint for WhatsApp
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
        return Response(content=challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/send-test")
async def send_test_message(
    mobile: str,
    message: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send a test message
    """
    success = WhatsAppService.send_promotional_message(mobile, message)
    
    if success:
        return {"status": "success", "message": "Message sent successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.post("/send-bulk")
async def send_bulk_messages(
    message: str,
    customer_grade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Send bulk messages to customers
    """
    from ...models import Customer
    
    query = db.query(Customer)
    
    if customer_grade:
        query = query.filter(Customer.grade == customer_grade)
    
    customers = query.all()
    
    recipients = [
        {
            "mobile": customer.mobile,
            "name": customer.name
        } for customer in customers
    ]
    
    # Use async bulk send
    import asyncio
    results = await WhatsAppService.send_bulk_messages(
        recipients,
        message,
        personalized=True
    )
    
    return {
        "status": "success",
        "total": len(recipients),
        "sent": results["success"],
        "failed": results["failed"]
    }