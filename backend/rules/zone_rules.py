import json
import os

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("zone_rules")

_zones = None


def _load_zones():
    global _zones
    if _zones is not None:
        return _zones
    try:
        path = os.path.join(settings.CONFIGS_DIR, "zones.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Support BOTH formats:
        # Format 1 (list): {"zones": [{"id":..., "name":..., "cameras":[...]}]}
        # Format 2 (dict): {"CAM-01": {"id":..., "name":...}}
        _zones = {}
        if isinstance(data, dict) and "zones" in data:
            for zone in data["zones"]:
                for cam in zone.get("cameras", []):
                    _zones[cam] = {"id": zone["id"], "name": zone["name"]}
        elif isinstance(data, dict):
            _zones = data
        else:
            _zones = {}

        logger.info(f"Loaded {len(_zones)} camera-zone mappings")
    except Exception as e:
        logger.error(f"zone load failed: {e}")
        _zones = {}
    return _zones


def zone_for_camera(camera_id: str) -> dict:
    zones = _load_zones()
    return zones.get(camera_id, {"id": "Z0", "name": "Unknown"})