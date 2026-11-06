import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

# Load .env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")
    
    PROJECT_NAME: str = "InsightOps"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # System Gemini API settings (loaded strictly from .env or environment variable)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    
    # Execution constraints
    MAX_TOOL_STEPS: int = 8
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = [".csv", ".xlsx", ".xls"]
    
    # Storage paths
    STORAGE_DIR: Path = BASE_DIR / "storage"
    DATASETS_DIR: Path = BASE_DIR / "storage" / "datasets"
    REPORTS_DIR: Path = BASE_DIR / "storage" / "reports"
    DATABASE_PATH: Path = BASE_DIR / "storage" / "insightops.db"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]

settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
