import cv2
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..ai import ppe_detector, fire_detector, smoke_detector
from ..rules import compliance_engine, zone_rules
from ..alerts import alert_manager
from ..utils.logger import get_logger

router = APIRouter(prefix="/api", tags=["live"])
logger = get_logger("live")

CAMERA_ID = "CAM-LIVE"

COLORS = {
    "fire": (0, 0, 255), "smoke": (0, 165, 255),
    "no_helmet": (0, 0, 255), "none": (0, 0, 255),
    "helmet": (0, 255, 0), "vest": (0, 255, 0),
    "Person": (255, 255, 0),
}


def _draw(frame, dets):
    for d in dets:
        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
        color = COLORS.get(d["label"], (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{d['label']} {int(d['confidence'] * 100)}%",
                    (x1, max(12, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def _live_gen(camera_index: int = 0):
    cap = cv2.VideoCapture(camera_index)   # 0 = laptop webcam
    if not cap.isOpened():
        logger.error("Webcam nahi khuli!")
        return
    logger.info("LIVE stream started (webcam)")
    frame_no = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_no += 1

        # Har 10ve frame par detection (CPU speed ke liye)
        if frame_no % 10 == 0:
            dets = (ppe_detector.detect(frame)
                    + fire_detector.detect(frame)
                    + smoke_detector.detect(frame))
            frame = _draw(frame, dets)

            # Compliance + incidents (cooldown spam rokta hai)
            analysis = compliance_engine.analyze_detections(dets)
            zone_name = zone_rules.zone_for_camera(CAMERA_ID).get("name", "Unknown")
            for v in analysis["violations"]:
                alert_manager.report_violation(v, CAMERA_ID, zone_name)

            seen = set()
            for d in dets:
                lbl = d["label"].lower()
                if lbl in ("fire", "smoke") and lbl not in seen:
                    seen.add(lbl)
                    alert_manager.report_violation(
                        {"type": lbl.upper(),
                         "severity": "CRITICAL" if lbl == "fire" else "HIGH",
                         "message": f"{lbl.capitalize()} Detected"},
                        CAMERA_ID, zone_name)

        ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                   + jpeg.tobytes() + b"\r\n")
    cap.release()


@router.get("/live/stream")
def live_stream(camera: int = 0):
    """MJPEG live stream — browser <img> tag se directly chalta hai."""
    return StreamingResponse(_live_gen(camera),
                             media_type="multipart/x-mixed-replace; boundary=frame")