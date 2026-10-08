import time

from ..rules import violation_tracker
from ..database import database
from ..utils.logger import get_logger

logger = get_logger("alert_manager")

COOLDOWN_SECONDS = 60
_last_seen = {}


def _cooldown_key(violation, camera_id, zone_name):
    """rule/type + camera + zone + worker — alag workers ab ek-dusre ko suppress nahi karenge."""
    return f"{violation.get('rule', violation.get('type'))}|{camera_id}|{zone_name}|{violation.get('worker_id')}"


def report_violation(violation, camera_id, zone_name, frame_url=None):
    key = _cooldown_key(violation, camera_id, zone_name)
    now = time.time()

    last = _last_seen.get(key)
    if last is None:
        last = database.get_cooldown(key)   # restart-safe (MySQL-backed)

    if last is not None and now - last < COOLDOWN_SECONDS:
        return None

    _last_seen[key] = now
    database.set_cooldown(key, now)
    return violation_tracker.record_incident(violation, camera_id, zone_name, frame_url)