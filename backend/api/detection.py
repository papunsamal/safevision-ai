import os
import cv2
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..utils import video as video_utils
from ..utils import evidence
from ..utils.logger import get_logger
from ..ai import ppe_detector, fire_smoke_detector
from ..rules import compliance_engine, zone_rules
from ..alerts import alert_manager
from ..database import database
from . import workers

router = APIRouter(prefix="/api", tags=["detection"])
logger = get_logger("detection")

NO_HEAD_CLASSES = {"no_helmet", "none"}

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
    if frontend_mode:
        if frontend_mode == "REAL" and os.path.exists(settings.MODEL_PATH):
            return "REAL"
        return "DEMO"
    if settings.AI_MODE == "REAL" and os.path.exists(settings.MODEL_PATH):
        return "REAL"
    return "DEMO"


@router.get("/videos")
def list_videos():
    if os.path.isdir(settings.VIDEOS_DIR):
        return sorted(f[:-4] for f in os.listdir(settings.VIDEOS_DIR)
                      if f.lower().endswith(".mp4"))
    return []


def _analyze(name: str, camera_id: str = "CAM-01", resolved_mode: str = None):
    # ---- DEMO fallback (clearly labeled — no fake AI) ----
    if (resolved_mode or effective_mode()) == "DEMO":
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
    total = video_utils.get_frame_count(cap)   # FIX: timeline % ke liye

    GRID = 10
    merged = {}
    last_frame_dets = []          # OVERLAY ke liye sirf current frame
    timeline = []                 # FIX: per-frame synced boxes

    # Boolean event counting: continuous event = 1 incident
    fire_incidents = smoke_incidents = 0
    fire_active = smoke_active = False

    evidence_frame = None
    evidence_score = -1

    for idx, frame in video_utils.sample_frames(cap, every_n=15, max_frames=10):
        dets = ppe_detector.detect(frame) + fire_smoke_detector.detect_all(frame)

        if not dets:
            fire_active = False
            smoke_active = False
            continue

        last_frame_dets = dets    # overlay = latest analyzed frame (clean)
        analysis = compliance_engine.analyze_detections(dets)

        # FIX: timeline entry — video time % par matching boxes
        timeline.append({
            "t": round(idx / total * 100, 2) if total else 0,
            "detections": video_utils.to_percent_boxes(dets, w, h),
        })

        # Workers merge (poore video se — STATS ke liye)
        persons = sorted((d for d in dets if d["label"].lower() == "person"),
                         key=lambda d: d["bbox"][0])
        for wk, p in zip(analysis["workers"], persons):
            b = p["bbox"]
            cx = ((b[0] + b[2]) / 2) / w * 100
            cy = ((b[1] + b[3]) / 2) / h * 100
            key = (int(cx // GRID), int(cy // GRID))
            m = merged.setdefault(key, {"x": cx, "helmet": False, "vest": False,
                                        "none": False, "no_vest": False,
                                        "none_count": 0, "no_vest_count": 0})
            m["helmet"] = m["helmet"] or wk["helmet"]
            m["vest"] = m["vest"] or wk["vest"]
            m["no_vest"] = m["no_vest"] or wk.get("no_vest", False)
            if wk["head_status"] in NO_HEAD_CLASSES:
                m["none"] = True
                m["none_count"] += 1
            if wk.get("no_vest"):
                m["no_vest_count"] += 1

        # Continuous event = 1 incident
        has_fire = any(d["label"] == "fire" for d in dets)
        has_smoke = any(d["label"] == "smoke" for d in dets)
        if has_fire and not fire_active:
            fire_incidents += 1
            fire_active = True
        elif not has_fire:
            fire_active = False
        if has_smoke and not smoke_active:
            smoke_incidents += 1
            smoke_active = True
        elif not has_smoke:
            smoke_active = False

        score = len(analysis["violations"]) + (1 if has_fire else 0) + (1 if has_smoke else 0)
        if score > evidence_score:
            evidence_score = score
            evidence_frame = frame

    workers_list, violations_list = [], []
    for i, (_, m) in enumerate(sorted(merged.items(), key=lambda kv: kv[1]["x"]), start=1):
        head_status = "helmet" if m["helmet"] else ("none" if m["none"] else None)
        workers_list.append({"id": i, "helmet": m["helmet"], "vest": m["vest"],
                             "no_vest": m["no_vest"], "head_status": head_status})
        if m["none"] and m["none_count"] >= 2:
            violations_list.append({"type": "PPE", "rule": "NO_HELMET", "severity": "HIGH",
                                    "message": "No Helmet Detected", "worker_id": i})
        if m["no_vest"] and m["no_vest_count"] >= 2:
            violations_list.append({"type": "PPE", "rule": "NO_VEST", "severity": "MEDIUM",
                                    "message": "No Vest Detected", "worker_id": i})

    compliant = sum(1 for wk in workers_list if wk["helmet"] and not wk["no_vest"])

    stats = {
        "totalWorkers": len(workers_list),
        "compliantWorkers": compliant,
        "ppeViolations": len(violations_list),
        "fireIncidents": fire_incidents,
        "smokeIncidents": smoke_incidents,
    }

    workers.update_analysis(workers_list, stats)
    try:
        database.upsert_daily_stats(stats)
    except Exception as e:
        logger.error(f"Daily stats save failed (MySQL down?): {e}")

    frame_url = None
    if (violations_list or fire_incidents or smoke_incidents) and evidence_frame is not None:
        frame_url = evidence.save_snapshot(evidence_frame, name)

    zone_name = zone_rules.zone_for_camera(camera_id).get("name", "Unknown")
    for v in violations_list:
        alert_manager.report_violation(v, camera_id, zone_name, frame_url)
    if fire_incidents > 0:
        alert_manager.report_violation(
            {"type": "FIRE", "severity": "CRITICAL", "message": "Fire Detected"},
            camera_id, zone_name, frame_url)
    if smoke_incidents > 0:
        alert_manager.report_violation(
            {"type": "SMOKE", "severity": "HIGH", "message": "Smoke Detected"},
            camera_id, zone_name, frame_url)

    logger.info(f"REAL analysis: {name} | workers={stats['totalWorkers']} "
                f"fire={fire_incidents} smoke={smoke_incidents}")

    return {
        "mode": "REAL", "video": name,
        "detections": video_utils.to_percent_boxes(last_frame_dets, w, h),
        "timeline": timeline,                       # FIX: sync data added
        "workers": workers_list,
        "violations": violations_list,
        "stats": stats,
    }


@router.get("/detections")
def get_detections(video: str = "compliant", mode: str = "DEMO"):
    rm = effective_mode(mode)
    if rm == "REAL":
        return _analyze(video, resolved_mode=rm)
    return {"mode": "DEMO", "detections": DEMO_DETECTIONS.get(video, []), "timeline": None}


@router.post("/analyze-video")
def analyze_video(video: str = "violation", mode: str = "DEMO"):
    rm = effective_mode(mode)
    if rm == "REAL":
        return _analyze(video, resolved_mode=rm)
    return {
        "mode": "DEMO", "video": video,
        "detections": DEMO_DETECTIONS.get(video, []),
        "timeline": None,
        "workers": workers.DEMO_WORKERS,
        "violations": [],
        "stats": workers.DEMO_STATS,
    }