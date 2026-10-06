import time

from ..rules import violation_tracker
from ..utils.logger import get_logger

logger = get_logger("alert_manager")

COOLDOWN_SECONDS = 60
_last_seen = {}


def report_violation(violation, camera_id, zone_name, frame_url=None):
    """Same rule + same camera within 60 sec => skip (alert spam nahi)."""
    key = (violation.get("rule", violation.get("type")), camera_id)
    now = time.time()
    if key in _last_seen and now - _last_seen[key] < COOLDOWN_SECONDS:
        return None
    _last_seen[key] = now
    return violation_tracker.record_incident(violation, camera_id, zone_name, frame_url)