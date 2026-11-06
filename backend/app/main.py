from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.connection import init_db
from app.services.dataset_service import DatasetService

from app.api.health import router as health_router
from app.api.datasets import router as datasets_router
from app.api.agent import router as agent_router
from app.api.reports import router as reports_router
from app.api.settings_router import router as settings_router

# Initialize database schema & seed sample datasets on load
init_db()
try:
    DatasetService.seed_sample_datasets_if_needed()
except Exception as e:
    print(f"[Warning] Sample dataset seed failed: {e}")

app = FastAPI(
    title="InsightOps – AI-Powered Data Analyst Agent API",
    description="Autonomous data analyst platform integrating Google Gemini tool-calling with sandboxed Python data operations.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": str(exc)}
    )

# Register API Routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(agent_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "message": "InsightOps Data Analyst Agent API is running.",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
