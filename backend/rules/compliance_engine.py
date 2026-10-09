from ..utils.logger import get_logger

logger = get_logger("compliance_engine")

# --- CLASS DEFINITIONS ---
CLASS_HELMET = "helmet"
CLASS_VEST = "vest"

# Classes that indicate MISSING HELMET (Explicit negatives + 'none' fallback)
NO_HELMET_CLASSES = {"no_helmet", "none"}

# Classes that indicate MISSING VEST
# HONESTY NOTE: Our dataset lacked a dedicated 'no_vest' class, so we only
# trust explicit no_vest labels. 'none' is NOT treated as vest violation.
NO_VEST_CLASSES = {"no_vest", "without_vest", "no-vest"}

# --- SPATIAL BANDS (Relative Y-position within Person Box) ---
# Head region: Top 0% to 50% of person height (covers crouching too)
HEAD_BAND = (0.0, 0.50)
# Torso/Vest region: 15% to 75% of person height
VEST_BAND = (0.15, 0.75)


def _overlap(box1, box2):
    """Calculate intersection area between two boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    if x2 < x1 or y2 < y1:
        return 0
    return (x2 - x1) * (y2 - y1)


def _assign(person_box, candidates, band, threshold=0.3):
    """
    Finds the best matching candidate for a specific body part based on
    spatial overlap and confidence. Returns the label string or None.
    """
    px1, py1, px2, py2 = person_box
    ph = py2 - py1

    best_label, best_score = None, 0

    for det in candidates:
        b = det["bbox"]
        cy = (b[1] + b[3]) / 2

        # Calculate relative vertical position inside the person box
        rel_y = (cy - py1) / ph if ph else 1

        # Check if this detection falls within the target band (Head or Vest)
        if not (band[0] <= rel_y <= band[1]):
            continue

        inter = _overlap(person_box, b)
        if inter <= 0:
            continue

        det_area = (b[2] - b[0]) * (b[3] - b[1])
        inside_ratio = inter / det_area if det_area else 0

        # Score combines overlap with person AND detection's own confidence
        score = inside_ratio * det["confidence"]

        if score > best_score and score > threshold:
            best_score, best_label = score, det["label"]

    return best_label


def _is_person(label: str) -> bool:
    return label.lower() == "person"


def analyze_detections(dets):
    """
    Main logic engine: Associates PPE items with Persons and generates violations.

    HONESTY FIX:
    - 'none' is treated as helmet violation (model has explicit 'no_helmet' class).
    - 'none' is NOT treated as vest violation, because the model does not have
      a dedicated 'no_vest' class. Only explicit no_vest labels trigger it.
    """
    persons = [d for d in dets if _is_person(d["label"])]
    persons.sort(key=lambda d: d["bbox"][0])  # left-to-right consistent IDs

    # Separate candidates by category
    head_candidates = []
    vest_candidates = []

    for d in dets:
        lbl_lower = d["label"].lower()
        if lbl_lower == CLASS_HELMET or lbl_lower in NO_HELMET_CLASSES:
            head_candidates.append(d)
        elif lbl_lower == CLASS_VEST or lbl_lower in NO_VEST_CLASSES:
            vest_candidates.append(d)

    workers, violations = [], []
    compliant_count = 0

    for i, p in enumerate(persons, start=1):
        # 1. Assign Head Gear
        head_label = _assign(p["bbox"], head_candidates, HEAD_BAND)

        # 2. Assign Body Gear (Vest)
        vest_label = _assign(p["bbox"], vest_candidates, VEST_BAND) if vest_candidates else None

        # --- DETERMINE COMPLIANCE STATUS ---

        # Helmet Status
        helmet_ok = (head_label == CLASS_HELMET)
        no_helmet = (head_label in NO_HELMET_CLASSES)

        # Vest Status — only explicit no_vest class triggers violation
        vest_ok = (vest_label == CLASS_VEST)
        no_vest = (vest_label in NO_VEST_CLASSES)

        # Append Worker Record
        workers.append({
            "id": i,
            "helmet": helmet_ok,
            "vest": vest_ok,
            "no_vest": no_vest,
            "head_status": head_label,
        })

        # Count Compliant (helmet present AND no explicit vest violation)
        if helmet_ok and not no_vest:
            compliant_count += 1

        # --- GENERATE VIOLATIONS ---
        if no_helmet:
            violations.append({
                "type": "PPE",
                "rule": "NO_HELMET",
                "severity": "HIGH",
                "message": f"No Helmet Detected (Worker #{i})",
                "worker_id": i,
            })

        if no_vest:
            violations.append({
                "type": "PPE",
                "rule": "NO_VEST",
                "severity": "MEDIUM",
                "message": f"No Vest Detected (Worker #{i})",
                "worker_id": i,
            })

    return {
        "workers": workers,
        "violations": violations,
        "stats": {
            "totalWorkers": len(persons),
            "compliantWorkers": compliant_count,
            "ppeViolations": len(violations),
        },
    }