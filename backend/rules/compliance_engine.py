from ..utils.logger import get_logger

logger = get_logger("compliance_engine")

# Model ke ACTUAL trained class names
CLASS_PERSON = "Person"
CLASS_HELMET = "helmet"
CLASS_VEST = "vest"
NO_HELMET_CLASSES = {"no_helmet", "none"}   # 'none' = head without helmet


def _overlap(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    if x2 < x1 or y2 < y1:
        return 0
    return (x2 - x1) * (y2 - y1)


def _assign(person_box, candidates, threshold=0.3):
    """Gear box kitna person ke ANDAR hai — usi se match karo."""
    best_label, best_score = None, 0
    for det in candidates:
        b = det["bbox"]
        inter = _overlap(person_box, b)
        if inter <= 0:
            continue
        det_area = (b[2] - b[0]) * (b[3] - b[1])
        inside_ratio = inter / det_area if det_area else 0
        score = inside_ratio * det["confidence"]
        if score > best_score and score > threshold:
            best_score, best_label = score, det["label"]
    return best_label


def analyze_detections(dets):
    persons = [d for d in dets if d["label"] == CLASS_PERSON]
    head_dets = [d for d in dets if d["label"] == CLASS_HELMET or d["label"] in NO_HELMET_CLASSES]
    vest_dets = [d for d in dets if d["label"] == CLASS_VEST]

    workers, violations = [], []
    compliant_count = 0

    for i, p in enumerate(persons, start=1):
        head = _assign(p["bbox"], head_dets)
        vest = _assign(p["bbox"], vest_dets) if vest_dets else None

        helmet_ok = head == CLASS_HELMET
        no_helmet = head in NO_HELMET_CLASSES
        vest_ok = vest == CLASS_VEST

        # HONESTY: dataset mein 'no_vest' class NAHI hai ->
        # compliance sirf helmet par; vest sirf informational
        workers.append({"id": i, "helmet": helmet_ok, "vest": vest_ok, "head_status": head})

        if helmet_ok:
            compliant_count += 1

        if no_helmet:
            violations.append({
                "type": "PPE", "rule": "NO_HELMET", "severity": "HIGH",
                "message": "No Helmet Detected", "worker_id": i,
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