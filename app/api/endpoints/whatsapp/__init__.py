# WhatsApp API Endpoints
from .whatsapp_templates import router as whatsapp_templates_router
from .whatsapp_campaigns import router as whatsapp_campaigns_router
from .whatsapp_messages import router as whatsapp_messages_router
from .whatsapp_contacts import router as whatsapp_contacts_router

__all__ = [
    "whatsapp_templates_router",
    "whatsapp_campaigns_router",
    "whatsapp_messages_router",
    "whatsapp_contacts_router"
]