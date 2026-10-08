from . import fire_smoke_detector


def detect(frame):
    """Delegate to shared module, filter smoke only."""
    return [d for d in fire_smoke_detector.detect_all(frame) if d["label"] == "smoke"]