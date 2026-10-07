from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["workers"])

DEMO_STATS = {"totalWorkers": 25, "compliantWorkers": 22, "ppeViolations": 3,
              "fireIncidents": 1, "smokeIncidents": 2}

DEMO_WORKERS = [
    {"id": 1, "helmet": True, "vest": True, "gloves": True},
    {"id": 2, "helmet": False, "vest": True},
    {"id": 3, "helmet": True, "vest": False},
    {"id": 4, "helmet": True, "vest": True},
]

# REAL mode: zero se shuru (koi fake data nahi) — real analysis ke baad update hota hai
EMPTY_STATS = {"totalWorkers": 0, "compliantWorkers": 0, "ppeViolations": 0,
               "fireIncidents": 0, "smokeIncidents": 0}

latest_analysis = {"workers": [], "stats": EMPTY_STATS}


def update_analysis(workers, stats):
    """Rules engine ka fresh analysis yahan save hota hai."""
    global latest_analysis
    latest_analysis = {"workers": workers, "stats": stats}


@router.get("/stats")
def get_stats(mode: str = "REAL"):
    if mode == "DEMO":
        return DEMO_STATS
    return latest_analysis["stats"]


@router.get("/workers")
def get_workers(mode: str = "REAL"):
    if mode == "DEMO":
        return DEMO_WORKERS
    return latest_analysis["workers"]