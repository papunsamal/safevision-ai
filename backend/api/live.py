import cv2
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..ai import ppe_detector, fire_detector, smoke_detector
from ..rules import compliance_engine, zone_rules
from ..alerts import alert_manager
from ..utils.logger import get_logger

router = APIRouter(prefix="/api", tags=["live"])
logger = get_logger("live")

CAMERA_ID = "CAM-LIVE"   # zones.json mein "Live Monitoring" (Z5) se mapped

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


def _live_gen(cap):
    logger.info("LIVE stream started (webcam)")
    zone_name = zone_rules.zone_for_camera(CAMERA_ID).get("name", "Unknown")
    frame_no = 0
    last_dets = []
    pending = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_no += 1

        if frame_no % 10 == 0:
            dets = (ppe_detector.detect(frame)
                    + fire_detector.detect(frame)
                    + smoke_detector.detect(frame))
            last_dets = dets

            # Temporal confirmation: 2 consecutive processed frames par hi PPE incident
            analysis = compliance_engine.analyze_detections(dets)
            new_pending = {}
            for v in analysis["violations"]:
                sig = (v["rule"], v.get("worker_id"))
                c = pending.get(sig, 0) + 1
                new_pending[sig] = c
                if c >= 2:
                    alert_manager.report_violation(v, CAMERA_ID, zone_name)
            pending = new_pending

            for lbl in ("fire", "smoke"):
                if any(d["label"] == lbl for d in dets):
                    alert_manager.report_violation(
                        {"type": lbl.upper(),
                         "severity": "CRITICAL" if lbl == "fire" else "HIGH",
                         "message": f"{lbl.capitalize()} Detected"},
                        CAMERA_ID, zone_name)

        # Flicker fix: HAR frame par last detections draw karo
        frame = _draw(frame, last_dets)

        ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                   + jpeg.tobytes() + b"\r\n")
    cap.release()


@router.get("/live/stream")
def live_stream(camera: int = 0):
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        cap.release()
        logger.error(f"Camera {camera} nahi khuli")
        raise HTTPException(503, f"Camera {camera} not available")
    return StreamingResponse(_live_gen(cap),
                             media_type="multipart/x-mixed-replace; boundary=frame")