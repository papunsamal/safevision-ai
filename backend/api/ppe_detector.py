import os
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("ppe_detector")

_model = None
_model_classes = []


def _load():
    global _model, _model_classes
    if _model is not None:
        return _model
    try:
        from ultralytics import YOLO
        if os.path.exists(settings.MODEL_PATH):
            _model = YOLO(settings.MODEL_PATH)
            _model_classes = list(_model.names.values())
            logger.info(f"Custom PPE model loaded | classes={_model_classes}")
        else:
            # HONESTY: generic YOLO sirf 'person' jaanta hai — ise PPE detector
            # kehna fake claim hoga. Model missing -> PPE detection OFF (no fake AI).
            _model = False
            _model_classes = []
            logger.warning("Custom PPE model NOT found -> PPE detection disabled (no fake AI)")
    except Exception as e:
        logger.error(f"PPE model load failed: {e}")
        _model = False
    return _model


def supported_classes():
    _load()
    return _model_classes


def detect(frame):
    model = _load()
    if not model:
        return []
    results = model(frame, conf=settings.CONFIDENCE_THRESHOLD, verbose=False)
    dets = []
    for r in results:
        for box in r.boxes:
            name = model.names[int(box.cls[0])]
            if name in _model_classes:
                dets.append({
                    "label": name,
                    "confidence": round(float(box.conf[0]), 2),
                    "bbox": [float(v) for v in box.xyxy[0]],
                })
    return dets