# 🦺 SafeVision AI
### See Risks. Detect Violations. Respond Faster.

AI-powered factory safety monitoring system jo **live webcam** aur recorded video feeds par **custom-trained YOLOv8 models** se PPE violations (no-helmet), **fire** aur **smoke** detect karta hai — real bounding boxes, real confidence scores, real MySQL persistence, real evidence snapshots. **Koi fake AI nahi.**

---

## ✨ Features

- 🔴 **Live Webcam Detection** — laptop/USB camera par REAL-time YOLO (MJPEG stream, `/api/live/stream`)
- 🧠 **2 Custom-Trained YOLOv8 Models:**
  - **PPE model** — 1,416 images, 11 classes (Person, helmet, no_helmet, none, vest, gloves, boots, goggles...)
  - **Fire/Smoke model** — Roboflow "Fire and smoke" dataset
- 🎭 **DEMO / REAL Modes** — DEMO clearly labeled (amber banner); REAL tabhi jab trained model maujood ho
- 👷 **Worker Compliance Engine** — Person ↔ Helmet spatial (IoU) matching, per-worker status
- 🔥 **Fire & Smoke Incidents** — CRITICAL / HIGH severity alerts
- 🚨 **Smart Alerts** — 60-second dedup cooldown (no alert spam)
- 📸 **Evidence Capture** — har violation ka frame snapshot (`evidence/alerts/*.jpg`)
- 🗄️ **MySQL 8.0 Persistence** — `incidents` + `daily_stats` tables
- 📊 **Real Reports** — REAL mode mein compliance/incident trends **MySQL se**
- 🗺️ **Zone Rules** — `configs/zones.json` (CAM-01…CAM-04 + CAM-LIVE) & `configs/ppe_rules.json`
- 📓 **Training Notebooks** — `notebooks/ppe_training.ipynb`, `notebooks/fire_smoke_training.ipynb`

---

## 🏗️ Architecture

```
┌──────────────────┐    HTTP/JSON     ┌──────────────────────────┐
│  React Frontend  │ ◄───────────────►│  FastAPI Backend (:8000) │
│ (Vite + Tailwind)│                  │                          │
└──────────────────┘                  └────────────┬─────────────┘
                                                   │
                ┌──────────────┬───────────────────┼──────────────┐
                ▼              ▼                   ▼              ▼
            ai/ (YOLO)     rules/             database/        utils/
            ppe + fire/    compliance         MySQL 8.0        video,
            smoke          engine (IoU)       incidents +      evidence,
                           zone rules         daily_stats      logger
                           violation tracker
                ▲
        alerts/ (alert manager — 60s dedup)
                ▲
            api/live (webcam MJPEG stream)
```

**backend/ structure:**
```
backend/
├── main.py            # App entry, routers, static serving, DB init (crash-safe)
├── config.py          # env-based settings (AI_MODE, MySQL, paths)
├── api/               # detection, alerts, workers, cameras, live
├── ai/                # ppe_detector, fire_detector, smoke_detector
├── rules/             # compliance_engine, zone_rules, violation_tracker
├── alerts/            # alert_manager (dedup cooldown)
├── database/          # models (schema) + database (MySQL CRUD)
└── utils/             # video sampling, evidence snapshots, logger
```

---

## 🚀 Setup

### Prerequisites
Python 3.10+ • Node 18+ • MySQL 8.0

### 1. Backend
```bash
python -m venv venv
venv\Scripts\activate                  # Windows
pip install -r requirements.txt

copy .env.example .env                 # apna MySQL password + AI_MODE=REAL
python -m uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                            # http://localhost:5173
```

### 3. Models & Videos (gitignored — Drive se)
Large assets GitHub par nahi hote (`.gitignore`), team ke liye **Google Drive** par:
```
models/ppe_model.pt          # PPE YOLOv8 (trained)
models/fire_smoke_model.pt   # Fire/Smoke YOLOv8 (trained)
videos/compliant.mp4         # free stock (pexels.com)
videos/violation.mp4
videos/fire_smoke.mp4
```
Models ke bina system **automatically DEMO MODE** mein chalta hai (honestly labeled).

---

## 🧠 Model Training (reproduce karne ke liye)

| | PPE Model | Fire/Smoke Model |
|---|---|---|
| Dataset | Roboflow PPE — 1,416 images, 11 classes | Roboflow "Fire and smoke" (YOLOv8) |
| Base | YOLOv8n | YOLOv8n |
| Training | Colab T4 GPU, 30 epochs, imgsz 640 | Colab T4 GPU, 30 epochs, imgsz 640 |
| Metrics | **Precision 0.75 • Recall 0.53 • mAP50 0.56** | dataset-dependent |
| Notebook | `notebooks/ppe_training.ipynb` | `notebooks/fire_smoke_training.ipynb` |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Mode (DEMO/REAL) + model status + supported classes |
| GET | `/api/live/stream?camera=0` | **Live webcam MJPEG stream with boxes** |
| GET | `/api/stats?mode=` | Worker/violation/fire/smoke stats |
| GET | `/api/workers?mode=` | Per-worker PPE status |
| GET | `/api/alerts?mode=` | Incidents (MySQL se, evidence URLs ke saath) |
| GET | `/api/reports?mode=` | REAL: MySQL trends • DEMO: sample |
| GET | `/api/cameras` | Camera list (demo; RTSP future scope) |
| GET | `/api/detections?video=&mode=` | Video analysis → bounding boxes |
| POST | `/api/analyze-video?video=` | Full analysis + incidents + evidence |
| GET | `/videos/*`, `/evidence/*` | Static media |

`mode=DEMO` → labeled sample data • `mode=REAL` → **sirf asli model/DB data** (kabhi demo fallback nahi).

---

## 🗄️ MySQL Schema

```sql
incidents     — id, type(PPE/FIRE/SMOKE), severity, message, camera, zone,
                worker_id, frame_url, created_at   [INDEX type, created_at]
daily_stats   — stat_date(PK), total_workers, compliant_workers,
                ppe_violations, fire_incidents, smoke_incidents
```

---

## 🎭 DEMO vs REAL — Honesty Policy

- **DEMO MODE:** amber banner, clearly labeled sample data
- **REAL MODE:** trained models + MySQL ka asli data; error par **khali result**, demo fallback nahi
- Vest **absence** ko violation **nahi** bola jata (dataset mein 'no_vest' class nahi) — vest sirf informational
- System kabhi fake detections claim **nahi** karta

---

## ⚠️ Honest Limitations

- Dataset mein explicit "no-vest" class nahi → vest sirf informational
- CPU inference ~10-20 sec/video; live webcam ~2-4 FPS (production: GPU)
- Reports trends ko 1+ din ka data chahiye (shuru mein sparse)
- Recorded videos + webcam; external CCTV (RTSP) future scope

## 🔮 Future Scope

RTSP/CCTV streams • GPU inference • Socket.IO push alerts • Worker tracking (frame-to-frame IDs) • PostgreSQL • Face blurring (privacy) • SMS/WhatsApp alerts

---

## 🛠️ Tech Stack

React • Vite • Tailwind CSS • FastAPI • Ultralytics YOLOv8 • OpenCV • MySQL 8.0 • Roboflow • Google Colab

---

**SafeVision AI — Hackathon 2026** 🦺⚡