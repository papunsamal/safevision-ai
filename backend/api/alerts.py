from fastapi import APIRouter

from ..database import database

router = APIRouter(prefix="/api", tags=["alerts"])

DEMO_ALERTS = [
    {"id": 1, "type": "PPE", "severity": "HIGH", "message": "No Helmet Detected", "camera": "CAM-01", "zone": "Production Area", "time": "10:41 AM"},
    {"id": 2, "type": "FIRE", "severity": "CRITICAL", "message": "Fire Detected", "camera": "CAM-02", "zone": "Warehouse", "time": "10:38 AM"},
    {"id": 3, "type": "SMOKE", "severity": "HIGH", "message": "Smoke Detected", "camera": "CAM-03", "zone": "Boiler Area", "time": "10:31 AM"},
    {"id": 4, "type": "PPE", "severity": "MEDIUM", "message": "No Vest Detected", "camera": "CAM-01", "zone": "Production Area", "time": "09:58 AM"},
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
def get_alerts():
    rows = database.fetch_incidents(50)   # REAL incidents (persistent)
    if rows:
        return rows
    return DEMO_ALERTS


@router.get("/reports")
def get_reports():
    return DEMO_REPORTS