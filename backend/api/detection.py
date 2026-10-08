import os
import cv2
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..utils import video as video_utils
from ..utils import evidence
from ..utils.logger import get_logger
from ..ai import ppe_detector, fire_detector, smoke_detector
from ..rules import compliance_engine, zone_rules
from ..alerts import alert_manager
from ..database import database
from . import workers

router = APIRouter(prefix="/api", tags=["detection"])
logger = get_logger("detection")

DEMO_DETECTIONS = {
    "compliant": [
        {"label": "person", "confidence": 0.96, "x": 10, "y": 15, "w": 22, "h": 70},
        {"label": "helmet", "confidence": 0.93, "x": 12, "y": 15, "w": 8, "h": 10},
        {"label": "vest", "confidence": 0.91, "x": 12, "y": 35, "w": 16, "h": 25},
        {"label": "person", "confidence": 0.94, "x": 55, "y": 20, "w": 22, "h": 68},
        {"label": "helmet", "confidence": 0.9, "x": 57, "y": 20, "w": 8, "h": 10},
    ],
    "violation": [
        {"label": "person", "confidence": 0.95, "x": 15, "y": 18, "w": 22, "h": 68},
        {"label": "no_helmet", "confidence": 0.89, "x": 17, "y": 18, "w": 8, "h": 10},
        {"label": "person", "confidence": 0.93, "x": 60, "y": 22, "w": 20, "h": 66},
        {"label": "helmet", "confidence": 0.92, "x": 62, "y": 22, "w": 8, "h": 10},
    ],
    "fire_smoke": [
        {"label": "fire", "confidence": 0.91, "x": 40, "y": 55, "w": 18, "h": 25},
        {"label": "smoke", "confidence": 0.87, "x": 38, "y": 20, "w": 26, "h": 35},
    ],
}


def effective_mode(frontend_mode: str = None) -> str:
    """
    Frontend mode param ko respect karo, lekin model check bhi karo.
    - Frontend REAL + model exists → REAL
    - Frontend REAL + model missing → DEMO fallback
    - Frontend DEMO → DEMO
    """
    # Frontend ne explicitly mode bheja hai?
    if frontend_mode:
        if frontend_mode == "REAL" and os.path.exists(settings.MODEL_PATH):
            return "REAL"
        return "DEMO"
    
    # Fallback: backend config check
    if settings.AI_MODE == "REAL" and os.path.exists(settings.MODEL_PATH):
        return "REAL"
    return "DEMO"


@router.get("/videos")
def list_videos():
    if os.path.isdir(settings.VIDEOS_DIR):
        return sorted(f[:-4] for f in os.listdir(settings.VIDEOS_DIR)
                      if f.lower().endswith(".mp4"))
    return []


def _analyze(name: str, camera_id: str = "CAM-01"):
    # Frontend query param se mode determine karo
    mode = effective_mode()  # will be overridden by query param below

    # ---- DEMO fallback ----
    if mode == "DEMO":
        return {
            "mode": "DEMO", "video": name,
            "detections": DEMO_DETECTIONS.get(name, []),
            "workers": workers.DEMO_WORKERS,
            "violations": [],
            "stats": workers.DEMO_STATS,
        }

    # ---- REAL pipeline ----
    path = os.path.join(settings.VIDEOS_DIR, f"{name}.mp4")
    if not os.path.exists(path):
        raise HTTPException(404, f"Video not found: videos/{name}.mp4")

    cap = video_utils.open_video(path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    last_frame_dets = []
    last_analysis = None
    last_frame = None

    for idx, frame in video_utils.sample_frames(cap, every_n=15, max_frames=10):
        last_frame = frame
        dets = (ppe_detector.detect(frame)
                + fire_detector.detect(frame)
                + smoke_detector.detect(frame))
        if not dets:
            continue
        last_frame_dets = dets
        last_analysis = compliance_engine.analyze_detections(dets)

    if last_analysis is None:
        last_analysis = {
            "workers": [], "violations": [],
            "stats": {"totalWorkers": 0, "compliantWorkers": 0, "ppeViolations": 0},
        }

    stats = last_analysis["stats"]
    stats["fireIncidents"] = sum(1 for d in last_frame_dets if d["label"].lower() == "fire")
    stats["smokeIncidents"] = sum(1 for d in last_frame_dets if d["label"].lower() == "smoke")

    workers.update_analysis(last_analysis["workers"], stats)
    try:
        database.upsert_daily_stats(stats)
    except Exception as e:
        logger.error(f"Daily stats save failed: {e}")

    has_fire_smoke = any(d["label"].lower() in ("fire", "smoke") for d in last_frame_dets)
    frame_url = None
    if (last_analysis["violations"] or has_fire_smoke) and last_frame is not None:
        frame_url = evidence.save_snapshot(last_frame, name)

    zone_name = zone_rules.zone_for_camera(camera_id).get("name", "Unknown")
    for v in last_analysis["violations"]:
        alert_manager.report_violation(v, camera_id, zone_name, frame_url)

    seen = set()
    for d in last_frame_dets:
        lbl = d["label"].lower()
        if lbl in ("fire", "smoke") and lbl not in seen:
            seen.add(lbl)
            alert_manager.report_violation(
                {"type": lbl.upper(),
                 "severity": "CRITICAL" if lbl == "fire" else "HIGH",
                 "message": f"{lbl.capitalize()} Detected"},
                camera_id, zone_name, frame_url)

    logger.info(f"REAL analysis: {name} | workers={stats['totalWorkers']} "
                f"fire={stats['fireIncidents']} smoke={stats['smokeIncidents']}")

    return {
        "mode": "REAL", "video": name,
        "detections": video_utils.to_percent_boxes(last_frame_dets, w, h),
        "workers": last_analysis["workers"],
        "violations": last_analysis["violations"],
        "stats": stats,
    }


@router.get("/detections")
def get_detections(video: str = "compliant", mode: str = "DEMO"):
    # Frontend mode param ko backend tak pahunchao
    effective = effective_mode(mode)
    if effective == "REAL":
        return _analyze(video)
    return {"mode": "DEMO", "detections": DEMO_DETECTIONS.get(video, [])}


@router.post("/analyze-video")
def analyze_video(video: str = "violation", mode: str = "DEMO"):
    # Analyze video bhi mode param accept kare
    effective = effective_mode(mode)
    if effective == "REAL":
        return _analyze(video)
    return {
        "mode": "DEMO", "video": video,
        "detections": DEMO_DETECTIONS.get(video, []),
        "workers": workers.DEMO_WORKERS,
        "violations": [],
        "stats": workers.DEMO_STATS,
    }