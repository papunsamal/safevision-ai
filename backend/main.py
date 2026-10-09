import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .utils.logger import get_logger
from .database import database as db
from .ai import ppe_detector
from .api import alerts, cameras, detection, workers, live

logger = get_logger("main")

app = FastAPI(title="SafeVision AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workers.router)
app.include_router(alerts.router)
app.include_router(cameras.router)
app.include_router(detection.router)
app.include_router(live.router)

# MySQL down ho to bhi backend chale (alerts/reports gracefully empty)
try:
    db.init_db()
except Exception as e:
    logger.error(f"MySQL init failed (backend phir bhi chalega): {e}")

os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=settings.EVIDENCE_DIR), name="evidence")

REAL_IMPLEMENTED = True


def effective_mode() -> str:
    if settings.AI_MODE == "REAL" and REAL_IMPLEMENTED and os.path.exists(settings.MODEL_PATH):
        return "REAL"
    return "DEMO"


@app.get("/health")
def health():
    logger.info("Health check requested")
    
    # Determine actual mode based on ENV setting AND file existence
    env_is_real = settings.AI_MODE == "REAL"
    model_exists = os.path.exists(settings.MODEL_PATH)
    
    # Honesty Policy: If env says REAL but model missing -> Force DEMO
    actual_mode = "REAL" if (env_is_real and model_exists) else "DEMO"

    return {
        "status": "ok",
        "mode": actual_mode,
        "models": {
            "ppe_model": model_exists,
            "fire_smoke_model": os.path.exists(settings.FIRE_SMOKE_MODEL_PATH),
        },
        "supported_classes": (
            ppe_detector.supported_classes()
            if model_exists
            else ["person"]
        ),
    }


if os.path.isdir(settings.VIDEOS_DIR):
    app.mount("/videos", StaticFiles(directory=settings.VIDEOS_DIR), name="videos")