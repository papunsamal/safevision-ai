from . import fire_smoke_detector


def detect(frame):
    return [d for d in fire_smoke_detector.detect_all(frame) if d["label"] == "fire"]