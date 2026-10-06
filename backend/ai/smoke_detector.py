import os
from ..config import settings

_model = None


def _load():
    global _model
    if _model is None:
        if os.path.exists(settings.FIRE_SMOKE_MODEL_PATH):
            from ultralytics import YOLO
            _model = YOLO(settings.FIRE_SMOKE_MODEL_PATH)
        else:
            _model = False
    return _model


def detect(frame):
    model = _load()
    if not model:
        return []
    out = []
    for r in model(frame, conf=settings.CONFIDENCE_THRESHOLD, verbose=False):
        for box in r.boxes:
            name = model.names[int(box.cls[0])]
            if "smoke" in name.lower():
                out.append({"label": "smoke", "confidence": round(float(box.conf[0]), 2),
                            "bbox": [float(v) for v in box.xyxy[0]]})
    return out