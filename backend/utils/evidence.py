import os
import time

import cv2

from ..config import settings


def save_snapshot(frame, tag: str) -> str:
    """Violation frame ko evidence/alerts/ mein save karta hai."""
    os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
    fname = f"{tag}_{int(time.time())}.jpg"
    path = os.path.join(settings.EVIDENCE_DIR, fname)
    cv2.imwrite(path, frame)
    return f"/evidence/{fname}"