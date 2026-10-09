import json
import os
from ..config import settings

# Load zones from config file if exists, otherwise use defaults
ZONES_CONFIG = {
    "CAM-01": {"name": "Production Area", "risk_level": "HIGH"},
    "CAM-02": {"name": "Warehouse", "risk_level": "MEDIUM"},
    "CAM-03": {"name": "Boiler Area", "risk_level": "CRITICAL"},
    "CAM-LIVE": {"name": "Live Feed Zone", "risk_level": "UNKNOWN"},
}

def load_zones():
    """Loads zone configurations from configs/zones.json if available."""
    global ZONES_CONFIG
    config_path = os.path.join(settings.CONFIGS_DIR, "zones.json")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                # Convert list of dicts to dict keyed by camera_id for faster lookup
                ZONES_CONFIG = {item['id']: item for item in data}
        except Exception as e:
            print(f"Warning: Could not load zones.json ({e}). Using defaults.")
    else:
        print("Info: No zones.json found. Using default hardcoded zones.")

# Initialize on import
load_zones()

def zone_for_camera(camera_id: str) -> dict:
    """
    Returns the zone details for a given camera ID.
    If unknown, returns a generic 'Unknown Zone'.
    """
    return ZONES_CONFIG.get(camera_id, {"name": "Unknown Zone", "risk_level": "LOW"})

def get_all_zones() -> list:
    """Returns all configured zones as a list."""
    return list(ZONES_CONFIG.values())