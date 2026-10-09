import cv2
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# Shared models import
from ..ai import ppe_detector, fire_smoke_detector
from ..rules import compliance_engine, zone_rules
from ..alerts import alert_manager
from ..utils.logger import get_logger

router = APIRouter(prefix="/api", tags=["live"])
logger = get_logger("live")

CAMERA_ID = "CAM-LIVE"   # zones.json mein mapped

COLORS = {
    "fire": (0, 0, 255), "smoke": (0, 165, 255),
    "no_helmet": (0, 0, 255), "none": (0, 0, 255),
    "helmet": (0, 255, 0), "vest": (0, 255, 0),
    "Person": (255, 255, 0),
}


def _draw(frame, dets):
    """Draw bounding boxes and labels on frame."""
    for d in dets:
        x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
        color = COLORS.get(d["label"], (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label_text = f"{d['label']} {int(d['confidence'] * 100)}%"
        cv2.putText(frame, label_text,
                    (x1, max(12, y1 - 8)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def _filter_detections(raw_dets, frame_shape):
    """
    Filter out tiny/noisy detections to reduce false positives.
    Keeps Fire/Smoke always. Filters Person/PPE by minimum area size.
    """
    if not raw_dets:
        return []
    
    h, w = frame_shape[:2]
    # Minimum area threshold: 2% of total image area
    min_area = (w * h) * 0.02 
    
    filtered = []
    for d in raw_dets:
        x1, y1, x2, y2 = d['bbox']
        area = abs(x2 - x1) * abs(y2 - y1)
        
        # Always keep fire/smoke regardless of size
        if d['label'].lower() in ['fire', 'smoke']:
            filtered.append(d)
        # Keep PPE items only if they are big enough (likely real objects)
        elif area > min_area:
            filtered.append(d)
            
    return filtered


def _live_gen(cap):
    logger.info("LIVE stream started (webcam)")
    zone_name = zone_rules.zone_for_camera(CAMERA_ID).get("name", "Unknown")
    frame_no = 0
    last_dets = []
    pending = {}

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_no += 1

            # Process every 10th frame for performance
            if frame_no % 10 == 0:
                # 1. Get Raw Detections
                raw_dets = ppe_detector.detect(frame) + fire_smoke_detector.detect_all(frame)
                
                # 2. FILTER NOISE (New Fix)
                dets = _filter_detections(raw_dets, frame.shape)
                last_dets = dets

                # 3. Analyze Compliance
                analysis = compliance_engine.analyze_detections(dets)
                new_pending = {}
                
                # Temporal Confirmation: Alert only if violation seen in 2+ consecutive processed frames
                for v in analysis["violations"]:
                    sig = (v["rule"], v.get("worker_id"))
                    c = pending.get(sig, 0) + 1
                    new_pending[sig] = c
                    if c >= 2:
                        alert_manager.report_violation(v, CAMERA_ID, zone_name)
                pending = new_pending

                # 4. Handle Fire/Smoke Alerts separately
                for lbl in ("fire", "smoke"):
                    if any(d["label"] == lbl for d in dets):
                        alert_manager.report_violation(
                            {"type": lbl.upper(),
                             "severity": "CRITICAL" if lbl == "fire" else "HIGH",
                             "message": f"{lbl.capitalize()} Detected"},
                            CAMERA_ID, zone_name)

            # Draw boxes on EVERY frame (using latest valid detections)
            frame_with_boxes = _draw(frame.copy(), last_dets)
            
            # Encode as JPEG for streaming
            ok, jpeg = cv2.imencode(".jpg", frame_with_boxes, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + jpeg.tobytes() + b"\r\n")
                       
    finally:
        # CRITICAL FIX: Ensure camera is ALWAYS released when stream stops/crashes
        cap.release()
        logger.info("LIVE stream stopped, camera released safely.")


@router.get("/live/stream")
def live_stream(camera: int = 0):
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        cap.release()
        logger.error(f"Camera {camera} could not be opened")
        raise HTTPException(503, f"Camera {camera} not available")
    
    return StreamingResponse(_live_gen(cap),
                             media_type="multipart/x-mixed-replace; boundary=frame")