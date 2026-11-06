from fastapi import APIRouter
from app.config import settings
from app.agents.llm_client import GeminiClientWrapper

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    llm = GeminiClientWrapper()
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "gemini_configured": llm.is_configured(),
        "active_model": llm.model,
        "max_tool_steps": settings.MAX_TOOL_STEPS
    }
