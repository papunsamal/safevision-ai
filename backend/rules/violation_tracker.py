from datetime import datetime

from ..database import database
from ..utils.logger import get_logger

logger = get_logger("violation_tracker")

_incident_counter = 1
_recent_incidents = []


def record_incident(violation, camera_id, zone_name, frame_url=None):
    global _incident_counter
    
    # 1. Create Structured Incident Object
    incident = {
        "id": _incident_counter,
        "type": violation["type"],
        "severity": violation["severity"],
        "message": violation["message"],
        "camera": camera_id,
        "zone": zone_name,
        "time": datetime.now().strftime("%H:%M"),
        "worker_id": violation.get("worker_id"),
    }
    
    # 2. Update In-Memory Ring Buffer (For Fast UI Access)
    _incident_counter += 1
    _recent_incidents.insert(0, incident)
    # Keep only last 50 incidents to prevent memory leaks
    _recent_incidents[:] = _recent_incidents[:50]

    # 3. Persistent Storage (MySQL) - Wrapped in Try-Except for Safety
    try:
        database.insert_incident(incident, frame_url)
    except Exception as e:
        # Log error but DO NOT crash the application
        logger.error(f"DB insert failed for Incident #{incident['id']}: {e}")

    logger.info(f"INCIDENT #{incident['id']}: {incident['message']} @ {camera_id}")
    return incident


def get_recent_incidents():
    """Returns the most recent incidents from memory."""
    return _recent_incidents