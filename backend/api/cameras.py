from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["cameras"])

# DEMO-ONLY: Real camera management future scope mein hai
DEMO_CAMERAS = [
    {"id": "CAM-01", "name": "Factory-Cam-01", "zone": "Production Area", "status": "ONLINE"},
    {"id": "CAM-02", "name": "Factory-Cam-02", "zone": "Warehouse", "status": "ONLINE"},
    {"id": "CAM-03", "name": "Factory-Cam-03", "zone": "Boiler Area", "status": "ONLINE"},
    {"id": "CAM-04", "name": "Factory-Cam-04", "zone": "Entry Gate", "status": "OFFLINE"},
]


@router.get("/cameras")
def get_cameras():
    """Returns demo camera list. Real RTSP camera management is future scope."""
    return DEMO_CAMERAS