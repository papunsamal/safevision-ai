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


def real_available():
    return os.path.exists(settings.MODEL_PATH)


@router.get("/videos")
def list_videos():
    """videos/ folder mein available mp4 names — frontend dropdown inhi se banta hai."""
    if os.path.isdir(settings.VIDEOS_DIR):
        return sorted(f[:-4] for f in os.listdir(settings.VIDEOS_DIR)
                      if f.lower().endswith(".mp4"))
    return []


def _analyze(name: str, camera_id: str = "CAM-01"):
    # ---- DEMO fallback (clearly labeled — no fake AI) ----
    if settings.AI_MODE != "REAL" or not real_available():
        return {
            "mode": "DEMO", "video": name,
            "detections": DEMO_DETECTIONS.get(name, []),
            "timeline": None,
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
    total = video_utils.get_frame_count(cap)

    # Poore video ka coverage: length ke hisaab se ~20 sampled frames
    every_n = max(5, total // 20) if total else 15

    timeline = []
    last_frame_dets = []
    last_analysis = None
    evidence_frame = None
    violation_counts = {}
    last_violation = {}
    fire_peak = smoke_peak = 0

    for idx, frame in video_utils.sample_frames(cap, every_n=every_n, max_frames=20):
        dets = (ppe_detector.detect(frame)
                + fire_detector.detect(frame)
                + smoke_detector.detect(frame))

        last_frame_dets = dets   # Bug 18: stale detections nahi
        timeline.append({
            "t": round(idx / total * 100, 2) if total else 0,
            "detections": video_utils.to_percent_boxes(dets, w, h),
        })
        if not dets:
            continue

        analysis = compliance_engine.analyze_detections(dets)
        last_analysis = analysis

        fire_peak = max(fire_peak, sum(1 for d in dets if d["label"] == "fire"))
        smoke_peak = max(smoke_peak, sum(1 for d in dets if d["label"] == "smoke"))

        # Bug 19: evidence frame = wahi frame jisme detection/violation tha
        if analysis["violations"] or fire_peak or smoke_peak:
            evidence_frame = frame

        # Bug 13: temporal confirmation ke liye frame-count
        for v in analysis["violations"]:
            sig = (v["rule"], v.get("worker_id"))
            violation_counts[sig] = violation_counts.get(sig, 0) + 1
            last_violation[sig] = v

    if last_analysis is None:
        last_analysis = {"workers": [], "violations": [],
                         "stats": {"totalWorkers": 0, "compliantWorkers": 0, "ppeViolations": 0}}

    stats = last_analysis["stats"]
    stats["fireIncidents"] = fire_peak    # Bug 16: poore video ka peak, sirf last frame nahi
    stats["smokeIncidents"] = smoke_peak

    workers.update_analysis(last_analysis["workers"], stats)
    database.upsert_daily_stats(stats)

    # >=2 sampled frames mein confirmed tabhi incident (single-frame false alert fix)
    confirmed = [last_violation[sig] for sig, c in violation_counts.items() if c >= 2]

    has_fire_smoke = fire_peak > 0 or smoke_peak > 0
    frame_url = None
    if (confirmed or has_fire_smoke) and evidence_frame is not None:
        frame_url = evidence.save_snapshot(evidence_frame, name)

    zone_name = zone_rules.zone_for_camera(camera_id).get("name", "Unknown")
    for v in confirmed:
        alert_manager.report_violation(v, camera_id, zone_name, frame_url)

    if fire_peak > 0:
        alert_manager.report_violation(
            {"type": "FIRE", "severity": "CRITICAL", "message": "Fire Detected"},
            camera_id, zone_name, frame_url)
    if smoke_peak > 0:
        alert_manager.report_violation(
            {"type": "SMOKE", "severity": "HIGH", "message": "Smoke Detected"},
            camera_id, zone_name, frame_url)

    logger.info(f"REAL analysis: {name} | workers={stats['totalWorkers']} "
                f"fire={fire_peak} smoke={smoke_peak}")

    return {
        "mode": "REAL", "video": name,
        "detections": video_utils.to_percent_boxes(last_frame_dets, w, h),
        "timeline": timeline,
        "workers": last_analysis["workers"],
        "violations": last_analysis["violations"],
        "stats": stats,
    }


@router.get("/detections")
def get_detections(video: str = "compliant", mode: str = "DEMO"):
    if mode == "REAL":
        return _analyze(video)
    return {"mode": "DEMO", "detections": DEMO_DETECTIONS.get(video, []), "timeline": None}


@router.post("/analyze-video")
def analyze_video(video: str = "violation"):
    return _analyze(video)