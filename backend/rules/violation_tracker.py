from datetime import datetime

from ..database import database
from ..utils.logger import get_logger

logger = get_logger("violation_tracker")

_incident_counter = 1
_recent_incidents = []


def record_incident(violation, camera_id, zone_name, frame_url=None):
    global _incident_counter
    incident = {
        "id": _incident_counter,
        "type": violation["type"],
        "severity": violation["severity"],
        "message": violation["message"],
        "camera": camera_id,
        "zone": zone_name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "worker_id": violation.get("worker_id"),
    }
    _incident_counter += 1
    _recent_incidents.insert(0, incident)
    _recent_incidents[:] = _recent_incidents[:50]

    # Persistent storage (MySQL)
    try:
        database.insert_incident(incident, frame_url)
    except Exception as e:
        logger.error(f"DB insert failed: {e}")

    logger.info(f"INCIDENT #{incident['id']}: {incident['message']} @ {camera_id}")
    return incident


def get_recent_incidents():
    return _recent_incidents