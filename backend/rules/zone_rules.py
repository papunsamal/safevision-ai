import json
import os
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("zone_rules")


def load_zones():
    path = os.path.join(settings.CONFIGS_DIR, "zones.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f).get("zones", [])


def load_ppe_rules():
    path = os.path.join(settings.CONFIGS_DIR, "ppe_rules.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def zone_for_camera(camera_id: str):
    for z in load_zones():
        if camera_id in z.get("cameras", []):
            return z
    return {"name": "Unknown Zone"}