# WhatsApp API Endpoints
from .whatsapp_templates import router as whatsapp_templates_router
from .whatsapp_messages import router as whatsapp_messages_router
from .whatsapp_campaigns import router as whatsapp_campaigns_router
from .whatsapp_integration import router as whatsapp_integration_router
from .whatsapp_webhooks import router as whatsapp_webhooks_router
from .whatsapp_setup import router as whatsapp_setup_router

__all__ = [
    "whatsapp_templates_router",
    "whatsapp_messages_router", 
    "whatsapp_campaigns_router",
    "whatsapp_integration_router",
    "whatsapp_webhooks_router",
    "whatsapp_setup_router"
]