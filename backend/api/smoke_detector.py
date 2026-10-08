from . import fire_smoke_detector


def detect(frame):
    """Shared model se smoke-only detections (output format same)."""
    return [d for d in fire_smoke_detector.detect_all(frame) if d["label"] == "smoke"]