from ..utils.logger import get_logger

logger = get_logger("compliance_engine")

CLASS_HELMET = "helmet"
CLASS_VEST = "vest"
NO_HELMET_CLASSES = {"no_helmet", "none"}
# Ye violation sirf tab banegi jab MODEL ye classes actually return kare
NO_VEST_CLASSES = {"no_vest", "without_vest", "no-vest"}

HEAD_BAND = (0.0, 0.50)   # crouching workers ke heads bhi cover hon
VEST_BAND = (0.15, 0.75)


def _overlap(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    if x2 < x1 or y2 < y1:
        return 0
    return (x2 - x1) * (y2 - y1)


def _assign(person_box, candidates, band, threshold=0.3):
    px1, py1, px2, py2 = person_box
    ph = py2 - py1
    best_label, best_score = None, 0
    for det in candidates:
        b = det["bbox"]
        cy = (b[1] + b[3]) / 2
        rel_y = (cy - py1) / ph if ph else 1
        if not (band[0] <= rel_y <= band[1]):
            continue
        inter = _overlap(person_box, b)
        if inter <= 0:
            continue
        det_area = (b[2] - b[0]) * (b[3] - b[1])
        inside_ratio = inter / det_area if det_area else 0
        score = inside_ratio * det["confidence"]
        if score > best_score and score > threshold:
            best_score, best_label = score, det["label"]
    return best_label


def _is_person(label: str) -> bool:
    return label.lower() == "person"


def analyze_detections(dets):
    persons = [d for d in dets if _is_person(d["label"])]
    persons.sort(key=lambda d: d["bbox"][0])
    head_dets = [d for d in dets if d["label"] == CLASS_HELMET or d["label"] in NO_HELMET_CLASSES]
    vest_dets = [d for d in dets if d["label"] == CLASS_VEST or d["label"] in NO_VEST_CLASSES]

    workers, violations = [], []
    compliant_count = 0

    for i, p in enumerate(persons, start=1):
        head = _assign(p["bbox"], head_dets, HEAD_BAND)
        vest = _assign(p["bbox"], vest_dets, VEST_BAND) if vest_dets else None

        helmet_ok = head == CLASS_HELMET
        no_helmet = head in NO_HELMET_CLASSES
        vest_ok = vest == CLASS_VEST
        no_vest = vest in NO_VEST_CLASSES   # model class na de to ye kabhi true nahi hoga

        workers.append({"id": i, "helmet": helmet_ok, "vest": vest_ok,
                        "no_vest": no_vest, "head_status": head})

        # compliant = helmet OK aur (agar model vest-violation jaanta ho) vest missing NA ho
        if helmet_ok and not no_vest:
            compliant_count += 1

        if no_helmet:
            violations.append({
                "type": "PPE", "rule": "NO_HELMET", "severity": "HIGH",
                "message": "No Helmet Detected", "worker_id": i,
            })

        if no_vest:
            violations.append({
                "type": "PPE", "rule": "NO_VEST", "severity": "MEDIUM",
                "message": "No Vest Detected", "worker_id": i,
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