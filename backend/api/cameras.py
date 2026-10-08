from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["cameras"])

# DEMO-ONLY: static sample list — real camera management future scope.
DEMO_CAMERAS = [
    {"id": "CAM-01", "name": "Factory-Cam-01", "zone": "Production Area", "status": "DEMO", "demo": True},
    {"id": "CAM-02", "name": "Factory-Cam-02", "zone": "Warehouse", "status": "DEMO", "demo": True},
    {"id": "CAM-03", "name": "Factory-Cam-03", "zone": "Boiler Area", "status": "DEMO", "demo": True},
    {"id": "CAM-04", "name": "Factory-Cam-04", "zone": "Entry Gate", "status": "DEMO", "demo": True},
]


@router.get("/cameras")
def get_cameras():
    """Sample camera list (demo). Fake ONLINE/OFFLINE state ab nahi dikhti."""
    return DEMO_CAMERAS