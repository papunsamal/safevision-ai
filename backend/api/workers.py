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

# Latest analysis store — REAL mode mein detection.py isse update karta hai.
# Jab tak real analysis nahi hua, demo data hi serve hota hai.
latest_analysis = {"workers": DEMO_WORKERS, "stats": DEMO_STATS}


def update_analysis(workers, stats):
    """Rules engine ka fresh analysis yahan save hota hai."""
    global latest_analysis
    latest_analysis = {"workers": workers, "stats": stats}


@router.get("/stats")
def get_stats():
    return latest_analysis["stats"]


@router.get("/workers")
def get_workers():
    return latest_analysis["workers"]