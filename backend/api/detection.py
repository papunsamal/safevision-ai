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


def effective_mode() -> str:
    """REAL tabhi jab trained model maujood ho."""
    if settings.AI_MODE == "REAL" and os.path.exists(settings.MODEL_PATH):
        return "REAL"
    return "DEMO"


@router.get("/videos")
def list_videos():
    """Available video names (404 fix)."""
    if os.path.isdir(settings.VIDEOS_DIR):
        return sorted(f[:-4] for f in os.listdir(settings.VIDEOS_DIR)
                      if f.lower().endswith(".mp4"))
    return []


def _analyze(name: str, camera_id: str = "CAM-01"):
    mode = effective_mode()

    # DEMO fallback
    if mode == "DEMO":
        return {
            "mode": "DEMO", "video": name,
            "detections": DEMO_DETECTIONS.get(name, []),
            "workers": workers.DEMO_WORKERS,
            "violations": [],
            "stats": workers.DEMO_STATS,
        }

    # REAL pipeline
    path = os.path.join(settings.VIDEOS_DIR, f"{name}.mp4")
    if not os.path.exists(path):
        raise HTTPException(404, f"Video not found: videos/{name}.mp4")

    cap = video_utils.open_video(path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Aggregate across ALL sampled frames (not just last)
    all_workers = []
    all_violations = []
    fire_count = 0
    smoke_count = 0
    last_frame_dets = []
    evidence_frame = None

    for idx, frame in video_utils.sample_frames(cap, every_n=15, max_frames=10):
        dets = (ppe_detector.detect(frame)
                + fire_detector.detect(frame)
                + smoke_detector.detect(frame))
        
        if not dets:
            continue

        last_frame_dets = dets
        analysis = compliance_engine.analyze_detections(dets)

        # Collect workers from this frame
        all_workers.extend(analysis["workers"])
        all_violations.extend(analysis["violations"])

        # Count unique fire/smoke events (not peak)
        fire_count += sum(1 for d in dets if d["label"] == "fire")
        smoke_count += sum(1 for d in dets if d["label"] == "smoke")

        # Evidence = frame with first violation/detection
        if evidence_frame is None and (analysis["violations"] or fire_count or smoke_count):
            evidence_frame = frame

     # Deduplicate workers by ID (keep first occurrence)
    seen_ids = set()
    unique_workers = []
    for wk in all_workers:
        if wk["id"] not in seen_ids:
            seen_ids.add(wk["id"])
            unique_workers.append(wk)

    # Deduplicate violations by (rule, worker_id)
    seen_violations = set()
    unique_violations = []
    for v in all_violations:
        sig = (v["rule"], v.get("worker_id"))
        if sig not in seen_violations:
            seen_violations.add(sig)
            unique_violations.append(v)

    compliant_count = sum(1 for w in unique_workers if w["helmet"])

    stats = {
        "totalWorkers": len(unique_workers),
        "compliantWorkers": compliant_count,
        "ppeViolations": len(unique_violations),
        "fireIncidents": fire_count,   # Bug #6: actual count, not peak
        "smokeIncidents": smoke_count,
    }

    workers.update_analysis(unique_workers, stats)
    database.upsert_daily_stats(stats)

    # Evidence snapshot
    frame_url = None
    if (unique_violations or fire_count or smoke_count) and evidence_frame is not None:
        frame_url = evidence.save_snapshot(evidence_frame, name)

    # Incidents
    zone_name = zone_rules.zone_for_camera(camera_id).get("name", "Unknown")
    for v in unique_violations:
        alert_manager.report_violation(v, camera_id, zone_name, frame_url)

    if fire_count > 0:
        alert_manager.report_violation(
            {"type": "FIRE", "severity": "CRITICAL", "message": "Fire Detected"},
            camera_id, zone_name, frame_url)
    if smoke_count > 0:
        alert_manager.report_violation(
            {"type": "SMOKE", "severity": "HIGH", "message": "Smoke Detected"},
            camera_id, zone_name, frame_url)

    logger.info(f"REAL analysis: {name} | workers={stats['totalWorkers']} "
                f"fire={fire_count} smoke={smoke_count}")

    return {
        "mode": "REAL", "video": name,
        "detections": video_utils.to_percent_boxes(last_frame_dets, w, h),
        "workers": unique_workers,
        "violations": unique_violations,
        "stats": stats,
    }


@router.get("/detections")
def get_detections(video: str = "compliant", mode: str = "DEMO"):
    result = _analyze(video)
    if mode == "REAL":
        return result
    return DEMO_DETECTIONS.get(video, [])


@router.post("/analyze-video")
def analyze_video(video: str = "violation"):
    return _analyze(video)