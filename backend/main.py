import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import get_settings
from routers import upload, pipeline, ws

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    logger.info("AutoML Copilot Backend started")
    yield
    logger.info("AutoML Copilot Backend shutting down")


app = FastAPI(
    title="Adaptive Multi-Agent AutoML Copilot",
    description="Enterprise-grade autonomous ML platform powered by CrewAI + Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
app.include_router(ws.router, tags=["websocket"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AutoML Copilot"}


@app.get("/api/download/{job_id}")
async def download_model(job_id: str):
    model_path = os.path.join(settings.MODELS_DIR, f"{job_id}_best_model.pkl")
    if not os.path.exists(model_path):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Model not found")
    return FileResponse(
        path=model_path,
        filename=f"automl_model_{job_id}.pkl",
        media_type="application/octet-stream",
    )
