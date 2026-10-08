# 🦺 SafeVision AI

### See Risks. Detect Violations. Respond Faster.

**SafeVision AI** is an AI-powered factory safety monitoring system built for **BPUT Hackathon 2026 — Problem Statement 6: Factory Safety Monitoring & Hazard Detection**.

It uses **custom-trained YOLOv8 models** to detect PPE violations, fire, and smoke from webcam feeds and recorded videos. Detected incidents are stored in **MySQL**, visual evidence is captured, and the React dashboard provides real-time safety monitoring and compliance reports.

---

## ✨ Key Features

- 🔴 **Live Webcam Detection** — Real-time YOLO inference with bounding-box overlays.
- 🧠 **Custom YOLOv8 Models** — Separate PPE and Fire/Smoke models trained on domain-specific datasets.
- 👷 **PPE Compliance** — Detects person, helmet, no-helmet, vest, gloves, boots and goggles classes.
- 🔥 **Fire & Smoke Detection** — Tracks continuous fire/smoke events without creating duplicate incidents for every frame.
- 🚨 **Smart Alerts** — MySQL-backed 60-second alert cooldown to prevent duplicate alerts.
- 📸 **Evidence Capture** — Saves JPEG snapshots for detected violations.
- 🗄️ **MySQL Persistence** — Stores incidents, daily statistics and alert cooldown data.
- 📊 **Real Reports** — Compliance and incident trends generated from MySQL data.
- 🗺️ **Zone-Based Alerts** — Camera-to-zone mapping using `configs/zones.json`.
- 🎭 **DEMO / REAL Mode** — Clearly separates sample data from genuine AI inference.
- 📓 **Training Notebooks** — Reproducible YOLOv8 training notebooks are included.

---

## 🏗️ Architecture

```text
┌─────────────────────┐
│   React Frontend    │
│ Vite + Tailwind CSS │
└──────────┬──────────┘
           │ HTTP / JSON
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│       :8000         │
└──────────┬──────────┘
           │
     ┌─────┼─────────────┐
     ▼     ▼             ▼
   YOLO   Rules        MySQL
   AI     Engine       Database
     │      │             │
     └──────┼─────────────┘
            ▼
      Alerts + Evidence
```

### Backend Structure

```text
backend/
├── main.py
├── config.py
├── api/
│   ├── detection.py
│   ├── live.py
│   ├── alerts.py
│   ├── workers.py
│   └── cameras.py
├── ai/
│   ├── ppe_detector.py
│   └── fire_smoke_detector.py
├── rules/
│   ├── compliance_engine.py
│   ├── zone_rules.py
│   └── violation_tracker.py
├── alerts/
│   └── alert_manager.py
├── database/
│   ├── models.py
│   └── database.py
└── utils/
    ├── video.py
    ├── evidence.py
    └── logger.py
```

---

# 🚀 Quick Start

## Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8.0

## 1. Backend

```bash
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
```

Configure `.env`:

```env
MYSQL_PASSWORD=your_password
AI_MODE=REAL
```

Start backend:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

---

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🧠 AI Models

The project uses two custom-trained YOLOv8 models.

| Model | Purpose |
|---|---|
| PPE Model | Person, helmet, no_helmet, vest, gloves, boots, goggles etc. |
| Fire/Smoke Model | Fire and smoke detection |

Training:

- Google Colab
- NVIDIA T4 GPU
- Roboflow datasets
- YOLOv8n
- 640×640 image size
- 30 epochs

Training notebooks:

```text
notebooks/ppe_training.ipynb
notebooks/fire_smoke_training.ipynb
```

---

# 🎭 DEMO vs REAL Mode

SafeVision AI follows an honesty-first architecture.

### DEMO Mode

- Uses sample/demo data.
- UI clearly displays **DEMO MODE**.
- No claim of real AI detection.

### REAL Mode

- Requires actual model files.
- Runs genuine YOLO inference.
- Never replaces failed AI inference with fake detections.

Required model paths:

```text
models/ppe_model.pt
models/fire_smoke_model.pt
```

If models are missing, the application automatically remains in DEMO mode.

---

# 📹 Video Assets

Place video files inside:

```text
videos/
├── compliant.mp4
├── violation.mp4
└── fire_smoke.mp4
```

Large model/video files are excluded from Git using `.gitignore`.

---

# 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | System and AI status |
| GET | `/api/videos` | Available videos |
| GET | `/api/detections` | Analyze video |
| POST | `/api/analyze-video` | Analyze + alerts + evidence |
| GET | `/api/stats` | Safety statistics |
| GET | `/api/workers` | Worker PPE status |
| GET | `/api/alerts` | Recent incidents |
| GET | `/api/reports` | Compliance/incident reports |
| GET | `/api/cameras` | Camera inventory |
| GET | `/api/live/stream` | Live webcam stream |
| GET | `/videos/*` | Video files |
| GET | `/evidence/*` | Evidence images |

Most analysis endpoints support:

```text
?mode=REAL
```

or

```text
?mode=DEMO
```

---

# 🗄️ Database

SafeVision AI uses **MySQL 8.0**.

Main tables:

```text
incidents
daily_stats
alert_cooldowns
```

### incidents

Stores:

- Incident type
- Severity
- Message
- Camera
- Zone
- Worker ID
- Evidence image
- Timestamp

### daily_stats

Stores daily:

- Total workers
- Compliant workers
- PPE violations
- Fire incidents
- Smoke incidents

### alert_cooldowns

Prevents duplicate alerts and remains effective after application restart.

---

# 🗺️ Zone System

Camera locations are configured using:

```text
configs/zones.json
```

Example zones:

```text
Production Area
Warehouse
Boiler Area
Entry Gate
Live Monitoring
```

Every generated incident can include its camera and physical zone.

---

# 📸 Evidence System

When a real violation is detected:

```text
Detection
   ↓
Violation
   ↓
Alert Manager
   ↓
Evidence Snapshot
   ↓
MySQL Incident
   ↓
Dashboard
```

Evidence is stored in:

```text
evidence/alerts/
```

---

# ⚠️ Known Limitations

- No explicit `no_vest` class, so vest absence is informational only.
- CPU inference can be slower than GPU inference.
- Current prototype supports one local webcam.
- RTSP/CCTV multi-camera support is planned for future versions.
- Worker tracking currently uses spatial association rather than advanced ReID.
- Reports require sufficient database history for meaningful trends.

---

# 🔮 Future Scope

- Multi-camera RTSP/CCTV support
- GPU batch inference
- WebSocket/SSE real-time notifications
- Advanced worker ReID tracking
- Privacy-preserving face blurring
- SMS/email alerts
- PostgreSQL support
- Production-scale deployment

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS |
| Backend | FastAPI, Uvicorn |
| AI | Ultralytics YOLOv8, OpenCV |
| Database | MySQL 8.0 |
| Charts | Recharts |
| Dataset | Roboflow |
| Training | Google Colab T4 |
| Runtime | Python 3.10+, Node.js 18+ |

---

# 📁 Repository Layout

```text
safevision-ai/
├── backend/
├── frontend/
├── configs/
├── models/
├── videos/
├── evidence/
├── notebooks/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

Large binary assets such as models, videos and generated evidence are intentionally excluded from GitHub.

---

# 🤝 Hackathon

**SafeVision AI — BPUT Hackathon 2026**

**Problem Statement 6:**  
Factory Safety Monitoring & Hazard Detection

### Tagline

> **See Risks. Detect Violations. Respond Faster.**

Built with an **honesty-first DEMO/REAL architecture** so the system never presents fabricated detections as real AI results.