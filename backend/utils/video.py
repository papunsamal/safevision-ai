import cv2
from ..utils.logger import get_logger

logger = get_logger("video")


def open_video(path: str):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Video nahi khul saka: {path}")
    return cap


def get_frame_count(cap) -> int:
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)


def sample_frames(cap, every_n: int = 10, max_frames: int = 50):
    idx = 0
    processed = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % every_n == 0:
            yield idx, frame
            processed += 1
            if processed >= max_frames:
                break
        idx += 1
    cap.release()


def to_percent_boxes(dets, frame_w, frame_h):
    out = []
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        out.append({
            "label": d["label"],
            "confidence": d["confidence"],
            "x": round(x1 / frame_w * 100, 2),
            "y": round(y1 / frame_h * 100, 2),
            "w": round((x2 - x1) / frame_w * 100, 2),
            "h": round((y2 - y1) / frame_h * 100, 2),
        })
    return out