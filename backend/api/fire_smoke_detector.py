import os
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("fire_smoke_detector")

_model = None


def _load():
    """Model memory mein SIRF EK BAAR load hota hai."""
    global _model
    if _model is None:
        if os.path.exists(settings.FIRE_SMOKE_MODEL_PATH):
            from ultralytics import YOLO
            _model = YOLO(settings.FIRE_SMOKE_MODEL_PATH)
            logger.info("Fire/Smoke model loaded (shared instance)")
        else:
            _model = False
            logger.warning("Fire/Smoke model NOT found -> detection disabled (no fake AI)")
    return _model


def detect_all(frame):
    """Ek inference mein fire + smoke dono classes."""
    model = _load()
    if not model:
        return []
    dets = []
    for r in model(frame, conf=settings.CONFIDENCE_THRESHOLD, verbose=False):
        for box in r.boxes:
            name = str(model.names[int(box.cls[0])]).lower()
            if "fire" in name or "smoke" in name:
                dets.append({
                    "label": "fire" if "fire" in name else "smoke",
                    "confidence": round(float(box.conf[0]), 2),
                    "bbox": [float(v) for v in box.xyxy[0]],
                })
    return dets