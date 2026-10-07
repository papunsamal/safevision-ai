from fastapi import APIRouter

from ..database import database
from ..utils.logger import get_logger

logger = get_logger("alerts")

router = APIRouter(prefix="/api", tags=["alerts"])

DEMO_ALERTS = [
    {"id": 1, "type": "PPE", "severity": "HIGH", "message": "No Helmet Detected", "camera": "CAM-01", "zone": "Production Area", "time": "10:41"},
    {"id": 2, "type": "FIRE", "severity": "CRITICAL", "message": "Fire Detected", "camera": "CAM-02", "zone": "Warehouse", "time": "10:38"},
    {"id": 3, "type": "SMOKE", "severity": "HIGH", "message": "Smoke Detected", "camera": "CAM-03", "zone": "Boiler Area", "time": "10:31"},
]

DEMO_REPORTS = {
    "complianceTrend": [
        {"day": "Mon", "value": 72}, {"day": "Tue", "value": 75}, {"day": "Wed", "value": 71},
        {"day": "Thu", "value": 80}, {"day": "Fri", "value": 84}, {"day": "Sat", "value": 82},
        {"day": "Sun", "value": 88},
    ],
    "incidentTrend": [
        {"day": "Mon", "ppe": 4, "fire": 1, "smoke": 2}, {"day": "Tue", "ppe": 3, "fire": 0, "smoke": 1},
        {"day": "Wed", "ppe": 6, "fire": 2, "smoke": 2}, {"day": "Thu", "ppe": 2, "fire": 0, "smoke": 1},
        {"day": "Fri", "ppe": 5, "fire": 1, "smoke": 3}, {"day": "Sat", "ppe": 3, "fire": 0, "smoke": 0},
        {"day": "Sun", "ppe": 1, "fire": 0, "smoke": 1},
    ],
}


@router.get("/alerts")
def get_alerts(mode: str = "REAL"):
    if mode == "DEMO":
        return DEMO_ALERTS
    try:
        return database.fetch_incidents(50)
    except Exception as e:
        logger.error(f"Alerts fetch failed (MySQL down?): {e}")
        return []


@router.get("/reports")
def get_reports(mode: str = "REAL"):
    if mode == "DEMO":
        return DEMO_REPORTS
    try:
        return database.fetch_trends()
    except Exception as e:
        logger.error(f"Reports fetch failed (MySQL down?): {e}")
        return {"complianceTrend": [], "incidentTrend": []}