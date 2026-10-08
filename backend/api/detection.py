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
    mode = effective_mode()

    # ---- DEMO fallback (unchanged, clearly labeled) ----
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

    frame_results = []
    last_frame_dets = []
    evidence_frame = None
    sig_counts = {}
    fire_peak = smoke_peak = 0

    for idx, frame in video_utils.sample_frames(cap, every_n=15, max_frames=10):
        dets = (ppe_detector.detect(frame)
                + fire_detector.detect(frame)
                + smoke_detector.detect(frame))
        if not dets:
            continue
        last_frame_dets = dets

        analysis = compliance_engine.analyze_detections(dets)
        frame_results.append({"frame": frame, "analysis": analysis})

        fire_n = sum(1 for d in dets if d["label"] == "fire")
        smoke_n = sum(1 for d in dets if d["label"] == "smoke")
        # Bug #2: peak concurrent = minimum distinct events
        # (same fire 10 frames mein dikhe to count 1 hi rahega, 10 nahi)
        fire_peak = max(fire_peak, fire_n)
        smoke_peak = max(smoke_peak, smoke_n)

        if evidence_frame is None and (analysis["violations"] or fire_n or smoke_n):
            evidence_frame = frame

        # temporal confirmation counts (single-frame false alert fix)
        for v in analysis["violations"]:
            sig = (v["rule"], v.get("worker_id"))
            sig_counts[sig] = sig_counts.get(sig, 0) + 1

    if not frame_results:
        workers_list, violations_list = [], []
        compliant = 0
    else:
        # Bug #1: workers + violations EK HI frame (best frame) se —
        # frame-local IDs ko persistent identity ki tarah claim nahi karte.
        best = max(frame_results,
                   key=lambda fr: (len(fr["analysis"]["violations"]), len(fr["analysis"]["workers"])))
        workers_list = best["analysis"]["workers"]
        compliant = best["analysis"]["stats"]["compliantWorkers"]
        # sirf temporally confirmed (>=2 frames) violations report karo,
        # best frame ke consistent worker IDs ke saath
        violations_list = [
            v for v in best["analysis"]["violations"]
            if sig_counts.get((v["rule"], v.get("worker_id")), 0) >= 2
        ]

    stats = {
        "totalWorkers": len(workers_list),
        "compliantWorkers": compliant,
        "ppeViolations": len(violations_list),
        "fireIncidents": fire_peak,
        "smokeIncidents": smoke_peak,
    }

    workers.update_analysis(workers_list, stats)
    try:
        database.upsert_daily_stats(stats)
    except Exception as e:
        logger.error(f"Daily stats save failed (MySQL down?): {e}")

    frame_url = None
    if (violations_list or fire_peak or smoke_peak) and evidence_frame is not None:
        frame_url = evidence.save_snapshot(evidence_frame, name)

    zone_name = zone_rules.zone_for_camera(camera_id).get("name", "Unknown")
    for v in violations_list:
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
        "workers": workers_list,
        "violations": violations_list,
        "stats": stats,
    }


@router.get("/detections")
def get_detections(video: str = "compliant", mode: str = "DEMO"):
    if mode == "REAL":
        return _analyze(video)
    return {"mode": "DEMO", "detections": DEMO_DETECTIONS.get(video, [])}


@router.post("/analyze-video")
def analyze_video(video: str = "violation"):
    return _analyze(video)