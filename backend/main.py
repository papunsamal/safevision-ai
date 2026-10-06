import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .utils.logger import get_logger
from .api import alerts, cameras, detection, workers
from .ai import ppe_detector
from .database import database as db

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
db.init_db()

os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=settings.EVIDENCE_DIR), name="evidence")

# Real YOLO inference code implement ho chuka hai (ai/ modules)
REAL_IMPLEMENTED = True


def effective_mode() -> str:
    """REAL sirf tab jab: env REAL ho + inference ready ho + trained model exist kare."""
    if settings.AI_MODE == "REAL" and REAL_IMPLEMENTED and os.path.exists(settings.MODEL_PATH):
        return "REAL"
    return "DEMO"


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {
        "status": "ok",
        "mode": effective_mode(),
        "models": {
            "ppe_model": os.path.exists(settings.MODEL_PATH),
            "fire_smoke_model": os.path.exists(settings.FIRE_SMOKE_MODEL_PATH),
        },
        "supported_classes": (
            ppe_detector.supported_classes()
            if os.path.exists(settings.MODEL_PATH)
            else ["person"]
        ),
    }


# Videos ko frontend ke liye serve karo
if os.path.isdir(settings.VIDEOS_DIR):
    app.mount("/videos", StaticFiles(directory=settings.VIDEOS_DIR), name="videos")