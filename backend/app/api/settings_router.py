import os
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings
from app.models.schemas import SettingsStatus
from app.agents.llm_client import GeminiClientWrapper

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsUpdate(BaseModel):
    gemini_model: Optional[str] = None
    max_tool_steps: Optional[int] = None

@router.get("", response_model=SettingsStatus)
def get_settings():
    llm = GeminiClientWrapper()
    return SettingsStatus(
        api_key_configured=llm.is_configured(),
        model=llm.model,
        max_tool_steps=settings.MAX_TOOL_STEPS
    )

@router.post("", response_model=SettingsStatus)
def update_settings(update: SettingsUpdate):
    if update.gemini_model is not None:
        m = update.gemini_model.strip()
        settings.GEMINI_MODEL = m
        os.environ["GEMINI_MODEL"] = m
        
    if update.max_tool_steps is not None and 1 <= update.max_tool_steps <= 20:
        settings.MAX_TOOL_STEPS = update.max_tool_steps
        
    llm = GeminiClientWrapper()
    return SettingsStatus(
        api_key_configured=llm.is_configured(),
        model=llm.model,
        max_tool_steps=settings.MAX_TOOL_STEPS
    )

@router.post("/test")
def test_gemini_connection():
    llm = GeminiClientWrapper()
    return llm.test_connection()
