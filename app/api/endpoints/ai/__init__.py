# AI API Endpoints
from .ai_analytics import router as ai_analytics_router
from .ai_predictions import router as ai_predictions_router
from .ai_models import router as ai_models_router
from .ai_insights import router as ai_insights_router

__all__ = [
    "ai_analytics_router",
    "ai_predictions_router",
    "ai_models_router",
    "ai_insights_router"
]